import time
from pathlib import Path

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service


# ===== 드라이버 생성 함수 =====
def get_driver():
    """
    크롬 드라이버를 초기화하여 WebDriver 객체를 반환합니다.
    - 옵션 및 경로 설정을 한 곳에서 관리
    """
    chromedriver_path = Path("chromedriver-win64/chromedriver.exe")
    if not chromedriver_path.exists():
        raise FileNotFoundError(
            "chromedriver-win64/chromedriver.exe 파일이 존재하지 않습니다."
        )

    # 크롬 옵션 세팅
    chrome_options = webdriver.ChromeOptions()
    # chrome_options.add_argument("--headless")  # 필요시 활성화
    chrome_options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36"
    )
    chrome_options.add_experimental_option(
        "excludeSwitches", ["enable-automation"]
    )
    chrome_options.add_experimental_option("useAutomationExtension", False)
    chrome_options.add_argument("disable-blink-features=AutomationControlled")

    service = Service(executable_path=str(chromedriver_path))
    return webdriver.Chrome(service=service, options=chrome_options)


# ===== 크롤링 함수 =====
def get_google_data(keyword):
    """
    지정된 키워드를 사용하여 Google 검색 결과 페이지의 HTML을 가져온 뒤,
    BeautifulSoup으로 구조화하여 파일로 저장합니다.
    """
    driver = get_driver()  # ✅ 드라이버 함수 호출

    try:
        # 1) 구글 접속
        url = f"https://www.google.com/search?q={keyword}"
        driver.get(url)
        print(f"[DEBUG] 구글 검색 페이지 접속 완료 → {url}")

        # 2) 캡차 입력 대기
        print("[DEBUG] 캡차가 뜨면 직접 입력 후 15초 대기...")
        time.sleep(15)

        # 3) 페이지 HTML 소스 가져오기
        html = driver.page_source

        # 4) BeautifulSoup으로 파싱
        soup = BeautifulSoup(html, "html.parser")

        # 5) HTML 일부 출력
        print("[DEBUG] HTML 소스 (앞부분 1000자만 미리보기)")
        print(soup.prettify()[:1000])
        print("[DEBUG] ...생략 (전체는 파일에서 확인하세요)")

        # 6) 파일 저장
        with open("02_result.txt", "w", encoding="utf-8") as file:
            file.write(soup.prettify())
        print("[DEBUG] 02_result.txt 저장 완료")

    finally:
        driver.quit()
        print("[DEBUG] 브라우저 종료 완료")


# ===== 실행부 =====
if __name__ == "__main__":
    keyword = "파이썬"
    get_google_data(keyword)
