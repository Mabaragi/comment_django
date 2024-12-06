from django.db import models
from user.models import CustomUser

class Series(models.Model):  # models.Model을 상속해야 Django 모델로 인식됨
    series_id = models.IntegerField(primary_key=True)  # 기본 키 설정
    title = models.CharField(max_length=100)
    image_src = models.TextField()
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)