from typing import List, Optional, Tuple
from itertools import chain

from apps.poster_enums.models import (
    Scene, PosterType, Style, Layout, Size, AspectRatio, ReferenceImage, Font
)


def _split_tags(s: Optional[str]) -> List[str]:
    if not s:
        return []
    return [t.strip() for t in s.split(",") if t.strip()]

def _uniq(seq: List[str]) -> List[str]:
    seen = set()
    out = []
    for x in seq:
        if x and x not in seen:
            seen.add(x)
            out.append(x)
    return out

def _size_spec(size: Optional[Size]) -> str:
    if not size:
        return ""
    w, h = size.width, size.height
    if not w or not h:
        return size.name
    orient = "竖版" if h >= w else "横版"
    from math import gcd
    g = gcd(w, h) or 1
    ratio = f"{w // g}:{h // g}"
    return f"{size.name or f'{w}×{h}px'}（{w}×{h}px，{orient}，约{ratio}）"

def _ratio_spec(r: Optional[AspectRatio]) -> str:
    if not r:
        return ""
    return f"{r.name}"

def build_prompt(
    *,
    scene: Optional[Scene] = None,
    ptype: Optional[PosterType] = None,
    style: Optional[Style] = None,
    main_color: Optional[str] = None,
    palette: Optional[List[str]] = None,
    title: Optional[str] = None,
    keywords: Optional[List[str]] = None,
    negative_keywords: Optional[List[str]] = None,
    layout: Optional[Layout] = None,
    reference_images: Optional[List[ReferenceImage]] = None,
    font: Optional[Font] = None,
    size: Size,
    aspect_ratio: AspectRatio,
    include_quality_hints: bool = True,
    include_default_negative: bool = True,
) -> Tuple[str, str]:
    scene_words = _uniq(([scene.name] if scene else []) + _split_tags(getattr(scene, "tags", None) if scene else ""))
    type_words = _uniq(([ptype.name] if ptype else []) + _split_tags(getattr(ptype, "tags", None) if ptype else ""))
    style_words = _uniq(([style.name] if style else []) + _split_tags(getattr(style, "tags", None) if style else ""))
    user_words = _uniq(keywords or [])

    color_parts = []
    if main_color:
        color_parts.append(f"主色调 {main_color}")
    if palette:
        color_parts.append(f"辅助色 {', '.join(palette)}")
    color_text = "；".join(color_parts) if color_parts else ""

    layout_text = ""
    if layout:
        layout_bits = [layout.name]
        if getattr(layout, "layout_type", None):
            layout_bits.append(layout.layout_type)
        if layout.description:
            layout_bits.append(layout.description)
        layout_text = "；".join(_uniq(layout_bits))

    size_text = _size_spec(size)
    ratio_text = _ratio_spec(aspect_ratio)

    ref_urls = [ri.image_url for ri in (reference_images or []) if ri and ri.image_url]
    ref_text = f"参考图：{', '.join(ref_urls)}" if ref_urls else ""
    font_text = f"字体：{font.name}（{font.category}）" if font and font.category else (f"字体：{font.name}" if font else "")

    if scene and ptype:
        context_text = f"{scene.name} 场景的 {ptype.name} 海报"
    elif scene and not ptype:
        context_text = f"{scene.name} 场景海报"
    elif ptype and not scene:
        context_text = f"{ptype.name} 海报"
    else:
        context_text = "海报"

    parts = [context_text]
    if style:
        parts.append(f"风格：{style.name}")

    kw_all = _uniq(list(chain(scene_words, type_words, style_words, user_words)))
    if kw_all:
        parts.append(f"主题关键词：{', '.join(kw_all)}")

    if title:
        parts.insert(0, f"标题：{title}")
    if color_text:
        parts.append(f"色彩方案：{color_text}")
    if layout_text:
        parts.append(f"布局：{layout_text}")
    if size_text:
        parts.append(f"画布尺寸：{size_text}")
    if ratio_text:
        parts.append(f"画面比例：{ratio_text}")
    if font_text:
        parts.append(font_text)
    if ref_text:
        parts.append(ref_text)

    if include_quality_hints:
        parts.append("清晰、对比强、版式平衡、层级明确、适配社交分享与打印")

    prompt = "；".join([p for p in parts if p])

    neg_base: List[str] = []
    if include_default_negative:
        neg_base = [
            "低质量", "模糊", "过曝", "欠曝", "失焦", "噪点",
            "拉伸变形", "比例错误", "拼写错误", "水印", "严重压缩痕迹",
        ]
    if negative_keywords:
        neg_base.extend(negative_keywords)
    negative_prompt = ", ".join(_uniq(neg_base))

    return prompt, negative_prompt