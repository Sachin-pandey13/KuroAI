from enum import Enum
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field

class HumanReviewAction(str, Enum):
    APPROVE = "APPROVE"                  # Unblock downstream tasks
    MINOR_REVISION = "MINOR_REVISION"    # Re-run task with feedback; produce V2 artifact
    MAJOR_REVISION = "MAJOR_REVISION"    # Mark target STALE; trigger upstream re-plan & produce V2
    REJECT = "REJECT"                    # Mark task FAILED; block downstream tasks

class HumanReviewCheckpoint(str, Enum):
    STORY_CHECKPOINT = "STORY_CHECKPOINT"
    CHARACTER_CHECKPOINT = "CHARACTER_CHECKPOINT"
    LAYOUT_CHECKPOINT = "LAYOUT_CHECKPOINT"
    FINAL_PAGE_CHECKPOINT = "FINAL_PAGE_CHECKPOINT"

class HumanReviewGate(BaseModel):
    gate_id: str = Field(default_factory=lambda: str(__import__("uuid").uuid4()))
    project_id: str = Field(description="Associated project ID")
    task_id: str = Field(description="Target Task ID awaiting human review")
    artifact_id: str = Field(description="ID of the target artifact inspected")
    checkpoint: HumanReviewCheckpoint = Field(description="Workflow checkpoint position")
    action: Optional[HumanReviewAction] = Field(default=None, description="Human decision (None if pending)")
    feedback_notes: Optional[str] = Field(default=None, description="Human feedback / instructions for revision")
    reviewed_at: Optional[datetime] = Field(default=None, description="Timestamp when review action was recorded")
