from openai import OpenAI
import datetime
import base64
import os

# OpenAI API 키 불러오기
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# 오늘 날짜
today = datetime.date.today().isoformat()
filename = f"{today}.jpg"

# 메뉴 설명
menu_text = """
1. 돈육모듬장조림
2. 흑미밥
3. 얼큰김치찌개
4. 새싹도토리묵*양념장
5. 치커리무침
6. 배추김치
"""

# 프롬프트 생성
prompt = f"A well-composed Korean meal showing: {menu_text}"

# 이미지 생성
response = client.images.generate(
    model="dall-e-3",
    prompt=prompt,
    size="256x256",
    response_format="b64_json",
    n=1
)

# 이미지 저장
image_data = response.data[0].b64_json
with open(filename, "wb") as f:
    f.write(base64.b64decode(image_data))
