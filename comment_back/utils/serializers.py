from rest_framework import serializers


class ErrorResponseSerializer(serializers.Serializer):
    """공통 에러 응답 Serializer"""

    error_code = serializers.CharField(help_text="에러 코드")
    message = serializers.CharField(help_text="사용자 친화적인 에러 메시지")
    detail = serializers.CharField(help_text="상세 에러 정보")
