"""Start Django from the packages installed in this interpreter."""

from __future__ import annotations

import sys
from importlib.metadata import version
from pathlib import Path


def _require_installed(repo: Path, module, distribution: str) -> None:
    location = Path(module.__file__).resolve()
    if repo == location or repo in location.parents:
        raise SystemExit(
            f"{module.__name__} was imported from the checkout: {location}"
        )
    if "site-packages" not in location.parts:
        raise SystemExit(
            f"{module.__name__} is not installed in site-packages: {location}"
        )
    print(f"{distribution} {version(distribution)} from {location}")


def main(argv: list[str] | None = None) -> int:
    arguments = list(sys.argv[1:] if argv is None else argv)
    if len(arguments) != 3:
        raise SystemExit(
            "Usage: check_django_install.py REPO_ROOT CORE_VERSION DJANGO_VERSION"
        )
    repo = Path(arguments[0]).resolve()
    core_version, django_version = arguments[1], arguments[2]

    import django
    from django.conf import settings
    from django.core.management import call_command

    settings.configure(
        SECRET_KEY="release-install-check",
        USE_TZ=True,
        DEFAULT_AUTO_FIELD="django.db.models.BigAutoField",
        DATABASES={
            "default": {
                "ENGINE": "django.db.backends.sqlite3",
                "NAME": ":memory:",
            }
        },
        INSTALLED_APPS=[
            "django.contrib.contenttypes",
            "django.contrib.auth",
            "django_providerkit",
        ],
    )
    django.setup()

    import django_providerkit
    import providerkit

    _require_installed(repo, providerkit, "providerkit")
    _require_installed(repo, django_providerkit, "django-providerkit")
    if version("providerkit") != core_version:
        raise SystemExit(
            f"Installed providerkit {version('providerkit')} != wheel {core_version}"
        )
    if version("django-providerkit") != django_version:
        raise SystemExit(
            "Installed django-providerkit "
            f"{version('django-providerkit')} != wheel {django_version}"
        )
    call_command("check")
    print("Django check passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
