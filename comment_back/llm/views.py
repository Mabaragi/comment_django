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
from services.llm_service import generate_comment_emotion
import json
from typing import TypedDict, List
from django.utils import timezone
from logging import getLogger

logger = getLogger(__name__)


class EmotionResult(TypedDict):
    score: int
    id: int
    reason: str


EmotionResponse = dict[str, List[EmotionResult]]


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


class CommentEmotionAnalysisView(APIView):
    """
    댓글 감정 분석 결과를 조회하는 API 뷰입니다.
    """

    def patch(self, request: Request, episode_id: int):
        """
        댓글 감정 분석 결과를 생성하는 API 뷰입니다.
        """
        episode = get_object_or_404(Episode, id=episode_id)
        comments_to_process = Comment.objects.filter(
            episode=episode, is_ai_processed=False
        )
        comments_map = {comment.id: comment for comment in comments_to_process}

        source_comments = [
            {"id": comment.id, "content": comment.content}
            for comment in comments_to_process
        ]

        analysis_result = generate_comment_emotion(source_comments)
        if not analysis_result:
            raise ValueError("No analysis result generated.")

        logger.debug(f"LLM 응답 수신: {analysis_result}")  # 로그 추가
        try:
            parsed_result: EmotionResponse = json.loads(analysis_result)
        except json.JSONDecodeError as e:
            logger.error(f"JSON 파싱 에러 발생: {e}")
            return Response(
                {"error": "Invalid JSON response from LLM."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        comments_to_update = []
        for item in parsed_result.get("response", []):
            comment_id = item.get("id")
            # 댓글 객체 가져오기
            comment = comments_map.get(comment_id)
            if not comment:
                continue

            score = item.get("score")
            reason = item.get("reason")

            comment.ai_emotion_score = score
            comment.ai_reason = reason
            comment.is_ai_processed = True
            comment.ai_processed_at = timezone.now()
            comments_to_update.append(comment)

        # 한 번에 데이터베이스에 저장
        Comment.objects.bulk_update(
            comments_to_update,
            [
                "ai_emotion_score",
                "ai_reason",
                "is_ai_processed",
                "ai_processed_at",
            ],
        )

        return Response(parsed_result, status=status.HTTP_200_OK)
