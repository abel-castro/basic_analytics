import random

from analytics.models import Domain
from analytics.tests.factories import (
    TEST_BROWSERS,
    TEST_DEVICES,
    TEST_METADATA,
    DomainFactory,
    PageViewFactory,
)
from django.core.management.base import BaseCommand
from freezegun import freeze_time


class Command(BaseCommand):
    help = "Create test page views for a test domain"

    def add_arguments(self, parser):
        parser.add_argument(
            "--clean",
            action="store_true",
            help="Delete all existing routes before triggering the import.",
        )
        parser.add_argument(
            "--random_values",
            action="store_true",
            help="Assign random values for browser and device",
        )

    def handle(self, *args, **options):
        clean = options["clean"]
        random_values = options["random_values"]
        if clean:
            Domain.objects.all().delete()

        amount_page_views = 0
        domain = DomainFactory.create()

        for i in range(1, 100):
            metadata = TEST_METADATA
            if random_values:
                metadata = {
                    "browser": random.choice(TEST_BROWSERS),
                    "os": "iOS",
                    "device": random.choice(TEST_DEVICES),
                    "country": "AT",
                }
                month = random.randint(1, 12)
                day = (
                    random.randint(1, 28)
                    if month == 2
                    else random.randint(1, 30 if month in [4, 6, 9, 11] else 31)
                )

            with freeze_time(f"2022-{month}-{day}"):
                page_views = PageViewFactory.create_batch(
                    random.randint(1, 100), domain=domain, metadata=metadata
                )
                amount_page_views += len(page_views)

            with freeze_time(f"2023-{month}-{day}"):
                page_views = PageViewFactory.create_batch(
                    random.randint(1, 100), domain=domain, metadata=metadata
                )
                amount_page_views += len(page_views)

        self.stdout.write(f"{amount_page_views} were created for the domain {domain}")
