"""Django ProviderKit - Provider management for Django."""

from __future__ import annotations

from django.db import models

__version__ = "0.1.0"


fields_associations = {
    'int': models.IntegerField,
    'float': models.FloatField,
    'bool': models.BooleanField,
    'list': models.JSONField,
    'str': models.CharField,
    'text': models.TextField,
    'date': models.DateField,
    'time': models.TimeField,
    'datetime': models.DateTimeField,
    'email': models.EmailField,
    'url': models.URLField,
    'json': models.JSONField,
    'dict': models.JSONField,
}

from .fields import ProviderField

__all__ = ['ProviderField']
