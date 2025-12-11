import pandas as pd
import matplotlib.pyplot as plt
from db_manager import DBManager
from config import OUTPUT


def main():
    db = DBManager()
    df = db.load_clean_data()
    
    if df.empty:
        print("Нет данных!")
        return
    
    city_stats = (
        df.groupby("city")[["pm25", "pm10", "no2", "so2", "o3"]]
        .mean()
        .sort_values("pm25", ascending=False)
    )
    
    print("\n=== Рейтинг городов по PM2.5 ===")
    print(city_stats["pm25"])
    
    worst = city_stats["pm25"].head(5)
    print("\nТоп-5 самых загрязнённых городов по PM2.5:")
    print(worst)
    
    best = city_stats["pm25"].tail(5)
    print("\nТоп-5 самых чистых городов по PM2.5:")
    print(best)
    
    # Интегральный индекс
    norm = (city_stats - city_stats.min()) / (city_stats.max() - city_stats.min())
    norm["pollution_index"] = norm[["pm25", "pm10", "no2", "so2"]].mean(axis=1)
    
    norm_sorted = norm.sort_values("pollution_index", ascending=False)
    
    print("\n=== Интегральный индекс загрязнения (0–1) ===")
    print(norm_sorted["pollution_index"])
    
    # Визуализации
    def save_bar(data, title, filename):
        plt.figure(figsize=(12, 6))
        data.plot(kind="bar")
        plt.title(title)
        plt.ylabel("Уровень загрязнения (мкг/м³)")
        plt.tight_layout()
        plt.savefig(OUTPUT / filename)
        plt.close()
    
    save_bar(city_stats["pm25"], "Средний PM2.5 по городам (2023–2025)", "pm25_by_city.png")
    save_bar(city_stats["pm10"], "Средний PM10 по городам (2023–2025)", "pm10_by_city.png")
    save_bar(city_stats["no2"], "NO₂ по городам", "no2_by_city.png")
    
    # Интегральный индекс
    plt.figure(figsize=(12, 6))
    norm_sorted["pollution_index"].plot(kind="bar")
    plt.title("Интегральный индекс загрязнения по городам (0–1)")
    plt.ylabel("Индекс загрязнения")
    plt.tight_layout()
    plt.savefig(OUTPUT / "pollution_index.png")
    plt.close()
    
    print(f"\n✔ Графики сохранены в {OUTPUT}")
    
    db.close()


if __name__ == "__main__":
    main()