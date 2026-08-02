"""
KuroAI Backend package root.
"""

from backend.version import BuildInfo, __version__, get_build_info

__all__ = ["__version__", "BuildInfo", "get_build_info"]
