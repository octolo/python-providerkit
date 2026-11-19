"""Install the two built wheels together, outside the checkout."""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import venv
import zipfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def _collect_wheels(arguments: list[str]) -> tuple[Path, Path]:
    wheels: list[Path] = []
    for argument in arguments:
        path = Path(argument)
        if path.is_dir():
            wheels.extend(sorted(path.glob("*.whl")))
        elif path.is_file() and path.suffix == ".whl":
            wheels.append(path)
        else:
            raise SystemExit(f"Not a wheel or directory: {path}")

    core = [wheel for wheel in wheels if wheel.name.startswith("providerkit-")]
    django = [wheel for wheel in wheels if wheel.name.startswith("django_providerkit-")]
    if len(core) != 1 or len(django) != 1:
        found = ", ".join(wheel.name for wheel in wheels) or "none"
        raise SystemExit(
            "Expected one providerkit wheel and one django_providerkit wheel, "
            f"found: {found}"
        )
    return core[0].resolve(), django[0].resolve()


def _wheel_version(wheel: Path) -> str:
    with zipfile.ZipFile(wheel) as archive:
        metadata_names = [
            name for name in archive.namelist() if name.endswith(".dist-info/METADATA")
        ]
        if len(metadata_names) != 1:
            raise SystemExit(f"{wheel.name} does not contain one METADATA file")
        metadata = archive.read(metadata_names[0]).decode()
    for line in metadata.splitlines():
        if line.startswith("Version:"):
            return line.split(":", 1)[1].strip()
    raise SystemExit(f"{wheel.name} METADATA has no Version")


def _clean_environment(work: Path) -> dict[str, str]:
    environment = os.environ.copy()
    environment.pop("PYTHONPATH", None)
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    environment["VIRTUAL_ENV"] = str(work)
    return environment


def _run(command: list[str], work: Path, environment: dict[str, str]) -> str:
    completed = subprocess.run(
        command,
        cwd=work,
        env=environment,
        check=False,
        text=True,
        capture_output=True,
    )
    if completed.returncode != 0:
        raise SystemExit(
            f"Command failed ({completed.returncode}): {' '.join(command)}\n"
            f"{completed.stdout}\n{completed.stderr}"
        )
    return completed.stdout


def install_wheels(core_wheel: Path, django_wheel: Path) -> None:
    core_version = _wheel_version(core_wheel)
    django_version = _wheel_version(django_wheel)
    with tempfile.TemporaryDirectory(prefix="providerkit-install-") as temporary:
        work = Path(temporary).resolve()
        if REPO_ROOT == work or REPO_ROOT in work.parents:
            raise SystemExit(f"Install directory is inside the checkout: {work}")
        venv.create(work, with_pip=True)
        python = work / "bin" / "python"
        environment = _clean_environment(work)
        _run(
            [
                str(python),
                "-m",
                "pip",
                "install",
                "--disable-pip-version-check",
                str(core_wheel),
                str(django_wheel),
            ],
            work,
            environment,
        )
        _run([str(python), "-m", "pip", "check"], work, environment)
        version_output = _run(
            [str(work / "bin" / "providerkit"), "version"],
            work,
            environment,
        )
        expected_line = f"providerkit version {core_version}"
        if expected_line not in version_output.splitlines():
            raise SystemExit(
                f"providerkit version returned {version_output!r}, "
                f"expected {expected_line!r}"
            )
        print(expected_line)
        startup = _run(
            [
                str(python),
                str(REPO_ROOT / "scripts" / "check_django_install.py"),
                str(REPO_ROOT),
                core_version,
                django_version,
            ],
            work,
            environment,
        )
        print(startup, end="" if startup.endswith("\n") else "\n")
        print(f"Installed {core_wheel.name} and {django_wheel.name} in {work}")


def main(argv: list[str] | None = None) -> int:
    arguments = list(sys.argv[1:] if argv is None else argv)
    if not arguments:
        raise SystemExit("Usage: install_built_wheels.py WHEEL_OR_DIST_DIR [...]")
    core_wheel, django_wheel = _collect_wheels(arguments)
    install_wheels(core_wheel, django_wheel)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
