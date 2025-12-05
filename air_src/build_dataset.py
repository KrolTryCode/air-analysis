import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "data" / "processed"
RAW = ROOT / "data" / "raw"

INPUT = PROCESSED / "air_quality_full.csv"
OUTPUT = PROCESSED / "air_quality_clean.csv"

def main():
    df = pd.read_csv(INPUT, parse_dates=["time"])

    print(f"Всего строк: {len(df)}")
    print(f"Города: {df['city'].nunique()}")

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

    df = df.dropna(axis=1, how='all')

    cities_before = df['city'].nunique()

    valid_cities = (
        df.groupby("city")["pm25"]
        .apply(lambda x: x.notna().sum() > 10000)
    )

    valid_city_list = valid_cities[valid_cities].index.tolist()

    print(f"Города с полноценными данными: {len(valid_city_list)} / {cities_before}")
    print(valid_city_list)

    df = df[df["city"].isin(valid_city_list)]

    df["date"] = df["datetime"].dt.date

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

    print(f"Получено строк: {len(agg)}")

    for col in ["pm25", "pm10", "no2", "so2", "o3"]:
        agg = agg[(agg[col] >= 0) & (agg[col] < 5000)]

    agg.to_csv(OUTPUT, index=False, encoding="utf-8")
    print(f"\n✔ Чистый датасет сохранён: {OUTPUT}")
    print(f"Готово. Формат таблицы:\n{agg.head(5)}")


if __name__ == "__main__":
    main()
