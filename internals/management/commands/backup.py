from django.contrib import admin
from django.contrib.contenttypes.models import ContentType
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from import_export import resources

from internals.models import Backup

import argparse
import datetime


def valid_date(s):
    try:
        return datetime.datetime.strptime(s, "%Y-%m-%d")
    except ValueError:
        msg = f"Not a valid date: '{s}'."
        raise argparse.ArgumentTypeError(msg)


class Command(BaseCommand):
    help = 'Creates data backup for previous day and uploads to Google Cloud Storage'

    def add_arguments(self, parser):
        parser.add_argument(
            "--startdate",
            default=timezone.now() - datetime.timedelta(days=1),
            help="The Start Date - format YYYY-MM-DD", 
            type=valid_date
        )
        parser.add_argument(
            "--enddate",
            default=timezone.now(),
            help="The End Date - format YYYY-MM-DD (not inclusive)", 
            type=valid_date
        )

    def handle(self, *args, **options):
        start_date = options["startdate"].date()
        end_date = options["enddate"].date()
        cur_date = timezone.now().date()
        if end_date > cur_date:
            end_date = cur_date
            self.stdout.write(self.style.WARNING(f"enddate can't be in future. Using default value {end_date}"))
        if start_date >= end_date:
            raise CommandError("enddate can't be equal or before startdate")
        if start_date > (timezone.now() - datetime.timedelta(days=1)).date():
            raise CommandError("startdate can't start from today or future")

        existing_ct_ids = []
        for i in ContentType.objects.all():
            if i.app_label in ["admin", "auth", "contenttypes", "sessions", "internals"]:
                continue
            if i.model_class():
                existing_ct_ids.append(i.id)
        content_types = ContentType.objects.filter(id__in=existing_ct_ids)

        day_count = (end_date - start_date).days
        for date in (start_date + datetime.timedelta(n) for n in range(day_count)):
            self.stdout.write(f"Backuping {date}")
            for content_type in content_types:
                model = content_type.model_class()
                resource = resources.modelresource_factory(model=model)()
                modeladmin = admin.site._registry.get(model)
                date_hierarchy = getattr(modeladmin, 'date_hierarchy', '')
                if not date_hierarchy:
                    if content_type.model.startswith('historical'):
                        date_hierarchy = "history_date"
                    else:
                        continue

                self.stdout.write(f"  - backuping {content_type.app_label}.{content_type.model}")

                self.stdout.write(f"    - querying database")
                queryset = model.objects.filter(**{
                    f"{date_hierarchy}__date__gte": date,
                    f"{date_hierarchy}__date__lt": date + datetime.timedelta(days=1),
                })
                
                self.stdout.write(f"    - exporting data to csv")
                dataset = resource.export(queryset)
                
                self.stdout.write(f"    - creating backup")
                backup = Backup(model=content_type, date=date)
                backup.file.save("test.csv", ContentFile(dataset.csv.encode('utf-8')))
                backup.save()
