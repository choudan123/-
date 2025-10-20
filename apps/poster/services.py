import os
from typing import Any, Dict, List, Optional

from volcenginesdkarkruntime import Ark
from volcenginesdkarkruntime.types.images.images import SequentialImageGenerationOptions

# 可配置
ARK_BASE_URL = os.environ.get("ARK_BASE_URL", "https://ark.cn-beijing.volces.com/api/v3")
ARK_MODEL = os.environ.get("ARK_IMAGE_MODEL", "doubao-seedream-4-0-250828")

_ark_client: Optional[Ark] = None  # 懒加载全局缓存


def _get_api_key() -> str:
    key = os.environ.get("ARK_API_KEY") or os.environ.get("API_KEY")
    if not key:
        raise RuntimeError("未找到方舟 API Key。请设置 ARK_API_KEY（或兼容 API_KEY）")
    return key


def _get_ark_client() -> Ark:
    global _ark_client
    if _ark_client is None:
        _ark_client = Ark(base_url=ARK_BASE_URL, api_key=_get_api_key())
    return _ark_client


def generate_poster(
    *,
    prompt: str,
    size: str,
    image: Optional[str] = None,           # 单一参考图
    images: Optional[List[str]] = None,     # 多参考图
    sequential_image_generation: str = "disabled",  # "disabled" | "auto"
    sequential_image_generation_options: Optional[Dict[str, Any]] = None,  # {"max_images": int} 仅为“上限”
    response_format: str = "url",
    watermark: bool = False,
    stream: Optional[bool] = None,
) -> Dict[str, Any]:
    """
    调用方舟 /images/generations 生成图片。
    - single: sequential_image_generation = "disabled"（模型输出 1 张）
    - group : sequential_image_generation = "auto"；输出张数由“提示词语义”决定，
              sequential_image_generation_options.max_images 仅作为上限（cap），非精确数量。
    返回:
      { "success": bool, "urls": [str], "sizes": [str], "error"?: str }
    """
    client = _get_ark_client()

    kwargs: Dict[str, Any] = {
        "model": ARK_MODEL,
        "prompt": prompt,
        "size": size,
        "response_format": response_format,
        "watermark": watermark,
        "sequential_image_generation": sequential_image_generation or "disabled",
    }

    # Ark 的字段名是 image，可以是字符串或数组；SDK 允许统一传入 image
    if images:
        kwargs["image"] = images
    elif image:
        kwargs["image"] = image

    if sequential_image_generation == "auto" and sequential_image_generation_options:
        max_images = int(sequential_image_generation_options.get("max_images", 0))
        if max_images > 0:
            kwargs["sequential_image_generation_options"] = SequentialImageGenerationOptions(max_images=max_images)

    if stream is not None:
        kwargs["stream"] = stream

    try:
        images_response = client.images.generate(**kwargs)
        return {
            "success": True,
            "urls": [getattr(img, "url", None) for img in images_response.data],
            "sizes": [getattr(img, "size", None) for img in images_response.data],
        }
    except Exception as e:
        return {"success": False, "error": str(e), "urls": []}