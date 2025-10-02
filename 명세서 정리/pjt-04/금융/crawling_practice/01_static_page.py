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
    print('')
    print('')
    print('')

    # 6. 페이지 내에 존재하는 모든 <a> 태그를 검색합니다.
    #    find_all() 함수는 해당 태그를 모두 리스트 형태로 반환합니다.
    a_tags = soup.find_all('a')
    # print(f'전체 a 태그 리스트: {a_tags}')
    print('전체 a 태그 리스트', end = '')
    for a in list(a_tags):
        print(a)
    print('')
    print('')
    print('')

    # 7. CSS 선택자를 사용하여 클래스 이름이 'text'인 요소 중 첫 번째 요소를 검색합니다.
    #    select_one() 함수는 선택자와 일치하는 첫 번째 요소를 반환합니다.
    word = soup.select_one('.text')
    print(
        f'CSS 선택자(.text)를 사용해 찾은 첫 번째 요소의 텍스트: {word.text}'
    )
    print('')
    print('')
    print('')

    # 8. CSS 선택자를 사용하여 클래스 이름이 'text'인 모든 요소를 검색합니다.
    #    select() 함수는 선택자와 일치하는 모든 요소를 리스트로 반환합니다.
    words = soup.select('.text')
    # 각 요소의 텍스트를 반복문을 통해 출력합니다.
    for w in words:
        print(f'요소 텍스트: {w.text}')
        print('')

    # 추가: BeautifulSoup의 prettify() 함수를 사용하면, HTML 코드를 들여쓰기가 잘된 형태로 출력할 수 있습니다.
    # print(soup.prettify())


# crawling_basic() 함수를 실행하여 웹 크롤링 과정을 확인합니다.
crawling_basic()

# < 출력 > 

'''
첫 번째 a 태그의 텍스트: Quotes to Scrape



전체 a 태그 리스트<a href="/" style="text-decoration: none">Quotes to Scrape</a>
<a href="/login">Login</a>
<a href="/tag/love/page/1/">love</a>
<a href="/author/Andre-Gide">(about)</a>
<a class="tag" href="/tag/life/page/1/">life</a>
<a class="tag" href="/tag/love/page/1/">love</a>
<a href="/author/Marilyn-Monroe">(about)</a>
<a class="tag" href="/tag/friends/page/1/">friends</a>
<a class="tag" href="/tag/heartbreak/page/1/">heartbreak</a>
<a class="tag" href="/tag/inspirational/page/1/">inspirational</a>
<a class="tag" href="/tag/life/page/1/">life</a>
<a class="tag" href="/tag/love/page/1/">love</a>
<a class="tag" href="/tag/sisters/page/1/">sisters</a>
<a href="/author/Bob-Marley">(about)</a>
<a class="tag" href="/tag/love/page/1/">love</a>
<a href="/author/Elie-Wiesel">(about)</a>
<a class="tag" href="/tag/activism/page/1/">activism</a>
<a class="tag" href="/tag/apathy/page/1/">apathy</a>
<a class="tag" href="/tag/hate/page/1/">hate</a>
<a class="tag" href="/tag/indifference/page/1/">indifference</a>
<a class="tag" href="/tag/inspirational/page/1/">inspirational</a>
<a class="tag" href="/tag/love/page/1/">love</a>
<a class="tag" href="/tag/opposite/page/1/">opposite</a>
<a class="tag" href="/tag/philosophy/page/1/">philosophy</a>
<a href="/author/Friedrich-Nietzsche">(about)</a>
<a class="tag" href="/tag/friendship/page/1/">friendship</a>
<a class="tag" href="/tag/lack-of-friendship/page/1/">lack-of-friendship</a>
<a class="tag" href="/tag/lack-of-love/page/1/">lack-of-love</a>
<a class="tag" href="/tag/love/page/1/">love</a>
<a class="tag" href="/tag/marriage/page/1/">marriage</a>
<a class="tag" href="/tag/unhappy-marriage/page/1/">unhappy-marriage</a>
<a href="/author/Pablo-Neruda">(about)</a>
<a class="tag" href="/tag/love/page/1/">love</a>
<a class="tag" href="/tag/poetry/page/1/">poetry</a>
<a href="/author/Marilyn-Monroe">(about)</a>
<a class="tag" href="/tag/girls/page/1/">girls</a>
<a class="tag" href="/tag/love/page/1/">love</a>
<a href="/author/Marilyn-Monroe">(about)</a>
<a class="tag" href="/tag/love/page/1/">love</a>
<a href="/author/James-Baldwin">(about)</a>
<a class="tag" href="/tag/love/page/1/">love</a>
<a href="/author/Jane-Austen">(about)</a>
<a class="tag" href="/tag/friendship/page/1/">friendship</a>
<a class="tag" href="/tag/love/page/1/">love</a>
<a href="/tag/love/page/2/">Next <span aria-hidden="true">→</span></a>
<a class="tag" href="/tag/love/" style="font-size: 28px">love</a>
<a class="tag" href="/tag/inspirational/" style="font-size: 26px">inspirational</a>
<a class="tag" href="/tag/life/" style="font-size: 26px">life</a>
<a class="tag" href="/tag/humor/" style="font-size: 24px">humor</a>
<a class="tag" href="/tag/books/" style="font-size: 22px">books</a>
<a class="tag" href="/tag/reading/" style="font-size: 14px">reading</a>
<a class="tag" href="/tag/friendship/" style="font-size: 10px">friendship</a>
<a class="tag" href="/tag/friends/" style="font-size: 8px">friends</a>
<a class="tag" href="/tag/truth/" style="font-size: 8px">truth</a>
<a class="tag" href="/tag/simile/" style="font-size: 6px">simile</a>
<a href="https://www.goodreads.com/quotes">GoodReads.com</a>
<a class="zyte" href="https://www.zyte.com">Zyte</a>



CSS 선택자(.text)를 사용해 찾은 첫 번째 요소의 텍스트: “It is better to be hated for what you are than to be loved for what you are not.”



요소 텍스트: “It is better to be hated for what you are than to be loved for what you are not.”

요소 텍스트: “This life is what you make it. No matter what, you're going to mess up sometimes, it's a universal truth. But the good part is you get to decide how you're going to mess it up. Girls will be your friends - they'll act like it anyway. But just remember, some come, some go. The ones that stay with you through everything - they're your true best friends. Don't let go of them. Also remember, sisters make the best friends in the world. As for lovers, well, they'll come and go too. And baby, I hate to say it, most of them - actually pretty much all of them are going to break your heart, but you can't give up because if you give up, you'll never find your soulmate. You'll never find that half who makes you whole and that goes for everything. Just because you fail once, doesn't mean you're gonna fail at everything. Keep trying, hold on, and always, always, always believe in yourself, because if you don't, then who will, sweetie? So keep your head high, keep your chin up, and most importantly, keep smiling, because life's a beautiful thing and there's so much to smile about.”

요소 텍스트: “You may not be her first, her last, or her only. She loved before she may love again. But if she loves you now, what else matters? She's not perfect—you aren't either, and the two of you may never be perfect together but if she can make you laugh, cause you to think twice, and admit to being human and making mistakes, hold onto her and give her the most you can. She may not be thinking about you every second of the day, but she will give you a part of her that she knows you can break—her heart. So don't hurt her, don't change her, don't analyze and don't expect more than she can give. Smile when she makes you happy, let her know when she makes you mad, and miss her when she's not there.”

요소 텍스트: “The opposite of love is not hate, it's indifference. The opposite of art is not ugliness, it's indifference. The opposite of faith is not heresy, it's indifference. And the opposite of life is not death, it's indifference.”

요소 텍스트: “It is not a lack of love, but a lack of friendship that makes unhappy marriages.”

요소 텍스트: “I love you without knowing how, or when, or from where. I love you simply, without problems or pride: I love you in this way because I do not know any other way of loving but this, in which there is no I or you, so intimate that your hand upon my chest is my hand, so intimate that when I fall asleep your eyes close.”

요소 텍스트: “If you can make a woman laugh, you can make her do anything.”

요소 텍스트: “The real lover is the man who can thrill you by kissing your forehead or smiling into your eyes or just staring into space.”

요소 텍스트: “Love does not begin and end the way we seem to think it does. Love is a battle, love is a war; love is a growing up.”

요소 텍스트: “There is nothing I would not do for those who are really my friends. I have no notion of loving people by halves, it is not my nature.”
'''