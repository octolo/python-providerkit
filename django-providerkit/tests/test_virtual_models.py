"""Virtual model and provider field integration tests."""

from django.forms import Select
from django.test import TestCase

from django_providerkit.fields import ProviderField
from django_providerkit.models.provider import ProviderkitModel
from django_providerkit.models.service import ProviderServiceModel


class VirtualModelTests(TestCase):
    def test_provider_and_service_catalogs_are_not_stored(self):
        self.assertFalse(ProviderkitModel._meta.managed)
        self.assertFalse(ProviderServiceModel._meta.managed)

        provider_names = {provider.name for provider in ProviderkitModel.objects.all()}
        self.assertTrue({"package", "config", "json", "folder"} <= provider_names)

        service = ProviderServiceModel.objects.get(name="get_providers")
        self.assertIsInstance(service.fields, dict)
        self.assertIn("name", service.fields)

        with self.assertRaises(NotImplementedError):
            service.save()
        with self.assertRaises(NotImplementedError):
            service.delete()


class ProviderFieldTests(TestCase):
    def test_choices_come_from_the_provider_catalog(self):
        field = ProviderField(package_name="providerkit")

        choices = list(field.get_provider_choices())
        values = {value for value, _label in choices}

        self.assertEqual(choices[0][0], "")
        self.assertTrue({"package", "config", "json", "folder"} <= values)

        form_field = field.formfield()
        self.assertIsInstance(form_field.widget, Select)
        self.assertEqual(
            [value for value, _label in form_field.choices],
            [value for value, _label in choices],
        )
