"""
AgentRuntime — Pure coordinator for the KuroAI execution pipeline.

The runtime composes every previous subsystem without absorbing domain logic:

    Task (from TaskScheduler)
          │
          ▼
    ContextEngine.build_context()
          │
          ▼
    AgentRegistry.get_agent(task.target_agent_type)
          │
          ▼
    CapabilityToolExecutor (injected)
          │
          ▼
    Agent.execute(context, tool_executor)
          │
          ▼
    RuntimeTransaction.commit()
          │
          ├── ArtifactRegistry ← produced artifacts
          ├── VersionGraph     ← version records
          ├── StateEngine      ← state updates
          └── EventBus         ← AGENT_COMPLETED / TASK_COMPLETED
          │
          ▼
    TaskScheduler.mark_completed() / mark_failed()

The runtime owns:
    AGENT_STARTED, AGENT_COMPLETED, AGENT_FAILED,
    TASK_COMPLETED, TASK_FAILED  (Single Publisher Rule)

The runtime does NOT own:
    Context assembly  → ContextEngine
    Capability routing → CapabilityRegistry
    Task storage      → TaskRegistry
    Scheduling logic  → TaskScheduler
    State storage     → ProjectStateEngine
"""
import asyncio
import time
from typing import List, Optional

from backend.contracts.task import Task, TaskStatus
from backend.contracts.agent import AgentResult, BatchResult
from backend.contracts.event import Event, EventType
from backend.contracts.context import AgentContext, ContextSection, ContextSectionType

from backend.agents.agent_registry import AgentRegistry
from backend.agents.tool_executor import CapabilityToolExecutor, BaseToolExecutor
from backend.agents.runtime_transaction import RuntimeTransaction, TransactionError


class AgentRuntime:
    """
    End-to-end execution coordinator.

    Dependency-injected constructor keeps the runtime fully testable:
    swap any subsystem for a mock without changing runtime logic.
    """

    def __init__(
        self,
        agent_registry: AgentRegistry,
        capability_registry,          # CapabilityRegistry
        artifact_registry,            # ArtifactRegistry
        version_graph,                # VersionGraph
        task_scheduler,               # TaskScheduler
        event_bus,                    # EventBus
        context_engine=None,          # ContextEngine (optional)
        state_engine=None,            # ProjectStateEngine (optional)
    ) -> None:
        self._agent_registry = agent_registry
        self._capability_registry = capability_registry
        self._artifact_registry = artifact_registry
        self._version_graph = version_graph
        self._task_scheduler = task_scheduler
        self._event_bus = event_bus
        self._context_engine = context_engine
        self._state_engine = state_engine

    # ------------------------------------------------------------------
    # Core execution pipeline
    # ------------------------------------------------------------------

    async def run_task(self, task: Task) -> AgentResult:
        """
        Execute a single task end-to-end through the full coordination pipeline.

        Steps:
            1. Publish AGENT_STARTED
            2. Build or synthesize AgentContext
            3. Resolve agent by task.target_agent_type
            4. Inject ToolExecutor and call agent.execute()
            5. Commit RuntimeTransaction (artifacts + versions + state + events)
            6. Notify TaskScheduler (mark_completed / mark_failed)
            7. Publish AGENT_COMPLETED + TASK_COMPLETED

        On any failure:
            - RuntimeTransaction.rollback()
            - TaskScheduler.mark_failed()
            - Publish AGENT_FAILED + TASK_FAILED
        """
        start_ms = time.monotonic() * 1000

        # 1. Announce start and mark task RUNNING if in task registry
        self._publish(EventType.AGENT_STARTED, {
            "task_id": task.task_id,
            "agent_type": task.target_agent_type,
        })

        if hasattr(self._task_scheduler, "_task_registry") and self._task_scheduler._task_registry.exists(task.task_id):
            registered_task = self._task_scheduler._task_registry.get_task(task.task_id)
            if registered_task.status in (TaskStatus.QUEUED, TaskStatus.SCHEDULED):
                self._task_scheduler._task_registry.start(task.task_id)

        # 2. Resolve agent
        try:
            agent = self._agent_registry.get_agent(task.target_agent_type)
        except Exception as exc:
            return self._fail_task(task, str(exc), start_ms)

        # 3. Build context
        context = self._build_context(task)

        # 4. Build ToolExecutor (injected — agent never sees CapabilityRegistry)
        tool_executor: BaseToolExecutor = CapabilityToolExecutor(self._capability_registry)

        # 5. Execute agent with optional timeout
        try:
            if task.execution_timeout is not None:
                result = await asyncio.wait_for(
                    agent.execute(context, tool_executor),
                    timeout=task.execution_timeout,
                )
            else:
                result = await agent.execute(context, tool_executor)
        except asyncio.TimeoutError:
            return self._fail_task(
                task,
                f"Agent '{task.target_agent_type}' timed out after "
                f"{task.execution_timeout}s (task.execution_timeout).",
                start_ms,
            )
        except Exception as exc:
            return self._fail_task(task, f"Agent execution error: {exc}", start_ms)

        # 6. Commit RuntimeTransaction
        txn = RuntimeTransaction(
            artifact_registry=self._artifact_registry,
            version_graph=self._version_graph,
            state_engine=self._state_engine,
            event_bus=self._event_bus,
        )
        for artifact in result.produced_artifacts:
            txn.stage_artifact(artifact)
            txn.stage_version(
                artifact_id=artifact.artifact_id,
                data=artifact.data,
                metadata=artifact.metadata,
                created_by=artifact.owner_agent,
            )
        if result.state_updates:
            txn.stage_state_updates(result.state_updates)
        txn.stage_event(Event(
            event_type=EventType.AGENT_COMPLETED,
            source_agent_id=result.agent_id,
            payload={"task_id": task.task_id, "artifacts": len(result.produced_artifacts)},
        ))
        txn.stage_event(Event(
            event_type=EventType.TASK_COMPLETED,
            source_agent_id=result.agent_id,
            payload={"task_id": task.task_id},
        ))

        try:
            txn.commit()
        except TransactionError as exc:
            txn.rollback()
            return self._fail_task(task, f"Persistence commit failed: {exc}", start_ms)

        # 7. Notify scheduler
        self._task_scheduler.mark_completed(task.task_id)

        result.execution_time_ms = round(time.monotonic() * 1000 - start_ms, 3)
        return result

    async def run_batch(self, tasks: List[Task]) -> BatchResult:
        """
        Execute multiple tasks asynchronously and return a BatchResult
        with aggregated success/failure counts and total duration.
        """
        start_ms = time.monotonic() * 1000
        results = await asyncio.gather(
            *[self.run_task(task) for task in tasks],
            return_exceptions=True,
        )

        batch = BatchResult(total_tasks=len(tasks))
        for result in results:
            if isinstance(result, Exception):
                # Wrap unexpected exceptions as failed AgentResult
                batch.failed.append(AgentResult(
                    task_id="unknown",
                    agent_id="unknown",
                    agent_type="unknown",
                    success=False,
                    error_message=str(result),
                ))
            elif result.success:
                batch.successful.append(result)
            else:
                batch.failed.append(result)

        batch.duration_ms = round(time.monotonic() * 1000 - start_ms, 3)
        return batch

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _build_context(self, task: Task) -> AgentContext:
        """
        Build AgentContext for the agent.
        Delegates to ContextEngine if available, otherwise synthesizes a
        valid AgentContext from task metadata.
        """
        if self._context_engine is not None:
            return self._context_engine.build_context(task)

        project_id = task.payload.get("project_id", "default_project") if task.payload else "default_project"

        sections = []
        if task.payload:
            sections.append(ContextSection(
                section_type=ContextSectionType.GOAL,
                title="Goal Payload",
                content=task.payload,
                estimated_token_cost=len(str(task.payload)) // 4,
            ))

        return AgentContext(
            task_id=task.task_id,
            project_id=project_id,
            target_agent_type=task.target_agent_type,
            goal={"goal_id": task.goal_id, "payload": task.payload},
            sections=sections,
            total_token_cost=sum(s.estimated_token_cost for s in sections),
        )

    def _fail_task(self, task: Task, error: str, start_ms: float) -> AgentResult:
        """Publish failure events, notify scheduler, and return failed AgentResult."""
        self._publish(EventType.AGENT_FAILED, {
            "task_id": task.task_id,
            "agent_type": task.target_agent_type,
            "error": error,
        })
        self._publish(EventType.TASK_FAILED, {
            "task_id": task.task_id,
            "error": error,
        })
        self._task_scheduler.mark_failed(task.task_id, error)
        return AgentResult(
            task_id=task.task_id,
            agent_id=task.target_agent_type.lower() + "_agent",
            agent_type=task.target_agent_type,
            success=False,
            error_message=error,
            execution_time_ms=round(time.monotonic() * 1000 - start_ms, 3),
        )

    def _publish(self, event_type: EventType, payload: dict, project_id: str = "default_project") -> None:
        """Publish an event to the EventBus."""
        self._event_bus.publish(Event(
            event_type=event_type,
            project_id=project_id,
            source_agent_id="agent_runtime",
            payload=payload,
        ))
