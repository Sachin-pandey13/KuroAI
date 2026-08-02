import time
from typing import List

from backend.capabilities.providers.base_provider import BaseProvider
from backend.contracts.capability import (
    CapabilityDescriptor,
    CapabilityType,
    ToolRequest,
    ToolResponse,
)


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
        import json
        import uuid

        start_ms = time.monotonic() * 1000

        prompt = request.parameters.get("prompt", "")
        seed = request.parameters.get("seed", 42)
        model = request.parameters.get("model", self.supported_models[0])

        # Detect JSON schema requests (from Phase 2C narrative agents)
        # and return a minimal valid JSON payload so Pydantic validation passes.
        if "JSON schema" in prompt or "model_json_schema" in prompt:
            if "StoryOutline" in prompt:
                generated_text = json.dumps(
                    {
                        "project_id": "mock_project",
                        "title": "Mock Story Title",
                        "logline": "A mock story about mocks.",
                        "beats": [
                            {
                                "beat_id": str(uuid.uuid4()),
                                "title": "Beat 1",
                                "summary": "Something happens.",
                                "emotional_arc": "Neutral",
                                "setting": "A city",
                            }
                        ],
                    }
                )
            elif "CharacterProfile" in prompt:
                generated_text = json.dumps(
                    {
                        "character_id": str(uuid.uuid4()),
                        "name": "Mock Character",
                        "age": "25",
                        "role": "Protagonist",
                        "personality": "Brave and curious.",
                        "backstory": "A humble origin.",
                        "appearance": {
                            "hair": "Black",
                            "eyes": "Brown",
                            "build": "Athletic",
                            "clothing": "Jacket",
                            "distinguishing_features": "None",
                        },
                        "relationships": [],
                    }
                )
            elif "SceneScript" in prompt:
                generated_text = json.dumps(
                    {
                        "scene_id": str(uuid.uuid4()),
                        "beat_id": "b1",
                        "location": "City rooftop",
                        "time_of_day": "Night",
                        "panels": [
                            {
                                "panel_number": 1,
                                "setting_details": "Neon lights below",
                                "action": "Hero stands",
                                "characters_present": [],
                                "camera_angle": "Wide shot",
                            }
                        ],
                    }
                )
            elif "MangaPageLayout" in prompt:
                generated_text = json.dumps(
                    {
                        "page_number": 1,
                        "total_panels": 2,
                        "grid_style": "DYNAMIC_ACTION",
                        "slots": [
                            {
                                "slot_id": "slot_1",
                                "panel_number": 1,
                                "importance": "ESTABLISHING",
                                "shot_type": "Wide shot",
                                "relative_position": "TOP_FULL",
                                "aspect_ratio_suggestion": "16:9",
                                "visual_description": "Establishing shot",
                            },
                            {
                                "slot_id": "slot_2",
                                "panel_number": 2,
                                "importance": "ACTION",
                                "shot_type": "Close-up",
                                "relative_position": "BOTTOM_FULL",
                                "aspect_ratio_suggestion": "4:3",
                                "visual_description": "Close up shot",
                            },
                        ],
                    }
                )
            elif "SceneDialogue" in prompt:
                generated_text = json.dumps(
                    {
                        "scene_id": str(uuid.uuid4()),
                        "bubbles": [
                            {
                                "bubble_id": str(uuid.uuid4()),
                                "panel_number": 1,
                                "character_id": None,
                                "dialogue_type": "NARRATION",
                                "text": "The city never sleeps.",
                                "emotion_tag": "Neutral",
                            }
                        ],
                    }
                )
            elif "ReviewFeedback" in prompt:
                generated_text = json.dumps(
                    {
                        "target_artifact_id": "art_img_1",
                        "reviewer_agent": "image_review_agent",
                        "passed": True,
                        "review_score": 92.5,
                        "confidence": 0.95,
                        "issues": [],
                    }
                )
            elif "ContinuityReport" in prompt:
                generated_text = json.dumps(
                    {
                        "project_id": "proj_mock",
                        "passed": True,
                        "review_score": 95.0,
                        "issues": [],
                        "characters_checked": ["c1"],
                        "scenes_checked": 2,
                    }
                )
            elif "ExportManifest" in prompt:
                generated_text = json.dumps(
                    {
                        "project_id": "proj_export",
                        "title": "Mock Manga Title",
                        "total_pages": 1,
                        "pages": [
                            {
                                "page_number": 1,
                                "grid_style": "DYNAMIC_ACTION",
                                "panels": [
                                    {
                                        "panel_number": 1,
                                        "image_asset_path": "/assets/panel_1.png",
                                        "shot_type": "Wide",
                                        "speech_bubbles": [],
                                    }
                                ],
                            }
                        ],
                        "export_format": "PDF_MANIFEST",
                        "output_pdf_path": "/exports/proj_export_manga.pdf",
                    }
                )
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

    def health_check(self, live: bool = False) -> bool:
        return True
