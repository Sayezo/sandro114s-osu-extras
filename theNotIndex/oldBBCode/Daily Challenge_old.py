import csv
import time
import random
from datetime import datetime, timedelta
from playwright.sync_api import sync_playwright

start_date = datetime(2026, 8, 12)
end_date = datetime.now()


output_file = "osutrack_full.csv"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()

    with open(output_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["title", "artist", "mapper", "href", "date", "scores", "mods"])

        current = start_date
        while current <= end_date:
            # Build date formats
            date_str = current.strftime("%Y%m%d")          # for URL
            date_formatted = current.strftime("%Y/%m/%d")  # for CSV

            url = f"https://ameobea.me/osutrack/daily-challenge/user/2/calendar?day={date_str}"
            print(f"Fetching {url}")

            page.goto(url)

            try:
                link = page.locator("h3.svelte-5iyy7u a").first
                title = link.inner_text()
                href = link.get_attribute("href")
            except:
                title = "NOT FOUND"
                href = "NOT FOUND"

            try:
                artist_raw = page.locator("div.root.svelte-5iyy7u b.svelte-5iyy7u").first.inner_text()
                artist = artist_raw.replace("By ", "").strip()
            except:
                artist = "NOT FOUND"

            try:
                mapper = page.locator("p.svelte-5iyy7u a.svelte-5iyy7u").first.inner_text()
            except:
                mapper = "NOT FOUND"

            try:
                scores_raw = page.locator("p.svelte-5iyy7u b.svelte-5iyy7u").first.inner_text()
                scores = scores_raw.replace(",", "")
            except:
                scores = "NOT FOUND"

            try:
                mod_spans = page.locator("span.mod-acronym").all_inner_texts()

                if len(mod_spans) > 0:
                    mods = ", ".join([m.strip() for m in mod_spans])
                else:
                    mods = page.locator("span.svelte-5iyy7u").nth(1).inner_text().strip()
            except:
                mods = "NOT FOUND"

            writer.writerow([title, artist, mapper, href, date_formatted, scores, mods])

            time.sleep(random.uniform(0.1, 0.3))

            current += timedelta(days=1)

    browser.close()

print("All dates processed!")
