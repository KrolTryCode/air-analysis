import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

INPUT = Path("data/processed/steam_sales_clean.csv")
OUT_DIR = Path("data/processed")

sns.set(style="whitegrid")

def plot_discount_distribution(df):
    plt.figure(figsize=(8,5))
    sns.histplot(df["discount"], bins=15, kde=True, color="skyblue")
    plt.title("Распределение скидок на игры в Steam")
    plt.xlabel("Скидка (%)")
    plt.ylabel("Количество игр")
    plt.tight_layout()
    plt.savefig(OUT_DIR / "discount_distribution.png")
    plt.close()
    print(" график discount_distribution.png")


def plot_top_genres(df):
    df = df.dropna(subset=["tags"])
    df["main_tag"] = df["tags"].apply(lambda x: x.split(",")[0].strip() if isinstance(x, str) and x else None)
    genre_stats = df.groupby("main_tag")["discount"].mean().sort_values(ascending=False).head(10)
    plt.figure(figsize=(8,5))
    sns.barplot(x=genre_stats.values, y=genre_stats.index, palette="viridis")
    plt.title("Средняя скидка по жанрам (топ-10)")
    plt.xlabel("Средняя скидка (%)")
    plt.ylabel("Жанр")
    plt.tight_layout()
    plt.savefig(OUT_DIR / "top_genres.png")
    plt.close()
    print("график top_genres.png")


def plot_discount_by_year(df):
    if "release_date" not in df.columns:
        print("release_date отсутствует")
        return
    df["release_year"] = pd.to_datetime(df["release_date"], errors="coerce").dt.year
    df = df.dropna(subset=["release_year", "discount"])

    year_avg = df.groupby("release_year")["discount"].mean().reset_index()
    plt.figure(figsize=(8,5))
    sns.lineplot(data=year_avg, x="release_year", y="discount", marker="o")
    plt.title("Средняя скидка по году релиза")
    plt.xlabel("Год релиза")
    plt.ylabel("Средняя скидка (%)")
    plt.tight_layout()
    plt.savefig(OUT_DIR / "discount_by_year.png")
    plt.close()
    print("график discount_by_year.png")


def plot_price_vs_discount(df):
    if not all(col in df.columns for col in ["orig_price", "discount"]):
        return

    plt.figure(figsize=(7,5))
    sns.scatterplot(data=df, x="orig_price", y="discount", alpha=0.6, color="teal")
    plt.title("Связь между ценой и скидкой")
    plt.xlabel("Оригинальная цена (₽)")
    plt.ylabel("Скидка (%)")
    plt.xscale("log")
    plt.tight_layout()
    plt.savefig(OUT_DIR / "price_vs_discount.png")
    plt.close()
    print("✅ Сохранён график price_vs_discount.png")


def main():
    df = pd.read_csv(INPUT)
    plot_discount_distribution(df)
    plot_top_genres(df)
    plot_discount_by_year(df)
    plot_price_vs_discount(df)
    print("графики сохранены в data/processed/")

if __name__ == "__main__":
    main()
