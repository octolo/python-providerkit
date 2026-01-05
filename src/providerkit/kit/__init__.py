"""Base classes for provider management."""

from __future__ import annotations

import sys
from types import ModuleType
from typing import Any

from .config import ConfigMixin
from .cost import CostMixin
from .package import PackageMixin
from .service import ServiceMixin
from .urls import UrlsMixin


class ProviderBase(PackageMixin, UrlsMixin, ConfigMixin, ServiceMixin, CostMixin):
    """Base class for providers with basic identification information."""

    name: str
    display_name: str
    description: str | None
    mandatory_base_fields: list[str] = ["name", "display_name"]
    path: str | None = None
    provider_can_be_used: bool = True
    priority: int = 0 # 0 - highest, 5 - lowest

    def __init_subclass__(cls, **kwargs):
        """Automatically import required packages when subclass is defined."""
        super().__init_subclass__(**kwargs)
        if hasattr(cls, "required_packages") and cls.required_packages:
            frame = sys._getframe(1)
            module_globals = frame.f_globals
            PackageMixin.safe_import_packages(cls.required_packages, module_globals)

    def __init__(self, **kwargs: str | None) -> None:
        """Initialize a provider with required identification.

        Args:
            **kwargs: Provider attributes:
                - name: Unique identifier for the provider (required).
                - display_name: Human-readable name for the provider (defaults to name if not provided).
                - description: Optional description of the provider.

        Raises:
            ValueError: If name or display_name is empty or not provided.
        """
        for field in self.mandatory_base_fields:
            setattr(self, field, kwargs.pop(field, getattr(self, field)))
            if not getattr(self, field):
                raise ValueError(f"{field} is required and cannot be empty")

        config = kwargs.pop("config", None)
        if config is not None:
            if isinstance(config, dict):
                self._init_config(config)
            else:
                self._init_config(None)

        for field, value in kwargs.items():
            setattr(self, field, value)

    def _get_nested_value(self, data: dict[str, Any], path: str | list[str] | tuple[str, ...], default: Any = None) -> Any:
        if isinstance(path, (list, tuple)):
            for p in path:
                value = self._get_nested_value(data, p, None)
                if value is not None:
                    return value
            return default

        if not path:
            return default
        keys = path.split(".")
        val: Any = data
        for k in keys:
            if isinstance(val, dict):
                val = val.get(k)
            elif isinstance(val, list):
                try:
                    index = int(k)
                    if 0 <= index < len(val):
                        val = val[index]
                    else:
                        return default
                except (ValueError, TypeError):
                    return default
            else:
                return default
            if val is None:
                return default
        return val

    def _normalize_recursive(self, data: dict[str, Any], field: str, source: str | list[str] | tuple[str, ...] | None) -> Any:
        if source is None:
            return None
        if isinstance(source, (tuple, list)):
            for path in source:
                value = self._normalize_recursive(data, field, path)
                if value is not None:
                    return value
            return None
        if isinstance(source, str):
            if "." in source:
                return self._get_nested_value(data, source)
            return data.get(source)
        return source

    def normalize(self, fields: list[str], data: dict[str, Any], fields_associations: dict[str, str | list[str] | tuple[str, ...] | None] | None = None) -> dict[str, Any]:
        if fields_associations is None:
            fields_associations = getattr(self, "fields_associations", {})
        normalized: dict[str, Any] = {}
        for field in fields:
            normalize_method = getattr(self, f"get_normalize_{field}", None)
            if normalize_method and callable(normalize_method):
                value = normalize_method(data)
            else:
                source = fields_associations.get(field)
                value = self._normalize_recursive(data, field, source)
            if value is not None:
                normalized[field] = value
        return normalized

