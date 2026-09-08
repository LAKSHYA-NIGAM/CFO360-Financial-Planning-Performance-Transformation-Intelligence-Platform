const BASE = "/api";

async function get(path, params = {}) {
  const query = new URLSearchParams(
    Object.fromEntries(Object.entries(params).filter(([, v]) => v != null && v !== ""))
  ).toString();
  const url = `${BASE}${path}${query ? `?${query}` : ""}`;
  const res = await fetch(url);
  if (!res.ok) {
    let detail = "";
    try {
      const body = await res.json();
      detail = body.error || body.detail || "";
    } catch (_) {}
    throw new Error(`API ${url} → ${res.status}${detail ? ": " + detail : ""}`);
  }
  return res.json();
}

export const api = {
  regions:         ()       => get("/regions"),
  kpiSummary:      ()       => get("/kpi-summary"),
  revenueTrend:    (region) => get("/revenue-trend",    { region }),
  revenueByRegion: ()       => get("/revenue-by-region"),
  revenueByProduct:()       => get("/revenue-by-product"),
  budgetVariance:  (region) => get("/budget-variance",  { region }),
  costByCategory:  (region) => get("/cost-by-category", { region }),
  profitability:   ()       => get("/profitability"),
  workingCapital:  (region) => get("/working-capital",  { region }),
  forecast:        ()       => get("/forecast"),
  insights:        ()       => get("/insights"),
};
