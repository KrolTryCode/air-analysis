import os
from pathlib import Path

RAW_DIR = Path("data/raw")
RAW_DIR.mkdir(parents=True, exist_ok=True)

def download_kaggle_dataset():
    os.system("kaggle datasets download -d hdcortes/daily-steam-sales -p data/raw --unzip")

if __name__ == "__main__":
    download_kaggle_dataset()
