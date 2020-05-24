from django.contrib import admin
from django.utils.translation import ugettext as _

from simple_history.admin import SimpleHistoryAdmin
from import_export.admin import ImportExportActionModelAdmin
from adminsortable2.admin import SortableAdminMixin

from .models import HallOfFameMember


@admin.register(HallOfFameMember)
class HallOfFameMemberAdmin(SortableAdminMixin, ImportExportActionModelAdmin, SimpleHistoryAdmin):
    list_display = ('full_name', 'achievement', 'order')
    autocomplete_fields = ('user',)

    def full_name(self, obj):
        return obj.user.get_full_name()
    full_name.short_description = _('Full Name')