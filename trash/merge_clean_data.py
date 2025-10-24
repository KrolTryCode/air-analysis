import pandas as pd
from pathlib import Path

RAW_DIR = Path("data/raw")
PROCESSED_DIR = Path("data/processed")
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

def clean_merge():
    df_api = pd.read_csv(RAW_DIR / "steam_app_details.csv")
    df_kaggle = pd.read_csv(RAW_DIR / "steam_sales_kaggle.csv")  # этот файл будет из Kaggle
    
    df_api["source"] = "api"
    df_kaggle["source"] = "kaggle"
    
    # нормализуем названия колонок
    df_api.rename(columns={"name": "game", "discount": "discount_percent"}, inplace=True)
    
    merged = pd.concat([df_api, df_kaggle], ignore_index=True)
    merged = merged.drop_duplicates(subset=["game"])
    merged.to_csv(PROCESSED_DIR / "merged_steam_data.csv", index=False)
    print(f"✅ Объединено {len(merged)} строк")

if __name__ == "__main__":
    clean_merge()
