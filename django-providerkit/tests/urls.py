"""URL configuration for testing django-providerkit."""

import django
import providerkit
from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

import django_providerkit

urlpatterns = [
    path("", RedirectView.as_view(url="/admin/", permanent=False)),
    path("admin/", admin.site.urls),
    path("django_providerkit/", include("django_providerkit.urls")),
]

_version = f"(Django {django.get_version()}, ProviderKit {providerkit.__version__}/{django_providerkit.__version__})"
admin.site.site_header = f"Django ProviderKit - Administration {_version}"
admin.site.site_title = f"Django ProviderKit Admin {_version}"
admin.site.index_title = f"Welcome to Django ProviderKit {_version}"
