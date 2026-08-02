"""
Retry policy with exponential backoff and jitter.
"""

import logging
import random
import time
from typing import Any, Callable, Optional, Tuple, Type

logger = logging.getLogger("kuroai.resilience.retry")


class MaxRetriesExceededError(Exception):
    """Raised when all retry attempts are exhausted."""

    pass


class RetryPolicy:
    """
    Configurable retry policy with exponential backoff and jitter.

    Example:
        policy = RetryPolicy(max_retries=3, base_delay=1.0, max_delay=30.0)
        result = policy.execute(my_function, arg1, arg2)
    """

    def __init__(
        self,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 30.0,
        backoff_factor: float = 2.0,
        jitter: bool = True,
        retryable_exceptions: Tuple[Type[Exception], ...] = (Exception,),
    ) -> None:
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.backoff_factor = backoff_factor
        self.jitter = jitter
        self.retryable_exceptions = retryable_exceptions

    def _compute_delay(self, attempt: int) -> float:
        delay = min(self.base_delay * (self.backoff_factor**attempt), self.max_delay)
        if self.jitter:
            delay = delay * (0.5 + random.random() * 0.5)
        return delay

    def execute(self, func: Callable, *args, **kwargs) -> Any:
        """Execute func with retry on failure."""
        last_exception: Optional[Exception] = None

        for attempt in range(self.max_retries + 1):
            try:
                return func(*args, **kwargs)
            except self.retryable_exceptions as exc:
                last_exception = exc
                if attempt < self.max_retries:
                    delay = self._compute_delay(attempt)
                    logger.warning(
                        f"Attempt {attempt + 1}/{self.max_retries + 1} failed: {exc}. "
                        f"Retrying in {delay:.2f}s..."
                    )
                    time.sleep(delay)

        raise MaxRetriesExceededError(
            f"All {self.max_retries + 1} attempts failed. Last error: {last_exception}"
        ) from last_exception
