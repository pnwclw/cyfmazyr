from django.core.management.base import BaseCommand
from django.utils import timezone

from users.models import SSOLink

from datetime import timedelta


class Command(BaseCommand):
    help = "Deletes all SSO links that haven't used within 1 minute"

    def handle(self, *args, **options):
        self.stdout.write("Getting all SSO links")
        datetime = timezone.now()
        links_to_remove = SSOLink.objects.filter(date_joined__lte=datetime - timedelta(minutes=1))
        self.stdout.write(f"Found {len(links_to_remove)} links. Deleting...")
        links_to_remove.delete()