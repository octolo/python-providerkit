from providerkit.providers.base import ProviderListBase

from .provider import ProviderkitModel
from .service import ProviderServiceModel, ProviderServiceModelBase
from .define import create_service_provider_model

services_models = []
for svc, cfg in ProviderListBase.services_cfg.items():
    model = create_service_provider_model(svc, cfg['fields'], 'django_providerkit', 'name')
    services_models.append(model)
    globals()[str(model.__name__)] = model

__all__ = [
    'ProviderkitModel',
    'ProviderServiceModel',
    'ProviderServiceModelBase',
    *[str(model.__name__) for model in services_models]
]
