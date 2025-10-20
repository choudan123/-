from django.core.management.base import BaseCommand
from django.db import transaction
from apps.poster_enums.models import AspectRatio


class Command(BaseCommand):
    help = "Seed common aspect ratios into the 'poster_enums_aspectratio' table."

    @transaction.atomic
    def handle(self, *args, **options):
        aspect_ratios = [
            {"name": "1:1", "ratio_w": 1, "ratio_h": 1},
            {"name": "4:3", "ratio_w": 4, "ratio_h": 3},
            {"name": "3:4", "ratio_w": 3, "ratio_h": 4},
            {"name": "16:9", "ratio_w": 16, "ratio_h": 9},
            {"name": "9:16", "ratio_w": 9, "ratio_h": 16},
            {"name": "3:2", "ratio_w": 3, "ratio_h": 2},
            {"name": "2:3", "ratio_w": 2, "ratio_h": 3},
            {"name": "21:9", "ratio_w": 21, "ratio_h": 9},
            {"name": "9:21", "ratio_w": 9, "ratio_h": 21},
            {"name": "5:4", "ratio_w": 5, "ratio_h": 4},
            {"name": "4:5", "ratio_w": 4, "ratio_h": 5},
        ]

        for ratio in aspect_ratios:
            AspectRatio.objects.get_or_create(
                name=ratio["name"],
                defaults={
                    "ratio_w": ratio["ratio_w"],
                    "ratio_h": ratio["ratio_h"],
                    "is_active": True,
                },
            )

        self.stdout.write(self.style.SUCCESS("Aspect ratios have been seeded successfully!"))