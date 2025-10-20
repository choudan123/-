from django.core.management.base import BaseCommand
from django.db import transaction
from apps.poster_enums.models import Size


class Command(BaseCommand):
    help = "Seed common sizes into the 'poster_enums_size' table."

    @transaction.atomic
    def handle(self, *args, **options):
        sizes = [
            {"name": "1K", "width": 1024, "height": 1024, "is_active": True},
            {"name": "2K", "width": 2048, "height": 2048, "is_active": True},
            {"name": "4K", "width": 4096, "height": 4096, "is_active": True},
            {"name": "1920x1080", "width": 1920, "height": 1080, "is_active": True},
            {"name": "1080x1920", "width": 1080, "height": 1920, "is_active": True},
            {"name": "2048x2048", "width": 2048, "height": 2048, "is_active": True},
            {"name": "2384x1728", "width": 2384, "height": 1728, "is_active": True},
            {"name": "1728x2304", "width": 1728, "height": 2304, "is_active": True},
            {"name": "2560x1440", "width": 2560, "height": 1440, "is_active": True},
            {"name": "1440x2560", "width": 1440, "height": 2560, "is_active": True},
        ]

        for size in sizes:
            Size.objects.get_or_create(
                name=size["name"],
                defaults={
                    "width": size["width"],
                    "height": size["height"],
                    "is_active": size["is_active"],
                },
            )

        self.stdout.write(self.style.SUCCESS("Sizes have been seeded successfully!"))