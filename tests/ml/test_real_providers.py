import os

import pytest

pytest.importorskip("anthropic")
pytest.importorskip("openai")

from backend.capabilities.providers.anthropic_provider import AnthropicProvider
from backend.capabilities.providers.gemini_provider import GeminiProvider
from backend.capabilities.providers.httpx_providers import (
    Automatic1111Provider,
    ComfyUIProvider,
    LocalLlamaProvider,
)
from backend.capabilities.providers.openai_provider import OpenAIProvider
from backend.contracts.capability import CapabilityType
from tests.test_provider_contract import verify_provider_contract

pytestmark = pytest.mark.skipif(
    os.getenv("TEST_REAL_PROVIDERS") != "1",
    reason="Skipping live provider tests. Set TEST_REAL_PROVIDERS=1 to run.",
)


@pytest.fixture
def text_params():
    return {"prompt": "Say 'hello' in one word.", "max_tokens": 10, "temperature": 0.0}


def test_openai_provider_contract(text_params):
    provider = OpenAIProvider()
    verify_provider_contract(
        provider, CapabilityType.GENERATE_TEXT, valid_params=text_params, invalid_params={}
    )


def test_anthropic_provider_contract(text_params):
    provider = AnthropicProvider()
    verify_provider_contract(
        provider, CapabilityType.GENERATE_TEXT, valid_params=text_params, invalid_params={}
    )


def test_gemini_provider_contract(text_params):
    provider = GeminiProvider()
    verify_provider_contract(
        provider, CapabilityType.GENERATE_TEXT, valid_params=text_params, invalid_params={}
    )


def test_local_llama_provider_contract(text_params):
    provider = LocalLlamaProvider()
    verify_provider_contract(
        provider, CapabilityType.GENERATE_TEXT, valid_params=text_params, invalid_params={}
    )


def test_comfyui_provider_contract():
    provider = ComfyUIProvider()
    verify_provider_contract(
        provider,
        CapabilityType.GENERATE_IMAGE,
        valid_params={
            "workflow": {"3": {"inputs": {"text": "hello"}, "class_type": "CLIPTextEncode"}}
        },
        invalid_params={},
    )


def test_automatic1111_provider_contract():
    provider = Automatic1111Provider()
    verify_provider_contract(
        provider,
        CapabilityType.GENERATE_IMAGE,
        valid_params={"prompt": "A cute cat"},
        invalid_params={},
    )
