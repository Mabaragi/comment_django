from rest_framework import serializers
from .models import *


class DynamicFieldsModelSerializer(serializers.ModelSerializer):
    """
    동적으로 필드를 선택할 수 있는 베이스 Serializer
    """

    def __init__(self, *args, **kwargs):
        fields = kwargs.pop("fields", None)
        super().__init__(*args, **kwargs)
        if fields:
            allowed = set(fields)
            existing = set(self.fields.keys())
            for field_name in existing - allowed:
                self.fields.pop(field_name)


class SeriesSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = Series
        fields = "__all__"


class SeriesCreateSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=True)

    class Meta:
        model = Series
        fields = ["id"]

    def validate_id(self, value):
        if Series.objects.filter(id=value).exists():
            raise serializers.ValidationError("해당 시리즈 id는 이미 존재합니다.")
        return value


class EpisodeSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = Episode
        fields = "__all__"


class EpisodeCreateSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=True)

    class Meta:
        model = Episode
        fields = ["id"]

    def validate_id(self, value):
        if Episode.objects.filter(id=value).exists():
            raise serializers.ValidationError("해당 에피소드 id는 이미 존재합니다.")
        return value


class EpisodeCreateResponseSerializer(serializers.Serializer):
    created_data = EpisodeSerializer(many=True)
    errors_items = serializers.ListField(child=serializers.DictField())


class CommentSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = Comment
        fields = "__all__"


class CommentCreateResponseSerializer(serializers.Serializer):
    created_data = CommentSerializer(many=True)
    error_items = serializers.ListField(child=serializers.DictField())


class CommentCountSerializer(serializers.Serializer):
    count = serializers.IntegerField(help_text="댓글 개수")
    spam_count = serializers.IntegerField(help_text="스팸 댓글 개수")
    not_spam_count = serializers.IntegerField(help_text="스팸이 아닌 댓글 개수")
    unprocessed_count = serializers.IntegerField(
        help_text="AI 분류가 완료되지 않은 댓글 개수"
    )

    episode_id = serializers.IntegerField(help_text="에피소드 ID")

    def validate_episode_id(self, value):
        if not Episode.objects.filter(id=value).exists():
            raise serializers.ValidationError("해당 에피소드 ID는 존재하지 않습니다.")
        return value
