import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta, timezone
import xml.etree.ElementTree as ET

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

now_utc = datetime.now(timezone.utc)
now = now_utc + timedelta(hours=9)
month = now.month
day = now.day
weekdays_kr = ["월요일", "화요일", "수요일", "목요일", "금요일", "토요일", "일요일"]
today_kr = weekdays_kr[now.weekday()]
today_str = now.strftime('%Y-%m-%d')

rss = ET.Element("rss", version="2.0")
channel = ET.SubElement(rss, "channel")
ET.SubElement(channel, "title").text = "폴리텍 식단 RSS"
ET.SubElement(channel, "link").text = "https://your-username.github.io/HanaLunch/docs/lunch_rss.xml"
ET.SubElement(channel, "description").text = "오늘의 메뉴 RSS crawling bot"
ET.SubElement(channel, "language").text = "ko"

item = ET.SubElement(channel, "item")
if today_kr in lunch_data:
    menu = lunch_data[today_kr].split(',')
    menu_str = "\n"+"\n".join([f"{i+1}. {item.strip()}" for i, item in enumerate(menu)])
    ET.SubElement(item, "title").text = f"{month}월 {day}일 {today_kr} 메뉴 😋"
    ET.SubElement(item, "description").text = menu_str
else:
    ET.SubElement(item, "title").text = f"{month}월 {day}일 {today_kr} 메뉴 없음"
    ET.SubElement(item, "description").text = "오늘의 중식 정보가 없습니다."

ET.SubElement(item, "pubDate").text = now.strftime('%a, %d %b %Y %H:%M:%S %z')

output_path = "docs/lunch_rss.xml"
tree = ET.ElementTree(rss)
tree.write(output_path, encoding="utf-8", xml_declaration=True)

print(f"RSS 피드가 {output_path}에 저장되었습니다.")
