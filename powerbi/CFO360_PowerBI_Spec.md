# CFO360 — Power BI Dashboard Spec

This is a build spec, not a finished `.pbix` — Power BI Desktop isn't available
in this environment, but everything below is copy-pasteable: Power Query
steps, DAX measures (`dax_measures.dax`, same folder), and exact page/visual
layouts. Following it end-to-end produces the dashboard described in the
brief.

## 1. Data model (star schema)

```
              DimDate
             /   |   \
   DimRegion  FactSales  DimProduct
             \   |   /
        DimBusinessUnit   DimCustomer
                |
   FactExpenses · FactBudget · FactWorkingCapital
   (all connect to DimDate + DimRegion + DimBusinessUnit)
```

One fact table per source CSV, one dimension table per shared attribute.
This is what lets a single region/date slicer filter revenue, EBITDA,
budget variance, and DSO simultaneously.

### Get Data steps

1. **Home → Get Data → Text/CSV**, load each of:
   `sales_clean.csv`, `expenses_clean.csv`, `budget_clean.csv`,
   `working_capital_clean.csv`, `customers_clean.csv` from the `data/`
   folder (or connect directly to Postgres via **Get Data → PostgreSQL
   database** and point at the `v_fact_monthly` view + raw tables from
   `sql/schema.sql` if you built the SQL layer).
2. In Power Query Editor, rename queries: `FactSales`, `FactExpenses`,
   `FactBudget`, `FactWorkingCapital`, `DimCustomer`.

### Power Query (M) transformations

**FactSales** — after load:
```
= Table.TransformColumnTypes(Source, {
    {"date", type date}, {"revenue", type number},
    {"units_sold", Int64.Type}, {"discount", type number}
})
```

**Build DimDate** (Home → New Source → Blank Query, then Advanced Editor):
```m
let
    StartDate = #date(2024, 1, 1),
    EndDate = #date(2026, 12, 31),
    DayCount = Duration.Days(EndDate - StartDate) + 1,
    Dates = List.Dates(StartDate, DayCount, #duration(1,0,0,0)),
    #"Converted to Table" = Table.FromList(Dates, Splitter.SplitByNothing(), {"date"}),
    #"Added Year" = Table.AddColumn(#"Converted to Table", "Year", each Date.Year([date])),
    #"Added Month" = Table.AddColumn(#"Added Year", "Month", each Date.Month([date])),
    #"Added MonthName" = Table.AddColumn(#"Added Month", "MonthName", each Date.ToText([date], "MMM yyyy")),
    #"Added Quarter" = Table.AddColumn(#"Added MonthName", "Quarter", each "Q" & Text.From(Date.QuarterOfYear([date])) & " " & Text.From(Date.Year([date]))),
    #"Added MonthStart" = Table.AddColumn(#"Added Quarter", "MonthStart", each Date.StartOfMonth([date]))
in
    #"Added MonthStart"
```
Mark this table as a **Date Table** (Table tools → Mark as Date Table →
`date` column) — required for `DATEADD`/`SAMEPERIODLASTYEAR` in the DAX
measures to work correctly.

**Build DimRegion / DimBusinessUnit / DimProduct** — Reference `FactSales`,
then: `Home → Remove Columns → keep only region` (or `business_unit` /
`product`) → `Remove Duplicates`. Repeat for each.

### Relationships (Model view)

| From | To | Cardinality | Cross-filter |
|---|---|---|---|
| FactSales[date] | DimDate[date] | Many-to-one | Single |
| FactSales[region] | DimRegion[region] | Many-to-one | Single |
| FactSales[business_unit] | DimBusinessUnit[business_unit] | Many-to-one | Single |
| FactSales[product] | DimProduct[product] | Many-to-one | Single |
| FactSales[customer_id] | DimCustomer[customer_id] | Many-to-one | Single |
| FactExpenses[date] | DimDate[date] | Many-to-one | Single |
| FactExpenses[region], [business_unit] | DimRegion, DimBusinessUnit | Many-to-one | Single |
| FactBudget[month] | DimDate[MonthStart] | Many-to-one | Single |
| FactBudget[region], [business_unit] | DimRegion, DimBusinessUnit | Many-to-one | Single |
| FactWorkingCapital[date] | DimDate[MonthStart] | Many-to-one | Single |
| FactWorkingCapital[region] | DimRegion | Many-to-one | Single |

All fact tables stay ungrouped (no relationships between fact tables
directly) — that's what avoids ambiguous filter paths.

## 2. DAX measures

See [`dax_measures.dax`](dax_measures.dax) in this folder — 7 groups
(Revenue, Profitability, Budget/Variance, Cost, Working Capital,
Root-cause helpers, Formatting). Create a disconnected `_Measures` table
to hold them (Home → Enter Data → one dummy column → delete the column
after moving measures into the table) so they don't clutter a real table
in the Fields list.

## 3. Report pages

Five pages, one slicer panel (Region, Business Unit, Product, Date range)
pinned on the left of every page via a **Sync Slicers** setup.

### Page 1 — Executive Summary

| Visual | Fields | Notes |
|---|---|---|
| 6 KPI cards (top row) | `Revenue (Cr)`, `EBITDA (Cr)`, `EBITDA Margin %`, `Revenue Growth %`, `Revenue Variance %`, `DSO (days)` | Use conditional formatting: red if `Revenue Variance % < -0.05`, green if `> 0` |
| Line chart | `Total Revenue` by `DimDate[MonthStart]`, split by `DimRegion[region]` | Shows the North divergence visually |
| Combo chart | `Total Revenue` (columns) vs `Budget Revenue` (line) by month | The "actual vs budget" story at a glance |
| Text card ("Key insight") | Bound to `insights.json` narrative (see §4) | This is the differentiator — not just numbers |

### Page 2 — Revenue

| Visual | Fields |
|---|---|
| Bar chart | `Revenue by Region` |
| Bar chart | `Revenue by Product` |
| Line chart | `Total Revenue` trend by month, all regions overlaid |
| Matrix | Region (rows) × Month (columns), `Revenue Variance %` (values), with color scale |
| Slicer | Product, Business Unit |

### Page 3 — Costs

| Visual | Fields |
|---|---|
| Donut/bar | `Cost by Category` (COGS, Employee, Marketing, Technology, Operations) |
| Line chart | `Total Expenses` vs `Budget Expense` by month |
| KPI card | `Cost Variance %`, `Expense Growth %` |
| Table | Region × Business Unit × `Cost % of Revenue` |

### Page 4 — Profitability

| Visual | Fields |
|---|---|
| Waterfall | Revenue → COGS → Gross Profit → OpEx → EBITDA (single period) |
| Line chart | `Gross Margin %` and `EBITDA Margin %` trend, dual axis |
| Matrix | Region × Product, `EBITDA Margin %` heatmap |

### Page 5 — Working Capital

| Visual | Fields |
|---|---|
| KPI cards | `DSO (days)`, `DPO (days)`, `Cash Conversion Cycle` |
| Line chart | DSO trend by region — this is where the North/East story shows up |
| Bar chart | `Accounts Receivable`, `Accounts Payable`, `Inventory` by region |
| Card | `DSO Change (days)` with conditional icon (▲ red if worsening) |

## 4. Surfacing the root-cause narrative in Power BI (not just Python)

Two options, both worth having in the portfolio:

**Option A — DAX-native drillthrough page.** Build a hidden page
"Why?" with:
- `Worst Region (Revenue Variance)` and `Discount Change (pts)` as cards
- Right-click any region bar on Page 2 → **Drillthrough → Why?** — Power
  BI auto-filters the page to that region and the cards recompute live.
  This reproduces the Python insight engine's logic natively in DAX.

**Option B — Python-generated narrative as a Power BI visual.** Import
`data/executive_narrative.md` text or `insights.json` as a table
(`Get Data → JSON`), flatten it, and drop it into a **Text Box** or
**Card with categorical narrative** visual on Page 1, so the automatically
generated recommendation ("Freeze further discount escalation on Product B
in North…") sits directly next to the chart it explains. This is the
"Deloitte-level" touch the brief calls out — the dashboard doesn't just
show the drop, it tells you why and what to do.

Recommend doing both: Option A for interactivity, Option B for the
one-glance executive view.

## 5. Formatting / theme

- Import a theme JSON (View → Themes → Browse for themes) using a
  neutral palette: dark navy (`#1a2b4c`) for primary, muted red
  (`#c0392b`) for negative variance, muted green (`#27824a`) for positive.
- Use `Revenue (Cr)` and equivalents everywhere instead of raw INR —
  matches how the brief's example dashboard displays numbers.
- Card visuals: 1 decimal place for Cr values, 1 decimal for %, 0
  decimals for days.

## 6. Publishing

```
Home → Publish → Power BI Service → CFO360 workspace
```
Then set up a **scheduled refresh** if the source is Postgres (via an
on-premises data gateway), or re-publish manually if the source is the
static CSVs — worth mentioning either way in an interview since it shows
you understand the refresh story, not just the visuals.
