"""The release tag has to be the PEP 440 version of both packages."""

from __future__ import annotations

import importlib.util
import subprocess
import sys
import tomllib
from pathlib import Path

import pytest
from packaging.version import Version

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "check_release_tag.py"


def _checker():
    spec = importlib.util.spec_from_file_location("check_release_tag", SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


CHECKER = _checker()


def _write_project(path: Path, version: str) -> Path:
    path.write_text(
        f'[project]\nname = "example"\nversion = "{version}"\n',
        encoding="utf-8",
    )
    return path


def test_stable_tag_matches_both_package_versions(tmp_path: Path) -> None:
    core = _write_project(tmp_path / "core.toml", "1.1.2")
    django = _write_project(tmp_path / "django.toml", "1.1.2")

    assert CHECKER.check_tag("v1.1.2", core, django) == Version("1.1.2")


def test_rc_tag_matches_equivalent_pep440_spellings(tmp_path: Path) -> None:
    core = _write_project(tmp_path / "core.toml", "1.1.2c1")
    django = _write_project(tmp_path / "django.toml", "1.1.2rc1")

    assert CHECKER.check_tag("v1.1.2rc1", core, django) == Version("1.1.2rc1")


def test_inconsistent_tag_is_rejected(tmp_path: Path) -> None:
    core = _write_project(tmp_path / "core.toml", "1.1.2")
    django = _write_project(tmp_path / "django.toml", "1.1.2")

    with pytest.raises(SystemExit, match="does not match"):
        CHECKER.check_tag("v1.1.3", core, django)

    other = _write_project(tmp_path / "django-other.toml", "1.1.3")
    with pytest.raises(SystemExit, match="does not match"):
        CHECKER.check_tag("v1.1.2", core, other)


def test_repository_tag_command_accepts_the_shared_version() -> None:
    core_version = tomllib.loads(
        (ROOT / "python-providerkit" / "pyproject.toml").read_text(encoding="utf-8")
    )["project"]["version"]
    django_version = tomllib.loads(
        (ROOT / "django-providerkit" / "pyproject.toml").read_text(encoding="utf-8")
    )["project"]["version"]
    assert core_version == django_version

    accepted = subprocess.run(
        [sys.executable, str(SCRIPT), f"v{core_version}"],
        cwd=ROOT,
        check=False,
        text=True,
        capture_output=True,
    )
    rejected = subprocess.run(
        [sys.executable, str(SCRIPT), f"v{core_version}rc1"],
        cwd=ROOT,
        check=False,
        text=True,
        capture_output=True,
    )

    assert accepted.returncode == 0, accepted.stderr
    assert rejected.returncode != 0
    assert "does not match" in rejected.stderr + rejected.stdout
