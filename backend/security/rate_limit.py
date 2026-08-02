"""
Rate limiting utilities — token bucket and sliding window implementations.
"""

import time
import threading
from collections import deque


class RateLimitExceededError(Exception):
    """Raised when a rate limit is exceeded."""
    pass


class TokenBucketRateLimiter:
    """
    Token bucket rate limiter.
    Tokens refill at `rate` per second up to `capacity`.
    """

    def __init__(self, capacity: float, rate: float) -> None:
        self.capacity = capacity
        self.rate = rate
        self._tokens = float(capacity)
        self._last_check = time.monotonic()
        self._lock = threading.Lock()

    def _refill(self) -> None:
        now = time.monotonic()
        elapsed = now - self._last_check
        self._tokens = min(self.capacity, self._tokens + elapsed * self.rate)
        self._last_check = now

    def is_allowed(self, cost: float = 1.0) -> bool:
        with self._lock:
            self._refill()
            if self._tokens >= cost:
                self._tokens -= cost
                return True
            return False

    def consume(self, cost: float = 1.0) -> None:
        if not self.is_allowed(cost):
            raise RateLimitExceededError(
                f"Rate limit exceeded. Capacity={self.capacity}/s, rate={self.rate}/s."
            )


class SlidingWindowRateLimiter:
    """
    Sliding window rate limiter.
    Allows at most `max_calls` within a rolling `window_seconds` window.
    """

    def __init__(self, max_calls: int, window_seconds: float) -> None:
        self.max_calls = max_calls
        self.window_seconds = window_seconds
        self._calls: deque = deque()
        self._lock = threading.Lock()

    def is_allowed(self) -> bool:
        now = time.monotonic()
        with self._lock:
            cutoff = now - self.window_seconds
            while self._calls and self._calls[0] < cutoff:
                self._calls.popleft()
            if len(self._calls) < self.max_calls:
                self._calls.append(now)
                return True
            return False

    def consume(self) -> None:
        if not self.is_allowed():
            raise RateLimitExceededError(
                f"Rate limit exceeded. Max {self.max_calls} calls per {self.window_seconds}s."
            )
