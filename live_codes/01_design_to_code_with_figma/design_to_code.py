import os
import base64  # 이미지를 텍스트로 변환(인코딩)하기 위한 라이브러리
from openai import OpenAI
from pathlib import Path
from dotenv import load_dotenv

# .env 파일에서 API 키를 안전하게 로드합니다.
load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# OpenAI 클라이언트 객체를 API 키와 함께 초기화합니다.
client = OpenAI(api_key=OPENAI_API_KEY)


def encode_image(image_path):
    """이미지 파일을 Base64 문자열로 인코딩하는 함수"""
    # 이미지 파일을 바이너리 읽기 모드('rb')로 엽니다.
    with Path(image_path).open('rb') as image_file:
        # 파일을 읽고 Base64로 인코딩한 뒤, utf-8 문자열로 변환하여 반환합니다.
        return base64.b64encode(image_file.read()).decode('utf-8')


def analyze_image(image_path, system_prompt, user_prompt):
    """OpenAI API에 이미지와 프롬프트를 보내 분석을 요청하는 함수"""
    # 1. 이미지 준비: 함수를 호출하여 이미지를 Base64 문자열로 변환합니다.
    base64_image = encode_image(image_path)

    # 2. API 호출: client.responses.create를 사용하여 요청을 보냅니다.
    response = client.responses.create(
        model='gpt-5-nano',  # 사용할 AI 모델을 지정합니다.
        input=[
            # system 역할: AI에게 기본적인 역할과 지켜야 할 규칙을 부여합니다.
            {
                'role': 'system',
                'content': [
                    {
                        'type': 'input_text',
                        'text': system_prompt,
                    }
                ],
            },
            # user 역할: AI에게 실제 처리할 데이터와 구체적인 질문을 전달합니다.
            {
                'role': 'user',
                # content를 리스트로 만들어, 텍스트와 이미지를 함께 전달합니다 (멀티모달 입력).
                'content': [
                    {
                        'type': 'input_text',
                        'text': user_prompt,  # 사용자의 텍스트 요구사항
                    },
                    {
                        'type': 'input_image',  # 이 content가 이미지임을 명시
                        'image_url': f'data:image/jpeg;base64,{base64_image}',  # Base64로 인코딩된 이미지 데이터
                    },
                ],
            },
        ],
    )
    # 최종적으로 AI가 생성한 텍스트(HTML/CSS 코드)를 반환합니다.
    return response.output_text


# --- 이 스크립트가 직접 실행될 때만 아래 코드가 동작합니다 ---
if __name__ == '__main__':
    # 변환할 디자인 시안 이미지의 경로를 지정합니다.
    target_image_path = 'image/my_img.png'

    # AI에게 전달할 시스템 프롬프트(역할, 규칙)를 정의합니다.
    system_prompt = """
    당신은 웹 개발 전문가입니다.
    Bootstrap5 프레임워크를 사용해야 합니다.
    HTML5, CSS3 표준을 준수하여 작성합니다.
    CSS는 OOCSS 방법론에 기반하여 유지보수가 쉽도록 구성합니다.
    다른 코멘트는 답변하지 말고 최종 결과 파일만 응답해주세요.
    """

    # AI에게 전달할 사용자 프롬프트(구체적인 요구사항)를 정의합니다.
    user_prompt = """
    다음 이미지를 분석해 HTML/CSS 코드로 변환해 주세요.
    만약 사용할 이미지가 없으면 Text로 대체해주세요. 
    """

    print(f'이미지 : {target_image_path}를 HTML/CSS 변환 요청')
    # 3. API 호출 실행
    result = analyze_image(target_image_path, system_prompt, user_prompt)

    # 응답으로 받은 코드를 'index.html' 파일로 저장합니다.
    html = Path('index.html')
    with html.open('w', encoding='utf-8') as f:
        f.write(result)

    print('코드 변환 완료! index.html 파일 생성')
