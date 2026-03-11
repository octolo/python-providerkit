"""Django ProviderKit application configuration."""

from __future__ import annotations

from typing import Any

from django.apps import AppConfig


def _django_settings_resolver(provider_name: str, key: str) -> Any:
    """Resolve provider config values from Django settings.

    Looks up PROVIDERKIT_PROVIDERS_CONFIG[provider_name][key] in settings.
    """
    from django.conf import settings

    config = getattr(settings, 'PROVIDERKIT_PROVIDERS_CONFIG', None)
    if config is None:
        return None
    return config.get(provider_name, {}).get(key)


class DjangoProviderkitConfig(AppConfig):
    name = 'django_providerkit'
    default_auto_field = 'django.db.models.BigAutoField'
    verbose_name = 'Django ProviderKit'

    def ready(self) -> None:
        from providerkit.kit.config import ConfigMixin

        ConfigMixin.register_config_resolver(_django_settings_resolver)
