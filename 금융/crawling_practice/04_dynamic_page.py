import time
from pathlib import Path

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service


# 1) 드라이버 초기화 함수
def get_driver():
    """
    로컬 chromedriver를 사용해 WebDriver 객체를 생성합니다.
    - 옵션/서비스 설정을 한 곳에서 관리
    """
    chromedriver_path = Path("chromedriver-win64/chromedriver.exe")
    if not chromedriver_path.exists():
        raise FileNotFoundError(
            "chromedriver-win64/chromedriver.exe 파일이 존재하지 않습니다."
        )

    chrome_options = webdriver.ChromeOptions()
    # chrome_options.add_argument("--headless")  # 필요 시 활성화
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


# 2) 구글 검색 결과 가져오기
def get_google_data(keyword):
    """
    지정된 키워드를 사용하여 Google 검색 결과 페이지의 HTML을 가져온 뒤,
    BeautifulSoup을 통해 구조화된 결과물에서 제목들을 추출하고, 파일로 저장합니다.
    """
    driver = get_driver()  # ✅ 분리된 드라이버 설정 사용
    try:
        # 1) 검색 URL 접속
        url = f"https://www.google.com/search?q={keyword}"
        driver.get(url)
        print(f"[DEBUG] 구글 검색 페이지 접속 완료 → {url}")

        # 2) 로딩 대기 (캡차가 있다면 직접 처리)
        print("[DEBUG] 캡차가 있다면 10초 안에 입력하세요.")
        time.sleep(10)

        # 3) HTML 소스 가져오기
        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")

        # 4) 검색 결과 제목 추출
        results = soup.select("div.notranslate")
        titles = []
        for result in results:
            title = result.select_one(".VuuXrf")
            if title:
                title_text = title.get_text().strip()
                print("제목 =", title_text)
                titles.append(title_text)

        # 5) 결과를 파일로 저장
        with open("04_result.txt", "w", encoding="utf-8") as result_file:
            for idx, title in enumerate(titles, 1):
                result_file.write(f"{idx}. {title}\n")
        print(f"[DEBUG] 04_result.txt 저장 완료 (총 {len(titles)}개)")
    finally:
        driver.quit()
        print("[DEBUG] 브라우저 종료 완료")


# 3) 실행부
if __name__ == "__main__":
    keyword = "파이썬"
    get_google_data(keyword)
