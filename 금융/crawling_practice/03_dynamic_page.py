import time
from pathlib import Path

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service


def get_driver():
    """
    크롬 드라이버를 초기화하고 WebDriver 객체를 반환합니다.
    - 옵션 설정
    - chromedriver-win64 폴더에서 드라이버 실행
    """
    # 크롬 옵션 설정
    options = webdriver.ChromeOptions()
    # options.add_argument("--headless")  # 필요시 활성화
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36"
    )
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    options.add_argument("disable-blink-features=AutomationControlled")

    # chromedriver-win64 폴더의 드라이버 사용
    chromedriver_path = Path("chromedriver-win64/chromedriver.exe")
    if not chromedriver_path.exists():
        raise FileNotFoundError(
            "chromedriver-win64/chromedriver.exe 파일을 찾을 수 없습니다."
        )
    service = Service(executable_path=str(chromedriver_path))

    return webdriver.Chrome(service=service, options=options)


def get_google_data(keyword):
    """
    지정된 키워드를 사용하여 Google 검색 결과 페이지를 로드한 후,
    페이지의 HTML 소스를 추출하여 BeautifulSoup으로 파싱하고,
    검색 결과의 제목 정보를 출력합니다.
    """
    driver = get_driver()  # <-- 드라이버 생성
    try:
        # 1) 검색 URL 생성
        url = f"https://www.google.com/search?q={keyword}"
        driver.get(url)

        # 캡차 입력 대기 (10초)
        time.sleep(10)

        # 2) HTML 소스 추출
        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")

        # 3) div 태그 중 class 가 VuuXrf 인 요소 출력
        result_stats = soup.select_one(".VuuXrf")
        if result_stats:
            print("[DEBUG] 검색 결과 제목:", result_stats.text)
        else:
            print(
                "[WARN] '.VuuXrf' 요소를 찾지 못했습니다. (구글 구조 변경 가능)"
            )

        # 4) 전체 HTML 저장
        with open("03_google_result.html", "w", encoding="utf-8") as f:
            f.write(soup.prettify())
        print("[DEBUG] 03_google_result.html 저장 완료")
    finally:
        driver.quit()


if __name__ == "__main__":
    keyword = "파이썬"
    get_google_data(keyword)
