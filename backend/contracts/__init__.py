"""
KuroAI 2.0 Centralized Contracts Package
Defines all immutable domain models, event contracts, state deltas, decision traces, and interfaces.
"""
from backend.contracts.execution_plan import (
    TaskSpec,
    ExecutionPlan,
    ExecutionPlanValidationError,
    validate_execution_plan,
)

