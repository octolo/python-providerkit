"""Require the MIT license file inside each wheel and source archive."""

from __future__ import annotations

import sys
import tarfile
import zipfile
from pathlib import Path


def _assert_license(label: str, names: list[str], read) -> None:
    matches = [name for name in names if Path(name).name == "LICENSE"]
    if not matches:
        raise SystemExit(f"{label} does not contain a LICENSE file")
    for name in matches:
        text = read(name)
        if b"MIT License" not in text or b"Copyright (c) 2025 Octolo" not in text:
            raise SystemExit(f"{label} LICENSE at {name} has unexpected content")
    print(f"{label}: {', '.join(matches)}")


def check_directory(dist: Path) -> None:
    wheels = list(dist.glob("*.whl"))
    sdists = list(dist.glob("*.tar.gz"))
    if not wheels or not sdists:
        raise SystemExit(f"Expected a wheel and a source archive in {dist}")

    for wheel in wheels:
        with zipfile.ZipFile(wheel) as archive:
            _assert_license(wheel.name, archive.namelist(), archive.read)
    for sdist in sdists:
        with tarfile.open(sdist) as archive:

            def read(name: str, archive: tarfile.TarFile = archive) -> bytes:
                member = archive.extractfile(name)
                if member is None:
                    raise SystemExit(f"Cannot read {name} from {sdist.name}")
                return member.read()

            _assert_license(sdist.name, archive.getnames(), read)


def main(argv: list[str] | None = None) -> int:
    arguments = list(sys.argv[1:] if argv is None else argv)
    if len(arguments) != 1:
        raise SystemExit("Usage: check_distribution_license.py DIST_DIR")
    check_directory(Path(arguments[0]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
