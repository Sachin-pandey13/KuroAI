from datetime import datetime

import pytest

from backend.agents.agent_registry import AgentRegistry
from backend.agents.character_agent import CharacterAgent
from backend.agents.dialogue_agent import DialogueAgent
from backend.agents.director_agent import DirectorAgent
from backend.agents.export_agent import ExportAgent
from backend.agents.image_agent import ImageAgent
from backend.agents.image_review_agent import ImageReviewAgent
from backend.agents.layout_agent import LayoutAgent
from backend.agents.runtime import AgentRuntime
from backend.agents.scene_planner_agent import ScenePlannerAgent
from backend.agents.story_agent import StoryAgent
from backend.capabilities.providers.mock_image_provider import MockImageProvider
from backend.capabilities.providers.mock_text_provider import MockTextProvider
from backend.capabilities.registry import CapabilityRegistry
from backend.contracts.artifact import Artifact, ArtifactState, ArtifactType
from backend.contracts.capability import CapabilityType
from backend.contracts.human_review import (
    HumanReviewAction,
    HumanReviewCheckpoint,
    HumanReviewGate,
)
from backend.contracts.task import Task, TaskStatus
from backend.engine.artifact_registry import ArtifactRegistry
from backend.engine.dependency_graph import DependencyGraph
from backend.engine.event_bus import EventBus
from backend.engine.scheduler import HumanApprovalEvaluator, TaskScheduler
from backend.engine.task_registry import TaskRegistry
from backend.engine.version_graph import VersionGraph


@pytest.fixture
def e2e_setup():
    task_reg = TaskRegistry()
    dep_graph = DependencyGraph()
    art_reg = ArtifactRegistry()
    ver_graph = VersionGraph()
    bus = EventBus()

    cap_reg = CapabilityRegistry()
    cap_reg.register_provider(CapabilityType.GENERATE_TEXT, MockTextProvider())
    cap_reg.register_provider(CapabilityType.GENERATE_IMAGE, MockImageProvider())

    scheduler = TaskScheduler(
        task_registry=task_reg,
        dependency_graph=dep_graph,
        artifact_registry=art_reg,
        event_bus=bus,
        readiness_evaluator=HumanApprovalEvaluator(),
    )

    agent_reg = AgentRegistry()
    agent_reg.register_agent(DirectorAgent())
    agent_reg.register_agent(StoryAgent())
    agent_reg.register_agent(ScenePlannerAgent())
    agent_reg.register_agent(CharacterAgent())
    agent_reg.register_agent(DialogueAgent())
    agent_reg.register_agent(LayoutAgent())
    agent_reg.register_agent(ImageAgent())
    agent_reg.register_agent(ImageReviewAgent())
    agent_reg.register_agent(ExportAgent())

    runtime = AgentRuntime(
        agent_registry=agent_reg,
        capability_registry=cap_reg,
        artifact_registry=art_reg,
        version_graph=ver_graph,
        task_scheduler=scheduler,
        event_bus=bus,
    )

    return {
        "task_reg": task_reg,
        "dep_graph": dep_graph,
        "art_reg": art_reg,
        "ver_graph": ver_graph,
        "scheduler": scheduler,
        "runtime": runtime,
    }


# =====================================================================
# E2E Tests
# =====================================================================


@pytest.mark.asyncio
async def test_full_phase2_pipeline_happy_path(e2e_setup):
    runtime = e2e_setup["runtime"]

    # Execute agents in topological sequence
    agents_to_run = [
        ("t_director", "DIRECTOR"),
        ("t_story", "STORY"),
        ("t_scene", "SCENE_PLANNER"),
        ("t_char", "CHARACTER"),
        ("t_dialogue", "DIALOGUE"),
        ("t_layout", "LAYOUT"),
        ("t_image", "IMAGE"),
        ("t_review", "IMAGE_REVIEW"),
        ("t_export", "EXPORT"),
    ]

    for task_id, agent_type in agents_to_run:
        task = Task(
            task_id=task_id,
            goal_id="g_cyberpunk",
            target_agent_type=agent_type,
            payload={"prompt": "Create cyberpunk manga page"},
        )
        e2e_setup["task_reg"].register_task(task)
        res = await runtime.run_task(task)
        assert res.success is True
        assert len(res.produced_artifacts) == 1

    # Verify final export artifact created in registry
    arts = e2e_setup["art_reg"].list_by_project("default_project")
    export_arts = [a for a in arts if a.artifact_type == ArtifactType.EXPORT_PDF]
    assert len(export_arts) == 1
    assert export_arts[0].data["export_format"] == "PDF_MANIFEST"


@pytest.mark.asyncio
async def test_human_review_gate_approval(e2e_setup):
    art_reg = e2e_setup["art_reg"]
    scheduler = e2e_setup["scheduler"]
    task_reg = e2e_setup["task_reg"]

    # Register an artifact under review
    target_art = Artifact(
        project_id="p1",
        artifact_type=ArtifactType.STORY_OUTLINE,
        owner_agent="story_agent",
        state=ArtifactState.ACTIVE,
    )
    art_reg.register(target_art)

    # Register a HumanReviewGate artifact with NO decision yet (action=None)
    gate = HumanReviewGate(
        project_id="p1",
        task_id="t_downstream",
        artifact_id=target_art.artifact_id,
        checkpoint=HumanReviewCheckpoint.STORY_CHECKPOINT,
        action=None,
    )
    gate_art = Artifact(
        artifact_id=gate.gate_id,
        project_id="p1",
        artifact_type=ArtifactType.HUMAN_REVIEW_GATE,
        owner_agent="human",
        data=gate.model_dump(),
    )
    art_reg.register(gate_art)

    task = Task(
        task_id="t_downstream",
        goal_id="g1",
        target_agent_type="SCENE_PLANNER",
        payload={"human_review_gate_id": gate.gate_id},
    )
    task_reg.register_task(task)

    # Evaluator check -> task should transition to WAITING_FOR_HUMAN_APPROVAL
    evaluator = HumanApprovalEvaluator()
    is_ready = evaluator.is_ready(task, scheduler._engines)
    assert is_ready is False
    assert task.status == TaskStatus.WAITING_FOR_HUMAN_APPROVAL

    # Record APPROVE decision
    gate.action = HumanReviewAction.APPROVE
    gate.reviewed_at = datetime.utcnow()
    gate_art.data = gate.model_dump()

    # Evaluator check -> task is now ready!
    is_ready_now = evaluator.is_ready(task, scheduler._engines)
    assert is_ready_now is True


@pytest.mark.asyncio
async def test_human_review_gate_minor_revision(e2e_setup):
    art_reg = e2e_setup["art_reg"]
    scheduler = e2e_setup["scheduler"]

    target_art = Artifact(
        project_id="p1",
        artifact_type=ArtifactType.CHARACTER_PROFILE,
        owner_agent="character_agent",
        state=ArtifactState.ACTIVE,
    )
    art_reg.register(target_art)

    gate = HumanReviewGate(
        project_id="p1",
        task_id="t_char_rev",
        artifact_id=target_art.artifact_id,
        checkpoint=HumanReviewCheckpoint.CHARACTER_CHECKPOINT,
        action=HumanReviewAction.MINOR_REVISION,
        feedback_notes="Give the hero blue eyes instead of brown",
    )
    gate_art = Artifact(
        artifact_id=gate.gate_id,
        project_id="p1",
        artifact_type=ArtifactType.HUMAN_REVIEW_GATE,
        owner_agent="human",
        data=gate.model_dump(),
    )
    art_reg.register(gate_art)

    task = Task(
        task_id="t_char_rev",
        goal_id="g1",
        target_agent_type="CHARACTER",
        payload={"human_review_gate_id": gate.gate_id},
    )

    evaluator = HumanApprovalEvaluator()
    is_ready = evaluator.is_ready(task, scheduler._engines)

    assert is_ready is False
    # Existing artifact state set to STALE (history preserved, V2 will be produced)
    assert target_art.state == ArtifactState.STALE
    assert task.status == TaskStatus.QUEUED
    assert task.payload["human_feedback"] == "Give the hero blue eyes instead of brown"


@pytest.mark.asyncio
async def test_human_review_gate_rejection(e2e_setup):
    art_reg = e2e_setup["art_reg"]
    scheduler = e2e_setup["scheduler"]

    gate = HumanReviewGate(
        project_id="p1",
        task_id="t_reject",
        artifact_id="art_bad",
        checkpoint=HumanReviewCheckpoint.STORY_CHECKPOINT,
        action=HumanReviewAction.REJECT,
        feedback_notes="Concept rejected entirely",
    )
    gate_art = Artifact(
        artifact_id=gate.gate_id,
        project_id="p1",
        artifact_type=ArtifactType.HUMAN_REVIEW_GATE,
        owner_agent="human",
        data=gate.model_dump(),
    )
    art_reg.register(gate_art)

    task = Task(
        task_id="t_reject",
        goal_id="g1",
        target_agent_type="STORY",
        payload={"human_review_gate_id": gate.gate_id},
    )

    evaluator = HumanApprovalEvaluator()
    is_ready = evaluator.is_ready(task, scheduler._engines)

    assert is_ready is False
    assert task.status == TaskStatus.FAILED
    assert "Human Review Rejected" in task.error_message


@pytest.mark.asyncio
async def test_major_revision_replans_pipeline(e2e_setup):
    art_reg = e2e_setup["art_reg"]
    dep_graph = e2e_setup["dep_graph"]
    ver_graph = e2e_setup["ver_graph"]
    scheduler = e2e_setup["scheduler"]
    runtime = e2e_setup["runtime"]

    # 1. Produce V1 artifact
    art_v1 = Artifact(
        project_id="p1",
        artifact_type=ArtifactType.STORY_OUTLINE,
        owner_agent="story_agent",
        state=ArtifactState.ACTIVE,
        data={"title": "V1 Outline"},
    )
    art_reg.register(art_v1)
    ver_graph.record_version(art_v1.artifact_id, art_v1.data, art_v1.metadata)
    dep_graph.create_node(art_v1.artifact_id, art_v1.artifact_type.value, ArtifactState.ACTIVE)

    # 2. Gate records MAJOR_REVISION
    gate = HumanReviewGate(
        project_id="p1",
        task_id="t_story_major",
        artifact_id=art_v1.artifact_id,
        checkpoint=HumanReviewCheckpoint.STORY_CHECKPOINT,
        action=HumanReviewAction.MAJOR_REVISION,
        feedback_notes="Change setting from sci-fi to fantasy kingdom",
    )
    gate_art = Artifact(
        artifact_id=gate.gate_id,
        project_id="p1",
        artifact_type=ArtifactType.HUMAN_REVIEW_GATE,
        owner_agent="human",
        data=gate.model_dump(),
    )
    art_reg.register(gate_art)

    task = Task(
        task_id="t_story_major",
        goal_id="g1",
        target_agent_type="STORY",
        payload={"human_review_gate_id": gate.gate_id},
    )
    e2e_setup["task_reg"].register_task(task)

    evaluator = HumanApprovalEvaluator()
    is_ready = evaluator.is_ready(task, scheduler._engines)

    # Verify V1 marked STALE in registry and graph, audit trail preserved
    assert is_ready is False
    assert art_v1.state == ArtifactState.STALE
    assert dep_graph.get_node(art_v1.artifact_id).state == ArtifactState.STALE

    # 3. Re-run task to produce V2 artifact
    res = await runtime.run_task(task)
    assert res.success is True
    assert len(res.produced_artifacts) == 1
    art_v2 = res.produced_artifacts[0]

    # Verify V2 created as new artifact version with history intact
    assert art_v2.artifact_id != art_v1.artifact_id
    assert art_v2.state == ArtifactState.ACTIVE
