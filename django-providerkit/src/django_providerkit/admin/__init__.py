from django.conf import settings
from django.contrib import admin
from django.http import HttpRequest, HttpResponseBase
from django.shortcuts import redirect
from providerkit.providers.base import ProviderListBase

from django_providerkit import models
from django_providerkit.models import ProviderkitModel, ProviderServiceModel

from .provider import BaseProviderAdmin, ProviderkitAdmin
from .service import ProviderServiceAdmin


class ProviderServiceChangeAdmin(ProviderServiceAdmin):
    """Service change page. The list is a providers admin subview."""

    def has_module_permission(self, request: HttpRequest) -> bool:  # noqa: ARG002
        return False

    def changelist_view(  # type: ignore[override]
        self,
        request: HttpRequest,
        extra_context: dict | None = None,  # noqa: ARG002
    ) -> HttpResponseBase:
        return redirect("admin:django_providerkit_providerkitmodel_services_list")


if "django_providerkit" in settings.INSTALLED_APPS:
    admin.site.register(ProviderkitModel, ProviderkitAdmin)
    admin.site.register(ProviderServiceModel, ProviderServiceChangeAdmin)

__all__ = [
    "BaseProviderAdmin",
]
