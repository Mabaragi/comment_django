# myapp/services/llm_service.py
import os
from google import genai
from google.genai import types

API_KEY = os.getenv("GOOGLE_API_KEY")

if not API_KEY:
    raise ValueError("GOOGLE_API_KEY environment variable not set.")


llm_client = genai.Client(api_key=API_KEY)


async def generate_comment_category(comment_content: str, client: genai.Client) -> str:

    model = "gemini-2.5-flash-lite-preview-06-17"
    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text=comment_content),
            ],
        ),
    ]
    generate_content_config = types.GenerateContentConfig(
        temperature=0,
        thinking_config=types.ThinkingConfig(
            thinking_budget=0,
        ),
        response_mime_type="text/plain",
        system_instruction=[
            types.Part.from_text(
                text="""
당신은 주어진 댓글의 의도를 분석하고, 정의된 세 가지 카테고리 중 하나로 분류하는 전문가입니다. 분류 결과와 그 근거를 반드시 JSON 형식으로만 응답해야 합니다.

# 카테고리 정의:
1.  **댓글읽기 재미**: 댓글 내용이 주로 유머, 감탄, 오락, 시간 보내기 등 유희적 목적을 가질 때 분류합니다.
2.  **여론 및 정보탐색**: 다른 사람들의 반응이 궁금하거나, 작품의 특정 내용(예: 복선, 설정)에 대한 정보를 얻거나 확인하려는 목적을 가질 때 분류합니다.
3.  **비판**: 작품의 내용, 그림, 전개 등에 대해 긍정적이거나 부정적인 평가, 분석, 제안, 혹은 자신의 생각과 비교하는 내용을 포함할 때 분류합니다.

# 출력 형식:
{
  "category": "분류된 카테고리명",
  "reason": "해당 카테고리로 분류한 구체적인 이유"
}

# 예시:
- 입력 댓글: "작가님 진짜 천재 아니냐고 ㅋㅋㅋㅋㅋ 오늘 화 미쳤다"
- 출력:
{
  "category": "댓글읽기 재미",
  "reason": "웃음을 나타내는 'ㅋㅋㅋㅋ'와 '미쳤다'는 감탄사를 사용하여 작품을 즐기고 감탄하는 유희적 반응을 보이고 있으므로 '댓글읽기 재미' 카테고리로 분류했습니다."
}

- 입력 댓글: "주인공이 왜 저기서 저런 선택을 한 거지? 다들 어떻게 생각함?"
- 출력:
{
  "category": "여론 및 정보탐색",
  "reason": "주인공의 행동에 의문을 제기하며 다른 사람들의 의견('다들 어떻게 생각함?')을 직접 묻고 있어 '여론 및 정보탐색'의 목적이 뚜렷합니다."
}

- 입력 댓글: "스토리 전개가 너무 작위적이네요. 이전 화보다 개연성이 떨어집니다."
- 출력:
{
  "category": "비판",
  "reason": "작품의 '스토리 전개'와 '개연성'에 대해 '작위적이다', '떨어진다'고 직접적으로 평가하고 분석하므로 '비판' 카테고리로 분류했습니다."
}

# 이제 다음 댓글을 분류하세요:
"""
            )
        ],
    )
    response = await client.aio.models.generate_content(
        model=model, contents=contents, config=generate_content_config
    )
    return response.text or "No response generated."


__all__ = [
    "llm_client",
]
