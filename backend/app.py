"""
CFO360 - Backend API  (production-ready)
-----------------------------------------
Thin read-only Flask API serving pre-computed analysis outputs from the
Python layer to the React frontend.  No business logic lives here.

Run dev:
    python app.py

Run production (Windows):
    waitress-serve --port=5000 app:app

Run production (Linux/macOS):
    gunicorn -w 4 -b 0.0.0.0:5000 app:app

Endpoints:
    GET /health
    GET /api/regions
    GET /api/kpi-summary
    GET /api/revenue-trend?region=<name optional>
    GET /api/revenue-by-region
    GET /api/revenue-by-product
    GET /api/budget-variance?region=<name optional>
    GET /api/cost-by-category?region=<name optional>
    GET /api/profitability
    GET /api/working-capital?region=<name optional>
    GET /api/forecast
    GET /api/insights
"""

import json
import os

import pandas as pd
from flask import Flask, jsonify, request

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # python-dotenv is optional; fall back to OS env vars

DATA_DIR = os.environ.get(
    "DATA_DIR",
    os.path.join(os.path.dirname(__file__), "..", "data"),
)
PORT = int(os.environ.get("PORT", 5000))
FLASK_ENV = os.environ.get("FLASK_ENV", "development")
ALLOWED_ORIGINS = os.environ.get(
    "ALLOWED_ORIGINS",
    "http://localhost:5173,http://localhost:4173,http://localhost:3000",
).split(",")

# ---------------------------------------------------------------------------
# App init
# ---------------------------------------------------------------------------
app = Flask(__name__)


# ---------------------------------------------------------------------------
# CORS  (fine-grained: only allow configured origins)
# ---------------------------------------------------------------------------
@app.after_request
def add_cors_headers(response):
    origin = request.headers.get("Origin", "")
    if origin in ALLOWED_ORIGINS or "*" in ALLOWED_ORIGINS:
        response.headers["Access-Control-Allow-Origin"] = origin or "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    return response


@app.route("/api/<path:p>", methods=["OPTIONS"])
def handle_options(p):
    return "", 204


# ---------------------------------------------------------------------------
# Data loading — once at startup
# ---------------------------------------------------------------------------
def _load_csv(name, parse_dates=None):
    path = os.path.join(DATA_DIR, name)
    if not os.path.exists(path):
        raise FileNotFoundError(f"Data file not found: {path}")
    return pd.read_csv(path, parse_dates=parse_dates)


def _load_json(name):
    path = os.path.join(DATA_DIR, name)
    if not os.path.exists(path):
        raise FileNotFoundError(f"Data file not found: {path}")
    with open(path, encoding="utf-8") as f:
        return json.load(f)


_data_error = None
try:
    fact          = _load_csv("fact_monthly.csv",       parse_dates=["month"])
    forecast_df   = _load_csv("forecast.csv",           parse_dates=["month"])
    wc            = _load_csv("working_capital_kpis.csv", parse_dates=["month"])
    kpi_summary_df = _load_csv("kpi_summary.csv")
    insights_data  = _load_json("insights.json")
except Exception as e:
    _data_error = str(e)
    fact = forecast_df = wc = kpi_summary_df = insights_data = None


# ---------------------------------------------------------------------------
# Error handlers
# ---------------------------------------------------------------------------
@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "endpoint not found"}), 404


@app.errorhandler(500)
def server_error(e):
    return jsonify({"error": "internal server error", "detail": str(e)}), 500


def _check_data():
    """Return a 503 JSON response if data failed to load, else None."""
    if _data_error:
        return jsonify({"error": "data not loaded", "detail": _data_error}), 503
    return None


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _region_filter(df, col="region"):
    region = request.args.get("region", "").strip()
    if region and region.lower() != "all":
        df = df[df[col].str.lower() == region.lower()]
    return df


def _cr(series):
    """Convert INR to Crore, rounded to 2dp."""
    return (series / 1e7).round(2)


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------
@app.get("/health")
def health():
    return jsonify({
        "status": "ok" if not _data_error else "degraded",
        "data_loaded": _data_error is None,
        "error": _data_error,
    })


@app.get("/api/regions")
def regions():
    err = _check_data()
    if err:
        return err
    return jsonify(sorted(fact["region"].unique().tolist()))


@app.get("/api/kpi-summary")
def kpi_summary():
    err = _check_data()
    if err:
        return err
    row = kpi_summary_df.iloc[0].to_dict()
    return jsonify(row)


@app.get("/api/revenue-trend")
def revenue_trend():
    err = _check_data()
    if err:
        return err
    df = _region_filter(fact.copy())
    monthly = (
        df.groupby("month")
        .agg(revenue=("revenue", "sum"), budget_revenue=("budget_revenue", "sum"))
        .reset_index()
        .sort_values("month")
    )
    monthly["month"] = monthly["month"].dt.strftime("%Y-%m")
    monthly["revenue_cr"] = _cr(monthly["revenue"])
    monthly["budget_revenue_cr"] = _cr(monthly["budget_revenue"])
    return jsonify(monthly[["month", "revenue_cr", "budget_revenue_cr"]].to_dict("records"))


@app.get("/api/revenue-by-region")
def revenue_by_region():
    err = _check_data()
    if err:
        return err
    latest = fact["month"].max()
    window = fact[fact["month"] >= latest - pd.DateOffset(months=2)]
    out = (
        window.groupby("region")
        .agg(revenue=("revenue", "sum"), budget_revenue=("budget_revenue", "sum"))
        .reset_index()
    )
    out["revenue_cr"] = _cr(out["revenue"])
    out["variance_pct"] = (
        (out["revenue"] - out["budget_revenue"]) / out["budget_revenue"] * 100
    ).round(2)
    return jsonify(out[["region", "revenue_cr", "variance_pct"]].to_dict("records"))


@app.get("/api/revenue-by-product")
def revenue_by_product():
    err = _check_data()
    if err:
        return err
    try:
        sales = _load_csv("sales_clean.csv", parse_dates=["date"])
    except FileNotFoundError as e:
        return jsonify({"error": str(e)}), 503
    latest = sales["date"].max()
    window = sales[sales["date"] >= latest - pd.DateOffset(months=2)]
    out = window.groupby("product")["revenue"].sum().reset_index()
    out["revenue_cr"] = _cr(out["revenue"])
    return jsonify(out[["product", "revenue_cr"]].to_dict("records"))


@app.get("/api/budget-variance")
def budget_variance():
    err = _check_data()
    if err:
        return err
    df = _region_filter(fact.copy())
    latest = df["month"].max()
    window = df[df["month"] >= latest - pd.DateOffset(months=2)]
    out = (
        window.groupby("region")
        .agg(revenue=("revenue", "sum"), budget_revenue=("budget_revenue", "sum"))
        .reset_index()
    )
    out["variance_pct"] = (
        (out["revenue"] - out["budget_revenue"]) / out["budget_revenue"] * 100
    ).round(2)
    out["revenue_cr"] = _cr(out["revenue"])
    out["budget_cr"] = _cr(out["budget_revenue"])
    return jsonify(
        out.sort_values("variance_pct")[
            ["region", "revenue_cr", "budget_cr", "variance_pct"]
        ].to_dict("records")
    )


@app.get("/api/cost-by-category")
def cost_by_category():
    err = _check_data()
    if err:
        return err
    try:
        expenses = _load_csv("expenses_clean.csv", parse_dates=["date"])
    except FileNotFoundError as e:
        return jsonify({"error": str(e)}), 503
    df = _region_filter(expenses.copy())
    latest = df["date"].max()
    window = df[df["date"] >= latest - pd.DateOffset(months=2)]
    out = window.groupby("expense_category")["amount"].sum().reset_index()
    out["amount_cr"] = _cr(out["amount"])
    total = out["amount_cr"].sum()
    out["pct_of_total"] = (out["amount_cr"] / total * 100).round(1)
    return jsonify(
        out.sort_values("amount_cr", ascending=False)[
            ["expense_category", "amount_cr", "pct_of_total"]
        ].to_dict("records")
    )


@app.get("/api/profitability")
def profitability():
    """Monthly EBITDA, gross profit and margin trend — trailing 12 months."""
    err = _check_data()
    if err:
        return err
    latest = fact["month"].max()
    window = fact[fact["month"] >= latest - pd.DateOffset(months=11)]
    monthly = (
        window.groupby("month")
        .agg(
            revenue=("revenue", "sum"),
            gross_profit=("gross_profit", "sum"),
            ebitda=("ebitda", "sum"),
        )
        .reset_index()
        .sort_values("month")
    )
    monthly["month"] = monthly["month"].dt.strftime("%Y-%m")
    monthly["revenue_cr"]      = _cr(monthly["revenue"])
    monthly["gross_profit_cr"] = _cr(monthly["gross_profit"])
    monthly["ebitda_cr"]       = _cr(monthly["ebitda"])
    monthly["gross_margin_pct"] = (
        monthly["gross_profit"] / monthly["revenue"] * 100
    ).round(2)
    monthly["ebitda_margin_pct"] = (
        monthly["ebitda"] / monthly["revenue"] * 100
    ).round(2)
    return jsonify(
        monthly[[
            "month", "revenue_cr", "gross_profit_cr", "ebitda_cr",
            "gross_margin_pct", "ebitda_margin_pct",
        ]].to_dict("records")
    )


@app.get("/api/working-capital")
def working_capital():
    err = _check_data()
    if err:
        return err
    df = _region_filter(wc.copy())
    out = (
        df.groupby("month")
        .agg(
            dso_days=("dso_days", "mean"),
            dpo_days=("dpo_days", "mean"),
            dio_days=("dio_days", "mean"),
            cash_conversion_cycle=("cash_conversion_cycle", "mean"),
        )
        .reset_index()
        .sort_values("month")
    )
    out["month"] = out["month"].dt.strftime("%Y-%m")
    out = out.round(1)
    return jsonify(out.to_dict("records"))


@app.get("/api/forecast")
def get_forecast():
    err = _check_data()
    if err:
        return err
    df = forecast_df.copy()
    df["month"] = df["month"].dt.strftime("%Y-%m")
    df["revenue_cr"] = _cr(df["revenue"])
    return jsonify(df[["month", "region", "revenue_cr", "type"]].to_dict("records"))


@app.get("/api/insights")
def get_insights():
    err = _check_data()
    if err:
        return err
    return jsonify(insights_data)


# ---------------------------------------------------------------------------
# Error Handlers
# ---------------------------------------------------------------------------
@app.errorhandler(404)
def handle_404(e):
    return jsonify({"error": "Route not found", "status": 404}), 404


@app.errorhandler(405)
def handle_405(e):
    return jsonify({"error": "Method not allowed", "status": 405}), 405


@app.errorhandler(500)
def handle_500(e):
    return jsonify({"error": "Internal server error", "status": 500}), 500


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    debug = FLASK_ENV != "production"
    print(f"[CFO360] Starting Flask on port {PORT} (debug={debug})")
    print(f"[CFO360] Data dir: {os.path.abspath(DATA_DIR)}")
    if _data_error:
        print(f"[CFO360] WARNING: data load error: {_data_error}")
    app.run(host="0.0.0.0", port=PORT, debug=debug)
