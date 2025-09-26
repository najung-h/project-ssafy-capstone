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


def search_company(company_name):
    driver = webdriver.Chrome(service=service, options=chrome_options)

    # TossInvest 메인 페이지 접속
    driver.get("https://www.tossinvest.com/")
    time.sleep(1)  # 페이지 확인용 대기

    # body 태그를 선택하여 '/' 입력 → 검색창 열림
    body = driver.find_element(By.TAG_NAME, "body")
    body.send_keys("/")
    time.sleep(1)

    # 검색 입력창 요소를 찾고, 회사명을 입력 후 Enter 입력
    search_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located(
            (By.XPATH, "//input[@placeholder='검색어를 입력해주세요']")
        )
    )
    search_input.send_keys(company_name)
    search_input.send_keys(Keys.ENTER)
    time.sleep(3)

    print(f"[2] '{company_name}' 검색 완료")
    driver.quit()


if __name__ == "__main__":
    search_company("삼성전자")
