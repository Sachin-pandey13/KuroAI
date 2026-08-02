"""
Benchmark for TaskScheduler dispatch and task handling throughput.
"""

import time
import tracemalloc

from backend.contracts import Task, TaskPriority
from backend.engine import DependencyGraph, TaskRegistry, TaskScheduler


def benchmark_scheduler(num_tasks: int = 1000):
    tracemalloc.start()
    start_time = time.monotonic()

    tr = TaskRegistry()
    dg = DependencyGraph()
    scheduler = TaskScheduler(tr, dg)

    for i in range(num_tasks):
        priority = TaskPriority.HIGH if i % 10 == 0 else TaskPriority.MEDIUM
        task = Task(
            task_id=f"task_{i}",
            goal_id="g1",
            target_agent_type="STORY",
            description=f"Description {i}",
            priority=priority,
        )
        scheduler.schedule(task)

    plan = scheduler.get_plan()
    duration_ms = (time.monotonic() - start_time) * 1000

    current_mem, peak_mem = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    return {
        "benchmark": "TaskScheduler",
        "tasks_scheduled": num_tasks,
        "dispatch_ms": round(duration_ms, 2),
        "scheduled_plan_len": len(plan.tasks) if hasattr(plan, "tasks") else 0,
        "peak_memory_mb": round(peak_mem / (1024 * 1024), 2),
    }
