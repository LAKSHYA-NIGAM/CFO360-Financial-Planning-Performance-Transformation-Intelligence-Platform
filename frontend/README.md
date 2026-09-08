# CFO360 frontend

React + Vite + Recharts dashboard that consumes the Flask API in `../backend`.

## Run it

```bash
# 1. start the backend (from ../backend)
cd ../backend
pip install flask pandas
python app.py                 # http://localhost:5000

# 2. start the frontend (from this folder, in a second terminal)
cd ../frontend
npm install
npm run dev                   # http://localhost:5173
```

The Vite dev server proxies `/api/*` to `localhost:5000` (see `vite.config.js`),
so `src/api.js` just calls `fetch("/api/...")` with no hardcoded host.

## Structure

```
frontend/
├── index.html
├── vite.config.js
├── package.json
└── src/
    ├── main.jsx
    ├── App.jsx              # tabs: Executive Summary, Revenue, Costs, Working Capital
    ├── api.js                # fetch wrapper over the Flask endpoints
    ├── index.css
    └── components/
        ├── KpiCards.jsx
        ├── RevenueTrendChart.jsx
        ├── BreakdownBarChart.jsx
        ├── WorkingCapitalChart.jsx
        └── InsightsPanel.jsx
```

`InsightsPanel.jsx` renders `python/financial_analysis.py`'s output
(`data/insights.json`, served via `GET /api/insights`) directly in the
UI — the Metric → Variance → Root Cause → Business Impact →
Recommendation chain sits right next to the chart it explains, on the
Executive Summary tab.
