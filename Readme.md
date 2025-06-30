# database

```sql
 -- postgres 컨테이너에 접속
docker exec -it postgres_db psql -U postgres
docker exec -it django_app bash


 -- 데이터베이스 목록 보기
\l

-- postgres 데이터베이스 접속
\c postgres

-- 테이블 목록 보기
\dt

-- 원하는 쿼리 실행
SELECT * FROM your_table;
```

# docker

```bash
# 컨터이너 로그 실시간으로 보기
docker logs -f django_app
```

# GraphQL

1. 🔁 cursor

- 의미: 페이징 처리를 위한 고유한 위치 표시자.

- 역할: 이전/다음 페이지를 불러올 때 기준이 되는 "포인터"

네, 지금까지 파악한 내용을 바탕으로  
**신입 개발자 자기소개(구현사항 중심, Swagger UI 포함)** 예시를 아래와 같이 정리해드립니다.

---

### 신입 개발자 자기소개 (구현사항 중심)

저는 댓글 분석 프로젝트의 백엔드 개발을 담당하며, 다음과 같은 주요 기능을 직접 구현하였습니다.

---

#### 1. Django & PostgreSQL 기반 백엔드 구축

- Django 프레임워크를 활용하여 프로젝트의 전체 백엔드 구조를 설계하고 구현하였습니다.
- 실제 서비스 환경에서 PostgreSQL 데이터베이스를 연동하여, 댓글 및 사용자 데이터를 효율적으로 저장·관리할 수 있도록 하였습니다.
- Django ORM을 이용해 데이터베이스와의 연동 및 CRUD 기능을 구현하였습니다.

#### 2. 요청 기반 크롤러 연동

- 크롤러 모듈을 개발하여, 사용자의 요청이 있을 때마다 외부 사이트에서 댓글 데이터를 수집하도록 구현하였습니다.
- 수집된 데이터는 Django 모델을 통해 PostgreSQL 데이터베이스에 저장되며, 데이터의 신뢰성과 일관성을 확보하였습니다.

#### 3. 사용자 인증 및 관리 기능

- 사용자 회원가입, 로그인 등 인증 기능을 직접 구현하였으며, JWT(Json Web Token) 기반 인증 방식을 적용하여 보안성을 높였습니다.
- Django의 Custom User 모델을 적용하여, 서비스에 맞는 사용자 관리가 가능하도록 설계하였습니다.

#### 4. RESTful API 및 Swagger UI 문서화

- Django REST Framework를 활용하여 댓글, 사용자 등 주요 기능에 대한 RESTful API를 설계하고 구현하였습니다.
- API의 명확한 사용법과 테스트를 위해 Swagger UI(drf_yasg, drf_spectacular)를 도입하였으며,  
  이를 통해 개발자 및 협업자들이 API를 쉽게 이해하고 활용할 수 있도록 하였습니다.

#### 5. Docker 환경 구성

- Dockerfile과 docker-compose.yml을 작성하여, 개발 및 배포 환경의 일관성을 확보하였습니다.
- Django 서버와 PostgreSQL 데이터베이스를 컨테이너로 관리하여, 누구나 손쉽게 동일한 환경에서 프로젝트를 실행할 수 있도록 하였습니다.

---

### 성장 포인트

이 프로젝트를 통해 Django와 PostgreSQL을 활용한 실전 백엔드 개발 경험을 쌓았으며,  
RESTful API 설계, JWT 인증, Swagger UI 기반의 API 문서화, Docker 환경 구성 등  
실무에서 요구되는 다양한 기술을 직접 구현해보며 백엔드 개발자로서의 역량을 키울 수 있었습니다.

---

**예시 문구(짧게 요약):**

> "저는 Django와 PostgreSQL을 기반으로 한 댓글 분석 프로젝트의 백엔드 개발을 담당하였으며, 요청 기반 크롤러, JWT 인증, Swagger UI를 통한 API 문서화, Docker 환경 구성 등 실무에 필요한 다양한 기능을 직접 구현하였습니다."

---

필요에 따라 위 내용을 자기소개서, 포트폴리오, 면접 답변 등에 맞게 조정해서 사용하시면 좋습니다!  
더 구체적인 코드 예시나, 강조하고 싶은 구현 포인트가 있다면 추가로 말씀해 주세요.

좋습니다. `drf` (Django REST framework, DRF)는 Django에서 API 서버를 만들 때 거의 필수적인 강력한 라이브러리입니다.
여기서는 DRF를 **처음 설치하고 기본 세팅**하는 과정을 안내드릴게요.

---

# 페이지 네이션

## ✅ 3단계: DRF 기본 설정 (선택)

`settings.py` 하단에 추가:

```python
REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'PAGE_SIZE': 20,
}
```

이렇게 하면 기본적으로 `limit=20`으로 작동하며, 쿼리 파라미터로 `limit`과 `offset`을 받을 수 있게 됩니다.

> 👉 이 설정은 `GenericAPIView`나 `ListAPIView`처럼 DRF의 generic view 기반일 때 자동으로 동작합니다.

---

## ✅ 4단계: 기본 뷰 사용 예시

```python
from rest_framework.generics import ListAPIView
from .models import Episode
from .serializers import EpisodeSerializer

class EpisodeListView(ListAPIView):
    queryset = Episode.objects.all()
    serializer_class = EpisodeSerializer
```

이 뷰는 이제 다음과 같이 작동합니다:

```http
GET /api/episodes?limit=10&offset=30
```

---

## ✅ 5단계: Swagger 세팅 (선택)

`urls.py`에 Swagger UI 추가:

```python
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

schema_view = get_schema_view(
   openapi.Info(
      title="API 문서",
      default_version='v1',
      description="Swagger 문서 예시",
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    ...
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
]
```

이제 `/swagger/`로 들어가면 자동 API 문서를 볼 수 있어요.

---

## ✅ 정리

| 단계 | 작업                                       |
| ---- | ------------------------------------------ |
| ①    | `pip install djangorestframework drf-yasg` |
| ②    | `INSTALLED_APPS`에 등록                    |
| ③    | `settings.py`에 `REST_FRAMEWORK` 설정 추가 |
| ④    | `ListAPIView` 사용해 기본 pagination 지원  |
| ⑤    | Swagger 문서를 `/swagger/`에 추가 (선택)   |

---

원하시면 지금 하고 계신 에피소드 API를 `ListAPIView` 기반으로 바꾸는 것도 도와드릴게요.
그리고 `pagination_class`를 커스터마이징해서 `max_limit` 제한을 넣을 수도 있습니다.
