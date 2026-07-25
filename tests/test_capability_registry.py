"""
Test: Capability Registry & Provider Routing Subsystem (Milestone 8)
Verifies Stages 1-4: Contracts, CapabilityDescriptor, ResolvedProvider, MockProviders,
ProviderHealthMonitor, PriorityRoutingStrategy, resolution vs execution separation,
fallback failover, error isolation, and provider lifecycle (enable/disable).
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from backend.contracts.capability import (
    CapabilityType,
    CapabilityDescriptor,
    ToolRequest,
    ToolResponse,
    ResolvedProvider,
)
from backend.capabilities.registry import (
    CapabilityRegistry,
    ProviderHealthMonitor,
    BaseRoutingStrategy,
    PriorityRoutingStrategy,
    ProviderNotFoundError,
    CapabilityNotRegisteredError,
)
from backend.capabilities.providers.mock_text_provider import MockTextProvider
from backend.capabilities.providers.mock_image_provider import MockImageProvider
from backend.capabilities.providers.base_provider import BaseProvider


@pytest.fixture
def text_provider() -> MockTextProvider:
    return MockTextProvider()


@pytest.fixture
def image_provider() -> MockImageProvider:
    return MockImageProvider()


@pytest.fixture
def registry(text_provider, image_provider) -> CapabilityRegistry:
    reg = CapabilityRegistry()
    reg.register_provider(CapabilityType.GENERATE_TEXT, text_provider)
    reg.register_provider(CapabilityType.GENERATE_IMAGE, image_provider)
    return reg


# =====================================================================
# Unit Tests — CapabilityDescriptor & Contract Enhancements
# =====================================================================

class TestCapabilityContracts:
    def test_capability_descriptor_defaults(self, text_provider):
        desc = text_provider.descriptor
        assert desc.capability_type == CapabilityType.GENERATE_TEXT
        assert desc.provider_name == "mock_text_provider"
        assert "mock-gpt-4o" in desc.supported_models
        assert desc.supports_json is True
        assert desc.supports_seed is True

    def test_tool_request_has_request_id(self):
        req = ToolRequest(capability_type=CapabilityType.GENERATE_TEXT)
        assert req.request_id is not None
        assert len(req.request_id) == 36  # UUID

    def test_tool_response_has_telemetry_fields(self, text_provider):
        req = ToolRequest(
            capability_type=CapabilityType.GENERATE_TEXT,
            parameters={"prompt": "Hello"},
        )
        resp = text_provider.execute(req)
        assert resp.request_id == req.request_id
        assert resp.response_id is not None
        assert "prompt_tokens" in resp.token_usage
        assert resp.cost_usd == 0.0


# =====================================================================
# Unit Tests — ProviderHealthMonitor
# =====================================================================

class TestProviderHealthMonitor:
    def test_provider_healthy_by_default(self):
        monitor = ProviderHealthMonitor()
        assert monitor.is_healthy("unknown_provider") is True

    def test_set_and_check_health(self):
        monitor = ProviderHealthMonitor()
        monitor.set_health("my_provider", False)
        assert monitor.is_healthy("my_provider") is False

    def test_mark_unhealthy(self):
        monitor = ProviderHealthMonitor()
        monitor.set_health("my_provider", True)
        monitor.mark_unhealthy("my_provider")
        assert monitor.is_healthy("my_provider") is False

    def test_refresh_health_from_live_check(self, text_provider):
        monitor = ProviderHealthMonitor()
        result = monitor.refresh_health(text_provider)
        assert result is True
        assert monitor.is_healthy(text_provider.provider_name) is True


# =====================================================================
# Unit Tests — Provider Registration & Queries
# =====================================================================

class TestCapabilityRegistryRegistration:
    def test_register_and_list_capabilities(self, registry):
        caps = registry.list_capabilities()
        assert CapabilityType.GENERATE_TEXT in caps
        assert CapabilityType.GENERATE_IMAGE in caps

    def test_list_providers_for_capability(self, registry):
        providers = registry.list_providers(CapabilityType.GENERATE_TEXT)
        assert "mock_text_provider" in providers

    def test_get_provider_instance(self, registry):
        provider = registry.get_provider(CapabilityType.GENERATE_TEXT, "mock_text_provider")
        assert provider.provider_name == "mock_text_provider"

    def test_get_descriptor(self, registry):
        desc = registry.get_descriptor(CapabilityType.GENERATE_TEXT, "mock_text_provider")
        assert isinstance(desc, CapabilityDescriptor)
        assert desc.capability_type == CapabilityType.GENERATE_TEXT

    def test_unregister_provider(self, registry):
        registry.unregister_provider(CapabilityType.GENERATE_TEXT, "mock_text_provider")
        providers = registry.list_providers(CapabilityType.GENERATE_TEXT)
        assert "mock_text_provider" not in providers

    def test_enable_disable_provider(self, registry):
        # Disable
        registry.disable_provider("mock_text_provider")
        with pytest.raises(ProviderNotFoundError):
            registry.resolve(ToolRequest(capability_type=CapabilityType.GENERATE_TEXT))

        # Re-enable
        registry.enable_provider("mock_text_provider")
        resolved = registry.resolve(ToolRequest(capability_type=CapabilityType.GENERATE_TEXT))
        assert resolved.provider_name == "mock_text_provider"


# =====================================================================
# Unit Tests — Resolution API (resolve vs execute separation)
# =====================================================================

class TestCapabilityRegistryResolution:
    def test_resolve_returns_resolved_provider(self, registry):
        """resolve() returns a pure-value ResolvedProvider, does NOT execute."""
        request = ToolRequest(
            capability_type=CapabilityType.GENERATE_TEXT,
            parameters={"prompt": "write a story"},
        )
        resolved = registry.resolve(request)
        assert isinstance(resolved, ResolvedProvider)
        assert resolved.capability_type == CapabilityType.GENERATE_TEXT
        assert resolved.provider_name == "mock_text_provider"
        assert resolved.resolution_strategy == "PriorityRoutingStrategy"

    def test_resolve_selects_preferred_model(self, registry):
        request = ToolRequest(
            capability_type=CapabilityType.GENERATE_TEXT,
            preferred_model="mock-claude-3-5",
        )
        resolved = registry.resolve(request)
        assert resolved.model_name == "mock-claude-3-5"

    def test_resolved_provider_can_execute(self, registry):
        """Agent Runtime pattern: resolve(), then provider_instance.execute()."""
        request = ToolRequest(
            capability_type=CapabilityType.GENERATE_TEXT,
            parameters={"prompt": "Hello World"},
        )
        resolved = registry.resolve(request)
        response = resolved.provider_instance.execute(request)
        assert isinstance(response, ToolResponse)
        assert response.success is True
        assert "text" in response.output_data

    def test_unregistered_capability_raises(self, registry):
        with pytest.raises(CapabilityNotRegisteredError):
            registry.resolve(ToolRequest(capability_type=CapabilityType.EXPORT_PDF))


# =====================================================================
# Unit Tests — Routing Strategy & Fallback
# =====================================================================

class TestRoutingStrategy:
    def test_preferred_provider_selected(self):
        """PriorityRoutingStrategy routes to preferred provider when healthy."""
        reg = CapabilityRegistry()
        p1 = MockTextProvider()
        reg.register_provider(CapabilityType.GENERATE_TEXT, p1)

        request = ToolRequest(
            capability_type=CapabilityType.GENERATE_TEXT,
            preferred_provider="mock_text_provider",
        )
        resolved = reg.resolve(request)
        assert resolved.provider_name == "mock_text_provider"

    def test_fallback_to_secondary_when_primary_unhealthy(self):
        """PriorityRoutingStrategy falls back to secondary if primary is unhealthy."""

        class SecondaryTextProvider(BaseProvider):
            @property
            def provider_name(self):
                return "secondary_text_provider"

            @property
            def supported_models(self):
                return ["secondary-model"]

            def execute(self, request):
                return MockTextProvider().execute(request)

            def health_check(self):
                return True

        reg = CapabilityRegistry()
        primary = MockTextProvider()
        secondary = SecondaryTextProvider()
        reg.register_provider(CapabilityType.GENERATE_TEXT, primary)
        reg.register_provider(CapabilityType.GENERATE_TEXT, secondary)

        # Mark primary unhealthy
        reg.disable_provider("mock_text_provider")

        resolved = reg.resolve(ToolRequest(capability_type=CapabilityType.GENERATE_TEXT))
        assert resolved.provider_name == "secondary_text_provider"

    def test_no_healthy_providers_raises(self):
        reg = CapabilityRegistry()
        reg.register_provider(CapabilityType.GENERATE_TEXT, MockTextProvider())
        reg.disable_provider("mock_text_provider")

        with pytest.raises(ProviderNotFoundError):
            reg.resolve(ToolRequest(capability_type=CapabilityType.GENERATE_TEXT))

    def test_custom_routing_strategy(self):
        """Verify BaseRoutingStrategy plugin contract."""

        class AlwaysFirstStrategy(BaseRoutingStrategy):
            def resolve(self, request, providers, health_monitor):
                return next(iter(providers.values()))

        reg = CapabilityRegistry(routing_strategy=AlwaysFirstStrategy())
        reg.register_provider(CapabilityType.GENERATE_TEXT, MockTextProvider())
        resolved = reg.resolve(ToolRequest(capability_type=CapabilityType.GENERATE_TEXT))
        assert resolved.provider_name == "mock_text_provider"


# =====================================================================
# Integration Tests — Mock Provider Execution & Telemetry
# =====================================================================

class TestMockProviderExecution:
    def test_mock_text_execution(self, registry):
        request = ToolRequest(
            capability_type=CapabilityType.GENERATE_TEXT,
            parameters={"prompt": "Write a samurai scene", "seed": 99},
        )
        response = registry.execute(request)
        assert response.success is True
        assert response.request_id == request.request_id
        assert "text" in response.output_data
        assert response.token_usage.get("total_tokens", 0) > 0
        assert response.execution_time_ms >= 0.0

    def test_mock_image_execution(self, registry):
        request = ToolRequest(
            capability_type=CapabilityType.GENERATE_IMAGE,
            parameters={"prompt": "Cyberpunk city at night", "width": 512, "height": 512},
        )
        response = registry.execute(request)
        assert response.success is True
        assert response.request_id == request.request_id
        assert "image_path" in response.output_data
        assert response.output_data["width"] == 512

    def test_error_isolation_returns_failure_response(self):
        """Provider exception is caught and returned as ToolResponse(success=False)."""

        class BrokenProvider(BaseProvider):
            @property
            def provider_name(self):
                return "broken_provider"

            @property
            def supported_models(self):
                return ["broken-model"]

            def execute(self, request):
                raise RuntimeError("Provider backend is down!")

            def health_check(self):
                return True

        reg = CapabilityRegistry()
        reg.register_provider(CapabilityType.GENERATE_TEXT, BrokenProvider())

        request = ToolRequest(capability_type=CapabilityType.GENERATE_TEXT)
        response = reg.execute(request)

        assert response.success is False
        assert response.request_id == request.request_id
        assert "Provider backend is down!" in response.error_message
