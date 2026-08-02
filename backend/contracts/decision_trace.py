from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ExecutionProvenance(BaseModel):
    """
    Exact parameter provenance for 100% reproducibility (Second Law).
    """

    model_name: str
    provider_name: str
    seed: Optional[int] = None
    prompt: str
    negative_prompt: Optional[str] = None
    hyperparameters: Dict[str, Any] = Field(default_factory=dict)
    lora_weights: Dict[str, float] = Field(default_factory=dict)
    controlnet_adapters: List[str] = Field(default_factory=list)


class DecisionTrace(BaseModel):
    """
    Structured explainability metadata attached to every agent decision.
    """

    agent_id: str
    confidence_score: float = Field(ge=0.0, le=1.0)
    reasoning_rationale: str
    identified_risks: List[str] = Field(default_factory=list)
    evaluated_alternatives: List[Dict[str, Any]] = Field(default_factory=list)
    context_sources_used: List[str] = Field(default_factory=list)
    provenance: ExecutionProvenance
    timestamp: datetime = Field(default_factory=datetime.utcnow)
