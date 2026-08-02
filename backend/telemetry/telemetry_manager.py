"""
Central Telemetry Manager for KuroAI.
"""

from typing import List, Dict, Any
from backend.telemetry.span import Span
from backend.telemetry.tracing import Tracer
from backend.telemetry.metrics import (
    MetricExporter,
    ConsoleExporter,
    JSONExporter,
    PrometheusExporter,
    OpenTelemetryExporter,
    EventAuditRegistry,
)
from backend.telemetry.instrumentation import (
    TASK_EXECUTION_COUNTER,
    TASK_LATENCY_HISTOGRAM,
    LLM_TOKEN_COUNTER,
    LLM_COST_COUNTER,
    EVENT_AUDIT,
)


class TelemetryManager:
    """
    Singleton telemetry manager controlling metrics, spans, and event auditing.
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(TelemetryManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self) -> None:
        if self._initialized:
            return
        self.tracer = Tracer("kuroai-telemetry")
        self.exporters: List[MetricExporter] = [JSONExporter(), PrometheusExporter()]
        self.event_audit: EventAuditRegistry = EVENT_AUDIT
        self.recorded_spans: List[Span] = []

        # Record finished spans locally
        self.tracer.add_span_listener(self._on_span_ended)
        self._initialized = True

    def _on_span_ended(self, span: Span) -> None:
        self.recorded_spans.append(span)

    def add_exporter(self, exporter: MetricExporter) -> None:
        """Register a new metric exporter."""
        self.exporters.append(exporter)

    def collect_metrics_snapshot(self) -> List[Dict[str, Any]]:
        """Gather current snapshot of all internal metrics."""
        summary_latency = TASK_LATENCY_HISTOGRAM.get_summary()
        snapshot = [
            {
                "name": "kuroai.task.executions",
                "type": "counter",
                "value": TASK_EXECUTION_COUNTER.get_value(),
            },
            {
                "name": "kuroai.task.latency_avg_ms",
                "type": "gauge",
                "value": summary_latency["avg"],
            },
            {
                "name": "kuroai.task.latency_p95_ms",
                "type": "gauge",
                "value": summary_latency["p95"],
            },
            {
                "name": "kuroai.llm.tokens",
                "type": "counter",
                "value": LLM_TOKEN_COUNTER.get_value(),
            },
            {
                "name": "kuroai.llm.cost_usd",
                "type": "counter",
                "value": LLM_COST_COUNTER.get_value(),
            },
        ]
        # Append event audit metrics
        for event_name, count in self.event_audit.get_all_counts().items():
            snapshot.append({
                "name": f"kuroai.event.{event_name.lower()}",
                "type": "counter",
                "value": float(count),
            })
        return snapshot

    def export_all(self) -> None:
        """Trigger metric export across all registered exporters."""
        metrics = self.collect_metrics_snapshot()
        for exporter in self.exporters:
            try:
                exporter.export_metrics(metrics)
            except Exception:
                pass

    def get_prometheus_output(self) -> str:
        """Return Prometheus metric format representation."""
        prom_exporter = next((e for e in self.exporters if isinstance(e, PrometheusExporter)), None)
        if prom_exporter:
            prom_exporter.export_metrics(self.collect_metrics_snapshot())
            return prom_exporter.get_prometheus_output()
        # Fallback exporter
        exporter = PrometheusExporter()
        exporter.export_metrics(self.collect_metrics_snapshot())
        return exporter.get_prometheus_output()
