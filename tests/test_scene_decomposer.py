import os

import pytest

scene_decomposer = pytest.importorskip("pipeline.scene_decomposer")


@pytest.mark.skipif(
    not os.getenv("ENABLE_LEGACY_PIPELINE_TESTS"),
    reason="Legacy scene decomposer test requires live pipeline environment",
)
def test_scene_decomposition():
    decomposer = scene_decomposer.SceneDecomposer()

    scene = {
        "scene_id": 1,
        "setting": "City at night",
        "action": "Hero watches from rooftop",
        "emotion": "Brooding",
        "visual_prompt": "dark cyberpunk city, rain, neon lights",
    }

    result = decomposer.decompose(scene)

    assert result["page"] == 1
    assert result["panel"] == 1
    assert "dark cyberpunk city" in result["positive_prompt"]
    assert "low quality" in result["negative_prompt"]
