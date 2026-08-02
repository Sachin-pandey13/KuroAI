"""
Context-propagating tracer for KuroAI using Python contextvars.
"""

import contextvars
from typing import Any, Callable, List, Optional

from backend.telemetry.span import Span

# Context variable storing the current active span
_CURRENT_SPAN: contextvars.ContextVar[Optional[Span]] = contextvars.ContextVar(
    "_CURRENT_SPAN", default=None
)


class Tracer:
    """
    Manages creation and context propagation of execution spans.
    """

    def __init__(self, name: str = "kuroai-tracer") -> None:
        self.name: str = name
        self._span_listeners: List[Callable[[Span], None]] = []

    def add_span_listener(self, listener: Callable[[Span], None]) -> None:
        """Register a callback invoked when any span ends."""
        self._span_listeners.append(listener)

    def start_span(self, name: str, attributes: Optional[dict] = None) -> Span:
        """
        Start a new span as a child of the current active span (if any).
        """
        parent_span = _CURRENT_SPAN.get()
        if parent_span:
            trace_id = parent_span.trace_id
            parent_span_id = parent_span.span_id
        else:
            trace_id = None
            parent_span_id = None

        span = Span(name=name, trace_id=trace_id, parent_span_id=parent_span_id)
        if attributes:
            span.set_attributes(attributes)

        return span

    def end_span(self, span: Span) -> None:
        """End a span and notify all registered listeners."""
        span.end()
        for listener in self._span_listeners:
            try:
                listener(span)
            except Exception:
                pass

    def start_as_current_span(self, name: str, attributes: Optional[dict] = None):
        """
        Context manager to automatically set and restore current active span.
        """

        class _SpanContextManager:
            def __init__(self, tracer: Tracer, span_name: str, attrs: Optional[dict]):
                self.tracer = tracer
                self.span_name = span_name
                self.attrs = attrs
                self.span: Optional[Span] = None
                self.token: Any = None

            def __enter__(self) -> Span:
                self.span = self.tracer.start_span(self.span_name, self.attrs)
                self.token = _CURRENT_SPAN.set(self.span)
                return self.span

            def __exit__(self, exc_type, exc_val, exc_tb):
                if exc_type is not None:
                    self.span.set_status("ERROR", str(exc_val))
                else:
                    if self.span.status == "UNSET":
                        self.span.set_status("OK")

                _CURRENT_SPAN.reset(self.token)
                self.tracer.end_span(self.span)

        return _SpanContextManager(self, name, attributes)


def get_current_span() -> Optional[Span]:
    """Return the active span in the current context."""
    return _CURRENT_SPAN.get()
