"""
Generic text formatting utilities.
"""

import re


def strip_markdown(text: str) -> str:
    """Remove markdown formatting codeblocks from a raw string."""
    text = re.sub(r"```json\s*", "", text)
    text = re.sub(r"```\s*", "", text)
    return text.strip()
