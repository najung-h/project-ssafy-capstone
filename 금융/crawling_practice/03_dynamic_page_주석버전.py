# 표준 라이브러리 -----------------------------------------------------------
import time                       # 단순 대기(캡차 수동 입력 시간 확보 등)에 사용
from pathlib import Path          # OS 독립적인 경로 처리(Windows/Unix 공통)

# 서드파티 라이브러리 -------------------------------------------------------
from bs4 import BeautifulSoup     # HTML 파싱/탐색/정제
from selenium import webdriver     # 브라우저 자동화를 위한 Selenium 엔트리 포인트
from selenium.webdriver.chrome.service import Service  # ChromeDriver 프로세스 관리용


def get_driver():
    """
    크롬 드라이버를 초기화하고 WebDriver 객체를 반환합니다.
    - 브라우저 옵션 설정(자동화 탐지 회피, UA 지정 등)
    - chromedriver-win64 폴더 내 드라이버 바이너리 사용
    - 실패 시 명시적 예외로 빠르게 원인 파악
    """
    # 1) 크롬 실행 옵션 생성
    #    - Selenium 4 기준: webdriver.ChromeOptions() 사용
    options = webdriver.ChromeOptions()

    #    (선택) 헤드리스 모드: 화면 없이 백그라운드 렌더링
    #    - CI/서버/컨테이너에서 유용하지만, 일부 사이트(특히 구글)는
    #      헤드리스에서 자동화 탐지가 더 잘 걸릴 수 있어 기본 비활성화.
    # options.add_argument("--headless")

    #    사용자 에이전트(User-Agent) 지정
    #    - 기본 UA가 'Headless' 등 자동화 티가 나면 차단될 수 있어 일반 브라우저 UA로 위장
    #    - 지나치게 오래된 UA는 반대로 차단/비정상 동작 유발 → 근래 버전 권장
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36"
    )

    #    자동화 배너 및 일부 자동화 플래그 비활성화
    #    - 브라우저 상단 '자동화로 제어 중' 배너 제거
    #    - 사이트의 간단한 자동화 탐지 우회에 약간 도움(완전한 회피 아님)
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    options.add_argument("disable-blink-features=AutomationControlled")

    # 2) ChromeDriver 경로 결정
    #    - Path를 쓰면 OS 경로 구분자 문제(\\ vs /) 없이 안전
    chromedriver_path = Path("chromedriver-win64/chromedriver.exe")

    #    드라이버 존재 여부 선검사
    #    - 없으면 Selenium 내부의 난해한 에러 대신 FileNotFoundError로 즉시 안내
    if not chromedriver_path.exists():
        raise FileNotFoundError(
            "chromedriver-win64/chromedriver.exe 파일을 찾을 수 없습니다."
        )

    # 3) Service 객체 준비 (Selenium 4 권장 방식)
    #    - 실행 경로/프로세스 생명주기를 명시적으로 관리
    service = Service(executable_path=str(chromedriver_path))

    # 4) WebDriver 인스턴스 생성
    #    - 옵션과 서비스 결합하여 실제 크롬 프로세스 기동
    return webdriver.Chrome(service=service, options=options)


def get_google_data(keyword):
    """
    지정된 키워드로 Google 검색 페이지를 로드한 뒤,
    - 현재 DOM의 HTML을 수집해 BeautifulSoup으로 파싱
    - 검색 결과 일부(특정 CSS 클래스)의 텍스트를 콘솔에 표시
    - prettify()된 전체 HTML을 파일로 저장

    [주의]
    - Google은 자동화/스크래핑을 강하게 제한(Captcha/차단)합니다.
    - 서비스 약관 및 robots 정책을 확인하고, 대량/주기 수집에는 공식 API 고려.
    """
    # 1) 드라이버 생성 (옵션/경로 등은 get_driver 내에서 일원화)
    driver = get_driver()
    try:
        # 2) 검색 URL 구성
        #    - f-string으로 간단히 결합했지만, 한글/특수문자 포함 시 URL 인코딩 필요할 수 있음
        #      (안전하게는 urllib.parse.quote_plus 사용 권장)
        url = f"https://www.google.com/search?q={keyword}"

        # 3) 페이지 로드
        #    - driver.get()은 네트워크 응답을 기다리지만 JS 렌더링 완료까지 보장하진 않음
        #      (필요 시 WebDriverWait으로 특정 요소 렌더링까지 대기)
        driver.get(url)

        # 4) 캡차/추가 로딩 대응을 위한 임시 대기
        #    - 자동화 트래픽으로 판단되면 캡차가 뜨므로 사람이 직접 해결할 시간을 줌
        #    - 고정 sleep은 과/부족 모두 가능 → 실제로는 조건부 대기(WebDriverWait) 권장
        time.sleep(10)

        # 5) 현재 DOM HTML 추출
        #    - Selenium은 JS 렌더링 반영된 DOM을 반환 → 정적 requests 대비 완성도가 높음
        html = driver.page_source

        # 6) BeautifulSoup으로 파싱
        #    - 내장 'html.parser'는 의존성 없고 간편, 속도/내구성은 lxml이 더 우수할 수 있음
        soup = BeautifulSoup(html, "html.parser")

        # 7) 특정 요소 선택/출력
        #    - 현재 코드는 CSS 클래스 '.VuuXrf'를 타겟팅(예: 결과 타이틀 영역에 사용된 적 있음)
        #    - 단, Google은 DOM/클래스를 수시로 바꾸므로 매우 취약한 선택자입니다.
        #      (실패 시 구조 변경 가능성 경고 출력)
        result_stats = soup.select_one(".VuuXrf")
        if result_stats:
            print("[DEBUG] 검색 결과 제목:", result_stats.text)
        else:
            print("[WARN] '.VuuXrf' 요소를 찾지 못했습니다. (구글 구조 변경 가능)")

        # 8) 전체 HTML 저장
        #    - prettify()는 가독성 좋지만 파일 크기가 커질 수 있음(디버깅용으로 적합)
        #    - 민감정보(쿠키/토큰 등)는 포함되지 않지만, 저장/공유 시 보안 유의
        with open("03_google_result.html", "w", encoding="utf-8") as f:
            f.write(soup.prettify())
        print("[DEBUG] 03_google_result.html 저장 완료")

    # 예외 발생 여부와 관계 없이 브라우저를 닫아 리소스 누수 방지
    finally:
        driver.quit()


if __name__ == "__main__":
    # 한글 키워드 예시
    # - 안전하게는 quote_plus("나정현")로 인코딩하여 URL에 넣는 것이 좋음
    keyword = "나정현"
    get_google_data(keyword)

# ===== 실행 결과 예시 ========================================================
# 아래 메시지는 크롬 내부 컴포넌트 경고/정보일 수 있으며,
# 크롤링 실패와 직접 관련 없을 때가 많습니다(무시 가능).
'''
DevTools listening on ws://127.0.0.1:56718/devtools/browser/4591b00d-dd2e-480c-a98a-9545a7553d90
[19332:23164:0926/121355.632:ERROR:google_apis\gcm\engine\registration_request.cc:291] Registration response error message: DEPRECATED_ENDPOINT   
Created TensorFlow Lite XNNPACK delegate for CPU.
[DEBUG] 검색 결과 제목: Google Sites
[DEBUG] 03_google_result.html 저장 완료

'''