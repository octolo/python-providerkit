from __future__ import annotations

from typing import Any

from providerkit.kit import ProviderBase  # noqa: TC001
from providerkit.providers import (
    ProviderListConfig,
    ProviderListFolder,
    ProviderListJson,
    ProviderListPackage,
)

from .load import (
    load_providers_from_config,  # noqa: F401
    load_providers_from_dir,  # noqa: F401
    load_providers_from_json,  # noqa: F401
)


def get_providerkit(**kwargs: Any) -> ProviderListConfig | ProviderListFolder | ProviderListJson | ProviderListPackage:
    if kwargs.get('config'):
        return ProviderListConfig()
    if kwargs.get('dir_path'):
        return ProviderListFolder()
    if kwargs.get('json'):
        return ProviderListJson()
    # Check if JSON file exists for lib_name
    lib_name = kwargs.get('lib_name', 'providerkit')
    if lib_name != 'providerkit':
        from pathlib import Path
        json_paths = [
            Path(f'.{lib_name}.json'),
            Path(f'{lib_name}.json'),
            Path.home() / f'.{lib_name}.json',
            Path('tests') / f'{lib_name}.json',
            Path('tests') / f'.{lib_name}.json',
        ]
        for json_path in json_paths:
            if json_path.exists():
                return ProviderListJson()
    return ProviderListPackage()


def get_providers(**kwargs: Any) -> list[ProviderBase]:
    print("kwargs", kwargs)
    pvk = get_providerkit(**kwargs)
    lib_name = kwargs.pop('lib_name', 'providerkit')
    return pvk.get_providers(lib_name=lib_name, **kwargs)


def call_providers(**kwargs: Any) -> list[dict[str, Any]]:
    lib_name = kwargs.pop('lib_name', 'providerkit')
    command = kwargs.pop('command', 'get_providers')
    pvs = get_providers(lib_name=lib_name, **kwargs)
    results = []
    for provider in pvs:
        results.append(
            {
                'name': provider.name,
                'provider': provider,
                'result': provider.call_service(command, **kwargs),
            }
        )
    return results
