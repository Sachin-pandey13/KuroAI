import uuid
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class EventType(str, Enum):
    GOAL_PUBLISHED = "GOAL_PUBLISHED"
    GOAL_UPDATED = "GOAL_UPDATED"
    TASK_QUEUED = "TASK_QUEUED"
    TASK_SCHEDULED = "TASK_SCHEDULED"
    TASK_DISPATCHED = "TASK_DISPATCHED"
    TASK_COMPLETED = "TASK_COMPLETED"
    TASK_FAILED = "TASK_FAILED"
    AGENT_STARTED = "AGENT_STARTED"
    AGENT_COMPLETED = "AGENT_COMPLETED"
    AGENT_FAILED = "AGENT_FAILED"
    ARTIFACT_CREATED = "ARTIFACT_CREATED"
    ARTIFACT_REGISTERED = "ARTIFACT_REGISTERED"
    ARTIFACT_UPDATED = "ARTIFACT_UPDATED"
    ARTIFACT_INVALIDATED = "ARTIFACT_INVALIDATED"
    ARTIFACT_ROLLED_BACK = "ARTIFACT_ROLLED_BACK"
    STATE_DELTA_MUTATED = "STATE_DELTA_MUTATED"


class Event(BaseModel):
    """
    Abstract Event payload emitted across the Event Bus and Project State Engine.
    """

    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    event_type: EventType
    project_id: str = "default_project"
    source_agent_id: Optional[str] = None
    target_artifact_id: Optional[str] = None
    payload: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class EventLog(BaseModel):
    """
    Audit and tracking record for event delivery on the EventBus.
    """

    log_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    event: Event
    delivered_to: int
    errors: list[str] = Field(default_factory=list)
    logged_at: datetime = Field(default_factory=datetime.utcnow)
