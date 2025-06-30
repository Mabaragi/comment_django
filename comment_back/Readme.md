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