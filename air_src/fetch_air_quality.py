import requests
import pandas as pd
from pymongo import MongoClient
from pathlib import Path
from tqdm import tqdm
import time

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
PROC = ROOT / "data" / "processed"
RAW.mkdir(parents=True, exist_ok=True)
PROC.mkdir(parents=True, exist_ok=True)

CITIES = [
    "Магадан", "Якутск"
]

START = "2023-01-01"
END   = "2025-12-01"

client = MongoClient("mongodb://localhost:27017/")
db = client["air_quality_db"]
collection = db["air_quality"]


def geocode_city(city: str):
    url = "https://geocoding-api.open-meteo.com/v1/search"
    params = {"name": city, "count": 1, "language": "ru", "format": "json"}
    r = requests.get(url, params=params)

    if r.status_code != 200 or "results" not in r.json():
        return None, None

    result = r.json()["results"][0]
    return result["latitude"], result["longitude"]


def fetch_air_quality(lat, lon):
    url = "https://air-quality-api.open-meteo.com/v1/air-quality"

    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": ",".join([
            "pm2_5", "pm10", "carbon_monoxide",
            "nitrogen_dioxide", "sulphur_dioxide",
            "ozone", "dust", "uv_index", "ammonia"
        ]),
        "start_date": START,
        "end_date": END,
        "timezone": "auto"
    }

    r = requests.get(url, params=params)
    data = r.json()

    if "hourly" not in data:
        return None

    df = pd.DataFrame(data["hourly"])
    df["time"] = pd.to_datetime(df["time"])
    return df


def save_to_mongo(city, df):
    records = df.to_dict(orient="records")
    for rec in records:
        rec["city"] = city
    if records:
        collection.insert_many(records)


def main():
    all_data = []

    for city in tqdm(CITIES, desc="Обработка городов"):
        print(f"\nГород: {city}")

        lat, lon = geocode_city(city)
        if lat is None:
            print(f"Не найден город: {city}")
            continue

        print(f"Координаты: {lat}, {lon}")

        df = fetch_air_quality(lat, lon)
        if df is None:
            print(f"Нет данных по воздуху: {city}")
            continue

        df["city"] = city

        save_path = RAW / f"{city.replace(' ', '_')}.csv"
        df.to_csv(save_path, index=False, encoding="utf-8")


        save_to_mongo(city, df)
        print(f"Сохранено в MongoDB ({len(df)} записей)")

        all_data.append(df)

        time.sleep(0.5)

    if all_data:
        full_df = pd.concat(all_data, ignore_index=True)
        full_path = PROC / "air_quality_full.csv"
        full_df.to_csv(full_path, index=False, encoding="utf-8")


if __name__ == "__main__":
    main()
