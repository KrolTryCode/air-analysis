"""
Модуль для валидации качества данных
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple


class DataValidator:
    """Валидатор качества данных о воздухе"""
    
    def __init__(self):
        # Допустимые диапазоны для каждого параметра (мкг/м³)
        self.valid_ranges = {
            'pm25': (0, 500),
            'pm10': (0, 1000),
            'no2': (0, 400),
            'so2': (0, 1000),
            'o3': (0, 500),
            'co': (0, 50000),
            'nh3': (0, 500),
            'dust': (0, 2000),
            'uv': (0, 15)
        }
        
        self.required_columns = ['city', 'date', 'pm25', 'pm10', 'no2', 'so2', 'o3']
        self.results = {}
    
    def validate_dataframe(self, df: pd.DataFrame) -> Dict:
        """Полная валидация датафрейма"""
        self.results = {
            'total_rows': len(df),
            'passed': True,
            'errors': [],
            'warnings': [],
            'statistics': {}
        }
        
        # Проверка структуры
        self._check_structure(df)
        
        # Проверка диапазонов значений
        self._check_value_ranges(df)
        
        # Проверка пропусков
        self._check_missing_values(df)
        
        # Проверка дубликатов
        self._check_duplicates(df)
        
        # Проверка временных промежутков
        self._check_date_continuity(df)
        
        # Статистические аномалии
        self._check_statistical_anomalies(df)
        
        return self.results
    
    def _check_structure(self, df: pd.DataFrame):
        """Проверка структуры данных"""
        missing_cols = [col for col in self.required_columns if col not in df.columns]
        
        if missing_cols:
            self.results['passed'] = False
            self.results['errors'].append(
                f"Отсутствуют обязательные колонки: {missing_cols}"
            )
        
        if df.empty:
            self.results['passed'] = False
            self.results['errors'].append("Датафрейм пустой")
    
    def _check_value_ranges(self, df: pd.DataFrame):
        """Проверка диапазонов значений"""
        for param, (min_val, max_val) in self.valid_ranges.items():
            if param not in df.columns:
                continue
            
            out_of_range = df[
                (df[param] < min_val) | (df[param] > max_val)
            ][param].dropna()
            
            if len(out_of_range) > 0:
                pct = (len(out_of_range) / len(df)) * 100
                
                if pct > 5:  # Более 5% - ошибка
                    self.results['passed'] = False
                    self.results['errors'].append(
                        f"{param}: {len(out_of_range)} значений ({pct:.2f}%) "
                        f"вне диапазона [{min_val}, {max_val}]"
                    )
                else:  # Менее 5% - предупреждение
                    self.results['warnings'].append(
                        f"{param}: {len(out_of_range)} значений ({pct:.2f}%) "
                        f"вне диапазона [{min_val}, {max_val}]"
                    )
    
    def _check_missing_values(self, df: pd.DataFrame):
        """Проверка пропущенных значений"""
        for col in self.required_columns:
            if col not in df.columns:
                continue
            
            missing_count = df[col].isna().sum()
            missing_pct = (missing_count / len(df)) * 100
            
            if missing_pct > 20:  # Более 20% пропусков - ошибка
                self.results['passed'] = False
                self.results['errors'].append(
                    f"{col}: {missing_count} пропусков ({missing_pct:.2f}%)"
                )
            elif missing_pct > 5:  # 5-20% - предупреждение
                self.results['warnings'].append(
                    f"{col}: {missing_count} пропусков ({missing_pct:.2f}%)"
                )
        
        self.results['statistics']['missing_values'] = df.isna().sum().to_dict()
    
    def _check_duplicates(self, df: pd.DataFrame):
        """Проверка дубликатов"""
        if 'city' in df.columns and 'date' in df.columns:
            duplicates = df.duplicated(subset=['city', 'date'], keep=False).sum()
            
            if duplicates > 0:
                pct = (duplicates / len(df)) * 100
                self.results['warnings'].append(
                    f"Найдено {duplicates} дубликатов ({pct:.2f}%)"
                )
                self.results['statistics']['duplicates'] = duplicates
    
    def _check_date_continuity(self, df: pd.DataFrame):
        """Проверка непрерывности временного ряда"""
        if 'date' not in df.columns or 'city' not in df.columns:
            return
        
        df_sorted = df.copy()
        df_sorted['date'] = pd.to_datetime(df_sorted['date'])
        
        gaps_by_city = {}
        
        for city in df_sorted['city'].unique():
            city_data = df_sorted[df_sorted['city'] == city].sort_values('date')
            
            if len(city_data) < 2:
                continue
            
            date_diff = city_data['date'].diff()
            large_gaps = date_diff[date_diff > pd.Timedelta(days=7)]
            
            if len(large_gaps) > 0:
                gaps_by_city[city] = len(large_gaps)
        
        if gaps_by_city:
            self.results['warnings'].append(
                f"Обнаружены временные промежутки >7 дней: {gaps_by_city}"
            )
            self.results['statistics']['temporal_gaps'] = gaps_by_city
    
    def _check_statistical_anomalies(self, df: pd.DataFrame):
        """Проверка статистических аномалий"""
        numeric_cols = ['pm25', 'pm10', 'no2', 'so2', 'o3']
        anomalies = {}
        
        for col in numeric_cols:
            if col not in df.columns:
                continue
            
            data = df[col].dropna()
            
            if len(data) < 10:
                continue
            
            # Метод IQR для поиска выбросов
            Q1 = data.quantile(0.25)
            Q3 = data.quantile(0.75)
            IQR = Q3 - Q1
            
            lower_bound = Q1 - 3 * IQR
            upper_bound = Q3 + 3 * IQR
            
            outliers = data[(data < lower_bound) | (data > upper_bound)]
            
            if len(outliers) > 0:
                outlier_pct = (len(outliers) / len(data)) * 100
                anomalies[col] = {
                    'count': len(outliers),
                    'percentage': outlier_pct,
                    'bounds': (lower_bound, upper_bound)
                }
                
                if outlier_pct > 10:
                    self.results['warnings'].append(
                        f"{col}: {len(outliers)} статистических выбросов ({outlier_pct:.2f}%)"
                    )
        
        if anomalies:
            self.results['statistics']['outliers'] = anomalies
    
    def generate_report(self) -> str:
        """Генерация текстового отчета"""
        report = []
        report.append("=" * 60)
        report.append("ОТЧЕТ О КАЧЕСТВЕ ДАННЫХ")
        report.append("=" * 60)
        
        report.append(f"\nОбщая информация:")
        report.append(f"  Всего записей: {self.results['total_rows']}")
        report.append(f"  Статус: {'✓ PASSED' if self.results['passed'] else '✗ FAILED'}")
        
        if self.results['errors']:
            report.append(f"\n❌ Ошибки ({len(self.results['errors'])}):")
            for error in self.results['errors']:
                report.append(f"  • {error}")
        
        if self.results['warnings']:
            report.append(f"\n⚠️  Предупреждения ({len(self.results['warnings'])}):")
            for warning in self.results['warnings']:
                report.append(f"  • {warning}")
        
        if not self.results['errors'] and not self.results['warnings']:
            report.append("\n✓ Проблем не обнаружено")
        
        report.append("\n" + "=" * 60)
        
        return "\n".join(report)


def validate_data_pipeline(db_manager) -> bool:
    """
    Валидация данных в конвейере обработки
    Возвращает True если валидация прошла успешно
    """
    validator = DataValidator()
    
    # Проверка очищенных данных
    df_clean = db_manager.load_clean_data()
    
    if df_clean.empty:
        print("⚠️  Нет данных для валидации")
        return False
    
    results = validator.validate_dataframe(df_clean)
    
    print(validator.generate_report())
    
    return results['passed']