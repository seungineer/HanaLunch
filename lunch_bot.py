import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime

URL = "https://www.kopo.ac.kr/gm/content.do?menu=12623"
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

now = datetime.now()
weekdays_kr = ["월요일", "화요일", "수요일", "목요일", "금요일", "토요일", "일요일"]
today_kr = weekdays_kr[now.weekday()]  # 한국어 요일 변환

payload = json.dumps({"text": f"😋 오늘의 중식 메뉴:\n{lunch_data[today_kr]}"})
headers = {"Content-Type": "application/json"}

WEBHOOK_URL = os.getenv("WEBHOOK_URL")

response = requests.post(WEBHOOK_URL, headers=headers, data=payload)

print(f"Webhook 응답 코드: {response.status_code}")
