import json
import os
from datetime import datetime
from rest_framework import serializers
from .models import CommentAnalysisResult, CommentsSummaryResult
import requests
from requests.exceptions import RequestException
from django.conf import settings
from crawler.models import Comment
from services.llm_service import generate_comment_summary


class CommentEmotionAnalysisSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommentAnalysisResult
        fields = "__all__"
        read_only_fields = (
            "sentiment",
            "content",
        )

    def create(self, validated_data):
        comment = validated_data.get("comment")
        comment_id = comment.id
        print(comment_id)
        print(validated_data)

        # content 추출
        content = comment.content
        print(settings.INFER_SERVER_URL)
        # 감정 분석 요청
        try:
            response = requests.post(
                f"{settings.INFER_SERVER_URL}/emotion",
                json={"content": content},
                timeout=5,
            )
        except RequestException as e:
            raise serializers.ValidationError(f"추론 서버 네트워크 오류입니다: {e}")

        handle_infer_response(response, context="추론 서버")

        try:
            sentiment_result = response.json().get("inference")
        except Exception as e:
            raise serializers.ValidationError(
                f"추론 서버 응답 파싱 오류입니다: {str(e)}"
            )

        if sentiment_result is None:
            raise serializers.ValidationError("추론 결과가 없습니다.")

        # 결과 저장
        return CommentAnalysisResult.objects.create(
            content=content, sentiment=sentiment_result, **validated_data
        )


class CommentsSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = CommentsSummaryResult
        fields = "__all__"
        read_only_fields = ["summary"]

    def create(self, validated_data):
        comment_contents = validated_data.get("source_comments", [])
        summary = generate_comment_summary(comment_contents)
        summary_instance = CommentsSummaryResult.objects.create(
            summary=summary,
            **validated_data,
        )
        return summary_instance


def handle_infer_response(response, context="추론 서버"):
    if response.status_code == 400:
        raise serializers.ValidationError(f"{context}에 잘못된 요청입니다.")
    elif response.status_code == 404:
        raise serializers.ValidationError(
            f"{context} 엔드포인트를 찾을 수 없습니다. {response.json()}"
        )
    elif response.status_code >= 500:
        raise serializers.ValidationError(f"{context} 내부 오류입니다.")
    elif response.status_code != 200:
        raise serializers.ValidationError(
            f"알 수 없는 {context} 오류 (status: {response.status_code})"
        )
