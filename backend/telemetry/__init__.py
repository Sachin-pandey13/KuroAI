"""
Telemetry package for KuroAI.
Exports tracing, metrics, instrumentation, and telemetry manager.
"""

from backend.telemetry.instrumentation import (
    EVENT_AUDIT,
    LLM_COST_COUNTER,
    LLM_TOKEN_COUNTER,
    TASK_EXECUTION_COUNTER,
    TASK_LATENCY_HISTOGRAM,
    instrument_context_assembly,
    instrument_provider_execution,
    instrument_task_execution,
)
from backend.telemetry.metrics import (
    ConsoleExporter,
    Counter,
    EventAuditRegistry,
    Gauge,
    Histogram,
    JSONExporter,
    MetricExporter,
    OpenTelemetryExporter,
    PrometheusExporter,
    Timer,
)
from backend.telemetry.span import Span
from backend.telemetry.telemetry_manager import TelemetryManager
from backend.telemetry.tracing import Tracer, get_current_span

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
