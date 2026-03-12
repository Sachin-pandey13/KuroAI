import os
import google.generativeai as genai
from PIL import Image
from io import BytesIO
import base64


class GeminiImageAdapter:
    def __init__(self):
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError("GEMINI_API_KEY not set")

        genai.configure(api_key=api_key)

        self.model = genai.GenerativeModel(
            model_name="models/gemini-1.5-flash-image-preview"
        )

    def generate(self, prompt: str, negative_prompt: str = "") -> Image.Image:
        full_prompt = f"""
        Generate a manga-style image.

        Prompt:
        {prompt}

        Avoid:
        {negative_prompt}
        """

        response = self.model.generate_content(full_prompt)

        for part in response.candidates[0].content.parts:
            if "inline_data" in part:
                image_bytes = base64.b64decode(part.inline_data.data)
                return Image.open(BytesIO(image_bytes))

        raise RuntimeError("Gemini did not return an image")
