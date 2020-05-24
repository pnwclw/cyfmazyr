from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext as _

from simple_history.models import HistoricalRecords

from users.models import User


class Contributor(models.Model):
    class Meta:
        verbose_name = _('Contributor')
        verbose_name_plural = _('Contributors')

    def get_photo_upload_path(instance, filename):
        ext = filename.split('.')[-1]
        dt = timezone.now()
        filename = f"{dt.year}-{dt.month:02d}-{dt.day:02d}-{dt.hour:02d}-{dt.minute:02d}-{dt.second:02d}.{ext}"
        return f"contributor/{filename}"

    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name=_('User'))
    contribution = models.TextField(verbose_name=_('Contribution'))
    url = models.URLField(null=True, blank=True, verbose_name=_('URL'))
    photo = models.ImageField(upload_to=get_photo_upload_path, verbose_name=_('Photo'))

    history = HistoricalRecords()

    def __str__(self):
        return self.user.get_full_name()


class HallOfFameMember(models.Model):
    class Meta:
        ordering = ('order',)
        verbose_name = _('Hall of Fame Member')
        verbose_name_plural = _('Hall of Fame Members')

    def get_photo_upload_path(instance, filename):
        ext = filename.split('.')[-1]
        dt = timezone.now()
        filename = f"{dt.year}-{dt.month:02d}-{dt.day:02d}-{dt.hour:02d}-{dt.minute:02d}-{dt.second:02d}.{ext}"
        return f"hall_of_fame/{filename}"

    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name=_('User'))
    achievement = models.TextField(verbose_name=_('Achievement'))
    photo = models.ImageField(upload_to=get_photo_upload_path, verbose_name=_('Photo'))
    order = models.PositiveIntegerField(default=0, blank=False, null=False)

    history = HistoricalRecords()

    def __str__(self):
        return self.user.get_full_name()
