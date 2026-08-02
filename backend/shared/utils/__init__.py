"""
Shared utility functions for KuroAI.
"""

from backend.shared.utils.id_generator import generate_uuid
from backend.shared.utils.time_utils import utc_now, utc_now_iso
from backend.shared.utils.token_counter import estimate_tokens
from backend.shared.utils.error_helpers import normalize_error
from backend.shared.utils.text_utils import strip_markdown

__all__ = [
    "generate_uuid",
    "utc_now",
    "utc_now_iso",
    "estimate_tokens",
    "normalize_error",
    "strip_markdown",
]
