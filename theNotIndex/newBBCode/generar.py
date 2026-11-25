import requests
import re
import json
import csv
import html
import time
import math
from decimal import Decimal, getcontext
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
from datetime import datetime

#fecha
fecha = datetime.now().strftime("%d/%b/%y")
fecha_archivo = datetime.now().strftime("%d-%b-%y")
archivo = f"{fecha_archivo}.txt"

#lovedCompletion
URL = "https://osucomplete.org/u/11394526/osu-loved"
headers = {"User-Agent": "Mozilla/5.0"}

pagina = requests.get(URL, headers=headers, timeout=12)
pagina.raise_for_status()
parser = BeautifulSoup(pagina.text, "html.parser")

mapas_pasados = None
mapas_restantes = None

for stat in parser.select("div.stats > div.stat"):
    clave = stat.select_one(".key")
    valor = stat.select_one(".value")

    if not clave or not valor:
        continue

    nombre = clave.get_text(strip=True).lower()
    numero = valor.get_text(strip=True).replace(",", "")

    if nombre == "maps passed":
        mapas_pasados = int(numero)
    elif nombre == "maps left":
        mapas_restantes = int(numero)

if mapas_pasados is not None and mapas_restantes is not None:
    total = mapas_pasados + mapas_restantes
    loved = mapas_pasados / total * 100

#plays, hits, percentage
baseurl = "https://osu.ppy.sh/users/11394526"
modes = {
    "/osu": "osu",
    "/taiko": "taiko",
    "/mania": "mania"
}

def extract_stat(page, key):
    selector = f"dl.profile-stats__entry--key-{key} dd.profile-stats__value"
    el = page.locator(selector)
    return el.inner_text().strip() if el.count() > 0 else None

def cleaned(text):
    if not text:
        return None
    return int(text.replace(",", ""))

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()

    playcounts = {}
    hits = {}

    for mode_path, mode_name in modes.items():
        url = baseurl + mode_path
        page.goto(url, wait_until="networkidle")
        page.wait_for_selector("dl.profile-stats__entry--key-play_count")

        play_count_raw = extract_stat(page, "play_count")
        total_hits_raw = extract_stat(page, "total_hits")

        playcounts[mode_name] = cleaned(play_count_raw)
        hits[mode_name] = cleaned(total_hits_raw)

    browser.close()
    
sPlays = playcounts["osu"]
sPlays2 = f"{sPlays:,}".replace(",", ".")
sPercent = (sPlays / 500)

tHits = hits["taiko"]
tHits2 = f"{tHits:,}".replace(",", ".")
tHitPercent = (tHits / 30000)  
tHitPercent10 = (tHits / 300000)  
jackTPlays = playcounts["taiko"]
jackTPercent = (jackTPlays / 50)

mHits = hits["mania"]
mHits2 = f"{mHits:,}".replace(",", ".")
mHitPercent = (mHits / 400000) 
jackMPlays = playcounts["mania"]
jackMPercent = (jackMPlays / 50)

#squares
floorS = math.floor(sPercent / 2)
unfloorS = 50 - floorS
squaresS = "■" * floorS + "□" * unfloorS

floorT = math.floor(tHitPercent / 2)
unfloorT = 50 - floorT
squaresT = "■" * floorT + "□" * unfloorT

floorM = math.floor(mHitPercent / 2)
unfloorM = 50 - floorM
squaresM = "■" * floorM + "□" * unfloorM

#template = (
#    "{date} {lovedCompletion:.5f} {jackTaikoPlays} {jackTaikoPercent:.2f} {jackManiaPlays} {jackManiaPercent:.2f} {standardPlays} {standardPercent:.4f} {drums} {drumPercent:.4f} {drumPercentTenth:.4f} {keys} {keyPercent:.4f} {squaresStandard} {squaresTaiko} {squaresMania}"
#)

with open("template.txt", "r", encoding="utf-8") as f:
    template = f.read()

resultado = template.format(date=fecha, lovedCompletion=loved, jackTaikoPlays=jackTPlays, jackTaikoPercent=jackTPercent, jackManiaPlays=jackMPlays, jackManiaPercent=jackMPercent, standardPlays=sPlays2, standardPercent=sPercent, drums=tHits2, keys=mHits2, drumPercent=tHitPercent, drumPercentTenth=tHitPercent10, keyPercent=mHitPercent, squaresStandard=squaresS, squaresTaiko=squaresT, squaresMania=squaresM)

with open(archivo, "w", encoding="utf-8") as f:
    f.write(resultado)