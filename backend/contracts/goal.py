from enum import Enum
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime
import uuid


class GoalStatus(str, Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class GoalPriority(int, Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


class CreativeGoal(BaseModel):
    """
    Represents a high-level creative direction set by the Human Director or Project Manager Agent.
    """
    goal_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    description: str
    target_milestone: str = "M1"
    priority: GoalPriority = GoalPriority.MEDIUM
    status: GoalStatus = GoalStatus.PENDING
    constraints: Dict[str, Any] = Field(default_factory=dict)
    parent_goal_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
