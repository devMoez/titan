"""Resolve Titan_HOME for standalone skill scripts.

Skill scripts may run outside the Titan process (e.g. system Python,
nix env, CI) where ``Titan_constants`` is not importable.  This module
provides the same ``get_Titan_home()`` and ``display_Titan_home()``
contracts as ``Titan_constants`` without requiring it on ``sys.path``.

When ``Titan_constants`` IS available it is used directly so that any
future enhancements (profile resolution, Docker detection, etc.) are
picked up automatically.  The fallback path replicates the core logic
from ``Titan_constants.py`` using only the stdlib.

All scripts under ``google-workspace/scripts/`` should import from here
instead of duplicating the ``Titan_HOME = Path(os.getenv(...))`` pattern.
"""

from __future__ import annotations

import os
from pathlib import Path

try:
    from Titan_constants import display_Titan_home as display_Titan_home
    from Titan_constants import get_Titan_home as get_Titan_home
except (ModuleNotFoundError, ImportError):

    def get_Titan_home() -> Path:
        """Return the Titan home directory (default: ~/.Titan).

        Mirrors ``Titan_constants.get_Titan_home()``."""
        val = os.environ.get("Titan_HOME", "").strip()
        return Path(val) if val else Path.home() / ".Titan"

    def display_Titan_home() -> str:
        """Return a user-friendly ``~/``-shortened display string.

        Mirrors ``Titan_constants.display_Titan_home()``."""
        home = get_Titan_home()
        try:
            return "~/" + str(home.relative_to(Path.home()))
        except ValueError:
            return str(home)

