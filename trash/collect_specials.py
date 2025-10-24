# import requests
# import re
# import json
# from pathlib import Path
# from bs4 import BeautifulSoup

# OUT_PATH = Path("data/raw/steam_specials_raw.json")
# OUT_PATH.parent.mkdir(parents=True, exist_ok=True)

# def fetch_specials():
#     print("🛒 Сбор скидок со страницы Steam Specials...")
#     url = "https://store.steampowered.com/search/?specials=1"
#     r = requests.get(url)
#     soup = BeautifulSoup(r.text, "html.parser")

#     items = []
#     for row in soup.select(".search_result_row"):
#         name = row.select_one(".title").text.strip()
#         link = row.get("href").split("?")[0]
#         discount_el = row.select_one(".search_discount span")
#         discount = discount_el.text.strip().replace("%", "") if discount_el else "0"
#         price_el = row.select_one(".discount_final_price")
#         price = price_el.text.strip().replace("₽", "").replace(" ", "") if price_el else ""
#         items.append({
#             "name": name,
#             "discount": discount,
#             "price": price,
#             "link": link
#         })

#     print(f"📦 Собрано {len(items)} записей")
#     with open(OUT_PATH, "w", encoding="utf-8") as f:
#         json.dump(items, f, ensure_ascii=False, indent=2)
#     print(f"✅ Данные сохранены в {OUT_PATH}")

# if __name__ == "__main__":
#     fetch_specials()
