# 6. KPIs and how to calculate them

All SQL runs on the schema from the analytics project (`customers`, `products`, `invoices`, `invoice_items`) plus
one new table and one view for the campaign (DR-03). It is written for SQLite, like the analytics repo, with the
PostgreSQL equivalents noted inline. Every query was checked on a small test data set (see the end of this page).

**Shared definitions (from the BRD)**
- **Sale:** a line on a non-cancelled invoice with revenue above zero (DR-01).
- **Reactivated:** at least one sale from the campaign start date up to, but not including, day 90 (DR-02).

## 6.1 KPI summary

| ID | KPI | Baseline | Target | How often | Owner |
|---|---|---|---|---|---|
| KPI-1 | At-Risk customers: count and lifetime revenue | 888 customers, £2.19M | Falls over time | Weekly | BI Analyst |
| KPI-2 | Reactivation rate, treatment vs control (90 days) | Unknown; the control group measures it | Uplift of +5 points or more | Weekly until day 90 | CRM Manager |
| KPI-3 | Uplift and incremental revenue (90 days) | n/a | Incremental revenue at least 3x the discount cost | Day 90 | Finance Manager |
| KPI-4 | Share of sales with no customer ID | ~14% (£2.94M of £20.48M) | Under 5% within 6 months of release | Monthly | Web Product Owner |
| KPI-5 | Month-1 retention (context for phase 2) | 21.2% average across cohorts | Track only | Monthly | BI Analyst |

**Guardrails** (from the email platform and web analytics, no SQL): unsubscribe rate under 0.5% per email; spam
complaint rate under 0.1%; checkout completion not down by more than 1 point (NFR-05); discount redemption rate
(for information).

## 6.2 New table and view for the campaign

```sql
-- @name: winback_tables
-- DR-03: one row per customer per campaign batch, written once before any email is sent.
CREATE TABLE winback_audience (
    campaign_id   TEXT    NOT NULL,                  -- e.g. 'WB-2012-01'
    customer_id   BIGINT  NOT NULL REFERENCES customers(customer_id),
    group_name    TEXT    NOT NULL CHECK (group_name IN ('treatment', 'control')),
    start_date    DATE    NOT NULL,                  -- day email 1 goes out (control: same day, no email)
    rules_version TEXT    NOT NULL,                  -- NFR-04: which audience rules produced this row
    PRIMARY KEY (campaign_id, customer_id)
);

-- One row per audience member: their sales in the 90-day window (DR-01, DR-02).
CREATE VIEW winback_customer_90d AS
SELECT a.campaign_id,
       a.group_name,
       a.customer_id,
       COUNT(DISTINCT it.invoice_no) AS orders_90d,     -- only invoices with at least one sale line
       COALESCE(SUM(it.revenue), 0)  AS revenue_90d
FROM winback_audience a
LEFT JOIN invoices i
       ON i.customer_id   = a.customer_id
      AND i.is_cancelled  = 0
      AND i.invoice_date >= a.start_date
      AND i.invoice_date <  date(a.start_date, '+90 days')   -- Postgres: a.start_date + INTERVAL '90 days'
LEFT JOIN invoice_items it
       ON it.invoice_no = i.invoice_no
      AND it.revenue    > 0
GROUP BY a.campaign_id, a.group_name, a.customer_id;
```

## 6.3 KPI-1: At-Risk customers

The audience source for FR-04 (before the consent and suppression checks). KPI-1 is the number of rows and the
sum of `monetary`. Same rules as the analysis, plus the FR-02 tie-break on `customer_id`. Because of that
tie-break, the count can differ by a few customers from the published 888.

```sql
-- @name: at_risk_customers
WITH snapshot AS (
    SELECT MAX(invoice_date) AS snap FROM invoices WHERE is_cancelled = 0
),
rfm AS (
    SELECT i.customer_id,
           MAX(i.invoice_date)                               AS last_order_date,
           CAST(julianday((SELECT snap FROM snapshot))
                - julianday(MAX(i.invoice_date)) AS INTEGER) AS recency_days,  -- Postgres: snap::date - MAX(i.invoice_date)::date
           COUNT(DISTINCT i.invoice_no)                      AS frequency,
           ROUND(SUM(it.revenue), 2)                         AS monetary
    FROM invoices i
    JOIN invoice_items it USING (invoice_no)
    WHERE i.is_cancelled = 0
      AND i.customer_id IS NOT NULL
      AND it.revenue > 0
    GROUP BY i.customer_id
),
scored AS (
    SELECT *,
           NTILE(4) OVER (ORDER BY recency_days DESC, customer_id) AS r_score,  -- FR-02: tie-break
           NTILE(4) OVER (ORDER BY frequency    ASC,  customer_id) AS f_score
    FROM rfm
)
SELECT customer_id, last_order_date, recency_days, frequency, monetary, r_score, f_score
FROM scored
WHERE r_score <= 2
  AND f_score >= 3
ORDER BY monetary DESC, customer_id;
```

## 6.4 KPI-2: reactivation rate by group

```sql
-- @name: campaign_results
SELECT campaign_id,
       group_name,
       COUNT(*)                                           AS customers,
       SUM(CASE WHEN orders_90d > 0 THEN 1 ELSE 0 END)    AS reactivated,
       ROUND(100.0 * SUM(CASE WHEN orders_90d > 0 THEN 1 ELSE 0 END) / COUNT(*), 1)
                                                          AS reactivation_rate_pct,
       ROUND(SUM(revenue_90d), 2)                         AS revenue_90d,
       ROUND(SUM(revenue_90d) * 1.0 / COUNT(*), 2)        AS revenue_per_customer
FROM winback_customer_90d
GROUP BY campaign_id, group_name
ORDER BY campaign_id, group_name;
```

## 6.5 KPI-3: uplift and incremental revenue

- **Uplift** = treatment reactivation rate − control reactivation rate (percentage points).
- **Incremental revenue** = (treatment revenue per customer − control revenue per customer) × treatment customers.

Comparing per-customer averages, rather than totals, keeps the 90% / 10% group sizes from distorting the result.

```sql
-- @name: campaign_uplift
WITH by_group AS (
    SELECT campaign_id,
           group_name,
           COUNT(*)                                          AS customers,
           AVG(CASE WHEN orders_90d > 0 THEN 1.0 ELSE 0 END) AS reactivation_rate,
           AVG(revenue_90d * 1.0)                            AS revenue_per_customer
    FROM winback_customer_90d
    GROUP BY campaign_id, group_name
)
SELECT t.campaign_id,
       ROUND(100 * (t.reactivation_rate - c.reactivation_rate), 1)                AS uplift_pct_points,
       ROUND((t.revenue_per_customer - c.revenue_per_customer) * t.customers, 2) AS incremental_revenue_90d
FROM by_group t
JOIN by_group c
  ON c.campaign_id = t.campaign_id
 AND c.group_name  = 'control'
WHERE t.group_name = 'treatment';
```

## 6.6 KPI-4: share of sales with no customer ID

```sql
-- @name: unattributed_sales_share
SELECT strftime('%Y-%m', i.invoice_date)  AS month,   -- Postgres: to_char(i.invoice_date, 'YYYY-MM')
       ROUND(SUM(it.revenue), 2)          AS sales,
       ROUND(SUM(CASE WHEN i.customer_id IS NULL THEN it.revenue ELSE 0 END), 2)
                                          AS sales_without_customer_id,
       ROUND(100.0 * SUM(CASE WHEN i.customer_id IS NULL THEN it.revenue ELSE 0 END)
             / SUM(it.revenue), 1)        AS unattributed_pct
FROM invoices i
JOIN invoice_items it USING (invoice_no)
WHERE i.is_cancelled = 0
  AND it.revenue > 0
GROUP BY month
ORDER BY month;
```

## 6.7 KPI-5: month-1 retention (context for phase 2)

The share of each monthly cohort that orders again in the next calendar month. The latest cohort is left out
because its next month isn't in the data yet.

```sql
-- @name: month1_retention
WITH first_purchase AS (
    SELECT customer_id, MIN(invoice_date) AS first_dt
    FROM invoices
    WHERE is_cancelled = 0 AND customer_id IS NOT NULL
    GROUP BY customer_id
),
activity AS (
    SELECT DISTINCT
           fp.customer_id,
           strftime('%Y-%m', fp.first_dt) AS cohort_month,     -- Postgres: to_char(fp.first_dt, 'YYYY-MM')
           (CAST(strftime('%Y', i.invoice_date) AS INTEGER) * 12 + CAST(strftime('%m', i.invoice_date) AS INTEGER))
         - (CAST(strftime('%Y', fp.first_dt)    AS INTEGER) * 12 + CAST(strftime('%m', fp.first_dt)    AS INTEGER))
                                          AS month_index
    FROM invoices i
    JOIN first_purchase fp USING (customer_id)
    WHERE i.is_cancelled = 0
)
SELECT cohort_month,
       COUNT(DISTINCT CASE WHEN month_index = 0 THEN customer_id END) AS cohort_size,
       COUNT(DISTINCT CASE WHEN month_index = 1 THEN customer_id END) AS ordered_next_month,
       ROUND(100.0 * COUNT(DISTINCT CASE WHEN month_index = 1 THEN customer_id END)
             / COUNT(DISTINCT CASE WHEN month_index = 0 THEN customer_id END), 1)
                                                                      AS month1_retention_pct
FROM activity
WHERE cohort_month < (SELECT strftime('%Y-%m', MAX(invoice_date)) FROM invoices WHERE is_cancelled = 0)
GROUP BY cohort_month
ORDER BY cohort_month;
```

## 6.8 How the SQL was checked

[`checks/check_kpi_sql.py`](checks/check_kpi_sql.py) runs every query on this page against an in-memory SQLite
database with the analytics schema and a small hand-made data set. The data set has 8 customers with known recency
and frequency, a cancelled invoice, a return line, a guest order, and a test campaign with 3 treatment and 2 control
customers. It needs only Python's standard library:

```bash
python checks/check_kpi_sql.py
```

Expected results, worked out by hand:
- **KPI-1** returns exactly customers 5 and 8, and matches a plain-Python version of the scoring. Customers 4, 6
  and 8 all have 2 orders, across a quartile boundary; only the customer-ID tie-break (FR-02) puts customer 8 in
  At-Risk.
- **KPI-2**: treatment 2 of 3 reactivated (66.7%), control 1 of 2 (50.0%). An order on day 90, a return-only
  invoice and a cancelled order are all ignored.
- **KPI-3**: uplift 16.7 points; incremental revenue 90.00.
- **KPI-4** and **KPI-5** match an independent calculation in plain Python.
