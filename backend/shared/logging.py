"""
Standardized logging configuration and logger factory for KuroAI.

Schema:
%(asctime)s | %(levelname)s | %(name)s | request_id=%(request_id)s task_id=%(task_id)s artifact_id=%(artifact_id)s agent_type=%(agent_type)s provider=%(provider_name)s duration_ms=%(duration_ms)s | %(message)s
"""

import logging
import sys
from typing import Optional, Dict, Any

DEFAULT_LOG_FORMAT = (
    "%(asctime)s | %(levelname)-8s | %(name)s | "
    "request_id=%(request_id)s task_id=%(task_id)s artifact_id=%(artifact_id)s "
    "agent_type=%(agent_type)s provider=%(provider_name)s duration_ms=%(duration_ms)s | "
    "%(message)s"
)


class StructuredLogFormatter(logging.Formatter):
    """Custom logging formatter injecting default contextual attributes if missing."""

    def format(self, record: logging.LogRecord) -> str:
        defaults = {
            "request_id": "-",
            "task_id": "-",
            "artifact_id": "-",
            "agent_type": "-",
            "provider_name": "-",
            "duration_ms": "-",
        }
        for key, val in defaults.items():
            if not hasattr(record, key):
                setattr(record, key, val)
        return super().format(record)


def get_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """
    Get or create a configured structured logger.

    Args:
        name: The name of the logger module.
        level: Minimum logging severity level.

    Returns:
        logging.Logger: Configured logger instance.
    """
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(StructuredLogFormatter(DEFAULT_LOG_FORMAT))
        logger.addHandler(handler)
        logger.setLevel(level)
        logger.propagate = False
    return logger
