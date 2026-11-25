import requests
import re
from bs4 import BeautifulSoup

# request
URL = "https://osucomplete.org/u/11394526/osu-loved"
headers = {"User-Agent": "Mozilla/5.0"}

# pedir la pagina y parsearla
pagina = requests.get(URL, headers=headers)
parser = BeautifulSoup(pagina.text, 'html.parser')

# encontrar el div y el porcentaje
busca = parser.find_all("div", class_="value")
teta = busca[2]
limpio = teta["title"]

match = re.search(r"Best was (.*?)on", limpio)
if match:
    porcentaje = match.group(1)
    print(porcentaje)
else:
    print("rompieron la pagina xdddd")