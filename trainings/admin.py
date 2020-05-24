from django.contrib import admin
from django.utils.translation import ugettext as _

from adminsortable2.admin import SortableAdminMixin
from django.utils.html import format_html
from import_export.admin import ImportExportActionModelAdmin
from simple_history.admin import SimpleHistoryAdmin

from .models import Topic, Task, StandardTest


@admin.register(Topic)
class TopicAdmin(SortableAdminMixin, ImportExportActionModelAdmin, SimpleHistoryAdmin):
    list_display = ('title_with_number', 'order')
    search_fields = ('title', 'order')

    def title_with_number(self, obj):
        return obj.__str__()
    title_with_number.short_description = _('Title')


class StandardTestInline(admin.TabularInline):
    model = StandardTest
    min_num = 0
    extra = 0


@admin.register(Task)
class TaskAdmin(SortableAdminMixin, ImportExportActionModelAdmin, SimpleHistoryAdmin):
    list_display = ('title', 'topic_num',)
    list_filter = ('topic',)
    search_fields = ('title', 'description')
    autocomplete_fields = ('topic', 'authors')
    filter_horizontal = ('authors',)
    inlines = [StandardTestInline,]

    def topic_num(self, obj):
        return format_html(
            f'<a href="/admin/{self.model._meta.app_label}/topic/{obj.topic.id}/change">{obj.topic.order}</a>'
        )
    topic_num.short_description = _('Topic Number')
