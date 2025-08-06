from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status
from rest_framework.generics import DestroyAPIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_yasg.utils import swagger_auto_schema

from crawler.models import Comment, Episode
from services.llm_service import generate_comment_emotion
from utils.swagger import get_path_parameter, DEFAULT_EPISODE_ID
from .models import CommentAnalysisResult, CommentsSummaryResult
from .serializers import CommentEmotionAnalysisSerializer, CommentsSummarySerializer
from logging import getLogger
import json
from typing import TypedDict, List

logger = getLogger(__name__)


# Type definitions
class EmotionResult(TypedDict):
    score: int
    id: int
    reason: str


EmotionResponse = dict[str, List[EmotionResult]]


class CommentAnalysisResultDestroyView(DestroyAPIView):
    """댓글 감정 분석 결과를 삭제하는 API 뷰"""

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
    """댓글 요약 결과 관리 API 뷰"""

    def _prepare_source_comments(self, episode_id: int) -> List[dict]:
        """에피소드의 댓글을 요약용 데이터로 변환"""
        comments = (
            Comment.objects.filter(episode=episode_id)
            .order_by("-created_at")
            .values_list("id", "content", "is_best")
        )
        return [
            {"id": comment[0], "content": comment[1], "is_best": comment[2]}
            for comment in comments
        ]

    @swagger_auto_schema(
        operation_description="댓글 요약 생성",
        operation_summary="에피소드의 댓글들을 요약하여 새로운 요약 결과를 생성합니다.",
        manual_parameters=[
            get_path_parameter(
                "episode_id",
                description="요약할 댓글들이 속한 에피소드의 ID",
                default=DEFAULT_EPISODE_ID,
            ),
        ],
        responses={
            201: CommentsSummarySerializer(),
            400: "Bad Request - 잘못된 요청 데이터",
            404: "Not Found - 에피소드를 찾을 수 없음",
        },
    )
    def post(self, request: Request, episode_id: int):
        """댓글 요약 생성"""
        get_object_or_404(Episode, id=episode_id)

        source_comments = self._prepare_source_comments(episode_id)
        data = {
            "episode": episode_id,
            "source_comments": source_comments,
        }

        serializer = CommentsSummarySerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="댓글 요약 목록 조회",
        operation_summary="특정 에피소드의 모든 댓글 요약 결과를 조회합니다.",
        manual_parameters=[
            get_path_parameter(
                "episode_id",
                description="조회할 에피소드의 ID",
                default=DEFAULT_EPISODE_ID,
            ),
        ],
        responses={
            200: CommentsSummarySerializer(many=True),
            404: "Not Found - 에피소드를 찾을 수 없음",
        },
    )
    def get(self, request: Request, episode_id: int):
        """댓글 요약 목록 조회"""
        get_object_or_404(Episode, id=episode_id)

        summary_results = CommentsSummaryResult.objects.filter(episode=episode_id)
        serializer = CommentsSummarySerializer(summary_results, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_description="댓글 요약 전체 삭제",
        operation_summary="특정 에피소드의 모든 댓글 요약 결과를 삭제합니다.",
        manual_parameters=[
            get_path_parameter(
                "episode_id",
                description="삭제할 요약들이 속한 에피소드의 ID",
                default=DEFAULT_EPISODE_ID,
            ),
        ],
        responses={
            204: "No Content - 삭제 성공",
            404: "Not Found - 삭제할 요약이 없음",
        },
    )
    def delete(self, request: Request, episode_id: int):
        """댓글 요약 전체 삭제"""
        summary_results = CommentsSummaryResult.objects.filter(episode=episode_id)
        if not summary_results.exists():
            return Response(
                {"detail": "No summaries found for this episode."},
                status=status.HTTP_404_NOT_FOUND,
            )

        summary_results.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CommentEmotionAnalysisView(APIView):
    """댓글 감정 분석 API 뷰"""

    def _get_unprocessed_comments(self, episode: Episode) -> tuple[List[Comment], dict]:
        """미처리 댓글 조회 및 맵핑 딕셔너리 생성"""
        comments = Comment.objects.filter(
            episode=episode, is_ai_processed=False, is_spam=None
        )
        comments_map = {comment.id: comment for comment in comments}
        return list(comments), comments_map

    def _prepare_source_comments(self, comments: List[Comment]) -> List[dict]:
        """댓글을 LLM 분석용 데이터로 변환"""
        return [{"id": comment.id, "content": comment.content} for comment in comments]

    def _parse_analysis_result(self, analysis_result: str) -> EmotionResponse:
        """LLM 분석 결과를 파싱"""
        try:
            return json.loads(analysis_result)
        except json.JSONDecodeError as e:
            logger.error(f"JSON 파싱 에러 발생: {e}")
            raise ValueError("Invalid JSON response from LLM") from e

    def _update_comments_with_analysis(
        self, parsed_result: EmotionResponse, comments_map: dict
    ) -> List[Comment]:
        """분석 결과로 댓글 정보 업데이트"""
        comments_to_update = []

        for item in parsed_result.get("response", []):
            comment_id = item.get("id")
            comment = comments_map.get(comment_id)

            if not comment:
                logger.warning(f"댓글 ID {comment_id}를 찾을 수 없습니다.")
                continue

            # 댓글 정보 업데이트
            comment.ai_emotion_score = item.get("score")
            comment.ai_reason = item.get("reason")
            comment.is_spam = item.get("is_spam")
            comment.is_ai_processed = True
            comment.ai_processed_at = timezone.now()
            comments_to_update.append(comment)

        return comments_to_update

    def _bulk_update_comments(self, comments_to_update: List[Comment]) -> None:
        """댓글 정보 일괄 업데이트"""
        if not comments_to_update:
            return

        Comment.objects.bulk_update(
            comments_to_update,
            [
                "ai_emotion_score",
                "ai_reason",
                "is_ai_processed",
                "ai_processed_at",
                "is_spam",
            ],
        )
        logger.info(f"{len(comments_to_update)}개 댓글 감정 분석 완료")

    @swagger_auto_schema(
        operation_description="댓글 감정 분석 실행",
        operation_summary="에피소드의 미처리 댓글들에 대해 감정 분석을 수행합니다.",
        manual_parameters=[
            get_path_parameter(
                "episode_id",
                description="분석할 댓글들이 속한 에피소드의 ID",
                default=DEFAULT_EPISODE_ID,
            ),
        ],
        responses={
            200: "분석 성공",
            404: "Not Found - 에피소드를 찾을 수 없음",
            500: "Internal Server Error - 분석 처리 오류",
        },
    )
    def patch(self, request: Request, episode_id: int):
        """댓글 감정 분석 실행"""
        episode = get_object_or_404(Episode, id=episode_id)

        # 미처리 댓글 조회
        comments, comments_map = self._get_unprocessed_comments(episode)

        if not comments:
            return Response(
                {"message": "처리할 댓글이 없습니다."}, status=status.HTTP_200_OK
            )

        # LLM 분석 요청
        source_comments = self._prepare_source_comments(comments)
        analysis_result = generate_comment_emotion(source_comments)

        if not analysis_result:
            logger.error("LLM에서 분석 결과를 받지 못했습니다.")
            return Response(
                {"error": "No analysis result generated."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        # 결과 파싱 및 업데이트
        try:
            logger.debug(f"LLM 응답 수신: {analysis_result}")
            parsed_result = self._parse_analysis_result(analysis_result)
            comments_to_update = self._update_comments_with_analysis(
                parsed_result, comments_map
            )
            self._bulk_update_comments(comments_to_update)

            return Response(parsed_result, status=status.HTTP_200_OK)

        except ValueError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
