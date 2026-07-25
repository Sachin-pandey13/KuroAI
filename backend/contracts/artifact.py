from enum import Enum
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime
import uuid
from backend.contracts.decision_trace import DecisionTrace


class ArtifactType(str, Enum):
    STORY_OUTLINE = "STORY_OUTLINE"
    SCENE_SCRIPT = "SCENE_SCRIPT"
    CHARACTER_PROFILE = "CHARACTER_PROFILE"
    WORLD_LORE = "WORLD_LORE"
    PANEL_PROMPT = "PANEL_PROMPT"
    GENERATED_IMAGE = "GENERATED_IMAGE"
    MANGA_PAGE_LAYOUT = "MANGA_PAGE_LAYOUT"
    SPEECH_BUBBLE = "SPEECH_BUBBLE"
    EXPORT_PDF = "EXPORT_PDF"


class ArtifactStatus(str, Enum):
    DRAFT = "DRAFT"
    ACTIVE = "ACTIVE"
    STALE = "STALE"
    ARCHIVED = "ARCHIVED"


class Artifact(BaseModel):
    """
    First-class project artifact representing a node in the Dependency Graph and Version Graph.
    The ArtifactRegistry owns artifact lifecycle.
    The ProjectStateEngine references artifacts by ID.
    """
    artifact_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    project_id: str
    artifact_type: ArtifactType
    owner_agent: str
    status: ArtifactStatus = ArtifactStatus.DRAFT
    current_version: int = 1
    data: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    upstream_dependencies: List[str] = Field(default_factory=list)
    downstream_dependents: List[str] = Field(default_factory=list)
    decision_trace: Optional[DecisionTrace] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
