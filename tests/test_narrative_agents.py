import json

import pytest

from backend.agents.character_agent import CharacterAgent
from backend.agents.dialogue_agent import DialogueAgent
from backend.agents.story_agent import StoryAgent
from backend.agents.tool_executor import BaseToolExecutor
from backend.contracts.capability import ToolRequest, ToolResponse
from backend.contracts.context import AgentContext


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


@pytest.mark.asyncio
async def test_story_agent_valid_json():
    agent = StoryAgent()
    valid_json = json.dumps(
        {
            "project_id": "proj1",
            "title": "Cyberpunk City",
            "logline": "A story about a neon city.",
            "beats": [
                {
                    "beat_id": "b1",
                    "title": "Intro",
                    "summary": "Start",
                    "emotional_arc": "Neutral",
                    "setting": "Street",
                }
            ],
        }
    )
    executor = MockJSONProvider(valid_json)
    ctx = AgentContext(
        task_id="t1", goal_id="g1", project_id="p1", target_agent_type="STORY", sections=[]
    )

    result = await agent.execute(ctx, executor)
    assert result.success is True
    assert len(result.produced_artifacts) == 1
    assert result.produced_artifacts[0].artifact_type == "STORY_OUTLINE"


@pytest.mark.asyncio
async def test_agent_schema_robustness_malformed_json():
    # Intentionally malformed JSON
    agent = StoryAgent()
    malformed_json = '{"project_id": "proj1", "title": "Missing quotes and brace'
    executor = MockJSONProvider(malformed_json)
    ctx = AgentContext(
        task_id="t1", goal_id="g1", project_id="p1", target_agent_type="STORY", sections=[]
    )

    result = await agent.execute(ctx, executor)
    assert result.success is False
    assert (
        "JSON validation error" in result.error_message
        or "validation error" in result.error_message.lower()
    )


@pytest.mark.asyncio
async def test_agent_schema_robustness_invalid_schema():
    # Valid JSON, but missing required fields
    agent = CharacterAgent()
    invalid_schema_json = json.dumps(
        {
            "name": "Hiro",
            # missing character_id, age, role, etc.
        }
    )
    executor = MockJSONProvider(invalid_schema_json)
    ctx = AgentContext(
        task_id="t1", goal_id="g1", project_id="p1", target_agent_type="CHARACTER", sections=[]
    )

    result = await agent.execute(ctx, executor)
    assert result.success is False
    assert "validation error" in result.error_message.lower()


@pytest.mark.asyncio
async def test_dialogue_agent_valid_json():
    agent = DialogueAgent()
    valid_json = json.dumps(
        {
            "scene_id": "s1",
            "bubbles": [
                {
                    "bubble_id": "b1",
                    "panel_number": 1,
                    "character_id": "c1",
                    "dialogue_type": "SPEECH",
                    "text": "Hello",
                }
            ],
        }
    )
    executor = MockJSONProvider(valid_json)
    ctx = AgentContext(
        task_id="t1", goal_id="g1", project_id="p1", target_agent_type="DIALOGUE", sections=[]
    )

    result = await agent.execute(ctx, executor)
    assert result.success is True
    assert len(result.produced_artifacts) == 1
    assert result.produced_artifacts[0].artifact_type == "SPEECH_BUBBLE"
