from django.db import models
from user.models import CustomUser


class Series(models.Model):  # models.Model을 상속해야 Django 모델로 인식됨
    id = models.IntegerField(primary_key=True)  # 기본 키 설정
    title = models.CharField(max_length=100)
    image_src = models.TextField()
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)


class Episode(models.Model):
    id = models.IntegerField(primary_key=True)  # 기본 키 설정
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=10)
    subcategory = models.CharField(max_length=20)
    series = models.ForeignKey(Series, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)


class Comment(models.Model):
    id = models.IntegerField(primary_key=True)
    content = models.TextField()
    created_at = models.DateTimeField()
    is_best = models.BooleanField()

    # 이 유저는 이 서비스의 유저가 아님, 댓글을 단 유저를 식별하기 위함.
    user_name = models.CharField(max_length=100)
    user_thumbnail_url = models.TextField()
    user_uid = models.IntegerField()

    episode = models.ForeignKey(Episode, on_delete=models.CASCADE)
    series = models.ForeignKey(Series, on_delete=models.CASCADE)
