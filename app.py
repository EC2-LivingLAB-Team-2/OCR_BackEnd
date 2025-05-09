from flask import Flask, request, jsonify
import requests
import os
from dotenv import load_dotenv
import easyocr

app = Flask(__name__)
load_dotenv()

API_KEY = os.getenv("API_KEY")
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

# OCR + 상품명 분류
@app.route('/parse-ingredients', methods=['POST'])
def parse_ingredients():
    reader = easyocr.Reader(['ko'])
    result = reader.readtext('image.png')  # 실제 사용할 이미지 파일 경로
    text = " ".join([d[1] for d in result])

    content = f"""
    아래는 OCR로 인식된 텍스트입니다. 상품명이 정확하지 않을 수 있으므로, 유사 발음과 일반적인 쇼핑 품목명을 기준으로 보정한 후, 상품명과 수량을 추출하고 각 상품을 아래의 음식 카테고리 중 하나로 분류해 주세요.

    ✅ 출력 형식은 다음과 같아야 합니다:
    [[상품명, 수량, 카테고리], [상품명, 수량, 카테고리], ...]

    ❗ 반드시 지켜야 할 조건:
    - 수량이 명시되지 않으면 1로 간주하세요.
    - 단위(개, 팩 등)는 생략하고 숫자만 포함하세요.
    - 상품명이 너무 불분명하거나 카테고리 분류가 어렵다면 제외하세요.
    - 설명 등 다른 텍스트는 절대 포함하지 마세요.

    📦 카테고리 목록:
    - 육류, 해산물, 음료, 과일, 채소, 유제품, 곡류/가공식품, 조미료/소스, 냉동식품, 간식, 베이커리, 유아식품

    텍스트:
    {text}
    """

    response = requests.post(GROQ_API_URL, headers={
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }, json={
        "model": "llama-3.3-70b-versatile",
        "messages": [{"role": "user", "content": content}]
    })

    if response.status_code == 200:
        return jsonify(response.json()['choices'][0]['message']['content'])
    else:
        return jsonify({"error": response.text}), response.status_code


# 레시피 추천
@app.route('/recommend-recipe', methods=['POST'])
def recommend_recipe():
    data = request.get_json()
    ingredients = data.get("ingredients", [])

    if not ingredients:
        return jsonify({"error": "No ingredients provided"}), 400

    ingredient_str = ", ".join([f"{name} {qty}" for name, qty in ingredients])

    prompt = f"""
    다음은 사용자가 현재 가지고 있는 재료 목록입니다: {ingredient_str}

    이 재료 중 일부 또는 전부를 활용하여 만들 수 있는 요리법을 1개 추천해 주세요. 각 레시피는 다음 조건을 따라 주세요:

    - 레시피 이름
    - 필요한 재료 목록
    - 간단한 조리 방법 설명 (3줄 이하)
    - 사용자 보유 재료에 기반하여 최대한 충족되는 요리
    - 조리 방법을 자세히 작성

    출력 형식:
    음식명: ...
    필요한 재료: ...
    조리 방법: ...
    (한국어로 작성)
    """

    response = requests.post(GROQ_API_URL, headers={
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }, json={
        "model": "llama-3.3-70b-versatile",
        "messages": [{"role": "user", "content": prompt.strip()}]
    })

    if response.status_code == 200:
        return jsonify(response.json()['choices'][0]['message']['content'])
    else:
        return jsonify({"error": response.text}), response.status_code


if __name__ == '__main__':
    app.run(debug=True)
