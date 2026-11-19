"""Admin rendering and permission tests for provider services."""

from unittest.mock import patch

from django.contrib.auth.models import Permission, User
from django.test import TestCase
from django.urls import reverse
from django.utils.safestring import SafeString

from django_providerkit.managers.service import ProviderServiceManager
from django_providerkit.models.service import ProviderServiceModel

HTML_FIELDS = {
    "label": "<img src=x onerror=alert(1)>",
    "note": "</pre><script>alert(1)</script>",
}
ESCAPED_IMAGE = "&lt;img src=x onerror=alert(1)&gt;"
ESCAPED_BREAKOUT = "&lt;/pre&gt;&lt;script&gt;alert(1)&lt;/script&gt;"


def service_catalog():
    return [
        {
            "name": "xss-service",
            "description": "Benign service description",
            "fields": HTML_FIELDS,
        }
    ]


class FieldsDisplayTests(TestCase):
    def test_fields_display_escapes_html_inside_pre(self):
        service = ProviderServiceModel(
            name="demo",
            description="demo",
            fields=HTML_FIELDS,
        )

        rendered = service.fields_display

        self.assertIsInstance(rendered, SafeString)
        self.assertIn("<pre>", rendered)
        self.assertIn("</pre>", rendered)
        self.assertIn(ESCAPED_IMAGE, rendered)
        self.assertIn(ESCAPED_BREAKOUT, rendered)
        self.assertNotIn("<img", rendered)
        self.assertNotIn("<script>", rendered)
        self.assertNotIn("</pre><script>", rendered)


class ServiceAdminTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.catalog_url = reverse(
            "admin:django_providerkit_providerkitmodel_services_list"
        )
        cls.detail_url = reverse(
            "admin:django_providerkit_providerservicemodel_change",
            args=["xss-service"],
        )
        cls.provider_view = Permission.objects.get(codename="view_providerkitmodel")
        cls.service_view = Permission.objects.get(codename="view_providerservicemodel")

    def setUp(self):
        self.catalog_patch = patch.object(
            ProviderServiceManager,
            "get_data",
            lambda self: service_catalog(),
        )
        self.catalog_patch.start()
        self.addCleanup(self.catalog_patch.stop)

    def _staff(self, username, *permissions):
        user = User.objects.create_user(username, password="secret", is_staff=True)
        if permissions:
            user.user_permissions.set(permissions)
        return user

    def test_detail_page_renders_fields_as_text(self):
        self.client.force_login(self._staff("viewer", self.service_view))

        response = self.client.get(self.detail_url)

        self.assertContains(response, "<pre>")
        self.assertContains(response, ESCAPED_IMAGE)
        self.assertContains(response, ESCAPED_BREAKOUT)
        self.assertNotContains(response, "<img src=x onerror=alert(1)>")
        self.assertNotContains(response, "</pre><script>alert(1)</script>")

    def test_anonymous_visitors_are_sent_to_login(self):
        catalog = self.client.get(self.catalog_url)
        detail = self.client.get(self.detail_url)

        self.assertEqual(catalog.status_code, 302)
        self.assertIn("/admin/login/", catalog["Location"])
        self.assertEqual(detail.status_code, 302)
        self.assertIn("/admin/login/", detail["Location"])

    def test_staff_without_permissions_cannot_open_catalog_or_detail(self):
        self.client.force_login(self._staff("noperms"))

        self.assertEqual(self.client.get(self.catalog_url).status_code, 403)
        self.assertEqual(self.client.get(self.detail_url).status_code, 403)

    def test_catalog_requires_provider_and_service_view_permissions(self):
        provider_only = self._staff("provider-only", self.provider_view)
        service_only = self._staff("service-only", self.service_view)
        both = self._staff("both", self.provider_view, self.service_view)

        self.client.force_login(provider_only)
        self.assertEqual(self.client.get(self.catalog_url).status_code, 403)

        self.client.force_login(service_only)
        self.assertEqual(self.client.get(self.catalog_url).status_code, 403)

        self.client.force_login(both)
        response = self.client.get(self.catalog_url)
        self.assertContains(response, "xss-service")

    def test_detail_requires_service_view_permission(self):
        self.client.force_login(self._staff("provider-only", self.provider_view))
        self.assertEqual(self.client.get(self.detail_url).status_code, 403)

        self.client.force_login(self._staff("service-only", self.service_view))
        self.assertContains(self.client.get(self.detail_url), ESCAPED_IMAGE)
