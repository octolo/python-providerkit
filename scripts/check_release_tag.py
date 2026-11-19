"""Compare a release tag with the version of both packages.

The leading ``v`` is removed, then both package versions must be the same PEP 440
version as the tag. ``1.1.2rc1`` and ``1.1.2c1`` therefore match.
"""

from __future__ import annotations

import argparse
import os
import tomllib
from pathlib import Path

from packaging.version import InvalidVersion, Version


def _parse_version(value: str, label: str) -> Version:
    try:
        return Version(value)
    except InvalidVersion as exc:
        raise SystemExit(f"{label} is not a PEP 440 version: {value}") from exc


def project_version(path: Path) -> Version:
    data = tomllib.loads(path.read_text(encoding="utf-8"))
    raw = str(data["project"]["version"])
    return _parse_version(raw, str(path))


def check_tag(tag: str, core_pyproject: Path, django_pyproject: Path) -> Version:
    expected = _parse_version(tag.removeprefix("v"), f"tag {tag}")
    core = project_version(core_pyproject)
    django = project_version(django_pyproject)
    if expected != core or expected != django:
        raise SystemExit(
            f"Tag {expected} does not match providerkit {core} "
            f"and django-providerkit {django}"
        )
    print(f"Tag {expected} matches providerkit and django-providerkit")
    return expected


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("tag", nargs="?")
    parser.add_argument(
        "--core-pyproject",
        type=Path,
        default=Path("python-providerkit/pyproject.toml"),
    )
    parser.add_argument(
        "--django-pyproject",
        type=Path,
        default=Path("django-providerkit/pyproject.toml"),
    )
    args = parser.parse_args(argv)
    tag = args.tag or os.environ.get("TAG_VERSION", "")
    if not tag:
        raise SystemExit("Pass a tag or set TAG_VERSION")
    check_tag(tag, args.core_pyproject, args.django_pyproject)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
