'''# SA.py
import os, json
from typing import List, Dict
from openai import OpenAI

# .env에서 키 읽기 (Django settings에서 load_dotenv 해두면 더 깔끔)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

from openai import OpenAI
client = OpenAI(api_key=OPENAI_API_KEY)


# 시스템 프롬프트 커스터마이징
SYSTEM_PROMPT = """
너는 소셜 코멘트 감성 분류기야.
각 문장을 긍정/중립/부정 중 하나로 분류하고 -1.0~1.0의 점수(부정:-1, 중립:0, 긍정:1 근처)를 부여해.
JSON 배열로만 응답해.
스키마: [{"text": "...", "label": "positive|neutral|negative", "score": float}]
"""

def _chunk(text: str, max_len: int = 300) -> str:
    # 워드클라우드용 전체텍스트는 별도로 쓰고,
    # 감성분석은 과금 고려해서 코멘트별 길이를 자른다.
    return text if len(text) <= max_len else text[:max_len]

def analyze_sentiments(texts: List[str], max_items: int = 300) -> List[Dict]:
    """
    texts: 댓글 문자열 리스트
    return: [{"text": str, "label": "positive|neutral|negative", "score": float}, ...]
    """
    if not texts:
        return []

    # 과금/속도 고려해 상한선
    texts = texts[:max_items]
    packed = json.dumps([_chunk(t) for t in texts], ensure_ascii=False)

    resp = client.responses.create(
        model="gpt-5-nano",
        input=[
            {"role": "system", "content":[{"type":"input_text","text": SYSTEM_PROMPT}]},
            {"role": "user", "content":[{"type":"input_text","text": packed}]},
        ],
    )

    raw = resp.output_text  # 모델이 말한 텍스트
    try:
        data = json.loads(raw)
        # 방어코드: 스키마 보정
        out = []
        for i, t in enumerate(texts):
            item = data[i] if i < len(data) else {}
            label = (item.get("label") or "neutral").lower()
            if label not in ("positive","neutral","negative"):
                label = "neutral"
            score = float(item.get("score", 0))
            out.append({"text": t, "label": label, "score": score})
        return out
    except Exception:
        # JSON 실패 시 전부 중립 처리 (서비스 죽지 않게)
        return [{"text": t, "label": "neutral", "score": 0.0} for t in texts]'''
        
# SA.py
import os, json, random
from typing import List, Dict
from openai import OpenAI

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

SYSTEM_PROMPT = """
너는 소셜 코멘트 감성 분류기야.
각 문장을 긍정/중립/부정 중 하나로 분류하고 -1.0~1.0의 점수(부정:-1, 중립:0, 긍정:1 근처)를 부여해.
JSON 배열로만 응답해.
스키마: [{"text": "...", "label": "positive|neutral|negative", "score": float}]
"""

def _clip(t: str, max_len: int = 300) -> str:
    return t if len(t) <= max_len else t[:max_len]

def analyze_sentiments(
    texts: List[str],
    max_items: int = 60,         # 💡 비용 절감: 기본 60개만 분석
    strategy: str = "head",      # "head"=상단 N개, "random"=무작위 N개
    seed: int | None = 42,
) -> List[Dict]:
    """
    texts: 원본 댓글 리스트
    max_items: API로 넘길 최대 건수 (비용/속도 한도)
    strategy: 'head'면 앞에서 N개, 'random'이면 전체에서 N개 샘플
    """
    if not texts:
        return []

    n = min(max_items, len(texts))
    if n <= 0:
        return []

    if strategy == "random":
        rnd = random.Random(seed)
        sampled = rnd.sample(texts, n)
    else:
        sampled = texts[:n]  # 상단 N개

    payload = json.dumps([_clip(t) for t in sampled], ensure_ascii=False)

    resp = client.responses.create(
        model="gpt-5-nano",
        input=[
            {"role": "system", "content":[{"type":"input_text","text": SYSTEM_PROMPT}]},
            {"role": "user", "content":[{"type":"input_text","text": payload}]},
        ],
    )

    raw = resp.output_text
    try:
        data = json.loads(raw)
        out = []
        for i, t in enumerate(sampled):
            item = data[i] if i < len(data) else {}
            label = (item.get("label") or "neutral").lower()
            if label not in ("positive","neutral","negative"):
                label = "neutral"
            score = float(item.get("score", 0))
            out.append({"text": t, "label": label, "score": score})
        return out
    except Exception:
        return [{"text": t, "label": "neutral", "score": 0.0} for t in sampled]
