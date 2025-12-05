import warnings
warnings.filterwarnings("ignore")

import pandas as pd
import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt
from pmdarima import auto_arima
from statsmodels.tsa.statespace.sarimax import SARIMAX
import statsmodels.api as sm

ROOT = Path(__file__).resolve().parents[1]
PROC = ROOT / "data" / "processed"
OUT = ROOT / "output"
OUT.mkdir(parents=True, exist_ok=True)

INPUT = PROC / "air_quality_clean.csv"

def load_series():
    df = pd.read_csv(INPUT, parse_dates=["date"])
    # среднее по всем городам (daily)
    grp = df.groupby("date")["pm25"].mean().reset_index()
    grp = grp.sort_values("date")
    grp = grp.set_index("date").asfreq("D")  # заполним отсутствующие даты как NaN
    # interpolate small gaps:
    grp["pm25"] = grp["pm25"].interpolate(method="time").ffill().bfill()
    return grp["pm25"]

def plot_timeseries(series):
    plt.figure(figsize=(12,4))
    series.plot()
    plt.title("Avg PM2.5 (средний по городам) — 2022-2024")
    plt.ylabel("PM2.5 (µg/m³)")
    plt.tight_layout()
    plt.savefig(OUT / "avg_pm25_timeseries.png")
    plt.close()

def fit_auto_arima(series):
    # Подбор параметров SARIMA
    model = auto_arima(series,
                       start_p=0, start_q=0,
                       max_p=3, max_q=3,
                       seasonal=True,
                       m=30,            # month seasonality
                       start_P=0, start_Q=0,
                       max_P=2, max_Q=2,
                       d=None, D=1,
                       trace=True,
                       error_action='ignore',
                       suppress_warnings=True,
                       stepwise=True,
                       information_criterion='aic')
    print(model.summary())
    return model

def fit_sarimax(series, order, seasonal_order):
    print("Fitting SARIMAX with order =", order, " seasonal_order=", seasonal_order)
    mod = SARIMAX(series, order=order, seasonal_order=seasonal_order,
                  enforce_stationarity=False, enforce_invertibility=False)
    res = mod.fit(disp=False, maxiter=200)
    print(res.summary())
    return res

def diagnostics_plot(res):
    fig = res.plot_diagnostics(figsize=(12,10))
    fig.savefig(OUT / "sarima_diagnostics.png")
    plt.close()

def forecast_and_plot(res, series, steps=365):
    forecast_res = res.get_forecast(steps=steps)
    mean = forecast_res.predicted_mean
    conf = forecast_res.conf_int(alpha=0.05)

    last_date = series.index.max()
    idx = pd.date_range(start=last_date + pd.Timedelta(days=1), periods=steps, freq="D")
    df_fore = pd.DataFrame({
        "date": idx,
        "pm25_forecast": mean.values,
        "lower": conf.iloc[:,0].values,
        "upper": conf.iloc[:,1].values
    })
    df_fore.to_csv(OUT / "pm25_forecast_2025.csv", index=False)

    plt.figure(figsize=(12,5))
    plt.plot(series.index, series.values, label="observed")
    plt.plot(idx, mean, label="forecast", color="tab:orange")
    plt.fill_between(idx, df_fore["lower"], df_fore["upper"], color="orange", alpha=0.2)
    plt.title("PM2.5: фактические значения (2023-2025) и прогноз на 2026")
    plt.xlabel("date")
    plt.ylabel("PM2.5")
    plt.legend()
    plt.tight_layout()
    plt.savefig(OUT / "pm25_forecast_2026.png")
    plt.close()
    return df_fore

def main():
    series = load_series()
    print("Series length:", len(series))
    plot_timeseries(series)

    auto = fit_auto_arima(series)

    order = auto.order
    seasonal_order = auto.seasonal_order  # (P,D,Q,m)
    print("Selected by auto_arima:", order, seasonal_order)


    res = fit_sarimax(series, order=order, seasonal_order=seasonal_order)
    diagnostics_plot(res)

    # Forecast next 365 days
    df_fore = forecast_and_plot(res, series, steps=365)
    print("Forecast saved to:", OUT / "pm25_forecast_2025.csv")
    print(df_fore.head(10))

if __name__ == "__main__":
    main()
