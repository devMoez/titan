"""Regression tests for _apply_profile_override Titan_HOME guard (issue #22502).

When Titan_HOME is set to the Titan root (e.g. systemd hardcodes
Titan_HOME=/root/.Titan), _apply_profile_override must still read
active_profile and update Titan_HOME to the profile directory.

When Titan_HOME is already a profile directory (.../profiles/<name>),
_apply_profile_override must trust it and return without re-reading
active_profile (child-process inheritance contract).
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest


def _run_apply_profile_override(
    tmp_path, monkeypatch, *, Titan_home: str | None, active_profile: str | None,
    argv: list[str] | None = None,
):
    """Run _apply_profile_override in isolation.

    Returns the value of os.environ["Titan_HOME"] after the call,
    or None if unset.
    """
    Titan_root = tmp_path / ".Titan"
    Titan_root.mkdir(parents=True, exist_ok=True)

    if active_profile is not None:
        (Titan_root / "active_profile").write_text(active_profile)

    if active_profile and active_profile != "default":
        (Titan_root / "profiles" / active_profile).mkdir(parents=True, exist_ok=True)

    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    if Titan_home is not None:
        monkeypatch.setenv("Titan_HOME", Titan_home)
    else:
        monkeypatch.delenv("Titan_HOME", raising=False)

    monkeypatch.setattr(sys, "argv", argv or ["Titan", "gateway", "start"])

    from Titan_cli.main import _apply_profile_override
    _apply_profile_override()

    return os.environ.get("Titan_HOME")


class TestApplyProfileOverrideTitanHomeGuard:
    """Regression guard for issue #22502.

    Verifies that Titan_HOME pointing to the Titan root does NOT suppress
    the active_profile check, while Titan_HOME already pointing to a
    profile directory IS trusted as-is.
    """

    def test_Titan_home_at_root_with_active_profile_is_redirected(
        self, tmp_path, monkeypatch
    ):
        """Titan_HOME=/root/.Titan + active_profile=coder must redirect
        Titan_HOME to .../profiles/coder.

        Bug scenario from #22502: systemd sets Titan_HOME to the Titan root
        and the user switches to a profile via `Titan profile use`.
        Before the fix, the guard returned early and active_profile was ignored.
        """
        Titan_root = tmp_path / ".Titan"
        Titan_root.mkdir(parents=True, exist_ok=True)

        result = _run_apply_profile_override(
            tmp_path,
            monkeypatch,
            Titan_home=str(Titan_root),
            active_profile="coder",
        )

        assert result is not None, "Titan_HOME must be set after profile redirect"
        assert "profiles" in result, (
            f"Expected Titan_HOME to point into profiles/ dir, got: {result!r}"
        )
        assert result.endswith("coder"), (
            f"Expected Titan_HOME to end with 'coder', got: {result!r}"
        )

    def test_Titan_home_already_profile_dir_is_trusted(self, tmp_path, monkeypatch):
        """Titan_HOME=.../profiles/coder must not be overridden even when
        active_profile says something different.

        Preserves the child-process inheritance contract: a subprocess spawned
        with Titan_HOME already set to a specific profile must stay in that
        profile.
        """
        Titan_root = tmp_path / ".Titan"
        profile_dir = Titan_root / "profiles" / "coder"
        profile_dir.mkdir(parents=True, exist_ok=True)

        (Titan_root / "active_profile").write_text("other")

        monkeypatch.setattr(Path, "home", lambda: tmp_path)
        monkeypatch.setenv("Titan_HOME", str(profile_dir))
        monkeypatch.setattr(sys, "argv", ["Titan", "gateway", "start"])

        from Titan_cli.main import _apply_profile_override
        _apply_profile_override()

        assert os.environ.get("Titan_HOME") == str(profile_dir), (
            "Titan_HOME must remain unchanged when already pointing to a profile dir"
        )

    def test_Titan_home_unset_reads_active_profile(self, tmp_path, monkeypatch):
        """Classic case: Titan_HOME unset + active_profile=coder must set
        Titan_HOME to the profile directory (existing behaviour must not regress).
        """
        result = _run_apply_profile_override(
            tmp_path,
            monkeypatch,
            Titan_home=None,
            active_profile="coder",
        )

        assert result is not None
        assert "coder" in result

    def test_Titan_home_unset_default_profile_no_redirect(self, tmp_path, monkeypatch):
        """active_profile=default must not redirect Titan_HOME."""
        Titan_root = tmp_path / ".Titan"
        Titan_root.mkdir(parents=True, exist_ok=True)

        monkeypatch.setattr(Path, "home", lambda: tmp_path)
        monkeypatch.delenv("Titan_HOME", raising=False)
        monkeypatch.setattr(sys, "argv", ["Titan", "gateway", "start"])
        (Titan_root / "active_profile").write_text("default")

        from Titan_cli.main import _apply_profile_override
        _apply_profile_override()

        assert os.environ.get("Titan_HOME") is None

