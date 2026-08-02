"""
Test: TaskScheduler & Task Orchestration Engine (Milestone 7)
Verifies Stages 1-4: Task Contracts, ExecutionPlan, TaskRegistry state machine,
Readiness Evaluators, Topological & Priority Dispatching, Retry & BLOCKED Cascades,
Deterministic Plan Generation, and Reactive Event Integration.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest

from backend.contracts.artifact import Artifact, ArtifactType
from backend.contracts.event import Event, EventType
from backend.contracts.task import ExecutionPlan, Task, TaskPriority, TaskStatus
from backend.engine.artifact_registry import ArtifactRegistry
from backend.engine.dependency_graph import DependencyGraph
from backend.engine.event_bus import EventBus
from backend.engine.scheduler import (
    BaseReadinessEvaluator,
    DAGReadinessEvaluator,
    TaskScheduler,
)
from backend.engine.task_registry import (
    InvalidTaskTransitionError,
    TaskAlreadyExistsError,
    TaskRegistry,
)


@pytest.fixture
def bus() -> EventBus:
    return EventBus()


@pytest.fixture
def registry() -> ArtifactRegistry:
    return ArtifactRegistry()


@pytest.fixture
def dep_graph() -> DependencyGraph:
    return DependencyGraph()


@pytest.fixture
def task_registry(bus) -> TaskRegistry:
    return TaskRegistry(event_bus=bus)


@pytest.fixture
def scheduler(task_registry, dep_graph, registry, bus) -> TaskScheduler:
    return TaskScheduler(
        task_registry=task_registry,
        dependency_graph=dep_graph,
        artifact_registry=registry,
        event_bus=bus,
    )


# =====================================================================
# Unit Tests — TaskRegistry State Machine & Storage
# =====================================================================


class TestTaskRegistry:
    def test_register_and_get_task(self, task_registry):
        task = Task(goal_id="g1", target_agent_type="STORY")
        task_id = task_registry.register_task(task)

        assert task_registry.exists(task_id) is True
        assert task_registry.count == 1
        retrieved = task_registry.get_task(task_id)
        assert retrieved.task_id == task_id
        assert retrieved.status == TaskStatus.QUEUED

    def test_duplicate_registration_raises(self, task_registry):
        task = Task(task_id="t-dup-01", goal_id="g1", target_agent_type="STORY")
        task_registry.register_task(task)

        with pytest.raises(TaskAlreadyExistsError):
            task_registry.register_task(task)

    def test_valid_status_transitions(self, task_registry):
        task = Task(goal_id="g1", target_agent_type="STORY")
        t_id = task_registry.register_task(task)

        assert task_registry.get_task(t_id).status == TaskStatus.QUEUED
        task_registry.schedule(t_id)
        assert task_registry.get_task(t_id).status == TaskStatus.SCHEDULED

        task_registry.start(t_id)
        assert task_registry.get_task(t_id).status == TaskStatus.RUNNING

        task_registry.complete(t_id)
        assert task_registry.get_task(t_id).status == TaskStatus.COMPLETED

    def test_invalid_status_transition_raises(self, task_registry):
        task = Task(goal_id="g1", target_agent_type="STORY")
        t_id = task_registry.register_task(task)
        task_registry.schedule(t_id)
        task_registry.start(t_id)
        task_registry.complete(t_id)

        # COMPLETED is terminal — transitioning to RUNNING must raise InvalidTaskTransitionError
        with pytest.raises(InvalidTaskTransitionError):
            task_registry.start(t_id)


# =====================================================================
# Unit Tests — Readiness Evaluator Strategy
# =====================================================================


class TestReadinessEvaluator:
    def test_dag_readiness_evaluator(self, task_registry, dep_graph, registry):
        evaluator = DAGReadinessEvaluator()
        engines = {
            "task_registry": task_registry,
            "dependency_graph": dep_graph,
            "artifact_registry": registry,
        }

        Artifact(
            artifact_id="art-01",
            project_id="p1",
            artifact_type=ArtifactType.STORY_OUTLINE,
            owner_agent="story_agent",
        )

        dep_graph.create_node("art-01", "STORY_OUTLINE")
        dep_graph.create_node("art-02", "SCENE_SCRIPT")
        dep_graph.connect("art-01", "art-02")

        task_downstream = Task(
            goal_id="g1", target_agent_type="STORY", required_dependencies=["art-02"]
        )
        assert evaluator.is_ready(task_downstream, engines) is True

        # Invalidate upstream art-01 -> marks downstream art-02 STALE
        dep_graph.invalidate("art-01", reason="modified")
        assert evaluator.is_ready(task_downstream, engines) is False

    def test_custom_readiness_evaluator_plugin(self, task_registry, dep_graph):
        class ManualApprovalEvaluator(BaseReadinessEvaluator):
            def is_ready(self, task, engines):
                return task.payload.get("approved", False) is True

        custom_evaluator = ManualApprovalEvaluator()
        task = Task(goal_id="g1", target_agent_type="STORY", payload={"approved": False})

        engines = {"task_registry": task_registry}
        assert custom_evaluator.is_ready(task, engines) is False

        task.payload["approved"] = True
        assert custom_evaluator.is_ready(task, engines) is True


# =====================================================================
# Unit & Integration Tests — TaskScheduler Dispatching & Execution Plans
# =====================================================================


class TestTaskSchedulerCore:
    def test_schedule_and_get_ready_tasks(self, scheduler, task_registry):
        t1 = Task(goal_id="g1", target_agent_type="STORY", priority=TaskPriority.LOW)
        t2 = Task(goal_id="g1", target_agent_type="IMAGE", priority=TaskPriority.CRITICAL)

        scheduler.schedule_task(t1)
        scheduler.schedule_task(t2)

        ready = scheduler.get_ready_tasks()
        assert len(ready) == 2
        # Critical priority task returned first
        assert ready[0].target_agent_type == "IMAGE"
        assert ready[1].target_agent_type == "STORY"

    def test_dispatch_next_and_event(self, scheduler, task_registry, bus):
        t1 = Task(goal_id="g1", target_agent_type="CHARACTER")
        scheduler.schedule_task(t1)

        dispatched = scheduler.dispatch_next()
        assert dispatched is not None
        assert dispatched.task_id == t1.task_id
        assert task_registry.get_task(t1.task_id).status == TaskStatus.RUNNING

        # Verify TASK_DISPATCHED event
        history = bus.get_history_by_type(EventType.TASK_DISPATCHED)
        assert len(history) == 1
        assert history[0].event.payload["task_id"] == t1.task_id

    def test_dispatch_batch(self, scheduler, task_registry):
        for i in range(5):
            t = Task(goal_id="g1", target_agent_type=f"AGENT_{i}")
            scheduler.schedule_task(t)

        batch = scheduler.dispatch_batch(max_batch_size=3)
        assert len(batch) == 3
        assert task_registry.list_by_status(TaskStatus.RUNNING).__len__() == 3

    def test_deterministic_execution_plan(self, scheduler, dep_graph):
        """Verify execution plan generation is 100% deterministic (Plan A == Plan B)."""
        dep_graph.create_node("Story", "STORY_OUTLINE")
        dep_graph.create_node("Scene", "SCENE_SCRIPT")
        dep_graph.create_node("Prompt", "PANEL_PROMPT")

        dep_graph.connect("Story", "Scene")
        dep_graph.connect("Scene", "Prompt")

        dep_graph.invalidate("Story", reason="edit")

        plan_a = scheduler.build_execution_plan()
        plan_b = scheduler.build_execution_plan()

        assert isinstance(plan_a, ExecutionPlan)
        assert len(plan_a.ordered_tasks) == 2  # Scene and Prompt dirty downstream nodes
        assert [t.payload["artifact_id"] for t in plan_a.ordered_tasks] == [
            t.payload["artifact_id"] for t in plan_b.ordered_tasks
        ]

    def test_retry_policy_requeues_task(self, scheduler, task_registry):
        t = Task(goal_id="g1", target_agent_type="STORY", max_retries=2)
        scheduler.schedule_task(t)
        scheduler.dispatch_next()

        # Fail attempt 1
        scheduler.mark_failed(t.task_id, error_message="Network glitch")

        updated = task_registry.get_task(t.task_id)
        assert updated.retry_count == 1
        assert updated.status == TaskStatus.QUEUED
        assert "Retry 1/2" in updated.error_message

    def test_max_retries_exceeded_fails_and_blocks_downstream(self, scheduler, task_registry, bus):
        t1 = Task(task_id="t-parent", goal_id="g1", target_agent_type="STORY", max_retries=1)
        t2 = Task(
            task_id="t-child",
            goal_id="g1",
            target_agent_type="IMAGE",
            required_dependencies=["t-parent"],
        )

        scheduler.schedule_task(t1)
        scheduler.schedule_task(t2)

        scheduler.dispatch_next()

        # Retry 1
        scheduler.mark_failed("t-parent", error_message="Fatal error 1")
        scheduler.dispatch_next()

        # Retry 2 (exceeds max_retries=1)
        scheduler.mark_failed("t-parent", error_message="Fatal error 2")

        assert task_registry.get_task("t-parent").status == TaskStatus.FAILED
        assert task_registry.get_task("t-child").status == TaskStatus.BLOCKED

        # Verify TASK_FAILED event
        history = bus.get_history_by_type(EventType.TASK_FAILED)
        assert len(history) == 1
        assert history[0].event.payload["task_id"] == "t-parent"

    def test_reactive_event_driven_auto_scheduling(self, scheduler, dep_graph, bus):
        scheduler.register_listeners(bus)

        dep_graph.create_node("Story", "STORY_OUTLINE")
        dep_graph.create_node("Prompt", "PANEL_PROMPT")
        dep_graph.connect("Story", "Prompt")

        # Emit ARTIFACT_INVALIDATED on EventBus
        bus.publish(
            Event(
                event_type=EventType.ARTIFACT_INVALIDATED,
                project_id="p1",
                target_artifact_id="Prompt",
            )
        )

        # Scheduler reactively enqueued auto-regeneration task!
        ready = scheduler.get_ready_tasks()
        assert len(ready) == 1
        assert ready[0].payload["artifact_id"] == "Prompt"
        assert ready[0].action_type == "REGENERATE"
