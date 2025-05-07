import requests
import json
import os
from bs4 import BeautifulSoup
from datetime import datetime, timedelta, timezone
from openai import OpenAI
import xml.etree.ElementTree as ET

URL = "https://www.kopo.ac.kr/gm/content.do?menu=12623"
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY_SGNR"))

# ==================== 메뉴 크롤링 ====================
response = requests.get(URL)
response.encoding = 'utf-8'
soup = BeautifulSoup(response.text, "html.parser")

meal_table = soup.find("table", class_="tbl_table menu")
rows = meal_table.find("tbody").find_all("tr")

lunch_data = {}
for row in rows:
    columns = row.find_all("td")
    if len(columns) >= 3:
        date = columns[0].get_text(strip=True)
        lunch = columns[2].get_text(strip=True).replace("\n", ", ")
        lunch_data[date] = lunch

now_utc = datetime.now(timezone.utc)
now = now_utc + timedelta(hours=9)
month = now.month
day = now.day
weekdays_kr = ["월요일", "화요일", "수요일", "목요일", "금요일", "토요일", "일요일"]
today_kr = weekdays_kr[now.weekday()]
today_str = now.strftime('%Y-%m-%d')

# ==================== 식단 탄단지 정보 요청 ====================
if today_kr in lunch_data:
    menu_items = lunch_data[today_kr].split('\r,')
    if len(menu_items) <= 2:
        print("menu_items: " + menu_items)
        print("정상적인 식단이 아닙니다.")
        exit()
    numbered_menu = "\n".join([f"{i+1}. {item.strip()}" for i, item in enumerate(menu_items)])
    prompt = f"""아래는 대학교 학생식당의 점심 메뉴입니다. 각 메뉴에 대해 메뉴명, 탄수화물(g), 단백질(g), 지방(g), 칼로리(kcal)를 JSON 형태로 제공해주세요. 각각의 데이터 정보는  농촌진흥청의 국가표준식품성분표, 식품의약품안전처의 식품영양정보, 또는 일반적인 영양 성분 앱 같은 곳에서 제공하는 1인분 기준 수치를 활용하세요.
    
{numbered_menu}

형식은 다음과 같습니다:
{{
  "1": {{"메뉴": "...", "탄수화물(g)": ..., "단백질(g)": ..., "지방(g)": ..., "칼로리(kcal)": ...}},
  "2": ...
}}"""

    completion = client.chat.completions.create(
        model="gpt-3.5-turbo-0125",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )

    try:
        nutrition_data = json.loads(completion.choices[0].message.content)

    except Exception as e:
        print("OpenAI 응답을 파싱 실패")
        nutrition_data = {}
else:
    print("식단 정보 없음")
    nutrition_data = {}

# ==================== HTML 테이블 생성 ====================
def generate_html_table(data):
    if not data:
        return "<p>오늘의 식단 정보가 없습니다.</p>"
    html = "<table border='2'><tr><th>메뉴</th><th>탄수화물(g)</th><th>단백질(g)</th><th>지방(g)</th><th>칼로리(kcal)</th></tr>"
    for item in data.values():
        html += f"<tr><td>{item['메뉴']}</td><td>{item['탄수화물(g)']}</td><td>{item['단백질(g)']}</td><td>{item['지방(g)']}</td><td>{item['칼로리(kcal)']}</td></tr>"
    html += "</table>"
    return html

table_html = generate_html_table(nutrition_data)

# ==================== RSS를 위한 ElementTree 생성부 ====================

rss = ET.Element("rss", version="2.0")
channel = ET.SubElement(rss, "channel")
ET.SubElement(channel, "title").text = "폴리텍 식단 RSS"
ET.SubElement(channel, "link").text = "https://seungineer.github.io/HanaLunch/docs/lunch_rss.xml"
ET.SubElement(channel, "description").text = "오늘의 메뉴 RSS crawling bot"
ET.SubElement(channel, "language").text = "ko"

item = ET.SubElement(channel, "item")
if today_kr in lunch_data:
    ET.SubElement(item, "title").text = f"{month}월 {day}일 {today_kr} 메뉴 😋"
    ET.SubElement(item, "description").text = f"<br>{table_html}"
    print(table_html)
else:
    ET.SubElement(item, "title").text = f"{month}월 {day}일 {today_kr} 메뉴 없음"
    ET.SubElement(item, "description").text = "오늘의 중식 정보가 없습니다."

ET.SubElement(item, "pubDate").text = now.strftime('%a, %d %b %Y %H:%M:%S %z')

output_path = "docs/lunch_rss.xml"
tree = ET.ElementTree(rss)
tree.write(output_path, encoding="utf-8", xml_declaration=True)

print(f"RSS 피드가 {output_path}에 저장되었습니다.")
