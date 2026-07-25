from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from backend.contracts.artifact import Artifact
from backend.contracts.event import Event
from backend.contracts.decision_trace import DecisionTrace


class AgentResult(BaseModel):
    """
    Standardized return payload for every agent execution.
    Carries produced artifacts, state updates, decision trace, and telemetry.
    """
    task_id: str
    agent_id: str
    agent_type: str = "UNKNOWN"
    success: bool
    state_updates: Dict[str, Any] = Field(default_factory=dict)
    produced_artifacts: List[Artifact] = Field(default_factory=list)
    emitted_events: List[Event] = Field(default_factory=list)
    decision_trace: Optional[DecisionTrace] = None
    error_message: Optional[str] = None
    execution_time_ms: float = 0.0
    capability_requests: List[str] = Field(default_factory=list)


class BatchResult(BaseModel):
    """
    Aggregate result of a run_batch() call, carrying metrics alongside results.
    """
    successful: List[AgentResult] = Field(default_factory=list)
    failed: List[AgentResult] = Field(default_factory=list)
    total_tasks: int = 0
    duration_ms: float = 0.0

    @property
    def success_count(self) -> int:
        return len(self.successful)

    @property
    def failure_count(self) -> int:
        return len(self.failed)

    @property
    def success_rate(self) -> float:
        if self.total_tasks == 0:
            return 0.0
        return self.success_count / self.total_tasks
