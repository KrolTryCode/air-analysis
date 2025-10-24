# import requests
# import time
# import pandas as pd
# from pathlib import Path

# RAW_DIR = Path("data/raw")
# RAW_DIR.mkdir(parents=True, exist_ok=True)

# def get_app_list():
#     url = "https://api.steampowered.com/ISteamApps/GetAppList/v2/"
#     return requests.get(url).json()["applist"]["apps"]

# def get_app_details(appid):
#     url = f"https://store.steampowered.com/api/appdetails?appids={appid}&cc=us&l=en"
#     r = requests.get(url)
#     try:
#         data = r.json().get(str(appid), {})
#         if data.get("success"):
#             d = data.get("data", {})
#             return {
#                 "appid": appid,
#                 "name": d.get("name"),
#                 "release_date": d.get("release_date", {}).get("date"),
#                 "price": d.get("price_overview", {}).get("final", None),
#                 "discount": d.get("price_overview", {}).get("discount_percent", None),
#                 "genres": ", ".join([g["description"] for g in d.get("genres", [])]) if d.get("genres") else None,
#             }
#     except Exception:
#         pass

# def main():
#     app_list = get_app_list()[:300]  # 300 для теста
#     data = [get_app_details(a["appid"]) for a in app_list]
#     df = pd.DataFrame([x for x in data if x])
#     df.to_csv(RAW_DIR / "steam_app_details.csv", index=False)
#     print(f"✅ Собрано {len(df)} записей из Steam API")

# if __name__ == "__main__":
#     main()
