"""
CircuitBreaker — CLOSED / OPEN / HALF_OPEN state machine for provider resilience.

Usage:
    breaker = CircuitBreaker(failure_threshold=3, recovery_timeout=30.0)

    with breaker.context("openai"):
        response = openai_client.call(...)

    # After 3 consecutive failures, circuit opens.
    # After recovery_timeout seconds, circuit moves to HALF_OPEN.
    # One success closes it again; one failure re-opens it.
"""

import threading
import time
from enum import Enum
from typing import Any, Callable, Optional


class CircuitState(str, Enum):
    CLOSED = "CLOSED"  # Normal operation
    OPEN = "OPEN"  # Blocking calls — failure threshold crossed
    HALF_OPEN = "HALF_OPEN"  # Probe allowed — testing recovery


class CircuitOpenError(Exception):
    """Raised when a call is attempted while the circuit is OPEN."""

    pass


class CircuitBreaker:
    """
    CircuitBreaker pattern protecting a single resource or provider.

    States:
        CLOSED    → calls pass through, failures counted
        OPEN      → calls blocked, recovery_timeout countdown begins
        HALF_OPEN → one probe call allowed; success → CLOSED, failure → OPEN
    """

    def __init__(
        self,
        failure_threshold: int = 3,
        recovery_timeout: float = 30.0,
        name: str = "default",
    ) -> None:
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.name = name

        self._state: CircuitState = CircuitState.CLOSED
        self._failure_count: int = 0
        self._last_failure_time: Optional[float] = None
        self._lock = threading.Lock()

    @property
    def state(self) -> CircuitState:
        with self._lock:
            return self._evaluate_state()

    def _evaluate_state(self) -> CircuitState:
        """Transition OPEN → HALF_OPEN if recovery_timeout has elapsed."""
        if self._state == CircuitState.OPEN:
            if (
                self._last_failure_time
                and (time.monotonic() - self._last_failure_time) >= self.recovery_timeout
            ):
                self._state = CircuitState.HALF_OPEN
        return self._state

    def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute func if circuit is CLOSED or HALF_OPEN.
        Records result and transitions state accordingly.
        """
        with self._lock:
            state = self._evaluate_state()
            if state == CircuitState.OPEN:
                raise CircuitOpenError(
                    f"Circuit '{self.name}' is OPEN. Calls blocked. "
                    f"Recovery in {self.recovery_timeout}s."
                )

        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except Exception:
            self._on_failure()
            raise

    def _on_success(self) -> None:
        with self._lock:
            self._failure_count = 0
            self._state = CircuitState.CLOSED

    def _on_failure(self) -> None:
        with self._lock:
            self._failure_count += 1
            self._last_failure_time = time.monotonic()
            if self._failure_count >= self.failure_threshold:
                self._state = CircuitState.OPEN

    def reset(self) -> None:
        """Manually reset circuit to CLOSED state."""
        with self._lock:
            self._state = CircuitState.CLOSED
            self._failure_count = 0
            self._last_failure_time = None

    def context(self, operation_name: str = ""):
        """Context manager interface for circuit breaker."""

        class _CircuitContext:
            def __init__(self_ctx):
                pass

            def __enter__(self_ctx):
                with self._lock:
                    state = self._evaluate_state()
                    if state == CircuitState.OPEN:
                        raise CircuitOpenError(f"Circuit '{self.name}' is OPEN. Calls blocked.")
                return self_ctx

            def __exit__(self_ctx, exc_type, exc_val, exc_tb):
                if exc_type is not None:
                    self._on_failure()
                else:
                    self._on_success()
                return False  # Don't suppress exceptions

        return _CircuitContext()
