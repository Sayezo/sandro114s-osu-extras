
import requests
from bs4 import BeautifulSoup
import time
import json

modes = {
    "osu": 50,
    "taiko": 8,
    "fruits": 6,
    "mania": 40
}

players = {}
session = requests.Session()

for mode, page_count in modes.items():
    players[mode] = []
    for page in range(1, page_count + 1):
        url = (
            f"https://osu.ppy.sh/rankings/{mode}/global/"
            f"performance?country=ES&filter=all&page={page}"
        )
        try:
            response = session.get(url, timeout=15)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")

            for player in soup.select(
                "a.ranking-page-table-main__link"
            ):
                players[mode].append({
                    "name": player.get_text(strip=True),
                    "id": int(player["data-user-id"])
                })

            print(f"[{mode}] Page {page}/{page_count} completed")
        except requests.RequestException as error:
            print(f"[{mode}] Page {page} failed: {error}")

        except (KeyError, ValueError) as error:
            print(f"[{mode}] Page {page} parsing error: {error}")
        time.sleep(2)
session.close()

with open("osu_players.json", "w", encoding="utf-8") as file:
    json.dump(players, file, indent=4, ensure_ascii=False)
print(":p")
