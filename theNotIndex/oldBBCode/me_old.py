from playwright.sync_api import sync_playwright

BASE_URL = "https://osu.ppy.sh/users/11394526"
MODES = {
    "/osu": "osu",
    "/taiko": "taiko",
    "/fruits": "fruits",
    "/mania": "mania"
}

def extract_stat(page, key):
    selector = f"dl.profile-stats__entry--key-{key} dd.profile-stats__value"
    el = page.locator(selector)
    return el.inner_text().strip() if el.count() > 0 else None

def clean_play_count(text):
    if not text:
        return None
    return int(text.replace(",", ""))

def clean_hits(text):
    if not text:
        return None
    return text.replace(",", ".")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()

    playcounts = {}
    percentages = {}
    hits = {}

    for mode_path, mode_name in MODES.items():
        url = BASE_URL + mode_path
        page.goto(url, wait_until="networkidle")
        page.wait_for_selector("dl.profile-stats__entry--key-play_count")

        play_count_raw = extract_stat(page, "play_count")
        total_hits_raw = extract_stat(page, "total_hits")

        playcount = clean_play_count(play_count_raw)
        playcounts[mode_name] = playcount
        hits[mode_name] = clean_hits(total_hits_raw)

        if playcount is not None:
            if mode_name == "osu":
                percentages[mode_name] = playcount / 500
            else:
                percentages[mode_name] = playcount / 50

    browser.close()

print("\n=== Playcounts ===")
print("Taiko:", playcounts["taiko"], f"({percentages['taiko']:.2f}%)")
print("Catch:", playcounts["fruits"], f"({percentages['fruits']:.2f}%)")
print("Mania:", playcounts["mania"], f"({percentages['mania']:.2f}%)")

print("\n=== Hits ===")
print("Taiko:", hits["taiko"])
print("Mania:", hits["mania"])
print("Catch:", hits["fruits"])

print("\n=== Standard Playcount ===")
print("Standard:", playcounts["osu"], f"({percentages['osu']:.3f}%)")
