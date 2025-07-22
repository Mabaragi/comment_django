import pytest
import os
from services.llm_service import generate_comment_emotion


class TestGenerateCommentEmotion:
    """generate_comment_emotion API 테스트 클래스"""

    @classmethod
    def setup_class(cls):
        """테스트 클래스 시작 전 실행"""
        cls.content_file_path = os.path.join(os.path.dirname(__file__), "content.txt")
        cls.output_file_path = os.path.join(os.path.dirname(__file__), "output.txt")
        cls.test_comments = cls.load_test_comments()

    @classmethod
    def load_test_comments(cls):
        """content.txt 파일에서 테스트 댓글 로드"""
        try:
            with open(cls.content_file_path, "r", encoding="utf-8") as f:
                content = f.read().strip()

            comments = []
            for i, comment_text in enumerate(content.split("\n"), 1):
                if comment_text.strip():
                    comments.append(
                        {
                            "id": i,
                            "content": comment_text.strip(),
                            "is_best": i % 3 == 0,  # 3번째마다 베스트 댓글로 설정
                        }
                    )
            return comments
        except FileNotFoundError:
            pytest.skip(f"테스트 파일을 찾을 수 없습니다: {cls.content_file_path}")
        except Exception as e:
            pytest.skip(f"테스트 파일 로드 오류: {e}")

    def test_api_returns_response(self):
        """API가 응답을 반환하는지 테스트"""
        with open(self.output_file_path, "w", encoding="utf-8") as f:
            result = generate_comment_emotion(self.test_comments)
            print(type(result))
            f.write(str(result) + "\n")
