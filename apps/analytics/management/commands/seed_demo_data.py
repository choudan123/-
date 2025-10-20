from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction

from apps.poster_enums.models import Scene, PosterType, Style

from apps.analytics.models import PosterEvent
from apps.analytics import constants as C


class Command(BaseCommand):
    help = "Seed demo data for scenes, poster types, styles and a few events to warm up recommendations."

    @transaction.atomic
    def handle(self, *args, **options):
        User = get_user_model()

        # 1) Ensure a demo user
        user, _ = User.objects.get_or_create(
            defaults={"is_active": True},
            **{User.USERNAME_FIELD: "demo_user"}  # 对于自定义 USERNAME_FIELD 会自动适配
        )

        # 2) Scenes
        scenes_spec = [
            {"name": "门店宣传", "tags": "门店,促销"},
            {"name": "社交分享", "tags": "社交,节日"},
            {"name": "招聘",   "tags": "招聘,校园"},
        ]
        scene_objs = {}
        for spec in scenes_spec:
            s, _ = Scene.objects.get_or_create(name=spec["name"], defaults={
                "is_active": True,
                "tags": spec.get("tags", ""),
            })
            scene_objs[spec["name"]] = s

        # 3) Styles
        styles_spec = [
            {"name": "极简", "tags": "简约,现代"},
            {"name": "复古", "tags": "复古,怀旧"},
            {"name": "科技", "tags": "科技,未来"},
            {"name": "商务", "tags": "商务,正式"},
        ]
        style_objs = {}
        for i, spec in enumerate(styles_spec):
            st, _ = Style.objects.get_or_create(name=spec["name"], defaults={
                "is_active": True,
                "tags": spec.get("tags", ""),
                "reference_images": [],
            })
            style_objs[spec["name"]] = st

        # 4) PosterTypes
        types_spec = [
            {"name": "促销广告", "order": 1, "tags": "促销,门店"},
            {"name": "活动宣传", "order": 2, "tags": "活动,社交"},
            {"name": "招聘海报", "order": 3, "tags": "招聘,校园"},
        ]
        type_objs = {}
        for spec in types_spec:
            pt, created = PosterType.objects.get_or_create(name=spec["name"], defaults={
                "is_active": True,
                "order": spec["order"],
                "tags": spec.get("tags", ""),
            })
            # 挂载主场景（任选一个合理主场景）
            if created:
                if pt.name == "促销广告":
                    pt.scene = scene_objs["门店宣传"]
                elif pt.name == "活动宣传":
                    pt.scene = scene_objs["社交分享"]
                else:
                    pt.scene = scene_objs["招聘"]
                pt.save()
            type_objs[spec["name"]] = pt

        # 5) 多场景关联 + 允许风格集合
        # 允许风格
        type_objs["促销广告"].styles.set([style_objs["极简"], style_objs["商务"]])
        type_objs["活动宣传"].styles.set([style_objs["极简"], style_objs["科技"]])
        type_objs["招聘海报"].styles.set([style_objs["极简"], style_objs["复古"]])

        # 多场景挂载（示例：有些类型在多个场景可用）
        type_objs["促销广告"].scenes.set([scene_objs["门店宣传"]])
        type_objs["活动宣传"].scenes.set([scene_objs["社交分享"], scene_objs["门店宣传"]])
        type_objs["招聘海报"].scenes.set([scene_objs["招聘"], scene_objs["社交分享"]])

        # 6) 生成一些行为事件（触发统计）
        def log(scene_name, type_name, style_name, event):
            PosterEvent.objects.create(
                user=user,
                scene=scene_objs[scene_name],
                poster_type=type_objs[type_name],
                style=style_objs[style_name],
                event=event,
            )

        # 门店宣传下，促销广告 + 极简/商务 更常被使用
        for _ in range(6):
            log("门店宣传", "促销广告", "极简", C.EVENT_GENERATE)
        for _ in range(3):
            log("门店宣传", "促销广告", "商务", C.EVENT_DOWNLOAD)

        # 社交分享下，活动宣传 + 科技更热
        for _ in range(5):
            log("社交分享", "活动宣传", "科技", C.EVENT_GENERATE)
        for _ in range(2):
            log("社交分享", "活动宣传", "极简", C.EVENT_VIEW)

        # 招聘下，招聘海报 + 极简/复古
        for _ in range(4):
            log("招聘", "招聘海报", "极简", C.EVENT_GENERATE)
        for _ in range(2):
            log("招聘", "招聘海报", "复古", C.EVENT_DOWNLOAD)

        self.stdout.write(self.style.SUCCESS("Seed demo data created."))