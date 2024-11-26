from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from typing import Dict
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.serializers import Serializer, CharField
from .models import CustomUser
from .serializers import CustomUserSerializer

# Serializer 정의
class MessageSerializer(Serializer):
    message = CharField(help_text="A welcome message")

# API View
@swagger_auto_schema(
    method="get",
    responses={200: MessageSerializer}
)
@api_view(["GET"])
def get_index(request: Request) -> Response:
    """
    Return a JSON response with a 'message' key and value 'Hello World'.
    """
    data = {"message": "hellow worlds!"}
    serializer = MessageSerializer(data)
    return Response(serializer.data)


class UserListView(APIView):
    @swagger_auto_schema(
        operation_description="Retrieve a list of users",
        responses={200: CustomUserSerializer(many=True)},  # Swagger에 응답 스키마 표시
    )
    def get(self, request:Request) -> Response:
        users = CustomUser.objects.all()
        serializer = CustomUserSerializer(users, many=True)
        return Response(serializer.data)
