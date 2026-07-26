from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Set
from datetime import datetime

from backend.contracts.task import Task, TaskStatus, TaskPriority, ExecutionPlan
from backend.contracts.execution_plan import (
    ExecutionPlan as ExecutionPlanModel,
    validate_execution_plan,
    ExecutionPlanValidationError,
)
from backend.contracts.dependency import DependencyNode
from backend.contracts.artifact import Artifact, ArtifactState
from backend.contracts.event import Event, EventType
from backend.engine.task_registry import TaskRegistry
from backend.engine.dependency_graph import DependencyGraph
from backend.engine.artifact_registry import ArtifactRegistry
from backend.engine.state_engine import ProjectStateEngine


class BaseReadinessEvaluator(ABC):
    """
    Abstract Base Class for pluggable task readiness strategies.
    Future evaluators (HumanApprovalEvaluator, TimeWindowEvaluator) extend this class.
    """

    @abstractmethod
    def is_ready(self, task: Task, engines: Dict[str, Any]) -> bool:
        """Return True if task dependencies and readiness conditions are satisfied."""
        pass


class DAGReadinessEvaluator(BaseReadinessEvaluator):
    """
    Default readiness strategy: A task is READY if all required_dependencies
    (artifact IDs or upstream task IDs) are in an ACTIVE/COMPLETED state.
    """

    def is_ready(self, task: Task, engines: Dict[str, Any]) -> bool:
        artifact_registry: Optional[ArtifactRegistry] = engines.get("artifact_registry")
        dependency_graph: Optional[DependencyGraph] = engines.get("dependency_graph")
        task_registry: Optional[TaskRegistry] = engines.get("task_registry")

        for dep_id in task.required_dependencies:
            # 1. Check if dependency is a Task in TaskRegistry
            if task_registry and task_registry.exists(dep_id):
                dep_task = task_registry.get_task(dep_id)
                if dep_task.status != TaskStatus.COMPLETED:
                    return False

            # 2. Check if dependency is an Artifact in DependencyGraph / Registry
            if dependency_graph and dependency_graph.has_node(dep_id):
                node = dependency_graph.get_node(dep_id)
                if node.state != ArtifactState.ACTIVE:
                    return False
            elif artifact_registry and artifact_registry.exists(dep_id):
                artifact = artifact_registry.get(dep_id)
                if artifact.state != ArtifactState.ACTIVE:
                    return False

        return True


class TaskScheduler:
    """
    TaskScheduler & Task Orchestration Engine.

    Responsibilities:
    - Queries TaskRegistry for task storage & status.
    - Evaluates task readiness via BaseReadinessEvaluator.
    - Dispatches ready tasks in deterministic topological + priority order.
    - Builds rich ExecutionPlan objects.
    - Enforces retry logic & downstream BLOCKED cascades on failure.
    - Reacts to EventBus events (ARTIFACT_INVALIDATED, TASK_COMPLETED, TASK_FAILED).
    """

    def __init__(
        self,
        task_registry: TaskRegistry,
        dependency_graph: DependencyGraph,
        artifact_registry: Optional[ArtifactRegistry] = None,
        project_state_engine: Optional[ProjectStateEngine] = None,
        event_bus: Optional[Any] = None,
        readiness_evaluator: Optional[BaseReadinessEvaluator] = None,
    ) -> None:
        self._task_registry = task_registry
        self._dep_graph = dependency_graph
        self._artifact_registry = artifact_registry
        self._state_engine = project_state_engine
        self._event_bus = event_bus
        self._evaluator = readiness_evaluator or DAGReadinessEvaluator()
        self._engines: Dict[str, Any] = {
            "task_registry": self._task_registry,
            "dependency_graph": self._dep_graph,
            "artifact_registry": self._artifact_registry,
            "state_engine": self._state_engine,
        }

    def schedule_task(self, task: Task) -> str:
        """
        Enqueue a task in the TaskRegistry.
        Returns the task_id.
        """
        if not self._task_registry.exists(task.task_id):
            self._task_registry.register_task(task)
        else:
            self._task_registry.queue(task.task_id)

        # Auto-evaluate readiness for task
        if self._evaluator.is_ready(task, self._engines):
            self._task_registry.schedule(task.task_id)

        return task.task_id

    def load_execution_plan(
        self,
        plan_artifact: Artifact,
        agent_registry: Optional[Any] = None,
        validate: bool = True,
    ) -> List[Task]:
        """
        Ingest a first-class ExecutionPlan artifact produced by DirectorAgent.

        1. Extract ExecutionPlan data model.
        2. Validate graph integrity (unique IDs, no cycles, valid dependencies, known agent types).
        3. Convert planning TaskSpecs into runtime Task instances.
        4. Register runtime Tasks into TaskRegistry and enqueue into TaskScheduler.
        5. Build DAG dependency nodes in DependencyGraph.

        Returns:
            List[Task]: Runtime tasks created and scheduled.
        """
        if isinstance(plan_artifact.data, dict):
            plan = ExecutionPlanModel.model_validate(plan_artifact.data)
        elif isinstance(plan_artifact.data, ExecutionPlanModel):
            plan = plan_artifact.data
        else:
            raise ValueError("Artifact data is not a valid ExecutionPlan object or dict.")

        known_types = None
        if agent_registry is not None and hasattr(agent_registry, "list_agents"):
            known_types = agent_registry.list_agents()

        if validate:
            validate_execution_plan(plan, known_agent_types=known_types)

        created_tasks: List[Task] = []
        for spec in plan.task_specs:
            if spec.priority >= 10:
                priority_val = TaskPriority.CRITICAL
            elif spec.priority >= 7:
                priority_val = TaskPriority.HIGH
            elif spec.priority >= 4:
                priority_val = TaskPriority.MEDIUM
            else:
                priority_val = TaskPriority.LOW

            task = Task(
                task_id=spec.spec_id,
                goal_id=plan.goal_id,
                target_agent_type=spec.target_agent_type,
                action_type=spec.payload.get("action", "EXECUTE"),
                priority=priority_val,
                status=TaskStatus.QUEUED,
                payload=spec.payload,
                required_dependencies=spec.dependencies,
                execution_timeout=spec.execution_timeout,
            )

            # Register in TaskRegistry & schedule
            self.schedule_task(task)

            # Add to DependencyGraph
            if self._dep_graph is not None:
                if not self._dep_graph.has_node(task.task_id):
                    self._dep_graph.create_node(
                        artifact_id=task.task_id,
                        artifact_type=task.target_agent_type,
                        state=ArtifactState.ACTIVE,
                    )
                for dep_id in spec.dependencies:
                    if self._dep_graph.has_node(dep_id):
                        self._dep_graph.connect(dep_id, task.task_id)

            created_tasks.append(task)

        return created_tasks

    def get_ready_tasks(self) -> List[Task]:
        """
        Return all tasks currently READY to execute (status SCHEDULED or QUEUED with satisfied dependencies).
        Tasks are sorted deterministically by topological DAG position first, then priority (CRITICAL -> LOW).
        """
        queued_and_scheduled = (
            self._task_registry.list_by_status(TaskStatus.QUEUED)
            + self._task_registry.list_by_status(TaskStatus.SCHEDULED)
        )

        ready_tasks: List[Task] = []
        for task in queued_and_scheduled:
            if self._evaluator.is_ready(task, self._engines):
                if task.status == TaskStatus.QUEUED:
                    self._task_registry.schedule(task.task_id)
                ready_tasks.append(task)

        # Deterministic sorting: Priority value (descending), then task_id
        ready_tasks.sort(key=lambda t: (-int(t.priority.value), t.task_id))
        return ready_tasks

    def dispatch_next(self) -> Optional[Task]:
        """
        Dispatch the single highest-priority ready task to RUNNING.
        Emits TASK_DISPATCHED event.
        """
        ready_tasks = self.get_ready_tasks()
        if not ready_tasks:
            return None

        target_task = ready_tasks[0]
        self._task_registry.start(target_task.task_id)

        if self._event_bus:
            project_id = target_task.payload.get("project_id", "default_project")
            self._event_bus.publish(
                Event(
                    event_type=EventType.TASK_DISPATCHED,
                    project_id=project_id,
                    payload={
                        "task_id": target_task.task_id,
                        "target_agent_type": target_task.target_agent_type,
                        "action_type": target_task.action_type,
                    },
                )
            )

        return target_task

    def dispatch_batch(self, max_batch_size: int = 5) -> List[Task]:
        """
        Dispatch up to max_batch_size independent ready tasks for parallel execution.
        """
        ready_tasks = self.get_ready_tasks()
        dispatched: List[Task] = []

        for task in ready_tasks[:max_batch_size]:
            self._task_registry.start(task.task_id)
            dispatched.append(task)

            if self._event_bus:
                project_id = task.payload.get("project_id", "default_project")
                self._event_bus.publish(
                    Event(
                        event_type=EventType.TASK_DISPATCHED,
                        project_id=project_id,
                        payload={
                            "task_id": task.task_id,
                            "target_agent_type": task.target_agent_type,
                            "action_type": task.action_type,
                        },
                    )
                )

        return dispatched

    def mark_completed(self, task_id: str) -> None:
        """
        Mark a task as COMPLETED in TaskRegistry.
        Re-evaluates queue readiness for downstream blocked tasks.
        """
        task = self._task_registry.complete(task_id)

        # Unblock downstream tasks if their dependencies are now met
        for blocked_task in self._task_registry.list_by_status(TaskStatus.BLOCKED):
            if task_id in blocked_task.required_dependencies:
                if self._evaluator.is_ready(blocked_task, self._engines):
                    self._task_registry.queue(blocked_task.task_id)

    def mark_failed(self, task_id: str, error_message: str) -> None:
        """
        Handle task failure with retry policy:
        - If retry_count < max_retries: re-queue task (QUEUED), increment retry_count.
        - If retry_count >= max_retries: mark FAILED, publish TASK_FAILED, and set downstream tasks to BLOCKED.
        """
        task = self._task_registry.get_task(task_id)

        if task.retry_count < task.max_retries:
            task.retry_count += 1
            self._task_registry.queue(task_id)
            task.error_message = f"Retry {task.retry_count}/{task.max_retries}: {error_message}"
        else:
            self._task_registry.fail(task_id, error_message=error_message)

            if self._event_bus:
                project_id = task.payload.get("project_id", "default_project")
                self._event_bus.publish(
                    Event(
                        event_type=EventType.TASK_FAILED,
                        project_id=project_id,
                        payload={"task_id": task_id, "error": error_message},
                    )
                )

            # Cascade BLOCKED status to all downstream dependent tasks
            self._cascade_blocked(task_id, reason=f"Upstream task '{task_id}' failed.")

    def _cascade_blocked(self, failed_task_id: str, reason: str) -> None:
        """Mark all tasks depending on failed_task_id as BLOCKED."""
        for t in self._task_registry.list_all():
            if failed_task_id in t.required_dependencies and t.status in (TaskStatus.QUEUED, TaskStatus.SCHEDULED):
                self._task_registry.block(t.task_id, reason=reason)

    def build_execution_plan(self) -> ExecutionPlan:
        """
        Generates a structured ExecutionPlan for current dirty/STALE nodes in the DependencyGraph.
        Includes ordered_tasks, parallel_groups, blocked_tasks, and dirty_artifact_ids.
        """
        dirty_nodes = self._dep_graph.get_dirty()
        dirty_ids = [n.artifact_id for n in dirty_nodes]

        try:
            topo_order = self._dep_graph.topological_sort()
            ordered_dirty_ids = [node_id for node_id in topo_order if node_id in dirty_ids]
        except Exception:
            ordered_dirty_ids = dirty_ids

        ordered_tasks: List[Task] = []
        parallel_groups: List[List[Task]] = []
        blocked_tasks = self._task_registry.list_by_status(TaskStatus.BLOCKED)

        for art_id in ordered_dirty_ids:
            node = self._dep_graph.get_node(art_id)
            t = Task(
                goal_id="auto_regen",
                target_agent_type=node.artifact_type,
                action_type="REGENERATE",
                priority=TaskPriority.HIGH,
                required_dependencies=node.upstream_ids,
                payload={"artifact_id": art_id},
            )
            ordered_tasks.append(t)

        # Compute parallel groups (tasks at the same topological level)
        if ordered_tasks:
            current_group: List[Task] = []
            for t in ordered_tasks:
                if not current_group:
                    current_group.append(t)
                elif any(dep in t.required_dependencies for dep in [gt.payload.get("artifact_id") for gt in current_group]):
                    parallel_groups.append(current_group)
                    current_group = [t]
                else:
                    current_group.append(t)
            if current_group:
                parallel_groups.append(current_group)

        return ExecutionPlan(
            ordered_tasks=ordered_tasks,
            parallel_groups=parallel_groups,
            blocked_tasks=blocked_tasks,
            dirty_artifact_ids=dirty_ids,
        )

    def register_listeners(self, bus: Any) -> None:
        """Register TaskScheduler event listeners on the EventBus."""
        bus.subscribe(EventType.ARTIFACT_INVALIDATED, self._on_artifact_invalidated)

    def unregister_listeners(self, bus: Any) -> None:
        """Unregister TaskScheduler event listeners from the EventBus."""
        bus.unsubscribe(EventType.ARTIFACT_INVALIDATED, self._on_artifact_invalidated)

    def _on_artifact_invalidated(self, event: Event) -> None:
        """React to ARTIFACT_INVALIDATED by auto-enqueuing regeneration task for target artifact."""
        art_id = event.target_artifact_id
        if art_id and self._dep_graph.has_node(art_id):
            node = self._dep_graph.get_node(art_id)
            task = Task(
                goal_id="auto_invalidation_regen",
                target_agent_type=node.artifact_type,
                action_type="REGENERATE",
                priority=TaskPriority.HIGH,
                required_dependencies=node.upstream_ids,
                payload={"artifact_id": art_id, "project_id": event.project_id},
            )
            self.schedule_task(task)

