import json
import re
import requests
from pathlib import Path
import time

RAW_PATH = Path("data/raw/steam_specials_raw.json")
OUT_PATH = Path("data/raw/app_details.json")

def get_appid_from_url(url):
    m = re.search(r"app/(\d+)", url)
    return m.group(1) if m else None

def enrich_data():
    with open(RAW_PATH, "r", encoding="utf-8") as f:
        games = json.load(f)

    enriched = []
    for i, game in enumerate(games[:50]):  # ограничим до 50, чтобы не спамить API
        appid = get_appid_from_url(game["link"])
        if not appid:
            continue
        api_url = f"https://store.steampowered.com/api/appdetails?appids={appid}&l=en"
        try:
            r = requests.get(api_url, timeout=5)
            data = r.json().get(appid, {}).get("data", {})
            game.update({
                "appid": appid,
                "genres": [g["description"] for g in data.get("genres", [])],
                "release_date": data.get("release_date", {}).get("date", ""),
                "reviews": data.get("metacritic", {}).get("score", None)
            })
            enriched.append(game)
        except Exception as e:
            print(f"⚠️ Ошибка {appid}: {e}")
        time.sleep(0.5)

    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(enriched, f, ensure_ascii=False, indent=2)
    print(f"✅ Расширенные данные сохранены в {OUT_PATH}")

if __name__ == "__main__":
    enrich_data()
