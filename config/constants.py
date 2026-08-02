"""
Immutable platform constants, artifact types, and status enumerations for KuroAI.
"""

from typing import Final

PLATFORM_NAME: Final[str] = "KuroAI"
PLATFORM_VERSION: Final[str] = "1.0.0-rc1"

# Contract Versioning
CONTRACT_VERSION: Final[str] = "v1"

# Event Channel Topics
EVENT_CHANNEL_ARTIFACTS: Final[str] = "channel.artifacts"
EVENT_CHANNEL_TASKS: Final[str] = "channel.tasks"
EVENT_CHANNEL_AGENTS: Final[str] = "channel.agents"
EVENT_CHANNEL_SYSTEM: Final[str] = "channel.system"
