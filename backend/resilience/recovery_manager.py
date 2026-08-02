"""
RecoveryManager — checkpoint-based state recovery, dead-letter queue,
poison task detection, and graceful shutdown handling.
"""

import time
import threading
from typing import Any, Dict, List, Optional
from collections import deque
import logging

logger = logging.getLogger("kuroai.resilience.recovery")


class PoisonTaskError(Exception):
    """Raised when a task has exceeded its failure threshold and is quarantined."""
    pass


class RecoveryManager:
    """
    Manages runtime resilience through checkpointing, rollback, dead-letter queues,
    and poison task detection.

    Key features:
    - save_checkpoint / restore_checkpoint: snapshot any serializable state dict.
    - dead_letter_queue: tasks quarantined after exceeding max_failures.
    - is_poison_task: detect tasks that have repeatedly failed.
    - graceful_shutdown: signal orderly teardown and wait for running operations.
    """

    def __init__(self, max_failures_before_poison: int = 3) -> None:
        self.max_failures = max_failures_before_poison
        self._checkpoints: Dict[str, Dict[str, Any]] = {}
        self._dead_letter_queue: deque = deque()
        self._failure_counts: Dict[str, int] = {}
        self._shutdown_event = threading.Event()
        self._lock = threading.Lock()

    # ── Checkpointing ──────────────────────────────────────────────────────

    def save_checkpoint(self, key: str, state: Dict[str, Any]) -> None:
        """Persist a named checkpoint."""
        with self._lock:
            self._checkpoints[key] = {
                "state": state,
                "saved_at": time.time(),
            }
        logger.info(f"Checkpoint saved: {key}")

    def restore_checkpoint(self, key: str) -> Optional[Dict[str, Any]]:
        """Restore a previously saved checkpoint. Returns None if not found."""
        with self._lock:
            entry = self._checkpoints.get(key)
        if entry:
            logger.info(f"Checkpoint restored: {key}")
            return entry["state"]
        logger.warning(f"Checkpoint not found: {key}")
        return None

    def list_checkpoints(self) -> List[str]:
        with self._lock:
            return list(self._checkpoints.keys())

    # ── Dead-Letter Queue ──────────────────────────────────────────────────

    def record_failure(self, task_id: str, error: str) -> None:
        """Record a task failure. Quarantine to DLQ if threshold exceeded."""
        with self._lock:
            self._failure_counts[task_id] = self._failure_counts.get(task_id, 0) + 1
            if self._failure_counts[task_id] >= self.max_failures:
                self._dead_letter_queue.append({
                    "task_id": task_id,
                    "error": error,
                    "failed_at": time.time(),
                    "failure_count": self._failure_counts[task_id],
                })
                logger.error(f"Task {task_id} quarantined to dead-letter queue after {self._failure_counts[task_id]} failures.")

    def is_poison_task(self, task_id: str) -> bool:
        """Return True if task has been quarantined."""
        with self._lock:
            return self._failure_counts.get(task_id, 0) >= self.max_failures

    def get_dead_letter_queue(self) -> List[Dict[str, Any]]:
        """Return snapshot of all dead-lettered tasks."""
        with self._lock:
            return list(self._dead_letter_queue)

    def flush_dead_letter_queue(self) -> int:
        """Clear the dead-letter queue and return number of tasks flushed."""
        with self._lock:
            count = len(self._dead_letter_queue)
            self._dead_letter_queue.clear()
            return count

    # ── Graceful Shutdown ──────────────────────────────────────────────────

    def signal_shutdown(self) -> None:
        """Signal graceful shutdown to all waiting operations."""
        self._shutdown_event.set()
        logger.info("Graceful shutdown signaled.")

    def is_shutdown_requested(self) -> bool:
        return self._shutdown_event.is_set()

    def wait_for_shutdown(self, timeout: Optional[float] = None) -> bool:
        """Block until shutdown is signaled or timeout expires."""
        return self._shutdown_event.wait(timeout=timeout)
