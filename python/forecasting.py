"""
CFO360 - Revenue Forecasting
------------------------------
Deliberately simple and explainable (a CFO needs to trust and defend a
forecast, not just receive a number): fits a linear trend + monthly
seasonality per region on log-revenue, then projects 3 months forward.

Run:
    python forecasting.py
Outputs:
    ../data/forecast.csv  - actual + forecasted revenue by region/month
"""

import numpy as np
import pandas as pd
import sys

# Ensure UTF-8 output on Windows cp1252 consoles
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

DATA = "../data"
FORECAST_HORIZON = 3


def fit_and_forecast(region_df):
    region_df = region_df.sort_values("month").reset_index(drop=True)
    region_df["t"] = np.arange(len(region_df))
    region_df["month_num"] = region_df["month"].dt.month
    region_df["log_rev"] = np.log(region_df["revenue"])

    # design matrix: trend + month dummies (seasonality)
    month_dummies = pd.get_dummies(region_df["month_num"], prefix="m", drop_first=True)
    X = pd.concat([region_df[["t"]], month_dummies], axis=1).astype(float)
    X.insert(0, "intercept", 1.0)
    y = region_df["log_rev"].values

    # OLS via normal equations
    beta, *_ = np.linalg.lstsq(X.values, y, rcond=None)

    # forecast next N months
    last_t = region_df["t"].max()
    last_month = region_df["month"].max()
    future_months = pd.date_range(last_month + pd.DateOffset(months=1), periods=FORECAST_HORIZON, freq="MS")
    future = pd.DataFrame({"t": np.arange(last_t + 1, last_t + 1 + FORECAST_HORIZON),
                            "month_num": future_months.month})
    future_dummies = pd.get_dummies(future["month_num"], prefix="m", drop_first=True)
    future_dummies = future_dummies.reindex(columns=month_dummies.columns, fill_value=0)
    Xf = pd.concat([future[["t"]], future_dummies], axis=1).astype(float)
    Xf.insert(0, "intercept", 1.0)

    log_forecast = Xf.values @ beta
    forecast_revenue = np.exp(log_forecast)

    result = pd.DataFrame({
        "month": future_months,
        "region": region_df["region"].iloc[0],
        "revenue": forecast_revenue,
        "type": "forecast",
    })
    actual = region_df[["month", "region", "revenue"]].copy()
    actual["type"] = "actual"
    return pd.concat([actual, result], ignore_index=True)


def main():
    fact = pd.read_csv(f"{DATA}/fact_monthly.csv", parse_dates=["month"])
    region_monthly = fact.groupby(["month", "region"]).revenue.sum().reset_index()

    all_forecasts = []
    for region, g in region_monthly.groupby("region"):
        all_forecasts.append(fit_and_forecast(g))

    out = pd.concat(all_forecasts, ignore_index=True).sort_values(["region", "month"])
    out.to_csv(f"{DATA}/forecast.csv", index=False)

    print("Forecast (next 3 months) by region, ₹ Cr:")
    fc = out[out.type == "forecast"].copy()
    fc["revenue_cr"] = (fc.revenue / 1e7).round(2)
    print(fc[["month", "region", "revenue_cr"]].to_string(index=False))


if __name__ == "__main__":
    main()
