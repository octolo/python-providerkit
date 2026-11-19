from __future__ import annotations

import importlib
import inspect
import json
import sys
from pathlib import Path
from typing import Any

from providerkit.kit import ProviderBase

from .module import (
    _build_module_path,
    _extract_providers_from_module,
    _infer_base_module,
    _load_module_from_file,
)


def _default_json_candidates(lib_name: str) -> list[Path]:
    return [
        Path(f".{lib_name}.json"),
        Path(f"{lib_name}.json"),
        Path.home() / f".{lib_name}.json",
        Path(f"tests/{lib_name}.json"),
        Path(f"tests/.{lib_name}.json"),
    ]


def _as_path(path: str | Path) -> Path:
    if isinstance(path, Path):
        return path
    return Path(path)


def _first_existing_json(
    lib_name: str, search_paths: list[str | Path] | None
) -> Path | None:
    if search_paths is None:
        candidates: list[str | Path] = _default_json_candidates(lib_name)
    else:
        candidates = [_as_path(path) for path in search_paths]
    for candidate in candidates:
        candidate_path = _as_path(candidate)
        if candidate_path.exists():
            return candidate_path
    return None


def _read_provider_config(json_file: str | Path) -> Any | None:
    try:
        with open(json_file, encoding="utf-8") as handle:
            return json.load(handle)
    except (json.JSONDecodeError, OSError):
        return None


def load_providers_from_json(
    json_path: str | Path | dict[str, Any] | None = None,
    *,
    lib_name: str = "providerkit",
    search_paths: list[str | Path] | None = None,
) -> dict[str, ProviderBase]:
    if isinstance(json_path, dict):
        return _load_providers_from_config(json_path.get("providers", []))

    json_file = json_path
    if json_file is None:
        json_file = _first_existing_json(lib_name, search_paths)
        if json_file is None:
            return {}

    config = _read_provider_config(json_file)
    if config is None:
        return {}
    providers = config.get("providers", []) if isinstance(config, dict) else config
    return _load_providers_from_config(providers)


def load_providers_from_config(config: list[dict[str, Any]]) -> dict[str, ProviderBase]:
    return _load_providers_from_config(config)


def _load_providers_from_config(
    config: list[dict[str, Any]],
) -> dict[str, ProviderBase]:
    providers: dict[str, ProviderBase] = {}

    for provider_config in config:
        class_path = provider_config.get("class", "")
        if not class_path:
            continue

        try:
            parts = class_path.split(".")
            module_path = ".".join(parts[:-1])
            class_name = parts[-1]
            module = importlib.import_module(module_path)  # nosec B307
            provider_class = getattr(module, class_name)

            if not issubclass(provider_class, ProviderBase):
                continue

            # Skip abstract providers
            if provider_class.__dict__.get("abstract", False):
                continue

            config_dict = provider_config.get("config", {})
            provider_instance = provider_class(
                config=config_dict, **provider_config.get("kwargs", {})
            )

            provider_name = getattr(provider_instance, "name", "").lower()
            if provider_name:
                providers[provider_name] = provider_instance
        except (ImportError, AttributeError, TypeError):
            continue

    return providers


def _prepare_base_module(dir_path_obj: Path, base_module: str | None) -> str | None:
    if base_module is not None:
        return base_module
    inferred = _infer_base_module(dir_path_obj)
    if not inferred:
        return None
    cwd = str(Path.cwd())
    if cwd not in sys.path:
        sys.path.insert(0, cwd)
    return inferred


def _load_provider_module(
    py_file: Path, dir_path_obj: Path, base_module: str | None
) -> tuple[Any, str] | None:
    if base_module:
        module_path = _build_module_path(py_file, dir_path_obj, base_module)
        return importlib.import_module(module_path), module_path  # nosec B307
    module = _load_module_from_file(py_file)
    if module is None:
        return None
    return module, module.__name__


def _providers_from_file(
    py_file: Path, dir_path_obj: Path, base_module: str | None
) -> dict[str, type[ProviderBase]]:
    try:
        loaded = _load_provider_module(py_file, dir_path_obj, base_module)
        if loaded is None:
            return {}
        module, module_path = loaded
        return _extract_providers_from_module(module, module_path)
    except (ImportError, AttributeError, TypeError, ValueError):
        return {}


def autodiscover_providers(
    dir_path: str | Path,
    *,
    base_module: str | None = None,
    exclude_files: list[str] | None = None,
) -> dict[str, type[ProviderBase]]:
    if exclude_files is None:
        exclude_files = ["__init__.py", "base.py"]

    dir_path_obj = Path(dir_path)
    if not dir_path_obj.exists() or not dir_path_obj.is_dir():
        return {}

    resolved_base = _prepare_base_module(dir_path_obj, base_module)
    providers: dict[str, type[ProviderBase]] = {}
    for py_file in dir_path_obj.rglob("*.py"):
        if py_file.name in exclude_files or py_file.name.startswith("_"):
            continue
        providers.update(_providers_from_file(py_file, dir_path_obj, resolved_base))
    return providers


def load_providers_from_dir(
    dir_path: str | Path,
    base_module: str | None = None,
) -> dict[str, ProviderBase]:
    dir_path_obj = Path(dir_path).resolve()
    if not dir_path_obj.exists():
        raise FileNotFoundError(f"Directory not found: {dir_path}")
    if not dir_path_obj.is_dir():
        raise NotADirectoryError(f"Path is not a directory: {dir_path}")

    provider_classes = autodiscover_providers(dir_path, base_module=base_module)
    providers: dict[str, ProviderBase] = {}
    for name, provider_class in provider_classes.items():
        try:
            provider_file = Path(inspect.getfile(provider_class)).resolve()
            relative_path = provider_file.relative_to(dir_path_obj)
            provider_instance = provider_class(path=str(relative_path))
            setattr(provider_instance, "class_name", provider_class.__name__)  # noqa: B010
            setattr(provider_instance, "class_path", provider_class.__module__)  # noqa: B010
            providers[name] = provider_instance
        except (TypeError, ValueError):
            continue
    return providers


def _find_package_providers_dir(lib_name: str) -> Path | None:
    try:
        package_module = importlib.import_module(lib_name)  # nosec B307
        if hasattr(package_module, "__file__") and package_module.__file__:
            package_dir = Path(package_module.__file__).parent
            providers_dir = package_dir / "providers"
            if providers_dir.exists() and providers_dir.is_dir():
                return providers_dir
    except (ImportError, AttributeError):
        pass
    return None


def load_providers_from_package(
    lib_name: str, base_module: str | None = None
) -> dict[str, ProviderBase]:
    providers_dir = _find_package_providers_dir(lib_name)
    if providers_dir:
        if base_module is None:
            base_module = f"{lib_name}.providers"
        return load_providers_from_dir(providers_dir, base_module)
    return {}
