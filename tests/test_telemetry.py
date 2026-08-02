"""
Unit tests for backend/telemetry module.
"""

from backend.telemetry import (
    Counter,
    EventAuditRegistry,
    Gauge,
    Histogram,
    Span,
    TelemetryManager,
    Timer,
    Tracer,
)


def test_span_lifecycle():
    span = Span(name="test-operation", trace_id="trace123")
    span.set_attribute("key", "val")
    span.add_event("event1", {"detail": "info"})
    span.set_status("OK")
    span.end()

    data = span.to_dict()
    assert data["name"] == "test-operation"
    assert data["trace_id"] == "trace123"
    assert data["status"] == "OK"
    assert data["attributes"]["key"] == "val"
    assert len(data["events"]) == 1
    assert data["duration_ms"] >= 0.0


def test_tracer_context_propagation():
    tracer = Tracer("test-tracer")

    with tracer.start_as_current_span("parent-span") as parent:
        assert parent.name == "parent-span"
        with tracer.start_as_current_span("child-span") as child:
            assert child.name == "child-span"
            assert child.trace_id == parent.trace_id
            assert child.parent_span_id == parent.span_id


def test_metrics_counter_gauge_histogram():
    c = Counter("test_counter")
    c.inc(5.0)
    assert c.get_value() == 5.0

    g = Gauge("test_gauge")
    g.set(10.0)
    g.dec(3.0)
    assert g.get_value() == 7.0

    h = Histogram("test_histogram")
    h.observe(10.0)
    h.observe(20.0)
    summary = h.get_summary()
    assert summary["count"] == 2.0
    assert summary["avg"] == 15.0


def test_timer_context_manager():
    h = Histogram("timer_hist")
    with Timer(h):
        pass
    assert h.get_summary()["count"] == 1.0


def test_event_audit_registry():
    audit = EventAuditRegistry()
    audit.record_event("TASK_COMPLETED")
    audit.record_event("TASK_COMPLETED")
    audit.record_event("TASK_FAILED")

    assert audit.get_count("TASK_COMPLETED") == 2
    assert audit.get_count("TASK_FAILED") == 1


def test_telemetry_manager_export():
    manager = TelemetryManager()
    manager.export_all()
    prom_output = manager.get_prometheus_output()
    assert "kuroai_task_executions" in prom_output
