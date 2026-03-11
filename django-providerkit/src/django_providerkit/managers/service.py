from virtualqueryset.managers import VirtualManager
from providerkit.helpers import get_providerkit
from typing import Any

class ProviderServiceManager(VirtualManager):
    """Base manager for provider service models."""

    package_name = 'providerkit'
    _services_by_name = {}  # Cache services by name

    def __init__(self, *args, **kwargs):
        self.package_name = kwargs.pop('package_name', 'providerkit')
        super().__init__(*args, **kwargs)

    def get_data(self) -> list[Any]:
        if not self.model:
            return []

        pvk = get_providerkit()
        provider = pvk.get_providers(lib_name=self.package_name)[0]
        return provider.get_services()
