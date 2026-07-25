from typing import Dict, List, Optional
from backend.contracts.capability import CapabilityType, ToolRequest, ToolResponse


class CapabilityRegistry:
    """
    Model-agnostic routing layer.
    Maps abstract Capabilities to Providers to Models.

    Capability (e.g. GenerateImage)
        -> Provider (e.g. ComfyUI, Replicate, LocalSD)
            -> Model (e.g. Flux, SDXL, Gemini)

    Agents never know which backend executes their request.
    """

    def __init__(self):
        pass

    def register_provider(self, capability_type: CapabilityType,
                          provider_name: str, provider_instance: object) -> None:
        """Register a provider implementation for a capability."""
        raise NotImplementedError("CapabilityRegistry.register_provider stub")

    def list_capabilities(self) -> List[CapabilityType]:
        """List all registered capabilities."""
        raise NotImplementedError("CapabilityRegistry.list_capabilities stub")

    def list_providers(self, capability_type: CapabilityType) -> List[str]:
        """List all providers available for a capability."""
        raise NotImplementedError("CapabilityRegistry.list_providers stub")

    def execute(self, request: ToolRequest) -> ToolResponse:
        """Route a ToolRequest to the appropriate provider and model."""
        raise NotImplementedError("CapabilityRegistry.execute stub")
