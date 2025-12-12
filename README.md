# Инструкция по запуску

## Получение и подготовка проекта
Склонируйте репозиторий и распакуйте дистрибутив:

```bash
git clone [<url>](https://github.com/KrolTryCode/air-analysis.git)
cd air-analysis
```
При необходимости измените параметры в config.py

## Запуск аналитических скриптов
Все команды выполняются внутри контейнера приложения, после fetch_data последовательность не важна, результаты появятся в корне проекта в папке output:
```
docker compose run app air_src/fetch_data.py
docker compose run app air_src/analysis_correlations.py
docker compose run app air_src/analysis_city_rankings.py
docker compose run app air_src/analysis_overview.py
docker compose run app air_src/analysis_seasonality.py
docker compose run app air_src/sarima_forecast.py
```
## Тестирование
```
docker compose run app tests/test_data_quality.py
docker compose run app tests/test_db_manager.py
docker compose run app tests/test_integration.py
```
