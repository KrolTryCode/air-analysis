import pandas as pd
from pymongo import MongoClient
from datetime import datetime
from config import MONGO_URI, DB_NAME, COLLECTION_RAW, COLLECTION_CLEAN


class DBManager:
    def __init__(self):
        self.client = MongoClient(MONGO_URI)
        self.db = self.client[DB_NAME]
        self.raw_collection = self.db[COLLECTION_RAW]
        self.clean_collection = self.db[COLLECTION_CLEAN]
    
    def save_raw_data(self, city, df):
        """Сохранить сырые данные в MongoDB"""
        records = df.to_dict(orient="records")
        for rec in records:
            rec["city"] = city
            rec["time"] = pd.to_datetime(rec["time"])
        
        if records:
            self.raw_collection.insert_many(records)
    
    def clear_collection(self, collection_name):
        """Очистить коллекцию"""
        if collection_name == "raw":
            self.raw_collection.delete_many({})
        elif collection_name == "clean":
            self.clean_collection.delete_many({})
    
    def load_raw_data(self):
        """Загрузить все сырые данные"""
        cursor = self.raw_collection.find({})
        df = pd.DataFrame(list(cursor))
        if not df.empty and '_id' in df.columns:
            df = df.drop('_id', axis=1)
        return df
    
    def save_clean_data(self, df):
        """Сохранить очищенные данные"""
        self.clean_collection.delete_many({})  # Очистить перед сохранением
        records = df.to_dict(orient="records")
        for rec in records:
            rec["date"] = pd.to_datetime(rec["date"])
        
        if records:
            self.clean_collection.insert_many(records)
    
    def load_clean_data(self):
        """Загрузить очищенные данные"""
        cursor = self.clean_collection.find({})
        df = pd.DataFrame(list(cursor))
        if not df.empty:
            if '_id' in df.columns:
                df = df.drop('_id', axis=1)
            df['date'] = pd.to_datetime(df['date'])
        return df
    
    def get_cities_count(self):
        """Получить количество городов"""
        return len(self.raw_collection.distinct("city"))
    
    def get_date_range(self):
        """Получить диапазон дат"""
        pipeline = [
            {"$group": {
                "_id": None,
                "min_date": {"$min": "$time"},
                "max_date": {"$max": "$time"}
            }}
        ]
        result = list(self.raw_collection.aggregate(pipeline))
        if result:
            return result[0]["min_date"], result[0]["max_date"]
        return None, None
    
    def close(self):
        """Закрыть соединение"""
        self.client.close()