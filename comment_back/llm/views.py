from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from .serializers import CommentEmotionAnalysisSerializer, CommentsSummarySerializer
from rest_framework.request import Request
from rest_framework.response import Response  # 추가
from rest_framework import status  # 추가
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import CommentAnalysisResult, CommentsSummaryResult
from crawler.models import Comment, Episode
from rest_framework.generics import DestroyAPIView
from rest_framework.permissions import AllowAny
from utils.swagger import (
    get_fields_query_parameter,
    get_path_parameter,
    DEFAULT_EPISODE_ID,
)

# Create your views here.


class CommentEmotionAnalysisView(APIView):
    """
    View for analyzing the emotion of comments.

    Possible responses:
        - 201 Created: Emotion analysis was successful.
        - 400 Bad Request: Invalid input data.
    """

    @swagger_auto_schema(
        operation_description="댓글 감정 분석 결과 조회",
        manual_parameters=[
            openapi.Parameter(
                "comment_id",
                openapi.IN_PATH,
                description="조회할 댓글의 ID",
                type=openapi.TYPE_INTEGER,
                required=True,
                default=165999266,
            ),
        ],
        responses={200: CommentEmotionAnalysisSerializer(), 404: "Not Found"},
    )
    def get(self, request: Request, comment_id: int):
        """
        Retrieve the emotion analysis result for a specific comment.
        """
        analysis_result = get_object_or_404(
            CommentAnalysisResult, comment_id=comment_id
        )
        serializer = CommentEmotionAnalysisSerializer(analysis_result)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_description="댓글 감정 분석 요청",
        manual_parameters=[
            get_path_parameter(
                "comment_id",
                description="분석할 댓글의 ID",
                default=165999266,
            ),
        ],
        responses={201: CommentEmotionAnalysisSerializer(), 400: "Bad Request"},
    )
    def post(self, request: Request, comment_id: int):
        comment = get_object_or_404(Comment, id=comment_id)
        data = {"comment": comment.id}  # Pass only comment_id
        serializer = CommentEmotionAnalysisSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CommentAnalysisResultDestroyView(DestroyAPIView):
    """
    댓글 감정 분석 결과를 삭제하는 API 뷰입니다.
    """

    queryset = CommentAnalysisResult.objects.all()
    serializer_class = CommentEmotionAnalysisSerializer
    lookup_field = "comment_id"

    @swagger_auto_schema(
        operation_description="댓글 감정 분석 결과 삭제",
        manual_parameters=[
            get_path_parameter(
                "comment_id",
                description="삭제할 댓글의 ID",
                default=165999266,
            ),
        ],
        responses={
            204: "삭제 성공 (No Content)",
            404: "Not Found",
        },
    )
    def delete(self, request, comment_id, *args, **kwargs):
        return super().delete(request, comment_id=comment_id, *args, **kwargs)


class CommentsSummaryResultView(APIView):
    """
    댓글 감정 분석 결과 요약을 조회하는 API 뷰입니다.
    """

    @swagger_auto_schema(
        operation_description="댓글 요약 생성",
        manual_parameters=[
            get_path_parameter(
                "episode_id",
                description="에피소드의 ID",
                default=DEFAULT_EPISODE_ID,
            ),
        ],
        responses={200: CommentsSummarySerializer(many=True), 404: "Not Found"},
    )
    def post(self, request: Request, episode_id: int):
        """
        Create a summary of comment emotion analysis results.
        """
        get_object_or_404(Episode, id=episode_id)
        comments = (
            Comment.objects.filter(episode=episode_id)
            .order_by("-created_at")
            .values_list("id", "content", "is_best")
        )
        source_comments = [
            {"id": comment[0], "content": comment[1], "is_best": comment[2]}
            for comment in comments
        ]
        data = {
            "episode": episode_id,
            "source_comments": source_comments,  # 댓글 ID 목록을 전달
        }
        serializer = CommentsSummarySerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="댓글 요약 조회",
        manual_parameters=[
            get_path_parameter(
                "episode_id",
                description="에피소드의 ID",
                default=DEFAULT_EPISODE_ID,
            ),
        ],
        responses={200: CommentsSummarySerializer(many=True), 404: "Not Found"},
    )
    def get(self, request: Request, episode_id: int):
        summary_results = CommentsSummaryResult.objects.filter(episode=episode_id)
        # summary_results = CommentsSummaryResult.objects.all()
        serializer = CommentsSummarySerializer(summary_results, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_description="댓글 요약 삭제",
        manual_parameters=[
            get_path_parameter(
                "episode_id",
                description="에피소드의 ID",
                default=DEFAULT_EPISODE_ID,
            ),
        ],
        responses={
            204: "삭제 성공 (No Content)",
            404: "No summaries found for this episode.",
        },
    )
    def delete(self, request: Request, episode_id: int):
        """
        Delete all comment summaries for a specific episode.
        """
        summary_results = CommentsSummaryResult.objects.filter(episode=episode_id)
        if not summary_results.exists():
            return Response(
                {"detail": "No summaries found for this episode."},
                status=status.HTTP_404_NOT_FOUND,
            )

        summary_results.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CommentClassificationView(APIView):
    """
    댓글 유형을 분류하는 View 입니다.
    """

    async def get(self, request: Request, episode_id: int):
        """
        Retrieve the classification result for comments in a specific episode.
        """
        episode = get_object_or_404(Episode, id=episode_id)
        comments = Comment.objects.filter(episode=episode)
        serializer = CommentsSummarySerializer(comments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
