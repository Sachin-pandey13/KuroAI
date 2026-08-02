"""
Prompt Safety Validation, Path Traversal Defense, and Input Sanitization.
"""

import os
import re
from typing import Tuple, Optional


class InputValidationError(Exception):
    """Raised when user input violates prompt safety or validation rules."""
    pass


class PromptSafetyValidator:
    """
    Validates user prompts for safety, size limits, allowed content policy, and unsafe tokens.
    """

    DEFAULT_MAX_PROMPT_CHARS = 50_000
    UNSAFE_PATTERNS = [
        re.compile(r"ignore\s+all\s+previous\s+instructions", re.IGNORECASE),
        re.compile(r"system\s*:\s*you\s+are", re.IGNORECASE),
        re.compile(r"<script.*?>.*?</script>", re.IGNORECASE),
    ]

    def __init__(self, max_chars: int = DEFAULT_MAX_PROMPT_CHARS) -> None:
        self.max_chars = max_chars

    def validate_prompt(self, prompt: str) -> Tuple[bool, Optional[str]]:
        """
        Validate prompt text against length restrictions and unsafe patterns.
        Returns (is_valid, error_reason).
        """
        if not prompt or not prompt.strip():
            return False, "Prompt cannot be empty"

        if len(prompt) > self.max_chars:
            return False, f"Prompt exceeds maximum character length of {self.max_chars}"

        for pattern in self.UNSAFE_PATTERNS:
            if pattern.search(prompt):
                return False, f"Prompt contains forbidden unsafe pattern: {pattern.pattern}"

        return True, None


def sanitize_filename(filename: str) -> str:
    """Sanitize input filename preventing directory traversal attacks."""
    if ".." in filename or "/" in filename or "\\" in filename:
        raise InputValidationError(f"Path traversal detected in filename: {filename}")
    clean = os.path.basename(filename)
    clean = re.sub(r"[^\w\.-]", "_", clean)
    if not clean or clean.startswith("."):
        raise InputValidationError(f"Invalid or unsafe filename: {filename}")
    return clean


def assert_safe_path(base_dir: str, target_path: str) -> str:
    """Assert target_path remains strictly inside base_dir boundary."""
    abs_base = os.path.abspath(base_dir)
    abs_target = os.path.abspath(target_path)
    if not abs_target.startswith(abs_base):
        raise InputValidationError(f"Path traversal detected: {target_path} is outside {base_dir}")
    return abs_target
