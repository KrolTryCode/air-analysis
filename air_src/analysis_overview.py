import pandas as pd
import matplotlib.pyplot as plt
from db_manager import DBManager
from config import OUTPUT


def main():
    db = DBManager()
    df = db.load_clean_data()
    
    if df.empty:
        print("Нет данных! Сначала запустите fetch_data.py")
        return
    
    print(f"Всего строк: {len(df)}")
    print(f"Городов: {df['city'].nunique()}")
    print(f"Города: {df['city'].unique()}\n")
    
    # Базовая статистика
    print("=== Базовая статистика загрязнения ===")
    print(df[["pm25", "pm10", "no2", "so2", "o3"]].describe())
    
    # Средний уровень по городам
    city_avg = (
        df.groupby("city")[["pm25", "pm10", "no2", "so2", "o3"]]
        .mean()
        .sort_values("pm25", ascending=False)
    )
    
    print("\nСредние уровни загрязнения по городам:")
    print(city_avg)
    
    # === Визуализации ===
    
    # 1. Распределение PM2.5
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
    plt.title("Средний уровень PM2.5 по городам (2023–2025)")
    plt.ylabel("PM2.5 (мкг/м³)")
    plt.tight_layout()
    plt.savefig(OUTPUT / "pm25_city_average.png")
    plt.close()
    
    print(f"\n✔ Графики сохранены в {OUTPUT}")
    
    db.close()


if __name__ == "__main__":
    main()