import time
from typing import List
from backend.contracts.capability import (
    CapabilityType,
    CapabilityDescriptor,
    ToolRequest,
    ToolResponse,
)
from backend.capabilities.providers.base_provider import BaseProvider


class MockTextProvider(BaseProvider):
    """
    Deterministic text generation provider for offline testing and CI.
    Produces reproducible outputs without any LLM API calls.
    """

    @property
    def provider_name(self) -> str:
        return "mock_text_provider"

    @property
    def supported_models(self) -> List[str]:
        return ["mock-gpt-4o", "mock-claude-3-5"]

    @property
    def descriptor(self) -> CapabilityDescriptor:
        return CapabilityDescriptor(
            capability_type=CapabilityType.GENERATE_TEXT,
            provider_name=self.provider_name,
            supported_models=self.supported_models,
            supports_streaming=False,
            supports_json=True,
            supports_seed=True,
            supports_vision=False,
            max_context_length=8192,
        )

    def execute(self, request: ToolRequest) -> ToolResponse:
        """Execute deterministic text generation."""
        start_ms = time.monotonic() * 1000

        prompt = request.parameters.get("prompt", "")
        seed = request.parameters.get("seed", 42)
        model = request.parameters.get("model", self.supported_models[0])

        generated_text = (
            f"[MockTextProvider][model={model}][seed={seed}] "
            f"Generated response for prompt: '{prompt[:80]}'"
        )
        prompt_tokens = max(1, len(prompt.split()))
        completion_tokens = max(1, len(generated_text.split()))

        elapsed_ms = time.monotonic() * 1000 - start_ms

        return ToolResponse(
            request_id=request.request_id,
            success=True,
            capability_type=CapabilityType.GENERATE_TEXT,
            provider_name=self.provider_name,
            model_name=model,
            output_data={"text": generated_text},
            execution_time_ms=round(elapsed_ms, 3),
            token_usage={
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": prompt_tokens + completion_tokens,
            },
            cost_usd=0.0,
            provenance_metadata={
                "seed": seed,
                "prompt_length": len(prompt),
                "provider": self.provider_name,
                "model": model,
            },
        )

    def health_check(self) -> bool:
        return True
