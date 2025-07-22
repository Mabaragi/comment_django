from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from collections import OrderedDict
from typing import Any, Union
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import QuerySet
from rest_framework.request import Request


class OptionalCountPagination(PageNumberPagination):
    """
    페이지네이션 클래스로, include_count 파라미터가 있을 때만 전체 개수를 계산합니다.
    count 쿼리 자체를 피하기 위해 커스텀 로직을 구현합니다.
    """

    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 10000

    def paginate_queryset(self, queryset, request, view=None):
        """
        include_count 파라미터가 false이면 count 쿼리를 실행하지 않습니다.
        """
        self.request = request

        # 페이지 크기 설정
        page_size = self.get_page_size(request)
        if not page_size:
            return None

        # 안전한 정수 변환
        if isinstance(page_size, (list, tuple)):
            page_size = page_size[0] if page_size else self.page_size

        try:
            page_size_int = int(page_size)
        except (ValueError, TypeError):
            page_size_int = self.page_size

        # 페이지 번호 가져오기
        page_number = request.query_params.get(self.page_query_param, 1)
        if page_number in self.last_page_strings:
            page_number = self.last_page_strings[0]

        try:
            page_number = int(page_number)
        except (TypeError, ValueError):
            page_number = 1

        # include_count 파라미터 확인
        include_count = request.query_params.get("include_count", "").lower() in (
            "true",
            "1",
            "yes",
        )

        if include_count:
            # count가 필요한 경우 기본 페이지네이션 사용
            paginator = Paginator(queryset, page_size_int)
            try:
                self.page = paginator.page(page_number)
            except PageNotAnInteger:
                self.page = paginator.page(1)
            except EmptyPage:
                self.page = paginator.page(paginator.num_pages)
        else:
            # count가 필요하지 않은 경우 커스텀 로직 사용
            self.page = self._get_page_without_count(
                queryset, page_number, page_size_int
            )

        return list(self.page)

    def _get_page_without_count(self, queryset, page_number: int, page_size: int):
        """
        count 쿼리 없이 페이지를 가져오는 메서드
        """
        # 시작 인덱스 계산
        start_index = (page_number - 1) * page_size

        # 현재 페이지 + 1개 더 가져와서 다음 페이지 존재 여부 확인
        end_index = start_index + page_size + 1

        # 쿼리셋 슬라이싱
        page_items = list(queryset[start_index:end_index])

        # 다음 페이지가 있는지 확인
        has_next = len(page_items) > page_size
        if has_next:
            page_items = page_items[:-1]  # 마지막 항목 제거

        # 커스텀 Page 객체 생성
        return CustomPage(page_items, page_number, page_size, has_next, start_index > 0)

    def get_paginated_response(self, data):
        # include_count 파라미터 확인
        include_count = self.request.query_params.get("include_count", "").lower() in (
            "true",
            "1",
            "yes",
        )

        response_data: OrderedDict[str, Any] = OrderedDict(
            [
                ("next", self.get_next_link()),
                ("previous", self.get_previous_link()),
                ("results", data),
            ]
        )

        # include_count가 True일 때만 count 추가 (일반 Django Page 객체인 경우만)
        if include_count:
            # CustomPage 객체가 아닌 경우에만 count 추가
            if (
                not isinstance(self.page, CustomPage)
                and hasattr(self.page, "paginator")
                and hasattr(self.page.paginator, "count")
            ):
                response_data["count"] = self.page.paginator.count
                response_data.move_to_end("results")

        return Response(response_data)

    def get_next_link(self):
        if not hasattr(self.page, "has_next") or not self.page.has_next:
            return None

        page_number = self.page.number + 1
        return self.get_page_link(page_number)

    def get_previous_link(self):
        if not hasattr(self.page, "has_previous") or not self.page.has_previous:
            return None

        page_number = self.page.number - 1
        return self.get_page_link(page_number)

    def get_page_link(self, page_number):
        url = self.request.build_absolute_uri()
        query_params = self.request.query_params.copy()
        query_params[self.page_query_param] = page_number
        return f"{url.split('?')[0]}?{query_params.urlencode()}"


class CustomPage:
    """
    Django의 Page 객체를 모방한 커스텀 페이지 클래스
    count 쿼리 없이 페이지네이션을 처리하기 위해 사용
    """

    def __init__(self, object_list, number, page_size, has_next, has_previous):
        self.object_list = object_list
        self.number = number
        self.page_size = page_size
        self.has_next = has_next
        self.has_previous = has_previous

    def __iter__(self):
        return iter(self.object_list)

    def __len__(self):
        return len(self.object_list)
