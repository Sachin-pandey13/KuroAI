from pipeline.page_composer import PageComposer


def test_page_composition():
    composer = PageComposer(panels_per_page=3)

    scenes = [
        {"positive_prompt": "scene 1", "style_anchor": "kuroai_manga_v1"},
        {"positive_prompt": "scene 2", "style_anchor": "kuroai_manga_v1"},
        {"positive_prompt": "scene 3", "style_anchor": "kuroai_manga_v1"},
        {"positive_prompt": "scene 4", "style_anchor": "kuroai_manga_v1"}
    ]

    pages = composer.compose(scenes)

    assert pages[0]["page"] == 1
    assert pages[0]["panel"] == 1
    assert pages[2]["page"] == 1
    assert pages[3]["page"] == 2
