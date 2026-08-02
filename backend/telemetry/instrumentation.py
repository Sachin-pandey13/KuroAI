"""
Instrumentation hooks for core KuroAI subsystems.
"""

import functools
import time
from typing import Callable, Any
from backend.telemetry.tracing import Tracer, get_current_span
from backend.telemetry.metrics import Counter, Histogram, EventAuditRegistry

# Global metric instances
TASK_EXECUTION_COUNTER = Counter("kuroai.task.executions", "Total task executions")
TASK_LATENCY_HISTOGRAM = Histogram("kuroai.task.latency_ms", "Task latency in ms")
LLM_TOKEN_COUNTER = Counter("kuroai.llm.tokens", "Total tokens used by LLMs")
LLM_COST_COUNTER = Counter("kuroai.llm.cost_usd", "Estimated LLM cost in USD")
EVENT_AUDIT = EventAuditRegistry()


def instrument_task_execution(tracer: Tracer) -> Callable:
    """Decorator to instrument task executions with tracing and metrics."""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(self, task, *args, **kwargs):
            start = time.monotonic()
            TASK_EXECUTION_COUNTER.inc(1.0, {"agent_type": getattr(task, "agent_type", "unknown")})
            EVENT_AUDIT.record_event("TASK_STARTED")

            with tracer.start_as_current_span(
                f"AgentRuntime.run_task:{getattr(task, 'agent_type', 'unknown')}",
                {"task_id": getattr(task, "task_id", ""), "agent_type": getattr(task, "agent_type", "")}
            ) as span:
                try:
                    result = await func(self, task, *args, **kwargs)
                    span.set_status("OK")
                    EVENT_AUDIT.record_event("TASK_COMPLETED")
                    return result
                except Exception as exc:
                    span.set_status("ERROR", str(exc))
                    EVENT_AUDIT.record_event("TASK_FAILED")
                    raise
                finally:
                    elapsed_ms = (time.monotonic() - start) * 1000
                    TASK_LATENCY_HISTOGRAM.observe(elapsed_ms)
        return wrapper
    return decorator


def instrument_provider_execution(tracer: Tracer) -> Callable:
    """Decorator to instrument capability tool execution."""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(self, request, *args, **kwargs):
            with tracer.start_as_current_span(
                f"CapabilityRegistry.execute:{getattr(request, 'capability_type', 'tool')}",
                {"capability_type": getattr(request, "capability_type", ""), "provider_name": getattr(request, "provider_name", "")}
            ) as span:
                try:
                    response = func(self, request, *args, **kwargs)
                    if hasattr(response, "success") and not response.success:
                        span.set_status("ERROR", getattr(response, "error_message", "Execution failed"))
                    else:
                        span.set_status("OK")
                    return response
                except Exception as exc:
                    span.set_status("ERROR", str(exc))
                    raise
        return wrapper
    return decorator


def instrument_context_assembly(tracer: Tracer) -> Callable:
    """Decorator to instrument ContextEngine assembly."""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(self, task, *args, **kwargs):
            with tracer.start_as_current_span(
                "ContextEngine.assemble_context",
                {"task_id": getattr(task, "task_id", "")}
            ) as span:
                result = func(self, task, *args, **kwargs)
                span.set_status("OK")
                return result
        return wrapper
    return decorator
