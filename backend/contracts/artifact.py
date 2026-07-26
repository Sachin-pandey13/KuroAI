from enum import Enum
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime
import uuid
from backend.contracts.decision_trace import DecisionTrace


class ArtifactType(str, Enum):
    EXECUTION_PLAN = "EXECUTION_PLAN"
    DIRECTOR_BRIEF = "DIRECTOR_BRIEF"
    STORY_OUTLINE = "STORY_OUTLINE"
    SCENE_SCRIPT = "SCENE_SCRIPT"
    CHARACTER_PROFILE = "CHARACTER_PROFILE"
    WORLD_LORE = "WORLD_LORE"
    PANEL_PROMPT = "PANEL_PROMPT"
    GENERATED_IMAGE = "GENERATED_IMAGE"
    MANGA_PAGE_LAYOUT = "MANGA_PAGE_LAYOUT"
    SPEECH_BUBBLE = "SPEECH_BUBBLE"
    EXPORT_PDF = "EXPORT_PDF"


class ArtifactState(str, Enum):
    DRAFT = "DRAFT"
    PENDING = "PENDING"
    GENERATING = "GENERATING"
    ACTIVE = "ACTIVE"
    STALE = "STALE"
    INVALID = "INVALID"
    FAILED = "FAILED"
    ARCHIVED = "ARCHIVED"


class Artifact(BaseModel):
    """
    First-class project artifact representing a node payload.
    The ArtifactRegistry owns artifact lifecycle and data.

    Provenance vs Graph Edges Separation:
      - parent_artifact_id ("Who created me?") -> Intrinsic provenance (stored in Artifact)
      - child_artifact_ids -> Intrinsic provenance (stored in Artifact)
      - Dynamic edges (upstream/downstream dependencies) -> Owned strictly by DependencyGraph
    """
    artifact_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    project_id: str
    artifact_type: ArtifactType
    owner_agent: str
    state: ArtifactState = ArtifactState.DRAFT
    current_version: int = 1
    data: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    parent_artifact_id: Optional[str] = None
    child_artifact_ids: List[str] = Field(default_factory=list)
    decision_trace: Optional[DecisionTrace] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
