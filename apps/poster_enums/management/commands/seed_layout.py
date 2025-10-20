from django.core.management.base import BaseCommand
from django.db import transaction
from apps.poster_enums.models import Layout

class Command(BaseCommand):
    help = "Seed about 20 layouts into the 'poster_enums_layout' table. Descriptions are strictly feature/visual style only."

    @transaction.atomic
    def handle(self, *args, **options):
        layouts = [
            {"name": "对称", "layout_type": "symmetry", "description": "中心轴两侧元素均衡分布，稳定庄重"},
            {"name": "网格", "layout_type": "grid", "description": "规则的横纵分割，内容整齐排列"},
            {"name": "Z型", "layout_type": "z-shape", "description": "元素沿Z字轨迹分布，强烈引导视线流动"},
            {"name": "F型", "layout_type": "f-shape", "description": "上方横向分布，左侧纵向分布，信息层级分明"},
            {"name": "三栏", "layout_type": "three-column", "description": "页面分为三等分，便于多组内容展示"},
            {"name": "左右分栏", "layout_type": "split", "description": "左侧与右侧内容分离，结构清晰"},
            {"name": "上下分栏", "layout_type": "vertical-split", "description": "上部与下部分区，突出层次关系"},
            {"name": "居中", "layout_type": "centered", "description": "主要元素居于中央，突出视觉焦点"},
            {"name": "环绕", "layout_type": "wrap", "description": "元素围绕主图或主标题分布，形成包围感"},
            {"name": "斜线", "layout_type": "diagonal", "description": "元素沿斜线排列，动态流动"},
            {"name": "圆形", "layout_type": "circle", "description": "内容环绕圆心分布，形成圆形视觉"},
            {"name": "网状", "layout_type": "mesh", "description": "多点分布连接，形成网络状结构"},
            {"name": "自由", "layout_type": "freeform", "description": "元素随意排布，无固定规则"},
            {"name": "拼贴", "layout_type": "collage", "description": "多图或多块内容组合，丰富层次"},
            {"name": "卡片", "layout_type": "card", "description": "内容以卡片形式分组排列，模块化展示"},
            {"name": "流式", "layout_type": "flow", "description": "元素按方向自然流动，形成连续轨迹"},
            {"name": "阶梯", "layout_type": "stair", "description": "元素逐级排列，呈阶梯状层次"},
            {"name": "对角线分割", "layout_type": "diagonal-split", "description": "页面以对角线切分，形成强烈区域对比"},
            {"name": "黄金分割", "layout_type": "golden-ratio", "description": "页面按照黄金比例分区，比例协调"},
            {"name": "边框式", "layout_type": "border", "description": "元素分布于边缘，形成包围框结构"},
        ]

        for l in layouts:
            Layout.objects.get_or_create(
                name=l["name"],
                defaults={
                    "layout_type": l["layout_type"],
                    "description": l["description"],
                    "is_active": True,
                },
            )

        self.stdout.write(self.style.SUCCESS("20 layouts with strict feature descriptions have been seeded!"))