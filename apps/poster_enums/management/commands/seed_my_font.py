from django.core.management.base import BaseCommand
from django.db import transaction
from apps.poster_enums.models import Font

class Command(BaseCommand):
    help = "Seed your own fonts with custom screenshot demo images into the 'poster_enums_font' table."

    @transaction.atomic
    def handle(self, *args, **options):
        fonts = [
            # 举例：你自己上传的截图链接
            {
                "name": "Noto Sans SC",
                "category": "中文",  # 语种分类即可
                "demo_image": f"/static/font/img.png",
                "is_system": True,
                "is_active": True,
            },
            {
                "name": "NOto Serif",
                "category": "中文",
                "demo_image": f"/static/font/img_1.png",
                "is_system": False,
                "is_active": True,
            },
            {
                "name": "WDXL Lubrifont SC",
                "category": "中文",
                "demo_image": f"/static/font/img_2.png",
                "is_system": True,
                "is_active": True,
            },
            {
                "name": "Ma Shan Zheng",
                "category": "中文",
                "demo_image": f"/static/font/img_3.png",
                "is_system": False,
                "is_active": True,
            },
            {
                "name": "ZCOOL XiaoWei",
                "category": "中文",
                "demo_image": f"/static/font/img_4.png",
                "is_system": True,
                "is_active": True,
            },
            {
                "name": "ZCOOL KuaiLe",
                "category": "中文",
                "demo_image": f"/static/font/img_5.png",
                "is_system": True,
                "is_active": True,
            },
            {
                "name": "ZCOOL QingKe HuangYou",
                "category": "中文",
                "demo_image": f"/static/font/img_6.png",
                "is_system": False,
                "is_active": True,
            },
            {
                "name": "Zhi Mang Xing",
                "category": "中文",
                "demo_image": f"/static/font/img_7.png",
                "is_system": False,
                "is_active": True,
            },
            {
                "name": "Liu Jian Mao Cao",
                "category": "中文",
                "demo_image": f"/static/font/img_8.png",
                "is_system": True,
                "is_active": True,
            },
            {
                "name": "Long Cang",
                "category": "中文",
                "demo_image": f"/static/font/img_9.png",
                "is_system": True,
                "is_active": True,
            },

            # ... 你可以继续添加其它字体
        ]

        for font in fonts:
            Font.objects.get_or_create(
                name=font["name"],
                defaults={
                    "category": font["category"],
                    "demo_image": font["demo_image"],
                    "is_system": font["is_system"],
                    "is_active": font["is_active"],
                },
            )

        self.stdout.write(self.style.SUCCESS("Your custom font library has been seeded successfully!"))