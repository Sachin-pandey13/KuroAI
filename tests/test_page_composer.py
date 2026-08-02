import os

import pytest

page_composer = pytest.importorskip("pipeline.page_composer")


@pytest.mark.skipif(
    not os.getenv("ENABLE_LEGACY_PIPELINE_TESTS"),
    reason="Legacy page composer test requires live pipeline environment",
)
def test_page_composition():
    composer = page_composer.PageComposer(panels_per_page=3)

    scenes = [
        {"positive_prompt": "scene 1", "style_anchor": "kuroai_manga_v1"},
        {"positive_prompt": "scene 2", "style_anchor": "kuroai_manga_v1"},
        {"positive_prompt": "scene 3", "style_anchor": "kuroai_manga_v1"},
        {"positive_prompt": "scene 4", "style_anchor": "kuroai_manga_v1"},
    ]

    pages = composer.compose(scenes)

    assert len(pages) == 2
    assert len(pages[0]["panels"]) == 3
    assert len(pages[1]["panels"]) == 1
