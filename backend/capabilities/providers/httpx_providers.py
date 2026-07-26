import time
import os
import httpx
from typing import List, Dict, Any
from backend.contracts.capability import ToolRequest, ToolResponse, CapabilityType
from backend.capabilities.providers.base_provider import BaseProvider

class LocalLlamaProvider(BaseProvider):
    """
    Thin adapter for a Local LLaMA API (e.g. Ollama or vLLM).
    Uses raw httpx since the REST API is simple and SDKs add little value.
    """

    def __init__(self, endpoint_url: str = None):
        self._endpoint = endpoint_url or os.getenv("OLLAMA_ENDPOINT", "http://localhost:11434/api/generate")

    @property
    def provider_name(self) -> str:
        return "local_llama"

    @property
    def supported_models(self) -> List[str]:
        return ["llama3", "mistral", "mixtral"]

    def execute(self, request: ToolRequest) -> ToolResponse:
        start_time = time.time()
        model = request.preferred_model or "llama3"
        
        try:
            if request.capability_type != CapabilityType.GENERATE_TEXT:
                raise ValueError(f"Capability {request.capability_type} not supported by LocalLlamaProvider")

            prompt = request.parameters.get("prompt", "")
            if not prompt and "messages" in request.parameters:
                messages = request.parameters["messages"]
                prompt = "\n".join([f'{m.get("role", "user")}: {m.get("content", "")}' for m in messages])

            payload = {
                "model": model,
                "prompt": prompt,
                "stream": False
            }

            with httpx.Client(timeout=60.0) as client:
                response = client.post(self._endpoint, json=payload)
                response.raise_for_status()
                data = response.json()

            end_time = time.time()
            content = data.get("response", "")

            return ToolResponse(
                request_id=request.request_id,
                success=True,
                capability_type=request.capability_type,
                provider_name=self.provider_name,
                model_name=model,
                output_data={"text": content},
                execution_time_ms=(end_time - start_time) * 1000,
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
        if not live:
            return True
        try:
            with httpx.Client(timeout=2.0) as client:
                # Ollama root endpoint
                base = self._endpoint.replace("/api/generate", "")
                r = client.get(base)
                return r.status_code == 200
        except Exception:
            return False


class ComfyUIProvider(BaseProvider):
    """
    Thin adapter for ComfyUI.
    Expects a pre-built workflow JSON in request.parameters["workflow"].
    """
    def __init__(self, endpoint_url: str = None):
        self._endpoint = endpoint_url or os.getenv("COMFYUI_ENDPOINT", "http://127.0.0.1:8188")

    @property
    def provider_name(self) -> str:
        return "comfyui"

    @property
    def supported_models(self) -> List[str]:
        return ["comfy-workflow"]

    def execute(self, request: ToolRequest) -> ToolResponse:
        start_time = time.time()
        model = "comfy-workflow"
        
        try:
            if request.capability_type != CapabilityType.GENERATE_IMAGE:
                raise ValueError(f"Capability {request.capability_type} not supported by ComfyUIProvider")

            workflow = request.parameters.get("workflow")
            if not workflow:
                raise ValueError("ComfyUI requires a 'workflow' parameter in ToolRequest")

            payload = {"prompt": workflow}

            with httpx.Client(timeout=120.0) as client:
                response = client.post(f"{self._endpoint}/prompt", json=payload)
                response.raise_for_status()
                data = response.json()
                prompt_id = data.get("prompt_id")

            end_time = time.time()
            # In a real sync adapter, we'd poll or use websockets for completion.
            # For this thin adapter, we return the prompt_id in output_data. 
            # A higher level executor handles async polling if needed, or we do basic polling here.
            # To keep it completely stateless and thin, returning the prompt_id is best,
            # or doing a simple synchronous block if the architecture demands it.
            # We'll return the prompt_id so the orchestrator can track it.
            
            return ToolResponse(
                request_id=request.request_id,
                success=True,
                capability_type=request.capability_type,
                provider_name=self.provider_name,
                model_name=model,
                output_data={"prompt_id": prompt_id, "status": "queued"},
                execution_time_ms=(end_time - start_time) * 1000,
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
        if not live:
            return True
        try:
            with httpx.Client(timeout=2.0) as client:
                r = client.get(f"{self._endpoint}/system_stats")
                return r.status_code == 200
        except Exception:
            return False


class Automatic1111Provider(BaseProvider):
    """
    Thin adapter for Automatic1111/WebUI REST API.
    """
    def __init__(self, endpoint_url: str = None):
        self._endpoint = endpoint_url or os.getenv("SD_WEBUI_ENDPOINT", "http://127.0.0.1:7860")

    @property
    def provider_name(self) -> str:
        return "automatic1111"

    @property
    def supported_models(self) -> List[str]:
        return ["sdxl", "sd-1.5"]

    def execute(self, request: ToolRequest) -> ToolResponse:
        start_time = time.time()
        model = request.preferred_model or "sdxl"
        
        try:
            if request.capability_type != CapabilityType.GENERATE_IMAGE:
                raise ValueError(f"Capability {request.capability_type} not supported by Automatic1111Provider")

            prompt = request.parameters.get("prompt")
            if not prompt:
                raise ValueError("Automatic1111 requires a 'prompt' parameter")

            payload = {
                "prompt": prompt,
                "negative_prompt": request.parameters.get("negative_prompt", ""),
                "steps": request.parameters.get("steps", 20),
                "width": request.parameters.get("width", 1024),
                "height": request.parameters.get("height", 1024),
                "send_images": True,
                "save_images": False
            }

            with httpx.Client(timeout=120.0) as client:
                response = client.post(f"{self._endpoint}/sdapi/v1/txt2img", json=payload)
                response.raise_for_status()
                data = response.json()

            end_time = time.time()
            images = data.get("images", [])
            
            return ToolResponse(
                request_id=request.request_id,
                success=True,
                capability_type=request.capability_type,
                provider_name=self.provider_name,
                model_name=model,
                output_data={"images_base64": images},
                execution_time_ms=(end_time - start_time) * 1000,
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
        if not live:
            return True
        try:
            with httpx.Client(timeout=2.0) as client:
                r = client.get(f"{self._endpoint}/sdapi/v1/sd-models")
                return r.status_code == 200
        except Exception:
            return False
