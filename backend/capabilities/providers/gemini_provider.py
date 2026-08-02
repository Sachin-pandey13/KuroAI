import os
import time
from typing import Dict, List, Optional

from google import genai

from backend.capabilities.providers.base_provider import BaseProvider
from backend.contracts.capability import CapabilityType, ToolRequest, ToolResponse


class GeminiProvider(BaseProvider):
    """
    Thin adapter for Gemini API using the official google-genai SDK.
    """

    def __init__(self, api_key: Optional[str] = None):
        self._api_key = api_key or os.getenv("GEMINI_API_KEY")
        self._client = genai.Client(api_key=self._api_key) if self._api_key else None

    @property
    def provider_name(self) -> str:
        return "gemini"

    @property
    def supported_models(self) -> List[str]:
        return ["gemini-2.5-flash", "gemini-2.5-pro", "gemini-1.5-pro"]

    def execute(self, request: ToolRequest) -> ToolResponse:
        start_time = time.time()
        model = request.preferred_model or "gemini-2.5-flash"

        if not self._client:
            return ToolResponse(
                request_id=request.request_id,
                success=False,
                capability_type=request.capability_type,
                provider_name=self.provider_name,
                model_name=model,
                error_message="GEMINI_API_KEY is not set or client uninitialized.",
                execution_time_ms=(time.time() - start_time) * 1000,
            )

        try:
            if request.capability_type not in (
                CapabilityType.GENERATE_TEXT,
                CapabilityType.VISION_REVIEW,
            ):
                raise ValueError(
                    f"Capability {request.capability_type} not supported by GeminiProvider"
                )

            prompt = request.parameters.get("prompt", "")
            if not prompt and "messages" in request.parameters:
                # Naive message conversion for now since Gemini contents format is different
                messages = request.parameters["messages"]
                prompt = "\n".join(
                    [f'{m.get("role", "user")}: {m.get("content", "")}' for m in messages]
                )

            # config logic if needed (temperature, max_tokens)
            config = {}
            if "temperature" in request.parameters:
                config["temperature"] = request.parameters["temperature"]
            if "max_tokens" in request.parameters:
                config["max_output_tokens"] = request.parameters["max_tokens"]

            response = self._client.models.generate_content(
                model=model,
                contents=prompt,
                config=genai.types.GenerateContentConfig(**config) if config else None,
            )

            end_time = time.time()
            content = response.text

            token_usage: Dict[str, int] = {}
            if hasattr(response, "usage_metadata") and response.usage_metadata:
                token_usage = {
                    "prompt_tokens": int(response.usage_metadata.prompt_token_count or 0),
                    "completion_tokens": int(response.usage_metadata.candidates_token_count or 0),
                    "total_tokens": int(response.usage_metadata.total_token_count or 0),
                }

            return ToolResponse(
                request_id=request.request_id,
                success=True,
                capability_type=request.capability_type,
                provider_name=self.provider_name,
                model_name=model,
                output_data={"text": content},
                execution_time_ms=(end_time - start_time) * 1000,
                token_usage=token_usage,
            )

        except Exception as e:
            end_time = time.time()
            return ToolResponse(
                request_id=request.request_id,
                success=False,
                capability_type=request.capability_type,
                provider_name=self.provider_name,
                model_name=model,
                error_message=str(e),
                execution_time_ms=(end_time - start_time) * 1000,
            )

    def health_check(self, live: bool = False) -> bool:
        if not self._api_key:
            return False
        if not live:
            return True
        return True
