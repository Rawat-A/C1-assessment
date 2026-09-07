# Sample data generation notes

Clean CSVs are built first (`generate_customers` / `generate_orders` / `generate_products`). A **copy** is then corrupted in `inject_quality_issues()` so generation and defect injection stay separate. Only the dirty files are written to `data/` (the Bronze source).

**Random seed:** `42` (`RANDOM_SEED` in `generate_sample_data.py`). Faker and NumPy both use this seed. Issue-row picks are disjoint within each table so Silver tests can assert the counts below without overlapping defects on the same row.

## Why these issues

| Issue | Real-world analogue | Silver check |
|---|---|---|
| Null `email` | Incomplete CRM signup / failed form validation | Completeness |
| Duplicate `customer_id` | Double load, CDC replay, or merge without a proper key | Uniqueness |
| Null `orders.customer_id` / `product_id` | Broken extract, optional join keys dropped in transit | Completeness (and typically RI) |
| `customer_id` / `product_id` not in parent tables | Late-arriving dimensions, deleted masters, or bad mapping | Referential integrity |
| Duplicate `order_id` | Exactly-once delivery failure; the same order file landed twice | Uniqueness |

Orphan keys use IDs `>= 1_000_000` so they cannot collide with real PKs (`1..10000` customers, `1..500` products).

Business-logic defects (negative qty, amount ≠ qty × price, bad enums) are **not** injected here; add them later if Silver business-rule tests need fixtures.

## Exact injected counts (assert these)

**customers.csv** — 10,000 clean + 10 extra rows = **10,010** rows

- 50 rows: `email` is null
- 10 extra rows: copy of an existing `customer_id` (appended, not overwritten)
- Uniqueness: 10 IDs appear twice → **20** rows share a duplicated PK

**orders.csv** — 100,000 clean + 20 extra rows = **100,020** rows

- 100 rows: `customer_id` is null
- 200 rows: `product_id` is null
- 50 rows: `customer_id` = `1000000..1000049` (not in customers)
- 30 rows: `product_id` = `1000000..1000029` (not in products)
- 20 extra rows: copy of an existing `order_id`
- Uniqueness: 20 IDs appear twice → **40** rows share a duplicated PK

**products.csv** — **500** rows, no injected issues

Duplicate source rows are chosen from a disjoint index pool so appended dupes are not the same rows as the null/orphan mutations.

## Run

```text
pip install pandas faker
python src/data_generation/generate_sample_data.py
```

Run from the `databricks-medallion-pipeline` root (or anywhere; output is `PROJECT_ROOT/data`).
