from enum import Enum
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class NodeState(str, Enum):
    CLEAN = "CLEAN"
    DIRTY = "DIRTY"
    PROCESSING = "PROCESSING"
    FAILED = "FAILED"


class DependencyEdge(BaseModel):
    source_artifact_id: str
    target_artifact_id: str
    dependency_type: str = "EXPLICIT"  # EXPLICIT, IMPLICIT, STYLE


class DependencyNode(BaseModel):
    """
    Node representation in the Dependency Graph Subsystem.
    """
    artifact_id: str
    artifact_type: str
    state: NodeState = NodeState.CLEAN
    upstream_ids: List[str] = Field(default_factory=list)
    downstream_ids: List[str] = Field(default_factory=list)
    last_invalidated_at: Optional[datetime] = None
    invalidation_reason: Optional[str] = None
