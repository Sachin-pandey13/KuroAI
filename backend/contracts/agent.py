from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from backend.contracts.artifact import Artifact
from backend.contracts.event import Event
from backend.contracts.decision_trace import DecisionTrace


class AgentResult(BaseModel):
    """
    Standardized return payload returned by every agent execution.
    """
    task_id: str
    agent_id: str
    success: bool
    state_updates: Dict[str, Any] = Field(default_factory=dict)
    produced_artifacts: List[Artifact] = Field(default_factory=list)
    emitted_events: List[Event] = Field(default_factory=list)
    decision_trace: Optional[DecisionTrace] = None
    error_message: Optional[str] = None
