import React from "react";
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid,
  Tooltip, Cell, ResponsiveContainer, LabelList,
} from "recharts";

const CustomTooltip = ({ active, payload, label, formatTooltip, yKey }) => {
  if (!active || !payload?.length) return null;
  const val = payload[0]?.value;
  return (
    <div style={{
      background: "var(--surface)",
      border: "1px solid var(--border)",
      borderRadius: 8,
      padding: "10px 14px",
      fontSize: 12,
    }}>
      <div style={{ color: "var(--text-muted)", marginBottom: 4, fontWeight: 600 }}>{label}</div>
      <div style={{ color: payload[0]?.fill || "var(--accent)" }}>
        {formatTooltip ? formatTooltip(val) : val}
      </div>
    </div>
  );
};

const DEFAULT_COLORS = ["#3b7bff", "#7c3aed", "#22c97a", "#f59e0b", "#e8503a"];

export default function BreakdownBarChart({
  data, xKey, yKey, yLabel, colorBy, formatTooltip, layout = "vertical",
}) {
  if (!data?.length) return (
    <div style={{ height: 260, display: "flex", alignItems: "center", justifyContent: "center", color: "var(--text-dim)", fontSize: 13 }}>
      No data
    </div>
  );

  const isVertical = layout === "vertical";

  return (
    <ResponsiveContainer width="100%" height={260}>
      <BarChart
        data={data}
        layout={isVertical ? "horizontal" : "vertical"}
        margin={{ top: 8, right: 20, left: isVertical ? 0 : 80, bottom: 0 }}
      >
        <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)"
          horizontal={isVertical} vertical={!isVertical} />
        {isVertical ? (
          <>
            <XAxis dataKey={xKey} tick={{ fontSize: 11, fill: "var(--text-muted)" }} tickLine={false} />
            <YAxis tick={{ fontSize: 10, fill: "var(--text-muted)" }} tickLine={false} axisLine={false}
              label={yLabel ? { value: yLabel, angle: -90, position: "insideLeft", fontSize: 10, fill: "var(--text-dim)" } : undefined} />
          </>
        ) : (
          <>
            <XAxis type="number" tick={{ fontSize: 10, fill: "var(--text-muted)" }} tickLine={false} axisLine={false} />
            <YAxis type="category" dataKey={xKey} tick={{ fontSize: 11, fill: "var(--text-muted)" }} tickLine={false} width={75} />
          </>
        )}
        <Tooltip content={<CustomTooltip formatTooltip={formatTooltip} yKey={yKey} />} cursor={{ fill: "rgba(255,255,255,0.03)" }} />
        <Bar dataKey={yKey} radius={isVertical ? [4, 4, 0, 0] : [0, 4, 4, 0]} maxBarSize={48}>
          {data.map((row, i) => (
            <Cell
              key={i}
              fill={colorBy ? colorBy(row) : DEFAULT_COLORS[i % DEFAULT_COLORS.length]}
              fillOpacity={0.9}
            />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
}
