"""
ToolExecutor — Injection interface between agents and the Capability Registry.

Agents depend ONLY on BaseToolExecutor. They never import CapabilityRegistry.
The AgentRuntime constructs and injects the concrete CapabilityToolExecutor.

This decoupling makes it trivial to swap in:
    MockToolExecutor       — deterministic test execution
    RecordingToolExecutor  — captures all requests for replay/debugging
    RetryToolExecutor      — wraps with exponential backoff
    CachedToolExecutor     — returns cached responses for identical requests
    RemoteToolExecutor     — routes to a remote capability service

Each is a decorator over BaseToolExecutor. The domain agents never change.
"""

from abc import ABC, abstractmethod

from backend.contracts.capability import ToolRequest, ToolResponse


class BaseToolExecutor(ABC):
    """
    Minimal capability execution interface injected into every agent.
    Agents express what they need; the executor decides how to deliver it.
    """

    @abstractmethod
    async def execute(self, request: ToolRequest) -> ToolResponse:
        """Execute a capability request. Always returns a ToolResponse."""
        pass


class CapabilityToolExecutor(BaseToolExecutor):
    """
    Production implementation: delegates to CapabilityRegistry.
    Constructed by AgentRuntime and injected into agent.execute().
    """

    def __init__(self, registry) -> None:
        # Typed as object to avoid circular imports.
        # Actual type: CapabilityRegistry from backend.capabilities.registry
        self._registry = registry

    async def execute(self, request: ToolRequest) -> ToolResponse:
        """Resolve provider and execute synchronously via the registry."""
        return self._registry.execute(request)  # type: ignore[no-any-return]


class MockToolExecutor(BaseToolExecutor):
    """
    Deterministic test executor. Returns pre-registered canned responses.
    Used in all unit and integration tests — no real providers needed.
    """

    def __init__(self) -> None:
        self._responses: dict[str, ToolResponse] = {}
        self._call_log: list[ToolRequest] = []

    def register_response(self, capability_type, response: ToolResponse) -> None:
        """Pre-register a canned response for a CapabilityType."""
        self._responses[str(capability_type)] = response

    async def execute(self, request: ToolRequest) -> ToolResponse:
        self._call_log.append(request)
        key = str(request.capability_type)
        if key in self._responses:
            response = self._responses[key]
            # Bind request_id for tracing
            response = response.model_copy(update={"request_id": request.request_id})
            return response
        from backend.contracts.capability import ToolResponse

        return ToolResponse(
            request_id=request.request_id,
            success=True,
            capability_type=request.capability_type,
            provider_name="mock_executor",
            model_name="mock-default",
            output_data={"text": f"[MockToolExecutor] response for {request.capability_type}"},
        )

    @property
    def call_count(self) -> int:
        return len(self._call_log)

    @property
    def calls(self) -> list:
        return list(self._call_log)
