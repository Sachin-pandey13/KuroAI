from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
import time

from backend.contracts.capability import (
    CapabilityType,
    CapabilityDescriptor,
    ToolRequest,
    ToolResponse,
    ResolvedProvider,
)
from backend.capabilities.providers.base_provider import BaseProvider


class ProviderNotFoundError(Exception):
    """Raised when no healthy provider can be resolved for a CapabilityType."""
    pass


class CapabilityNotRegisteredError(Exception):
    """Raised when a CapabilityType has no registered providers."""
    pass


class ProviderHealthMonitor:
    """
    Cached health tracking for registered providers.
    Decouples health probing from the request routing hot path.
    Call refresh_health(provider) to update from a live health_check().
    """

    def __init__(self) -> None:
        self._health: Dict[str, bool] = {}

    def set_health(self, provider_name: str, healthy: bool) -> None:
        self._health[provider_name] = healthy

    def is_healthy(self, provider_name: str) -> bool:
        return self._health.get(provider_name, True)

    def refresh_health(self, provider: BaseProvider) -> bool:
        """Probe a live health_check() and update the cached status."""
        try:
            result = provider.health_check()
        except Exception:
            result = False
        self._health[provider.provider_name] = result
        return result

    def mark_unhealthy(self, provider_name: str) -> None:
        self._health[provider_name] = False


class BaseRoutingStrategy(ABC):
    """
    Abstract strategy for resolving which provider handles a ToolRequest.
    Future strategies (LowestLatencyStrategy, RoundRobinStrategy) extend this.
    """

    @abstractmethod
    def resolve(
        self,
        request: ToolRequest,
        providers: Dict[str, BaseProvider],
        health_monitor: ProviderHealthMonitor,
    ) -> BaseProvider:
        """Return the best healthy provider for the given ToolRequest."""
        pass


class PriorityRoutingStrategy(BaseRoutingStrategy):
    """
    Default routing strategy:
    1. preferred_provider (if specified and healthy)
    2. First healthy registered primary provider
    3. Any remaining healthy fallback provider
    """

    def resolve(
        self,
        request: ToolRequest,
        providers: Dict[str, BaseProvider],
        health_monitor: ProviderHealthMonitor,
    ) -> BaseProvider:
        if not providers:
            raise ProviderNotFoundError("No providers registered for capability.")

        # 1. Explicit preferred provider
        if request.preferred_provider and request.preferred_provider in providers:
            candidate = providers[request.preferred_provider]
            if health_monitor.is_healthy(candidate.provider_name):
                return candidate

        # 2. First healthy provider in registration order
        for provider in providers.values():
            if health_monitor.is_healthy(provider.provider_name):
                return provider

        raise ProviderNotFoundError(
            f"No healthy provider found for capability '{request.capability_type}'. "
            f"Registered: {list(providers.keys())}"
        )


class CapabilityRegistry:
    """
    Model-agnostic provider resolution engine.

    Resolves ToolRequests to a ResolvedProvider via routing strategy.
    Does NOT own execution — the Agent Runtime calls provider.execute() directly.

    Hierarchy:
        CapabilityType (e.g. GENERATE_TEXT)
            → BaseProvider (e.g. MockTextProvider)
                → Model (e.g. mock-gpt-4o)
    """

    def __init__(
        self,
        routing_strategy: Optional[BaseRoutingStrategy] = None,
        health_monitor: Optional[ProviderHealthMonitor] = None,
    ) -> None:
        # Dict[CapabilityType, Dict[provider_name, BaseProvider]]
        self._registry: Dict[CapabilityType, Dict[str, BaseProvider]] = {}
        self._disabled: Dict[str, bool] = {}
        self._strategy = routing_strategy or PriorityRoutingStrategy()
        self._health_monitor = health_monitor or ProviderHealthMonitor()

    def register_provider(
        self,
        capability_type: CapabilityType,
        provider_instance: BaseProvider,
    ) -> None:
        """Register a provider for a CapabilityType. Initializes health to healthy."""
        if capability_type not in self._registry:
            self._registry[capability_type] = {}
        self._registry[capability_type][provider_instance.provider_name] = provider_instance
        self._health_monitor.set_health(provider_instance.provider_name, True)

    def unregister_provider(
        self,
        capability_type: CapabilityType,
        provider_name: str,
    ) -> None:
        """Remove a provider from a CapabilityType."""
        if capability_type in self._registry:
            self._registry[capability_type].pop(provider_name, None)

    def enable_provider(self, provider_name: str) -> None:
        """Re-enable a disabled provider."""
        self._disabled.pop(provider_name, None)
        self._health_monitor.set_health(provider_name, True)

    def disable_provider(self, provider_name: str) -> None:
        """Temporarily disable a provider without unregistering it."""
        self._disabled[provider_name] = True
        self._health_monitor.set_health(provider_name, False)

    def list_capabilities(self) -> List[CapabilityType]:
        """List all CapabilityTypes that have at least one registered provider."""
        return [cap for cap, providers in self._registry.items() if providers]

    def list_providers(self, capability_type: CapabilityType) -> List[str]:
        """List all provider names registered for a CapabilityType."""
        return list(self._registry.get(capability_type, {}).keys())

    def get_provider(
        self,
        capability_type: CapabilityType,
        provider_name: str,
    ) -> BaseProvider:
        """Retrieve a specific provider instance."""
        providers = self._registry.get(capability_type, {})
        if provider_name not in providers:
            raise ProviderNotFoundError(
                f"Provider '{provider_name}' not registered for '{capability_type}'."
            )
        return providers[provider_name]

    def get_descriptor(
        self,
        capability_type: CapabilityType,
        provider_name: str,
    ) -> CapabilityDescriptor:
        """Retrieve the CapabilityDescriptor for a given provider."""
        provider = self.get_provider(capability_type, provider_name)
        if hasattr(provider, "descriptor"):
            return provider.descriptor
        return CapabilityDescriptor(
            capability_type=capability_type,
            provider_name=provider_name,
            supported_models=provider.supported_models,
        )

    def resolve(self, request: ToolRequest) -> ResolvedProvider:
        """
        Core resolution API: determine the best provider and model for a ToolRequest.
        Returns a pure-value ResolvedProvider — does NOT execute.
        """
        if request.capability_type not in self._registry:
            raise CapabilityNotRegisteredError(
                f"No providers registered for capability '{request.capability_type}'."
            )

        providers = self._registry[request.capability_type]
        provider = self._strategy.resolve(request, providers, self._health_monitor)

        model_name = request.preferred_model or (
            provider.supported_models[0] if provider.supported_models else "default"
        )
        descriptor = self.get_descriptor(request.capability_type, provider.provider_name)

        return ResolvedProvider(
            capability_type=request.capability_type,
            provider_name=provider.provider_name,
            model_name=model_name,
            provider_instance=provider,
            descriptor=descriptor,
            resolution_strategy=type(self._strategy).__name__,
        )

    def execute(self, request: ToolRequest) -> ToolResponse:
        """
        Convenience execution method: resolve() then provider.execute().
        Used when the caller does not need a separate ResolvedProvider step.
        On provider exception, returns ToolResponse(success=False) rather than raising.
        """
        start_ms = time.monotonic() * 1000
        try:
            resolved = self.resolve(request)
            response = resolved.provider_instance.execute(request)
            response.execution_time_ms = round(time.monotonic() * 1000 - start_ms, 3)
            return response
        except ProviderNotFoundError as exc:
            return ToolResponse(
                request_id=request.request_id,
                success=False,
                capability_type=request.capability_type,
                provider_name="none",
                model_name="none",
                error_message=str(exc),
                execution_time_ms=round(time.monotonic() * 1000 - start_ms, 3),
            )
        except Exception as exc:
            return ToolResponse(
                request_id=request.request_id,
                success=False,
                capability_type=request.capability_type,
                provider_name="unknown",
                model_name="unknown",
                error_message=f"Provider execution error: {exc}",
                execution_time_ms=round(time.monotonic() * 1000 - start_ms, 3),
            )

