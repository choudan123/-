from django.db import models


class Scene(models.Model):
    """
    应用场景（如门店宣传、社交分享等）
    """
    name = models.CharField(max_length=50, unique=True, help_text="场景名称")
    icon = models.URLField(blank=True, null=True, help_text="场景图标URL")
    is_active = models.BooleanField(default=True, help_text="是否激活该场景")
    tags = models.CharField(max_length=100, blank=True, null=True, help_text="用于场景分组和检索的标签，逗号分隔")

    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=['is_active']),
            models.Index(fields=['name']),
        ]
        ordering = ['name']

    def __str__(self):
        return self.name


class Style(models.Model):
    """
    风格（如极简、复古、科技等）
    可配置参考图片，参与标签相似度与行为统计。
    """
    name = models.CharField(max_length=30, unique=True, help_text="风格名称")
    reference_images = models.JSONField(default=list, blank=True, help_text="风格参考图片URL列表（JSON 数组）")
    tags = models.CharField(max_length=100, blank=True, null=True, help_text="风格标签，逗号分隔")
    is_active = models.BooleanField(default=True, help_text="是否激活该风格")

    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=['is_active']),
            models.Index(fields=['name']),
        ]
        ordering = ['name']

    def __str__(self):
        return self.name


class PosterType(models.Model):
    """
    海报类型（如商业广告、招聘海报等）
    - scene: 主推荐场景（兼容旧逻辑，冷启动兜底）
    - scenes: 多场景挂载（一个类型可关联多个场景）
    - styles: 限定该类型允许的风格集合（用于过滤候选与提升推荐准确度）
    - tags: 冷启动时做标签相似度
    """
    name = models.CharField(max_length=50, unique=True, help_text="海报类型名称")

    # 兼容原有单场景字段（可保留作为主场景或后续迁移后移除）
    scene = models.ForeignKey(
        Scene, blank=True, null=True, on_delete=models.SET_NULL, help_text="主推荐关联场景（冷启动兜底用）"
    )

    # 多场景关联
    scenes = models.ManyToManyField(
        Scene, blank=True, related_name='poster_types', help_text="该类型关联的多个场景"
    )

    # 限定可用风格集合
    styles = models.ManyToManyField(
        Style, blank=True, related_name='poster_types', help_text="该类型可用的风格集合（用于过滤候选集）"
    )

    # 标签
    tags = models.CharField(max_length=100, blank=True, null=True, help_text="类型标签，逗号分隔（冷启动相似度用）")

    order = models.PositiveIntegerField(default=0, help_text="排序值")
    is_active = models.BooleanField(default=True, help_text="是否激活该类型")

    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=['is_active']),
            models.Index(fields=['order']),
            models.Index(fields=['name']),
        ]
        ordering = ['order', 'id']  # 先按排序值，再按主键保证稳定顺序

    def __str__(self):
        return self.name


class ColorScheme(models.Model):
    """
       仅存储常用主色调，便于前端快速选用。
    """
    name = models.CharField(max_length=30, unique=True, help_text="色彩名称")
    main_color = models.CharField(max_length=20, help_text="主色调HEX值")  # 必填
    preview_image = models.URLField(blank=True, null=True, help_text="色彩预览图片URL")
    order = models.PositiveIntegerField(default=0, help_text="排序值")
    is_active = models.BooleanField(default=True, help_text="是否激活该色彩方案")

    def __str__(self):
        return self.name

class Layout(models.Model):
    """
    布局结构（如对称、网格、Z型等）
    用于指导AI生成的海报版式。
    """
    name = models.CharField(
        max_length=30,
        unique=True,
        help_text="布局名称"
    )
    description = models.TextField(
        blank=True,
        null=True,
        help_text="布局描述"
    )
    layout_type = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        help_text="布局类型标签"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="是否激活该布局"
    )

    def __str__(self):
        return self.name

class Size(models.Model):
    """
    尺寸/输出像素
    """
    name = models.CharField(max_length=20, unique=True, help_text="尺寸规格")
    is_active = models.BooleanField(default=True, help_text="是否激活该尺寸")

    def __str__(self):
        return self.name


class AspectRatio(models.Model):
    """
    宽高比（如 1:1、4:3、16:9 等）
    仅用于业务上的比例选择与提示词描述；不直接传给 Ark。
    """
    name = models.CharField(max_length=20, unique=True, help_text="宽高比（如 1:1、4:3、16:9）")
    ratio_w = models.PositiveIntegerField(help_text="宽比（分子，例如 16:9 的 16）")
    ratio_h = models.PositiveIntegerField(help_text="高比（分母，例如 16:9 的 9）")
    is_active = models.BooleanField(default=True, help_text="是否激活该宽高比")

    def __str__(self):
        return f"{self.name} ({self.ratio_w}:{self.ratio_h})"


class Font(models.Model):
    """
    字体/文字风格（如衬线、无衬线、手写等）
    前端应提供直观选择（如字体预览卡片），也允许用户自定义输入字体名称。
    """
    name = models.CharField(
        max_length=50,
        unique=True,
        help_text="字体名称"
    )
    category = models.CharField(
        max_length=30,
        blank=True,
        null=True,
        help_text="字体类别标签"
    )
    demo_image = models.URLField(
        blank=True,
        null=True,
        help_text="字体示例图片URL"
    )
    is_system = models.BooleanField(
        default=False,
        help_text="系统常用字体（前端常用推荐）"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="是否激活该字体"
    )

    def __str__(self):
        return self.name


class ReferenceImage(models.Model):
    """
    系统预设图片供选用（如风格参考图、素材库）
    用户可直接选择，也可结合风格、标签筛选。
    """
    name = models.CharField(
        max_length=50,
        help_text="图片名称"
    )
    image_url = models.URLField(
        help_text="图片URL"
    )
    tags = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="图片标签分组"
    )
    style = models.ForeignKey(
        Style,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        help_text="关联风格"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="是否激活该图片"
    )

    def __str__(self):
        return self.name