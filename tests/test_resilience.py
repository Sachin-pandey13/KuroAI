"""
Resilience unit tests — CircuitBreaker, RetryPolicy, RecoveryManager.
"""

import time
import pytest
from backend.resilience import (
    CircuitBreaker,
    CircuitState,
    CircuitOpenError,
    RetryPolicy,
    MaxRetriesExceededError,
    RecoveryManager,
)


# ─── CircuitBreaker ────────────────────────────────────────────────────────────

class TestCircuitBreaker:
    def test_starts_closed(self):
        breaker = CircuitBreaker(failure_threshold=3, recovery_timeout=60)
        assert breaker.state == CircuitState.CLOSED

    def test_opens_after_threshold(self):
        breaker = CircuitBreaker(failure_threshold=3, recovery_timeout=60)
        def failing():
            raise RuntimeError("fail")
        for _ in range(3):
            with pytest.raises(RuntimeError):
                breaker.call(failing)
        assert breaker.state == CircuitState.OPEN

    def test_blocks_when_open(self):
        breaker = CircuitBreaker(failure_threshold=1, recovery_timeout=60)
        with pytest.raises(RuntimeError):
            breaker.call(lambda: (_ for _ in ()).throw(RuntimeError("x")))
        with pytest.raises(CircuitOpenError):
            breaker.call(lambda: "ok")

    def test_closes_after_success(self):
        breaker = CircuitBreaker(failure_threshold=3, recovery_timeout=60)
        with pytest.raises(RuntimeError):
            breaker.call(lambda: (_ for _ in ()).throw(RuntimeError("x")))
        breaker.call(lambda: "success")
        assert breaker.state == CircuitState.CLOSED

    def test_context_manager_on_success(self):
        breaker = CircuitBreaker(failure_threshold=3, recovery_timeout=60)
        with breaker.context("op"):
            pass
        assert breaker.state == CircuitState.CLOSED

    def test_context_manager_on_failure(self):
        breaker = CircuitBreaker(failure_threshold=1, recovery_timeout=60)
        with pytest.raises(ValueError):
            with breaker.context("op"):
                raise ValueError("error")
        assert breaker.state == CircuitState.OPEN

    def test_manual_reset(self):
        breaker = CircuitBreaker(failure_threshold=1, recovery_timeout=60)
        with pytest.raises(RuntimeError):
            breaker.call(lambda: (_ for _ in ()).throw(RuntimeError("x")))
        breaker.reset()
        assert breaker.state == CircuitState.CLOSED

    def test_half_open_after_timeout(self):
        breaker = CircuitBreaker(failure_threshold=1, recovery_timeout=0.05)
        with pytest.raises(RuntimeError):
            breaker.call(lambda: (_ for _ in ()).throw(RuntimeError("x")))
        time.sleep(0.1)
        assert breaker.state == CircuitState.HALF_OPEN


# ─── RetryPolicy ───────────────────────────────────────────────────────────────

class TestRetryPolicy:
    def test_succeeds_on_first_try(self):
        policy = RetryPolicy(max_retries=3, base_delay=0)
        result = policy.execute(lambda: 42)
        assert result == 42

    def test_retries_and_succeeds(self):
        attempt_counter = {"count": 0}
        def flaky():
            attempt_counter["count"] += 1
            if attempt_counter["count"] < 3:
                raise ValueError("temporary failure")
            return "success"

        policy = RetryPolicy(max_retries=5, base_delay=0, jitter=False)
        result = policy.execute(flaky)
        assert result == "success"
        assert attempt_counter["count"] == 3

    def test_raises_after_max_retries(self):
        policy = RetryPolicy(max_retries=2, base_delay=0, jitter=False)
        with pytest.raises(MaxRetriesExceededError):
            policy.execute(lambda: (_ for _ in ()).throw(RuntimeError("always fails")))


# ─── RecoveryManager ───────────────────────────────────────────────────────────

class TestRecoveryManager:
    def test_checkpoint_save_and_restore(self):
        rm = RecoveryManager()
        state = {"task_id": "t1", "progress": 42}
        rm.save_checkpoint("test_key", state)
        restored = rm.restore_checkpoint("test_key")
        assert restored == state

    def test_restore_missing_checkpoint(self):
        rm = RecoveryManager()
        result = rm.restore_checkpoint("nonexistent")
        assert result is None

    def test_poison_task_detection(self):
        rm = RecoveryManager(max_failures_before_poison=3)
        for i in range(3):
            rm.record_failure("task_99", f"error_{i}")
        assert rm.is_poison_task("task_99") is True

    def test_dead_letter_queue(self):
        rm = RecoveryManager(max_failures_before_poison=2)
        rm.record_failure("task_bad", "failure 1")
        rm.record_failure("task_bad", "failure 2")
        dlq = rm.get_dead_letter_queue()
        assert any(item["task_id"] == "task_bad" for item in dlq)

    def test_flush_dead_letter_queue(self):
        rm = RecoveryManager(max_failures_before_poison=1)
        rm.record_failure("task_x", "err")
        count = rm.flush_dead_letter_queue()
        assert count >= 1
        assert rm.get_dead_letter_queue() == []

    def test_graceful_shutdown_signaling(self):
        rm = RecoveryManager()
        assert rm.is_shutdown_requested() is False
        rm.signal_shutdown()
        assert rm.is_shutdown_requested() is True
        result = rm.wait_for_shutdown(timeout=0.1)
        assert result is True
