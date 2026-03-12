from pipeline.orchestrator import KuroAIOrchestrator

def test_end_to_end_run():
    app = KuroAIOrchestrator()
    result = app.run("A noir city mystery")

    assert "images" in result
    assert len(result["images"]) > 0
