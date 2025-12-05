import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "data" / "processed"
OUTPUT = ROOT / "output"
OUTPUT.mkdir(exist_ok=True)

INPUT = PROCESSED / "air_quality_clean.csv"


def main():
    df = pd.read_csv(INPUT, parse_dates=["date"])

    print(f"Всего строк: {len(df)}")
    print(f"Городов: {df['city'].nunique()}")
    print(f"Города: {df['city'].unique()}")
    print()

    # --- Базовая статистика ---
    print("\n=== Базовая статистика загрязнения (PM2.5, PM10, NO2, SO2, O3) ===")
    print(df[["pm25", "pm10", "no2", "so2", "o3"]].describe())

    # --- Средний уровень загрязнения по каждому городу ---
    city_avg = (
        df.groupby("city")[["pm25", "pm10", "no2", "so2", "o3"]]
        .mean()
        .sort_values("pm25", ascending=False)
    )

    print("\nСредние уровни загрязнения по городам:")
    print(city_avg)

    # === Визуализации ===

    # 1. Распределение PM2.5 по всей России
    plt.figure(figsize=(8, 5))
    df["pm25"].hist(bins=40)
    plt.title("Распределение PM2.5")
    plt.xlabel("PM2.5 (мкг/м³)")
    plt.ylabel("Частота")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(OUTPUT / "pm25_distribution.png")
    plt.close()

    # 2. Средний PM2.5 по городам
    plt.figure(figsize=(12, 6))
    city_avg["pm25"].plot(kind="bar")
    plt.title("Средний уровень PM2.5 по городам (2022–2024)")
    plt.ylabel("PM2.5 (мкг/м³)")
    plt.tight_layout()
    plt.savefig(OUTPUT / "pm25_city_average.png")
    plt.close()


if __name__ == "__main__":
    main()
