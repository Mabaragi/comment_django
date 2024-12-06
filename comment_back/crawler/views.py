from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.views import APIView
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.permissions import AllowAny

from .models import Series
from .serializers import SeriesSerializer
from .crawler.selenium_crawler import get_title_with_selenium


class SeriesListView(APIView):
    # permission_classes = [AllowAny]
    @swagger_auto_schema(
        operation_description="Retrieve a list of users",
        # request_body=openapi.Schema(
        #     type=openapi.TYPE_OBJECT,
        #     properties={
        #         'user_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='User ID'),
        #     },
        # ),
        responses={200: SeriesSerializer(many=True)},  # Swagger에 응답 스키마 표시
    )
    def get(self, request:Request) -> Response:
        series = Series.objects.all()
        serializer = SeriesSerializer(series, many=True)
        return Response(serializer.data)
    
class SeriesView(APIView):

    @swagger_auto_schema(
        operation_description="Retrieve a list of users",
        # request_body=openapi.Schema(
        #     type=openapi.TYPE_OBJECT,
        #     properties={
        #         'user_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='User ID'),
        #     },
        # ),
        responses={200: SeriesSerializer(many=True)},  # Swagger에 응답 스키마 표시
    )
    def get(self, request:Request) -> Response:
        series = Series.objects.all()
        serializer = SeriesSerializer(series, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="Retrieve a list of users",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'series_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='시리즈 id'),
            },
        ),
        responses={200: SeriesSerializer(many=True)},  # Swagger에 응답 스키마 표시
    )
    def post(self, request:Request) -> Response:
        series_id = request.data.get('series_id')
        if not series_id:
            return Response({'error': 'series_id is required'}, status=400)
        
        user = request.user
        if Series.objects.filter(series_id=series_id).exists():
            series = Series.objects.get(series_id=series_id)
            serializer = SeriesSerializer(series)
            return Response({'message': 'Series already exists', 'data': serializer.data}, status=200)
        
        
        try:
            title, image_src = get_title_with_selenium(series_id=series_id).values()
        except Exception as e:
            return Response({'error': str(e), 'message': '시리즈를 가져오는데 실패했습니다.'})

        series = Series.objects.create(
            series_id=series_id,
            title=title,
            image_src=image_src,
            user=user
        )


        serializer = SeriesSerializer(series)
        return Response({'message': 'Series created successfully', 'data': serializer.data}, status=200)