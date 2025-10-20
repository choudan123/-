import os, uuid
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.core.files.storage import default_storage

class PosterImageUploadView(APIView):
    """
    上传参考图片（与头像区分）
    支持匿名或已登录；若需强制登录改为 IsAuthenticated
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        file = request.FILES.get('file')
        if not file:
            return Response({'error': '未收到文件'}, status=status.HTTP_400_BAD_REQUEST)

        allowed = {'image/jpeg', 'image/png', 'image/webp', 'image/gif'}
        if file.content_type not in allowed:
            return Response({'error': '仅支持 JPG/PNG/WEBP/GIF'}, status=status.HTTP_400_BAD_REQUEST)

        # 保存路径：media/posters/<uuid>.<ext>
        _, ext = os.path.splitext(file.name)
        ext = (ext or '.jpg').lower()
        rel_path = f'posters/{uuid.uuid4().hex}{ext}'
        saved_path = default_storage.save(rel_path, file)
        url = request.build_absolute_uri(
            os.path.join(settings.MEDIA_URL, saved_path).replace('\\', '/')
        )
        return Response({'image_url': url}, status=status.HTTP_201_CREATED)