"""
Exporter-agnostic metric primitives and structured event audit.
"""

import threading
import time
from typing import Any, Dict, List, Optional


class MetricExporter:
    """Abstract interface for metric exporters."""

    def export_metrics(self, metrics_data: List[Dict[str, Any]]) -> None:
        raise NotImplementedError


class ConsoleExporter(MetricExporter):
    """Exports metrics to console output."""

    def export_metrics(self, metrics_data: List[Dict[str, Any]]) -> None:
        for item in metrics_data:
            print(
                f"[METRIC] {item['name']} ({item['type']}): {item['value']} | labels={item.get('labels', {})}"
            )


class JSONExporter(MetricExporter):
    """Exports metrics as JSON objects stored in memory / log output."""

    def __init__(self) -> None:
        self.exported: List[Dict[str, Any]] = []

    def export_metrics(self, metrics_data: List[Dict[str, Any]]) -> None:
        self.exported.extend(metrics_data)


class PrometheusExporter(MetricExporter):
    """Formats metrics according to Prometheus exposition format."""

    def __init__(self) -> None:
        self.lines: List[str] = []

    def export_metrics(self, metrics_data: List[Dict[str, Any]]) -> None:
        formatted = []
        for item in metrics_data:
            labels_str = ",".join(f'{k}="{v}"' for k, v in item.get("labels", {}).items())
            labels_part = f"{{{labels_str}}}" if labels_str else ""
            name = item["name"].replace(".", "_").replace("-", "_")
            formatted.append(f"# TYPE {name} {item['type']}")
            formatted.append(f"{name}{labels_part} {item['value']}")
        self.lines = formatted

    def get_prometheus_output(self) -> str:
        return "\n".join(self.lines) + "\n" if self.lines else ""


class OpenTelemetryExporter(MetricExporter):
    """Formats metrics according to OpenTelemetry data structures."""

    def __init__(self) -> None:
        self.otlp_records: List[Dict[str, Any]] = []

    def export_metrics(self, metrics_data: List[Dict[str, Any]]) -> None:
        for item in metrics_data:
            self.otlp_records.append(
                {
                    "metric_name": item["name"],
                    "type": item["type"],
                    "points": [{"value": item["value"], "time_unix_nano": int(time.time() * 1e9)}],
                    "attributes": item.get("labels", {}),
                }
            )


class Counter:
    """Cumulative metric representing a single monotonically increasing counter."""

    def __init__(self, name: str, description: str = "") -> None:
        self.name: str = name
        self.description: str = description
        self._value: float = 0.0
        self._lock = threading.Lock()
        self._labels_values: Dict[str, float] = {}

    def inc(self, value: float = 1.0, labels: Optional[Dict[str, str]] = None) -> None:
        if value < 0:
            raise ValueError("Counter increments must be non-negative")
        with self._lock:
            self._value += value
            if labels:
                key = str(sorted(labels.items()))
                self._labels_values[key] = self._labels_values.get(key, 0.0) + value

    def get_value(self) -> float:
        with self._lock:
            return self._value


class Gauge:
    """Metric representing a value that can arbitrarily go up and down."""

    def __init__(self, name: str, description: str = "") -> None:
        self.name: str = name
        self.description: str = description
        self._value: float = 0.0
        self._lock = threading.Lock()

    def set(self, value: float) -> None:
        with self._lock:
            self._value = value

    def inc(self, value: float = 1.0) -> None:
        with self._lock:
            self._value += value

    def dec(self, value: float = 1.0) -> None:
        with self._lock:
            self._value -= value

    def get_value(self) -> float:
        with self._lock:
            return self._value


class Histogram:
    """Tracks sample observations (usually latencies or sizes) in buckets."""

    def __init__(self, name: str, description: str = "") -> None:
        self.name: str = name
        self.description: str = description
        self._observations: List[float] = []
        self._lock = threading.Lock()

    def observe(self, value: float) -> None:
        with self._lock:
            self._observations.append(value)

    def get_summary(self) -> Dict[str, float]:
        with self._lock:
            if not self._observations:
                return {"count": 0, "sum": 0.0, "avg": 0.0, "p50": 0.0, "p95": 0.0, "p99": 0.0}
            sorted_obs = sorted(self._observations)
            n = len(sorted_obs)
            return {
                "count": float(n),
                "sum": sum(sorted_obs),
                "avg": sum(sorted_obs) / n,
                "p50": sorted_obs[int(n * 0.50)],
                "p95": sorted_obs[min(int(n * 0.95), n - 1)],
                "p99": sorted_obs[min(int(n * 0.99), n - 1)],
            }


class Timer:
    """Timer utility for measuring execution duration using Histogram."""

    def __init__(self, histogram: Histogram) -> None:
        self.histogram: Histogram = histogram
        self._start: Optional[float] = None

    def __enter__(self) -> "Timer":
        self._start = time.monotonic()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        if self._start is not None:
            elapsed_ms = (time.monotonic() - self._start) * 1000
            self.histogram.observe(elapsed_ms)


class EventAuditRegistry:
    """Structured Event Audit counter to track system-wide event occurrences."""

    def __init__(self) -> None:
        self._counts: Dict[str, int] = {}
        self._lock = threading.Lock()

    def record_event(self, event_type: str) -> None:
        """Record occurrence of a structured event."""
        with self._lock:
            self._counts[event_type] = self._counts.get(event_type, 0) + 1

    def get_count(self, event_type: str) -> int:
        with self._lock:
            return self._counts.get(event_type, 0)

    def get_all_counts(self) -> Dict[str, int]:
        with self._lock:
            return dict(self._counts)
