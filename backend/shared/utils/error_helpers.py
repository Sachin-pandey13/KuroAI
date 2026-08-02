"""
Generic error normalization utility.
"""

from typing import Dict, Any


def normalize_error(error: Exception) -> Dict[str, Any]:
    """
    Format an exception into a structured error dictionary.
    """
    return {
        "error_type": error.__class__.__name__,
        "message": str(error),
    }
