from typing import Dict, List, Tuple, Optional, Set
from datetime import timedelta
import random

from django.db.models import Sum, Count, Q
from django.utils import timezone
from django.core.cache import cache

from apps.poster_enums.models import PosterType, Style, Scene
from .models import SceneTypeStyleStat, PosterEvent

CACHE_TTL = 300  # 秒


def _normalize(scores: Dict[int, float]) -> Dict[int, float]:
    if not scores:
        return {}
    mx = max(scores.values())
    if mx <= 0:
        return {k: 0.0 for k in scores}
    return {k: v / mx for k, v in scores.items()}


def _jaccard(a: Optional[str], b: Optional[str]) -> float:
    if not a or not b:
        return 0.0
    A = {x.strip() for x in a.split(',') if x.strip()}
    B = {x.strip() for x in b.split(',') if x.strip()}
    if not A and not B:
        return 0.0
    return len(A & B) / max(1, len(A | B))


def _diversify_results(candidates: List[Tuple], diversity_factor=0.3) -> List[Tuple]:
    """
    增加推荐结果的多样性
    diversity_factor: 多样性权重 (0-1)，0表示完全按分数排序，1表示完全随机
    """
    if len(candidates) <= 2:
        return candidates

    # 分离高分和低分候选
    sorted_candidates = sorted(candidates, key=lambda x: x[1], reverse=True)
    top_score = sorted_candidates[0][1] if sorted_candidates else 0

    # 保证前2个一定是高分的
    guaranteed = sorted_candidates[:2]
    remaining = sorted_candidates[2:]

    if not remaining:
        return guaranteed

    # 对剩余的进行多样性选择
    diversified = []
    selected_tags: Set[str] = set()

    # 收集已选择项目的标签
    for item, score in guaranteed:
        if hasattr(item, 'tags') and item.tags:
            selected_tags.update(tag.strip() for tag in item.tags.split(',') if tag.strip())

    for item, score in remaining:
        # 计算多样性分数
        item_tags = set()
        if hasattr(item, 'tags') and item.tags:
            item_tags = {tag.strip() for tag in item.tags.split(',') if tag.strip()}

        # 标签重叠度 (越低越好)
        if selected_tags and item_tags:
            overlap = len(selected_tags & item_tags) / len(selected_tags | item_tags)
        else:
            overlap = 0.0

        # 多样性分数 = 原始分数 * (1 - diversity_factor * overlap)
        diversity_bonus = 1 - diversity_factor * overlap
        final_score = score * diversity_bonus

        diversified.append((item, final_score, score))  # 保留原始分数用于显示

        # 更新已选择的标签
        selected_tags.update(item_tags)

    # 按新分数排序
    diversified.sort(key=lambda x: x[1], reverse=True)

    # 合并结果，保留原始分数格式
    result = guaranteed + [(item, original_score) for item, _, original_score in diversified]

    return result


def recommend_types_for_scene(scene_id: int, user_id: Optional[int], top_n=6, alpha=0.7, diversity_factor=0.3) -> List[
    Tuple[PosterType, float]]:
    """
    类型推荐（支持多场景 PosterType.scenes）：
    - 全局：基于 SceneTypeStyleStat 的 decayed_score 按 type 聚合
    - 个性化：用户在该场景历史事件计数（近90天）
    - 多样性：避免推荐结果过于集中
    - 冷启动兜底：优先匹配多对多 scenes；其次单场景 scene；最后无绑定场景
    """
    cache_key = f"rec:types:s{scene_id}:u{user_id or 0}:n{top_n}:a{alpha}:d{diversity_factor}"
    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    # 全局热度（强制 dict 行）
    global_rows = (
        SceneTypeStyleStat.objects
        .filter(scene_id=scene_id, poster_type__is_active=True)
        .values('poster_type_id')
        .annotate(score=Sum('decayed_score'))
        .values('poster_type_id', 'score')
        .order_by('-score')
    )
    global_scores = {r['poster_type_id']: float(r['score'] or 0.0) for r in global_rows}
    global_scores = _normalize(global_scores)

    # 用户偏好（近90天，强制 dict 行）
    user_scores: Dict[int, float] = {}
    if user_id:
        since = timezone.now() - timedelta(days=90)
        q = (
            PosterEvent.objects
            .filter(scene_id=scene_id, user_id=user_id, poster_type__isnull=False, created_at__gte=since)
            .values('poster_type_id')
            .annotate(cnt=Count('id'))
            .values('poster_type_id', 'cnt')
        )
        user_scores = {r['poster_type_id']: float(r['cnt']) for r in q}
        user_scores = _normalize(user_scores)

    fused: Dict[int, float] = {}
    ids = set(global_scores) | set(user_scores)
    for _id in ids:
        fused[_id] = alpha * global_scores.get(_id, 0.0) + (1 - alpha) * user_scores.get(_id, 0.0)

    if fused:
        # 获取更多候选，为多样性筛选做准备
        extended_top_n = min(top_n * 2, len(fused))
        top_ids = sorted(fused.keys(), key=lambda i: fused[i], reverse=True)[:extended_top_n]
        objs = {o.id: o for o in PosterType.objects.filter(id__in=top_ids)}
        candidates = [(objs[i], fused[i]) for i in top_ids if i in objs]

        # 应用多样性筛选
        diversified = _diversify_results(candidates, diversity_factor)[:top_n]

        cache.set(cache_key, diversified, CACHE_TTL)
        return diversified

    # 冷启动兜底
    qs = (
        PosterType.objects
        .filter(is_active=True)
        .filter(Q(scenes__id=scene_id) | Q(scene_id=scene_id) | Q(scenes__isnull=True, scene__isnull=True))
        .distinct()
        .order_by('order', 'id')[:top_n]
    )
    result = [(obj, 1.0 - i * 0.1) for i, obj in enumerate(qs)]
    cache.set(cache_key, result, CACHE_TTL)
    return result


def recommend_styles_for_scene_type(scene_id: int, type_id: int, user_id: Optional[int], top_n=6, alpha=0.7,
                                    diversity_factor=0.3) -> List[Tuple[Style, float]]:
    """
    风格推荐：
    - 若 PosterType.styles 已配置，仅在允许集合内排序
    - 全局：按 (scene, type) 聚合 decayed_score
    - 个性化：用户在该场景+类型下的历史偏好
    - 多样性：避免推荐结果过于集中
    - 冷启动兜底：用标签相似度，同样可限制在允许集合内
    """
    cache_key = f"rec:styles:s{scene_id}:t{type_id}:u{user_id or 0}:n{top_n}:a{alpha}:d{diversity_factor}"
    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    # 限定风格集合（若类型配置了 allowed styles）
    allowed_ids = list(
        Style.objects.filter(poster_types__id=type_id, is_active=True).values_list('id', flat=True)
    )

    # 全局热度（强制 dict 行）
    qset = SceneTypeStyleStat.objects.filter(scene_id=scene_id, poster_type_id=type_id)
    if allowed_ids:
        qset = qset.filter(style_id__in=allowed_ids)
    else:
        qset = qset.filter(style__is_active=True)

    global_rows = (
        qset.values('style_id')
        .annotate(score=Sum('decayed_score'))
        .values('style_id', 'score')
        .order_by('-score')
    )
    global_scores = {r['style_id']: float(r['score'] or 0.0) for r in global_rows}
    global_scores = _normalize(global_scores)

    # 用户偏好（近90天，强制 dict 行）
    user_scores: Dict[int, float] = {}
    if user_id:
        since = timezone.now() - timedelta(days=90)
        uq = (
            PosterEvent.objects
            .filter(scene_id=scene_id, poster_type_id=type_id, user_id=user_id, style__isnull=False,
                    created_at__gte=since)
            .values('style_id')
            .annotate(cnt=Count('id'))
            .values('style_id', 'cnt')
        )
        if allowed_ids:
            uq = uq.filter(style_id__in=allowed_ids)
        user_scores = {r['style_id']: float(r['cnt']) for r in uq}
        user_scores = _normalize(user_scores)

    fused: Dict[int, float] = {}
    ids = set(global_scores) | set(user_scores)
    for _id in ids:
        fused[_id] = alpha * global_scores.get(_id, 0.0) + (1 - alpha) * user_scores.get(_id, 0.0)

    if fused:
        # 获取更多候选，为多样性筛选做准备
        extended_top_n = min(top_n * 2, len(fused))
        top_ids = sorted(fused.keys(), key=lambda i: fused[i], reverse=True)[:extended_top_n]
        objs = {o.id: o for o in Style.objects.filter(id__in=top_ids)}
        candidates = [(objs[i], fused[i]) for i in top_ids if i in objs]

        # 应用多样性筛选
        diversified = _diversify_results(candidates, diversity_factor)[:top_n]

        cache.set(cache_key, diversified, CACHE_TTL)
        return diversified

    # 冷启动兜底：标签相似度
    scene = Scene.objects.filter(id=scene_id).only('tags').first()
    ptype = PosterType.objects.filter(id=type_id).only('tags', 'name').first()
    base_tag = ((scene.tags or '') if scene else '')
    base_tag = base_tag + ',' + ((ptype.tags or (ptype.name if ptype else '')))

    styles_qs = Style.objects.filter(is_active=True)
    if allowed_ids:
        styles_qs = styles_qs.filter(id__in=allowed_ids)

    scored = [(st, _jaccard(base_tag, st.tags)) for st in styles_qs.only('id', 'tags', 'name')]
    scored.sort(key=lambda x: x[1], reverse=True)

    # 对冷启动结果也应用多样性
    diversified = _diversify_results(scored, diversity_factor)[:top_n]

    cache.set(cache_key, diversified, CACHE_TTL)
    return diversified