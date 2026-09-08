import React from "react";
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid,
  Tooltip, Legend, ResponsiveContainer, ReferenceLine, ReferenceArea,
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
          {p.name}: {Number(p.value).toFixed(1)} days
        </div>
      ))}
    </div>
  );
};

export default function WorkingCapitalChart({ data }) {
  if (!data?.length) return (
    <div style={{ height: 280, display: "flex", alignItems: "center", justifyContent: "center", color: "var(--text-dim)" }}>
      No data
    </div>
  );
  return (
    <ResponsiveContainer width="100%" height={280}>
      <LineChart data={data} margin={{ top: 8, right: 16, left: 0, bottom: 0 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" />
        <XAxis dataKey="month" tick={{ fontSize: 10, fill: "var(--text-muted)" }} tickLine={false} />
        <YAxis tick={{ fontSize: 10, fill: "var(--text-muted)" }} tickLine={false} axisLine={false}
               label={{ value: "Days", angle: -90, position: "insideLeft", fontSize: 10, fill: "var(--text-dim)" }} />
        <Tooltip content={<CustomTooltip />} />
        <Legend wrapperStyle={{ fontSize: 12 }} />
        {/* Danger zone: DSO > 60 days */}
        <ReferenceArea y1={60} y2={90} fill="rgba(232,80,58,0.06)" />
        <ReferenceLine y={60} stroke="var(--red)" strokeDasharray="4 3" strokeWidth={1}
                       label={{ value: "DSO warning", fill: "var(--red)", fontSize: 10, position: "right" }} />
        <Line type="monotone" dataKey="dso_days" name="DSO"
              stroke="var(--red)" strokeWidth={2.5} dot={false} activeDot={{ r: 4 }} />
        <Line type="monotone" dataKey="dpo_days" name="DPO"
              stroke="var(--green)" strokeWidth={2} dot={false} activeDot={{ r: 4 }} />
        <Line type="monotone" dataKey="cash_conversion_cycle" name="CCC"
              stroke="var(--accent)" strokeWidth={2} strokeDasharray="5 3" dot={false} activeDot={{ r: 4 }} />
      </LineChart>
    </ResponsiveContainer>
  );
}
