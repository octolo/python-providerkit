from django.conf import settings
from django.contrib import admin
from providerkit.providers.base import ProviderListBase
from clicommands.utils import snake_to_camel

from django_providerkit import models
from django_providerkit.models import ProviderkitModel, ProviderServiceModel

from .provider import BaseProviderAdmin
from .service import ProviderServiceAdmin

services_admins = []
if "django_providerkit" in settings.INSTALLED_APPS:
    admin.site.register(ProviderkitModel, BaseProviderAdmin)
    admin.site.register(ProviderServiceModel, ProviderServiceAdmin)

__all__ = ['BaseProviderAdmin', ]
