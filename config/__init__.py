"""
KuroAI Configuration Package.
"""

from config.defaults import *
from config.environment import settings
from config.constants import *

__all__ = [
    "settings",
    "DEFAULT_CONTEXT_BUDGET",
    "DEFAULT_MAX_RETRIES",
    "DEFAULT_TASK_TIMEOUT_SECONDS",
    "PLATFORM_NAME",
    "PLATFORM_VERSION",
]
