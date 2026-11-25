import csv
import datetime
import random

from playwright.sync_api import sync_playwright

start_date = datetime.datetime(2026, 8, 6, tzinfo=datetime.UTC).date()
end_date = datetime.datetime.now(tz=datetime.UTC).date()

output_file = "osutrack_full.csv"

days = (end_date - start_date).days
dates = [start_date + datetime.timedelta(days=i) for i in range(days + 1)]

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()

    with open(output_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["title", "artist", "mapper", "href", "date", "scores", "mods"])

        for current in dates:
            date_str = current.strftime("%Y%m%d")
            date_formatted = current.strftime("%Y/%m/%d")

            url = f"https://ameobea.me/osutrack/daily-challenge/user/2/calendar?day={date_str}"
            print(f"Fetching {url}")

            page.goto(url)
            page.wait_for_load_state("networkidle")

            if page.locator(".loading.svelte-5iyy7u").count() > 0:
                writer.writerow(
                    ["NOT FOUND"] * 4 + [date_formatted] + ["NOT FOUND"] * 2
                )
                continue

            link = page.locator("h3.svelte-5iyy7u a").first
            title = link.inner_text()
            href = link.get_attribute("href")

            artist = (
                page.locator("div.root.svelte-5iyy7u b.svelte-5iyy7u")
                .first.inner_text()
                .replace("By ", "")
                .strip()
            )

            mapper = page.locator("p.svelte-5iyy7u a.svelte-5iyy7u").first.inner_text()

            n_scores = (
                page.locator("p.svelte-5iyy7u b.svelte-5iyy7u")
                .first.inner_text()
                .replace(",", "")
            )

            mod_spans: list[str] = page.locator("span.mod-acronym").all_inner_texts()

            if len(mod_spans) > 0:
                mods = ", ".join([mod.strip() for mod in mod_spans])
            else:
                mods = page.locator("span.svelte-5iyy7u").nth(1).inner_text().strip()

            writer.writerow(
                [title, artist, mapper, href, date_formatted, n_scores, mods]
            )

            page.wait_for_timeout(random.uniform(100, 300))

print("All dates processed!")
