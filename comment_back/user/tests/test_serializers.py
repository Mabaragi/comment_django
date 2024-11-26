from rest_framework.test import APITestCase
from rest_framework.exceptions import ValidationError
from ..serializers import CustomUserSerializer


class CustomUserSerializerTest(APITestCase):

    def setUp(self):
        # 유효한 데이터 세트
        self.valid_data = {
            "username": "valid_user",
            "password": "ValidPass123!",
            "email": "valid.email@example.com",
            "name": "ValidName"
        }
    
    def assertInvalidField(self, field_name: str, invalid_value:str):
        """
        헬퍼 메서드: 특정 필드에 잘못된 값을 넣어 테스트.
        """
        data = self.valid_data.copy()
        data[field_name] = invalid_value
        serializer = CustomUserSerializer(data=data)
        self.assertFalse(serializer.is_valid())

    def test_valid_data(self):
        serializer = CustomUserSerializer(data=self.valid_data)
        self.assertTrue(serializer.is_valid())

    # 아이디 검증 테스트
    def test_invalid_username_too_short(self):
        self.assertInvalidField("username", "a")

    def test_invalid_username_special_characters(self):
        self.assertInvalidField("username", "invalid@user")

    # 닉네임 검증 테스트
    def test_invalid_name_too_short(self):
        self.assertInvalidField("username", "a")
