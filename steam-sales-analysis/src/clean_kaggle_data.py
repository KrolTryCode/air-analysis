import json
import pandas as pd
from pathlib import Path

RAW_PATH = Path("data/raw/steamgames.json")
PROCESSED_DIR = Path("data/processed")
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_PATH = PROCESSED_DIR / "steam_sales_clean.csv"

def clean_text(text):
    if not isinstance(text, str):
        return text
    return text.replace("\r", "").replace("\n", "").replace("\t", "").strip()

def main():
    with open(RAW_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    print(f"Найдено {len(data)} записей")

    df = pd.DataFrame(data)

    for col in ["name", "orig_price", "disc_price", "discount"]:
        if col in df.columns:
            df[col] = df[col].astype(str).apply(clean_text)

    for col in ["orig_price", "disc_price", "discount"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df["tags"] = df["tags"].apply(
        lambda tags: ", ".join([clean_text(t) for t in tags]) if isinstance(tags, list) else ""
    )

    df = df.dropna(subset=["discount"])
    df = df[df["discount"] > 0]

    df = df.drop_duplicates(subset=["name"])

    df.to_csv(OUTPUT_PATH, index=False)
    print(f"данные сохранены в {OUTPUT_PATH}")
    print(df.head(5))

if __name__ == "__main__":
    main()
