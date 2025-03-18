import requests
import json
import os
from bs4 import BeautifulSoup
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
month = now.month
day = now.day
weekdays_kr = ["월요일", "화요일", "수요일", "목요일", "금요일", "토요일", "일요일"]
today_kr = weekdays_kr[now.weekday()]  # 한국어 요일 변환

if today_kr in lunch_data:
    menu = lunch_data[today_kr].split(',')
    menu_list = []
    for item in menu:
        menu_list.append(str(len(menu_list) + 1) +'.' + item.strip() + '\\\n')

    message_text = f"{month}월 {day}일 {today_kr}\n😋 오늘의 메뉴\n{''.join(menu_list)}"
else:
    message_text = f"{month}월 {day}일 {today_kr}\n오늘의 중식 정보가 없습니다."

WEBHOOK_URL = os.getenv("WEBHOOK_URL")
payload = json.dumps({"text": message_text})
headers = {"Content-Type": "application/json"}
response = requests.post(WEBHOOK_URL, headers=headers, data=payload)

print(f"Webhook 응답 코드: {response.status_code}")
