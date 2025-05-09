import os
import requests
from dotenv import load_dotenv

# .env 파일에서 API 키 로드
load_dotenv()
API_KEY = os.getenv("API_KEY")

# 사용자가 보유한 재료
ingredients = [
    ["소고기", "1"], ["닭가슴살", "2"], ["계란", "3"], ["우유", "1"], ["치즈", "1"],
    ["양파", "2"], ["당근", "1"], ["감자", "2"], ["시금치", "1"], ["토마토", "2"],
    ["사과", "1"], ["바나나", "2"], ["오징어", "1"], ["새우", "1"], ["두부", "1"],
    ["밥", "2"], ["빵", "1"], ["간장", "1"], ["고추장", "1"], ["케첩", "1"],
    ["버터", "1"], ["식용유", "1"], ["물", "무제한"], ["소금", "1"], ["후추", "1"],
]

# 문자열로 포맷
ingredient_str = ", ".join([f"{name} {qty}" for name, qty in ingredients])

# 프롬프트 생성
prompt = f"""
다음은 사용자가 현재 가지고 있는 재료 목록입니다: {ingredient_str}

이 재료 중 일부 또는 전부를 활용하여 만들 수 있는 요리법을 1개 추천해 주세요. 각 레시피는 다음 조건을 따라 주세요:

- 레시피 이름
- 필요한 재료 목록
- 간단한 조리 방법 설명 (3줄 이하)
- 사용자 보유 재료에 기반하여 최대한 충족되는 요리
- 조리 방법을 자세히 작성

답변은 꼭 한국어로 해 주세요.

출력 형식:
음식명: ...
필요한 재료: ...
조리 방법: ...
"""

# Groq API 요청
url = "https://api.groq.com/openai/v1/chat/completions"
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {API_KEY}"
}
data = {
    "model": "llama-3.3-70b-versatile",
    "messages": [{"role": "user", "content": prompt.strip()}]
}

response = requests.post(url, headers=headers, json=data)

# 결과 출력
if response.status_code == 200:
    result = response.json()
    print("Response:\n")
    print(result['choices'][0]['message']['content'])
else:
    print(f"Error {response.status_code}: {response.text}")
