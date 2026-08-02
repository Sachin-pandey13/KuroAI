from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field

from backend.contracts.artifact import ArtifactState


class EdgeType(str, Enum):
    EXPLICIT = "EXPLICIT"  # Direct parent -> child generation link
    IMPLICIT = "IMPLICIT"  # Context dependency
    STYLE = "STYLE"  # Style guide / character blueprint constraint


class DependencyEdge(BaseModel):
    """
    Represents a directed edge in the Dependency Graph: source -> target.
    Source must be computed before Target.
    If Source changes, Target becomes STALE/INVALID.
    Supports optional weighting, confidence, and provenance metadata.
    """

    source_artifact_id: str
    target_artifact_id: str
    edge_type: EdgeType = EdgeType.EXPLICIT
    weight: float = 1.0
    confidence: float = 1.0
    created_by: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class InvalidationRecord(BaseModel):
    """
    Rich record explaining exact invalidation provenance (First Law).
    Answers: Why is this artifact stale? Who caused it? At what depth?
    """

    source_artifact_id: str
    affected_artifact_id: str
    reason: str
    propagation_depth: int = 0
    caused_by_event: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


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
    last_invalidation_record: Optional[InvalidationRecord] = None
