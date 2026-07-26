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
        import json, uuid
        start_ms = time.monotonic() * 1000

        prompt = request.parameters.get("prompt", "")
        seed = request.parameters.get("seed", 42)
        model = request.parameters.get("model", self.supported_models[0])

        # Detect JSON schema requests (from Phase 2C narrative agents)
        # and return a minimal valid JSON payload so Pydantic validation passes.
        if "JSON schema" in prompt or "model_json_schema" in prompt:
            if "StoryOutline" in prompt or "story_outline" in prompt.lower():
                generated_text = json.dumps({
                    "project_id": "mock_project",
                    "title": "Mock Story Title",
                    "logline": "A mock story about mocks.",
                    "beats": [{"beat_id": str(uuid.uuid4()), "title": "Beat 1", "summary": "Something happens.", "emotional_arc": "Neutral", "setting": "A city"}],
                })
            elif "CharacterProfile" in prompt or "character_profile" in prompt.lower():
                generated_text = json.dumps({
                    "character_id": str(uuid.uuid4()),
                    "name": "Mock Character",
                    "age": "25",
                    "role": "Protagonist",
                    "personality": "Brave and curious.",
                    "backstory": "A humble origin.",
                    "appearance": {"hair": "Black", "eyes": "Brown", "build": "Athletic", "clothing": "Jacket", "distinguishing_features": "None"},
                    "relationships": [],
                })
            elif "SceneScript" in prompt or "scene_script" in prompt.lower():
                generated_text = json.dumps({
                    "scene_id": str(uuid.uuid4()),
                    "beat_id": "b1",
                    "location": "City rooftop",
                    "time_of_day": "Night",
                    "panels": [{"panel_number": 1, "setting_details": "Neon lights below", "action": "Hero stands", "characters_present": [], "camera_angle": "Wide shot"}],
                })
            elif "SceneDialogue" in prompt or "dialogue" in prompt.lower():
                generated_text = json.dumps({
                    "scene_id": str(uuid.uuid4()),
                    "bubbles": [{"bubble_id": str(uuid.uuid4()), "panel_number": 1, "character_id": None, "dialogue_type": "NARRATION", "text": "The city never sleeps.", "emotion_tag": "Neutral"}],
                })
            else:
                generated_text = json.dumps({"mock": "response"})
        else:
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
