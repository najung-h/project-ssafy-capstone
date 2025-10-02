[toc]

> 📌반드시 이 문서를 읽으면서 실습 후 관통 프로젝트를 진행 해주세요!📌

# 크롤링 입문: 예제 파일 설명

- 웹 크롤링(Web Crawling)
  - 웹사이트에서 원하는 데이터를 자동으로 가져오는 기술

- 크롤링은 크게 정적 페이지와 동적 페이지로 나눌 수 있습니다.



## 01_static_page.py — 정적 페이지 크롤링

> 사용 라이브러리: `requests`, `BeautifulSoup`

- 정적 페이지란?
  - HTML 코드가 고정되어 있고, 브라우저에서 실행할 때 추가로 데이터가 바뀌지 않는 웹페이지
  - 예시: 단순 글 목록 페이지, 네이버 메인 페이지

- 동작 과정
  - `requests.get(url)`: 서버에 요청을 보내서 HTML 소스를 가져옴
  - `BeautifulSoup(html, "html.parser")`: 가져온 HTML을 구조화
  - `.find(), .find_all(), .select_one()` 등을 활용해 원하는 태그와 내용을 추출

- 예제 사이트: [Quotes to Scrape](http://quotes.toscrape.com/tag/love/)
  - 이 사이트는 연습용으로 많이 쓰이며, "Love" 태그가 붙은 명언들을 가져옵니다.

- 핵심 요약
  - 정적 페이지는 requests + BeautifulSoup 조합만으로 충분합니다.
  - `requests` 로 페이지를 가져와서
  - `BeautifulSoup` 로 파싱하자
  
  

---



## 02_dynamic_page.py — 동적 페이지 크롤링 (구글 HTML 저장)

>  사용 라이브러리: `selenium`, `BeautifulSoup`

- 동적 페이지란?
  - HTML 코드만으로는 데이터가 보이지 않고, 자바스크립트 실행 후에 데이터가 채워지는 웹페이지
  - 예시: 구글 검색, 네이버 뉴스 댓글

- 동작 과정
  - `selenium` 으로 크롬 브라우저를 직접 실행
  - `driver.get(url)` 로 구글 검색 페이지 접속
  - 사람이 보는 것과 동일한 화면이 로딩된 뒤 HTML을 가져옴
  - `BeautifulSoup` 으로 파싱하여 파일(`02_result.txt`)로 저장

- 핵심 요약
  - 동적 페이지는 `requests` 만으로는 크롤링 불가
  - 브라우저를 직접 띄워주는 `selenium` 이 필요하다
  
  

---



## 03_dynamic_page.py — 구글 검색 결과 제목 추출

> 사용 라이브러리: `selenium`, `BeautifulSoup`

- 기능
  - 구글 검색 결과에서 특정 텍스트(제목)를 추출
  - HTML 전체 저장이 아니라 필요한 부분만 뽑아냄

- 동작 과정
  - `selenium` 으로 구글 검색 실행
  - `BeautifulSoup` 으로 HTML 파싱
  - CSS 선택자 `.VuuXrf` 를 이용해 검색 결과 제목 추출
  - 결과를 `google_result.html` 파일로 저장

- 핵심 요약
  - HTML 전체 저장 → 원하는 데이터만 추출하는 연습
  - 크롤링의 핵심은 "필요한 부분만 뽑아내기"
  
  

---



## 04_dynamic_page.py — 구글 검색 결과 여러 개 저장

> 사용 라이브러리: `selenium,` `BeautifulSoup`

- 기능
  - 구글 검색 결과에서 여러 개의 제목을 모아 텍스트 파일로 저장

- 동작 과정
  - 구글에서 키워드 검색
  - 검색 결과 페이지에서 여러 개의 제목 추출
  - 결과를 `04_result.txt` 파일에 순서대로 저장

- 핵심 요약
  - 반복문을 통해 원하는 데이터 여러 개 수집
  - 크롤링 결과를 파일로 정리하는 방법 학습




### 이제 05_toss_practice 에서  토스 크롤링을 실습해봅시다!