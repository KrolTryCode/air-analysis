import warnings
warnings.filterwarnings("ignore")

import pandas as pd
import matplotlib.pyplot as plt
from pmdarima import auto_arima
from statsmodels.tsa.statespace.sarimax import SARIMAX
from db_manager import DBManager
from config import OUTPUT


def load_series(db):
    """Загрузить временной ряд PM2.5"""
    df = db.load_clean_data()
    
    # Среднее по всем городам (daily)
    grp = df.groupby("date")["pm25"].mean().reset_index()
    grp = grp.sort_values("date")
    grp["date"] = pd.to_datetime(grp["date"])
    grp = grp.set_index("date").asfreq("D")
    
    # Интерполяция пропусков
    grp["pm25"] = grp["pm25"].interpolate(method="time").ffill().bfill()
    return grp["pm25"]


def plot_timeseries(series):
    """График временного ряда"""
    plt.figure(figsize=(12, 4))
    series.plot()
    plt.title("Avg PM2.5 (средний по городам) — 2023-2025")
    plt.ylabel("PM2.5 (µg/m³)")
    plt.tight_layout()
    plt.savefig(OUTPUT / "avg_pm25_timeseries.png")
    plt.close()


def fit_auto_arima(series):
    """Подбор параметров SARIMA"""
    print("\n=== Подбор параметров SARIMA ===")
    model = auto_arima(
        series,
        start_p=0, start_q=0,
        max_p=3, max_q=3,
        seasonal=True,
        m=30,  # месячная сезонность
        start_P=0, start_Q=0,
        max_P=2, max_Q=2,
        d=None, D=1,
        trace=True,
        error_action='ignore',
        suppress_warnings=True,
        stepwise=True,
        information_criterion='aic'
    )
    print(model.summary())
    return model


def fit_sarimax(series, order, seasonal_order):
    """Обучение модели SARIMAX"""
    print(f"\n=== Обучение SARIMAX ===")
    print(f"Order: {order}, Seasonal: {seasonal_order}")
    
    mod = SARIMAX(
        series,
        order=order,
        seasonal_order=seasonal_order,
        enforce_stationarity=False,
        enforce_invertibility=False
    )
    res = mod.fit(disp=False, maxiter=200)
    print(res.summary())
    return res


def diagnostics_plot(res):
    """График диагностики модели"""
    fig = res.plot_diagnostics(figsize=(12, 10))
    fig.savefig(OUTPUT / "sarima_diagnostics.png")
    plt.close()


def forecast_and_plot(res, series, steps=365):
    """Прогноз и визуализация"""
    forecast_res = res.get_forecast(steps=steps)
    mean = forecast_res.predicted_mean
    conf = forecast_res.conf_int(alpha=0.05)
    
    last_date = series.index.max()
    idx = pd.date_range(start=last_date + pd.Timedelta(days=1), periods=steps, freq="D")
    
    df_fore = pd.DataFrame({
        "date": idx,
        "pm25_forecast": mean.values,
        "lower": conf.iloc[:, 0].values,
        "upper": conf.iloc[:, 1].values
    })
    
    # График
    plt.figure(figsize=(12, 5))
    plt.plot(series.index, series.values, label="Наблюдаемые", alpha=0.7)
    plt.plot(idx, mean, label="Прогноз", color="tab:orange", linewidth=2)
    plt.fill_between(idx, df_fore["lower"], df_fore["upper"], 
                     color="orange", alpha=0.2, label="95% доверительный интервал")
    plt.title("PM2.5: фактические значения (2023-2025) и прогноз на 2026")
    plt.xlabel("Дата")
    plt.ylabel("PM2.5 (µg/m³)")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(OUTPUT / "pm25_forecast_2026.png", dpi=150)
    plt.close()
    
    return df_fore


def main():
    db = DBManager()
    
    # Загрузка данных
    series = load_series(db)
    print(f"Длина временного ряда: {len(series)}")
    
    # График исходного ряда
    plot_timeseries(series)
    
    # Подбор параметров
    auto = fit_auto_arima(series)
    order = auto.order
    seasonal_order = auto.seasonal_order
    
    print(f"\nВыбранные параметры: order={order}, seasonal={seasonal_order}")
    
    # Обучение модели
    res = fit_sarimax(series, order=order, seasonal_order=seasonal_order)
    
    # Диагностика
    diagnostics_plot(res)
    
    # Прогноз на 2026 год
    df_fore = forecast_and_plot(res, series, steps=365)
    
    print(f"\n✔ Прогноз создан")
    print(f"✔ Графики сохранены в {OUTPUT}")
    
    # Статистика прогноза
    print("\n=== Статистика прогноза на 2026 год ===")
    print(f"Средний прогноз: {df_fore['pm25_forecast'].mean():.2f} µg/m³")
    print(f"Зима 2026: {df_fore.iloc[:90]['pm25_forecast'].mean():.2f} µg/m³")
    print(f"Лето 2026: {df_fore.iloc[180:270]['pm25_forecast'].mean():.2f} µg/m³")
    
    db.close()


if __name__ == "__main__":
    main()