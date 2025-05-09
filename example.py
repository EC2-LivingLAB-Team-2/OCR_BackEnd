import requests
import easyocr

reader = easyocr.Reader(['ko']) 
result = reader.readtext('image.png')

text = ""
for detection in result:
    text += detection[1] + " " 


content = f"""
아래는 OCR로 인식된 텍스트입니다. 상품 이름이 정확하지 않을 수 있으니, 일반적인 쇼핑 품목을 기준으로 자연어 처리를 통해 보정한 뒤, 상품명과 수량만 추출해 주세요.

결과는 다음 형식의 Python 리스트로 출력해 주세요:
[[상품명, 수량], [상품명, 수량], ...]

예: [["바나나", "2"], ["우유", "1"]]

※ 설명이나 다른 텍스트는 출력하지 마세요.
※ 명확하지 않거나 상품으로 보기 어려운 항목은 제외하세요.

텍스트:
{text}
"""

url = "https://api.groq.com/openai/v1/chat/completions"
headers = {
    "Content-Type": "application/json",
    "Authorization": "Bearer "
}
data = {
    "model": "llama-3.3-70b-versatile",
    "messages": [
        {"role": "user", "content": content.strip()}
    ]
}

response = requests.post(url, headers=headers, json=data)

if response.status_code == 200:
    result = response.json()
    print("Response:", result['choices'][0]['message']['content'])
else:
    print(f"Error {response.status_code}: {response.text}")
