from enum import Enum
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime


from enum import Enum
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
import uuid


class CapabilityType(str, Enum):
    GENERATE_TEXT = "GENERATE_TEXT"
    GENERATE_IMAGE = "GENERATE_IMAGE"
    VISION_REVIEW = "VISION_REVIEW"
    SEGMENT_IMAGE = "SEGMENT_IMAGE"
    INPAINT_IMAGE = "INPAINT_IMAGE"
    EXPORT_PDF = "EXPORT_PDF"


class CapabilityDescriptor(BaseModel):
    """
    Rich metadata describing a provider's execution capabilities for a CapabilityType.
    """
    capability_type: CapabilityType
    provider_name: str
    supported_models: List[str] = Field(default_factory=list)
    supports_streaming: bool = False
    supports_json: bool = True
    supports_seed: bool = True
    supports_vision: bool = False
    max_context_length: int = 4096


class ToolRequest(BaseModel):
    """
    Model-agnostic tool request payload dispatched to the Capability Registry.
    """
    request_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    capability_type: CapabilityType
    parameters: Dict[str, Any] = Field(default_factory=dict)
    preferred_provider: Optional[str] = None
    preferred_model: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ToolResponse(BaseModel):
    """
    Standardized response returned by Capability Providers with telemetry and provenance.
    """
    request_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    response_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    success: bool
    capability_type: CapabilityType
    provider_name: str
    model_name: str
    output_data: Dict[str, Any] = Field(default_factory=dict)
    error_message: Optional[str] = None
    execution_time_ms: float = 0.0
    token_usage: Dict[str, int] = Field(default_factory=dict)
    cost_usd: float = 0.0
    provenance_metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ResolvedProvider(BaseModel):
    """
    Pure value object holding the resolved provider instance, selected model, and capability descriptor.
    """
    capability_type: CapabilityType
    provider_name: str
    model_name: str
    provider_instance: Any  # BaseProvider reference
    descriptor: CapabilityDescriptor
    resolution_strategy: str = "PriorityRoutingStrategy"

    model_config = ConfigDict(arbitrary_types_allowed=True)

