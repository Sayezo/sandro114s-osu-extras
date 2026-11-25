import csv
import random
import time
from datetime import datetime, timedelta

from playwright.sync_api import sync_playwright


START_DATE = datetime(2026, 10, 25)
END_DATE = datetime.now()

OUTPUT_FILE = "osutrack_full.csv"
BASE_URL = "https://ameobea.me/osutrack/daily-challenge/user/2/calendar"


def get_text(page, selector, default="NOT FOUND"):
    """Obtiene el texto del primer elemento que coincida con el selector."""
    try:
        return page.locator(selector).first.inner_text().strip()
    except Exception:
        return default


def get_attribute(page, selector, attribute, default="NOT FOUND"):
    """Obtiene un atributo del primer elemento que coincida con el selector."""
    try:
        value = page.locator(selector).first.get_attribute(attribute)
        return value if value is not None else default
    except Exception:
        return default


def get_mods(page):
    """Obtiene los mods del mapa."""
    try:
        mods = page.locator("span.mod-acronym").all_inner_texts()

        if mods:
            return ", ".join(mod.strip() for mod in mods)

        return page.locator("span.svelte-5iyy7u").nth(1).inner_text().strip()

    except Exception:
        return "NOT FOUND"


def get_daily_challenge(page, date):
    """Obtiene los datos del Daily Challenge. Devuelve None si no existe."""
    date_url = date.strftime("%Y%m%d")
    date_csv = date.strftime("%Y/%m/%d")

    url = f"{BASE_URL}?day={date_url}"
    print(f"Fetching {url}")

    page.goto(url, wait_until="domcontentloaded")

    title_selector = "h3.svelte-5iyy7u a.svelte-5iyy7u"

    # Esperamos hasta 2 segundos a que aparezca el challenge.
    # Si no aparece, asumimos que para esa fecha no existe.
    try:
        link = page.locator(title_selector).first
        link.wait_for(state="visible", timeout=2026)

        title = link.inner_text().strip()
        href = link.get_attribute("href") or "NOT FOUND"

    except Exception:
        print(f"No Daily Challenge found for {date_csv}. Stopping.")
        return None

    artist_selector = "div.root.svelte-5iyy7u b.svelte-5iyy7u"
    mapper_selector = "p.svelte-5iyy7u a.svelte-5iyy7u"
    scores_selector = "p.svelte-5iyy7u b.svelte-5iyy7u"

    artist = get_text(page, artist_selector)
    if artist != "NOT FOUND":
        artist = artist.removeprefix("By ").strip()

    mapper = get_text(page, mapper_selector)

    scores = get_text(page, scores_selector)
    if scores != "NOT FOUND":
        scores = scores.replace(",", "")

    mods = get_mods(page)

    return [
        title,
        artist,
        mapper,
        href,
        date_csv,
        scores,
        mods,
    ]


def main():
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page()

        with open(
            OUTPUT_FILE,
            "w",
            newline="",
            encoding="utf-8",
        ) as file:
            writer = csv.writer(file)

            writer.writerow([
                "title",
                "artist",
                "mapper",
                "href",
                "date",
                "scores",
                "mods",
            ])

            current_date = START_DATE

            while current_date <= END_DATE:
                row = get_daily_challenge(page, current_date)

                # No hay challenge para esta fecha, terminamos inmediatamente
                if row is None:
                    break

                writer.writerow(row)
                file.flush()  # Guarda inmediatamente los datos en el CSV

                time.sleep(random.uniform(0.1, 0.3))
                current_date += timedelta(days=1)

        browser.close()

    print("All dates processed!")


if __name__ == "__main__":
    main()