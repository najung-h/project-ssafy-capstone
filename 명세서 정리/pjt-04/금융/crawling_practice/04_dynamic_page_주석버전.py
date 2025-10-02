# 표준 라이브러리 ----------------------------------------------------------------
import time                       # 고정 대기(캡차 수동 입력 시간 확보 등)에 사용
from pathlib import Path          # OS 독립적인 경로 처리(Windows/Unix 공통)

# 서드파티 라이브러리 ------------------------------------------------------------
from bs4 import BeautifulSoup     # HTML 파싱/탐색/정제
from selenium import webdriver     # 브라우저 자동화를 위한 Selenium 엔트리 포인트
from selenium.webdriver.chrome.service import Service  # ChromeDriver 프로세스 관리

# 1) 드라이버 초기화 함수 ---------------------------------------------------------
def get_driver():
    """
    로컬 chromedriver를 사용해 WebDriver 객체를 생성합니다.
    - 옵션/서비스 설정을 한 곳에서 관리하여 재사용성·유지보수성 향상
    - 실패(드라이버 미존재 등) 시 명시적 예외로 빠르게 원인 파악
    """
    # 1-1) ChromeDriver 바이너리 경로 지정
    #      Path를 쓰면 Windows의 '\\'와 Unix의 '/' 차이를 신경 쓰지 않아도 됩니다.
    chromedriver_path = Path("chromedriver-win64/chromedriver.exe")

    # 1-2) 드라이버 존재 여부 선검사
    #      - 없으면 Selenium 내부의 난해한 에러 대신, FileNotFoundError로 즉시 중단/안내.
    if not chromedriver_path.exists():
        raise FileNotFoundError(
            "chromedriver-win64/chromedriver.exe 파일이 존재하지 않습니다."
        )

    # 1-3) 크롬 실행 옵션 구성
    chrome_options = webdriver.ChromeOptions()

    #      (선택) 헤드리스 모드: GUI 없이 백그라운드에서 렌더링
    #      - CI/서버 환경에서 유용하지만, 구글은 헤드리스에서 자동화 탐지가 더 쉬울 수 있어 기본 비활성화.
    # chrome_options.add_argument("--headless")  # 필요 시 활성화

    #      사용자 에이전트(User-Agent) 지정
    #      - 기본 UA가 'Headless' 등 자동화 티가 나면 차단될 수 있어 일반 브라우저 UA로 위장.
    #      - 너무 오래된 UA는 또 다른 차단/비정상 동작 원인 → 근래 버전 권장.
    chrome_options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36"
    )

    #      자동화 배너/플래그 제거
    #      - 'Chrome is being controlled by automated test software' 배너 제거
    #      - 간단한 자동화 탐지 우회에 도움(완전한 회피는 아님).
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option("useAutomationExtension", False)
    chrome_options.add_argument("disable-blink-features=AutomationControlled")

    # 1-4) Service 객체 생성 (Selenium 4 권장)
    #      - 드라이버 프로세스의 생명주기를 명시적으로 관리
    service = Service(executable_path=str(chromedriver_path))

    # 1-5) WebDriver 인스턴스 생성
    #      - 옵션/서비스 결합하여 실제 크롬 프로세스를 기동
    return webdriver.Chrome(service=service, options=chrome_options)


# 2) 구글 검색 결과 가져오기 ------------------------------------------------------
def get_google_data(keyword):
    """
    지정된 키워드로 Google 검색 결과 페이지를 로드한 뒤,
    - 렌더링된 DOM의 HTML을 수집하여 BeautifulSoup으로 파싱
    - 특정 컨테이너(div.notranslate) 내부에서 결과 타이틀(.VuuXrf)을 추출
    - 추출한 타이틀을 콘솔 출력 및 파일로 저장

    [중요 주의]
    - Google은 자동화/스크래핑을 강하게 제한(Captcha/차단)합니다.
    - 서비스 약관과 robots 정책을 준수하고, 대량/주기 수집은 공식 API 고려가 바람직합니다.
    """
    # 2-1) 드라이버 생성 (옵션/경로는 get_driver에서 일원화)
    driver = get_driver()
    try:
        # 2-2) 검색 URL 생성
        #      - 현재는 f-string으로 단순 결합. 한글/특수문자 키워드는 URL 인코딩 필요 가능.
        #        안전하게는 urllib.parse.quote_plus 사용 권장.
        url = f"https://www.google.com/search?q={keyword}"

        # 2-3) 페이지 이동
        #      - driver.get()은 네트워크 응답까지 기다리지만 JS 렌더링 완료 보장은 아님.
        #        필요한 경우 WebDriverWait으로 특정 요소 렌더링을 기다리면 더 견고합니다.
        driver.get(url)
        print(f"[DEBUG] 구글 검색 페이지 접속 완료 → {url}")

        # 2-4) 고정 대기 (캡차/추가 로딩 대응)
        #      - 자동화 트래픽으로 판단되면 사람이 직접 캡차를 풀 시간 필요.
        #      - 고정 sleep은 과하거나 부족할 수 있음 → 실제 운영에서는 조건부 대기(WebDriverWait) 권장.
        print("[DEBUG] 캡차가 있다면 10초 안에 입력하세요.")
        time.sleep(10)

        # 2-5) 렌더링된 DOM의 HTML 수집
        html = driver.page_source

        # 2-6) BeautifulSoup 파싱
        #      - 'html.parser'는 내장 파서(의존성 X). 대규모/불완전 HTML에는 lxml이 더 빠르고 견고할 수 있음.
        soup = BeautifulSoup(html, "html.parser")

        # 2-7) 검색 결과 제목 추출
        #      - 현재 선택자는 'div.notranslate' 컨테이너 내부의 '.VuuXrf' 엘리먼트.
        #      - Google은 클래스명이 빈번히 바뀌므로(AB 테스트/리전별 DOM 차이) 매우 취약합니다.
        #        실패 시 선택자 전략 재검토 필요(아래 "개선 팁" 참고).
        results = soup.select("div.notranslate")  # 상위 컨테이너 후보들
        titles = []                                # 추출된 타이틀 누적 리스트
        for result in results:
            # 각 컨테이너에서 타이틀(현재 DOM 기준으로 보이는 클래스)을 찾음
            title = result.select_one(".VuuXrf")
            if title:
                # get_text(strip=True)와 동일하나, 명확성을 위해 분리
                title_text = title.get_text().strip()
                print("제목 =", title_text)   # 콘솔 디버깅 용도
                titles.append(title_text)

        # 2-8) 결과를 파일로 저장
        #      - 인코딩을 utf-8로 고정하여 한글 깨짐 방지
        #      - prettify가 아닌 순수 텍스트 목록을 저장(가볍고 바로 확인 가능)
        with open("04_result.txt", "w", encoding="utf-8") as result_file:
            for idx, title in enumerate(titles, 1):
                result_file.write(f"{idx}. {title}\n")
        print(f"[DEBUG] 04_result.txt 저장 완료 (총 {len(titles)}개)")

    # 2-9) 예외 발생 여부와 관계없이 드라이버 종료(리소스 누수 방지)
    finally:
        driver.quit()
        print("[DEBUG] 브라우저 종료 완료")


# 3) 실행부 ---------------------------------------------------------------------
if __name__ == "__main__":
    # 한글 키워드 예시
    # - 안전하게는 quote_plus("나정현")로 인코딩 후 URL 구성 권장.
    keyword = "나정현"
    get_google_data(keyword)


### 출력
'''
DevTools listening on ws://127.0.0.1:62560/devtools/browser/cf2b9cf2-f08c-4550-be28-2aeb015b4ce4
[DEBUG] 구글 검색 페이지 접속 완료 → https://www.google.com/search?q=나정현
[DEBUG] 캡차가 있다면 10초 안에 입력하세요.
[21124:24100:0926/122023.689:ERROR:google_apis\gcm\engine\registration_request.cc:291] Registration response error message: DEPRECATED_ENDPOINT
Created TensorFlow Lite XNNPACK delegate for CPU.
제목 = Google Sites
제목 = 성신여자대학교
제목 = LinkedIn
제목 = litt.ly
제목 = 교보문고
제목 = LinkedIn · 나정현
제목 = DBpia
제목 = 국립중앙도서관
제목 = Google Sites
[DEBUG] 04_result.txt 저장 완료 (총 9개)
[DEBUG] 브라우저 종료 완료
'''