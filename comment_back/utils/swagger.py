from drf_yasg import openapi
from typing import Optional


def get_fields_query_parameter(example: str = "id,name,image_src") -> openapi.Parameter:
    return openapi.Parameter(
        name="fields",
        in_=openapi.IN_QUERY,
        type=openapi.TYPE_STRING,
        description=f"불러올 필드 이름을 쉼표로 구분하여 지정 (예: {example})",
        required=False,
    )


def get_ordering_query_parameter(
    example: str = "id,-created_at,name",
) -> openapi.Parameter:
    return openapi.Parameter(
        name="ordering",
        in_=openapi.IN_QUERY,
        type=openapi.TYPE_STRING,
        description=f"정렬할 필드 이름을 쉼표로 구분하여 지정. '-'를 앞에 붙이면 내림차순 (예: {example})",
        required=False,
    )


def get_path_parameter(
    name: str,
    description: str,
    default: Optional[str | int] = None,
) -> openapi.Parameter:
    return openapi.Parameter(
        name=name,
        in_=openapi.IN_PATH,
        type=openapi.TYPE_INTEGER,
        description=description,
        default=default,
        required=True,
    )
