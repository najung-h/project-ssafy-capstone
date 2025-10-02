# 표준 라이브러리 -----------------------------------------------------------
import time                       # 단순한 대기(sleep)나 타이밍 측정을 위해 사용
from pathlib import Path          # OS에 독립적인 파일/디렉토리 경로 처리 (Windows/Unix 공통)

# 서드파티 라이브러리 -------------------------------------------------------
from bs4 import BeautifulSoup     # HTML 파싱 및 DOM 탐색/정제용 라이브러리
from selenium import webdriver     # 브라우저 자동화를 위한 Selenium 진입점
from selenium.webdriver.chrome.service import Service  # ChromeDriver 프로세스 관리를 위한 Service 객체


# ===== 드라이버 생성 함수 ====================================================
def get_driver():
    """
    크롬 드라이버를 초기화하여 WebDriver 객체를 반환합니다.
    - 한 곳에서 옵션/경로 세팅을 관리하면 코드 재사용성과 유지보수성이 올라갑니다.
    - 실패(예: 드라이버 없음) 시 즉시 오류를 내도록 하여 원인 파악이 쉬워집니다.
    """
    # 1) 드라이버 바이너리 경로 정의
    #    Path를 쓰면 OS별 경로 구분자(\\ vs /) 문제 없이 안전하게 처리됩니다.
    # 헐,,,, 이걸로 고생했던 기억이 새록새록한데,
    # 이런 해결 방법이 있군요....
    chromedriver_path = Path("chromedriver-win64/chromedriver.exe")

    # 2) 드라이버 파일 존재 여부 확인
    #    - 파일이 없으면 Selenium이 내부적으로 던지는 난해한 에러보다,
    #      명확한 FileNotFoundError로 빠르게 원인을 알 수 있습니다.
    if not chromedriver_path.exists():
        raise FileNotFoundError(
            "chromedriver-win64/chromedriver.exe 파일이 존재하지 않습니다."
        )

    # 3) 크롬 실행 옵션 세팅
    #    - 브라우저 동작/식별 관련 옵션을 중앙에서 제어합니다.
    chrome_options = webdriver.ChromeOptions()

    #    (선택) 헤드리스 모드: UI 없이 백그라운드에서 렌더링
    #    - CI 서버나 컨테이너 환경에서 자주 사용합니다.
    #    - 캡차가 뜨는 페이지(구글 등)는 헤드리스에서 차단이 더 심해질 수 있어 기본 비활성화.
    # chrome_options.add_argument("--headless")

    #    사용자 에이전트(User-Agent) 지정:
    #    - 일부 사이트는 헤드리스/자동화 UA를 차단하므로 일반 브라우저처럼 위장할 수 있습니다.
    #    - 너무 오래된 UA는 또다른 차단/이상동작을 유발할 수 있어 최신 또는 근래 UA 권장.
    chrome_options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36"
    )

    #    자동화 배너/플래그 숨김:
    #    - Selenium 실행 시 'Chrome is being controlled by automated test software' 배너 제거
    #    - 일부 사이트의 자동화 감지 로직을 살짝 우회하지만,
    #      완전한 우회는 아니며 차단을 100% 막지 못합니다.
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option("useAutomationExtension", False)
    chrome_options.add_argument("disable-blink-features=AutomationControlled")

    # 4) Service 객체 생성
    #    - Selenium 4에서 권장되는 방식: Service로 드라이버 경로/프로세스 관리
    service = Service(executable_path=str(chromedriver_path))

    # 5) WebDriver 인스턴스 생성
    #    - 옵션과 서비스를 결합하여 실제 브라우저 프로세스를 띄웁니다.
    #    - 실패 시 예외가 발생하므로 상위 호출부에서 처리 가능.
    return webdriver.Chrome(service=service, options=chrome_options)


# ===== 크롤링(수집) 함수 =====================================================
def get_google_data(keyword):
    """
    지정된 키워드를 사용하여 Google 검색 결과 페이지의 HTML을 가져온 뒤,
    BeautifulSoup으로 구조화(파싱)하여 파일로 저장합니다.

    [중요한 주의사항]
    - Google은 자동화/스크래핑을 강하게 제한합니다(로봇 차단, Captcha 등).
    - 서비스 약관 및 로봇 배제 규약을 반드시 확인하세요.
    - 운영 환경에서는 요청 간 지연/랜덤 대기, 프록시 회전, 정식 API(예: Custom Search API) 고려가 필요합니다.
    """
    # 1) 드라이버 초기화
    #    - 별도 함수로 분리되어 있어 옵션/경로 변경이 쉬움
    driver = get_driver()

    try:
        # 2) 대상 URL 구성
        #    - 간단히 쿼리스트링으로 검색 키워드를 붙입니다.
        #    - 실무에서는 urllib.parse.quote_plus로 인코딩을 권장합니다.
        url = f"https://www.google.com/search?q={keyword}"

        # 3) 페이지 로드
        #    - driver.get()은 네트워크 응답을 기다리지만,
        #      JS 렌더링까지 완전히 끝났다고 보장하지 않습니다.
        driver.get(url)
        print(f"[DEBUG] 구글 검색 페이지 접속 완료 → {url}")

        # 4) Captcha(사람 확인) 대응
        #    - 구글은 자동화 트래픽을 감지하면 Captcha를 띄웁니다.
        #    - 여기서는 사용자가 직접 풀고 돌아오도록 15초 대기합니다.
        #    - 운영 자동화에서는 이 지점이 병목이므로,
        #      (a) 정식 API 사용, (b) 요청 빈도/패턴 완화, (c) 대안 검색 엔진 고려가 현실적입니다.
        print("[DEBUG] 캡차가 뜨면 직접 입력 후 15초 대기...")
        time.sleep(15)

        # 5) 현재 DOM의 HTML 소스 가져오기
        #    - Selenium은 JS 렌더링 후의 DOM을 반환하므로
        #      정적 요청(requests.get) 대비 완성된 구조를 얻을 가능성이 큼.
        html = driver.page_source

        # 6) BeautifulSoup 파싱
        #    - 'html.parser'는 표준 파서(파이썬 내장). 복잡한 페이지에는 lxml이 더 빠르고 견고할 수 있음.
        soup = BeautifulSoup(html, "html.parser")

        # 7) 미리보기 출력
        #    - soup.prettify()는 보기 좋게 들여쓴 문자열을 반환하지만 큰 페이지는 매우 큼.
        #      콘솔 스팸을 막기 위해 앞 1000자만 출력합니다.
        print("[DEBUG] HTML 소스 (앞부분 1000자만 미리보기)")
        print(soup.prettify()[:1000])
        print("[DEBUG] ...생략 (전체는 파일에서 확인하세요)")

        # 8) 파일로 전체 HTML 저장
        #    - 인코딩은 유니코드 한글 안전을 위해 utf-8 지정.
        #    - 결과 리포지토리 커밋 시 비밀정보/쿠키가 섞이지 않도록 주의.
        with open("02_result.txt", "w", encoding="utf-8") as file:
            file.write(soup.prettify())
        print("[DEBUG] 02_result.txt 저장 완료")

    # finally 블록은 try 내부 어디에서 예외가 나도 반드시 실행됩니다.
    # 브라우저 프로세스를 남기지 않도록 종료 처리 필수!
    finally:
        driver.quit()
        print("[DEBUG] 브라우저 종료 완료")


# ===== 실행부(엔트리 포인트) ================================================
if __name__ == "__main__":
    # 예시 키워드:
    # - 한글 키워드는 URL 인코딩이 필요할 수 있습니다.
    #   현재 코드는 간단화를 위해 raw 문자열을 사용하지만,
    #   안전하게는 urllib.parse.quote_plus("나정현") 권장.
    keyword = "나정현"

    # 크롤링 실행
    get_google_data(keyword)


# 실행 결과 예시
# - QUOTA_EXCEEDED : 크롬 내 일부 서비스(푸시/클라우드 메시징 등) 관련 내부 경고로,
#   크롤링 실패 원인과 직접적 연관이 없는 경우가 많습니다.

# - TensorFlow Lite delegate : 크롬 일부 컴포넌트/미디어 처리에서 출력될 수 있는 메시지로
#   무시 가능.


'''

DevTools listening on ws://127.0.0.1:53147/devtools/browser/01a2ea88-6c62-45c8-a309-8acccd518b93
[DEBUG] 구글 검색 페이지 접속 완료 → https://www.google.com/search?q=나정현
[DEBUG] 캡차가 뜨면 직접 입력 후 15초 대기...
[23468:21632:0926/120555.125:ERROR:google_apis\gcm\engine\registration_request.cc:291] Registration response error message: QUOTA_EXCEEDED
Created TensorFlow Lite XNNPACK delegate for CPU.
[DEBUG] HTML 소스 (앞부분 1000자만 미리보기)
<html itemscope="" itemtype="http://schema.org/SearchResultsPage" lang="ko">
 <head>
  <meta charset="utf-8"/>
  <meta content="origin" name="referrer"/>
  <link href="//www.gstatic.com/images/branding/searchlogo/ico/favicon.ico" rel="icon"/>
  <meta content="/images/branding/googleg/1x/googleg_standard_color_128dp.png" itemprop="image"/>
  <title>
   나정현 - Google 검색
  </title>
  <script nonce="">
   window._hst=Date.now();
  </script>
  <script nonce="">
   (function(){var b=window.addEventListener;window.addEventListener=function(a,c,d){a!=="unload"&&b(a,c,d)};}).call(this);(function(){var _g={kEI:'FQPWaIqmJKTc2roPkevi-A4',kEXPI:'31',kBL:'deBz',kOPI:89978449};(function(){var a;((a=window.google)==null?0:a.stvsc)?google.kEI=_g.kEI:window.google=_g;}).call(this);})();(function(){google.sn='web';google.kHL='ko';google.rdn=false;})();(function(){
var g=this||self;function k(){return window.google&&window.google.kOPI||null};var l,m=[];function n(a){for(var b;a&&(!a.getAttribute||!(b=a.get   
[DEBUG] ...생략 (전체는 파일에서 확인하세요)
[DEBUG] 02_result.txt 저장 완료
[DEBUG] 브라우저 종료 완료
'''
