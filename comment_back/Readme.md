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

| 항목             | 개선 전     | 개선 후         | 비고                                            |
| ---------------- | ----------- | --------------- | ----------------------------------------------- |
| ⏱️ API 응답 시간 | 약 6000ms   | **300ms 내외**  | 약 **20배 성능 향상**                           |
| 🔄 SQL 쿼리 수   | 500개 이상  | **4개**         |                                                 |
| 🧷 데이터 무결성 | 실시간 참조 | **스냅샷 보존** | 원본 댓글 수정/삭제와 무관하게 요약 데이터 유지 |

> 💡 _결과적으로, JSON 기반 Snapshot 전략은 성능을 대폭 향상시켰을 뿐 아니라,  
> 데이터의 역사적 무결성도 함께 강화하는 효과를 얻었습니다._

---
