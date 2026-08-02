import os

from inference.image_generator import ImageGenerator


def test_image_generation_pipeline():
    gen = ImageGenerator()

    panel = {
        "page": 1,
        "panel": 1,
        "prompt": "dark cyberpunk city",
        "layout": "wide",
        "style_anchor": "kuroai_manga_v1",
    }

    result = gen.generate(panel)

    assert os.path.exists(result["image_path"])
