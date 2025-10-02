# 아주 단순한 룰 기반 감성 분류 (한국어 키워드 포함)
POS_WORDS = {"호재", "상승", "좋", "최고", "흑자", "매수", "강세", "훌륭", "개선", "성장"}
NEG_WORDS = {"악재", "하락", "나쁨", "최악", "적자", "매도", "약세", "부정", "위험", "문제"}

def simple_ko_sentiment(text: str) -> str:
    """
    text 안에 긍/부 키워드 개수로 pos/neg/neu 리턴
    """
    if not text:
        return "neu"
    s = 0
    for w in POS_WORDS:
        if w in text:
            s += 1
    for w in NEG_WORDS:
        if w in text:
            s -= 1
    if s > 0:
        return "pos"
    elif s < 0:
        return "neg"
    return "neu"

def palette(kind: str):
    """
    배지 표시용 (라벨, Bootstrap 색상 클래스)
    """
    mapping = {
        "pos": ("긍정", "success"),
        "neg": ("부정", "danger"),
        "neu": ("중립", "secondary"),
    }
    return mapping.get(kind, ("중립", "secondary"))
