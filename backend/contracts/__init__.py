"""
KuroAI Centralized Contracts Package.
Defines all immutable domain models, event contracts, state deltas, decision traces, and interfaces.
"""

from backend.contracts.agent import AgentResult, BatchResult
from backend.contracts.artifact import Artifact, ArtifactType, ArtifactState
from backend.contracts.capability import CapabilityType, ToolRequest, ToolResponse
from backend.contracts.character import CharacterProfile
from backend.contracts.context import AgentContext, ContextSection, ContextSectionType
from backend.contracts.decision_trace import DecisionTrace, ExecutionProvenance
from backend.contracts.dependency import DependencyNode, DependencyEdge, EdgeType
from backend.contracts.dialogue import SpeechBubble, SceneDialogue, DialogueType
from backend.contracts.event import Event, EventType, EventLog
from backend.contracts.execution_plan import TaskSpec, ExecutionPlan, validate_execution_plan
from backend.contracts.export import ExportManifest, PageExportBundle, PanelExportSlot
from backend.contracts.goal import CreativeGoal
from backend.contracts.human_review import HumanReviewAction, HumanReviewCheckpoint, HumanReviewGate
from backend.contracts.layout import MangaPageLayout, SemanticPanelSlot, PanelImportance, RelativePosition
from backend.contracts.project_state import ProjectStateModel, AutonomyLevel
from backend.contracts.review import ContinuityReport, ReviewIssue, ReviewSeverity, ReviewCategory
from backend.contracts.scene import SceneScript, PanelDescription
from backend.contracts.story import StoryOutline, StoryBeat
from backend.contracts.task import Task, TaskStatus, TaskPriority
from backend.contracts.version import VersionEntry, DiffResult

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
