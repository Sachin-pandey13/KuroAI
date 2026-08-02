"""
System defaults for budgets, timeouts, retries, and allocations in KuroAI.
"""

from typing import Final

# Context Engine & Token Defaults
DEFAULT_CONTEXT_BUDGET: Final[int] = 4000
DEFAULT_MAX_TOKENS_PER_SECTION: Final[int] = 1000
DEFAULT_TRUNCATION_STRATEGY: Final[str] = "FIFO"

# Scheduler & Task Defaults
DEFAULT_MAX_RETRIES: Final[int] = 3
DEFAULT_TASK_TIMEOUT_SECONDS: Final[int] = 120
DEFAULT_CONCURRENCY_LIMIT: Final[int] = 5

# Provider Defaults
DEFAULT_LLM_TEMPERATURE: Final[float] = 0.7
DEFAULT_IMAGE_ASPECT_RATIO: Final[str] = "1:1"
DEFAULT_PROVIDER_TIMEOUT_SECONDS: Final[int] = 30
