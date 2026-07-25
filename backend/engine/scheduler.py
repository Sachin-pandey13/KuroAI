from typing import List, Optional
from backend.contracts.task import Task, TaskStatus
from backend.contracts.event import Event


class TaskScheduler:
    """
    Listens to state events, evaluates task readiness via the
    Dependency Graph, and dispatches executable tasks to agents.
    """

    def __init__(self):
        pass

    def on_event(self, event: Event) -> None:
        """Handle an incoming state event and evaluate task scheduling."""
        raise NotImplementedError("TaskScheduler.on_event stub")

    def schedule_task(self, task: Task) -> None:
        """Queue a task for dispatch."""
        raise NotImplementedError("TaskScheduler.schedule_task stub")

    def get_ready_tasks(self) -> List[Task]:
        """Return all tasks whose dependencies are satisfied."""
        raise NotImplementedError("TaskScheduler.get_ready_tasks stub")

    def dispatch_next(self) -> Optional[Task]:
        """Dispatch the highest-priority ready task to its assigned agent."""
        raise NotImplementedError("TaskScheduler.dispatch_next stub")

    def mark_completed(self, task_id: str) -> None:
        """Mark a task as completed."""
        raise NotImplementedError("TaskScheduler.mark_completed stub")

    def mark_failed(self, task_id: str, error: str) -> None:
        """Mark a task as failed with an error message."""
        raise NotImplementedError("TaskScheduler.mark_failed stub")
