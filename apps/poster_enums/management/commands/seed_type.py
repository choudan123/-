from django.core.management.base import BaseCommand
from django.db import transaction
from apps.poster_enums.models import Scene, Style, PosterType


class Command(BaseCommand):
    help = "Seed all poster enum tables with verified relationships based on actual model definitions."

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write("Starting verified seed of all enum tables...")

        # 1. 创建场景数据
        scenes = self.create_scenes()
        self.stdout.write(self.style.SUCCESS(f"Scenes seeded: {len(scenes)}"))

        # 2. 创建风格数据
        styles = self.create_styles()
        self.stdout.write(self.style.SUCCESS(f"Styles seeded: {len(styles)}"))

        # 3. 创建海报类型及关联关系（严格验证）
        poster_types = self.create_poster_types_with_verified_relations(scenes, styles)
        self.stdout.write(self.style.SUCCESS(f"Poster types seeded: {len(poster_types)}"))

        # 4. 验证关系完整性
        self.verify_relationships()

        self.stdout.write(self.style.SUCCESS("✅ All enum tables seeded and verified successfully!"))

    def create_scenes(self):
        """创建应用场景数据 - 共40个"""
        scenes_data = [
            # 商业相关场景 (0-14)
            {"name": "门店宣传", "tags": "线下,门店,导流,零售,店铺"},
            {"name": "电商促销", "tags": "电商,促销,转化,折扣,销售"},
            {"name": "新品发布", "tags": "新品,发布,品牌,上新,产品"},
            {"name": "品牌形象", "tags": "品牌,形象,调性,视觉,企业"},
            {"name": "开业海报", "tags": "开业,新店,开张,开门红,庆典"},
            {"name": "会员招募", "tags": "会员,权益,增长,积分,福利"},
            {"name": "限时折扣", "tags": "限时,折扣,秒杀,抢购,优惠"},
            {"name": "价格清单", "tags": "价目,清单,报价,目录,价格"},
            {"name": "招商合作", "tags": "招商,合作,代理,加盟,商务"},
            {"name": "展会布告", "tags": "展会,参展,展位,导览,B2B"},
            {"name": "汽车促销", "tags": "汽车,车展,试驾,降价,4S店"},
            {"name": "房产海报", "tags": "房产,楼盘,看房,开盘,地产"},
            {"name": "家政维修", "tags": "家政,维修,上门,清洁,服务"},
            {"name": "招聘海报", "tags": "招聘,岗位,人才,HR,求职"},
            {"name": "课程招生", "tags": "教育,招生,课程,培训,学习"},

            # 餐饮相关场景 (15-19)
            {"name": "菜单海报", "tags": "菜单,餐饮,菜品,美食,价格"},
            {"name": "餐饮优惠", "tags": "餐饮,优惠,套餐,团购,美食"},
            {"name": "咖啡新品", "tags": "咖啡,新品,饮品,手作,轻食"},
            {"name": "酒吧活动", "tags": "夜店,酒吧,派对,DJ,娱乐"},
            {"name": "美业促销", "tags": "美容,美发,美甲,皮肤,护理"},

            # 活动相关场景 (20-29)
            {"name": "社交分享", "tags": "社媒,曝光,互动,分享,朋友圈"},
            {"name": "活动预热", "tags": "活动,预热,倒计时,造势,宣传"},
            {"name": "线下活动报名", "tags": "报名,活动,线下,聚会,参与"},
            {"name": "节日祝福", "tags": "节日,节庆,祝福,节气,贺卡"},
            {"name": "社区活动", "tags": "社区,邻里,公益,便民,志愿"},
            {"name": "校园活动", "tags": "校园,社团,青春,活动,学生"},
            {"name": "会议日程", "tags": "会议,议程,峰会,论坛,商务"},
            {"name": "演出海报", "tags": "演出,舞台,戏剧,剧场,艺术"},
            {"name": "音乐会", "tags": "音乐,演出,live,演奏,音乐节"},
            {"name": "运动赛事", "tags": "运动,比赛,报名,锦标,体育"},

            # 公益服务场景 (30-34)
            {"name": "慈善募捐", "tags": "慈善,公益,募捐,基金,爱心"},
            {"name": "旅游推广", "tags": "旅游,目的地,打卡,攻略,景点"},
            {"name": "健身团课", "tags": "健身,团课,私教,塑形,运动"},
            {"name": "医疗门诊通知", "tags": "医疗,门诊,排班,就诊,预约"},
            {"name": "药店健康科普", "tags": "药店,健康,科普,用药,保健"},

            # 通知公告场景 (35-39)
            {"name": "公告通知", "tags": "公告,通知,告示,通告,信息"},
            {"name": "温馨提示", "tags": "提示,指引,礼貌,提醒,注意"},
            {"name": "安全提示", "tags": "安全,规范,须知,防护,警示"},
            {"name": "寻物启事", "tags": "寻物,丢失,启事,失物,寻找"},
            {"name": "招领启事", "tags": "招领,失物,启事,公告,拾到"},
        ]

        scenes = []
        for i, s in enumerate(scenes_data):
            scene, _ = Scene.objects.get_or_create(
                name=s["name"],
                defaults={
                    "icon": "",
                    "is_active": True,
                    "tags": s["tags"],
                },
            )
            scenes.append(scene)
        return scenes

    def create_styles(self):
        """创建视觉风格数据 - 共24个"""
        styles_data = [
            # 基础风格 (0-7)
            {"name": "极简", "tags": "极简,minimal,留白,简洁,克制,现代"},
            {"name": "复古", "tags": "复古,vintage,怀旧,做旧,胶片,经典"},
            {"name": "科技", "tags": "科技,tech,赛博,霓虹,未来,数字"},
            {"name": "商务", "tags": "商务,business,专业,稳重,蓝灰,正式"},
            {"name": "时尚", "tags": "时尚,fashion,潮流,前卫,高街,现代"},
            {"name": "奢华", "tags": "奢华,luxury,金色,质感,大理石,高端"},
            {"name": "温馨", "tags": "温馨,warm,柔和,治愈,家庭,舒适"},
            {"name": "卡通", "tags": "卡通,cute,童趣,Q版,表情,可爱"},

            # 创意风格 (8-15)
            {"name": "手绘", "tags": "手绘,hand-drawn,插画,素描,线稿,艺术"},
            {"name": "扁平", "tags": "扁平,flat,简化,图标,清晰,几何"},
            {"name": "渐变", "tags": "渐变,gradient,多彩,流光,叠加,色彩"},
            {"name": "霓虹", "tags": "霓虹,neon,夜色,高饱和,辉光,炫酷"},
            {"name": "金属", "tags": "金属,metal,拉丝,镜面,工业,质感"},
            {"name": "抽象", "tags": "抽象,abstract,意象,涂抹,肌理,艺术"},
            {"name": "几何", "tags": "几何,geometric,图形,对称,秩序,规律"},
            {"name": "摄影", "tags": "摄影,photo,实景,纪实,大片,真实"},

            # 特殊风格 (16-23)
            {"name": "大标题", "tags": "大标题,bold,巨型文字,强对比,信息焦点,醒目"},
            {"name": "拼贴", "tags": "拼贴,collage,叠加,剪影,复合,创意"},
            {"name": "粉彩", "tags": "粉彩,pastel,浅色,柔和,少女感,温柔"},
            {"name": "自然", "tags": "自然,nature,木纹,植物,有机,环保"},
            {"name": "色块", "tags": "色块,color block,大面积,版面,对比,鲜明"},
            {"name": "单色", "tags": "单色,monochrome,同色系,统一,纯净,简约"},
            {"name": "黑白高对比", "tags": "黑白,高对比,mono,硬朗,极致明暗,经典"},
            {"name": "极繁", "tags": "极繁,maximalism,复杂,堆叠,强烈装饰,丰富"},
        ]

        styles = []
        for s in styles_data:
            style, _ = Style.objects.get_or_create(
                name=s["name"],
                defaults={
                    "tags": s["tags"],
                    "reference_images": [],
                    "is_active": True,
                },
            )
            styles.append(style)
        return styles

    def create_poster_types_with_verified_relations(self, scenes, styles):
        """创建海报类型及建立严格验证的多对多关系"""

        # 海报类型数据 - 根据实际模型字段调整
        poster_types_data = [
            {
                "name": "商业广告",
                "tags": "商业,广告,宣传,营销,推广",
                "order": 100,
                "main_scene": "门店宣传",  # scene 字段（主推荐场景）
                "scene_names": ["门店宣传", "电商促销", "新品发布", "品牌形象", "限时折扣", "招商合作", "汽车促销"],
                "style_names": ["极简", "商务", "时尚", "奢华", "扁平", "摄影", "大标题", "色块"]
            },
            {
                "name": "招聘海报",
                "tags": "招聘,人事,职位,人才,求职",
                "order": 90,
                "main_scene": "招聘海报",
                "scene_names": ["招聘海报", "校园活动", "课程招生"],
                "style_names": ["极简", "商务", "扁平", "摄影", "单色"]
            },
            {
                "name": "餐饮美食",
                "tags": "餐饮,美食,菜单,食品,饮品",
                "order": 95,
                "main_scene": "菜单海报",
                "scene_names": ["门店宣传", "菜单海报", "餐饮优惠", "咖啡新品", "限时折扣"],
                "style_names": ["温馨", "手绘", "摄影", "自然", "粉彩", "色块"]
            },
            {
                "name": "活动宣传",
                "tags": "活动,宣传,预热,报名,聚会",
                "order": 85,
                "main_scene": "活动预热",
                "scene_names": ["活动预热", "线下活动报名", "社区活动", "校园活动", "演出海报", "音乐会", "运动赛事"],
                "style_names": ["时尚", "扁平", "渐变", "霓虹", "大标题", "拼贴", "色块"]
            },
            {
                "name": "节日祝福",
                "tags": "节日,祝福,贺卡,节庆,庆典",
                "order": 80,
                "main_scene": "节日祝福",
                "scene_names": ["节日祝福", "社交分享", "社区活动", "开业海报"],
                "style_names": ["温馨", "卡通", "手绘", "渐变", "粉彩", "自然"]
            },
            {
                "name": "新品发布",
                "tags": "新品,发布,上新,产品,展示",
                "order": 85,
                "main_scene": "新品发布",
                "scene_names": ["新品发布", "电商促销", "咖啡新品", "品牌形象"],
                "style_names": ["科技", "时尚", "奢华", "金属", "摄影", "大标题"]
            },
            {
                "name": "会员营销",
                "tags": "会员,营销,权益,积分,福利",
                "order": 70,
                "main_scene": "会员招募",
                "scene_names": ["会员招募", "电商促销", "限时折扣"],
                "style_names": ["商务", "时尚", "奢华", "大标题", "色块"]
            },
            {
                "name": "公告通知",
                "tags": "公告,通知,告示,提示,信息",
                "order": 60,
                "main_scene": "公告通知",
                "scene_names": ["公告通知", "温馨提示", "安全提示", "医疗门诊通知", "会议日程"],
                "style_names": ["极简", "商务", "扁平", "几何", "大标题", "单色", "黑白高对比"]
            },
            {
                "name": "社交媒体",
                "tags": "社交,媒体,分享,朋友圈,互动",
                "order": 85,
                "main_scene": "社交分享",
                "scene_names": ["社交分享", "新品发布", "节日祝福", "活动预热", "旅游推广"],
                "style_names": ["极简", "复古", "时尚", "卡通", "手绘", "渐变", "拼贴", "粉彩"]
            },
            {
                "name": "教育培训",
                "tags": "教育,培训,课程,招生,学习",
                "order": 75,
                "main_scene": "课程招生",
                "scene_names": ["课程招生", "校园活动", "公告通知"],
                "style_names": ["极简", "商务", "扁平", "几何", "色块"]
            },
            {
                "name": "美容美业",
                "tags": "美容,美业,美发,护肤,保养",
                "order": 70,
                "main_scene": "美业促销",
                "scene_names": ["门店宣传", "新品发布", "美业促销", "限时折扣"],
                "style_names": ["时尚", "温馨", "渐变", "粉彩", "自然"]
            },
            {
                "name": "健康医疗",
                "tags": "健康,医疗,养生,保健,科普",
                "order": 60,
                "main_scene": "医疗门诊通知",
                "scene_names": ["医疗门诊通知", "药店健康科普", "温馨提示", "健身团课"],
                "style_names": ["极简", "商务", "扁平", "自然", "单色"]
            },
            {
                "name": "运动健身",
                "tags": "运动,健身,赛事,体育,锻炼",
                "order": 65,
                "main_scene": "运动赛事",
                "scene_names": ["运动赛事", "健身团课", "活动预热", "线下活动报名"],
                "style_names": ["时尚", "扁平", "渐变", "霓虹", "摄影", "色块"]
            },
            {
                "name": "旅游度假",
                "tags": "旅游,度假,景点,出行,攻略",
                "order": 70,
                "main_scene": "旅游推广",
                "scene_names": ["旅游推广", "社交分享", "活动预热"],
                "style_names": ["复古", "温馨", "手绘", "摄影", "自然"]
            },
            {
                "name": "寻物启事",
                "tags": "寻物,丢失,启事,失物,寻找",
                "order": 50,
                "main_scene": "寻物启事",
                "scene_names": ["寻物启事", "招领启事"],
                "style_names": ["极简", "扁平", "大标题", "黑白高对比"]
            }
        ]

        poster_types = []
        for pt_data in poster_types_data:
            # 1. 找到主推荐场景
            main_scene = None
            try:
                main_scene = next(s for s in scenes if s.name == pt_data["main_scene"])
            except StopIteration:
                self.stdout.write(
                    self.style.WARNING(
                        f"Main scene '{pt_data['main_scene']}' not found for PosterType '{pt_data['name']}'")
                )

            # 2. 创建海报类型
            poster_type, created = PosterType.objects.get_or_create(
                name=pt_data["name"],
                defaults={
                    "tags": pt_data["tags"],
                    "order": pt_data["order"],
                    "scene": main_scene,  # 设置主推荐场景
                    "is_active": True,
                }
            )

            # 3. 如果是更新现有记录，也要更新主场景
            if not created:
                poster_type.scene = main_scene
                poster_type.tags = pt_data["tags"]
                poster_type.order = pt_data["order"]
                poster_type.save()
                # 清除现有多对多关系
                poster_type.scenes.clear()
                poster_type.styles.clear()

            # 4. 设置多场景关联（通过名称匹配，确保准确性）
            for scene_name in pt_data["scene_names"]:
                try:
                    scene = next(s for s in scenes if s.name == scene_name)
                    poster_type.scenes.add(scene)
                except StopIteration:
                    self.stdout.write(
                        self.style.WARNING(f"Scene '{scene_name}' not found for PosterType '{pt_data['name']}'")
                    )

            # 5. 设置风格关联（通过名称匹配，确保准确性）
            for style_name in pt_data["style_names"]:
                try:
                    style = next(s for s in styles if s.name == style_name)
                    poster_type.styles.add(style)
                except StopIteration:
                    self.stdout.write(
                        self.style.WARNING(f"Style '{style_name}' not found for PosterType '{pt_data['name']}'")
                    )

            poster_types.append(poster_type)

        return poster_types

    def verify_relationships(self):
        """验证多对多关系的完整性"""
        self.stdout.write("Verifying relationships...")

        poster_types = PosterType.objects.all()
        for pt in poster_types:
            scene_count = pt.scenes.count()
            style_count = pt.styles.count()
            main_scene = pt.scene.name if pt.scene else "None"

            if scene_count == 0:
                self.stdout.write(
                    self.style.WARNING(f"PosterType '{pt.name}' has no scenes associated!")
                )

            if style_count == 0:
                self.stdout.write(
                    self.style.WARNING(f"PosterType '{pt.name}' has no styles associated!")
                )

            self.stdout.write(
                f"PosterType '{pt.name}': main_scene='{main_scene}', {scene_count} scenes, {style_count} styles")

        self.stdout.write("Relationship verification completed.")