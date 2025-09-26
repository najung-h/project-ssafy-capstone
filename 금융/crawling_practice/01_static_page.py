import requests
from bs4 import BeautifulSoup


def crawling_basic():
    """
    웹 크롤링의 기본 예제를 수행하는 함수입니다.

    이 함수는 다음과 같은 작업을 수행합니다.
      1. 지정한 URL(http://quotes.toscrape.com/tag/love/)에 HTTP GET 요청을 보내 HTML 소스를 가져옵니다.
      2. 가져온 HTML 소스를 BeautifulSoup를 사용하여 파싱합니다.
      3. 파싱된 결과에서 다양한 방법(find, find_all, select_one, select)을 사용해
         특정 HTML 요소들을 검색하고 그 내용을 출력합니다.

    주의: 웹사이트의 구조가 변경될 경우, 선택자(selector) 및 태그명이 달라질 수 있으므로,
           코드의 일부 결과가 달라질 수 있습니다.
    """
    # 1. 크롤링할 웹페이지 URL을 문자열로 지정합니다.
    url = 'http://quotes.toscrape.com/tag/love/'

    # 2. requests 라이브러리의 get() 함수를 사용하여 지정된 URL로부터 HTML 데이터를 가져옵니다.
    response = requests.get(url)

    # 3. 응답 객체의 text 속성을 통해 HTML 문서(문자열 형태)를 추출합니다.
    html_text = response.text

    # 4. BeautifulSoup을 사용하여 HTML 텍스트를 파싱합니다.
    #    'html.parser'를 파서로 지정하여 HTML 문서를 구조화된 형태로 변환합니다.
    soup = BeautifulSoup(html_text, 'html.parser')

    # 5. 첫 번째 <a> 태그를 검색합니다.
    #    find() 함수는 지정한 태그의 첫 번째 요소만 반환합니다.
    main = soup.find('a')
    print(f'첫 번째 a 태그의 텍스트: {main.text}')

    # 6. 페이지 내에 존재하는 모든 <a> 태그를 검색합니다.
    #    find_all() 함수는 해당 태그를 모두 리스트 형태로 반환합니다.
    a_tags = soup.find_all('a')
    print(f'전체 a 태그 리스트: {a_tags}')

    # 7. CSS 선택자를 사용하여 클래스 이름이 'text'인 요소 중 첫 번째 요소를 검색합니다.
    #    select_one() 함수는 선택자와 일치하는 첫 번째 요소를 반환합니다.
    word = soup.select_one('.text')
    print(
        f'CSS 선택자(.text)를 사용해 찾은 첫 번째 요소의 텍스트: {word.text}'
    )

    # 8. CSS 선택자를 사용하여 클래스 이름이 'text'인 모든 요소를 검색합니다.
    #    select() 함수는 선택자와 일치하는 모든 요소를 리스트로 반환합니다.
    words = soup.select('.text')
    # 각 요소의 텍스트를 반복문을 통해 출력합니다.
    for w in words:
        print(f'요소 텍스트: {w.text}')

    # 추가: BeautifulSoup의 prettify() 함수를 사용하면, HTML 코드를 들여쓰기가 잘된 형태로 출력할 수 있습니다.
    # print(soup.prettify())


# crawling_basic() 함수를 실행하여 웹 크롤링 과정을 확인합니다.
crawling_basic()
