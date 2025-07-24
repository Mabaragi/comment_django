## DRF ModelSerializer에서 관계 필드의 입력과 검증 결과

### 현상 요약

- **입력 시**:  
  관계 필드(예: ForeignKey, OneToOneField, ManyToManyField)는  
  **pk(정수, id)** 값으로 입력받는다.

- **검증 후**:  
  `serializer.is_valid()`가 호출되고 나면  
  **validated_data**에는 해당 pk에 해당하는 **모델 인스턴스(객체)**가 들어간다.

---

### 왜 이런가?

- DRF의 `ModelSerializer`는 관계 필드에 대해 내부적으로 `PrimaryKeyRelatedField`를 사용한다.
- 이 필드는 입력값이 pk일 때, 검증 과정에서 해당 pk로 DB에서 객체를 조회하여  
  **validated_data에 실제 모델 객체로 변환**해 준다.

---

### 예시 코드

```python
# 입력 시
serializer = CommentEmotionAnalysisSerializer(data={"comment": 123})

# 검증 전
serializer.initial_data["comment"]  # 123 (pk)

# 검증
serializer.is_valid()

# 검증 후
serializer.validated_data["comment"]  # <Comment: ...> (Comment 객체)
```

---

### 시리얼라이저의 검증 시점

- DRF에서 시리얼라이저의 검증은 **`serializer.is_valid()` 메서드를 호출하는 순간** 결정됩니다.
- 이 메서드를 호출하면 입력 데이터에 대한 유효성 검사와 변환이 한 번에 이루어집니다.
- 검증이 통과하면, `serializer.validated_data`에 변환된(예: pk → 객체) 값이 저장됩니다.
- 검증이 실패하면, `serializer.errors`에 에러 정보가 저장됩니다.

**정리:**

- 시리얼라이저의 검증은 `is_valid()` 호출 시점에 실행된다.
- 이때 validated_data가 채워지고, 관계 필드는 pk에서 객체로 변환된다.

---

### 결론

- **입력**: pk 값(int)
- **검증 후**: 실제 모델 인스턴스
- 이 동작은 DRF의 표준이며, 관계 필드의 일관된 처리 방식이다.
- 따라서, 시리얼라이저 내부에서 validated_data["comment"]를 사용할 때는 항상 객체가 들어온다고 생각하면 된다.

---

**참고:**

- 공식 문서: [DRF PrimaryKeyRelatedField](https://www.django-rest-framework.org/api-guide/relations/#primarykeyrelatedfield)

![alt text](image-5.png)

## Django API 성능 개선: 6초에서 300ms로 응답 속도 단축

### 1. 문제 상황

댓글 요약 생성 API 요청 시, **응답 시간이 6초 이상** 소요되는 심각한 성능 저하가 발생했습니다.  
Django Debug Toolbar로 확인한 결과, **API 호출 한 번에 500개 이상의 SQL 쿼리**가 실행되고 있었습니다.

---

### 2. 원인 분석

쿼리 로그를 상세히 분석한 결과, 500개가 넘는 쿼리의 총 실행 시간(SQL time)은 **약 400ms에 불과**했습니다.  
이를 통해 **DB 성능이 아닌, Django ORM 오버헤드**가 병목의 원인임을 추정할 수 있었습니다.

#### 📌 근본 원인

- `Serializer`의 `ManyToManyField` 유효성 검사 과정에서 **N+1 쿼리 문제** 발생
- 댓글 ID 목록을 개별적으로 `SELECT`하여 유효성 검사 수행
- 댓글 수만큼 **불필요한 DB 접근**이 발생

---

### 3. 해결 과정

단순 쿼리 최적화를 넘어서 **데이터 모델링의 적절성**을 재검토했습니다.

#### 🔍 요구사항 재정의

- 목표: **요약 생성 시점의 댓글 목록**을 저장
- 필요 없음: 댓글 → 요약 역참조

#### 🛠️ 해결 방법

- 실시간 관계를 위한 `ManyToManyField` → 과도한 설계

  전

  ![alt text](image-4.png)

  후

  ![alt text](image-3.png)

- → `JSONField`로 변경하여 **댓글 ID 리스트를 Snapshot 방식으로 저장**
- 이를 통해 Django는 더 이상 무결성 검증을 위한 수백 개의 쿼리를 실행하지 않게 됨

---

### 4. 개선 결과

![alt text](image-1.png)

![alt text](image-5.png)

| 항목             | 개선 전     | 개선 후         | 비고                                            |
| ---------------- | ----------- | --------------- | ----------------------------------------------- |
| ⏱️ API 응답 시간 | 약 6000ms   | **300ms 내외**  | 약 **20배 성능 향상**                           |
| 🔄 SQL 쿼리 수   | 500개 이상  | **4개**         |                                                 |
| 🧷 데이터 무결성 | 실시간 참조 | **스냅샷 보존** | 원본 댓글 수정/삭제와 무관하게 요약 데이터 유지 |

💡 _결과적으로, JSON 기반 Snapshot 전략은 성능을 대폭 향상시켰을 뿐 아니라,  
데이터의 역사적 무결성도 함께 강화하는 효과를 얻었습니다._

---

### Bulk Update로 댓글 감정 분석 성능 개선

#### 🎯 최적화 대상: 댓글 감정 분석 결과 저장

댓글 감정 분석 API에서 LLM 분석 결과를 개별 댓글에 저장하는 과정에서 성능 병목이 발생했습니다.

#### 📊 문제 상황

**개선 전 - 개별 Save 방식:**

```python
# N개의 댓글 = N번의 UPDATE 쿼리
for item in parsed_result.get("response", []):
    comment = Comment.objects.get(id=item["id"])
    comment.ai_emotion_score = item["score"]
    comment.ai_reason = item["reason"]
    comment.is_ai_processed = True
    comment.ai_processed_at = timezone.now()
    comment.save()  # 개별 UPDATE 쿼리 실행
```

**성능 이슈:**

- 100개 댓글 분석 시 → **100번의 개별 UPDATE 쿼리**
- 각 쿼리마다 DB 왕복 비용 발생
- 트랜잭션 오버헤드 누적

#### 🚀 해결 방법: Bulk Update 패턴

```python
def _update_comments_with_analysis(
    self, parsed_result: EmotionResponse, comments_map: dict
) -> List[Comment]:
    """분석 결과로 댓글 정보 업데이트"""
    comments_to_update = []

    for item in parsed_result.get("response", []):
        comment_id = item.get("id")
        comment = comments_map.get(comment_id)  # 메모리에서 조회

        if comment:
            # 메모리상에서 객체 수정
            comment.ai_emotion_score = item.get("score")
            comment.ai_reason = item.get("reason")
            comment.is_ai_processed = True
            comment.ai_processed_at = timezone.now()
            comments_to_update.append(comment)

    return comments_to_update

def _bulk_update_comments(self, comments_to_update: List[Comment]) -> None:
    """댓글 정보 일괄 업데이트"""
    if not comments_to_update:
        return

    # 단일 쿼리로 모든 댓글 업데이트
    Comment.objects.bulk_update(
        comments_to_update,
        [
            "ai_emotion_score",
            "ai_reason",
            "is_ai_processed",
            "ai_processed_at",
        ],
    )
    logger.info(f"{len(comments_to_update)}개 댓글 감정 분석 완료")
```

#### 📈 성능 개선 결과

| 항목            | 개선 전             | 개선 후  | 개선 효과              |
| --------------- | ------------------- | -------- | ---------------------- |
| **SQL 쿼리 수** | N개 (댓글 수만큼)   | **1개**  | 약 **100배 감소**      |
| **DB 트랜잭션** | N번                 | **1번**  | 트랜잭션 오버헤드 제거 |
| **응답 시간**   | 댓글 수에 비례 증가 | **일정** | 확장성 확보            |

![alt text](image-6.png)
![alt text](image-7.png)

#### 🎯 핵심 최적화 포인트

1. **메모리 기반 처리**: 이미 조회된 댓글 객체를 `comments_map`으로 재활용
2. **배치 처리**: 모든 변경사항을 메모리에서 준비 후 한 번에 DB 반영
3. **단일 트랜잭션**: `bulk_update`로 원자성 보장하면서 성능 확보

#### 💡 교훈

**개별 저장 vs Bulk 연산**

- 소량 데이터: 개별 저장도 무관
- **대량 데이터**: Bulk 연산 필수
- Django ORM의 `bulk_update`, `bulk_create` 적극 활용

이러한 최적화를 통해 **댓글 수가 증가해도 일정한 성능**을 유지할 수 있게 되었습니다.

---
