from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ContextSelector(str, Enum):
    PROJECT_STATE = "PROJECT.STATE"
    PROJECT_STYLE = "PROJECT.STYLE"
    PROJECT_LORE = "PROJECT.LORE"
    ARTIFACT_UPSTREAM = "ARTIFACT.UPSTREAM"
    ARTIFACT_HISTORY = "ARTIFACT.HISTORY"
    ARTIFACT_RELATED = "ARTIFACT.RELATED"
    CHARACTER_BLUEPRINT = "CHARACTER.BLUEPRINT"
    CHARACTER_RELATIONSHIPS = "CHARACTER.RELATIONSHIPS"


class ContextSectionType(str, Enum):
    GOAL = "GOAL"
    UPSTREAM_ARTIFACT = "UPSTREAM_ARTIFACT"
    ARTIFACT = "ARTIFACT"  # Generic artifact reference
    DIRECTOR_BRIEF = "DIRECTOR_BRIEF"  # DirectorAgent brief artifact
    CHARACTER_BLUEPRINT = "CHARACTER_BLUEPRINT"
    STYLE_GUIDELINES = "STYLE_GUIDELINES"
    WORLD_LORE = "WORLD_LORE"
    VERSION_HISTORY = "VERSION_HISTORY"
    CUSTOM = "CUSTOM"


class BudgetStrategy(str, Enum):
    DROP = "DROP"  # Shed section if budget exceeded
    TRUNCATE = "TRUNCATE"  # Trim section content payload length if budget exceeded
    SUMMARIZE = "SUMMARIZE"  # Reserved for future LLM summarization


class ContextPolicy(BaseModel):
    """
    Configurable context requirements per agent type.
    """

    agent_type: str
    selectors: List[ContextSelector] = Field(
        default_factory=lambda: [
            ContextSelector.PROJECT_STATE,
            ContextSelector.ARTIFACT_UPSTREAM,
        ]
    )
    required_artifact_types: List[str] = Field(default_factory=list)
    include_character_blueprints: bool = False
    include_world_lore: bool = False
    include_style_guidelines: bool = False
    max_history_depth: int = 0
    max_token_budget: int = 4000
    budget_strategy: BudgetStrategy = BudgetStrategy.DROP
    priority_order: List[ContextSelector] = Field(
        default_factory=lambda: [
            ContextSelector.PROJECT_STATE,
            ContextSelector.ARTIFACT_UPSTREAM,
            ContextSelector.CHARACTER_BLUEPRINT,
            ContextSelector.PROJECT_STYLE,
            ContextSelector.PROJECT_LORE,
            ContextSelector.ARTIFACT_HISTORY,
        ]
    )


class ContextSection(BaseModel):
    """
    A single self-contained, typed section of an AgentContext payload.
    """

    section_type: ContextSectionType
    title: str
    content: Dict[str, Any] = Field(default_factory=dict)
    priority: int = 1
    estimated_token_cost: int = 0


class AgentContext(BaseModel):
    """
    Focused, extensible payload prepared by the Context Engine for task execution.
    Supports both section-based M6 payloads and backward-compatible M1 fields.
    """

    task_id: str
    project_id: str
    target_agent_type: str
    action_type: str = "EXECUTE"
    sections: List[ContextSection] = Field(default_factory=list)
    total_token_cost: int = 0
    is_truncated: bool = False

    # Backward-compatibility fields
    goal: Dict[str, Any] = Field(default_factory=dict)
    relevant_artifacts: List[Dict[str, Any]] = Field(default_factory=list)
    character_blueprints: Dict[str, Any] = Field(default_factory=dict)
    style_guidelines: Dict[str, Any] = Field(default_factory=dict)
    additional_context: Dict[str, Any] = Field(default_factory=dict)

    def get_section(self, section_type: ContextSectionType) -> Optional[ContextSection]:
        """Convenience method to retrieve a specific section by ContextSectionType."""
        for s in self.sections:
            if s.section_type == section_type:
                return s
        return None

    @property
    def goal_id(self) -> str:
        """Convenience helper to extract goal_id from goal dict or fallback to task_id."""
        return self.goal.get("goal_id", self.task_id)  # type: ignore[no-any-return]
