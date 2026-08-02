import pytest

pytest.importorskip("jsonschema")

from inference.story_planner import StoryPlanner


def test_story_planner_output():
    planner = StoryPlanner()
    story = planner.generate("A dark cyberpunk revenge story")

    assert "title" in story
    assert "genre" in story
    assert len(story["scenes"]) >= 3
    assert all("visual_prompt" in s for s in story["scenes"])
