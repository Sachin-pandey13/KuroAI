import pytest

from backend.agents.agent_registry import AgentRegistry
from backend.agents.base_agent import BaseAgent
from backend.agents.character_agent import CharacterAgent
from backend.agents.creative_safety_agent import CreativeSafetyAgent
from backend.agents.director_agent import DirectorAgent
from backend.agents.runtime import AgentRuntime
from backend.agents.story_agent import StoryAgent
from backend.capabilities.providers.mock_image_provider import MockImageProvider
from backend.capabilities.providers.mock_text_provider import MockTextProvider
from backend.capabilities.registry import CapabilityRegistry
from backend.contracts.agent import AgentResult
from backend.contracts.artifact import Artifact, ArtifactType
from backend.contracts.capability import CapabilityType
from backend.contracts.context import AgentContext, ContextSection, ContextSectionType
from backend.contracts.execution_plan import (
    ExecutionPlan,
    ExecutionPlanValidationError,
    TaskSpec,
    validate_execution_plan,
)
from backend.contracts.task import Task
from backend.engine.artifact_registry import ArtifactRegistry
from backend.engine.dependency_graph import DependencyGraph
from backend.engine.event_bus import EventBus
from backend.engine.scheduler import TaskScheduler
from backend.engine.task_registry import TaskRegistry
from backend.engine.version_graph import VersionGraph

# ----------------------------------------------------------------------
# 1. Contract & Immutability & Validation Tests
# ----------------------------------------------------------------------


def test_task_spec_and_execution_plan_contracts():
    spec1 = TaskSpec(
        spec_id="spec_1",
        target_agent_type="STORY",
        payload={"prompt": "Write cyberpunk chapter"},
        priority=10,
    )
    spec2 = TaskSpec(
        spec_id="spec_2",
        target_agent_type="CHARACTER",
        payload={"prompt": "Design protagonist"},
        dependencies=["spec_1"],
        priority=8,
    )

    plan = ExecutionPlan(
        goal_id="goal_100",
        user_prompt="12-page cyberpunk manga",
        task_specs=[spec1, spec2],
    )

    assert plan.goal_id == "goal_100"
    assert len(plan.task_specs) == 2
    assert plan.task_specs[1].dependencies == ["spec_1"]

    # Test Immutability
    with pytest.raises(Exception):
        plan.goal_id = "goal_mutated"


def test_validate_execution_plan_success():
    spec1 = TaskSpec(spec_id="t1", target_agent_type="STORY", dependencies=[])
    spec2 = TaskSpec(spec_id="t2", target_agent_type="CHARACTER", dependencies=["t1"])
    spec3 = TaskSpec(spec_id="t3", target_agent_type="IMAGE", dependencies=["t2"])

    plan = ExecutionPlan(goal_id="g1", user_prompt="Test", task_specs=[spec1, spec2, spec3])
    # Should pass cleanly
    validate_execution_plan(plan, known_agent_types=["STORY", "CHARACTER", "IMAGE", "DIRECTOR"])


def test_validate_execution_plan_empty():
    plan = ExecutionPlan(goal_id="g1", user_prompt="Empty", task_specs=[])
    with pytest.raises(ExecutionPlanValidationError, match="contains no task specifications"):
        validate_execution_plan(plan)


def test_validate_execution_plan_duplicate_ids():
    spec1 = TaskSpec(spec_id="dup_id", target_agent_type="STORY")
    spec2 = TaskSpec(spec_id="dup_id", target_agent_type="CHARACTER")
    plan = ExecutionPlan(goal_id="g1", user_prompt="Dup", task_specs=[spec1, spec2])
    with pytest.raises(ExecutionPlanValidationError, match="Duplicate task spec_id"):
        validate_execution_plan(plan)


def test_validate_execution_plan_unknown_agent_type():
    spec1 = TaskSpec(spec_id="t1", target_agent_type="UNKNOWN_AGENT")
    plan = ExecutionPlan(goal_id="g1", user_prompt="Unknown", task_specs=[spec1])
    with pytest.raises(ExecutionPlanValidationError, match="Unknown target_agent_type"):
        validate_execution_plan(plan, known_agent_types=["STORY", "CHARACTER"])


def test_validate_execution_plan_missing_dependency_reference():
    spec1 = TaskSpec(spec_id="t1", target_agent_type="STORY", dependencies=["non_existent_id"])
    plan = ExecutionPlan(goal_id="g1", user_prompt="Missing Dep", task_specs=[spec1])
    with pytest.raises(ExecutionPlanValidationError, match="references unknown dependency"):
        validate_execution_plan(plan)


def test_validate_execution_plan_self_dependency():
    spec1 = TaskSpec(spec_id="t1", target_agent_type="STORY", dependencies=["t1"])
    plan = ExecutionPlan(goal_id="g1", user_prompt="Self Dep", task_specs=[spec1])
    with pytest.raises(ExecutionPlanValidationError, match="cannot depend on itself"):
        validate_execution_plan(plan)


def test_validate_execution_plan_cycle_detection():
    # t1 -> t2 -> t3 -> t1
    spec1 = TaskSpec(spec_id="t1", target_agent_type="STORY", dependencies=["t3"])
    spec2 = TaskSpec(spec_id="t2", target_agent_type="CHARACTER", dependencies=["t1"])
    spec3 = TaskSpec(spec_id="t3", target_agent_type="IMAGE", dependencies=["t2"])

    plan = ExecutionPlan(goal_id="g1", user_prompt="Cycle", task_specs=[spec1, spec2, spec3])
    with pytest.raises(ExecutionPlanValidationError, match="Cyclic dependency detected"):
        validate_execution_plan(plan)


# ----------------------------------------------------------------------
# 2. DirectorAgent Unit & Execution Tests
# ----------------------------------------------------------------------


@pytest.mark.asyncio
async def test_director_agent_execution():
    agent = DirectorAgent()
    assert agent.agent_id == "director_agent"
    assert agent.agent_type == "DIRECTOR"

    context = AgentContext(
        task_id="task_dir_1",
        project_id="proj_cyberpunk",
        target_agent_type="DIRECTOR",
        goal={"goal_id": "goal_manga_001"},
        sections=[
            ContextSection(
                section_type=ContextSectionType.GOAL,
                title="User Request",
                content={"prompt": "Create a 12-page cyberpunk manga"},
                estimated_token_cost=10,
            )
        ],
    )

    result = await agent.execute(context)

    assert result.success is True
    assert len(result.produced_artifacts) == 1
    artifact = result.produced_artifacts[0]
    assert artifact.artifact_type == ArtifactType.EXECUTION_PLAN
    assert artifact.owner_agent == "director_agent"

    # Verify produced ExecutionPlan data
    plan = ExecutionPlan.model_validate(artifact.data)
    assert plan.goal_id == "goal_manga_001"
    assert plan.user_prompt == "Create a 12-page cyberpunk manga"
    assert len(plan.task_specs) >= 4

    # Verify decision trace
    assert result.decision_trace is not None
    assert result.decision_trace.agent_id == "director_agent"


# ----------------------------------------------------------------------
# 3. TaskScheduler Integration Tests (load_execution_plan)
# ----------------------------------------------------------------------


def test_task_scheduler_load_execution_plan():
    task_reg = TaskRegistry()
    dep_graph = DependencyGraph()
    scheduler = TaskScheduler(task_registry=task_reg, dependency_graph=dep_graph)

    agent_reg = AgentRegistry()
    agent_reg.register_agent(StoryAgent())
    agent_reg.register_agent(CharacterAgent())
    agent_reg.register_agent(CreativeSafetyAgent())

    spec1 = TaskSpec(spec_id="spec_story_1", target_agent_type="STORY", priority=10)
    spec2 = TaskSpec(
        spec_id="spec_char_1",
        target_agent_type="CHARACTER",
        dependencies=["spec_story_1"],
        priority=8,
    )

    plan = ExecutionPlan(
        goal_id="goal_cyber", user_prompt="Cyberpunk story", task_specs=[spec1, spec2]
    )
    artifact = Artifact(
        project_id="proj_1",
        artifact_type=ArtifactType.EXECUTION_PLAN,
        owner_agent="director_agent",
        data=plan.model_dump(),
    )

    created_tasks = scheduler.load_execution_plan(artifact, agent_registry=agent_reg)

    assert len(created_tasks) == 2
    assert task_reg.exists("spec_story_1")
    assert task_reg.exists("spec_char_1")

    # Dependency graph should have nodes and edges
    assert dep_graph.has_node("spec_story_1")
    assert dep_graph.has_node("spec_char_1")
    assert dep_graph.has_edge("spec_story_1", "spec_char_1")

    # Topological readiness test:
    # spec_story_1 has no deps -> READY (SCHEDULED)
    # spec_char_1 depends on spec_story_1 -> BLOCKED (QUEUED)
    ready = scheduler.get_ready_tasks()
    assert len(ready) == 1
    assert ready[0].task_id == "spec_story_1"


# ----------------------------------------------------------------------
# 4. End-to-End Goal -> DirectorAgent -> ExecutionPlan -> Runtime Pipeline
# ----------------------------------------------------------------------


class DummyAgent(BaseAgent):
    def __init__(self, a_id: str, a_type: str):
        self._a_id = a_id
        self._a_type = a_type

    @property
    def agent_id(self) -> str:
        return self._a_id

    @property
    def agent_type(self) -> str:
        return self._a_type

    async def execute(self, context, tool_executor=None):
        return AgentResult(
            task_id=context.task_id,
            agent_id=self.agent_id,
            agent_type=self.agent_type,
            success=True,
        )


@pytest.mark.asyncio
async def test_end_to_end_director_pipeline():
    # Setup full infrastructure
    agent_reg = AgentRegistry()
    director = DirectorAgent()
    story_agent = DummyAgent("story_agent", "STORY")
    char_agent = DummyAgent("char_agent", "CHARACTER")
    safety_agent = DummyAgent("safety_agent", "CREATIVE_SAFETY")
    image_agent = DummyAgent("image_agent", "IMAGE")
    layout_agent = DummyAgent("layout_agent", "LAYOUT")

    agent_reg.register_agent(director)
    agent_reg.register_agent(story_agent)
    agent_reg.register_agent(char_agent)
    agent_reg.register_agent(safety_agent)
    agent_reg.register_agent(image_agent)
    agent_reg.register_agent(layout_agent)

    cap_reg = CapabilityRegistry()
    cap_reg.register_provider(CapabilityType.GENERATE_TEXT, MockTextProvider())
    cap_reg.register_provider(CapabilityType.GENERATE_IMAGE, MockImageProvider())

    task_reg = TaskRegistry()
    dep_graph = DependencyGraph()
    art_reg = ArtifactRegistry()
    ver_graph = VersionGraph()
    event_bus = EventBus()

    scheduler = TaskScheduler(
        task_registry=task_reg,
        dependency_graph=dep_graph,
        artifact_registry=art_reg,
        event_bus=event_bus,
    )

    runtime = AgentRuntime(
        agent_registry=agent_reg,
        capability_registry=cap_reg,
        artifact_registry=art_reg,
        version_graph=ver_graph,
        task_scheduler=scheduler,
        event_bus=event_bus,
    )

    # 1. User Goal dispatched to DirectorAgent task
    director_task = Task(
        task_id="task_director_initial",
        goal_id="goal_full_pipeline",
        target_agent_type="DIRECTOR",
        payload={"prompt": "Build a multi-page cyberpunk saga", "project_id": "proj_e2e"},
    )
    scheduler.schedule_task(director_task)

    dir_result = await runtime.run_task(director_task)
    assert dir_result.success is True
    assert len(dir_result.produced_artifacts) == 1

    plan_artifact = dir_result.produced_artifacts[0]
    assert plan_artifact.artifact_type == ArtifactType.EXECUTION_PLAN

    # 2. Ingest ExecutionPlan into TaskScheduler
    planned_tasks = scheduler.load_execution_plan(plan_artifact, agent_registry=agent_reg)
    assert len(planned_tasks) >= 3

    # 3. Execute planned tasks through AgentRuntime in topological order
    executed_count = 0
    while True:
        ready_task = scheduler.dispatch_next()
        if not ready_task:
            break
        result = await runtime.run_task(ready_task)
        assert result.success is True
        executed_count += 1

    assert executed_count >= 3
