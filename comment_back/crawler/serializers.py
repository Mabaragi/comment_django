from rest_framework import serializers
from .models import *


class SeriesSerializer(serializers.ModelSerializer):
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


class EpisodeSerializer(serializers.ModelSerializer):
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
    errors = serializers.ListField(child=serializers.DictField())


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = "__all__"


class CommentCreateResponseSerializer(serializers.Serializer):
    created_data = CommentSerializer(many=True)
    errors = serializers.ListField(child=serializers.DictField())
