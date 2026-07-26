import pytest
import json
from pydantic import BaseModel, Field

from backend.agents.output_parser import OutputParser
from backend.contracts.context import AgentContext, ContextSection, ContextSectionType
from backend.contracts.capability import ToolRequest, ToolResponse, CapabilityType
from backend.contracts.artifact import ArtifactType
from backend.agents.tool_executor import BaseToolExecutor

from backend.agents.layout_agent import LayoutAgent
from backend.agents.continuity_agent import (
    ContinuityAgent,
    CharacterAppearanceRule,
    RelationshipRule,
)
from backend.agents.image_review_agent import ImageReviewAgent
from backend.contracts.layout import MangaPageLayout
from backend.contracts.review import ReviewFeedback, ContinuityReport, ReviewSeverity


class MockJSONProvider(BaseToolExecutor):
    def __init__(self, response_json: str, success: bool = True):
        self.response_json = response_json
        self.success = success

    async def execute(self, request: ToolRequest) -> ToolResponse:
        return ToolResponse(
            request_id=request.request_id,
            success=self.success,
            capability_type=request.capability_type,
            provider_name="mock_json_provider",
            model_name="mock_json_model",
            output_data={"text": self.response_json} if self.success else {},
            error_message=None if self.success else "Mock failure",
        )


class DummyModel(BaseModel):
    name: str
    count: int


# =====================================================================
# OutputParser Tests
# =====================================================================

def test_output_parser_strips_markdown_and_parses():
    raw_markdown = """```json
    {
        "name": "KuroAI",
        "count": 42
    }
    ```"""
    parsed = OutputParser.parse_json(raw_markdown, DummyModel)
    assert parsed is not None
    assert parsed.name == "KuroAI"
    assert parsed.count == 42


def test_output_parser_returns_none_on_invalid_json():
    invalid_json = "```json\n{ invalid_json: \n```"
    parsed = OutputParser.parse_json(invalid_json, DummyModel)
    assert parsed is None


# =====================================================================
# LayoutAgent Tests
# =====================================================================

@pytest.mark.asyncio
async def test_layout_agent_valid_json():
    agent = LayoutAgent()
    valid_json = json.dumps({
        "page_number": 1,
        "total_panels": 2,
        "grid_style": "DYNAMIC_ACTION",
        "slots": [
            {
                "slot_id": "s1",
                "panel_number": 1,
                "importance": "ESTABLISHING",
                "shot_type": "Wide shot",
                "relative_position": "TOP_FULL",
                "aspect_ratio_suggestion": "16:9",
                "visual_description": "Establishing shot of city"
            }
        ]
    })
    executor = MockJSONProvider(valid_json)
    ctx = AgentContext(task_id="t1", goal_id="g1", project_id="p1", target_agent_type="LAYOUT", sections=[])

    result = await agent.execute(ctx, executor)
    assert result.success is True
    assert len(result.produced_artifacts) == 1
    assert result.produced_artifacts[0].artifact_type == ArtifactType.MANGA_PAGE_LAYOUT


@pytest.mark.asyncio
async def test_layout_agent_malformed_json():
    agent = LayoutAgent()
    executor = MockJSONProvider("```json\n{ malformed: \n```")
    ctx = AgentContext(task_id="t1", goal_id="g1", project_id="p1", target_agent_type="LAYOUT", sections=[])

    result = await agent.execute(ctx, executor)
    assert result.success is False
    assert "JSON validation error" in result.error_message


# =====================================================================
# ContinuityAgent Tests & Multiple Rules Aggregation
# =====================================================================

def test_continuity_multiple_rules_aggregation():
    """Verify that ContinuityAgent correctly aggregates multiple rule hits."""
    chars = [
        {
            "character_id": "c1",
            "name": "Ren",
            "appearance": {"hair": "blonde", "eyes": "blue"},
            "relationships": [{"target_character_id": "c2", "relationship_type": "enemy"}]
        },
        {
            "character_id": "c2",
            "name": "Kaito",
            "appearance": {"hair": "black", "eyes": "brown"},
            "relationships": []
        }
    ]
    scenes = [
        {
            "scene_id": "s1",
            "panels": [
                # Trigger appearance rule: Ren has dark hair in action
                {"panel_number": 1, "action": "Ren stands with dark hair looking around"},
                # Trigger relationship rule: enemies hugging warmly
                {"panel_number": 2, "action": "Ren and Kaito hugs warmly as best friends"}
            ]
        }
    ]

    rule1 = CharacterAppearanceRule()
    rule2 = RelationshipRule()

    issues1 = rule1.evaluate(chars, scenes)
    issues2 = rule2.evaluate(chars, scenes)

    assert len(issues1) == 1
    assert issues1[0].severity == ReviewSeverity.WARNING

    assert len(issues2) == 1
    assert issues2[0].severity == ReviewSeverity.ERROR

    agent = ContinuityAgent(rules=[rule1, rule2])
    ctx = AgentContext(
        task_id="t1",
        goal_id="g1",
        project_id="p1",
        target_agent_type="CONTINUITY",
        sections=[
            ContextSection(section_type=ContextSectionType.ARTIFACT, title="Char", content={"artifact_type": "CHARACTER_PROFILE", "data": chars[0]}),
            ContextSection(section_type=ContextSectionType.ARTIFACT, title="Char2", content={"artifact_type": "CHARACTER_PROFILE", "data": chars[1]}),
            ContextSection(section_type=ContextSectionType.ARTIFACT, title="Scene", content={"artifact_type": "SCENE_SCRIPT", "data": scenes[0]}),
        ]
    )

    # Execute without executor to rely strictly on rule engine pipeline
    import asyncio
    result = asyncio.run(agent.execute(ctx, tool_executor=None))
    assert result.success is True
    report_data = result.produced_artifacts[0].data
    assert report_data["passed"] is False  # ERROR severity issue present
    assert len(report_data["issues"]) == 2


# =====================================================================
# ImageReviewAgent Tests
# =====================================================================

@pytest.mark.asyncio
async def test_image_review_agent_passes():
    agent = ImageReviewAgent()
    valid_json = json.dumps({
        "target_artifact_id": "art_1",
        "reviewer_agent": "image_review_agent",
        "passed": True,
        "review_score": 95.0,
        "confidence": 0.98,
        "issues": []
    })
    executor = MockJSONProvider(valid_json)
    ctx = AgentContext(task_id="t1", goal_id="g1", project_id="p1", target_agent_type="IMAGE_REVIEW", sections=[])

    result = await agent.execute(ctx, executor)
    assert result.success is True
    assert result.produced_artifacts[0].artifact_type == ArtifactType.REVIEW_FEEDBACK
    assert result.produced_artifacts[0].data["passed"] is True
    assert result.produced_artifacts[0].data["review_score"] == 95.0
