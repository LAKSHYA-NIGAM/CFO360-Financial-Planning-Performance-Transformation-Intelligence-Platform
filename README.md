# CFO360 — Financial Planning, Performance & Transformation Intelligence Platform

A simulated Deloitte-style engagement for a fictional technology & business
services company, **NexaTech Industries**. The brief:

> "NexaTech's revenue is growing, but management believes profitability and
> cash efficiency are deteriorating. Analyze the company's financial
> performance and identify opportunities for improvement."

This repo answers that question end-to-end: synthetic data generation → data
cleaning → SQL/Python KPI engine → automated root-cause insights →
recommendations → (next phases: Power BI dashboard, React app).

```
CFO360
  │
  ├── Excel / CSV data
  ├── SQL (PostgreSQL schema + KPI + root-cause queries)
  ├── Python (cleaning, KPI engine, forecasting)
  │
  └── → Power BI dashboard → Business Insights → Recommendations → React App
```

## Why this project exists

Most portfolio "dashboards" stop at `Revenue = ₹92 Cr`. A CFO doesn't want a
number — they want the causal chain:

```
Metric → Variance → Root Cause → Business Impact → Recommendation
```

Everything in this repo is built around producing that chain automatically,
not just visualizing data.

## The company: NexaTech Industries (fictional)

- Industry: Technology & Business Services
- 4 regions (North, South, East, West)
- 5 business units (Consulting Services, Cloud Infrastructure, Managed IT
  Support, Software Products, Data & Analytics)
- 4 product/service categories (Product A–D)
- Monthly data, Jan 2024 – Aug 2026

The data is **synthetic but not random** — it has a deliberate, discoverable
story baked in so the analysis layer has something real to find:

1. **Revenue miss:** From mid-2025, North region has been increasing
   discounts on Product B (to defend volume against a competitor), which
   quietly erodes revenue and shows up as a growing budget miss.
2. **Working capital drag:** North and East extended payment terms to a few
   large enterprise clients from mid-2025, so DSO — and the cash conversion
   cycle — has been creeping up even as the top line grows.

The whole point is to practice finding these stories with code, not to
hand-wave over pre-labeled anomalies.

## Data model

| Table | Grain | Key columns |
|---|---|---|
| `sales` | 1 row per transaction | date, region, business_unit, product, customer_id, revenue, units_sold, discount |
| `expenses` | 1 row per region/BU/category/month | date, region, business_unit, expense_category, amount |
| `budget` | 1 row per region/BU/month | month, region, business_unit, budget_revenue, budget_expense |
| `working_capital` | 1 row per region/month | date, region, accounts_receivable, accounts_payable, inventory |
| `customers` | 1 row per customer | customer_id, customer_name, industry, region |

## KPIs (defined up front, not invented after the fact)

**Revenue** — Total Revenue · Revenue Growth % · Revenue by Region · Revenue by Product
**Profitability** — Gross Profit · Gross Margin % · EBITDA · EBITDA Margin %
**Budget** — Actual vs Budget Revenue · Revenue Variance · Revenue Variance %
**Cost** — Total Expenses · Expense Growth · Cost Variance · Cost by Category
**Working Capital** — DSO · DPO · Cash Conversion Cycle

## How to run it

```bash
cd python
pip install pandas numpy

python generate_data.py       # builds data/sales.csv, expenses.csv, budget.csv,
                               # working_capital.csv, customers.csv
python data_cleaning.py       # data-quality checks -> *_clean.csv + report
python financial_analysis.py  # KPI engine + automated insight generation
                               # -> fact_monthly.csv, kpi_summary.csv,
                               #    insights.json, executive_narrative.md
python forecasting.py         # 3-month revenue forecast by region -> forecast.csv
```

For the SQL side (optional, same logic reproduced in Postgres):

```bash
createdb cfo360
psql -d cfo360 -f sql/schema.sql
psql -d cfo360 -c "\copy sales FROM 'data/sales_clean.csv' CSV HEADER"
# ...repeat \copy for the other 4 tables
psql -d cfo360 -f sql/kpi_queries.sql
psql -d cfo360 -f sql/analysis.sql
```

To regenerate the one-page executive summary PDF:

```bash
cd consulting
pip install reportlab pdf2image
python make_executive_summary.py
```

## Sample output (auto-generated, not hand-written)

> **Total Revenue vs Budget** — Company revenue is 7.3% below budget over the
> trailing 3 months.
> - Region driver: North region is the largest negative contributor, running
>   14.5% below its budget.
> - Product driver: within North, Product B revenue is down 8.3% versus the
>   prior 3-month period.
> - Root cause: average discount on Product B in North has increased by 2.0
>   percentage points over the same window.
>
> **Business impact:** ~₹5.6 Cr in foregone revenue over 3 months for
> Product B in North alone — the single largest driver of the company-wide
> budget miss.
>
> **Recommendation:** Freeze further discount escalation on Product B in
> North; run a win/loss review on recent deals; reallocate sales incentives
> toward higher-margin, on-plan products while a pricing review is completed.

Full output: [`consulting/executive_summary.pdf`](consulting/executive_summary.pdf),
[`data/executive_narrative.md`](data/executive_narrative.md), [`data/insights.json`](data/insights.json).

## Project status / roadmap

| Layer | Status |
|---|---|
| Data model + synthetic data generator | ✅ Done |
| Data cleaning / validation | ✅ Done |
| SQL schema + KPI + root-cause queries | ✅ Done |
| Python KPI engine + automated insights | ✅ Done |
| Forecasting (trend + seasonality) | ✅ Done |
| Executive summary (PDF) | ✅ Done |
| Power BI dashboard | ✅ Spec + DAX complete (see `powerbi/`) — build the `.pbix` in Desktop following the spec |
| React dashboard (frontend + backend API) | ✅ Done — Flask API (`backend/`) tested end-to-end, React/Vite UI (`frontend/`) |

## Repository structure

```
CFO360/
├── data/                    # generated CSVs + KPI/insight outputs
├── python/
│   ├── generate_data.py
│   ├── data_cleaning.py
│   ├── financial_analysis.py
│   └── forecasting.py
├── sql/
│   ├── schema.sql
│   ├── kpi_queries.sql
│   └── analysis.sql
├── consulting/
│   ├── make_executive_summary.py
│   └── executive_summary.pdf
├── powerbi/
│   ├── CFO360_PowerBI_Spec.md
│   └── dax_measures.dax
├── backend/
│   └── app.py                # Flask API — tested end-to-end against real data
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── api.js
│   │   └── components/       # KpiCards, RevenueTrendChart, BreakdownBarChart, WorkingCapitalChart, InsightsPanel
│   └── package.json
└── README.md
```

## Running the full stack locally

```bash
# backend
cd backend && pip install flask pandas && python app.py      # :5000

# frontend (second terminal)
cd frontend && npm install && npm run dev                     # :5173
```

## What's been tested, and what hasn't

- **Backend**: all 10 endpoints (`/api/regions`, `/api/kpi-summary`,
  `/api/revenue-trend` incl. `?region=` filtering, `/api/revenue-by-region`,
  `/api/revenue-by-product`, `/api/budget-variance`, `/api/cost-by-category`,
  `/api/working-capital`, `/api/forecast`, `/api/insights`) were started and
  curled end-to-end against the real generated data — all return 200 with
  correct numbers.
- **Frontend**: written to consume those exact endpoints via `src/api.js`,
  but not run through `npm install`/`npm run dev` in this environment (no
  network access to the npm registry here). A self-contained live demo with
  the same UI and the real computed numbers hard-coded in
  (`CFO360_live_demo.jsx`, shared alongside this repo) stands in for that —
  open it to see the actual dashboard rendered. Before treating the
  `frontend/` folder as "done" for an interview, run `npm install && npm run
  dev` yourself once to confirm it builds clean.



- Defining KPIs from a business question *before* writing code, not
  calculating metrics for their own sake.
- Building an analytical chain — Metric → Variance → Root Cause → Business
  Impact → Recommendation — programmatically in both Python and SQL.
- End-to-end data pipeline literacy: generation → cleaning/validation →
  modeling → analysis → forecasting → reporting.
- Comfort across the stack a Decision Sciences / analytics consulting role
  actually needs: Python (pandas/numpy), SQL (PostgreSQL, window functions,
  CTEs), and reporting output (PDF, and Power BI/React as the next layer).

*NexaTech Industries is a fictional company created for this project so the
full repository, including data, can be published on GitHub.*
