import os

import pytest

orchestrator = pytest.importorskip("pipeline.orchestrator")


@pytest.mark.skipif(
    not os.getenv("ENABLE_LEGACY_PIPELINE_TESTS"),
    reason="Legacy orchestrator test requires live OpenAI API key",
)
def test_end_to_end_run():
    app = orchestrator.KuroAIOrchestrator()
    result = app.run("A noir city mystery")

    assert "images" in result
    assert len(result["images"]) > 0
