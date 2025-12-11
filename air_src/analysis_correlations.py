import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from db_manager import DBManager
from config import OUTPUT


def main():
    db = DBManager()
    df = db.load_clean_data()
    
    if df.empty:
        print("Нет данных!")
        return
    
    params = ["pm25", "pm10", "no2", "so2", "o3", "uv", "nh3", "dust", "co"]
    params = [p for p in params if p in df.columns]
    
    corr = df[params].corr()
    print("\n=== Корреляционная матрица ===")
    print(corr)
    
    # Тепловая карта
    plt.figure(figsize=(10, 8))
    sns.heatmap(corr, annot=True, cmap="coolwarm", fmt=".2f")
    plt.title("Корреляционная матрица загрязнений")
    plt.tight_layout()
    plt.savefig(OUTPUT / "correlation_heatmap.png")
    plt.close()
    
    # PM2.5 vs PM10
    plt.figure(figsize=(7, 5))
    sns.scatterplot(data=df, x="pm25", y="pm10", alpha=0.2)
    plt.title("PM2.5 vs PM10")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(OUTPUT / "pm25_vs_pm10.png")
    plt.close()
    
    # PM2.5 vs O₃
    plt.figure(figsize=(7, 5))
    sns.scatterplot(data=df, x="pm25", y="o3", alpha=0.2)
    plt.title("PM2.5 vs O₃")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(OUTPUT / "pm25_vs_o3.png")
    plt.close()
    
    print(f"\n✔ Графики сохранены в {OUTPUT}")
    
    db.close()


if __name__ == "__main__":
    main()