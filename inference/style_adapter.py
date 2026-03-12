from PIL import Image, ImageDraw


class StyleAdapter:
    def apply(self, image: Image.Image, panel: dict) -> Image.Image:
        draw = ImageDraw.Draw(image)
        draw.text((20, 450), "Style: KuroAI Ink", fill=(0, 0, 0))
        return image
