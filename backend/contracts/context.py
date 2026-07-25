from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


class ContextPolicy(BaseModel):
    """
    Configurable context requirements per agent type.
    """
    agent_type: str
    required_artifact_types: List[str] = Field(default_factory=list)
    include_character_blueprints: bool = False
    include_world_lore: bool = False
    include_style_guidelines: bool = False
    max_history_depth: int = 5


class AgentContext(BaseModel):
    """
    Focused payload prepared by the Context Engine for task execution.
    """
    task_id: str
    project_id: str
    target_agent_type: str
    goal: Dict[str, Any] = Field(default_factory=dict)
    relevant_artifacts: List[Dict[str, Any]] = Field(default_factory=list)
    character_blueprints: Dict[str, Any] = Field(default_factory=dict)
    style_guidelines: Dict[str, Any] = Field(default_factory=dict)
    additional_context: Dict[str, Any] = Field(default_factory=dict)
