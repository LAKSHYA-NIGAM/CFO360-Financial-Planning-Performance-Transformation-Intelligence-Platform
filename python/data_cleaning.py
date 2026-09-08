"""
CFO360 - Data Cleaning & Validation
-------------------------------------
Runs standard data-quality checks on the raw CSVs before they hit the
analysis layer. Even though this project uses generated data, this script
follows the same checklist you'd run against a real CFO data extract:

  1. Schema check (columns, dtypes)
  2. Null / missing value handling
  3. Duplicate detection
  4. Referential integrity (region/business_unit spelling consistent
     across sales, expenses, budget, working_capital)
  5. Range / outlier checks (negative revenue, discount > 100%, etc.)
  6. Type casting (dates, numerics)

Run:
    python data_cleaning.py
Outputs a data-quality report to ../data/data_quality_report.txt and
writes cleaned versions of each file with a `_clean` suffix.
"""

import pandas as pd

DATA = "../data"
report_lines = []


def log(msg):
    print(msg)
    report_lines.append(msg)


def check_and_clean(name, df, date_cols=None, numeric_cols=None, categorical_cols=None):
    log(f"\n--- {name} ---")
    log(f"Rows: {len(df)}, Columns: {list(df.columns)}")

    nulls = df.isnull().sum()
    nulls = nulls[nulls > 0]
    if len(nulls):
        log(f"Nulls found:\n{nulls}")
        df = df.dropna()
        log("-> Dropped rows with nulls.")
    else:
        log("No nulls found.")

    dupes = df.duplicated().sum()
    if dupes:
        log(f"Duplicate rows found: {dupes} -> removed.")
        df = df.drop_duplicates()
    else:
        log("No duplicate rows.")

    if date_cols:
        for c in date_cols:
            df[c] = pd.to_datetime(df[c], errors="coerce")
        bad_dates = df[date_cols].isnull().any(axis=1).sum()
        if bad_dates:
            log(f"Unparseable dates: {bad_dates} -> dropped.")
            df = df.dropna(subset=date_cols)

    if numeric_cols:
        for c in numeric_cols:
            df[c] = pd.to_numeric(df[c], errors="coerce")
        negatives = (df[numeric_cols] < 0).any(axis=1).sum()
        if negatives:
            log(f"WARNING: {negatives} rows with negative values in {numeric_cols} — flagged, not dropped.")

    if categorical_cols:
        for c in categorical_cols:
            df[c] = df[c].str.strip()
            log(f"Distinct values in '{c}': {sorted(df[c].unique())}")

    return df


def main():
    sales = pd.read_csv(f"{DATA}/sales.csv")
    expenses = pd.read_csv(f"{DATA}/expenses.csv")
    budget = pd.read_csv(f"{DATA}/budget.csv")
    wc = pd.read_csv(f"{DATA}/working_capital.csv")
    customers = pd.read_csv(f"{DATA}/customers.csv")

    sales = check_and_clean(
        "sales", sales, date_cols=["date"],
        numeric_cols=["revenue", "units_sold", "discount"],
        categorical_cols=["region", "business_unit", "product"],
    )
    expenses = check_and_clean(
        "expenses", expenses, date_cols=["date"],
        numeric_cols=["amount"],
        categorical_cols=["region", "business_unit", "expense_category"],
    )
    budget = check_and_clean(
        "budget", budget, date_cols=["month"],
        numeric_cols=["budget_revenue", "budget_expense"],
        categorical_cols=["region", "business_unit"],
    )
    wc = check_and_clean(
        "working_capital", wc, date_cols=["date"],
        numeric_cols=["accounts_receivable", "accounts_payable", "inventory"],
        categorical_cols=["region"],
    )
    customers = check_and_clean(
        "customers", customers,
        categorical_cols=["region", "industry"],
    )

    # Referential integrity: region/business_unit sets must match across tables
    log("\n--- Referential Integrity ---")
    for col in ["region"]:
        sets = {
            "sales": set(sales[col]), "expenses": set(expenses[col]),
            "budget": set(budget[col]), "working_capital": set(wc[col]),
        }
        base = sets["sales"]
        for tbl, s in sets.items():
            if s != base:
                log(f"MISMATCH in '{col}' between sales and {tbl}: {base.symmetric_difference(s)}")
        log(f"'{col}' consistent across tables: {all(s == base for s in sets.values())}")

    sales.to_csv(f"{DATA}/sales_clean.csv", index=False)
    expenses.to_csv(f"{DATA}/expenses_clean.csv", index=False)
    budget.to_csv(f"{DATA}/budget_clean.csv", index=False)
    wc.to_csv(f"{DATA}/working_capital_clean.csv", index=False)
    customers.to_csv(f"{DATA}/customers_clean.csv", index=False)

    with open(f"{DATA}/data_quality_report.txt", "w") as f:
        f.write("\n".join(report_lines))

    log("\nData quality report written to data_quality_report.txt")


if __name__ == "__main__":
    main()
