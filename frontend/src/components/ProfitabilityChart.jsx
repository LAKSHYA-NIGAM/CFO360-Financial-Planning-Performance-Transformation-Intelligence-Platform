import React from "react";
import {
  ComposedChart, Area, Line, XAxis, YAxis, CartesianGrid,
  Tooltip, Legend, ResponsiveContainer,
} from "recharts";

const CustomTooltip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null;
  return (
    <div style={{
      background: "var(--surface)", border: "1px solid var(--border)",
      borderRadius: 8, padding: "10px 14px", fontSize: 12,
    }}>
      <div style={{ color: "var(--text-muted)", marginBottom: 6, fontWeight: 600 }}>{label}</div>
      {payload.map((p) => (
        <div key={p.name} style={{ color: p.color, marginBottom: 3 }}>
          {p.name}: {p.name.includes("%") || p.name.includes("Margin")
            ? `${Number(p.value).toFixed(1)}%`
            : `₹${Number(p.value).toFixed(1)} Cr`}
        </div>
      ))}
    </div>
  );
};

export default function ProfitabilityChart({ data }) {
  if (!data?.length) return (
    <div style={{ height: 300, display: "flex", alignItems: "center", justifyContent: "center", color: "var(--text-dim)" }}>
      No data
    </div>
  );
  return (
    <ResponsiveContainer width="100%" height={300}>
      <ComposedChart data={data} margin={{ top: 8, right: 60, left: 0, bottom: 0 }}>
        <defs>
          <linearGradient id="gpGrad" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%"  stopColor="#22c97a" stopOpacity={0.2} />
            <stop offset="95%" stopColor="#22c97a" stopOpacity={0}   />
          </linearGradient>
          <linearGradient id="ebitdaGrad" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%"  stopColor="#3b7bff" stopOpacity={0.2} />
            <stop offset="95%" stopColor="#3b7bff" stopOpacity={0}   />
          </linearGradient>
        </defs>
        <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" />
        <XAxis dataKey="month" tick={{ fontSize: 10, fill: "var(--text-muted)" }} tickLine={false} />
        {/* Left Y: ₹ Cr */}
        <YAxis yAxisId="cr" tick={{ fontSize: 10, fill: "var(--text-muted)" }} tickLine={false} axisLine={false}
               label={{ value: "₹ Cr", angle: -90, position: "insideLeft", fontSize: 10, fill: "var(--text-dim)" }} />
        {/* Right Y: % */}
        <YAxis yAxisId="pct" orientation="right" tick={{ fontSize: 10, fill: "var(--text-muted)" }} tickLine={false} axisLine={false}
               label={{ value: "%", angle: 90, position: "insideRight", fontSize: 10, fill: "var(--text-dim)" }} />
        <Tooltip content={<CustomTooltip />} />
        <Legend wrapperStyle={{ fontSize: 12 }} />
        <Area yAxisId="cr" type="monotone" dataKey="gross_profit_cr" name="Gross Profit (Cr)"
              stroke="#22c97a" strokeWidth={2} fill="url(#gpGrad)" dot={false} />
        <Area yAxisId="cr" type="monotone" dataKey="ebitda_cr" name="EBITDA (Cr)"
              stroke="#3b7bff" strokeWidth={2} fill="url(#ebitdaGrad)" dot={false} />
        <Line yAxisId="pct" type="monotone" dataKey="gross_margin_pct" name="Gross Margin %"
              stroke="#22c97a" strokeWidth={2} strokeDasharray="5 3" dot={false} />
        <Line yAxisId="pct" type="monotone" dataKey="ebitda_margin_pct" name="EBITDA Margin %"
              stroke="#3b7bff" strokeWidth={2} strokeDasharray="5 3" dot={false} />
      </ComposedChart>
    </ResponsiveContainer>
  );
}
