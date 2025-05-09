from flask import Flask, request, jsonify
from flask_cors import CORS 
import requests
import os
from dotenv import load_dotenv
import easyocr
import json
from datetime import datetime
import ast

app = Flask(__name__)
CORS(app)
load_dotenv()

API_KEY = os.getenv("API_KEY")
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

# OCR + 상품명 분류
@app.route('/api/v1/parse-ingredients', methods=['POST'])
def parse_ingredients():
    # form-data에서 이미지 받기
    if 'image' not in request.files:
        return jsonify({'error': 'No image file provided'}), 400

    image_file = request.files['image']
    image_path = 'temp_image.png'
    image_file.save(image_path)

    try:
        # OCR
        reader = easyocr.Reader(['ko'])
        result = reader.readtext(image_path)
        text = " ".join([d[1] for d in result])

        # 현재 날짜와 시간 생성
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # 프롬프트 생성
        content = f"""
        아래는 OCR로 인식된 텍스트입니다. 상품명이 정확하지 않을 수 있으므로, 유사 발음과 일반적인 쇼핑 품목명을 기준으로 보정한 후, 상품명과 수량을 추출하고 각 상품을 아래의 음식 카테고리 중 하나로 분류해 주세요.

        ✅ 출력 형식은 다음과 같아야 합니다:
        [["상품명", 수량, "카테고리", "{current_time}"], ...]

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

        # Groq API 호출
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {API_KEY}"
        }
        payload = {
            "model": "llama-3.3-70b-versatile",
            "messages": [{"role": "user", "content": content.strip()}]
        }
        response = requests.post(GROQ_API_URL, headers=headers, json=payload)

        if response.status_code == 200:
            raw_data = response.json()['choices'][0]['message']['content']
            parsed_list = ast.literal_eval(raw_data)  

            return jsonify({
                                "status": 200,
                                "data": parsed_list
                            })
        else:
            return jsonify({
                                "status": response.status_code,
                                "data": {
                                    "error": response.text
                                }
                            })
    finally:
        # 이미지 삭제
        if os.path.exists(image_path):
            os.remove(image_path)


# 레시피 추천
@app.route('/api/v1/recommend-recipe', methods=['POST'])
def recommend_recipe():
    data = request.get_json()
    ingredients = data.get("ingredients", [])

    if not ingredients:
        return jsonify({
                            "status": 400,
                            "data": {
                                "error": "No ingredients provided"
                            }
                        })

    ingredient_str = ", ".join([f"{name} {qty}" for name, qty in ingredients])

    prompt = f"""
    다음은 사용자가 현재 가지고 있는 재료 목록입니다: {ingredient_str}

    이 재료 중 일부 또는 전부를 활용하여 만들 수 있는 요리법을 10개 추천해 주세요. 각 레시피는 다음 조건을 따라 주세요:

    - 레시피 이름
    - 필요한 재료 목록
    - 명확하고 구체적인 조리 방법
    - 사용자 보유 재료를 최대한 활용한 요리

    ✅ 출력 형식은 반드시 아래의 JSON 배열 구조를 따르세요 (설명 없이 JSON만 반환):

    [
    {{
        "name": "요리 이름",
        "ingredients": ["재료1", "재료2", ...],
        "instructions": "조리 방법은 명확하고 구체적으로 작성"
    }},
    ...
    ]

    답변은 반드시 한국어로 작성해 주세요.
    """

    response = requests.post(GROQ_API_URL, headers={
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }, json={
        "model": "llama-3.3-70b-versatile",
        "messages": [{"role": "user", "content": prompt.strip()}]
    })

    if response.status_code == 200:
        # 응답에서 코드 블록 제거하기
        response_content = response.json()['choices'][0]['message']['content']
        response_content = response_content.strip('```json\n').strip('```')

        try:
            # 응답 내용을 JSON으로 파싱
            recipe_data = json.loads(response_content)
            return jsonify({
                "status": 200,
                "data": recipe_data
            })
        except json.JSONDecodeError:
            return jsonify({
                "status": 500,
                "data": {
                    "error": "Response format error"
                }
            })

    else:
        return jsonify({
            "status": response.status_code,
            "data": {
                "error": response.text
            }
        })


if __name__ == '__main__':
    app.run(debug=True)
