from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext as _


def get_file_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = f"{instance.date.year}-{instance.date.month:02d}-{instance.date.day:02d}.{ext}"
    return f"{instance.model.app_label}/{instance.model.model}/{filename}"


class Backup(models.Model):
    model = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    file = models.FileField(upload_to=get_file_path)
    date = models.DateField(default=timezone.now)

    def __str__(self):
        return "{} backup ({})".format(self.model, self.date)


class Script(models.Model):
    name = models.CharField(_('Name'), max_length=100)
    source = models.TextField(_('Source'))

    class Meta:
        verbose_name = _('Script')
        verbose_name_plural = _('Scripts')

    def __str__(self):
        return self.name


class School(models.Model):
    class Meta:
        verbose_name = _('School')
        verbose_name_plural = _('Schools')

    full_name = models.CharField(max_length=128, verbose_name=_('Full Name of School'))
    headmaster = models.CharField(default='' ,max_length=128, verbose_name=_('Headmaster\'s Full Name'), blank=True)

    def __str__(self):
        return self.full_name


class University(models.Model):
    class Meta:
        verbose_name = _('University')
        verbose_name_plural = _('Universities')

    def get_logo_upload_path(instance, filename):
        ext = filename.split('.')[-1]
        dt = timezone.now()
        filename = f"{dt.year}-{dt.month:02d}-{dt.day:02d}-{dt.hour:02d}-{dt.minute:02d}-{dt.second:02d}.{ext}"
        return f"university_logos/{instance.id}/{filename}"

    full_name = models.CharField(max_length=128, verbose_name=_('Full name of University'))
    location = models.CharField(max_length=128, verbose_name=_('Location'))
    logo = models.ImageField(upload_to=get_logo_upload_path, verbose_name=_('University Logo'))

    def __str__(self):
        return self.full_name
