# inference/stability_image_adapter.py

import torch
from diffusers import StableDiffusionPipeline
from PIL import Image


class StabilityImageAdapter:
    def __init__(self):
        model_path = "models/sd15/model.safetensors"

        self.pipe = StableDiffusionPipeline.from_single_file(
            model_path,
            torch_dtype=torch.float16
        ).to("cuda")

        self.pipe.enable_attention_slicing()

    def generate(self, prompt: str, seed: int = None) -> Image.Image:
        generator = None

        if seed is not None:
            generator = torch.Generator("cuda").manual_seed(seed)

        image = self.pipe(
            prompt,
            generator=generator,
            num_inference_steps=30,
            guidance_scale=7.5
        ).images[0]

        torch.cuda.empty_cache()

        return image