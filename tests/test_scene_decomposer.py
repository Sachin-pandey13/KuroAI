from pipeline.scene_decomposer import SceneDecomposer


def test_scene_decomposition():
    decomposer = SceneDecomposer()

    scene = {
        "scene_id": 1,
        "setting": "City at night",
        "action": "Hero watches from rooftop",
        "emotion": "Brooding",
        "visual_prompt": "dark cyberpunk city, rain, neon lights"
    }

    result = decomposer.decompose(scene)

    assert "positive_prompt" in result
    assert "negative_prompt" in result
    assert "camera" in result
    assert "lighting" in result
    assert result["style_anchor"] == "kuroai_manga_v1"
