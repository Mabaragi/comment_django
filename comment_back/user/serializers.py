from rest_framework import serializers
from .models import CustomUser
from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator
import re


class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ["username", "email", "name"]
        extra_kwargs = {"password": {"write_only": True}}

    def validate_username(self, value):
        # 길이 제한 검증
        if len(value) < 2 or len(value) > 15:
            raise ValidationError("아이디는 2자 이상 15자 이하여야 합니다.")

        # 특수문자 및 공백 검증
        if not re.match(r"^[a-zA-Z0-9_]+$", value):
            raise ValidationError("아이디는 특수문자나 공백을 포함할 수 없습니다.")

        return value

    def validate_name(self, value):
        # 길이 제한 검증
        if len(value) < 2 or len(value) > 10:
            raise ValidationError("닉네임은 2자 이상 10자 이하여야 합니다.")

        # 특수문자 및 공백 검증
        if not re.match(r"^[a-zA-Z0-9_]+$", value):
            raise ValidationError("닉네임은 특수문자나 공백을 포함할 수 없습니다.")

        return value

    def validate_email(self, value):
        email_validator = EmailValidator(message=("올바른 이메일 형식을 입력하세요."))
        email_validator(value)
        return value

    def validate_password(self, value):
        if len(value) < 8:
            raise ValidationError("Password must be at least 8 characters long.")
        if not re.search(r"[A-Za-z]", value):
            raise ValidationError("Password must contain at least one letter.")
        if not re.search(r"\d", value):
            raise ValidationError("Password must contain at least one number.")
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', value):
            raise ValidationError(
                "Password must contain at least one special character."
            )
        return value


class CustomTokenObtainPairSerializer(serializers.Serializer):
    """
    Custom serializer for obtaining JWT tokens.
    This can be extended to include additional fields if needed.
    """

    access = serializers.CharField()
    refresh = serializers.CharField()
