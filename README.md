# E-Commerce Medallion Pipeline (Databricks)

Bronze → Silver → Gold → Dashboard pipeline for e-commerce sales analytics. Ingests `customers.csv`, `orders.csv`, and `products.csv`, applies Silver quality checks (flag, never delete), and builds Gold aggregations for Databricks SQL dashboards.

**Stack:** Databricks Community Edition, PySpark, Delta Lake, SQL

## Project structure

```
src/
  data_generation/   # Sample CSV generator (pandas + Faker)
  bronze/            # Raw CSV → Delta ingestion
  silver/            # Quality checks + quality_check_result column
  gold/              # SQL aggregations + create_gold_tables.py
  dashboard/         # Dashboard SQL queries
notebooks/
  run_medallion_pipeline.py   # Databricks notebook (import or open in workspace)
data/                # Generated CSVs (not committed at scale)
delta/               # Bronze/Silver/Gold Delta output (created at runtime)
```

## Quick start

### 1. Generate sample data (local)

```bash
pip install -r requirements.txt
python src/data_generation/generate_sample_data.py
```

Produces `data/customers.csv` (10,010 rows), `orders.csv` (100,020), `products.csv` (500) with intentional quality defects (seed `42`). See `src/data_generation/DATA_GENERATION_NOTES.md`.

### 2. Run pipeline on Databricks

Upload the repo to Databricks (Repos or workspace files). Set paths if needed:

| Variable | Default |
|---|---|
| `PIPELINE_DATA_PATH` | `<repo>/data` |
| `PIPELINE_DELTA_PATH` | `<repo>/delta` |
| `HIGH_VALUE_THRESHOLD` | `5000` |

Run in order (cluster with Delta enabled):

```python
# Notebook or job — add repo src/ to path
import sys
sys.path.insert(0, "/Workspace/Repos/<user>/databricks-medallion-pipeline/src")

from bronze.ingest_all import ingest_all
from silver.create_silver_tables import create_silver_tables
from gold.create_gold_tables import create_gold_tables

spark = spark  # Databricks provides this
ingest_all(spark)
create_silver_tables(spark)
create_gold_tables(spark)
```

Or run scripts individually:

- `src/bronze/ingest_all.py`
- `src/silver/create_silver_tables.py`
- `src/gold/create_gold_tables.py`

### 3. Dashboard

Use queries in `src/dashboard/dashboard_queries.sql`. See `src/dashboard/DASHBOARD_GUIDE.md`.

## Silver quality rules

- **Never delete rows** — invalid records get `quality_check_result = 'FAIL: <reason>'`
- Checks: completeness, uniqueness, type validation, referential integrity (orders), business logic
- Metrics report printed after Silver run (% passed per check)

## Gold tables

| Table | Description |
|---|---|
| `gold_sales_by_product` | Orders and revenue by product |
| `gold_revenue_by_customer` | Revenue and LTV by customer |
| `gold_daily_weekly_trends` | Daily/weekly trend rollup |
| `gold_customer_segmentation` | High-Value / Repeat / One-Time / Inactive |

Gold uses Silver `PASS` rows and `order_status = 'Completed'` unless noted in SQL.

## Reference docs

- `tool-specific/cursor-workflow/project-context.md` — paste into Cursor sessions
- `tool-specific/cursor-workflow/spec.md` — functional specification
- `database/schema.sql` — table DDL reference
- `.cursorrules` — coding standards
