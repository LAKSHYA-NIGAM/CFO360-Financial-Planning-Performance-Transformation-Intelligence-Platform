"""
CFO360 - Synthetic Data Generator for NexaTech Industries
-----------------------------------------------------------
Generates 3 years (2024-01 to 2026-08) of monthly financial data across
4 regions x 5 business units x 4 product categories, with:

  - Real revenue growth trend + seasonality
  - A deliberately embedded root-cause story:
      North region has been increasing discounts on Product B since
      mid-2025 to defend volume against a competitor, which erodes both
      revenue and margin there -> shows up as a budget miss traceable
      to region -> product -> discount driver.
  - A deliberately embedded working-capital story:
      Accounts Receivable collection has been slipping (DSO rising)
      because North and East regions extended payment terms to a few
      large enterprise customers -> cash conversion cycle lengthens
      even though revenue is growing.

Output (all in ../data/):
  sales.csv, expenses.csv, budget.csv, working_capital.csv, customers.csv
"""

import numpy as np
import pandas as pd
from datetime import date

rng = np.random.default_rng(42)

REGIONS = ["North", "South", "East", "West"]
BUSINESS_UNITS = [
    "Consulting Services",
    "Cloud Infrastructure",
    "Managed IT Support",
    "Software Products",
    "Data & Analytics",
]
PRODUCTS = ["Product A", "Product B", "Product C", "Product D"]

MONTHS = pd.date_range("2024-01-01", "2026-08-01", freq="MS")  # 32 months

# ---- Regional base strength (relative revenue index) ----
REGION_BASE = {"North": 1.15, "South": 1.00, "East": 0.85, "West": 0.95}

# ---- Product base revenue share and margin profile ----
PRODUCT_BASE = {
    "Product A": {"share": 0.32, "cogs_pct": 0.42},
    "Product B": {"share": 0.28, "cogs_pct": 0.50},
    "Product C": {"share": 0.22, "cogs_pct": 0.55},
    "Product D": {"share": 0.18, "cogs_pct": 0.60},
}

BU_LIST = BUSINESS_UNITS

# ---- Customers ----
N_CUSTOMERS = 120
INDUSTRIES = ["BFSI", "Retail", "Healthcare", "Manufacturing", "Telecom", "Public Sector"]
customers = pd.DataFrame({
    "customer_id": [f"CUST{str(i).zfill(4)}" for i in range(1, N_CUSTOMERS + 1)],
    "customer_name": [f"Client {i}" for i in range(1, N_CUSTOMERS + 1)],
    "industry": rng.choice(INDUSTRIES, N_CUSTOMERS),
    "region": rng.choice(REGIONS, N_CUSTOMERS, p=[0.3, 0.25, 0.2, 0.25]),
})
customers.to_csv("../data/customers.csv", index=False)


def month_index(m):
    """Months since 2024-01 (0-based), used to drive trend/seasonality."""
    return (m.year - 2024) * 12 + (m.month - 1)


def north_product_b_discount(m):
    """Discount % for North/Product B: starts ~8%, climbs to ~28% from mid-2025."""
    idx = month_index(m)
    if m < pd.Timestamp("2025-06-01"):
        return 0.08 + idx * 0.003
    else:
        ramp = month_index(m) - month_index(pd.Timestamp("2025-06-01"))
        return min(0.10 + ramp * 0.018, 0.30)


def base_discount(region, product, m):
    if region == "North" and product == "Product B":
        return north_product_b_discount(m)
    return float(np.clip(rng.normal(0.07, 0.02), 0.02, 0.15))


sales_rows = []
expense_rows = []
budget_rows = []
wc_rows = []

sale_id_counter = 1
expense_id_counter = 1
budget_id_counter = 1

TOTAL_MONTHLY_REVENUE_BASE = 18.5  # in Cr, starting point company-wide

for m in MONTHS:
    idx = month_index(m)
    # overall company growth trend (~1.1%/month compounding) + seasonality (Q4 bump, Q1 dip)
    trend = (1.011) ** idx
    seasonality = 1.0 + 0.06 * np.sin((m.month - 1) / 12 * 2 * np.pi + 1.2)
    company_revenue_target = TOTAL_MONTHLY_REVENUE_BASE * trend * seasonality

    for region in REGIONS:
        region_factor = REGION_BASE[region]

        # North's growth throttles down from mid-2025 onward because of the
        # Product B discount story eating into realized revenue.
        region_growth_drag = 1.0
        if region == "North" and m >= pd.Timestamp("2025-06-01"):
            drag_idx = month_index(m) - month_index(pd.Timestamp("2025-06-01"))
            region_growth_drag = max(1.0 - drag_idx * 0.012, 0.75)

        for bu in BU_LIST:
            bu_factor = rng.uniform(0.85, 1.15)

            for product in PRODUCTS:
                p = PRODUCT_BASE[product]
                base_amt = (
                    company_revenue_target
                    * region_factor
                    * p["share"]
                    * bu_factor
                    / len(BU_LIST)
                    * region_growth_drag
                )
                noise = rng.normal(1.0, 0.06)
                gross_target = max(base_amt * noise, 0.02)  # Cr, pre-discount list revenue

                disc = base_discount(region, product, m)
                net_revenue_cr = gross_target * (1 - disc)

                # split this region/bu/product/month revenue into 3-6 transactions
                n_txn = rng.integers(3, 7)
                weights = rng.dirichlet(np.ones(n_txn))
                cust_pool = customers[customers.region == region].customer_id.values
                if len(cust_pool) == 0:
                    cust_pool = customers.customer_id.values

                for w in weights:
                    txn_revenue_cr = net_revenue_cr * w
                    txn_revenue = round(txn_revenue_cr * 1e7, 2)  # convert Cr -> INR
                    units = max(int(txn_revenue / rng.uniform(15000, 45000)), 1)
                    day = rng.integers(1, 28)
                    sales_rows.append({
                        "sale_id": f"SALE{str(sale_id_counter).zfill(6)}",
                        "date": date(m.year, m.month, day),
                        "region": region,
                        "business_unit": bu,
                        "product": product,
                        "customer_id": rng.choice(cust_pool),
                        "revenue": txn_revenue,
                        "units_sold": units,
                        "discount": round(float(disc), 4),
                    })
                    sale_id_counter += 1

                # ---- COGS (expense row, category = COGS) ----
                cogs_amt = round(net_revenue_cr * p["cogs_pct"] * 1e7, 2)
                expense_rows.append({
                    "expense_id": f"EXP{str(expense_id_counter).zfill(6)}",
                    "date": date(m.year, m.month, 28),
                    "region": region,
                    "business_unit": bu,
                    "expense_category": "COGS",
                    "amount": cogs_amt,
                })
                expense_id_counter += 1

            # ---- Operating expenses per region/BU (once per BU per month) ----
            for cat, pct_of_bu_rev in [
                ("Employee Costs", 0.22),
                ("Marketing", 0.06),
                ("Technology & Infra", 0.05),
                ("Operations & Admin", 0.04),
            ]:
                bu_month_revenue = sum(
                    r["revenue"] for r in sales_rows
                    if r["business_unit"] == bu and r["region"] == region
                    and r["date"].year == m.year and r["date"].month == m.month
                )
                amt = round(bu_month_revenue * pct_of_bu_rev * rng.uniform(0.9, 1.1), 2)
                expense_rows.append({
                    "expense_id": f"EXP{str(expense_id_counter).zfill(6)}",
                    "date": date(m.year, m.month, 28),
                    "region": region,
                    "business_unit": bu,
                    "expense_category": cat,
                    "amount": amt,
                })
                expense_id_counter += 1

            # ---- Budget: regions/months with the Product B discount problem
            # get a materially harder budget (management didn't see it coming),
            # so North shows a genuine, investigable miss from mid-2025 onward.
            bu_month_revenue_total = sum(
                r["revenue"] for r in sales_rows
                if r["business_unit"] == bu and r["region"] == region
                and r["date"].year == m.year and r["date"].month == m.month
            )
            budget_revenue = round(bu_month_revenue_total * rng.uniform(1.03, 1.07)
                                    if not (region == "North" and m >= pd.Timestamp("2025-06-01"))
                                    else bu_month_revenue_total * rng.uniform(1.12, 1.20), 2)
            bu_month_expense_total = sum(
                e["amount"] for e in expense_rows
                if e["business_unit"] == bu and e["region"] == region
                and e["date"].year == m.year and e["date"].month == m.month
            )
            budget_expense = round(bu_month_expense_total * rng.uniform(0.95, 1.02), 2)

            budget_rows.append({
                "budget_id": f"BUD{str(budget_id_counter).zfill(6)}",
                "month": date(m.year, m.month, 1),
                "region": region,
                "business_unit": bu,
                "budget_revenue": budget_revenue,
                "budget_expense": budget_expense,
            })
            budget_id_counter += 1

    # ---- Working capital (once per region per month) ----
    for region in REGIONS:
        month_region_revenue = sum(
            r["revenue"] for r in sales_rows
            if r["region"] == region and r["date"].year == m.year and r["date"].month == m.month
        )
        # DSO story: North & East stretch out from mid-2025 (extended terms to big clients)
        dso_days = 45
        if region in ("North", "East") and m >= pd.Timestamp("2025-06-01"):
            drag_idx = month_index(m) - month_index(pd.Timestamp("2025-06-01"))
            dso_days = 45 + drag_idx * 1.6
        dso_days = min(dso_days, 78) + rng.normal(0, 2)

        dpo_days = 38 + rng.normal(0, 2)

        ar = round(month_region_revenue * (dso_days / 30), 2)
        ap = round(month_region_revenue * 0.55 * (dpo_days / 30), 2)
        inventory = round(month_region_revenue * 0.12 * rng.uniform(0.9, 1.1), 2)

        wc_rows.append({
            "date": date(m.year, m.month, 1),
            "region": region,
            "accounts_receivable": ar,
            "accounts_payable": ap,
            "inventory": inventory,
        })

sales = pd.DataFrame(sales_rows)
expenses = pd.DataFrame(expense_rows)
budget = pd.DataFrame(budget_rows)
working_capital = pd.DataFrame(wc_rows)

sales.to_csv("../data/sales.csv", index=False)
expenses.to_csv("../data/expenses.csv", index=False)
budget.to_csv("../data/budget.csv", index=False)
working_capital.to_csv("../data/working_capital.csv", index=False)

print("sales:", sales.shape)
print("expenses:", expenses.shape)
print("budget:", budget.shape)
print("working_capital:", working_capital.shape)
print("customers:", customers.shape)
print("Total revenue (Cr):", round(sales.revenue.sum() / 1e7, 1))
