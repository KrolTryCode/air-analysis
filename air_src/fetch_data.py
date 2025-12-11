import requests
import pandas as pd
from tqdm import tqdm
import time
from db_manager import DBManager
from config import CITIES, START_DATE, END_DATE


def geocode_city(city: str):
    """Получить координаты города"""
    url = "https://geocoding-api.open-meteo.com/v1/search"
    params = {"name": city, "count": 1, "language": "ru", "format": "json"}
    r = requests.get(url, params=params)
    
    if r.status_code != 200 or "results" not in r.json():
        return None, None
    
    result = r.json()["results"][0]
    return result["latitude"], result["longitude"]


def fetch_air_quality(lat, lon):
    """Получить данные о качестве воздуха"""
    url = "https://air-quality-api.open-meteo.com/v1/air-quality"
    
    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": ",".join([
            "pm2_5", "pm10", "carbon_monoxide",
            "nitrogen_dioxide", "sulphur_dioxide",
            "ozone", "dust", "uv_index", "ammonia"
        ]),
        "start_date": START_DATE,
        "end_date": END_DATE,
        "timezone": "auto"
    }
    
    r = requests.get(url, params=params)
    data = r.json()
    
    if "hourly" not in data:
        return None
    
    df = pd.DataFrame(data["hourly"])
    df["time"] = pd.to_datetime(df["time"])
    return df


def process_and_clean_data(db: DBManager):
    """Обработать и очистить данные"""
    print("\n=== Обработка и очистка данных ===")
    
    df = db.load_raw_data()
    
    if df.empty:
        print("Нет данных для обработки!")
        return
    
    print(f"Загружено строк: {len(df)}")
    
    # Переименование колонок
    df = df.rename(columns={
        "time": "datetime",
        "pm2_5": "pm25",
        "carbon_monoxide": "co",
        "nitrogen_dioxide": "no2",
        "sulphur_dioxide": "so2",
        "ozone": "o3",
        "dust": "dust",
        "uv_index": "uv",
        "ammonia": "nh3"
    })
    
    # Удаление полностью пустых колонок
    df = df.dropna(axis=1, how='all')
    
    # Фильтрация городов с достаточным количеством данных
    cities_before = df['city'].nunique()
    
    valid_cities = (
        df.groupby("city")["pm25"]
        .apply(lambda x: x.notna().sum() > 10000)
    )
    
    valid_city_list = valid_cities[valid_cities].index.tolist()
    
    print(f"Города с полноценными данными: {len(valid_city_list)} / {cities_before}")
    print(valid_city_list)
    
    df = df[df["city"].isin(valid_city_list)]
    
    # Агрегация по дням
    df["date"] = pd.to_datetime(df["datetime"]).dt.date
    
    agg = df.groupby(["city", "date"]).agg({
        "pm25": "mean",
        "pm10": "mean",
        "no2": "mean",
        "so2": "mean",
        "o3": "mean",
        "co": "mean",
        "dust": "mean",
        "uv": "mean",
        "nh3": "mean"
    }).reset_index()
    
    # Удаление выбросов
    for col in ["pm25", "pm10", "no2", "so2", "o3"]:
        if col in agg.columns:
            agg = agg[(agg[col] >= 0) & (agg[col] < 5000)]
    
    print(f"Получено строк после очистки: {len(agg)}")
    
    # Сохранение в MongoDB
    db.save_clean_data(agg)
    print("✔ Очищенные данные сохранены в MongoDB")


def main():
    """Основная функция загрузки данных"""
    db = DBManager()
    
    print("=== Загрузка данных о качестве воздуха ===")
    print(f"Период: {START_DATE} — {END_DATE}")
    print(f"Городов: {len(CITIES)}\n")
    
    # Очистка старых данных
    response = input("Очистить существующие данные? (y/n): ")
    if response.lower() == 'y':
        db.clear_collection("raw")
        db.clear_collection("clean")
        print("Данные очищены\n")
    
    # Загрузка данных по городам
    for city in tqdm(CITIES, desc="Загрузка данных"):
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
        
        db.save_raw_data(city, df)
        print(f"Сохранено в MongoDB: {len(df)} записей")
        
        time.sleep(0.5)
    
    # Обработка и очистка данных
    process_and_clean_data(db)
    
    # Статистика
    print("\n=== Итоговая статистика ===")
    print(f"Городов в базе: {db.get_cities_count()}")
    min_date, max_date = db.get_date_range()
    if min_date and max_date:
        print(f"Период данных: {min_date} — {max_date}")
    
    db.close()


if __name__ == "__main__":
    main()