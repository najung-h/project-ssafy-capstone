import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# 크롬 옵션 설정
chrome_options = Options()
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--disable-extensions")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

# 이전 폴더의 크롬 드라이버를 읽어옴
service = Service("../chromedriver-win64/chromedriver.exe")


def open_community_page(company_name):
    # [1] 브라우저 실행 및 Toss 접속
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.get("https://www.tossinvest.com/")
    time.sleep(1)

    # [2] 회사명 검색
    body = driver.find_element(By.TAG_NAME, "body")
    body.send_keys("/")  # '/' 입력 → 검색창 열림
    time.sleep(1)

    search_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located(
            (By.XPATH, "//input[@placeholder='검색어를 입력해주세요']")
        )
    )
    search_input.send_keys(company_name)
    search_input.send_keys(Keys.ENTER)
    time.sleep(1)

    # [3] 종목 코드 추출
    WebDriverWait(driver, 15).until(EC.url_contains("/order"))
    current_url = driver.current_url
    stock_code = current_url.split("/")[
        current_url.split("/").index("stocks") + 1
    ]
    print(f"[INFO] 종목 코드 추출 완료 → {stock_code}")

    # [4] 커뮤니티 페이지 접속
    community_url = f"https://www.tossinvest.com/stocks/{stock_code}/community"
    driver.get(community_url)
    time.sleep(1)

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "main article"))
    )
    print(f"[INFO] 커뮤니티 페이지 접속 완료: {community_url}")

    driver.quit()


if __name__ == "__main__":
    open_community_page("삼성전자")

# 출력결과
'''
[INFO] 종목 코드 추출 완료 → A005930
[INFO] 커뮤니티 페이지 접속 완료: https://www.tossinvest.com/stocks/A005930/community

'''