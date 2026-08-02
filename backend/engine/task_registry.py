from datetime import datetime
from typing import Any, Dict, List, Optional, Set

from backend.contracts.event import Event, EventType
from backend.contracts.task import Task, TaskStatus


class TaskNotFoundError(Exception):
    """Raised when a task ID does not exist in the registry."""

    pass


class TaskAlreadyExistsError(Exception):
    """Raised when attempting to register a task with a duplicate ID."""

    pass


class InvalidTaskTransitionError(Exception):
    """Raised when an invalid task status transition is attempted."""

    pass


class TaskRegistry:
    """
    Owns task storage, retrieval, and state transitions.
    Enforces valid state machine transitions across TaskStatus values.

    Lifecycle:
        QUEUED -> SCHEDULED -> RUNNING -> COMPLETED / FAILED / BLOCKED
    """

    VALID_TRANSITIONS: Dict[TaskStatus, Set[TaskStatus]] = {
        TaskStatus.QUEUED: {
            TaskStatus.SCHEDULED,
            TaskStatus.RUNNING,
            TaskStatus.BLOCKED,
            TaskStatus.FAILED,
        },
        TaskStatus.SCHEDULED: {
            TaskStatus.RUNNING,
            TaskStatus.QUEUED,
            TaskStatus.BLOCKED,
            TaskStatus.FAILED,
        },
        TaskStatus.RUNNING: {
            TaskStatus.COMPLETED,
            TaskStatus.FAILED,
            TaskStatus.QUEUED,
            TaskStatus.BLOCKED,
        },
        TaskStatus.FAILED: {TaskStatus.QUEUED, TaskStatus.BLOCKED, TaskStatus.FAILED},
        TaskStatus.BLOCKED: {TaskStatus.QUEUED, TaskStatus.SCHEDULED, TaskStatus.FAILED},
        TaskStatus.COMPLETED: set(),  # Terminal state
    }

    def __init__(self, event_bus: Optional[Any] = None) -> None:
        self._store: Dict[str, Task] = {}
        self._event_bus = event_bus

    def register_task(self, task: Task) -> str:
        """
        Register a new task in the registry.
        Raises TaskAlreadyExistsError if the task_id is already taken.
        """
        if task.task_id in self._store:
            raise TaskAlreadyExistsError(f"Task '{task.task_id}' already exists in registry.")
        self._store[task.task_id] = task

        if self._event_bus:
            self._event_bus.publish(
                Event(
                    event_type=EventType.TASK_QUEUED,
                    project_id=task.payload.get("project_id", "default_project"),
                    payload={"task_id": task.task_id, "target_agent_type": task.target_agent_type},
                )
            )

        return task.task_id

    def get_task(self, task_id: str) -> Task:
        """Fetch a task by ID. Raises TaskNotFoundError if not found."""
        if task_id not in self._store:
            raise TaskNotFoundError(f"Task '{task_id}' not found in registry.")
        return self._store[task_id]

    def exists(self, task_id: str) -> bool:
        """Check whether a task ID exists in the registry."""
        return task_id in self._store

    def update_status(
        self, task_id: str, new_status: TaskStatus, error_message: Optional[str] = None
    ) -> Task:
        """Public API method for transitioning task status."""
        return self._transition_status(task_id, new_status, error_message=error_message)

    def _transition_status(
        self, task_id: str, new_status: TaskStatus, error_message: Optional[str] = None
    ) -> Task:
        """Internal helper enforcing state machine transition rules."""

        task = self.get_task(task_id)
        current_status = task.status

        if new_status != current_status and new_status not in self.VALID_TRANSITIONS.get(
            current_status, set()
        ):
            raise InvalidTaskTransitionError(
                f"Cannot transition task '{task_id}' from '{current_status.value}' to '{new_status.value}'."
            )

        task.status = new_status
        if error_message:
            task.error_message = error_message
        task.updated_at = datetime.utcnow()
        return task

    def queue(self, task_id: str) -> Task:
        """Transition task status to QUEUED."""
        return self._transition_status(task_id, TaskStatus.QUEUED)

    def schedule(self, task_id: str) -> Task:
        """Transition task status to SCHEDULED."""
        return self._transition_status(task_id, TaskStatus.SCHEDULED)

    def start(self, task_id: str) -> Task:
        """Transition task status to RUNNING."""
        return self._transition_status(task_id, TaskStatus.RUNNING)

    def complete(self, task_id: str) -> Task:
        """Transition task status to COMPLETED."""
        return self._transition_status(task_id, TaskStatus.COMPLETED)

    def fail(self, task_id: str, error_message: Optional[str] = None) -> Task:
        """Transition task status to FAILED."""
        return self._transition_status(task_id, TaskStatus.FAILED, error_message=error_message)

    def block(self, task_id: str, reason: Optional[str] = None) -> Task:
        """Transition task status to BLOCKED."""
        msg = f"Blocked: {reason}" if reason else None
        return self._transition_status(task_id, TaskStatus.BLOCKED, error_message=msg)

    def list_by_status(self, status: TaskStatus) -> List[Task]:
        """List all tasks matching a TaskStatus."""
        return [t for t in self._store.values() if t.status == status]

    def list_by_agent(self, agent_type: str) -> List[Task]:
        """List all tasks targeted to a specific agent type."""
        return [t for t in self._store.values() if t.target_agent_type == agent_type]

    def list_all(self) -> List[Task]:
        """Return all registered tasks."""
        return list(self._store.values())

    @property
    def count(self) -> int:
        """Total number of registered tasks."""
        return len(self._store)
