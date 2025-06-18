from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    WebDriverException,
)

from dotenv import load_dotenv
import os
from ..utils import handle_exception

load_dotenv()
CHROME_DRIVER_PATH = os.getenv("CHROME_DRIVER_PATH")


class SeleniumCrawlError(Exception):
    """기본 Selenium 크롤링 예외"""

    pass


class SeleniumTimeoutError(SeleniumCrawlError):
    """요소 로딩 타임아웃 예외"""

    pass


class SeleniumElementNotFoundError(SeleniumCrawlError):
    """요소가 아예 존재하지 않을 때"""

    pass


class SeleniumDriverError(SeleniumCrawlError):
    """웹드라이버 실행 실패"""

    pass


def get_title_with_selenium(series_id: int) -> dict:
    url = f"https://page.kakao.com/content/{series_id}"
    print(CHROME_DRIVER_PATH)
    # Selenium 설정
    chrome_options = Options()
    chrome_options.binary_location = "/usr/bin/google-chrome"
    chrome_options.add_argument("--headless=new")  # Headless 모드 사용
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    driver = None
    try:
        service = Service(CHROME_DRIVER_PATH)
        driver = webdriver.Chrome(service=service, options=chrome_options)
        wait = WebDriverWait(driver, 10)
        driver.get(url)

        try:
            title_element = wait.until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "span.font-large3-bold.text-ellipsis")
                )
            )
            image_element = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'img[alt="썸네일"]'))
            )
        except TimeoutException as e:
            handle_exception(e, SeleniumTimeoutError, "요소 로딩 시간 초과")
        except NoSuchElementException as e:
            handle_exception(e, SeleniumElementNotFoundError, "요소를 찾을 수 없음")

        return {
            "title": title_element.text.strip(),
            "image_src": image_element.get_attribute("src"),
        }

    except WebDriverException as e:
        handle_exception(e, SeleniumDriverError, "웹드라이버 실행 오류")

    except Exception as e:
        # 기타 예상하지 못한 에러
        handle_exception(e, SeleniumCrawlError, "알 수 없는 셀레늄 크롤링 오류")

    finally:
        if driver:
            driver.quit()


# 사용 예제
# series_id = 59071959
# title = get_title_with_selenium(series_id)
# print(f"제목: {title}")
