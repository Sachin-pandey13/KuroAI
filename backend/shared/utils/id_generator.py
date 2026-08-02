"""
Generic UUID generation utilities.
"""

import uuid


def generate_uuid() -> str:
    """Generate a standard string representation of a UUIDv4."""
    return str(uuid.uuid4())
