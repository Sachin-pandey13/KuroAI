import time
import os
from typing import List
from openai import OpenAI, OpenAIError
from backend.contracts.capability import ToolRequest, ToolResponse, CapabilityType
from backend.capabilities.providers.base_provider import BaseProvider

class OpenAIProvider(BaseProvider):
    """
    Thin adapter for OpenAI's REST API using the official SDK.
    Responsible only for payload translation and telemetry.
    """

    def __init__(self, api_key: str = None):
        self._api_key = api_key or os.getenv("OPENAI_API_KEY")
        self._client = OpenAI(api_key=self._api_key) if self._api_key else None

    @property
    def provider_name(self) -> str:
        return "openai"

    @property
    def supported_models(self) -> List[str]:
        return ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo"]

    def execute(self, request: ToolRequest) -> ToolResponse:
        start_time = time.time()
        model = request.preferred_model or "gpt-4o-mini"
        
        # Guard against uninitialized client
        if not self._client:
            return ToolResponse(
                request_id=request.request_id,
                success=False,
                capability_type=request.capability_type,
                provider_name=self.provider_name,
                model_name=model,
                error_message="OPENAI_API_KEY is not set or client uninitialized.",
                execution_time_ms=(time.time() - start_time) * 1000
            )

        try:
            # We only support text and vision text for now via chat completions
            if request.capability_type not in (CapabilityType.GENERATE_TEXT, CapabilityType.VISION_REVIEW):
                raise ValueError(f"Capability {request.capability_type} not supported by OpenAIProvider")

            messages = request.parameters.get("messages", [])
            if not messages:
                # Fallback to simple prompt if messages not provided
                prompt = request.parameters.get("prompt", "")
                messages = [{"role": "user", "content": prompt}]

            response = self._client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=request.parameters.get("temperature", 0.7),
                max_tokens=request.parameters.get("max_tokens", None)
            )

            end_time = time.time()
            content = response.choices[0].message.content

            token_usage = {}
            if response.usage:
                token_usage = {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
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
                provenance_metadata={"system_fingerprint": response.system_fingerprint}
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
                execution_time_ms=(end_time - start_time) * 1000
            )

    def health_check(self, live: bool = False) -> bool:
        if not self._api_key:
            return False
        if not live:
            return True
        # Live ping
        try:
            self._client.models.list()
            return True
        except Exception:
            return False
