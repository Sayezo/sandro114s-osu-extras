import requests
from bs4 import BeautifulSoup

URL = "https://osucomplete.org/u/11394526/osu-loved"
headers = {"User-Agent": "Mozilla/5.0"}

# pedir la pagina y parsearla
pagina = requests.get(URL, headers=headers, timeout=15)
pagina.raise_for_status()

parser = BeautifulSoup(pagina.text, "html.parser")

# valores por defecto
mapas_pasados = None
mapas_restantes = None

# recorrer cada bloque de estadisticas
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

# calcular el porcentaje con el mismo peso para cada mapa
if mapas_pasados is not None and mapas_restantes is not None:
    total = mapas_pasados + mapas_restantes
    porcentaje = mapas_pasados / total * 100

    print(f"{porcentaje:.5f}%")
else:
    print("No se encontraron maps passed o maps left.")
