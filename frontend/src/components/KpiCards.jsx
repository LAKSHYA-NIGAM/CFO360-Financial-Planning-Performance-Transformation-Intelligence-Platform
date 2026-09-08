import React from "react";
import { KpiSkeleton } from "./Skeleton";

function KpiCard({ label, value, badge, color, badgeBg }) {
  return (
    <div
      className="kpi-card"
      style={{ "--kpi-color": color, "--kpi-badge-bg": badgeBg }}
    >
      <div className="kpi-label">{label}</div>
      <div className="kpi-value">{value}</div>
      {badge != null && <div className="kpi-badge">{badge}</div>}
    </div>
  );
}

export default function KpiCards({ summary }) {
  if (!summary) return <KpiSkeleton />;

  const variance = Number(summary.revenue_variance_pct);
  const growth   = Number(summary.revenue_growth_pct);
  const dso      = Number(summary.avg_dso_days);
  const ccc      = Number(summary.avg_cash_conversion_cycle);

  const fmtPct = (v) => `${v > 0 ? "+" : ""}${v}%`;

  return (
    <div className="kpi-grid">
      <KpiCard
        label="Revenue"
        value={`₹${summary.total_revenue_cr} Cr`}
        badge={`${fmtPct(growth)} QoQ`}
        color={growth >= 0 ? "var(--green)" : "var(--red)"}
        badgeBg={growth >= 0 ? "var(--green-dim)" : "var(--red-dim)"}
      />
      <KpiCard
        label="Budget Variance"
        value={fmtPct(variance)}
        badge={variance >= -3 ? "On plan" : variance >= -10 ? "Below plan" : "Critical miss"}
        color={variance >= -3 ? "var(--green)" : variance >= -10 ? "var(--amber)" : "var(--red)"}
        badgeBg={variance >= -3 ? "var(--green-dim)" : variance >= -10 ? "rgba(245,158,11,0.15)" : "var(--red-dim)"}
      />
      <KpiCard
        label="Gross Margin"
        value={`${summary.gross_margin_pct}%`}
        color="var(--accent)"
        badgeBg="var(--accent-dim)"
      />
      <KpiCard
        label="EBITDA"
        value={`₹${summary.ebitda_cr} Cr`}
        badge={`${summary.ebitda_margin_pct}% margin`}
        color="var(--accent)"
        badgeBg="var(--accent-dim)"
      />
      <KpiCard
        label="DSO"
        value={`${dso} days`}
        badge={dso > 60 ? "⚠ elevated" : "healthy"}
        color={dso > 60 ? "var(--amber)" : "var(--green)"}
        badgeBg={dso > 60 ? "rgba(245,158,11,0.15)" : "var(--green-dim)"}
      />
      <KpiCard
        label="Cash Conv. Cycle"
        value={`${ccc} days`}
        badge={ccc > 30 ? "⚠ watch" : "normal"}
        color={ccc > 30 ? "var(--amber)" : "var(--text)"}
        badgeBg={ccc > 30 ? "rgba(245,158,11,0.15)" : "var(--surface3)"}
      />
    </div>
  );
}
