-- CFO360 / NexaTech Industries — Root-cause analysis queries
-- These mirror the logic in python/financial_analysis.py::generate_insights(),
-- so the same story can be reproduced/verified directly in SQL.

-- ============================================================
-- A. Full chain in one query: company -> region -> product -> discount driver
-- (trailing 3 months vs prior 3 months)
-- ============================================================
WITH recent AS (
    SELECT region, product, SUM(revenue) AS revenue, AVG(discount) AS avg_discount
    FROM sales
    WHERE date >= (SELECT MAX(date) FROM sales) - INTERVAL '3 months'
    GROUP BY region, product
),
prior AS (
    SELECT region, product, SUM(revenue) AS revenue, AVG(discount) AS avg_discount
    FROM sales
    WHERE date >= (SELECT MAX(date) FROM sales) - INTERVAL '6 months'
      AND date <  (SELECT MAX(date) FROM sales) - INTERVAL '3 months'
    GROUP BY region, product
)
SELECT
    r.region, r.product,
    r.revenue AS recent_revenue,
    p.revenue AS prior_revenue,
    ROUND(100.0 * (r.revenue - p.revenue) / NULLIF(p.revenue, 0), 2) AS revenue_change_pct,
    ROUND((r.avg_discount - p.avg_discount) * 100, 2) AS discount_change_pts
FROM recent r
JOIN prior p USING (region, product)
ORDER BY revenue_change_pct ASC
LIMIT 10;

-- ============================================================
-- B. Rank regions by budget miss severity (identifies "North" automatically)
-- ============================================================
SELECT
    region,
    ROUND(100.0 * (SUM(revenue) - SUM(budget_revenue)) / NULLIF(SUM(budget_revenue), 0), 2) AS variance_pct,
    RANK() OVER (ORDER BY (SUM(revenue) - SUM(budget_revenue)) / NULLIF(SUM(budget_revenue), 0) ASC) AS worst_rank
FROM v_fact_monthly
WHERE month >= (SELECT MAX(month) FROM v_fact_monthly) - INTERVAL '2 months'
GROUP BY region;

-- ============================================================
-- C. Estimated revenue foregone from discount creep (business impact quantification)
-- ============================================================
WITH baseline AS (
    -- Assume the discount level from 6-9 months ago as the "normal" baseline
    SELECT region, product, AVG(discount) AS baseline_discount
    FROM sales
    WHERE date >= (SELECT MAX(date) FROM sales) - INTERVAL '9 months'
      AND date <  (SELECT MAX(date) FROM sales) - INTERVAL '6 months'
    GROUP BY region, product
),
current_period AS (
    SELECT region, product, SUM(revenue) AS revenue, AVG(discount) AS current_discount,
           SUM(revenue) / (1 - AVG(discount)) AS implied_gross_revenue
    FROM sales
    WHERE date >= (SELECT MAX(date) FROM sales) - INTERVAL '3 months'
    GROUP BY region, product
)
SELECT
    c.region, c.product,
    ROUND((c.current_discount - b.baseline_discount) * 100, 2) AS discount_creep_pts,
    ROUND(c.implied_gross_revenue * (c.current_discount - b.baseline_discount) / 1e7, 2) AS est_revenue_foregone_cr
FROM current_period c
JOIN baseline b USING (region, product)
WHERE c.current_discount > b.baseline_discount
ORDER BY est_revenue_foregone_cr DESC;

-- ============================================================
-- D. Working capital driver: which region's DSO moved the most
-- ============================================================
WITH monthly_rev AS (
    SELECT date_trunc('month', date)::date AS month, region, SUM(revenue) AS revenue
    FROM sales GROUP BY 1, 2
),
dso AS (
    SELECT w.date AS month, w.region,
           w.accounts_receivable / NULLIF(m.revenue, 0) * 30 AS dso_days
    FROM working_capital w
    JOIN monthly_rev m ON m.month = w.date AND m.region = w.region
),
recent AS (
    SELECT region, AVG(dso_days) AS dso_recent
    FROM dso WHERE month >= (SELECT MAX(month) FROM dso) - INTERVAL '2 months'
    GROUP BY region
),
prior AS (
    SELECT region, AVG(dso_days) AS dso_prior
    FROM dso
    WHERE month >= (SELECT MAX(month) FROM dso) - INTERVAL '5 months'
      AND month <  (SELECT MAX(month) FROM dso) - INTERVAL '2 months'
    GROUP BY region
)
SELECT r.region, ROUND(r.dso_recent, 1) AS dso_recent, ROUND(p.dso_prior, 1) AS dso_prior,
       ROUND(r.dso_recent - p.dso_prior, 1) AS dso_change_days
FROM recent r JOIN prior p USING (region)
ORDER BY dso_change_days DESC;
