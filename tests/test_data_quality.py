"""
Тесты качества данных
"""
import unittest
import pandas as pd
import numpy as np
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "air_src"))

from air_src.data_validator import DataValidator


class TestDataValidator(unittest.TestCase):
    """Тесты для DataValidator"""
    
    def setUp(self):
        """Подготовка перед каждым тестом"""
        self.validator = DataValidator()
    
    def test_valid_data(self):
        """Тест с корректными данными"""
        df = pd.DataFrame({
            'city': ['Москва'] * 10,
            'date': pd.date_range('2023-01-01', periods=10),
            'pm25': [10, 15, 12, 18, 14, 16, 11, 13, 17, 15],
            'pm10': [20, 25, 22, 28, 24, 26, 21, 23, 27, 25],
            'no2': [30, 35, 32, 38, 34, 36, 31, 33, 37, 35],
            'so2': [5, 7, 6, 8, 7, 6, 5, 7, 8, 6],
            'o3': [40, 45, 42, 48, 44, 46, 41, 43, 47, 45]
        })
        
        results = self.validator.validate_dataframe(df)
        
        self.assertTrue(results['passed'], "Валидация корректных данных должна пройти")
        self.assertEqual(len(results['errors']), 0, "Не должно быть ошибок")
    
    def test_missing_columns(self):
        """Тест с отсутствующими колонками"""
        df = pd.DataFrame({
            'city': ['Москва'] * 10,
            'pm25': [10, 15, 12, 18, 14, 16, 11, 13, 17, 15]
        })
        
        results = self.validator.validate_dataframe(df)
        
        self.assertFalse(results['passed'], "Валидация должна не пройти")
        self.assertGreater(len(results['errors']), 0, "Должны быть ошибки")
    
    def test_out_of_range_values(self):
        """Тест со значениями вне диапазона"""
        df = pd.DataFrame({
            'city': ['Москва'] * 10,
            'date': pd.date_range('2023-01-01', periods=10),
            'pm25': [10, 15, 12, 600, 14, 16, 11, 13, 17, 15],  # 600 вне диапазона
            'pm10': [20, 25, 22, 28, 24, 26, 21, 23, 27, 25],
            'no2': [30, 35, 32, 38, 34, 36, 31, 33, 37, 35],
            'so2': [5, 7, 6, 8, 7, 6, 5, 7, 8, 6],
            'o3': [40, 45, 42, 48, 44, 46, 41, 43, 47, 45]
        })
        
        results = self.validator.validate_dataframe(df)
        
        # Должно быть предупреждение (10% выбросов)
        self.assertTrue(len(results['warnings']) > 0 or len(results['errors']) > 0,
                       "Должны быть предупреждения или ошибки для значений вне диапазона")
    
    def test_missing_values(self):
        """Тест с пропущенными значениями"""
        df = pd.DataFrame({
            'city': ['Москва'] * 10,
            'date': pd.date_range('2023-01-01', periods=10),
            'pm25': [10, np.nan, 12, np.nan, 14, np.nan, 11, 13, 17, 15],  # 30% пропусков
            'pm10': [20, 25, 22, 28, 24, 26, 21, 23, 27, 25],
            'no2': [30, 35, 32, 38, 34, 36, 31, 33, 37, 35],
            'so2': [5, 7, 6, 8, 7, 6, 5, 7, 8, 6],
            'o3': [40, 45, 42, 48, 44, 46, 41, 43, 47, 45]
        })
        
        results = self.validator.validate_dataframe(df)
        
        self.assertFalse(results['passed'], "Валидация с большим количеством пропусков должна не пройти")
    
    def test_report_generation(self):
        """Тест генерации отчета"""
        df = pd.DataFrame({
            'city': ['Москва'] * 10,
            'date': pd.date_range('2023-01-01', periods=10),
            'pm25': [10, 15, 12, 18, 14, 16, 11, 13, 17, 15],
            'pm10': [20, 25, 22, 28, 24, 26, 21, 23, 27, 25],
            'no2': [30, 35, 32, 38, 34, 36, 31, 33, 37, 35],
            'so2': [5, 7, 6, 8, 7, 6, 5, 7, 8, 6],
            'o3': [40, 45, 42, 48, 44, 46, 41, 43, 47, 45]
        })
        
        self.validator.validate_dataframe(df)
        report = self.validator.generate_report()
        
        self.assertIsInstance(report, str, "Отчет должен быть строкой")
        self.assertIn("ОТЧЕТ О КАЧЕСТВЕ ДАННЫХ", report, "Отчет должен содержать заголовок")
        self.assertGreater(len(report), 50, "Отчет должен быть содержательным")


if __name__ == '__main__':
    unittest.main()