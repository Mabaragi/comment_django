from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dotenv import load_dotenv
import os

load_dotenv()
CHROME_DRIVER_PATH = os.getenv('CHROME_DRIVER_PATH')
print(CHROME_DRIVER_PATH)
def get_title_with_selenium(series_id: int) -> dict:
    url = f"https://page.kakao.com/content/{series_id}"
    
    # Selenium 설정
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    service = Service(CHROME_DRIVER_PATH)  # chromedriver 경로 지정
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    try:
        driver.get(url)
        
        # 제목 요소 대기 및 추출
        wait = WebDriverWait(driver, 10)
        title_element = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "span.font-large3-bold.text-ellipsis"))
        )
        title = title_element.text.strip()
        image = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.relative.overflow-hidden.h-326pxr.w-320pxr.pt-40pxr > div.relative.h-full.min-h-\[inherit\] > div > div > div.jsx-1044487760.image-container.relative > img"))
        )
        image_src = image.get_attribute("src")
        return {'title': title, 'image_src': image_src}
    except Exception as e:
        return {"error" : e, 'message':'시리즈를 가져올 수 없습니다.'}
    finally:
        driver.quit()

# 사용 예제
series_id = 59071959
title = get_title_with_selenium(series_id)
print(f"제목: {title}")
