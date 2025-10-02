from django.shortcuts import render, redirect
from django.conf import settings
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from openai import OpenAI
from .models import StockData
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import StaleElementReferenceException

# ---- Selenium Chrome 설정 ----
chrome_options = Options()
# chrome_options.add_argument("--headless")  # 필요시 활성화 가능
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--disable-extensions")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--blink-settings=imagesEnabled=false")

chrome_driver_path = settings.BASE_DIR / "chromedriver-win64" / "chromedriver.exe"
service = Service(executable_path=str(chrome_driver_path))

# ---- OpenAI Client ----
client = OpenAI(api_key=settings.OPENAI_API_KEY)

def ask_comment(prompt, model="gpt-5-nano"):
    """OpenAI 모델을 사용해 댓글 분석"""
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"오류 발생: {e}"
    
def fetch_stock_and_comments(driver, company_name, limit=20, max_scroll=10):
    """
    Toss Invest:
    1) 사이트 접속
    2) 검색창 활성화 → 회사 검색 (ENTER로 바로 첫 번째 결과 진입)
    3) /order URL에서 종목 코드 추출
    4) /community 이동 → 댓글 최대 20개 수집
    """
    try:
        # 1) 사이트 접속
        print("[DEBUG] 메인 페이지 이동")
        driver.get("https://www.tossinvest.com/")
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )

        # 2) 검색창 활성화
        body = driver.find_element(By.TAG_NAME, "body")
        body.send_keys("/")
        search_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, "//input[@placeholder='검색어를 입력해주세요']")
            )
        )
        search_input.click()
        search_input.clear()
        search_input.send_keys(company_name)
        search_input.send_keys(Keys.ENTER)
        print(f"[DEBUG] 검색어 입력 및 첫 결과 선택 완료: {company_name}")

        # 3) /order 페이지 로딩 대기
        WebDriverWait(driver, 15).until(EC.url_contains("/order"))
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.TAG_NAME, "main"))
        )
        current_url = driver.current_url
        print(f"[DEBUG] /order 페이지 진입: {current_url}")

        # 종목 코드 추출
        parts = current_url.split("/")
        stock_code = None
        if "stocks" in parts:
            idx = parts.index("stocks")
            if idx + 1 < len(parts):
                stock_code = parts[idx + 1]

        # 4) 커뮤니티 페이지로 이동
        community_url = f"https://www.tossinvest.com/stocks/{stock_code}/community"
        driver.get(community_url)
        print(f"[DEBUG] 커뮤니티 페이지 이동: {community_url}")

        # 댓글 영역 로딩 대기
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "main article"))
        )

        # 5) 댓글 수집 (스크롤 반복 + 누적)
        comments = []
        last_height = driver.execute_script("return document.body.scrollHeight")

        for _ in range(max_scroll):
            # 현재 화면의 댓글 추출
            spans = driver.find_elements(By.CSS_SELECTOR, "article.comment span.tw-1r5dc8g0._60z0ev1")
            for span in spans:
                text = span.text.strip()
                if text and text not in comments:
                    comments.append(text)

            if len(comments) >= limit:
                break

            # 스크롤 다운
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1)

            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

        print(f"[DEBUG] 댓글 {len(comments)}개 수집 완료")
        return stock_code, company_name, comments[:limit]

    except Exception as e:
        import traceback
        print("fetch_stock_and_comments 에러:", traceback.format_exc())
        raise


def analyze_comments(comments, company_name):
    """댓글을 GPT 모델로 분석"""
    if comments:
        combined_comments = "\n".join(comments)
        prompt = f"다음은 {company_name}에 대한 댓글들입니다. 종합적인 분석을 한글로 작성하고, 마지막 줄에는 여론을 긍정적, 부정적, 중립으로 판단해 주세요:\n{combined_comments}"
        return ask_comment(prompt)
    return "댓글을 찾을 수 없습니다."


def stock_finder(request):
    driver = None
    if request.method == "POST":
        company_name = request.POST.get('company_name', '').strip().lower()
        loading_step = request.POST.get('loading_step', '')

        if not company_name:
            return render(request, 'contentfetch/stock_finder.html', {'error_message': "회사 이름을 입력하세요."})

        try:
            # DB 캐시 확인
            existing_data = StockData.objects.filter(company_name__icontains=company_name).first()
            if existing_data:
                return render(request, 'contentfetch/stock_finder.html', {
                    'company_name': existing_data.company_name,
                    'stock_code': existing_data.stock_code,
                    'comments': existing_data.comments.split("\n"),
                    'chatgpt_response': existing_data.analysis,
                    'is_existing_data': True,
                    'is_loading': False
                })

            if not loading_step:
                return render(request, 'contentfetch/stock_finder.html', {
                    'is_loading': True,
                    'loading_step': 'selenium',
                    'company_name': company_name,
                    'form_data': {'company_name': company_name, 'loading_step': 'selenium'}
                })

            # Selenium 실행
            driver = webdriver.Chrome(service=service, options=chrome_options)
            stock_code, company_name, comments = fetch_stock_and_comments(driver, company_name)

            # 댓글 분석
            chatgpt_response = analyze_comments(comments, company_name)

            # DB 저장
            stock_data = StockData(
                company_name=company_name,
                stock_code=stock_code,
                comments="\n".join(comments),
                analysis=chatgpt_response
            )
            stock_data.save()

            return render(request, 'contentfetch/stock_finder.html', {
                'company_name': company_name,
                'stock_code': stock_code,
                'comments': comments,
                'chatgpt_response': chatgpt_response,
                'is_existing_data': False,
                'is_loading': False
            })

        except Exception as e:
            return render(request, 'contentfetch/stock_finder.html', {
                'error_message': f"스크래핑 중 오류 발생: {e}",
                'is_loading': False
            })
        finally:
            if driver:
                driver.quit()

    return render(request, 'contentfetch/stock_finder.html', {'is_loading': False})


def delete_comment(request):
    """DB에서 댓글 삭제 후 ChatGPT 재분석"""
    if request.method == "POST":
        stock_code = request.POST.get('stock_code')
        comment_index = request.POST.get('comment_index')

        if stock_code and comment_index is not None:
            try:
                comment_index = int(comment_index)
                stock_data = StockData.objects.get(stock_code=stock_code)

                if stock_data:
                    comments = stock_data.comments.split("\n")
                    if 0 <= comment_index < len(comments):
                        # 댓글 삭제
                        del comments[comment_index]
                        stock_data.comments = "\n".join(comments)

                        # ChatGPT 응답 재분석
                        chatgpt_response = analyze_comments(comments, stock_data.company_name)
                        stock_data.analysis = chatgpt_response
                        stock_data.save()

                        return render(request, 'contentfetch/stock_finder.html', {
                            'company_name': stock_data.company_name,
                            'stock_code': stock_data.stock_code,
                            'comments': comments,
                            'chatgpt_response': chatgpt_response,
                        })
            except ValueError:
                pass

                # 에러 시에도 redirect (에러 메시지 대신 기본 화면)
        return redirect("/stock_finder/")

    # GET 요청이면 그냥 stock_finder 페이지로 이동
    return redirect("/stock_finder/")
