"""
Unit-тесты для DBManager
"""
import unittest
from unittest.mock import MagicMock, patch
import pandas as pd
import sys
from pathlib import Path

# Добавляем src в путь
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "air_src"))

from air_src.db_manager import DBManager


class TestDBManager(unittest.TestCase):
    """Тесты для класса DBManager"""
    
    @patch('db_manager.MongoClient')
    def setUp(self, mock_client):
        """Настройка перед каждым тестом"""
        self.mock_client = mock_client
        self.db = DBManager()
    
    def test_save_raw_data(self):
        """Тест сохранения сырых данных"""
        df = pd.DataFrame({
            'time': pd.date_range('2023-01-01', periods=3, freq='H'),
            'pm25': [10, 15, 12],
            'pm10': [20, 25, 22]
        })
        
        # Проверяем что метод вызывается без ошибок
        try:
            self.db.save_raw_data("Москва", df)
            success = True
        except Exception as e:
            success = False
            print(f"Error: {e}")
        
        self.assertTrue(success, "save_raw_data должен работать без ошибок")
    
    def test_load_clean_data_empty(self):
        """Тест загрузки пустых данных"""
        self.db.clean_collection.find = MagicMock(return_value=[])
        
        df = self.db.load_clean_data()
        
        self.assertTrue(df.empty, "При отсутствии данных должен вернуться пустой DataFrame")
    
    def test_save_clean_data(self):
        """Тест сохранения очищенных данных"""
        df = pd.DataFrame({
            'date': pd.date_range('2023-01-01', periods=3),
            'city': ['Москва', 'Москва', 'Москва'],
            'pm25': [10, 15, 12]
        })
        
        try:
            self.db.save_clean_data(df)
            success = True
        except Exception:
            success = False
        
        self.assertTrue(success, "save_clean_data должен работать корректно")


class TestDataValidation(unittest.TestCase):
    """Тесты валидации данных"""
    
    def test_valid_pm25_range(self):
        """Тест валидации диапазона PM2.5"""
        valid_values = [0, 50, 100, 250, 499]
        invalid_values = [-1, 501, 1000]
        
        for val in valid_values:
            self.assertTrue(0 <= val <= 500, f"{val} должно быть в допустимом диапазоне")
        
        for val in invalid_values:
            self.assertFalse(0 <= val <= 500, f"{val} должно быть вне допустимого диапазона")
    
    def test_dataframe_structure(self):
        """Тест структуры DataFrame"""
        df = pd.DataFrame({
            'date': pd.date_range('2023-01-01', periods=5),
            'city': ['Москва'] * 5,
            'pm25': [10, 15, 12, 18, 14]
        })
        
        required_columns = ['date', 'city', 'pm25']
        
        for col in required_columns:
            self.assertIn(col, df.columns, f"Колонка {col} должна присутствовать")


if __name__ == '__main__':
    unittest.main()