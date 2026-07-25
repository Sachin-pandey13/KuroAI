from enum import Enum
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime
import uuid


class TaskStatus(str, Enum):
    QUEUED = "QUEUED"
    SCHEDULED = "SCHEDULED"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    BLOCKED = "BLOCKED"


class Task(BaseModel):
    """
    Represents an actionable unit of work dispatched to a specialized agent.
    """
    task_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    goal_id: str
    target_agent_type: str
    action_type: str = "EXECUTE"
    status: TaskStatus = TaskStatus.QUEUED
    payload: Dict[str, Any] = Field(default_factory=dict)
    required_dependencies: List[str] = Field(default_factory=list)
    retry_count: int = 0
    max_retries: int = 3
    error_message: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
