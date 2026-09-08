import React from "react";
import {
  ComposedChart, Area, Line, XAxis, YAxis,
  CartesianGrid, Tooltip, Legend, ResponsiveContainer, ReferenceLine,
} from "recharts";

const CustomTooltip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null;
  return (
    <div style={{
      background: "var(--surface)",
      border: "1px solid var(--border)",
      borderRadius: 8,
      padding: "10px 14px",
      fontSize: 12,
    }}>
      <div style={{ color: "var(--text-muted)", marginBottom: 6, fontWeight: 600 }}>{label}</div>
      {payload.map((p) => (
        <div key={p.name} style={{ color: p.color, marginBottom: 3 }}>
          {p.name}: ₹{p.value} Cr
        </div>
      ))}
    </div>
  );
};

export default function RevenueTrendChart({ data }) {
  if (!data?.length) return (
    <div style={{ height: 280, display: "flex", alignItems: "center", justifyContent: "center", color: "var(--text-dim)" }}>
      No data
    </div>
  );
  return (
    <ResponsiveContainer width="100%" height={280}>
      <ComposedChart data={data} margin={{ top: 8, right: 16, left: 0, bottom: 0 }}>
        <defs>
          <linearGradient id="revenueGrad" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%"  stopColor="#3b7bff" stopOpacity={0.25} />
            <stop offset="95%" stopColor="#3b7bff" stopOpacity={0}    />
          </linearGradient>
        </defs>
        <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" />
        <XAxis dataKey="month" tick={{ fontSize: 10, fill: "var(--text-muted)" }} tickLine={false} />
        <YAxis tick={{ fontSize: 10, fill: "var(--text-muted)" }} tickLine={false} axisLine={false}
               label={{ value: "₹ Cr", angle: -90, position: "insideLeft", fontSize: 10, fill: "var(--text-dim)" }} />
        <Tooltip content={<CustomTooltip />} />
        <Legend wrapperStyle={{ fontSize: 12 }} />
        <Area
          type="monotone" dataKey="revenue_cr" name="Actual revenue"
          stroke="#3b7bff" strokeWidth={2.5} fill="url(#revenueGrad)" dot={false}
        />
        <Line
          type="monotone" dataKey="budget_revenue_cr" name="Budget"
          stroke="var(--red)" strokeWidth={2} strokeDasharray="6 4" dot={false}
        />
      </ComposedChart>
    </ResponsiveContainer>
  );
}
