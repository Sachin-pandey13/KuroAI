"""
Telemetry package for KuroAI.
Exports tracing, metrics, instrumentation, and telemetry manager.
"""

from backend.telemetry.span import Span
from backend.telemetry.tracing import Tracer, get_current_span
from backend.telemetry.metrics import (
    Counter,
    Gauge,
    Histogram,
    Timer,
    MetricExporter,
    ConsoleExporter,
    JSONExporter,
    PrometheusExporter,
    OpenTelemetryExporter,
    EventAuditRegistry,
)
from backend.telemetry.instrumentation import (
    instrument_task_execution,
    instrument_provider_execution,
    instrument_context_assembly,
    TASK_EXECUTION_COUNTER,
    TASK_LATENCY_HISTOGRAM,
    LLM_TOKEN_COUNTER,
    LLM_COST_COUNTER,
    EVENT_AUDIT,
)
from backend.telemetry.telemetry_manager import TelemetryManager
from backend.telemetry.instrumentation import (
    instrument_task_execution,
    instrument_provider_execution,
    instrument_context_assembly,
)

__all__ = [
    "Span",
    "Tracer",
    "get_current_span",
    "Counter",
    "Gauge",
    "Histogram",
    "Timer",
    "MetricExporter",
    "ConsoleExporter",
    "JSONExporter",
    "PrometheusExporter",
    "OpenTelemetryExporter",
    "EventAuditRegistry",
    "TelemetryManager",
    "TASK_EXECUTION_COUNTER",
    "TASK_LATENCY_HISTOGRAM",
    "LLM_TOKEN_COUNTER",
    "LLM_COST_COUNTER",
    "EVENT_AUDIT",
    "instrument_task_execution",
    "instrument_provider_execution",
    "instrument_context_assembly",
]
