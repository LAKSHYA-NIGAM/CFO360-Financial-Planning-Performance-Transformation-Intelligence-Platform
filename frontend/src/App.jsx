import React, { useEffect, useState } from "react";
import { api } from "./api";
import KpiCards from "./components/KpiCards";
import RevenueTrendChart from "./components/RevenueTrendChart";
import BreakdownBarChart from "./components/BreakdownBarChart";
import WorkingCapitalChart from "./components/WorkingCapitalChart";
import ProfitabilityChart from "./components/ProfitabilityChart";
import ForecastChart from "./components/ForecastChart";
import InsightsPanel from "./components/InsightsPanel";
import { ChartSkeleton } from "./components/Skeleton";

const TABS = [
  { id: "exec",    label: "Executive Summary" },
  { id: "revenue", label: "Revenue" },
  { id: "cost",    label: "Costs" },
  { id: "profit",  label: "Profitability" },
  { id: "wc",      label: "Working Capital" },
  { id: "forecast",label: "Forecast" },
];

// ─── small card wrapper ────────────────────────────────────────────────────
function Panel({ title, children, style }) {
  return (
    <div className="card section" style={style}>
      {title && <div className="card-title">{title}</div>}
      {children}
    </div>
  );
}

// ─── budget variance badge ─────────────────────────────────────────────────
function VBadge({ pct }) {
  const neg = pct < 0;
  return (
    <span className={`variance-badge ${neg ? "negative" : "positive"}`}>
      {neg ? "▼" : "▲"} {Math.abs(pct).toFixed(1)}%
    </span>
  );
}

// ─── main app ──────────────────────────────────────────────────────────────
export default function App() {
  const [tab, setTab] = useState("exec");
  const [region, setRegion] = useState("All");
  const [regions, setRegions] = useState([]);

  const [summary,          setSummary]          = useState(null);
  const [revenueTrend,     setRevenueTrend]     = useState([]);
  const [revenueByRegion,  setRevenueByRegion]  = useState([]);
  const [revenueByProduct, setRevenueByProduct] = useState([]);
  const [budgetVariance,   setBudgetVariance]   = useState([]);
  const [costByCategory,   setCostByCategory]   = useState([]);
  const [profitability,    setProfitability]    = useState([]);
  const [workingCapital,   setWorkingCapital]   = useState([]);
  const [forecast,         setForecast]         = useState([]);
  const [insights,         setInsights]         = useState([]);

  const [loading, setLoading] = useState(true);
  const [error,   setError]   = useState(null);

  // ── static data (no region filter) ──────────────────────────────────────
  useEffect(() => {
    const all = [
      api.regions()        .then(setRegions),
      api.kpiSummary()     .then(setSummary),
      api.revenueByRegion().then(setRevenueByRegion),
      api.revenueByProduct().then(setRevenueByProduct),
      api.budgetVariance() .then(setBudgetVariance),
      api.profitability()  .then(setProfitability),
      api.forecast()       .then(setForecast),
      api.insights()       .then((d) => setInsights(d.insights || [])),
    ];
    Promise.allSettled(all)
      .then((results) => {
        const failed = results.find((r) => r.status === "rejected");
        if (failed) setError(failed.reason.message);
      })
      .finally(() => setLoading(false));
  }, []);

  // ── region-filtered data ─────────────────────────────────────────────────
  useEffect(() => {
    const r = region === "All" ? undefined : region;
    api.revenueTrend(r)   .then(setRevenueTrend)   .catch((e) => setError(e.message));
    api.costByCategory(r) .then(setCostByCategory) .catch((e) => setError(e.message));
    api.workingCapital(r) .then(setWorkingCapital) .catch((e) => setError(e.message));
  }, [region]);

  const regionLabel = region !== "All" ? ` — ${region}` : "";

  return (
    <div className="app">
      {/* ── Header ── */}
      <header className="header">
        <div className="header-brand">
          <div className="header-logo">C3</div>
          <div>
            <div className="header-title">CFO360</div>
            <div className="header-subtitle">NexaTech Industries · Financial Intelligence Platform</div>
          </div>
        </div>
        <select
          className="region-select"
          value={region}
          onChange={(e) => setRegion(e.target.value)}
          aria-label="Filter by region"
        >
          <option value="All">All regions</option>
          {regions.map((r) => (
            <option key={r} value={r}>{r}</option>
          ))}
        </select>
      </header>

      {/* ── Error banner ── */}
      {error && (
        <div className="error-banner">
          ⚠ {error} — make sure the Flask backend is running on port 5000.
        </div>
      )}

      {/* ── Nav tabs ── */}
      <nav className="nav" role="tablist" aria-label="Dashboard sections">
        {TABS.map((t) => (
          <button
            key={t.id}
            role="tab"
            aria-selected={tab === t.id}
            className={`nav-btn${tab === t.id ? " active" : ""}`}
            onClick={() => setTab(t.id)}
          >
            {t.label}
          </button>
        ))}
      </nav>

      {/* ════════════════════════════════════════════════════════
          TAB: Executive Summary
      ════════════════════════════════════════════════════════ */}
      {tab === "exec" && (
        <>
          <KpiCards summary={summary} />

          <Panel title={`Revenue vs Budget${regionLabel}`}>
            {revenueTrend.length ? <RevenueTrendChart data={revenueTrend} /> : <ChartSkeleton />}
          </Panel>

          <div style={{ fontSize: 13, fontWeight: 700, color: "var(--text)", marginBottom: 14, marginTop: 4 }}>
            ⚡ Why we're off plan
          </div>
          <InsightsPanel insights={insights} />
        </>
      )}

      {/* ════════════════════════════════════════════════════════
          TAB: Revenue
      ════════════════════════════════════════════════════════ */}
      {tab === "revenue" && (
        <>
          <div className="grid-2 section">
            <Panel title="Revenue by Region (trailing 3M)">
              <BreakdownBarChart
                data={revenueByRegion}
                xKey="region"
                yKey="revenue_cr"
                yLabel="₹ Cr"
                colorBy={(row) => row.variance_pct < -10 ? "var(--red)" : row.variance_pct < -3 ? "var(--amber)" : "var(--accent)"}
                formatTooltip={(v) => `₹${v} Cr`}
              />
            </Panel>

            <Panel title="Revenue by Product (trailing 3M)">
              <BreakdownBarChart
                data={revenueByProduct}
                xKey="product"
                yKey="revenue_cr"
                yLabel="₹ Cr"
                formatTooltip={(v) => `₹${v} Cr`}
              />
            </Panel>

            <Panel title={`Revenue vs Budget Trend${regionLabel}`} style={{ gridColumn: "1 / -1" }}>
              {revenueTrend.length ? <RevenueTrendChart data={revenueTrend} /> : <ChartSkeleton />}
            </Panel>
          </div>

          {/* Budget variance table */}
          <Panel title="Budget Variance by Region (trailing 3M)">
            <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 13 }}>
              <thead>
                <tr style={{ borderBottom: "1px solid var(--border)" }}>
                  {["Region", "Actual (₹ Cr)", "Budget (₹ Cr)", "Variance"].map((h) => (
                    <th key={h} style={{ padding: "8px 12px", textAlign: "left", color: "var(--text-muted)", fontWeight: 600, fontSize: 11 }}>{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {budgetVariance.map((row) => (
                  <tr key={row.region} style={{ borderBottom: "1px solid var(--border)" }}>
                    <td style={{ padding: "10px 12px", fontWeight: 600 }}>{row.region}</td>
                    <td style={{ padding: "10px 12px" }}>₹{row.revenue_cr} Cr</td>
                    <td style={{ padding: "10px 12px", color: "var(--text-muted)" }}>₹{row.budget_cr} Cr</td>
                    <td style={{ padding: "10px 12px" }}><VBadge pct={row.variance_pct} /></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </Panel>
        </>
      )}

      {/* ════════════════════════════════════════════════════════
          TAB: Costs
      ════════════════════════════════════════════════════════ */}
      {tab === "cost" && (
        <>
          <Panel title={`Cost by Category (trailing 3M)${regionLabel}`}>
            <BreakdownBarChart
              data={costByCategory}
              xKey="expense_category"
              yKey="amount_cr"
              yLabel="₹ Cr"
              formatTooltip={(v) => `₹${v} Cr`}
            />
          </Panel>

          <Panel title="Cost Breakdown (%)">
            <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 13 }}>
              <thead>
                <tr style={{ borderBottom: "1px solid var(--border)" }}>
                  {["Category", "₹ Cr", "% of Total"].map((h) => (
                    <th key={h} style={{ padding: "8px 12px", textAlign: "left", color: "var(--text-muted)", fontWeight: 600, fontSize: 11 }}>{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {costByCategory.map((row) => (
                  <tr key={row.expense_category} style={{ borderBottom: "1px solid var(--border)" }}>
                    <td style={{ padding: "10px 12px", fontWeight: 600 }}>{row.expense_category}</td>
                    <td style={{ padding: "10px 12px" }}>₹{row.amount_cr} Cr</td>
                    <td style={{ padding: "10px 12px" }}>
                      <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                        <div style={{
                          height: 6, width: `${row.pct_of_total * 2}px`,
                          background: "var(--accent)", borderRadius: 3, opacity: 0.8,
                        }} />
                        <span style={{ color: "var(--text-muted)" }}>{row.pct_of_total}%</span>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </Panel>
        </>
      )}

      {/* ════════════════════════════════════════════════════════
          TAB: Profitability
      ════════════════════════════════════════════════════════ */}
      {tab === "profit" && (
        <Panel title="EBITDA & Gross Margin — Trailing 12 Months">
          {profitability.length
            ? <ProfitabilityChart data={profitability} />
            : <ChartSkeleton height={300} />}
        </Panel>
      )}

      {/* ════════════════════════════════════════════════════════
          TAB: Working Capital
      ════════════════════════════════════════════════════════ */}
      {tab === "wc" && (
        <Panel title={`DSO / DPO / Cash Conversion Cycle${regionLabel}`}>
          {workingCapital.length
            ? <WorkingCapitalChart data={workingCapital} />
            : <ChartSkeleton />}
        </Panel>
      )}

      {/* ════════════════════════════════════════════════════════
          TAB: Forecast
      ════════════════════════════════════════════════════════ */}
      {tab === "forecast" && (
        <>
          <Panel title="Revenue Forecast — Actual + Next 3 Months (all regions combined)">
            {forecast.length
              ? <ForecastChart data={forecast} />
              : <ChartSkeleton height={320} />}
          </Panel>

          <Panel title="Forecast by Region (₹ Cr)">
            <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 13 }}>
              <thead>
                <tr style={{ borderBottom: "1px solid var(--border)" }}>
                  {["Month", "Region", "Revenue (₹ Cr)", "Type"].map((h) => (
                    <th key={h} style={{ padding: "8px 12px", textAlign: "left", color: "var(--text-muted)", fontWeight: 600, fontSize: 11 }}>{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {forecast
                  .filter((r) => r.type === "forecast")
                  .sort((a, b) => a.month.localeCompare(b.month) || a.region.localeCompare(b.region))
                  .map((row, i) => (
                    <tr key={i} style={{ borderBottom: "1px solid var(--border)" }}>
                      <td style={{ padding: "10px 12px", color: "var(--text-muted)" }}>{row.month}</td>
                      <td style={{ padding: "10px 12px", fontWeight: 600 }}>{row.region}</td>
                      <td style={{ padding: "10px 12px" }}>₹{row.revenue_cr} Cr</td>
                      <td style={{ padding: "10px 12px" }}>
                        <span style={{ background: "rgba(245,158,11,0.15)", color: "var(--amber)", fontSize: 11, fontWeight: 600, padding: "2px 8px", borderRadius: 20 }}>
                          forecast
                        </span>
                      </td>
                    </tr>
                  ))}
              </tbody>
            </table>
          </Panel>
        </>
      )}
    </div>
  );
}
