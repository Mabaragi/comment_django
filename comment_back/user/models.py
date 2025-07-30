from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MinLengthValidator


class CustomUser(AbstractUser):
    username = models.CharField(max_length=15, unique=True)
    name = models.CharField(max_length=30)

    def __str__(self):
        return self.username
