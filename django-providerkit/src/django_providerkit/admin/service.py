from django.utils.translation import gettext_lazy as _
from django_boosted import AdminBoostModel
from django_providerkit.models.service import ProviderServiceModel

class ProviderServiceAdmin(AdminBoostModel):
    """Admin for provider service model."""
    list_display = ['name', 'description', 'fields_count_display']
    search_fields = ['name']
    readonly_fields = ['name', 'description', 'fields_display']
    list_filter = []
    ordering = ['name']

    def fields_count_display(self, obj):
        return len(obj.fields) if isinstance(getattr(obj, 'fields', None), dict) else '-'
    fields_count_display.short_description = _("Fields")

    def change_fieldsets(self):
        self.add_to_fieldset(None, ['name', 'description'])
        self.add_to_fieldset(_("Fields"), ['fields_display'])
