from enum import Enum
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime
from backend.contracts.artifact import ArtifactState


class EdgeType(str, Enum):
    EXPLICIT = "EXPLICIT"    # Direct parent -> child generation link
    IMPLICIT = "IMPLICIT"    # Context dependency
    STYLE = "STYLE"          # Style guide / character blueprint constraint


class DependencyEdge(BaseModel):
    """
    Represents a directed edge in the Dependency Graph: source -> target.
    Source must be computed before Target.
    If Source changes, Target becomes STALE/INVALID.
    """
    source_artifact_id: str
    target_artifact_id: str
    edge_type: EdgeType = EdgeType.EXPLICIT
    created_at: datetime = Field(default_factory=datetime.utcnow)


class DependencyNode(BaseModel):
    """
    Node representation inside the Dependency Graph Subsystem.
    Owns upstream & downstream relationship links strictly within the graph.
    """
    artifact_id: str
    artifact_type: str
    state: ArtifactState = ArtifactState.ACTIVE
    upstream_ids: List[str] = Field(default_factory=list)
    downstream_ids: List[str] = Field(default_factory=list)
    last_invalidated_at: Optional[datetime] = None
    invalidation_reason: Optional[str] = None
