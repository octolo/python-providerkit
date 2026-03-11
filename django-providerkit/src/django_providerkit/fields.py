"""Custom fields for django-providerkit."""

from django.db import models
from django.forms import Select
from django.utils.translation import gettext_lazy as _

from providerkit.helpers import get_providerkit


class ProviderValue:
    """Wrapper around provider name string that adds _provider attribute."""

    def __init__(self, value: str, package_name: str | None):
        self._value = value
        self._package_name = package_name
        self._provider_instance = None

    def __str__(self) -> str:
        return str(self._value)

    def __repr__(self) -> str:
        return repr(self._value)

    def __eq__(self, other) -> bool:
        if isinstance(other, ProviderValue):
            return self._value == other._value
        return self._value == other

    def __hash__(self) -> int:
        return hash(self._value)

    @property
    def _provider(self):
        """Get the provider instance."""
        if self._provider_instance is None:
            try:
                pvk = get_providerkit()
                providers = pvk.get_providers(lib_name=self._package_name)
                if isinstance(providers, dict):
                    providers = providers.values()
                for provider in providers:
                    if self._value in [provider.name, provider.display_name]:
                        self._provider_instance = provider
                        break
            except Exception:
                pass
        return self._provider_instance

    def call_service(self, service_name: str, **kwargs):
        """Call a service on the provider."""
        return self._provider.call_service_formatted(service_name, **kwargs)


class ProviderDescriptor:
    """Descriptor that wraps field value with ProviderValue."""

    def __init__(self, field, package_name: str | None):
        self.field = field
        self.package_name = package_name

    def __get__(self, instance, owner=None):
        if instance is None:
            return self
        value = instance.__dict__.get(self.field.attname, None)
        if not value:
            return value
        return ProviderValue(value, self.package_name)

    def __set__(self, instance, value):
        if hasattr(value, '_value'):
            value = value._value
        instance.__dict__[self.field.attname] = value


class ProviderField(models.CharField):
    """
    CharField storing a provider name, with dynamic choices
    loaded from providerkit at form rendering time.
    """

    def __init__(self, package_name: str | None = None, *args, **kwargs):
        self.package_name = package_name

        kwargs.setdefault("max_length", 100)
        kwargs.setdefault("blank", True)
        kwargs.setdefault("verbose_name", _("Provider"))
        kwargs.setdefault("help_text", _("Select a provider"))

        super().__init__(*args, **kwargs)

    def contribute_to_class(self, cls, name, **kwargs):
        """Add custom descriptor to provide _provider access."""
        super().contribute_to_class(cls, name, **kwargs)
        setattr(cls, name, ProviderDescriptor(self, self.package_name))

    def formfield(self, **kwargs):
        """
        Return a form field with dynamically injected choices.
        """
        formfield = super().formfield(**kwargs)

        # Inject dynamic choices at form level (NOT field init)
        choices = self.get_provider_choices()
        formfield.choices = choices
        formfield.widget = Select(choices=choices)

        return formfield

    def get_provider_choices(self):
        """
        Return provider choices as (value, label) tuples.
        Always returns at least the empty choice.
        """
        choices = [("", _("---------"))]

        try:
            pvk = get_providerkit()
            providers = pvk.get_providers(lib_name=self.package_name)

            if isinstance(providers, dict):
                providers = providers.values()

            for provider in providers:
                display_name = getattr(provider, "display_name", None) or provider.name
                choices.append((provider.name, display_name))
        except Exception:
            pass

        return choices


