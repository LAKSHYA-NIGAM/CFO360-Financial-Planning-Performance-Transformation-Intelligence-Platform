-- CFO360 / NexaTech Industries — KPI queries
-- All amounts in INR; divide by 1e7 for ₹ Cr.

-- ============================================================
-- 1. Monthly fact table: revenue, COGS, opex, EBITDA, budget variance
-- ============================================================
CREATE OR REPLACE VIEW v_fact_monthly AS
WITH rev AS (
    SELECT date_trunc('month', date)::date AS month, region, business_unit,
           SUM(revenue) AS revenue
    FROM sales
    GROUP BY 1, 2, 3
),
cogs AS (
    SELECT date_trunc('month', date)::date AS month, region, business_unit,
           SUM(amount) AS cogs
    FROM expenses WHERE expense_category = 'COGS'
    GROUP BY 1, 2, 3
),
opex AS (
    SELECT date_trunc('month', date)::date AS month, region, business_unit,
           SUM(amount) AS opex
    FROM expenses WHERE expense_category <> 'COGS'
    GROUP BY 1, 2, 3
)
SELECT
    r.month, r.region, r.business_unit,
    r.revenue,
    COALESCE(c.cogs, 0)  AS cogs,
    COALESCE(o.opex, 0)  AS opex,
    r.revenue - COALESCE(c.cogs, 0) AS gross_profit,
    ROUND(100.0 * (r.revenue - COALESCE(c.cogs, 0)) / NULLIF(r.revenue, 0), 2) AS gross_margin_pct,
    r.revenue - COALESCE(c.cogs, 0) - COALESCE(o.opex, 0) AS ebitda,
    ROUND(100.0 * (r.revenue - COALESCE(c.cogs, 0) - COALESCE(o.opex, 0)) / NULLIF(r.revenue, 0), 2) AS ebitda_margin_pct,
    b.budget_revenue,
    b.budget_expense,
    r.revenue - b.budget_revenue AS revenue_variance,
    ROUND(100.0 * (r.revenue - b.budget_revenue) / NULLIF(b.budget_revenue, 0), 2) AS revenue_variance_pct
FROM rev r
LEFT JOIN cogs c USING (month, region, business_unit)
LEFT JOIN opex o USING (month, region, business_unit)
LEFT JOIN budget b ON b.month = r.month AND b.region = r.region AND b.business_unit = r.business_unit;

-- ============================================================
-- 2. Revenue growth % (month-over-month, per region) — window function
-- ============================================================
SELECT
    month, region,
    SUM(revenue) AS revenue,
    ROUND(
      100.0 * (SUM(revenue) - LAG(SUM(revenue)) OVER (PARTITION BY region ORDER BY month))
      / NULLIF(LAG(SUM(revenue)) OVER (PARTITION BY region ORDER BY month), 0)
    , 2) AS revenue_growth_pct
FROM v_fact_monthly
GROUP BY month, region
ORDER BY region, month;

-- ============================================================
-- 3. Budget variance by region — trailing 3 months, worst first
-- ============================================================
SELECT
    region,
    SUM(revenue)           AS actual_revenue,
    SUM(budget_revenue)    AS budget_revenue,
    ROUND(100.0 * (SUM(revenue) - SUM(budget_revenue)) / NULLIF(SUM(budget_revenue), 0), 2) AS variance_pct
FROM v_fact_monthly
WHERE month >= (SELECT MAX(month) FROM v_fact_monthly) - INTERVAL '2 months'
GROUP BY region
ORDER BY variance_pct ASC;

-- ============================================================
-- 4. Drill-down: which product inside the worst region is driving the miss
-- ============================================================
SELECT
    s.product,
    SUM(s.revenue) AS revenue,
    ROUND(AVG(s.discount) * 100, 2) AS avg_discount_pct
FROM sales s
WHERE s.region = 'North'                                   -- swap in worst region from query 3
  AND s.date >= (SELECT MAX(date) FROM sales) - INTERVAL '3 months'
GROUP BY s.product
ORDER BY revenue ASC;

-- ============================================================
-- 5. Cost variance and cost by category
-- ============================================================
SELECT
    expense_category,
    SUM(amount) AS total_amount,
    ROUND(100.0 * SUM(amount) / SUM(SUM(amount)) OVER (), 2) AS pct_of_total
FROM expenses
WHERE date >= (SELECT MAX(date) FROM expenses) - INTERVAL '3 months'
GROUP BY expense_category
ORDER BY total_amount DESC;

-- ============================================================
-- 6. Working capital: DSO, DPO, Cash Conversion Cycle by region
-- ============================================================
WITH monthly_rev AS (
    SELECT date_trunc('month', date)::date AS month, region, SUM(revenue) AS revenue
    FROM sales GROUP BY 1, 2
)
SELECT
    w.date AS month, w.region,
    ROUND(w.accounts_receivable / NULLIF(m.revenue, 0) * 30, 1) AS dso_days,
    ROUND(w.accounts_payable / NULLIF(m.revenue * 0.55, 0) * 30, 1) AS dpo_days,
    ROUND(w.inventory / NULLIF(m.revenue * 0.5, 0) * 30, 1) AS dio_days,
    ROUND(
        (w.accounts_receivable / NULLIF(m.revenue, 0) * 30)
      + (w.inventory / NULLIF(m.revenue * 0.5, 0) * 30)
      - (w.accounts_payable / NULLIF(m.revenue * 0.55, 0) * 30)
    , 1) AS cash_conversion_cycle
FROM working_capital w
JOIN monthly_rev m ON m.month = w.date AND m.region = w.region
ORDER BY w.region, w.date;

-- ============================================================
-- 7. EBITDA trend, trailing 12 months, company-wide
-- ============================================================
SELECT
    month,
    SUM(revenue)  AS revenue,
    SUM(ebitda)   AS ebitda,
    ROUND(100.0 * SUM(ebitda) / NULLIF(SUM(revenue), 0), 2) AS ebitda_margin_pct
FROM v_fact_monthly
WHERE month >= (SELECT MAX(month) FROM v_fact_monthly) - INTERVAL '11 months'
GROUP BY month
ORDER BY month;
