-- CFO360 / NexaTech Industries — PostgreSQL schema
-- Run: psql -d cfo360 -f schema.sql

DROP TABLE IF EXISTS sales, expenses, budget, working_capital, customers CASCADE;

CREATE TABLE customers (
    customer_id     VARCHAR(10) PRIMARY KEY,
    customer_name   VARCHAR(100) NOT NULL,
    industry        VARCHAR(50),
    region          VARCHAR(20) NOT NULL
);

CREATE TABLE sales (
    sale_id         VARCHAR(12) PRIMARY KEY,
    date            DATE NOT NULL,
    region          VARCHAR(20) NOT NULL,
    business_unit   VARCHAR(50) NOT NULL,
    product         VARCHAR(20) NOT NULL,
    customer_id     VARCHAR(10) REFERENCES customers(customer_id),
    revenue         NUMERIC(14,2) NOT NULL CHECK (revenue >= 0),
    units_sold      INTEGER NOT NULL CHECK (units_sold >= 0),
    discount        NUMERIC(5,4) NOT NULL CHECK (discount BETWEEN 0 AND 1)
);

CREATE TABLE expenses (
    expense_id       VARCHAR(12) PRIMARY KEY,
    date             DATE NOT NULL,
    region           VARCHAR(20) NOT NULL,
    business_unit    VARCHAR(50) NOT NULL,
    expense_category VARCHAR(30) NOT NULL,
    amount           NUMERIC(14,2) NOT NULL CHECK (amount >= 0)
);

CREATE TABLE budget (
    budget_id       VARCHAR(12) PRIMARY KEY,
    month           DATE NOT NULL,
    region          VARCHAR(20) NOT NULL,
    business_unit   VARCHAR(50) NOT NULL,
    budget_revenue  NUMERIC(14,2) NOT NULL,
    budget_expense  NUMERIC(14,2) NOT NULL,
    UNIQUE (month, region, business_unit)
);

CREATE TABLE working_capital (
    date                  DATE NOT NULL,
    region                VARCHAR(20) NOT NULL,
    accounts_receivable   NUMERIC(14,2) NOT NULL,
    accounts_payable      NUMERIC(14,2) NOT NULL,
    inventory             NUMERIC(14,2) NOT NULL,
    PRIMARY KEY (date, region)
);

CREATE INDEX idx_sales_month_region ON sales (date, region, business_unit, product);
CREATE INDEX idx_expenses_month_region ON expenses (date, region, business_unit, expense_category);
CREATE INDEX idx_budget_month_region ON budget (month, region, business_unit);

-- Loading (adjust paths as needed):
-- \copy customers FROM '../data/customers_clean.csv' CSV HEADER
-- \copy sales FROM '../data/sales_clean.csv' CSV HEADER
-- \copy expenses FROM '../data/expenses_clean.csv' CSV HEADER
-- \copy budget FROM '../data/budget_clean.csv' CSV HEADER
-- \copy working_capital FROM '../data/working_capital_clean.csv' CSV HEADER
