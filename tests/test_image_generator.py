import os

import pytest

image_generator = pytest.importorskip("inference.image_generator")


@pytest.mark.skipif(
    not os.getenv("ENABLE_LEGACY_PIPELINE_TESTS"),
    reason="Legacy pipeline test requires live AI weights/API keys",
)
def test_image_generation_pipeline():
    gen = image_generator.ImageGenerator()

    panel = {
        "page": 1,
        "panel": 1,
        "prompt": "dark cyberpunk city",
        "layout": "wide",
        "style_anchor": "kuroai_manga_v1",
    }

    result = gen.generate(panel)

    assert os.path.exists(result["image_path"])
