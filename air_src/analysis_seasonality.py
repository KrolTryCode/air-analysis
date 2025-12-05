import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
import seaborn as sns

ROOT = Path(__file__).resolve().parents[1]
PROC = ROOT / "data" / "processed"
OUTPUT = ROOT / "output"
OUTPUT.mkdir(exist_ok=True)

INPUT = PROC / "air_quality_clean.csv"


def main():
    df = pd.read_csv(INPUT, parse_dates=["date"])

    df["month"] = df["date"].dt.month
    df["year"] = df["date"].dt.year

    # === Средние загрязнения по месяцам (вся РФ) ===
    monthly = df.groupby("month")[["pm25", "pm10", "no2", "so2", "o3"]].mean()

    print("\n=== Средние показатели по месяцам ===")
    print(monthly)

    # === Графики сезонности ===
    def plot_monthly(param, title, filename):
        plt.figure(figsize=(8, 5))
        monthly[param].plot(marker="o")
        plt.title(title)
        plt.xlabel("Месяц")
        plt.ylabel(param.upper())
        plt.grid(True)
        plt.xticks(range(1, 13))
        plt.tight_layout()
        plt.savefig(OUTPUT / filename)
        plt.close()

    plot_monthly("pm25", "Сезонность PM2.5 (2022–2024)", "seasonality_pm25.png")
    plot_monthly("pm10", "Сезонность PM10 (2022–2024)", "seasonality_pm10.png")
    plot_monthly("no2",  "Сезонность NO₂ (2022–2024)",  "seasonality_no2.png")
    plot_monthly("o3",   "Сезонность O₃ (2022–2024)",   "seasonality_o3.png")

    # === Тепловая карта сезонности по городам ===
    heat = (
        df.groupby(["city", "month"])["pm25"]
        .mean()
        .unstack(level=1)
    )

    plt.figure(figsize=(14, 7))
    sns.heatmap(heat, cmap="coolwarm", annot=False)
    plt.title("PM2.5 — сезонность по городам (heatmap)")
    plt.xlabel("Месяц")
    plt.ylabel("Город")
    plt.tight_layout()
    plt.savefig(OUTPUT / "seasonality_heatmap_pm25.png")
    plt.close()



if __name__ == "__main__":
    main()
