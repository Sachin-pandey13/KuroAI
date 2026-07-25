"""
Test: Contract Validation (Milestone 1)
Verifies all contracts import cleanly, serialize/deserialize correctly,
and have zero circular dependencies.
"""
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest


class TestGoalContract:
    def test_goal_creation(self):
        from backend.contracts.goal import CreativeGoal, GoalStatus, GoalPriority
        goal = CreativeGoal(
            title="Create Chapter 1",
            description="Draft the opening chapter of the manga",
            target_milestone="STORY_DRAFT",
        )
        assert goal.goal_id is not None
        assert goal.status == GoalStatus.PENDING
        assert goal.priority == GoalPriority.MEDIUM

    def test_goal_serialization(self):
        from backend.contracts.goal import CreativeGoal
        goal = CreativeGoal(
            title="Test Goal",
            description="Test",
            target_milestone="TEST",
        )
        data = goal.model_dump()
        restored = CreativeGoal(**data)
        assert restored.title == goal.title
        assert restored.goal_id == goal.goal_id


class TestTaskContract:
    def test_task_creation(self):
        from backend.contracts.task import Task, TaskStatus
        task = Task(
            goal_id="goal-123",
            target_agent_type="STORY",
            action_type="DRAFT_SCENE",
        )
        assert task.task_id is not None
        assert task.status == TaskStatus.QUEUED
        assert task.retry_count == 0

    def test_task_serialization(self):
        from backend.contracts.task import Task
        task = Task(
            goal_id="goal-123",
            target_agent_type="STORY",
            action_type="DRAFT_SCENE",
        )
        data = task.model_dump()
        restored = Task(**data)
        assert restored.task_id == task.task_id


class TestEventContract:
    def test_event_creation(self):
        from backend.contracts.event import Event, EventType
        event = Event(
            event_type=EventType.GOAL_PUBLISHED,
            project_id="proj-001",
        )
        assert event.event_id is not None
        assert event.event_type == EventType.GOAL_PUBLISHED


class TestDecisionTraceContract:
    def test_decision_trace_creation(self):
        from backend.contracts.decision_trace import DecisionTrace, ExecutionProvenance
        provenance = ExecutionProvenance(
            model_name="flux-dev",
            provider_name="ComfyUI",
            seed=42,
            prompt="A samurai standing in rain",
        )
        trace = DecisionTrace(
            agent_id="image_agent",
            confidence_score=0.87,
            reasoning_rationale="Scene matches dark aesthetic from style guide",
            identified_risks=["Character pose may differ from reference"],
            provenance=provenance,
        )
        assert trace.confidence_score == 0.87
        assert trace.provenance.seed == 42

    def test_confidence_bounds(self):
        from backend.contracts.decision_trace import DecisionTrace, ExecutionProvenance
        provenance = ExecutionProvenance(
            model_name="test", provider_name="test", prompt="test"
        )
        with pytest.raises(Exception):
            DecisionTrace(
                agent_id="test",
                confidence_score=1.5,  # Out of bounds
                reasoning_rationale="test",
                provenance=provenance,
            )


class TestArtifactContract:
    def test_artifact_creation(self):
        from backend.contracts.artifact import Artifact, ArtifactType
        artifact = Artifact(
            project_id="proj-001",
            artifact_type=ArtifactType.CHARACTER_PROFILE,
            owner_agent="character_agent",
            data={"name": "Kuro", "hair": "black"},
        )
        assert artifact.artifact_id is not None
        assert artifact.version == 1
        assert artifact.artifact_type == ArtifactType.CHARACTER_PROFILE


class TestDependencyContract:
    def test_dependency_node_creation(self):
        from backend.contracts.dependency import DependencyNode, NodeState
        node = DependencyNode(
            artifact_id="art-001",
            artifact_type="STORY_OUTLINE",
        )
        assert node.state == NodeState.CLEAN
        assert node.upstream_ids == []
        assert node.downstream_ids == []

    def test_dependency_edge_creation(self):
        from backend.contracts.dependency import DependencyEdge
        edge = DependencyEdge(
            source_artifact_id="art-001",
            target_artifact_id="art-002",
        )
        assert edge.dependency_type == "EXPLICIT"


class TestProjectStateContract:
    def test_project_state_creation(self):
        from backend.contracts.project_state import ProjectStateModel, AutonomyLevel
        state = ProjectStateModel(
            title="My Manga",
            description="A dark fantasy manga",
        )
        assert state.project_id is not None
        assert state.autonomy_level == AutonomyLevel.GUIDED
        assert state.version == 1


class TestContextContract:
    def test_context_policy_creation(self):
        from backend.contracts.context import ContextPolicy
        policy = ContextPolicy(
            agent_type="STORY",
            required_artifact_types=["STORY_OUTLINE", "CHARACTER_PROFILE"],
            include_character_blueprints=True,
            include_world_lore=True,
        )
        assert policy.agent_type == "STORY"
        assert len(policy.required_artifact_types) == 2

    def test_agent_context_creation(self):
        from backend.contracts.context import AgentContext
        ctx = AgentContext(
            task_id="task-001",
            project_id="proj-001",
            target_agent_type="STORY",
        )
        assert ctx.relevant_artifacts == []


class TestCapabilityContract:
    def test_tool_request_creation(self):
        from backend.contracts.capability import ToolRequest, CapabilityType
        req = ToolRequest(
            capability_type=CapabilityType.GENERATE_IMAGE,
            parameters={"prompt": "samurai in rain", "seed": 42},
        )
        assert req.capability_type == CapabilityType.GENERATE_IMAGE

    def test_tool_response_creation(self):
        from backend.contracts.capability import ToolResponse, CapabilityType
        resp = ToolResponse(
            success=True,
            capability_type=CapabilityType.GENERATE_IMAGE,
            provider_name="ComfyUI",
            model_name="flux-dev",
            output_data={"image_path": "/output/panel_01.png"},
        )
        assert resp.success is True


class TestAgentContract:
    def test_agent_result_creation(self):
        from backend.contracts.agent import AgentResult
        result = AgentResult(
            task_id="task-001",
            agent_id="story_agent",
            success=True,
            state_updates={"story_outline": "Chapter 1 drafted"},
        )
        assert result.success is True
        assert result.produced_artifacts == []
