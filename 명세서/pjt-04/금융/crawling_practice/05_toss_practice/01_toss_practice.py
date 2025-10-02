import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# 크롬 드라이버 옵션 설정
chrome_options = Options()
chrome_options.add_argument("--disable-gpu")  # GPU 비활성화
chrome_options.add_argument("--disable-extensions")  # 확장 프로그램 비활성화
chrome_options.add_argument("--no-sandbox")  # 샌드박스 모드 비활성화
chrome_options.add_argument(
    "--disable-dev-shm-usage"
)  # /dev/shm 공유 메모리 사용 제한 해제

# 이전 폴더의 크롬 드라이버를 읽어옴
service = Service("../chromedriver-win64/chromedriver.exe")


def open_toss_main():
    # 크롬 브라우저 실행
    driver = webdriver.Chrome(service=service, options=chrome_options)

    # TossInvest 메인 페이지 접속
    driver.get("https://www.tossinvest.com/")
    time.sleep(3)  # 3초간 페이지 확인

    # 페이지 로딩 완료까지 대기 (body 태그가 나타날 때까지)
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.TAG_NAME, "body"))
    )
    print("[1] TossInvest 메인 페이지 접속 완료")

    # 브라우저 종료
    driver.quit()


if __name__ == "__main__":
    open_toss_main()
