import React, { useState } from "react";

function InsightCard({ ins }) {
  const [expanded, setExpanded] = useState(true);

  return (
    <div className="insight-card">
      <div className="insight-metric">{ins.metric}</div>
      <div className="insight-finding">{ins.finding}</div>

      <button
        onClick={() => setExpanded((v) => !v)}
        style={{
          background: "none",
          border: "none",
          color: "var(--accent)",
          fontSize: 12,
          cursor: "pointer",
          fontFamily: "inherit",
          padding: "0 0 8px",
          display: "flex",
          alignItems: "center",
          gap: 4,
        }}
      >
        {expanded ? "▾" : "▸"} Root-cause chain
      </button>

      {expanded && (
        <ul className="insight-chain">
          {ins.root_cause_chain.map((step, j) => (
            <li key={j}>{step}</li>
          ))}
        </ul>
      )}

      <div className="insight-impact">
        <strong>Business impact: </strong>
        {ins.business_impact}
      </div>
      <div className="insight-rec">
        <strong>Recommendation: </strong>
        {ins.recommendation}
      </div>
    </div>
  );
}

export default function InsightsPanel({ insights }) {
  if (!insights?.length) return null;
  return (
    <div>
      {insights.map((ins, i) => (
        <InsightCard key={i} ins={ins} />
      ))}
    </div>
  );
}
