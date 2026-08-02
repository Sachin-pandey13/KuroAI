"""
Environment Secret Manager & Validator.
"""

import os
from typing import Dict, Optional


class SecretManager:
    """Manages secure resolution and validation of environment secrets."""

    def __init__(self, env: Optional[Dict[str, str]] = None) -> None:
        self._env = env if env is not None else os.environ

    def get_secret(self, name: str, default: Optional[str] = None) -> Optional[str]:
        """Retrieve a secret by environment variable name."""
        return self._env.get(name, default)

    def validate_required_secrets(self, required_names: list[str]) -> bool:
        """Validate that all required secrets are set and non-empty."""
        missing = [name for name in required_names if not self._env.get(name)]
        if missing:
            raise ValueError(f"Missing required environment secrets: {', '.join(missing)}")
        return True
