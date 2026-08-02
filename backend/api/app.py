"""
FastAPI health and metrics endpoints for KuroAI production deployment.
"""

try:
    from fastapi import FastAPI
    from fastapi.responses import JSONResponse, PlainTextResponse
except ImportError:
    raise ImportError("FastAPI is required for the API server. Run: pip install fastapi uvicorn")

import time

from backend.resilience.recovery_manager import RecoveryManager
from backend.telemetry.telemetry_manager import TelemetryManager

app = FastAPI(
    title="KuroAI Platform API",
    description="Production health and observability endpoints for KuroAI v1.0 RC-2.",
    version="1.0.0-rc2",
)

_start_time = time.time()
_recovery = RecoveryManager()
_telemetry = TelemetryManager()


@app.get("/health/liveness", tags=["Health"])
async def liveness():
    """
    Liveness probe: confirms the process is alive and responding.
    Always returns 200 if the server is running.
    """
    return JSONResponse(
        content={"status": "alive", "uptime_seconds": round(time.time() - _start_time, 1)}
    )


@app.get("/health/readiness", tags=["Health"])
async def readiness():
    """
    Readiness probe: confirms the service is ready to handle requests.
    Returns 503 if shutdown is in progress.
    """
    if _recovery.is_shutdown_requested():
        return JSONResponse(status_code=503, content={"status": "shutting_down"})
    return JSONResponse(content={"status": "ready", "version": "1.0.0-rc2"})


@app.get("/metrics", tags=["Observability"])
async def metrics():
    """
    Prometheus-format metrics endpoint.
    Returns real-time system metrics in Prometheus exposition format.
    """
    output = _telemetry.get_prometheus_output()
    return PlainTextResponse(content=output, media_type="text/plain; version=0.0.4")


@app.get("/metrics/json", tags=["Observability"])
async def metrics_json():
    """JSON format metrics snapshot for dashboards and debugging."""
    snapshot = _telemetry.collect_metrics_snapshot()
    return JSONResponse(content={"metrics": snapshot})


@app.get("/metrics/events", tags=["Observability"])
async def event_audit():
    """Structured Event Audit counters — TASK_COMPLETED, ARTIFACT_REGISTERED, etc."""
    counts = _telemetry.event_audit.get_all_counts()
    return JSONResponse(content={"event_counts": counts})
