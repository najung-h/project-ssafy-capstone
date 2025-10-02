import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

# 크롬 드라이버 옵션
chrome_options = Options()
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--disable-extensions")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

# 이전 폴더의 크롬 드라이버 경로
service = Service(ChromeDriverManager().install())


def fetch_visible_comments(company_name, limit=20, max_scroll=10):
    """
    토스증권 커뮤니티에서 특정 종목의 '화면에 로드된 댓글' 텍스트를 수집합니다.
    - company_name : 검색창에 입력할 회사명(예: "삼성전자")
    - limit        : 최소 수집 목표 개수(초과 수집 가능, 반환 시 슬라이스)
    - max_scroll   : 스크롤 반복 횟수 상한(무한스크롤 페이지 보호)

    [작동 개요]
      1) tossinvest.com 접속 → '/'키로 상단 검색창 열기
      2) 회사명 입력/엔터 → 종목 주문 페이지로 이동(주소에 /stocks/{코드}/order 패턴)
      3) URL에서 종목코드 추출 → /community 페이지로 이동
      4) 스크롤을 반복하며 보이는 댓글 span을 모아 중복 없이 누적
      5) limit 충족 또는 더 내려갈 게 없으면 중단 → 수집 결과 반환

    [중요 주의]
      - 사이트 구조/클래스명은 언제든 바뀔 수 있어 선택자가 쉽게 깨집니다.
      - 서비스 약관/robots 정책을 준수하세요. 과도한 빈도는 차단/법적 문제 소지.
      - UI 핫키('/')는 사이트 변경 시 동작하지 않을 수 있으니 대체 경로(검색 아이콘 클릭)도 준비 권장.
    """
    driver = webdriver.Chrome(service=service, options=chrome_options)

    # 1. Toss 메인 접속
    driver.get("https://www.tossinvest.com/")
    time.sleep(1)

    # 2. 회사명 검색
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

    # 3. 종목 코드 추출
    WebDriverWait(driver, 15).until(EC.url_contains("/order"))
    current_url = driver.current_url
    stock_code = current_url.split("/")[
        current_url.split("/").index("stocks") + 1
    ]

    # 4. 커뮤니티 페이지 접속
    community_url = f"https://www.tossinvest.com/stocks/{stock_code}/community"
    driver.get(community_url)
    time.sleep(1)

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "main article"))
    )

    # 5. 댓글 수집 (스크롤 반복하며 누적)
    comments = []
    last_height = driver.execute_script("return document.body.scrollHeight")

    for scroll in range(max_scroll):
        spans = driver.find_elements(
            By.CSS_SELECTOR, "article.comment span.tw-1r5dc8g0._60z0ev1"
        )
        # 이유 - 개발자 도구로 보면 이렇게 되어 있어서 클래스 선택자로 이용했네요.
        # <span class="tw-1r5dc8g0 _60z0ev1 _60z0ev6 _60z0ev0 _1tvp9v41 _1sihfl60" style="--tds-wts-font-weight: 500; --tds-wts-foreground-color: var(--wts-adaptive-grey700); --tds-wts-line-height: 1.45; --tds-wts-font-size: 15px;">계속오르는 주식은 없습니다.</span>

        # 새 댓글 누적 (중복 제거)
        # 그냥 set 써도 될 것 같은데
        for span in spans:
            text = span.text.strip()
            if text and text not in comments:
                comments.append(text)

        # 목표 개수 이상 모이면 종료
        if len(comments) >= limit:
            break

        # 스크롤 다운
        driver.execute_script(
            "window.scrollTo(0, document.body.scrollHeight);"
        )
        time.sleep(1)

        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:  # 더 이상 내려갈 게 없으면 종료
            break
        last_height = new_height

    driver.quit()
    return comments[:limit]


if __name__ == "__main__":
    comments = fetch_visible_comments("삼성전자", limit=20)
    print("\n=== 커뮤니티 댓글 (최대 20개) ===")
    if not comments:
        print("댓글을 가져오지 못했습니다.")
    for i, c in enumerate(comments, 1):
        print(f"{i:02d}. {c}")


# 출력결과
'''
DevTools listening on ws://127.0.0.1:61724/devtools/browser/7c990bea-9b50-493c-9b36-feaa510f60bf

=== 커뮤니티 댓글 (최대 20개) ===
01. 계속오르는 주식은 없습니다.
02. 잘먹고갑니다
03. ㅋㅋㅋ 그동안 오른건 생각안하고
조금내렷다고 개잡주래 ㅋㅋ
급등할때 타니까 쳐물리지 ㅉㅉㅉ
걍주식 하지마시고 적금드세요~~
돈날리고 깡통차지마시고
04. 이재명이 쉽xx
05. 주식장은 뻔하지 않나요
여태 잘 올랐으니 조정도 있겠죠
무슨 올를땐 자기가 잘나 올랐다고 좋아 난리치다가 내릴땐 정부탓이나 하고 왜 그럴까요
누가 주식하라고 부추긴것도 아닌데 좋고 희망적인 이야기만 올리시면 좋겠네요
06. 개미 기관 매도ㅜㅜ
07. 대한민국은 이상없고...개명이가 문제..
08. 환희에 팔고 상승장에 타지말고 공포에 사고 하락장에 내리지마세요
09. 다 나가주세요.
저 혼자 있고 싶어요.
10. 오늘 9만 갈줄알았는데
11. #삼성전자
12. 추석 지나면 오르지 않을까요?
일단 조금씩 추매 하면 될꺼같은데..
13. 이번달배당금 29일락일입니다
잘생각들하구파세요~~
14. 환율좀보고 정신차러라 니들 ㅋㅋ
15. 아나
16. 환율보고 잠시 정리합니다.

나중에 뵈어요
17. 적정가
18. 85층 구조대 기다리면서 다음주에 올게,,,, 일에 집중이 안댄다,,,,,
이러다가 주말도 푹 못쉬겠엉,,,, 삼성,,,, 나 핸드폰 부터 모든 전자기기 삼성쓰니깐 배신 하지말아줘,,,,,,,, 울다 지쳐 잠드는날,,,,버리 지말아줘,,,,,,,,
19. ㅋㅋ와 정치들먹이면서 선동하는애들 많아진거보면
진짜 댓글부대란게 있긴하구나 ㄷㄷ 소름...
20. 하……어제 팔았어야했나..?ㅜㅜㅜㅜ
'''