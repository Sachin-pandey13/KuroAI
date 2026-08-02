"""
KuroAI version and build information metadata.
"""

import os
import platform
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime

__version__ = "1.0.0-rc3"


@dataclass(frozen=True)
class BuildInfo:
    """Immutable metadata snapshot describing the KuroAI build state."""

    version: str
    commit: str
    branch: str
    build_date: str
    python_version: str
    platform: str

    def to_dict(self) -> dict:
        return {
            "version": self.version,
            "commit": self.commit,
            "branch": self.branch,
            "build_date": self.build_date,
            "python_version": self.python_version,
            "platform": self.platform,
        }


def _get_git_commit() -> str:
    try:
        out = subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"], stderr=subprocess.DEVNULL
        )
        return out.decode("utf-8").strip()
    except Exception:
        return "unknown"


def _get_git_branch() -> str:
    try:
        out = subprocess.check_output(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"], stderr=subprocess.DEVNULL
        )
        return out.decode("utf-8").strip()
    except Exception:
        return "unknown"


def get_build_info() -> BuildInfo:
    """Construct and return current BuildInfo metadata."""
    return BuildInfo(
        version=__version__,
        commit=_get_git_commit(),
        branch=_get_git_branch(),
        build_date=os.getenv("BUILD_DATE", datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")),
        python_version=sys.version.split()[0],
        platform=platform.platform(),
    )
