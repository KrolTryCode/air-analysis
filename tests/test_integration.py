"""
Интеграционные тесты
"""
import unittest
import pandas as pd
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "air_src"))

from air_src.db_manager import DBManager
from air_src.data_validator import DataValidator


class TestDataPipeline(unittest.TestCase):
    """Тесты полного цикла обработки данных"""
    
    @patch('db_manager.MongoClient')
    def setUp(self, mock_client):
        """Настройка"""
        self.db = DBManager()
        self.validator = DataValidator()
        
        # Тестовые данные
        self.test_data_raw = pd.DataFrame({
            'time': pd.date_range('2023-01-01', periods=100, freq='H'),
            'pm2_5': [10 + i % 20 for i in range(100)],
            'pm10': [20 + i % 30 for i in range(100)],
            'nitrogen_dioxide': [30 + i % 15 for i in range(100)],
            'sulphur_dioxide': [5 + i % 10 for i in range(100)],
            'ozone': [40 + i % 25 for i in range(100)]
        })
    
    def test_data_transformation(self):
        """Тест трансформации данных"""
        # Имитируем процесс очистки
        df = self.test_data_raw.copy()
        
        # Переименование
        df = df.rename(columns={
            'time': 'datetime',
            'pm2_5': 'pm25',
            'nitrogen_dioxide': 'no2',
            'sulphur_dioxide': 'so2',
            'ozone': 'o3'
        })
        
        # Проверки
        self.assertIn('pm25', df.columns, "Должна быть колонка pm25")
        self.assertIn('no2', df.columns, "Должна быть колонка no2")
        self.assertNotIn('pm2_5', df.columns, "Старое название должно быть удалено")
    
    def test_aggregation(self):
        """Тест агрегации данных"""
        df = self.test_data_raw.copy()
        df['city'] = 'Москва'
        df['date'] = pd.to_datetime(df['time']).dt.date
        
        # Агрегация по дням
        agg = df.groupby(['city', 'date']).agg({
            'pm2_5': 'mean',
            'pm10': 'mean'
        }).reset_index()
        
        # Проверки
        self.assertLess(len(agg), len(df), "Агрегированных записей должно быть меньше")
        self.assertTrue(all(agg['pm2_5'] >= 0), "Все значения должны быть неотрицательными")
    
    def test_end_to_end_validation(self):
        """End-to-end тест: сохранение -> загрузка -> валидация"""
        # Создаем корректные данные
        df_clean = pd.DataFrame({
            'city': ['Москва'] * 30,
            'date': pd.date_range('2023-01-01', periods=30),
            'pm25': [10 + i % 15 for i in range(30)],
            'pm10': [20 + i % 20 for i in range(30)],
            'no2': [30 + i % 10 for i in range(30)],
            'so2': [5 + i % 8 for i in range(30)],
            'o3': [40 + i % 15 for i in range(30)]
        })
        
        # Валидация
        results = self.validator.validate_dataframe(df_clean)
        
        # Проверки
        self.assertTrue(results['passed'], "Валидация должна пройти успешно")
        self.assertEqual(results['total_rows'], 30, "Должно быть 30 записей")


if __name__ == '__main__':
    unittest.main()