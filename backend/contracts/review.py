from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field

class ReviewSeverity(str, Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"

class ReviewCategory(str, Enum):
    ANATOMY = "ANATOMY"
    CONTINUITY = "CONTINUITY"
    PROMPT_ADHERENCE = "PROMPT_ADHERENCE"
    TEXT_LEGIBILITY = "TEXT_LEGIBILITY"
    STYLE_CONSISTENCY = "STYLE_CONSISTENCY"
    CHARACTER_APPEARANCE = "CHARACTER_APPEARANCE"
    TIMELINE_LOGIC = "TIMELINE_LOGIC"
    RELATIONSHIP_DYNAMIC = "RELATIONSHIP_DYNAMIC"

class ReviewIssue(BaseModel):
    issue_id: str = Field(description="Unique identifier for the review issue")
    severity: ReviewSeverity = Field(description="Severity level: INFO, WARNING, or ERROR")
    category: ReviewCategory = Field(description="Classification of issue")
    description: str = Field(description="Human-readable detail of what went wrong or needs attention")
    panel_number: Optional[int] = Field(default=None, description="Associated panel number if applicable")

class ReviewFeedback(BaseModel):
    target_artifact_id: str = Field(description="ID of the artifact inspected")
    reviewer_agent: str = Field(description="Agent ID that performed the inspection")
    passed: bool = Field(description="True if quality threshold is met, False if action required")
    review_score: float = Field(ge=0.0, le=100.0, description="Overall quality score from 0 to 100")
    confidence: Optional[float] = Field(default=1.0, ge=0.0, le=1.0, description="Model confidence in evaluation")
    issues: List[ReviewIssue] = Field(default_factory=list, description="List of identified issues")

class ContinuityReport(BaseModel):
    project_id: str = Field(description="Project ID being evaluated")
    passed: bool = Field(description="True if no blocking continuity errors found")
    review_score: float = Field(ge=0.0, le=100.0, description="Continuity score from 0 to 100")
    issues: List[ReviewIssue] = Field(default_factory=list, description="Continuity discrepancies found across scenes")
    characters_checked: List[str] = Field(default_factory=list, description="Character IDs checked for consistency")
    scenes_checked: int = Field(default=0, description="Total scenes validated")
