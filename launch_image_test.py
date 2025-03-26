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
1. 미야자키난방
2. 쌀밥
3. 아욱된장국
4. 매운순두부양념찜
5. 그린샐러드*키위드레싱
6. 깍두기
"""

# 프롬프트 생성
prompt = f"A well-composed Korean meal showing: {menu_text}"

# 이미지 생성
response = client.images.generate(
    model="dall-e-3",
    prompt=prompt,
    size="1024x1024",
    response_format="b64_json",
    n=1
)

# 이미지 저장
image_data = response.data[0].b64_json
with open(filename, "wb") as f:
    f.write(base64.b64decode(image_data))
