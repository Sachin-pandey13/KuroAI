"""
Environment variable configuration loader for KuroAI.
"""

import os
from typing import Optional
from config import defaults


class Settings:
    """Application runtime settings backed by environment variables with fallback defaults."""

    @property
    def LOG_LEVEL(self) -> str:
        return os.getenv("KUROAI_LOG_LEVEL", "INFO").upper()

    @property
    def MAX_RETRIES(self) -> int:
        val = os.getenv("KUROAI_MAX_RETRIES")
        return int(val) if val and val.isdigit() else defaults.DEFAULT_MAX_RETRIES

    @property
    def DEFAULT_CONTEXT_BUDGET(self) -> int:
        val = os.getenv("KUROAI_CONTEXT_BUDGET")
        return int(val) if val and val.isdigit() else defaults.DEFAULT_CONTEXT_BUDGET

    @property
    def TASK_TIMEOUT_SECONDS(self) -> int:
        val = os.getenv("KUROAI_TASK_TIMEOUT")
        return int(val) if val and val.isdigit() else defaults.DEFAULT_TASK_TIMEOUT_SECONDS

    @property
    def OPENAI_API_KEY(self) -> Optional[str]:
        return os.getenv("OPENAI_API_KEY")

    @property
    def ANTHROPIC_API_KEY(self) -> Optional[str]:
        return os.getenv("ANTHROPIC_API_KEY")

    @property
    def GEMINI_API_KEY(self) -> Optional[str]:
        return os.getenv("GEMINI_API_KEY")


settings = Settings()
