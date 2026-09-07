# Databricks Dashboard Guide

Use these steps to build a Databricks SQL dashboard from the Gold tables.

## Prerequisites

1. Run the full pipeline: Bronze → Silver → Gold (`ingest_all.py`, `create_silver_tables.py`, `create_gold_tables.py`).
2. Register Gold tables in Unity Catalog or create SQL views pointing at Delta paths under `delta/gold_*`.

## Recommended visualizations

| Query in `dashboard_queries.sql` | Chart type | X-axis / dimension | Y-axis / metric |
|---|---|---|---|
| Query 1 — revenue by category | Bar | `category` | `total_revenue` |
| Query 2 — revenue buckets | Histogram / bar | `revenue_bucket` | `customer_count` |
| Query 3 — segment share | Pie | `segment_type` | `customer_count` |
| Query 4 — top customers | Bar (optional) | `customer_name` | `total_revenue` |

## Databricks SQL steps

1. Open **SQL** → **Queries** in the Databricks workspace.
2. Paste each query from `src/dashboard/dashboard_queries.sql` (one query per saved query).
3. Point table names at your catalog/schema (e.g. `main.ecommerce.gold_sales_by_product`) or create views:

```sql
CREATE OR REPLACE VIEW gold_sales_by_product AS
SELECT * FROM delta.`/path/to/delta/gold_sales_by_product`;
```

4. Create a **Dashboard** and add:
   - Bar chart: category revenue (Query 1)
   - Histogram: customer revenue distribution (Query 2)
   - Pie chart: segment mix (Query 3)

## Filters (optional)

Add dashboard parameters for `order_date` range once daily/weekly trends are wired from `gold_daily_weekly_trends`.
