from django.contrib import admin
from django.contrib.contenttypes.models import ContentType
from django.urls import path

from .forms import ScriptForm
from .models import Backup, Script, School, University
from .views import execute_script_view


@admin.register(Backup)
class BackupAdmin(admin.ModelAdmin):
    list_display = ('model', 'file', 'date')
    list_filter = (
        ('model', admin.RelatedOnlyFieldListFilter),
    )
    date_hierarchy = 'date'

    def get_form(self, request, obj=None, **kwargs):
        form = super(BackupAdmin, self).get_form(request, obj, **kwargs)
        model = form.base_fields.get('model')
        if model:
            existing_ids = []
            for i in model.queryset:
                if i.model_class():
                    existing_ids.append(i.id)
            model.queryset = ContentType.objects.filter(id__in=existing_ids)

        return form


@admin.register(Script)
class ScriptAdmin(admin.ModelAdmin):
    form = ScriptForm
    list_display = ('name',)
    change_form_template = 'internals/scripts/change_form.html'

    def get_urls(self):
        urls = super(ScriptAdmin, self).get_urls()
        custom_urls = [
            path('execute/', self.admin_site.admin_view(execute_script_view), name="execute-script"),
        ]
        return custom_urls + urls


@admin.register(School)
class SchoolAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'headmaster')
    search_fields = ('full_name',)


@admin.register(University)
class UniversityAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'location')
    search_fields = ('full_name',)
