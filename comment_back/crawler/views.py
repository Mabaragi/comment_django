from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.serializers import ModelSerializer
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.permissions import AllowAny
from django.db.models import Model
from typing import Any

from .models import Series
from .serializers import *
from .crawler.selenium_crawler import get_title_with_selenium
from .crawler.crawler import (
    get_all_episodes_by_series,
    get_episode_count_by_series,
    get_comment_count_by_episode,
    get_comments_by_episode,
)


def validate_and_separate_data(
    data: list[dict[str, Any]], serializer_class: type[ModelSerializer]
) -> tuple[list[Model], list[dict[str, Any]], list[dict[str, Any]]]:
    """
    주어진 데이터 리스트를 검증하고 유효한 데이터와 유효하지 않은 데이터를 분리합니다.

    Args:
        data (List[Dict[str, Any]]): 검증할 데이터 리스트.
        serializer_class (Type[ModelSerializer]): 데이터를 검증할 직렬화 클래스.

    Returns:
        Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
            유효한 데이터 리스트와 유효하지 않은 데이터 리스트.
    """
    valid_instances, valid_data, invalid_data = [], [], []
    model = serializer_class.Meta.model  # type: ignore
    for item in data:
        # print(item)
        serializer = serializer_class(data=item)
        if serializer.is_valid():
            valid_instances.append(model(**serializer.validated_data))  # type: ignore
            valid_data.append(serializer.data)
        else:
            invalid_data.append({"data": item, "errors": serializer.errors})
    return valid_instances, valid_data, invalid_data


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
    def get(self, request: Request) -> Response:
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
    def get(self, request: Request) -> Response:
        series = Series.objects.all()
        serializer = SeriesSerializer(series, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="Create a series",
        request_body=SeriesCreateSerializer,  # Serializer를 직접 사용
        responses={200: SeriesSerializer},  # 응답 스키마 표시
    )
    def post(self, request: Request) -> Response:
        serializer = SeriesCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        series_id = serializer.validated_data[  # type: ignore
            "id"
        ]  # is_valid를 하면 validated_data attr가 생김.
        user = request.user

        try:
            title, image_src = get_title_with_selenium(series_id=series_id).values()
        except Exception as e:
            return Response(
                {"error": str(e), "message": "시리즈를 가져오는데 실패했습니다."},
                status=500,
            )

        serializer = SeriesSerializer(
            data={
                "id": series_id,
                "title": title,
                "image_src": image_src,
                "user": user.id,
            }
        )
        if serializer.is_valid(raise_exception=True):
            serializer.save()
        return Response(
            {"message": "Series created successfully", "data": serializer.data},
            status=200,
        )


class SeriesDetailView(APIView):
    @swagger_auto_schema(
        operation_description="Retrieve a series by ID",
        responses={
            200: SeriesSerializer,
            404: "Not Found",
        },  # Swagger에 응답 스키마 표시
    )
    def get(self, request: Request, series_id: int) -> Response:
        try:
            series = Series.objects.get(id=series_id)
        except Series.DoesNotExist:
            return Response({"error": "Series not found"}, status=404)

        serializer = SeriesSerializer(series)
        return Response(serializer.data)


class EpisodeCrawlView(APIView):
    @swagger_auto_schema(
        operation_description="특정 시리즈의 에피소드를 보여줍니다.",
        responses={200: EpisodeSerializer(many=True)},  # Swagger에 응답 스키마 표시
    )
    def get(self, request: Request, series_id: int) -> Response:
        episodes = Episode.objects.filter(series=series_id)
        serializer = EpisodeSerializer(episodes, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="에피소드를 크롤링하여 db에 저장합니다.",
        responses={
            207: EpisodeCreateResponseSerializer(),  # 상태 코드 207 사용
        },
    )
    def post(self, request: Request, series_id: int) -> Response:

        episode_count = get_episode_count_by_series(series_id=series_id)
        if episode_count <= Episode.objects.filter(series=series_id).count():
            return Response({"message": "에피소드를 크롤링할 필요가 없습니다."})

        user = request.user
        try:
            data = [
                {**item, "user": user.id}
                for item in get_all_episodes_by_series(series_id=series_id)
            ]
        except Exception as e:
            return Response(
                {"error": str(e), "message": "에피소드를 가져오는데 실패했습니다."},
                status=500,
            )

        valid_instances, valid_data, invalid_data = validate_and_separate_data(
            data, EpisodeSerializer
        )
        if valid_instances:
            Episode.objects.bulk_create(valid_instances)  # type: ignore
        return Response(
            {"created_data": valid_data, "errors": invalid_data}, status=207
        )


class EpisodeListView(ListAPIView):
    """
    에피소드 목록을 조회하는 API 뷰입니다.
    """

    serializer_class = EpisodeSerializer
    request: Request

    def get_queryset(self):
        series_id = self.kwargs.get("series_id")
        fields_param = self.request.query_params.get("fields", None)
        if fields_param:
            fields = fields_param.split(",")
            return Episode.objects.filter(series=series_id).only(*fields)
        return Episode.objects.filter(series=series_id)

    def get_serializer(self, *args, **kwargs):
        fields_param = self.request.query_params.get("fields", None)
        if fields_param:
            fields = fields_param.split(",")
            kwargs["fields"] = fields
        return super().get_serializer(*args, **kwargs)

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                name="fields",
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                description="불러올 필드 이름을 쉼표로 구분하여 지정 (예: id,name,image_src)",
                required=False,
            )
        ]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class EpisodeDetailView(APIView):
    @swagger_auto_schema(
        operation_description="특정 시리즈의 에피소드를 조회합니다.",
        responses={
            200: EpisodeSerializer,
            404: "Not Found",
        },  # Swagger에 응답 스키마 표시
    )
    def get(self, request: Request, series_id: int, product_id: int) -> Response:
        try:
            episode = Episode.objects.get(series=series_id, id=product_id)
        except Episode.DoesNotExist:
            return Response({"error": "Episode not found"}, status=404)

        serializer = EpisodeSerializer(episode)
        return Response(serializer.data)


class CommentView(APIView):
    @swagger_auto_schema(
        operation_description="에피소드의 댓글을 조회합니다.",
        responses={
            200: CommentSerializer(),  # 상태 코드 207 사용
        },
    )
    def get(self, request: Request, series_id: int, product_id: int) -> Response:
        comments = Comment.objects.filter(series=series_id, episode=product_id)
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="에피소드의 댓글을 크롤링하여 db에 저장합니다.",
        responses={
            207: EpisodeCreateResponseSerializer(),  # 상태 코드 207 사용
        },
    )
    def post(self, request: Request, series_id: int, product_id: int) -> Response:
        comment_count = get_comment_count_by_episode(
            series_id=series_id, product_id=product_id
        )
        if comment_count <= Comment.objects.filter(id=product_id).count():
            return Response({"message": "댓글을 크롤링할 필요가 없습니다."})

        try:
            data = get_comments_by_episode(series_id=series_id, product_id=product_id)
        except Exception as e:
            return Response(
                {"error": str(e), "message": "댓글을 가져오는데 실패했습니다."}
            )

        valid_instances, valid_data, invalid_data = validate_and_separate_data(
            data, CommentSerializer
        )
        if valid_instances:
            Comment.objects.bulk_create(valid_instances)  # type: ignore
        return Response(
            {"created_data": valid_data, "errors": invalid_data}, status=207
        )
