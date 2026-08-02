import time
from typing import List

from backend.capabilities.providers.base_provider import BaseProvider
from backend.contracts.capability import (
    CapabilityDescriptor,
    CapabilityType,
    ToolRequest,
    ToolResponse,
)


class MockImageProvider(BaseProvider):
    """
    Deterministic image generation provider for offline testing and CI.
    Produces reproducible metadata outputs without calling any image generation API.
    """

    @property
    def provider_name(self) -> str:
        return "mock_image_provider"

    @property
    def supported_models(self) -> List[str]:
        return ["mock-flux-1-dev", "mock-sdxl"]

    @property
    def descriptor(self) -> CapabilityDescriptor:
        return CapabilityDescriptor(
            capability_type=CapabilityType.GENERATE_IMAGE,
            provider_name=self.provider_name,
            supported_models=self.supported_models,
            supports_streaming=False,
            supports_json=True,
            supports_seed=True,
            supports_vision=False,
            max_context_length=512,
        )

    def execute(self, request: ToolRequest) -> ToolResponse:
        """Execute deterministic image generation."""
        start_ms = time.monotonic() * 1000

        prompt = request.parameters.get("prompt", "")
        seed = request.parameters.get("seed", 42)
        width = request.parameters.get("width", 1024)
        height = request.parameters.get("height", 1024)
        model = request.parameters.get("model", self.supported_models[0])

        image_path = f"/mock/output/{model}_seed{seed}_w{width}_h{height}.png"

        elapsed_ms = time.monotonic() * 1000 - start_ms

        return ToolResponse(
            request_id=request.request_id,
            success=True,
            capability_type=CapabilityType.GENERATE_IMAGE,
            provider_name=self.provider_name,
            model_name=model,
            output_data={
                "image_path": image_path,
                "width": width,
                "height": height,
                "format": "png",
            },
            execution_time_ms=round(elapsed_ms, 3),
            token_usage={},
            cost_usd=0.0,
            provenance_metadata={
                "seed": seed,
                "prompt": prompt[:200],
                "width": width,
                "height": height,
                "provider": self.provider_name,
                "model": model,
            },
        )

    def health_check(self, live: bool = False) -> bool:
        return True
