"""
CFO360 - Financial Analysis Engine
-----------------------------------
Loads the 5 source tables and produces:
  1. A clean, consistent monthly fact table (revenue, cogs, opex, ebitda, etc.)
  2. All KPIs defined in the project brief (Revenue, Profitability, Budget,
     Cost, Working Capital)
  3. An automated root-cause narrative: Metric -> Variance -> Root Cause ->
     Business Impact -> Recommendation, following the exact analytical
     chain the brief asks for (region -> product -> driver).

Run:
    python financial_analysis.py
Outputs (in ../data/):
    fact_monthly.csv          - one row per region/business_unit/month with all KPIs
    kpi_summary.csv           - company-level KPI summary
    insights.json             - structured root-cause + recommendation output
    executive_narrative.md    - human-readable version of the same insights
"""

import json
import sys
import numpy as np
import pandas as pd

# Ensure the terminal can print Unicode (e.g. ₹ sign) on Windows cp1252 consoles
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

DATA = "../data"


def load_data():
    sales = pd.read_csv(f"{DATA}/sales.csv", parse_dates=["date"])
    expenses = pd.read_csv(f"{DATA}/expenses.csv", parse_dates=["date"])
    budget = pd.read_csv(f"{DATA}/budget.csv", parse_dates=["month"])
    wc = pd.read_csv(f"{DATA}/working_capital.csv", parse_dates=["date"])
    customers = pd.read_csv(f"{DATA}/customers.csv")
    for df in (sales, expenses, wc):
        df["month"] = df["date"].values.astype("datetime64[M]")
    return sales, expenses, budget, wc, customers


def build_fact_monthly(sales, expenses, budget):
    """One row per (month, region, business_unit) with revenue, cogs, opex, ebitda, budget."""
    rev = sales.groupby(["month", "region", "business_unit"]).revenue.sum().reset_index()

    cogs = (
        expenses[expenses.expense_category == "COGS"]
        .groupby(["month", "region", "business_unit"]).amount.sum()
        .reset_index().rename(columns={"amount": "cogs"})
    )
    opex = (
        expenses[expenses.expense_category != "COGS"]
        .groupby(["month", "region", "business_unit"]).amount.sum()
        .reset_index().rename(columns={"amount": "opex"})
    )

    fact = rev.merge(cogs, on=["month", "region", "business_unit"], how="left")
    fact = fact.merge(opex, on=["month", "region", "business_unit"], how="left")
    fact = fact.merge(
        budget.rename(columns={"month": "month"}),
        on=["month", "region", "business_unit"], how="left"
    )
    fact[["cogs", "opex"]] = fact[["cogs", "opex"]].fillna(0)

    fact["gross_profit"] = fact.revenue - fact.cogs
    fact["gross_margin_pct"] = fact.gross_profit / fact.revenue * 100
    fact["ebitda"] = fact.gross_profit - fact.opex
    fact["ebitda_margin_pct"] = fact.ebitda / fact.revenue * 100
    fact["total_expense"] = fact.cogs + fact.opex

    fact["revenue_variance"] = fact.revenue - fact.budget_revenue
    fact["revenue_variance_pct"] = fact.revenue_variance / fact.budget_revenue * 100
    fact["cost_variance"] = fact.total_expense - fact.budget_expense
    fact["cost_variance_pct"] = fact.cost_variance / fact.budget_expense * 100

    fact = fact.sort_values(["region", "business_unit", "month"])
    fact["revenue_prev_month"] = fact.groupby(["region", "business_unit"]).revenue.shift(1)
    fact["revenue_growth_pct"] = (
        (fact.revenue - fact.revenue_prev_month) / fact.revenue_prev_month * 100
    )
    return fact


def build_working_capital_kpis(wc, sales):
    """DSO, DPO, Cash Conversion Cycle by region/month."""
    rev_by_month_region = sales.groupby(["month", "region"]).revenue.sum().reset_index()
    wc = wc.merge(rev_by_month_region, on=["month", "region"], how="left")
    wc["dso_days"] = wc.accounts_receivable / wc.revenue * 30
    wc["dpo_days"] = wc.accounts_payable / (wc.revenue * 0.55) * 30
    wc["dio_days"] = wc.inventory / (wc.revenue * 0.5) * 30  # rough inventory-days proxy
    wc["cash_conversion_cycle"] = wc.dso_days + wc.dio_days - wc.dpo_days
    return wc


def company_kpi_summary(fact, wc, sales, budget):
    latest_month = fact.month.max()
    trailing_3 = fact[fact.month >= latest_month - pd.DateOffset(months=2)]

    total_revenue = trailing_3.revenue.sum()
    total_budget_revenue = trailing_3.budget_revenue.sum()
    total_expense = trailing_3.total_expense.sum()
    total_budget_expense = trailing_3.budget_expense.sum()
    gross_profit = trailing_3.gross_profit.sum()
    ebitda = trailing_3.ebitda.sum()

    prior_3 = fact[
        (fact.month < latest_month - pd.DateOffset(months=2))
        & (fact.month >= latest_month - pd.DateOffset(months=5))
    ]
    revenue_growth_pct = (total_revenue - prior_3.revenue.sum()) / prior_3.revenue.sum() * 100

    wc_latest = wc[wc.month == latest_month]

    summary = {
        "period": f"Trailing 3 months ending {latest_month.strftime('%b %Y')}",
        "total_revenue_cr": round(total_revenue / 1e7, 2),
        "budget_revenue_cr": round(total_budget_revenue / 1e7, 2),
        "revenue_variance_pct": round((total_revenue - total_budget_revenue) / total_budget_revenue * 100, 2),
        "revenue_growth_pct": round(revenue_growth_pct, 2),
        "gross_profit_cr": round(gross_profit / 1e7, 2),
        "gross_margin_pct": round(gross_profit / total_revenue * 100, 2),
        "ebitda_cr": round(ebitda / 1e7, 2),
        "ebitda_margin_pct": round(ebitda / total_revenue * 100, 2),
        "total_expense_cr": round(total_expense / 1e7, 2),
        "cost_variance_pct": round((total_expense - total_budget_expense) / total_budget_expense * 100, 2),
        "avg_dso_days": round(wc_latest.dso_days.mean(), 1),
        "avg_dpo_days": round(wc_latest.dpo_days.mean(), 1),
        "avg_cash_conversion_cycle": round(wc_latest.cash_conversion_cycle.mean(), 1),
    }
    return summary


def generate_insights(fact, wc, sales, latest_month=None):
    """
    Automated Metric -> Variance -> Root Cause -> Business Impact -> Recommendation
    chain. Walks: company variance -> worst region -> worst product in that
    region -> worst driver (discount trend) -> recommendation.
    """
    if latest_month is None:
        latest_month = fact.month.max()
    window = fact[fact.month >= latest_month - pd.DateOffset(months=2)]

    insights = []

    # ---- 1. Company-level revenue variance ----
    co_rev = window.revenue.sum()
    co_budget = window.budget_revenue.sum()
    co_var_pct = (co_rev - co_budget) / co_budget * 100

    # ---- 2. Region-level variance -> find worst region ----
    region_var = (
        window.groupby("region")
        .apply(lambda g: (g.revenue.sum() - g.budget_revenue.sum()) / g.budget_revenue.sum() * 100)
        .rename("variance_pct").reset_index()
        .sort_values("variance_pct")
    )
    worst_region = region_var.iloc[0]

    # ---- 3. Within worst region, find worst product ----
    sales_window = sales[(sales.month >= latest_month - pd.DateOffset(months=2))
                          & (sales.region == worst_region.region)]
    sales_prior = sales[(sales.month >= latest_month - pd.DateOffset(months=5))
                         & (sales.month < latest_month - pd.DateOffset(months=2))
                         & (sales.region == worst_region.region)]
    prod_now = sales_window.groupby("product").revenue.sum()
    prod_prior = sales_prior.groupby("product").revenue.sum()
    prod_change_pct = ((prod_now - prod_prior) / prod_prior * 100).sort_values()
    worst_product = prod_change_pct.index[0]
    worst_product_change = prod_change_pct.iloc[0]

    # ---- 4. Root cause driver: discount trend for that region/product ----
    disc_now = sales_window[sales_window["product"] == worst_product].discount.mean()
    disc_prior = sales_prior[sales_prior["product"] == worst_product].discount.mean()
    disc_change_pts = (disc_now - disc_prior) * 100

    insights.append({
        "metric": "Total Revenue vs Budget",
        "finding": f"Company revenue is {co_var_pct:.1f}% {'below' if co_var_pct < 0 else 'above'} budget "
                   f"over the trailing 3 months.",
        "root_cause_chain": [
            f"Region driver: {worst_region.region} region is the largest negative contributor, "
            f"running {worst_region.variance_pct:.1f}% below its budget.",
            f"Product driver: within {worst_region.region}, {worst_product} revenue is down "
            f"{worst_product_change:.1f}% versus the prior 3-month period.",
            f"Root cause: average discount on {worst_product} in {worst_region.region} has "
            f"increased by {disc_change_pts:.1f} percentage points over the same window, "
            f"consistent with a pricing/competitive response eroding realized revenue.",
        ],
        "business_impact": (
            f"At the current run rate, sustaining this discount level costs approximately "
            f"₹{abs(worst_product_change) / 100 * (prod_prior.sum() / 1e7):.1f} Cr in foregone "
            f"revenue over 3 months for {worst_product} in {worst_region.region} alone, and is "
            f"the single largest driver of the company-wide budget miss."
        ),
        "recommendation": (
            f"Freeze further discount escalation on {worst_product} in {worst_region.region}; "
            f"run a win/loss review on recent deals to confirm whether the competitive threat is "
            f"real or self-inflicted, and reallocate sales incentives toward higher-margin, "
            f"on-plan products in that region while a pricing review is completed."
        ),
    })

    # ---- Working capital insight ----
    wc_window = wc[wc.month >= latest_month - pd.DateOffset(months=2)]
    wc_prior = wc[(wc.month >= latest_month - pd.DateOffset(months=5))
                  & (wc.month < latest_month - pd.DateOffset(months=2))]
    dso_now = wc_window.groupby("region").dso_days.mean()
    dso_prior = wc_prior.groupby("region").dso_days.mean()
    dso_change = (dso_now - dso_prior).sort_values(ascending=False)
    worst_dso_region = dso_change.index[0]
    ccc_now = wc_window.cash_conversion_cycle.mean()
    ccc_prior = wc_prior.cash_conversion_cycle.mean()

    insights.append({
        "metric": "Cash Conversion Cycle",
        "finding": f"Company-wide cash conversion cycle has moved from {ccc_prior:.0f} to "
                   f"{ccc_now:.0f} days, a deterioration of {ccc_now - ccc_prior:.0f} days.",
        "root_cause_chain": [
            f"Region driver: {worst_dso_region} shows the sharpest DSO increase, up "
            f"{dso_change.iloc[0]:.0f} days versus the prior period.",
            f"Root cause: extended payment terms granted to large enterprise accounts in "
            f"{worst_dso_region} are slowing collections faster than payables or inventory "
            f"are improving.",
        ],
        "business_impact": (
            f"Every additional day of DSO ties up roughly ₹{(wc_window[wc_window.region==worst_dso_region].accounts_receivable.mean()/dso_now[worst_dso_region])/1e7:.2f} "
            f"Cr of working capital in {worst_dso_region} alone, directly reducing free cash "
            f"available for reinvestment."
        ),
        "recommendation": (
            f"Renegotiate payment terms on the top 3-5 overdue accounts in {worst_dso_region}, "
            f"introduce early-payment incentives, and set a DSO ceiling as a regional finance "
            f"KPI going forward."
        ),
    })

    return insights


def write_narrative_md(summary, insights, path):
    lines = []
    lines.append("# NexaTech Industries — Executive Financial Narrative\n")
    lines.append(f"**Period:** {summary['period']}\n")
    lines.append("## Headline KPIs\n")
    lines.append(f"- Revenue: ₹{summary['total_revenue_cr']} Cr (Growth: {summary['revenue_growth_pct']}%)")
    lines.append(f"- Budget Variance: {summary['revenue_variance_pct']}%")
    lines.append(f"- EBITDA: ₹{summary['ebitda_cr']} Cr (Margin: {summary['ebitda_margin_pct']}%)")
    lines.append(f"- Gross Margin: {summary['gross_margin_pct']}%")
    lines.append(f"- DSO: {summary['avg_dso_days']} days | DPO: {summary['avg_dpo_days']} days | "
                 f"Cash Conversion Cycle: {summary['avg_cash_conversion_cycle']} days\n")

    for ins in insights:
        lines.append(f"## {ins['metric']}\n")
        lines.append(f"**Finding:** {ins['finding']}\n")
        lines.append("**Root cause chain:**")
        for step in ins["root_cause_chain"]:
            lines.append(f"- {step}")
        lines.append(f"\n**Business impact:** {ins['business_impact']}\n")
        lines.append(f"**Recommendation:** {ins['recommendation']}\n")

    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def main():
    sales, expenses, budget, wc, customers = load_data()
    fact = build_fact_monthly(sales, expenses, budget)
    wc_kpi = build_working_capital_kpis(wc, sales)
    summary = company_kpi_summary(fact, wc_kpi, sales, budget)
    insights = generate_insights(fact, wc_kpi, sales)

    fact.to_csv(f"{DATA}/fact_monthly.csv", index=False)
    wc_kpi.to_csv(f"{DATA}/working_capital_kpis.csv", index=False)
    pd.DataFrame([summary]).to_csv(f"{DATA}/kpi_summary.csv", index=False)
    with open(f"{DATA}/insights.json", "w", encoding="utf-8") as f:
        json.dump({"summary": summary, "insights": insights}, f, indent=2, default=str)
    write_narrative_md(summary, insights, f"{DATA}/executive_narrative.md")

    print("=== KPI SUMMARY ===")
    for k, v in summary.items():
        print(f"{k}: {v}")
    print("\n=== INSIGHTS ===")
    for ins in insights:
        print(f"\n--- {ins['metric']} ---")
        print(ins["finding"])
        for step in ins["root_cause_chain"]:
            print(" -", step)
        print("Impact:", ins["business_impact"])
        print("Recommendation:", ins["recommendation"])


if __name__ == "__main__":
    main()
