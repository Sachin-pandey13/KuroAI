"""
KuroAI Configuration Package.
"""

from config.constants import PLATFORM_NAME, PLATFORM_VERSION
from config.defaults import (
    DEFAULT_CONTEXT_BUDGET,
    DEFAULT_MAX_RETRIES,
    DEFAULT_TASK_TIMEOUT_SECONDS,
)
from config.environment import settings

__all__ = [
    "settings",
    "DEFAULT_CONTEXT_BUDGET",
    "DEFAULT_MAX_RETRIES",
    "DEFAULT_TASK_TIMEOUT_SECONDS",
    "PLATFORM_NAME",
    "PLATFORM_VERSION",
]
