"""
Span model for distributed tracing in KuroAI.
"""

import time
import uuid
from typing import Any, Dict, List, Optional


class Span:
    """
    Represents a single operation within a trace.
    Supports hierarchical relationships (parent_span_id), attributes, and lifecycle timing.
    """

    def __init__(
        self,
        name: str,
        trace_id: Optional[str] = None,
        span_id: Optional[str] = None,
        parent_span_id: Optional[str] = None,
    ):
        self.name: str = name
        self.trace_id: str = trace_id or uuid.uuid4().hex
        self.span_id: str = span_id or uuid.uuid4().hex[:16]
        self.parent_span_id: Optional[str] = parent_span_id
        self.start_time: float = time.time()
        self.end_time: Optional[float] = None
        self.attributes: Dict[str, Any] = {}
        self.events: List[Dict[str, Any]] = []
        self.status: str = "UNSET"  # "OK", "ERROR", "UNSET"
        self.error_message: Optional[str] = None

    def set_attribute(self, key: str, value: Any) -> "Span":
        """Set a single attribute key-value pair."""
        self.attributes[key] = value
        return self

    def set_attributes(self, attrs: Dict[str, Any]) -> "Span":
        """Set multiple attributes at once."""
        self.attributes.update(attrs)
        return self

    def add_event(self, name: str, attributes: Optional[Dict[str, Any]] = None) -> "Span":
        """Add an event timestamped relative to span execution."""
        self.events.append(
            {
                "name": name,
                "timestamp": time.time(),
                "attributes": attributes or {},
            }
        )
        return self

    def set_status(self, status: str, description: Optional[str] = None) -> "Span":
        """Set span completion status ("OK" or "ERROR")."""
        self.status = status
        if description:
            self.error_message = description
        return self

    def end(self) -> "Span":
        """Record end time for the span."""
        if self.end_time is None:
            self.end_time = time.time()
        return self

    @property
    def duration_ms(self) -> float:
        """Calculate duration in milliseconds."""
        end = self.end_time or time.time()
        return round((end - self.start_time) * 1000, 3)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize span to dictionary representation."""
        return {
            "name": self.name,
            "trace_id": self.trace_id,
            "span_id": self.span_id,
            "parent_span_id": self.parent_span_id,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration_ms": self.duration_ms,
            "status": self.status,
            "error_message": self.error_message,
            "attributes": self.attributes,
            "events": self.events,
        }
