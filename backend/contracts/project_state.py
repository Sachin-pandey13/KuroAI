from enum import Enum
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime
import uuid
from backend.contracts.artifact import Artifact
from backend.contracts.goal import CreativeGoal


class AutonomyLevel(str, Enum):
    GUIDED = "GUIDED"
    SMART = "SMART"
    AUTONOMOUS_STUDIO = "AUTONOMOUS_STUDIO"


class ProjectStateModel(BaseModel):
    """
    Complete state representation of a KuroAI 2.0 Manga Project.
    Single Source of Truth (Fourth Law).
    """
    project_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    description: str
    autonomy_level: AutonomyLevel = AutonomyLevel.GUIDED
    active_goals: List[CreativeGoal] = Field(default_factory=list)
    artifacts: Dict[str, Artifact] = Field(default_factory=dict)
    character_registry: Dict[str, Any] = Field(default_factory=dict)
    style_guidelines: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    version: int = 1
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
