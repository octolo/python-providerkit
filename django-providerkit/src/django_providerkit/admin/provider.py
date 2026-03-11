from django.contrib import admin
from django.templatetags.static import static
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from django_boosted import AdminBoostModel, admin_boost_view
from providerkit.kit import FIELDS_PROVIDER_BASE
from providerkit.kit.config import FIELDS_CONFIG_BASE
from providerkit.kit.package import FIELDS_PACKAGE_BASE
from providerkit.kit.service import FIELDS_SERVICE_BASE

FIELDS_PROVIDERKIT = {
    **FIELDS_PROVIDER_BASE,
    **FIELDS_CONFIG_BASE,
    **FIELDS_PACKAGE_BASE,
    **FIELDS_SERVICE_BASE,
}


class BaseProviderAdminFilters(admin.SimpleListFilter):
    """Filter for base provider model."""
    title = _("Base provider")
    parameter_name = "base_provider"
    field: str | None = None

    def lookups(self, request, model_admin):  # noqa: ARG002
        return (
            ("1", _("Yes")),
            ("0", _("No")),
        )

    def queryset(self, request, queryset):  # noqa: ARG002
        if self.field and self.value():
            filter_value = self.value() == "1"
            return queryset.filter(**{self.field: filter_value})
        return queryset


class PackagesInstalledFilter(BaseProviderAdminFilters):
    """Filter for packages installed status using pkg alias."""
    title = _("Packages installed")
    parameter_name = "pkg"
    field = "are_packages_installed"


class ServicesImplementedFilter(BaseProviderAdminFilters):
    """Filter for services implemented status using svc alias."""
    title = _("Services implemented")
    parameter_name = "svc"
    field = "are_services_implemented"


class ConfigReadyFilter(BaseProviderAdminFilters):
    """Filter for config ready status using cfg alias."""
    title = _("Config ready")
    parameter_name = "cfg"
    field = "is_config_ready"


class BaseProviderAdmin(AdminBoostModel):
    """Admin for provider model."""
    list_display = ['admin_display_name', "config_status_display", "package_status_display", "service_status_display"]
    search_fields = tuple(FIELDS_PROVIDER_BASE.keys())
    readonly_fields = tuple(FIELDS_PROVIDERKIT.keys())
    fieldsets = [
        (None, {'fields': tuple(FIELDS_PROVIDER_BASE.keys())}),
    ]
    list_filter = [PackagesInstalledFilter, ServicesImplementedFilter, ConfigReadyFilter]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.generate_fields_costs_and_services()

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def _make_cost_and_service_display(self, service_name: str):
        """Create an admin method to display the cost of a service."""
        cost_field = f"{service_name}_cost"

        def cost_and_service_display(self, obj):
            has = getattr(obj, f"has_{service_name}", False)
            cost = getattr(obj, cost_field, _("N/A or Free"))
            icon_html = self.boolean_icon_html(has)
            return self.format_with_help_text(icon_html, cost)

        cost_and_service_display.short_description = service_name
        return cost_and_service_display

    def generate_fields_costs_and_services(self):
        services_fields = getattr(self.model, "has_service_fields", [])
        for field in services_fields:
            service_name = field.replace("has_", "")
            field_name = f"status_{service_name}"
            setattr(self.__class__, field_name, self._make_cost_and_service_display(service_name))

    def get_fields_costs_and_services(self):
        services_fields = getattr(self.model, "has_service_fields", [])
        return [f"status_{f.replace('has_', '')}" for f in services_fields]

    def boolean_icon_html(self, value):
        """Return the HTML image (admin icon) for a boolean value."""
        is_ok = value == "✓" if isinstance(value, str) else bool(value)
        icon = "icon-yes.svg" if is_ok else "icon-no.svg"
        return format_html(
            '<img src="{}" alt="{}">',
            static(f"admin/img/{icon}"),
            _("Yes") if is_ok else _("No"),
        )

    def _status_display(self, obj, attr_name: str):
        """Display the boolean icon + label when status is not OK."""
        provider = getattr(obj, "_provider", None) or obj
        status_str = getattr(provider, attr_name)
        status_ok = status_str == "✓"
        icon_html = self.boolean_icon_html(status_ok)
        if status_ok:
            return icon_html
        label_html = self.format_label(status_str, size="small", label_type="secondary")
        return format_html("{} {}", icon_html, label_html)

    def config_status_display(self, obj):
        return self._status_display(obj, "config_status_str")
    config_status_display.short_description = _("Config status")

    def package_status_display(self, obj):
        return self._status_display(obj, "package_status_str")
    package_status_display.short_description = _("Package status")

    def service_status_display(self, obj):
        return self._status_display(obj, "service_status_str")
    service_status_display.short_description = _("Service status")

    def admin_display_name(self, obj):
        return self.format_with_help_text(obj.display_name, obj.description)

    def change_fieldsets(self):
        self.add_to_fieldset('Config', list(FIELDS_CONFIG_BASE.keys()))
        self.add_to_fieldset('Packages', list(FIELDS_PACKAGE_BASE.keys()))
        self.add_to_fieldset('Services', list(FIELDS_SERVICE_BASE.keys()))

    @admin_boost_view("list", _("Costs"))
    def costs_list(self, request):
        return {
            "title": _("Costs"),
            "queryset": self.get_queryset(request),
            "list_display": ['admin_display_name', *self.get_fields_costs_and_services()],
            "search_fields": ['name', 'display_name', 'description'],
        }
