import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROC = ROOT / "data" / "processed"
OUTPUT = ROOT / "output"
OUTPUT.mkdir(exist_ok=True)

INPUT = PROC / "air_quality_clean.csv"


def main():
    df = pd.read_csv(INPUT, parse_dates=["date"])

    params = ["pm25", "pm10", "no2", "so2", "o3", "uv", "nh3", "dust", "co"]

    corr = df[params].corr()
    print("\n=== Корреляционная матрица ===")
    print(corr)

    plt.figure(figsize=(10, 8))
    sns.heatmap(corr, annot=True, cmap="coolwarm", fmt=".2f")
    plt.title("Корреляционная матрица загрязнений")
    plt.tight_layout()
    plt.savefig(OUTPUT / "correlation_heatmap.png")
    plt.close()

    plt.figure(figsize=(7, 5))
    sns.scatterplot(data=df, x="pm25", y="pm10", alpha=0.2)
    plt.title("PM2.5 vs PM10")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(OUTPUT / "pm25_vs_pm10.png")
    plt.close()

    plt.figure(figsize=(7, 5))
    sns.scatterplot(data=df, x="pm25", y="o3", alpha=0.2)
    plt.title("PM2.5 vs O₃")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(OUTPUT / "pm25_vs_o3.png")
    plt.close()

    temp_corr = df[["pm25", "o3", "uv"]].corr()
    print("\n=== Корреляции с метеопоказателями (замены): ===")
    print(temp_corr)



if __name__ == "__main__":
    main()
