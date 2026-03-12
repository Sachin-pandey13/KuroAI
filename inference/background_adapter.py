# inference/background_adapter.py

import os
import replicate
import requests
from PIL import Image
from io import BytesIO


class BackgroundAdapter:
    def __init__(self):
        token = os.environ.get("REPLICATE_API_TOKEN")
        if not token:
            raise RuntimeError("REPLICATE_API_TOKEN not set")

        os.environ["REPLICATE_API_TOKEN"] = token

        # Correct Replicate model
        self.model = "stability-ai/stable-diffusion@db21e45e0c1f4b1c6d94b6a8c59c3c8b2d5e8b0c"


    def generate(self, prompt: str, negative_prompt: str) -> Image.Image:
        output = replicate.run(
            self.model,
            input={
                "prompt": prompt,
                "negative_prompt": negative_prompt,
                "width": 768,
                "height": 512,
                "num_inference_steps": 28,
                "guidance_scale": 7.0
            }
        )

        image_url = output[0]

        response = requests.get(image_url, timeout=120)
        response.raise_for_status()

        return Image.open(BytesIO(response.content))
