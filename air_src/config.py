from pathlib import Path

# Пути
ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "output"
OUTPUT.mkdir(exist_ok=True)

# MongoDB
MONGO_URI = "mongodb://mongodb:27017/"
DB_NAME = "air_quality_db"
COLLECTION_RAW = "raw_data"
COLLECTION_CLEAN = "clean_data"

# Города для анализа
CITIES = [
    "Москва",
    "Санкт-Петербург",
    "Тула",
    "Ростов-на-Дону",
    "Воронеж",
    "Краснодар",
    "Мурманск",
    "Волгоград",
    "Нижний Новгород",
    "Калининград",
    "Самара",
    "Саратов",
    "Екатеринбург",
    "Челябинск",
    "Уфа",
    "Казань",
    "Тюмень",
    "Архангельск"
]

# Период данных
START_DATE = "2024-01-01"
END_DATE = "2025-12-01"