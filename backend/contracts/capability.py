from enum import Enum
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class CapabilityType(str, Enum):
    GENERATE_TEXT = "GENERATE_TEXT"
    GENERATE_IMAGE = "GENERATE_IMAGE"
    SEGMENT_IMAGE = "SEGMENT_IMAGE"
    INPAINT_IMAGE = "INPAINT_IMAGE"
    EXPORT_PDF = "EXPORT_PDF"


class ToolRequest(BaseModel):
    """
    Model-agnostic tool request payload dispatched to the Capability Registry.
    """
    capability_type: CapabilityType
    parameters: Dict[str, Any] = Field(default_factory=dict)
    preferred_provider: Optional[str] = None
    preferred_model: Optional[str] = None


class ToolResponse(BaseModel):
    """
    Standardized response returned by Capability Providers.
    """
    success: bool
    capability_type: CapabilityType
    provider_name: str
    model_name: str
    output_data: Dict[str, Any] = Field(default_factory=dict)
    error_message: Optional[str] = None
    execution_time_ms: float = 0.0
    provenance_metadata: Dict[str, Any] = Field(default_factory=dict)
