from enum import Enum
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime
import uuid


class EventType(str, Enum):
    GOAL_PUBLISHED = "GOAL_PUBLISHED"
    GOAL_UPDATED = "GOAL_UPDATED"
    TASK_SCHEDULED = "TASK_SCHEDULED"
    TASK_COMPLETED = "TASK_COMPLETED"
    TASK_FAILED = "TASK_FAILED"
    ARTIFACT_CREATED = "ARTIFACT_CREATED"
    ARTIFACT_UPDATED = "ARTIFACT_UPDATED"
    ARTIFACT_INVALIDATED = "ARTIFACT_INVALIDATED"
    STATE_DELTA_MUTATED = "STATE_DELTA_MUTATED"


class Event(BaseModel):
    """
    Abstract Event payload emitted across the Event Bus and Project State Engine.
    """
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    event_type: EventType
    project_id: str
    source_agent_id: Optional[str] = None
    target_artifact_id: Optional[str] = None
    payload: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
