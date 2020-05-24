from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class InternalsConfig(AppConfig):
    name = 'internals'
    verbose_name = _('Internals')
