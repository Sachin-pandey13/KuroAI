import os

import pytest

torch = pytest.importorskip("torch")
diffusers = pytest.importorskip("diffusers")

from diffusers import StableDiffusionPipeline  # noqa: E402


@pytest.mark.skipif(
    not os.getenv("ENABLE_LEGACY_PIPELINE_TESTS"),
    reason="Stable Diffusion pipeline test requires local GPU & weights",
)
def test_stable_diffusion_pipeline():
    model_path = "models/sd15/model.safetensors"
    if not os.path.exists(model_path):
        pytest.skip(f"Model file not found at {model_path}")

    pipe = StableDiffusionPipeline.from_single_file(model_path, torch_dtype=torch.float16).to(
        "cuda"
    )

    pipe.enable_attention_slicing()

    prompt = "black and white manga panel, clean line art, professional manga style"
    image = pipe(prompt, num_inference_steps=5, guidance_scale=7.5).images[0]

    assert image is not None
