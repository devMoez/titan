from pathlib import Path
from unittest.mock import patch


def test_ensure_dependency_skips_when_present():
    """ensure_dependency is a no-op when the dep is already available."""
    from Titan_cli.dep_ensure import ensure_dependency
    with patch("Titan_cli.dep_ensure.shutil") as mock_shutil:
        mock_shutil.which.return_value = "/usr/bin/node"
        result = ensure_dependency("node", interactive=False)
        assert result is True


def test_ensure_dependency_returns_false_when_missing_noninteractive():
    """ensure_dependency returns False for missing dep in non-interactive mode."""
    from Titan_cli.dep_ensure import ensure_dependency
    with patch("Titan_cli.dep_ensure.shutil") as mock_shutil:
        mock_shutil.which.return_value = None
        with patch("Titan_cli.dep_ensure._find_install_script", return_value=None):
            result = ensure_dependency("node", interactive=False)
            assert result is False


def test_find_install_script_from_checkout(tmp_path):
    """_find_install_script finds scripts/install.sh in a git checkout."""
    from Titan_cli.dep_ensure import _find_install_script
    scripts_dir = tmp_path / "scripts"
    scripts_dir.mkdir()
    (scripts_dir / "install.sh").write_text("#!/bin/bash", encoding="utf-8")
    result = _find_install_script(package_dir=tmp_path / "Titan_cli", repo_root=tmp_path)
    assert result is not None
    assert result.name == "install.sh"


def test_find_install_script_from_wheel(tmp_path):
    """_find_install_script finds bundled install.sh in a wheel."""
    from Titan_cli.dep_ensure import _find_install_script
    bundled = tmp_path / "Titan_cli" / "scripts"
    bundled.mkdir(parents=True)
    (bundled / "install.sh").write_text("#!/bin/bash", encoding="utf-8")
    result = _find_install_script(package_dir=tmp_path / "Titan_cli", repo_root=tmp_path)
    assert result is not None
    assert result.name == "install.sh"

