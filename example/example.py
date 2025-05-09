import requests
import easyocr
from dotenv import load_dotenv
import os

# .env 파일에서 환경 변수 로드
load_dotenv()

# .env 파일에서 API_KEY 값 가져오기
API_KEY = os.getenv('API_KEY')

# OCR 처리
reader = easyocr.Reader(['ko']) 
result = reader.readtext('image.png')

# 텍스트 추출
text = " ".join([detection[1] for detection in result])

# LLM 프롬프트 작성
content = f"""
아래는 OCR로 인식된 텍스트입니다. 상품명이 정확하지 않을 수 있으므로, 유사 발음과 일반적인 쇼핑 품목명을 기준으로 보정한 후, 상품명과 수량을 추출하고 각 상품을 아래의 음식 카테고리 중 하나로 분류해 주세요.

✅ 출력 형식은 다음과 같아야 합니다:
[[상품명, 수량, 카테고리], [상품명, 수량, 카테고리], ...]

예: [["블랙커피", "2", "음료"], ["우유", "1", "유제품"]]

❗ 반드시 지켜야 할 조건:
- 수량이 명시되지 않으면 1로 간주하세요.
- 단위(개, 팩 등)는 생략하고 숫자만 포함하세요.
- 상품명이 너무 불분명하거나 카테고리 분류가 어렵다면 제외하세요.
- 설명 등 다른 텍스트는 절대 포함하지 마세요.

📦 카테고리 목록:
- 육류 (소고기, 돼지고기, 닭고기, 햄, 베이컨 등)
- 해산물 (생선, 오징어, 새우, 미역 등)
- 음료 (물, 주스, 커피, 차, 맥주 등)
- 과일 (바나나, 사과, 포도, 수박 등)
- 채소 (양파, 감자, 토마토, 브로콜리 등)
- 유제품 (우유, 치즈, 요거트 등)
- 곡류/가공식품 (쌀, 라면, 과자, 통조림 등)
- 조미료/소스 (소금, 간장, 케첩, 마요네즈 등)
- 냉동식품 (냉동만두, 냉동피자 등)
- 간식 (초콜릿, 젤리, 아이스크림 등)
- 베이커리 (식빵, 케이크 등)
- 유아식품 (분유, 이유식 등)

텍스트:
{text}
"""


# API 요청
url = "https://api.groq.com/openai/v1/chat/completions"
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {API_KEY}"  # .env에서 가져온 API 키 사용
}
data = {
    "model": "llama-3.3-70b-versatile",
    "messages": [{"role": "user", "content": content.strip()}]
}

# 결과 출력
response = requests.post(url, headers=headers, json=data)

if response.status_code == 200:
    result = response.json()
    print("Response:", result['choices'][0]['message']['content'])
else:
    print(f"Error {response.status_code}: {response.text}")
