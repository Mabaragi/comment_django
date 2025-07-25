from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport
import json

# 1. GraphQL 엔드포인트 URL 설정
GRAPHQL_ENDPOINT = "https://bff-page.kakao.com/graphql"

# 2. GraphQL 쿼리 정의
# Python에서는 긴 문자열을 여러 줄에 걸쳐 정의할 수 있습니다.
query_string = """
query simpleSeriesSingleInfo($seriesId: Long!, $productId: Long) {
  simpleSeriesSingleInfo(productId: $productId, seriesId: $seriesId) {
    seriesAgeGrade
    singleAgeGrade
    singleSlideType
    singleIsFree
    singleIsTextViewer
    seriesSaleState
    singleSaleState
  }
}
"""
query = gql(query_string)  # gql 함수로 쿼리 문자열을 파싱합니다.

# 3. 요청에 필요한 변수 (variables) 정의
variables = {
    "seriesId": 566114411,  # 테스트할 seriesId 값
    "productId": None,  # productId는 선택 사항이므로 None으로 설정
}

# 4. HTTP 트랜스포트 설정 (요청을 보낼 방식)
# 여기서는 requests 라이브러리 기반의 HTTP 트랜스포트를 사용합니다.
# 헤더를 추가하여 브라우저에서 보냈던 것과 유사하게 설정할 수 있습니다.
transport = RequestsHTTPTransport(
    url=GRAPHQL_ENDPOINT,
    headers={
        "Content-Type": "application/json",
        "Accept": "application/json",
        # CORS와 무관하게 서버에서 특정 Referer를 요구할 수 있으므로 포함
        "Referer": "https://page.kakao.com/",
        # 추가적으로 필요하다고 생각하는 헤더를 여기에 포함할 수 있습니다.
        # 예: "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/XXX.0.0.0 Safari/537.36"
    },
    verify=True,  # SSL 인증서 검증을 활성화 (일반적으로 True 권장)
    retries=3,  # 실패 시 재시도 횟수
)

# 5. GraphQL 클라이언트 생성
client = Client(transport=transport, fetch_schema_from_transport=False)

# 6. 쿼리 실행
try:
    print(f"'{GRAPHQL_ENDPOINT}'로 GraphQL 쿼리를 전송합니다...")
    response_data = client.execute(query, variable_values=variables)

    # 7. 응답 출력
    print("\n--- GraphQL 응답 ---")
    print(response_data)

    # 특정 데이터에 접근하는 예시
    if "simpleSeriesSingleInfo" in response_data:
        info = response_data["simpleSeriesSingleInfo"]
        print("\n--- 파싱된 시리즈 정보 ---")
        print(f"시리즈 연령 등급: {info.get('seriesAgeGrade')}")
        print(f"단일 콘텐츠 판매 상태: {info.get('singleSaleState')}")
    else:
        print("응답에 'simpleSeriesSingleInfo' 필드가 없습니다.")

except Exception as e:
    print(f"\n--- 에러 발생 ---")
    # print(f"GraphQL 요청 중 오류가 발생했습니다: {e}")
    try:
        print(json.dumps(e.__dict__["errors"][0], ensure_ascii=False, indent=2))
    except Exception as dump_err:
        print(f"오류 객체를 JSON으로 덤프하는 중 추가 오류 발생: {dump_err}")
