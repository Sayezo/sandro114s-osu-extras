import requests
import re
import json
import csv
import html
from decimal import Decimal, getcontext
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
import time

getcontext().prec = 21

BASE_URL = f"https://osu.ppy.sh/users/11394526"
MODES = ["/osu", "/taiko", "/fruits", "/mania"]
headers = {"User-Agent": "Mozilla/5.0"}

html_text = requests.get(BASE_URL, headers=headers).text
matches = re.findall(r'data-initial-data="([^"]+)"', html_text)

data = None
for block in matches:
    try:
        unescaped = html.unescape(block)
        parsed = json.loads(unescaped)
        if "achievements" in parsed:
            data = parsed
            break
    except:
        continue

achievements = data["achievements"]
unlocked = set()

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()

    for mode in MODES:
        url = BASE_URL + mode
        page.goto(url)

        page.wait_for_load_state("networkidle")
        time.sleep(0.4)

        html_dynamic = page.content()
        soup = BeautifulSoup(html_dynamic, "html.parser")

        imgs = soup.find_all("img", class_="badge-achievement__image")

        for img in imgs:
            alt = img.get("alt", "").strip()
            if alt:
                unlocked.add(alt)

    browser.close()

columns = [
    "name",
    "description",
    "instructions",
    "grouping",
    "mode",
    "achieved_percent",
    "achieved_count",
    "unlocked",
]

cleaned = []

for medal in achievements:
    row = {}

    for key in columns:
        if key == "unlocked":
            row["unlocked"] = medal["name"] in unlocked
        else:
            value = medal.get(key, None)

            if key == "instructions" and value:
                value = BeautifulSoup(value, "html.parser").get_text()

            if key == "achieved_percent" and value is not None:
                value = Decimal(str(value))
                
            if key == "mode":
                value = value or "any"


            row[key] = value

    cleaned.append(row)

cleaned.sort(
    key=lambda m: m["achieved_count"]
    if m["achieved_count"] is not None
    else Decimal("21")
)

with open("osu_medals.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(columns)

    for medal in cleaned:
        row = []
        for key in columns:
            value = medal[key]
                
            if key == "achieved_percent" and value is not None:
                value = (value * Decimal("100")).normalize()
                value = f"{value}%"
            row.append(value)
        writer.writerow(row)

print("Dinosaur rawr :3")
