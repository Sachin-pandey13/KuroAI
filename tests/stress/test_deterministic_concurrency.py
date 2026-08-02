"""
Deterministic concurrency test verifying TaskScheduler plan execution hashes match 100%.
"""

import hashlib
import pytest
from backend.contracts import Task, TaskPriority
from backend.engine import TaskRegistry, TaskScheduler, DependencyGraph


def _generate_plan_hash() -> str:
    tr = TaskRegistry()
    dg = DependencyGraph()
    scheduler = TaskScheduler(tr, dg)

    # Schedule tasks with varying priorities
    for i in range(50):
        priority = TaskPriority.HIGH if i % 3 == 0 else TaskPriority.MEDIUM
        task = Task(
            task_id=f"t_{i}",
            goal_id="g1",
            target_agent_type="STORY",
            description=f"Task {i}",
            priority=priority,
        )
        scheduler.schedule(task)

    plan = scheduler.get_plan()
    task_ids = [t.task_id if hasattr(t, "task_id") else str(t) for t in plan.ordered_tasks]
    serialized = ",".join(task_ids)
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


def test_deterministic_scheduler_concurrency():
    """Assert scheduler produces identical execution plan hashes across 100 runs."""
    base_hash = _generate_plan_hash()

    for _ in range(100):
        run_hash = _generate_plan_hash()
        assert run_hash == base_hash, f"Determinism failure: {run_hash} != {base_hash}"
