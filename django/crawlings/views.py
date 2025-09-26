'''# crawlings/views.py

from django.shortcuts import render, redirect, get_object_or_404
from .models import Comment
from django.contrib import messages
# 크롤러 함수 import
from toss_crawling import fetch_visible_comments  



def index(request):
    # F01: 단순 폼 페이지
    return render(request, 'crawlings/index.html')

# 1번 2번을 하거나
# 삭제한다면, 1 2 3 2 하게 됨.


def comments_crawling(request):
    """
    GET /crawlings/comments/?name=삼성전자
    - 회사명 입력을 받으면: 크롤링 → DB 저장까지만 하고 끝낸다.
    """
    name = request.GET.get('name', '').strip()
    
    
    if name:
        try:
            # F02: 크롤링 호출 (제공된 함수는 댓글 텍스트 리스트만 반환)
            texts = fetch_visible_comments(company_name=name, limit=30)
            # 저장 (현재 stock_code는 없음 → 공란)
            new_objs = [
                Comment(company_name=name, stock_code="", text=t)
                for t in texts
            ]
            if new_objs:
                Comment.objects.bulk_create(new_objs, ignore_conflicts=True)
                messages.success(request, f"'{name}' 댓글 {len(new_objs)}건 저장 완료")
            else:
                messages.warning(request, f"'{name}'에 대한 신규 댓글을 찾지 못했습니다.")
        except Exception as e:
            messages.error(request, f"크롤링 중 오류: {e}")

        qs = Comment.objects.filter(company_name=name)
    else:
        qs = Comment.objects.all()

    context = {
        "name": name,
        "comments": qs,
    }
    return render(request, 'crawlings/comments.html', context)



def comments_printing(request):
    """
    GET /crawlings/comments/?name=삼성전자
    - DB에서 회사명을 찾아서, 해당 회사 댓글만 목록 출력한다.
    """
    name = request.GET.get('name', '').strip()

    context = {
        "name": name,
        "comments": qs,
    }
    return render(request, 'crawlings/comments.html', context)



def delete(request, pk):
    """
    F04: 단일 댓글 삭제
    """
    obj = get_object_or_404(Comment, pk=pk)
    obj.delete()
    messages.info(request, "댓글을 삭제했습니다.")
    # 삭제 후: 같은 회사 목록으로 돌아가면 UX 좋음
    return redirect(f"/crawlings/comments/?name={obj.company_name}")'''

import io, re, base64, os
import numpy as np
from PIL import Image
from wordcloud import WordCloud

from django.conf import settings
from django.templatetags.static import static  # static 파일 경로 얻기용

# (선택) 프로젝트 내 한글 폰트 경로 지정
KOREAN_FONT_PATH = os.path.join(settings.BASE_DIR, "crawlings", "static", "crawlings", "fonts", "Paperlogy-8ExtraBold.ttf")



def _build_wordcloud_base64(texts, mask_image_path, font_path=None, width=1200, height=1200):
    """
    - texts: 댓글 문자열 리스트
    - mask_image_path: 정적 경로(또는 절대 경로) - 토스 로고 PNG
    - font_path: 한글 폰트 파일 경로
    - return: base64 인코딩된 PNG 문자열 (data URI 없이 본문만)
    """
    if not texts:
        return None

    # 1) 텍스트 전처리: 한글/영문/숫자만 남기고 1글자 제거, 불용어 제거
    raw = " ".join(texts)
    # 특수문자 제거 & 공백 정규화
    raw = re.sub(r"[^0-9A-Za-z가-힣\s]", " ", raw)
    raw = re.sub(r"\s+", " ", raw)

    tokens = raw.split()
    # 아주 기초 불용어(필요시 추가)
    stopwords = set(["그리고", "하지만", "그러나", "에서", "하다", "합니다", "있는", "것", "좀", "너무", "진짜", "그냥"])
    tokens = [t for t in tokens if len(t) >= 2 and t not in stopwords]
    joined = " ".join(tokens).strip()
    if not joined:
        return None

    # 2) 마스크 생성 (흰색=비움, 검정=채움). 컬러 PNG여도 그레이로 변환해서 사용
    # static()은 URL을 반환하므로 파일 시스템 경로로 바꿔줘야 함.
    # 배포 환경에선 collectstatic 경로 대신 앱 내 상대경로를 안전하게 계산해야 하므로 아래처럼 처리
    if mask_image_path.startswith("/"):
        mask_fs_path = mask_image_path
    else:
        # 프로젝트 루트 기준 상대경로일 경우
        mask_fs_path = os.path.join(settings.BASE_DIR, mask_image_path)

    mask_img = Image.open(mask_fs_path).convert("L")   # 그레이스케일
    mask = np.array(mask_img)

    # 3) 워드클라우드 생성
    wc = WordCloud(
        font_path=font_path,
        width=width,
        height=height,
        background_color="white",
        mask=mask,                # 로고 모양 마스크 적용
        colormap="Blues",         # 토스 계열 톤(취향에 따라 변경)
        prefer_horizontal=0.9,
    ).generate(joined)

    # 4) PNG로 메모리에 저장 후 base64 인코딩
    buf = io.BytesIO()
    wc.to_image().save(buf, format="PNG")
    buf.seek(0)
    return base64.b64encode(buf.read()).decode("utf-8")

















from urllib.parse import quote
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse

from .models import Comment
from toss_crawling import fetch_visible_comments  # 너의 크롤러

def index(request):
    return render(request, 'crawlings/index.html')


def comments_crawling(request):
    """
    GET /crawlings/comments/crawl/?name=삼성전자
    - 회사명 입력을 받으면: 크롤링 → DB 저장까지만 하고,
      항상 comments_printing 으로 redirect.
    """
    name = (request.GET.get('name') or request.GET.get('company') or '').strip()

    if not name:
        messages.warning(request, "회사명을 입력해주세요.")
        return redirect(reverse('crawlings:comments_printing'))

    try:
        texts = fetch_visible_comments(company_name=name, limit=30)
        if texts:
            objs = [Comment(company_name=name, stock_code="", text=t) for t in texts]
            Comment.objects.bulk_create(objs)
            messages.success(request, f"'{name}' 댓글 {len(objs)}건 저장 완료")
        else:
            messages.info(request, f"'{name}' 신규 댓글이 없습니다.")
    except Exception as e:
        # 저장이 실패해도, 기존 DB 목록은 출력에서 확인 가능
        messages.error(request, f"크롤링 중 오류: {e}")

    # 출력 전용 뷰로 이동
    url = f"{reverse('crawlings:comments_printing')}?name={quote(name)}"
    return redirect(url)


def comments_printing(request):
    """
    GET /crawlings/comments/?name=삼성전자
    - DB에서 회사명으로 필터링(없으면 전체)하여 목록만 출력
    - 추가: 같은 텍스트로 토스 로고 모양 워드클라우드 생성하여 함께 표시
    """
    name = (request.GET.get('name') or request.GET.get('company') or '').strip()
    qs = Comment.objects.all()
    if name:
        qs = qs.filter(company_name=name)

    # 워드클라우드 생성용 텍스트 추출 (최근 N개 등 제한을 두고 싶다면 .order_by('-id')[:300] 등 적용)
    texts = list(qs.values_list("text", flat=True))

    # 정적 파일 경로(앱 내에 저장한 로고 png). 예: crawlings/static/crawlings/toss_logo.png
    # 파일 시스템 절대경로를 만들어 넘긴다.
    logo_rel_path = os.path.join("crawlings", "static", "crawlings", "toss_logo.png")

    wc_data = _build_wordcloud_base64(
        texts=texts,
        mask_image_path=logo_rel_path,
        font_path=KOREAN_FONT_PATH,   # 없으면 None
        width=1000,
        height=1000
    )

    context = {
        "name": name,
        "comments": qs,
        "wc_data": wc_data,  # 템플릿에서 <img src="data:image/png;base64, ..."> 로 출력
    }
    return render(request, 'crawlings/comments.html', context)


def delete(request, pk):
    """
    F04: 단일 댓글 삭제 → 같은 회사 목록으로 출력 뷰 재진입
    """
    obj = get_object_or_404(Comment, pk=pk)
    name = obj.company_name  # 삭제 전에 회사명 보존
    obj.delete()
    messages.info(request, "댓글을 삭제했습니다.")
    url = f"{reverse('crawlings:comments_printing')}?name={quote(name)}"
    return redirect(url)
