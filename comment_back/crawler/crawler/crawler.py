from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport
from .queries import COMMENT_QUERY, EPISODE_QUERY
from typing import List, Dict
from bs4 import BeautifulSoup
import logging, requests


# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)


class NoCommentError(Exception):
    """크롤링 된 댓글이 없을때 발생하는 에러"""


class NoSeriesError(Exception):
    """시리즈가 없을때 발생하는 에러"""


HEADERS = {
    "Accept": "application/json",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
    "Referer": "https://page.kakao.com/",
    "accept": "*/*",
    "accept-language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
    "content-type": "application/json",
    "priority": "u=1, i",
    "sec-ch-ua": '"Chromium";v="130", "Google Chrome";v="130", "Not?A_Brand";v="99"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-site",
}

# 상수 정의
transport = RequestsHTTPTransport(
    url="https://bff-page.kakao.com/graphql", headers=HEADERS
)
client = Client(transport=transport, fetch_schema_from_transport=False)
comment_query = gql(COMMENT_QUERY)
episode_query = gql(EPISODE_QUERY)
ITEM_PER_PAGE = 25


def get_page_count(total_count: int) -> int:
    """총 아이템 수에 따라 필요한 페이지 수 계산"""
    return (total_count + ITEM_PER_PAGE - 1) // ITEM_PER_PAGE


def crawl_episode_comments(
    series_id: int,
    product_id: int,
    page: int = 0,
    last_comment_uid: int = None,
) -> Dict:
    """특정 에피소드의 댓글 데이터 크롤링"""
    return client.execute(
        comment_query,
        variable_values={
            "commentListInput": {
                "page": page,
                "seriesId": series_id,
                "productId": product_id,
                "lastCommentUid": last_comment_uid,
            }
        },
    )


def get_comments_by_episode(series_id: int, product_id: int) -> List[Dict]:
    """특정 에피소드의 댓글 전체를 가져옴"""
    comments = []
    last_comment_uid = None
    page = 0

    while True:
        comment_data = crawl_episode_comments(
            series_id, product_id, page, last_comment_uid
        )
        if page == 0:
            comment_count = comment_data["commentList"]["totalCount"]
            page_count = get_page_count(comment_count)

        if not comment_data or "commentList" not in comment_data:
            raise NoCommentError("댓글이 없습니다.")

        comment_list = comment_data["commentList"].get("commentList", [])
        if not comment_list:
            raise NoCommentError("댓글이 없습니다.")

        comments.extend(comment_list)
        last_comment_uid = comment_list[-1]["commentUid"]
        # logger.info(f"페이지 {page + 1} 댓글 {len(comments)}개 크롤링 완료.")
        page += 1

        if comment_data["commentList"].get("isEnd", False) or page >= page_count:
            break

    comments = [
        {
            "id": comment["commentUid"],
            "content": comment["comment"],
            "created_at": comment["createDt"],
            "is_best": comment["isBest"],
            "user_name": comment["userName"],
            "user_thumbnail_url": comment["userThumbnailUrl"],
            "user_uid": comment["userUid"],
            "series": series_id,
            "episode": product_id,
        }
        for comment in comments
    ]

    return comments


def get_comment_count_by_episode(series_id: int, product_id: int) -> int:
    return (
        crawl_episode_comments(series_id=series_id, product_id=product_id)
        .get("commentList", {})
        .get("totalCount", {})
    )


def get_episode_by_series(series_id: int, after: str = None) -> Dict:
    """특정 시리즈의 에피소드 데이터를 가져옴"""
    variables = {"seriesId": series_id, "after": after, "sortType": "asc"}
    data = client.execute(episode_query, variable_values=variables)
    if not data.get("contentHomeProductList"):
        raise NoSeriesError("해당 시리즈가 존재하지 않습니다.")
    return data.get("contentHomeProductList", {})


def get_episode_count_by_series(series_id: int) -> int:
    return get_episode_by_series(series_id=series_id).get("totalCount", 0)


def get_all_episodes_by_series(series_id: int) -> List[Dict]:
    """특정 시리즈의 모든 에피소드를 가져옴"""
    after = "0"
    page = 0
    episode_list = []

    while True:
        content = get_episode_by_series(series_id=series_id, after=after)
        if page == 0:
            total_count = content.get("totalCount", 1)
            page_count = get_page_count(total_count)

        has_next_page = content.get("pageInfo", {}).get("hasNextPage", False)
        episode_list.extend(content.get("edges", []))
        after = f"{int(after) + ITEM_PER_PAGE}"

        if not has_next_page or page >= page_count:
            break
    episodes = [episode["node"]["eventLog"]["eventMeta"] for episode in episode_list]
    keeped_keys = ["id", "category", "name", "subcategory"]
    result = [
        {
            **{key: episode[key] for key in keeped_keys if key in episode},
            "series": series_id,
        }
        for episode in episodes
    ]
    return result


def test_get_all_episodes_by_series(series_id: int) -> tuple[List[Dict], int]:
    """특정 시리즈의 모든 에피소드를 가져옴"""
    after = "0"
    page = 0
    episode_list = []

    while True:
        content = get_episode_by_series(series_id=series_id, after=after)
        if page == 0:
            total_count = content.get("totalCount", 1)
            page_count = get_page_count(total_count)

        has_next_page = content.get("pageInfo", {}).get("hasNextPage", False)
        episode_list.extend(content.get("edges", []))
        after = f"{int(after) + ITEM_PER_PAGE}"

        if not has_next_page or page >= page_count:
            break
    return (episode_list, total_count)


# def get_series(series_id: int) -> Dict:
#     url = f"https://page.kakao.com/content/{series_id}"
#     response = requests.get(url, headers=HEADERS)
#     soup = BeautifulSoup(response.text, "html.parser")
#     title = soup.select("span.font-large3-bold.mb-3pxr.text-ellipsis.break-all.text-el-70.line-clamp-2")
#     print(title)
#     print(soup)
#     return soup
