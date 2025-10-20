from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework import status

from .serializers import LogEventSerializer, RecommendTypesQuery, RecommendStylesQuery
from .models import PosterEvent
from .services import recommend_types_for_scene, recommend_styles_for_scene_type

class LogEventView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def post(self, request):
        ser = LogEventSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        data = ser.validated_data
        PosterEvent.objects.create(
            user_id=(request.user.id if request.user.is_authenticated else None),
            scene_id=data.get('scene_id'),
            poster_type_id=data.get('poster_type_id'),
            style_id=data.get('style_id'),
            event=data['event'],
        )
        return Response({'ok': True}, status=status.HTTP_201_CREATED)

class RecommendTypesView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request):
        ser = RecommendTypesQuery(data=request.query_params)
        ser.is_valid(raise_exception=True)
        scene_id = ser.validated_data['scene_id']
        top_n = ser.validated_data['top_n']
        diversity_factor = float(request.query_params.get('diversity_factor', 0.3))
        user_id = request.user.id if request.user.is_authenticated else None

        pairs = recommend_types_for_scene(scene_id, user_id, top_n=top_n, diversity_factor=diversity_factor)
        data = [{'id': t.id, 'name': t.name, 'score': float(score)} for t, score in pairs]
        return Response({'results': data})

class RecommendStylesView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request):
        ser = RecommendStylesQuery(data=request.query_params)
        ser.is_valid(raise_exception=True)
        scene_id = ser.validated_data['scene_id']
        type_id = ser.validated_data['poster_type_id']
        top_n = ser.validated_data['top_n']
        diversity_factor = float(request.query_params.get('diversity_factor', 0.3))
        user_id = request.user.id if request.user.is_authenticated else None

        pairs = recommend_styles_for_scene_type(scene_id, type_id, user_id, top_n=top_n, diversity_factor=diversity_factor)
        data = [{'id': s.id, 'name': s.name, 'score': float(score)} for s, score in pairs]
        return Response({'results': data})