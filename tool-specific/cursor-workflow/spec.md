# Functional spec — medallion pipeline

## Bronze

- Read `customers.csv`, `orders.csv`, `products.csv` from a **config** local/DBFS path (no hardcoded paths).
- Write one Delta table per source (`bronze_customers`, `bronze_orders`, `bronze_products`). **No transformations** (no type coercion beyond Spark inference, no filters, no derived columns except optional `_ingest_timestamp` TIMESTAMP).
- Log **row count** per file/table and **ingestion timestamp**.
- Inputs: CSVs. Outputs: Bronze Delta + logs.

## Silver

- Read Bronze Delta. Apply four checks; **never delete rows**.
- Add `quality_check_result` STRING: `PASS` or `FAIL: <reason>` (combine reasons if multiple fail).
- Output Silver Delta (`silver_customers`, `silver_orders`, `silver_products`) plus a **quality metrics report** (% rows that passed each check, overall pass rate).

**Completeness:** PKs and required attributes non-null; `payment_date` allowed null.

**Uniqueness:** duplicate PK → FAIL those rows (keep all copies).

**Referential integrity (orders):** `customer_id` in customers; `product_id` in products.

**Business logic:** `quantity` > 0; monetary fields ≥ 0; `total_amount` matches `quantity * unit_price` (small decimal tolerance); enums valid (`Premium`/`Standard`/`Basic`; `Pending`/`Completed`/`Cancelled`); Completed ⇒ `payment_date` not null.

## Gold

Build from Silver **PASS** orders (typically `order_status = 'Completed'`) joined to customers/products.

**A) `gold_sales_by_product`**

| Column | Type |
|---|---|
| product_id | INT |
| product_name | STRING |
| category | STRING |
| total_orders | BIGINT |
| total_revenue | DECIMAL |
| avg_order_value | DECIMAL |

**B) `gold_revenue_by_customer`**

| Column | Type |
|---|---|
| customer_id | INT |
| customer_name | STRING |
| customer_segment | STRING |
| total_orders | BIGINT |
| total_revenue | DECIMAL |
| avg_order_value | DECIMAL |
| lifetime_value_actual | DECIMAL |

(`lifetime_value_actual` = sum of qualifying `total_amount`.)

**C) `gold_customer_segmentation`**

| Column | Type |
|---|---|
| segment_type | STRING |
| customer_count | BIGINT |
| avg_revenue | DECIMAL |
| total_revenue | DECIMAL |

`segment_type`: **High-Value** (revenue above a config threshold), **Repeat** (≥2 orders, not High-Value unless documented overlap rule: assign one type per customer, High-Value first), **One-Time** (exactly 1 order), **Inactive** (0 completed orders in window or no qualifying orders).

## Dashboard (Databricks SQL)

≥3 queries against Gold (uppercase SQL, one clause per line):

1. **Bar** — revenue by `product_name` or `category` (`gold_sales_by_product`).
2. **Histogram / distribution** — `avg_order_value` or `total_revenue` buckets (`gold_revenue_by_customer`).
3. **Pie** — `customer_count` by `segment_type` (`gold_customer_segmentation`).

Optional: top customers by `total_revenue`. Visuals: Databricks SQL bar, histogram, pie.