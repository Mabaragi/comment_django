# myapp/services/llm_service.py
import os
from google import genai
from google.genai import types

API_KEY = os.getenv("GOOGLE_API_KEY")

if not API_KEY:
    raise ValueError("GOOGLE_API_KEY environment variable not set.")


llm_client = genai.Client(api_key=API_KEY)


def generate_comment_summary(
    comment_contents: dict, client: genai.Client = llm_client
) -> str:

    comment_contents_str = str(comment_contents)
    model = "gemini-2.5-flash-lite"
    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text=comment_contents_str),
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
너는 웹툰 작가에게 독자 피드백을 보고하는 전문 데이터 분석가야. 이제부터 제공될 독자 댓글 목록(JSON 형식)을 분석해서, 작가가 다음 스토리를 구상하는 데 실질적인 도움이 될 유의미한 피드백 보고서를 작성해 줘.

[분석 시 핵심 준수 사항]
- 'is_best' 필드 활용: 댓글 데이터에는 `is_best: boolean` 필드가 포함되어 있어. `is_best`가 `true`인 댓글은 독자들에게 가장 많은 공감을 얻은 '베스트 댓글'이야. 분석 시 이 베스트 댓글의 내용에 가중치를 부여하고, 여론을 증명하는 핵심 근거로 반드시 인용해야 해.
- 심층적 제언: 단순 요약을 넘어, 분석 결과를 바탕으로 "이러한 반응은 OOO라는 점에서 긍정적이며, 향후 OOO 방향으로 스토리를 이끌어가는 것을 고려해볼 수 있습니다" 와 같이 작가에게 실질적인 도움이 될 전략적 제언을 포함해 줘.

아래 보고서 구조와 지침에 따라 결과물을 생성해 줘.

---
**1. 총평 (Executive Summary)**
해당 회차의 전반적인 독자 반응과 가장 핵심적인 화두를 2~3문장으로 압축해서 요약해 줘.

**2. 긍정적 반응 (What Readers Loved)**
독자들이 열광한 포인트를 주제별(예: 캐릭터 매력, 스토리 전개, 작화 등)로 분류해서 설명해 줘. 각 포인트마다 핵심적인 베스트 댓글(is_best: true)이나 대표 댓글을 1~2개 직접 인용해서 근거를 제시해 줘. 이러한 긍정적 반응이 작품에 어떤 의미가 있는지 분석하고, 계속 유지하거나 강화할 점을 제언해 줘.

**3. 부정적/우려 반응 (Constructive Criticism & Concerns)**
독자들이 제기한 비판이나 우려 사항을 정리해 줘. (단, 비난이 아닌 건설적인 의견 위주로) 이것이 소수의 의견인지, 다수의 공감을 얻고 있는지 베스트 댓글 여부를 통해 판단하고 명시해 줘. 관련 댓글을 직접 인용하고, 작가가 이 피드백을 어떻게 고려해볼 수 있을지 실행 가능한 개선안을 제시해 줘.

**4. 독자들이 가장 궁금해하는 점 (Top Questions & Theories)**
독자들이 가장 활발하게 추측하고 질문하는 내용(떡밥)이 무엇인지 분석해 줘. 독자들의 호기심을 가장 잘 보여주는 베스트 댓글이나 대표적인 질문을 직접 인용해 줘. 이러한 독자들의 궁금증이 향후 스토리에 어떤 기회를 제공하는지 설명하고, 이를 어떻게 활용하면 좋을지 전략을 제언해 줘. (예: "OOO에 대한 높은 궁금증은 향후 스토리의 중요한 클라이맥스로 활용할 수 있는 좋은 기회입니다.")
"""
            )
        ],
    )
    response = client.models.generate_content(
        model=model, contents=contents, config=generate_content_config
    )
    return response.text or "No response generated."


def generate_comment_emotion(comments: list[dict], client: genai.Client = llm_client):
    """
    댓글의 감정 점수를 생성하는 함수 (예시: 긍정/부정/중립 및 점수 반환)
    comment: {"id": ..., "content": ..., "is_best": ...}
    """
    model = "gemini-2.5-flash-lite"
    comment_contents = str(comments[:100])  # 최대 100개 댓글만 처리
    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text=comment_contents),
            ],
        ),
    ]
    generate_content_config = types.GenerateContentConfig(
        temperature=0,
        thinking_config=types.ThinkingConfig(
            thinking_budget=0,
        ),
        response_mime_type="application/json",
        response_schema=types.Schema(
            type=types.Type.OBJECT,
            properties={
                "response": types.Schema(
                    type=types.Type.ARRAY,
                    items=types.Schema(
                        type=types.Type.OBJECT,
                        required=["score", "id", "reason"],
                        properties={
                            "score": types.Schema(
                                type=types.Type.INTEGER,
                            ),
                            "id": types.Schema(
                                type=types.Type.NUMBER,
                            ),
                            "reason": types.Schema(
                                type=types.Type.STRING,
                            ),
                        },
                    ),
                ),
            },
        ),
        system_instruction=[
            types.Part.from_text(
                text="""너는 감정 분석 전문가야. 댓글을 보고 '긍정', '부정', '중립' 중 하나로 분류하고, 0~100 사이의 감정 점수(긍정일수록 100, 부정일수록 0, 중립은 50)와 그렇게 반환한 이유를 JSON으로 반환해줘.
"""
            ),
        ],
    )
    response = client.models.generate_content(
        model=model, contents=contents, config=generate_content_config
    )

    return response.text


__all__ = [
    "llm_client",
]
