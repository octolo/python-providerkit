from typing import Any

from providerkit.kit import ProviderBase


class ProviderListSort:
    """Sort providers."""

    def _get_sort_key(
        self, provider: ProviderBase, order_by: list[str] | None = None
    ) -> tuple[tuple[int, Any], ...]:
        """Get sort key for a provider."""
        if order_by is None:
            order_by = ['name', 'priority']
        key_parts: list[tuple[int, Any]] = []
        for attr_name in order_by:
            attr_value = getattr(provider, attr_name, None)
            if callable(attr_value):
                try:
                    attr_value = attr_value()
                except Exception:
                    attr_value = None
            if attr_value is None:
                key_parts.append((1, None))
            else:
                key_parts.append((0, attr_value))
        return tuple(key_parts)

    def sort_providers(
        self, providers: list[ProviderBase], order_by: list[str] | None = None
    ) -> list[ProviderBase]:
        """Sort providers."""
        return sorted(providers, key=lambda p: self._get_sort_key(p, order_by))
