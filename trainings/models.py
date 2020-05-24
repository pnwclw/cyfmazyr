from django.db import models
from django.utils.translation import ugettext as _

from simple_history.models import HistoricalRecords

from users.models import User


class Topic(models.Model):
    class Meta:
        ordering = ('order',)

    title = models.CharField(max_length=256)
    order = models.PositiveIntegerField(default=0, blank=False, null=False)

    history = HistoricalRecords()

    def __str__(self):
        return f'{self.order}. {self.title}'


class Task(models.Model):
    class Meta:
        ordering = ('order',)

    topic = models.ForeignKey(Topic, on_delete=models.SET_NULL, null=True)
    title = models.CharField(max_length=128)
    authors = models.ManyToManyField(User, blank=True)
    source = models.CharField(max_length=128, blank=True)
    input_file = models.CharField(default='stdin', max_length=128)
    output_file = models.CharField(default='stdout', max_length=128)
    url = models.URLField(max_length=512, blank=True)
    description = models.TextField(max_length=8192, help_text=_('Use HTML markup'))
    archive = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0, blank=False, null=False)

    history = HistoricalRecords()

    def __str__(self):
        return self.title


class StandardTest(models.Model):
    task = models.OneToOneField(Task, on_delete=models.CASCADE)
    input_data = models.TextField(max_length=1024)
    output_data = models.TextField(max_length=1024)

    history = HistoricalRecords()

    def __str__(self):
        return _(f'{self.task} test')
