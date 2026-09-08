import React from "react";
import {
  ComposedChart, Area, Line, XAxis, YAxis, CartesianGrid,
  Tooltip, Legend, ResponsiveContainer, ReferenceLine,
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
        <div key={p.dataKey} style={{ color: p.color, marginBottom: 3 }}>
          {p.name}: ₹{Number(p.value).toFixed(2)} Cr
        </div>
      ))}
    </div>
  );
};

/** Splits forecast data into actual + forecast segments so the dashed section
 *  only starts where type === 'forecast'. */
function splitSeries(data) {
  const actuals   = data.map((d) => ({ ...d, actual_cr:   d.type === "actual"   ? d.revenue_cr : null }));
  const forecasts = data.map((d) => ({ ...d, forecast_cr: d.type === "forecast" ? d.revenue_cr : null }));
  return actuals.map((a, i) => ({ ...a, ...forecasts[i] }));
}

export default function ForecastChart({ data }) {
  if (!data?.length) return (
    <div style={{ height: 320, display: "flex", alignItems: "center", justifyContent: "center", color: "var(--text-dim)" }}>
      No data
    </div>
  );

  // Group by region, take all-region view for the combined chart
  const regions = [...new Set(data.map((d) => d.region))].sort();

  // Find the boundary month (first forecast point)
  const boundaryMonth = data.find((d) => d.type === "forecast")?.month;

  // Aggregate across regions per month
  const monthMap = {};
  data.forEach(({ month, revenue_cr, type, region }) => {
    if (!monthMap[month]) monthMap[month] = { month, total_cr: 0, type };
    monthMap[month].total_cr = +(monthMap[month].total_cr + revenue_cr).toFixed(2);
  });
  const combined = Object.values(monthMap).sort((a, b) => a.month.localeCompare(b.month));
  const split = splitSeries(combined.map((d) => ({
    ...d,
    revenue_cr: d.total_cr,
  })));

  return (
    <ResponsiveContainer width="100%" height={320}>
      <ComposedChart data={split} margin={{ top: 8, right: 16, left: 0, bottom: 0 }}>
        <defs>
          <linearGradient id="actualGrad" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%"  stopColor="#3b7bff" stopOpacity={0.25} />
            <stop offset="95%" stopColor="#3b7bff" stopOpacity={0}    />
          </linearGradient>
          <linearGradient id="fcGrad" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%"  stopColor="#f59e0b" stopOpacity={0.2} />
            <stop offset="95%" stopColor="#f59e0b" stopOpacity={0}   />
          </linearGradient>
        </defs>
        <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" />
        <XAxis dataKey="month" tick={{ fontSize: 10, fill: "var(--text-muted)" }} tickLine={false} />
        <YAxis tick={{ fontSize: 10, fill: "var(--text-muted)" }} tickLine={false} axisLine={false}
               label={{ value: "₹ Cr", angle: -90, position: "insideLeft", fontSize: 10, fill: "var(--text-dim)" }} />
        <Tooltip content={<CustomTooltip />} />
        <Legend wrapperStyle={{ fontSize: 12 }} />
        {boundaryMonth && (
          <ReferenceLine x={boundaryMonth} stroke="var(--amber)" strokeDasharray="4 3"
            label={{ value: "Forecast →", fill: "var(--amber)", fontSize: 10, position: "top" }} />
        )}
        <Area type="monotone" dataKey="actual_cr" name="Actual revenue"
              stroke="#3b7bff" strokeWidth={2.5} fill="url(#actualGrad)" dot={false} connectNulls />
        <Area type="monotone" dataKey="forecast_cr" name="Forecast"
              stroke="var(--amber)" strokeWidth={2} strokeDasharray="6 4" fill="url(#fcGrad)" dot={false} connectNulls />
      </ComposedChart>
    </ResponsiveContainer>
  );
}
