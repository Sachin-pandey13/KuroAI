import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class VersionEntry(BaseModel):
    """
    Immutable version snapshot for an artifact node (Third Law).
    Each artifact owns an independent, auditable version timeline.
    """

    version_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    artifact_id: str
    version_number: int
    parent_version: Optional[int] = None
    rollback_of: Optional[int] = None
    trigger_event: Optional[str] = None
    data_snapshot: Dict[str, Any] = Field(default_factory=dict)
    metadata_snapshot: Dict[str, Any] = Field(default_factory=dict)
    created_by: str = "system"
    change_summary: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class DiffResult(BaseModel):
    """
    Structural comparison result between two historical versions of an artifact.
    """

    artifact_id: str
    version_a: int
    version_b: int
    added: Dict[str, Any] = Field(default_factory=dict)
    removed: Dict[str, Any] = Field(default_factory=dict)
    modified: Dict[str, Dict[str, Any]] = Field(
        default_factory=dict
    )  # field -> {"old": val, "new": val}
    unchanged: List[str] = Field(default_factory=list)
