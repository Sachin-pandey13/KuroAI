"""
Generic UTC timestamp utilities.
"""

from datetime import datetime, timezone


def utc_now() -> datetime:
    """Return the current timezone-aware UTC datetime."""
    return datetime.now(timezone.utc)


def utc_now_iso() -> str:
    """Return current UTC time in ISO-8601 string format."""
    return utc_now().isoformat()
