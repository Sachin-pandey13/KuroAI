"""
KuroAI Centralized Contracts Package.
Defines all immutable domain models, event contracts, state deltas, decision traces, and interfaces.
"""

from backend.contracts.agent import AgentResult, BatchResult
from backend.contracts.artifact import Artifact, ArtifactState, ArtifactType
from backend.contracts.capability import CapabilityType, ToolRequest, ToolResponse
from backend.contracts.character import CharacterProfile
from backend.contracts.context import AgentContext, ContextSection, ContextSectionType
from backend.contracts.decision_trace import DecisionTrace, ExecutionProvenance
from backend.contracts.dependency import DependencyEdge, DependencyNode, EdgeType
from backend.contracts.dialogue import DialogueType, SceneDialogue, SpeechBubble
from backend.contracts.event import Event, EventLog, EventType
from backend.contracts.execution_plan import ExecutionPlan, TaskSpec, validate_execution_plan
from backend.contracts.export import ExportManifest, PageExportBundle, PanelExportSlot
from backend.contracts.goal import CreativeGoal
from backend.contracts.human_review import HumanReviewAction, HumanReviewCheckpoint, HumanReviewGate
from backend.contracts.layout import (
    MangaPageLayout,
    PanelImportance,
    RelativePosition,
    SemanticPanelSlot,
)
from backend.contracts.project_state import AutonomyLevel, ProjectStateModel
from backend.contracts.review import ContinuityReport, ReviewCategory, ReviewIssue, ReviewSeverity
from backend.contracts.scene import PanelDescription, SceneScript
from backend.contracts.story import StoryBeat, StoryOutline
from backend.contracts.task import Task, TaskPriority, TaskStatus
from backend.contracts.version import DiffResult, VersionEntry

__all__ = [
    "AgentResult",
    "BatchResult",
    "Artifact",
    "ArtifactType",
    "ArtifactState",
    "CapabilityType",
    "ToolRequest",
    "ToolResponse",
    "CharacterProfile",
    "AgentContext",
    "ContextSection",
    "ContextSectionType",
    "DecisionTrace",
    "ExecutionProvenance",
    "DependencyNode",
    "DependencyEdge",
    "EdgeType",
    "SpeechBubble",
    "SceneDialogue",
    "DialogueType",
    "Event",
    "EventType",
    "EventLog",
    "TaskSpec",
    "ExecutionPlan",
    "validate_execution_plan",
    "ExportManifest",
    "PageExportBundle",
    "PanelExportSlot",
    "CreativeGoal",
    "HumanReviewAction",
    "HumanReviewCheckpoint",
    "HumanReviewGate",
    "MangaPageLayout",
    "SemanticPanelSlot",
    "PanelImportance",
    "RelativePosition",
    "ProjectStateModel",
    "AutonomyLevel",
    "ContinuityReport",
    "ReviewIssue",
    "ReviewSeverity",
    "ReviewCategory",
    "SceneScript",
    "PanelDescription",
    "StoryOutline",
    "StoryBeat",
    "Task",
    "TaskStatus",
    "TaskPriority",
    "VersionEntry",
    "DiffResult",
]
