import uuid
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


class TaskSpec(BaseModel):
    """
    Planning-level representation of a task to be executed.
    Decoupled from runtime Task concept — converted into Task by TaskScheduler.
    """

    spec_id: str = Field(default_factory=lambda: f"task_spec_{uuid.uuid4().hex[:8]}")
    target_agent_type: str
    payload: Dict[str, Any] = Field(default_factory=dict)
    dependencies: List[str] = Field(default_factory=list)
    priority: int = 1
    execution_timeout: Optional[float] = None

    model_config = ConfigDict(extra="forbid")


class ExecutionPlan(BaseModel):
    """
    First-class immutable planning artifact produced by DirectorAgent.
    Defines the full task breakdown and DAG dependency structure for a user goal.
    """

    plan_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    goal_id: str
    user_prompt: str
    task_specs: List[TaskSpec] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    version: int = 1

    model_config = ConfigDict(frozen=True)


class ExecutionPlanValidationError(Exception):
    """Raised when an ExecutionPlan fails structural or graph validation."""

    pass


def validate_execution_plan(
    plan: ExecutionPlan,
    known_agent_types: Optional[List[str]] = None,
) -> None:
    """
    Validate an ExecutionPlan before runtime ingestion:
    1. Plan must contain at least one TaskSpec.
    2. All spec_ids must be unique.
    3. All dependency references must exist within the plan.
    4. No cyclic dependencies allowed (DAG check).
    5. If known_agent_types is provided, target_agent_types must be registered.
    """
    if not plan.task_specs:
        raise ExecutionPlanValidationError("ExecutionPlan contains no task specifications.")

    spec_map: Dict[str, TaskSpec] = {}
    for spec in plan.task_specs:
        if spec.spec_id in spec_map:
            raise ExecutionPlanValidationError(
                f"Duplicate task spec_id found in plan: '{spec.spec_id}'."
            )
        spec_map[spec.spec_id] = spec

        if known_agent_types is not None and spec.target_agent_type not in known_agent_types:
            raise ExecutionPlanValidationError(
                f"Unknown target_agent_type '{spec.target_agent_type}' in task spec '{spec.spec_id}'. "
                f"Known types: {known_agent_types}"
            )

    # Validate dependency references
    for spec in plan.task_specs:
        for parent_id in spec.dependencies:
            if parent_id not in spec_map:
                raise ExecutionPlanValidationError(
                    f"Task spec '{spec.spec_id}' references unknown dependency '{parent_id}'."
                )
            if parent_id == spec.spec_id:
                raise ExecutionPlanValidationError(
                    f"Task spec '{spec.spec_id}' cannot depend on itself."
                )

    # Cycle Detection (DFS / Kahn's algorithm)
    in_degree: Dict[str, int] = {s.spec_id: 0 for s in plan.task_specs}
    graph: Dict[str, List[str]] = {s.spec_id: [] for s in plan.task_specs}

    for spec in plan.task_specs:
        for parent_id in spec.dependencies:
            graph[parent_id].append(spec.spec_id)
            in_degree[spec.spec_id] += 1

    zero_in_degree = [node for node, degree in in_degree.items() if degree == 0]
    visited_count = 0

    while zero_in_degree:
        curr = zero_in_degree.pop(0)
        visited_count += 1
        for neighbor in graph[curr]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                zero_in_degree.append(neighbor)

    if visited_count != len(plan.task_specs):
        raise ExecutionPlanValidationError(
            "Cyclic dependency detected in ExecutionPlan task graph."
        )
