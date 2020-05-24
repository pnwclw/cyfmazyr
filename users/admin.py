from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils import timezone
from django.utils.html import format_html
from django.utils.translation import ugettext as _

from simple_history.admin import SimpleHistoryAdmin
from import_export.admin import ImportExportMixin

from .models import User, Session, Profile, Parent, Student
from .templatetags.users import device, location


class ParentInline(ImportExportMixin, admin.StackedInline):
    model = User.parents.through
    extra = 0
    max_num = 2
    verbose_name = _('Parent')
    verbose_name_plural = _('Parents')


class StudentInline(ImportExportMixin, admin.StackedInline):
    model = Student
    extra = 0
    max_num = 1
    autocomplete_fields = ('university',)
    description = _('Provide here information in case if user is student.')


class ProfileInline(ImportExportMixin, admin.StackedInline):
    model = Profile
    extra = 0
    max_num = 1


@admin.register(Parent)
class ParentAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ('full_name', 'phone_number_link', 'job', 'user_list')
    search_fields = ('first_name', 'last_name', 'phone_number', 'email',)

    def full_name(self, obj):
        return obj.get_full_name()
    full_name.short_description = _('Full Name')

    def phone_number_link(self, obj):
        return format_html(f'<a href="tel:{obj.phone_number}">{obj.phone_number}</a>')
    phone_number_link.short_description = _('Phone Number')

    def user_list(self, obj):
        return format_html(', '.join([
            f'<a href="/admin/{self.model._meta.app_label}/user/{i.id}/change">{i.get_full_name()}</a>' for i in obj.user_set.all()
        ]))
    user_list.short_description = _('Users')


@admin.register(User)
class CustomUserAdmin(ImportExportMixin, UserAdmin, SimpleHistoryAdmin):
    list_filter = UserAdmin.list_filter + ('group', 'klass', 'school')
    list_display = ('full_name', 'phone_number_link', 'date_joined')
    search_fields = ('first_name', 'last_name', 'phone_number', 'email',)
    autocomplete_fields = ('school',)
    date_hierarchy = 'date_joined'
    inlines = [ParentInline, ProfileInline, StudentInline]

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal Info'), {'fields': ('sex', 'last_name', 'first_name', 'middle_name', 'birthday')}),
        (_('Contacts'), {'fields': ('phone_number', 'email')}),
        (_('Group'), {'fields': ('group',)}),
        (_('Education'), {'fields': ('school', 'klass', 'symbol')}),
        (_('Permissions'), {
            'classes': ('collapse',),
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    filter_horizontal = ('groups', 'user_permissions')

    def phone_number_link(self, obj):
        return format_html(f'<a href="tel:{obj.phone_number}">{obj.phone_number}</a>')
    phone_number_link.short_description = _('Phone Number')

    def full_name(self, obj):
        return obj.get_full_name()
    full_name.short_description = _('Full Name')


class ExpiredFilter(admin.SimpleListFilter):
    title = _('Is valid')
    parameter_name = 'active'

    def lookups(self, request, model_admin):
        return (
            ('1', _('Active')),
            ('0', _('Expired'))
        )

    def queryset(self, request, queryset):
        if self.value() == '1':
            return queryset.filter(expire_date__gt=timezone.now())
        elif self.value() == '0':
            return queryset.filter(expire_date__lte=timezone.now())


@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = ('ip', 'user', 'is_valid', 'location', 'device',)
    search_fields = ('ip', 'user__id',)
    autocomplete_fields = ('user',)
    list_filter = (ExpiredFilter,)
    exclude = ('session_key',)
    readonly_fields = ('user', 'user_agent', 'ip',)

    fieldsets = (
        (None, {'fields': ('user',)}),
        (_('User agent'), {'fields': ('user_agent', 'ip')}),
        (_('Stored data'), {'fields': ('session_data', 'expire_date')}),
    )

    def is_valid(self, obj):
        return obj.expire_date > timezone.now()
    is_valid.boolean = True

    def location(self, obj):
        return location(obj.ip)
    location.short_description = _("Location")

    def device(self, obj):
        return device(obj.user_agent) if obj.user_agent else '-'
    location.short_description = _("Location")

    def get_form(self,request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        session_data = form.base_fields.get("session_data")
        session_data.help_text = f"Decoded value: {obj.get_decoded()}"
        return form
