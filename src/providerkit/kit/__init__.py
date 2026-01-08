"""Base classes for provider management."""

from __future__ import annotations

import sys
from typing import Any

from .config import ConfigMixin
from .cost import CostMixin
from .package import PackageMixin
from .response import ResponseMixin
from .service import ServiceMixin
from .urls import UrlsMixin

FIELDS_PROVIDER_BASE = {
    'name': {'label': 'Name', 'description': 'Provider name', 'format': 'str'},
    'display_name': {
        'label': 'Display Name',
        'description': 'Provider display name',
        'format': 'str',
    },
    'description': {'label': 'Description', 'description': 'Provider description', 'format': 'str'},
}


class ProviderBase(PackageMixin, UrlsMixin, ConfigMixin, ServiceMixin, CostMixin, ResponseMixin):
    """Base class for providers with basic identification information."""

    name: str
    display_name: str
    description: str | None
    mandatory_base_fields: list[str] = ['name', 'display_name']
    path: str | None = None
    abstract: bool = False
    priority: int = 0  # 0 - highest, 5 - lowest

    def __init_subclass__(cls, **kwargs):
        """Automatically import required packages when subclass is defined."""
        super().__init_subclass__(**kwargs)
        if hasattr(cls, 'required_packages') and cls.required_packages:
            frame = sys._getframe(1)
            module_globals = frame.f_globals
            PackageMixin.safe_import_packages(cls.required_packages, module_globals)

    def __init__(self, **kwargs: str | None) -> None:
        """Initialize a provider with required identification."""
        for field in self.mandatory_base_fields:
            setattr(self, field, kwargs.pop(field, getattr(self, field)))
            if not getattr(self, field):
                raise ValueError(f'{field} is required and cannot be empty')

        config = kwargs.pop('config', None)
        if config is not None:
            if isinstance(config, dict):
                self._init_config(config)
            else:
                self._init_config(None)

        for field, value in kwargs.items():
            setattr(self, field, value)

        self._service_results_cache: dict[str, dict[str, Any]] = {}

    def _get_nested_value(
        self, data: dict[str, Any], path: str | list[str] | tuple[str, ...], default: Any = None
    ) -> Any:
        if isinstance(path, (list, tuple)):
            for p in path:
                value = self._get_nested_value(data, p, None)
                if value is not None:
                    return value
            return default

        if not path:
            return default
        keys = path.split('.')
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

    def _normalize_recursive(
        self,
        data: dict[str, Any] | Any,
        field: str,
        source: str | list[str] | tuple[str, ...] | None,
    ) -> Any:
        if source is None:
            return None
        if isinstance(source, (tuple, list)):
            for path in source:
                value = self._normalize_recursive(data, field, path)
                if value is not None:
                    return value
            return None
        if callable(source):
            return source(data)
        if isinstance(source, str):
            if '.' in source:
                parts = source.split('.')
                current = data
                for part in parts:
                    if isinstance(current, dict):
                        current = current.get(part)
                    else:
                        current = getattr(current, part, None)
                    if current is None:
                        return None
                return current() if callable(current) else current
            if isinstance(data, dict):
                return data.get(source)
            value = getattr(data, source, None)
            if callable(value):
                return value()
            return value
        return source

    def normalize(
        self, data: dict[str, Any], config: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        if config is None:
            config = getattr(self, 'config', {})
        fields = config.get('fields', {})
        normalized: dict[str, Any] = {}
        for field, cfg in fields.items():
            normalize_method = getattr(self, f'get_normalize_{field}', None)
            if normalize_method and callable(normalize_method):
                value = normalize_method(data)
            else:
                value = self._normalize_recursive(data, field, cfg.get('source', field))
            label = cfg.get('label', field)
            normalized[label] = value
        return normalized
