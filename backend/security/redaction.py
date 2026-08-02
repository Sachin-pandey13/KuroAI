"""
Secret & Credential Redaction Filter.
"""

import re
from typing import List, Pattern


class SecretRedactor:
    """
    Scrubs sensitive patterns (API keys, bearer tokens, passwords) from text and dictionary payloads.
    """

    PATTERNS: List[Pattern] = [
        re.compile(r"ghp_[A-Za-z0-9_]{36}"),                # GitHub PAT
        re.compile(r"sk-[A-Za-z0-9_-]{32,}"),                # OpenAI API Key
        re.compile(r"Bearer\s+[A-Za-z0-9\._-]{20,}", re.I),  # JWT Bearer Token
        re.compile(r"password\s*=\s*['\"][^'\"]+['\"]", re.I),
    ]

    REDACTION_STUB = "[REDACTED_SECRET]"

    @classmethod
    def redact_text(cls, text: str) -> str:
        """Replace all secret matches in a string with a redaction stub."""
        if not text:
            return text
        result = text
        for pattern in cls.PATTERNS:
            result = pattern.sub(cls.REDACTION_STUB, result)
        return result

    @classmethod
    def redact_dict(cls, data: dict) -> dict:
        """Recursively redact string values inside a dictionary."""
        redacted = {}
        for k, v in data.items():
            if isinstance(v, str):
                redacted[k] = cls.redact_text(v)
            elif isinstance(v, dict):
                redacted[k] = cls.redact_dict(v)
            elif isinstance(v, list):
                redacted[k] = [cls.redact_text(item) if isinstance(item, str) else item for item in v]
            else:
                redacted[k] = v
        return redacted
