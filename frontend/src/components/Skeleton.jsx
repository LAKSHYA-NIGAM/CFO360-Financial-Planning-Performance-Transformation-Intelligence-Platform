import React from "react";

/** Shimmer skeleton block */
export function SkeletonBlock({ height = 20, width = "100%", style = {} }) {
  return (
    <div
      className="skeleton"
      style={{ height, width, borderRadius: 8, ...style }}
    />
  );
}

/** Skeleton for a KPI grid row */
export function KpiSkeleton() {
  return (
    <div className="kpi-grid" style={{ marginBottom: 24 }}>
      {[1, 2, 3, 4, 5, 6].map((i) => (
        <div
          key={i}
          style={{
            background: "var(--surface2)",
            border: "1px solid var(--border)",
            borderRadius: "var(--radius)",
            padding: "18px 20px",
          }}
        >
          <SkeletonBlock height={10} width="60%" style={{ marginBottom: 12 }} />
          <SkeletonBlock height={28} width="80%" />
        </div>
      ))}
    </div>
  );
}

/** Skeleton for a chart card */
export function ChartSkeleton({ height = 280 }) {
  return (
    <div
      className="card"
      style={{ marginBottom: 18 }}
    >
      <SkeletonBlock height={12} width={140} style={{ marginBottom: 20 }} />
      <SkeletonBlock height={height} />
    </div>
  );
}
