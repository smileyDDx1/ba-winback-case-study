"""Check the KPI SQL in 06-kpis.md on a small hand-made data set.

Run from the repo root:   python checks/check_kpi_sql.py

Uses only the Python standard library (sqlite3, in memory), so nothing is written to disk.
The expected answers below were worked out by hand; see section 6.8 of 06-kpis.md.
"""
import re
import sqlite3
import sys
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Same tables as ecommerce-analytics/sql/schema.sql
SCHEMA = """
CREATE TABLE customers (customer_id BIGINT PRIMARY KEY, country TEXT NOT NULL);
CREATE TABLE products  (stock_code TEXT PRIMARY KEY, description TEXT);
CREATE TABLE invoices (
    invoice_no   TEXT PRIMARY KEY,
    customer_id  BIGINT REFERENCES customers(customer_id),
    invoice_date TIMESTAMP NOT NULL,
    is_cancelled BOOLEAN NOT NULL DEFAULT FALSE
);
CREATE TABLE invoice_items (
    item_id    BIGINT PRIMARY KEY,
    invoice_no TEXT NOT NULL REFERENCES invoices(invoice_no),
    stock_code TEXT NOT NULL REFERENCES products(stock_code),
    quantity   INTEGER NOT NULL,
    price      NUMERIC(10,2) NOT NULL,
    revenue    NUMERIC(12,2) NOT NULL
);
"""

SNAPSHOT = datetime(2011, 12, 9, 12, 0)   # latest sale in the test data

# customer_id: (days since last order, number of orders).
# R tiles by recency: {8,7}=1 {6,5}=2 {4,3}=3 {2,1}=4
# F tiles by orders, then customer ID: {3,7}=1 {4,6}=2 {8,2}=3 {1,5}=4
# Customers 4, 6 and 8 all have 2 orders across the tile 2/3 boundary: only the customer-ID
# tie-break (FR-02) puts 8 in tile 3, so At-Risk (R 1-2 and F 3-4) is customers 5 and 8.
CUSTOMERS = {1: (0, 5), 2: (10, 4), 3: (20, 1), 4: (30, 2),
             5: (200, 6), 6: (300, 2), 7: (400, 1), 8: (500, 2)}

CAMPAIGN_START = "2011-12-10"   # day 90 = 2012-03-09
AUDIENCE = [(4, "treatment"), (5, "treatment"), (6, "treatment"), (7, "control"), (8, "control")]


def base_invoices():
    """Invoices as (invoice_no, customer_id, date, is_cancelled, [(quantity, price), ...])."""
    rows = []
    for cid, (recency, orders) in CUSTOMERS.items():
        for k in range(orders):
            lines = [(1, 10.0)]
            if cid == 1 and k == 1:
                lines.append((-1, 10.0))                       # a return line on a normal invoice
            rows.append((f"{cid}-{k}", cid, SNAPSHOT - timedelta(days=recency + 7 * k), 0, lines))
    rows.append(("C900", 3, SNAPSHOT + timedelta(days=1), 1, [(-1, 10.0)]))   # cancelled, after the snapshot
    rows.append(("G1", None, datetime(2011, 11, 15, 10, 0), 0, [(5, 10.0)]))  # guest order, no customer ID
    return rows


def campaign_invoices():
    return [
        ("W1", 4, datetime(2011, 12, 15, 10, 0), 0, [(3, 10.0)]),   # treatment, in the window
        ("W2", 4, datetime(2012, 1, 20, 10, 0), 0, [(2, 10.0)]),    # treatment, second order
        ("W3", 5, datetime(2012, 2, 1, 10, 0), 0, [(10, 10.0)]),    # treatment, in the window
        ("W4", 6, datetime(2012, 3, 9, 8, 0), 0, [(8, 10.0)]),      # day 90: outside the window
        ("W5", 6, datetime(2011, 12, 20, 10, 0), 0, [(-1, 10.0)]),  # return-only invoice: not a sale
        ("W6", 7, datetime(2012, 1, 5, 10, 0), 0, [(4, 10.0)]),     # control, in the window
        ("W7", 8, datetime(2012, 1, 10, 10, 0), 1, [(4, 10.0)]),    # control, cancelled order: not a sale
    ]


def load_queries():
    text = (ROOT / "06-kpis.md").read_text(encoding="utf-8")
    queries = {}
    for block in re.findall(r"```sql\n(.*?)```", text, re.S):
        name = re.match(r"--\s*@name:\s*(\w+)", block).group(1)
        queries[name] = block
    return queries


def new_db(invoices):
    db = sqlite3.connect(":memory:")
    db.executescript(SCHEMA)
    db.execute("INSERT INTO products VALUES ('P1', 'Test product')")
    db.executemany("INSERT INTO customers VALUES (?, 'United Kingdom')", [(c,) for c in CUSTOMERS])
    insert_invoices(db, invoices)
    return db


def insert_invoices(db, invoices):
    item_id = db.execute("SELECT COALESCE(MAX(item_id), 0) FROM invoice_items").fetchone()[0]
    for inv, cid, day, cancelled, lines in invoices:
        db.execute("INSERT INTO invoices VALUES (?, ?, ?, ?)",
                   (inv, cid, day.strftime("%Y-%m-%d %H:%M:%S"), cancelled))
        for qty, price in lines:
            item_id += 1
            db.execute("INSERT INTO invoice_items VALUES (?, ?, 'P1', ?, ?, ?)",
                       (item_id, inv, qty, price, round(qty * price, 2)))


def ntile(ordered_ids, buckets=4):
    """SQL NTILE: split an ordered list into `buckets` groups, earlier groups one larger if uneven."""
    size, extra = divmod(len(ordered_ids), buckets)
    tiles, start = {}, 0
    for tile in range(1, buckets + 1):
        end = start + size + (1 if tile <= extra else 0)
        for cid in ordered_ids[start:end]:
            tiles[cid] = tile
        start = end
    return tiles


def expected_at_risk(invoices):
    """KPI-1 in plain Python, breaking ties by customer ID (FR-02)."""
    snapshot = max(day for _, _, day, cancelled, _ in invoices if not cancelled)
    stats = {}
    for _, cid, day, cancelled, lines in invoices:
        sales = [round(qty * price, 2) for qty, price in lines if qty * price > 0]
        if cancelled or cid is None or not sales:
            continue
        last, orders, spend = stats.get(cid, (day, 0, 0.0))
        stats[cid] = (max(last, day), orders + 1, spend + sum(sales))
    recency = {cid: int((snapshot - last).total_seconds() // 86400) for cid, (last, _, _) in stats.items()}
    r = ntile(sorted(stats, key=lambda c: (-recency[c], c)))
    f = ntile(sorted(stats, key=lambda c: (stats[c][1], c)))
    rows = [(c, recency[c], stats[c][1], round(stats[c][2], 2)) for c in stats if r[c] <= 2 and f[c] >= 3]
    return sorted(rows, key=lambda row: (-row[3], row[0]))


def expected_unattributed(invoices):
    """KPI-4 in plain Python: share of each month's sales with no customer ID."""
    sales, guest = {}, {}
    for _, cid, day, cancelled, lines in invoices:
        for qty, price in lines:
            revenue = round(qty * price, 2)
            if cancelled or revenue <= 0:
                continue
            month = day.strftime("%Y-%m")
            sales[month] = sales.get(month, 0) + revenue
            if cid is None:
                guest[month] = guest.get(month, 0) + revenue
    return {m: round(100.0 * guest.get(m, 0) / sales[m], 1) for m in sorted(sales)}


def expected_month1(invoices):
    """KPI-5 in plain Python: share of each cohort ordering again the next calendar month."""
    valid = [(cid, day) for _, cid, day, cancelled, _ in invoices if not cancelled and cid is not None]
    first = {}
    for cid, day in valid:
        first[cid] = min(first.get(cid, day), day)
    last_month = max(day for _, _, day, cancelled, _ in invoices if not cancelled).strftime("%Y-%m")
    cohorts = {}
    for cid, day in valid:
        cohort = first[cid].strftime("%Y-%m")
        index = (day.year * 12 + day.month) - (first[cid].year * 12 + first[cid].month)
        cohorts.setdefault(cohort, ({0: set(), 1: set()}))
        if index in (0, 1):
            cohorts[cohort][index].add(cid)
    return {c: round(100.0 * len(v[1]) / len(v[0]), 1) for c, v in sorted(cohorts.items()) if c < last_month}


def check(label, actual, expected):
    if actual != expected:
        print(f"FAIL  {label}\n      expected {expected}\n      got      {actual}")
        sys.exit(1)
    print(f"ok    {label}")


def main():
    q = load_queries()
    base = base_invoices()
    db = new_db(base)

    # KPI-1: At-Risk customers, by hand and against plain Python with the FR-02 tie-break
    at_risk = [(r[0], r[2], r[3], r[4]) for r in db.execute(q["at_risk_customers"])]
    check("KPI-1 At-Risk customers are 5 and 8", at_risk, [(5, 200, 6, 60.0), (8, 500, 2, 20.0)])
    check("KPI-1 ties broken by customer ID (FR-02)", at_risk, expected_at_risk(base))

    # KPI-4 and KPI-5 against plain Python
    check("KPI-4 unattributed share by month",
          {r[0]: r[3] for r in db.execute(q["unattributed_sales_share"])}, expected_unattributed(base))
    check("KPI-5 month-1 retention by cohort",
          {r[0]: r[3] for r in db.execute(q["month1_retention"])}, expected_month1(base))

    # KPI-2 and KPI-3 on a test campaign
    db.executescript(q["winback_tables"])
    db.executemany("INSERT INTO winback_audience VALUES ('WB-TEST', ?, ?, ?, 'v1')",
                   [(cid, group, CAMPAIGN_START) for cid, group in AUDIENCE])
    insert_invoices(db, campaign_invoices())
    check("KPI-2 reactivation by group",
          db.execute(q["campaign_results"]).fetchall(),
          [("WB-TEST", "control", 2, 1, 50.0, 40.0, 20.0),
           ("WB-TEST", "treatment", 3, 2, 66.7, 150.0, 50.0)])
    check("KPI-3 uplift and incremental revenue",
          db.execute(q["campaign_uplift"]).fetchall(), [("WB-TEST", 16.7, 90.0)])

    print(f"\nAll KPI SQL checks passed (SQLite {sqlite3.sqlite_version}).")


if __name__ == "__main__":
    main()
