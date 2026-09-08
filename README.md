# E-Commerce Medallion Architecture Pipeline

A Databricks pipeline that takes synthetic e-commerce CSVs through **Medallion Architecture** — a layered Bronze → Silver → Gold pattern that keeps raw data, validates it, then publishes business-ready aggregates — and surfaces the Gold tables in a Databricks Genie / SQL dashboard. Bronze lands the CSVs as Delta tables; Silver flags (never deletes) quality defects via a `quality_check_result` column; Gold aggregates only `PASS` + `Completed` orders into analytics tables. Runs on **Databricks Community Edition** with Unity Catalog Volumes.

**Repository:** https://github.com/Rawat-A/C1-assessment

---

## Table of contents

1. [Architecture](#1-architecture)
2. [Prerequisites](#2-prerequisites)
3. [Quick Start](#3-quick-start)
4. [Repository structure](#4-repository-structure)
5. [Pipeline layers](#5-pipeline-layers)
6. [Dashboard assets](#6-dashboard-assets)
7. [Data quality strategy](#7-data-quality-strategy)
8. [Testing](#8-testing)
9. [Troubleshooting / known issues](#9-troubleshooting--known-issues)
10. [AI-assisted development](#10-ai-assisted-development)
11. [Resetting the environment](#11-resetting-the-environment)

Related docs: `design-notes.md`, `data-quality-strategy.md`, `database/setup-notes.md`, `src/dashboard/DASHBOARD_GUIDE.md`, `tool-specific/cursor-workflow/spec.md`.

---

## 1. Architecture

```
Repo CSVs (data/*.csv)
        │
        ▼  copy to Volume
/Volumes/main/default/c1_assessment/data/
        │
        ▼
┌───────────────────────────────────────────────────────────┐
│                     BRONZE LAYER                          │
│  Raw ingestion — no transformation                        │
│  Delta: .../delta/bronze_customers                          │
│         .../delta/bronze_orders                           │
│         .../delta/bronze_products                         │
│  + _ingest_timestamp                                      │
└───────────────────────────────────────────────────────────┘
        │
        ▼
┌───────────────────────────────────────────────────────────┐
│                     SILVER LAYER                          │
│  Data quality & validation                                │
│  Flag bad rows (never delete)                             │
│  quality_check_result = PASS | FAIL: <reason>              │
│  Delta: .../delta/silver_*                                │
└───────────────────────────────────────────────────────────┘
        │  only quality_check_result = 'PASS'
        │  and order_status = 'Completed' for revenue
        ▼
┌───────────────────────────────────────────────────────────┐
│                      GOLD LAYER                           │
│  Business-ready aggregations                              │
│  .../delta/gold_sales_by_product                          │
│  .../delta/gold_revenue_by_customer                       │
│  .../delta/gold_customer_segmentation                     │
│  .../delta/gold_daily_weekly_trends                       │
└───────────────────────────────────────────────────────────┘
        │
        ▼
┌───────────────────────────────────────────────────────────┐
│           DATABRICKS GENIE / SQL DASHBOARD                │
│  Revenue by category · customer segments · top customers  │
│  Revenue distribution histogram · daily/weekly trends     │
└───────────────────────────────────────────────────────────┘
```

**Design principles**

| Principle | Implementation |
|-----------|----------------|
| Raw fidelity | Bronze stores CSVs as-is plus `_ingest_timestamp` |
| Flag, don't delete | Silver adds `quality_check_result`; Gold filters to `PASS` |
| Config-driven paths | `pipeline_config.py` + env vars `PIPELINE_DATA_PATH`, `PIPELINE_DELTA_PATH` |
| Idempotency | Delta `overwrite` on each layer run |
| CE-compatible storage | Unity Catalog Volume (Workspace path is read-only for Delta writes) |

---

## 2. Prerequisites

* **Databricks Community Edition** workspace with Unity Catalog enabled
* A **cluster** with Delta Lake support (Runtime 13.3 LTS+ recommended)
* Permission to create a Volume: `/Volumes/main/default/c1_assessment`
* **Local (data generation only):** Python 3.10+, `pandas`, `faker`

```bash
pip install -r requirements.txt
```

PySpark and Delta are provided by the Databricks cluster — no local Spark install required for the main pipeline.

---

## 3. Quick Start

### Step 1 — Clone and generate CSVs (local)

```bash
git clone https://github.com/Rawat-A/C1-assessment.git
cd C1-assessment
pip install -r requirements.txt
python src/data_generation/generate_sample_data.py
```

| File | Rows (seed 42) |
|------|----------------|
| `data/customers.csv` | 10,010 |
| `data/orders.csv` | 100,020 |
| `data/products.csv` | 500 |

### Step 2 — Create Unity Catalog Volume (Databricks SQL)

```sql
CREATE SCHEMA IF NOT EXISTS main.default;
CREATE VOLUME IF NOT EXISTS main.default.c1_assessment;
```

### Step 3 — Run the pipeline notebook

Open `notebooks/run_medallion_pipeline.py` in Databricks (or import it). Update `REPO_PATH` if your clone path differs, then run cells top to bottom:

1. **Setup** — sets Volume paths and `sys.path`
2. **Copy CSVs** — `dbutils.fs.cp` from Workspace repo to Volume
3. **Bronze** — ingest three CSVs to Delta
4. **Silver** — quality checks + metrics report
5. **Gold** — four aggregation tables
6. **Register views** — temp views for SQL / dashboard queries
7. **Dashboard SQL** — bar, pie, histogram preview queries

**Default paths (configurable via env vars):**

| Variable | Default on Databricks CE |
|----------|------------------------|
| `PIPELINE_DATA_PATH` | `/Volumes/main/default/c1_assessment/data` |
| `PIPELINE_DELTA_PATH` | `/Volumes/main/default/c1_assessment/delta` |
| `HIGH_VALUE_THRESHOLD` | `5000` |

### Step 4 — Create UC views for Genie dashboard (SQL)

```sql
CREATE SCHEMA IF NOT EXISTS main.ecommerce;

CREATE OR REPLACE VIEW main.ecommerce.gold_sales_by_product AS
SELECT * FROM delta.`/Volumes/main/default/c1_assessment/delta/gold_sales_by_product`;

CREATE OR REPLACE VIEW main.ecommerce.gold_revenue_by_customer AS
SELECT * FROM delta.`/Volumes/main/default/c1_assessment/delta/gold_revenue_by_customer`;

CREATE OR REPLACE VIEW main.ecommerce.gold_customer_segmentation AS
SELECT * FROM delta.`/Volumes/main/default/c1_assessment/delta/gold_customer_segmentation`;

CREATE OR REPLACE VIEW main.ecommerce.gold_daily_weekly_trends AS
SELECT * FROM delta.`/Volumes/main/default/c1_assessment/delta/gold_daily_weekly_trends`;
```

### Step 5 — Build Genie dashboard

1. **New → Dashboard** → open **Genie Code** → **Agent** mode
2. Prompt example:

```
Create an e-commerce dashboard using @main.ecommerce.gold_sales_by_product,
@main.ecommerce.gold_revenue_by_customer, and @main.ecommerce.gold_customer_segmentation.
Include: total revenue KPI, bar chart by category, pie chart by segment_type,
top 10 customers bar chart, and customer revenue distribution histogram.
```

See `src/dashboard/DASHBOARD_GUIDE.md` for full details.

### Verify row counts

```python
from pipeline_config import bronze_path, silver_path, gold_path
spark.read.format("delta").load(bronze_path("customers")).count()  # 10010
spark.read.format("delta").load(silver_path("orders")).count()     # 100020
spark.read.format("delta").load(gold_path("sales_by_product")).count()
```

---

## 4. Repository structure

```
C1-assessment/
├── README.md                          # This file
├── candidate-info.md
├── requirements-analysis.md
├── design-notes.md
├── data-model.md
├── data-quality-strategy.md
├── debugging-notes.md
├── reflection.md
├── final-ai-usage-summary.md
├── tool-workflow.md
├── .cursorrules
├── .gitignore
├── requirements.txt
│
├── notebooks/
│   └── run_medallion_pipeline.py      # Databricks notebook (full pipeline)
│
├── src/
│   ├── pipeline_config.py             # Shared path + threshold config
│   ├── data_generation/
│   │   ├── generate_sample_data.py
│   │   └── DATA_GENERATION_NOTES.md
│   ├── bronze/
│   │   ├── ingest_utils.py
│   │   ├── 01_ingest_customers.py
│   │   ├── 02_ingest_orders.py
│   │   ├── 03_ingest_products.py
│   │   └── ingest_all.py
│   ├── silver/
│   │   ├── quality_utils.py
│   │   ├── 01_quality_completeness.py
│   │   ├── 02_quality_uniqueness.py
│   │   ├── 03_quality_type_validation.py
│   │   ├── 04_quality_referential_integrity.py
│   │   ├── 05_quality_business_logic.py
│   │   └── create_silver_tables.py
│   ├── gold/
│   │   ├── 01_sales_by_product.sql
│   │   ├── 02_revenue_by_customer.sql
│   │   ├── 03_daily_weekly_trends.sql
│   │   ├── 04_customer_segmentation.sql
│   │   └── create_gold_tables.py
│   └── dashboard/
│       ├── dashboard_queries.sql
│       └── DASHBOARD_GUIDE.md
│
├── data/                              # Generated CSVs (seed 42)
├── database/
│   ├── schema.sql
│   ├── seed-data-notes.md
│   └── setup-notes.md
│
├── ai-prompts/
│   ├── all-project-prompts.md         # Core AI prompts (submission)
│   └── [layer-specific prompt stubs]
│
└── tool-specific/cursor-workflow/
    ├── project-context.md
    ├── spec.md
    └── task-breakdown.md
```

---

## 5. Pipeline layers

### 5.1 Data generation

**Command** (from repo root):

```bash
python src/data_generation/generate_sample_data.py
```

Deterministic with `RANDOM_SEED = 42`. Injects known defects in `inject_quality_issues()` — see `src/data_generation/DATA_GENERATION_NOTES.md`.

### 5.2 Bronze

Reads CSVs from `PIPELINE_DATA_PATH`, writes Delta to `PIPELINE_DELTA_PATH/bronze_*` with `_ingest_timestamp`. No filtering or transformation.

```python
from bronze.ingest_all import ingest_all
ingest_all(spark)
```

| Table | Expected rows |
|-------|---------------|
| `bronze_customers` | 10,010 |
| `bronze_orders` | 100,020 |
| `bronze_products` | 500 |

### 5.3 Silver

Applies five quality modules; **never deletes rows**. Adds `quality_check_result` (`PASS` or `FAIL: <reason>`). Prints pass-rate report.

```python
from silver.create_silver_tables import create_silver_tables
create_silver_tables(spark)
```

Silver row counts match Bronze exactly.

### 5.4 Gold

Builds four aggregation tables from Silver `PASS` + `Completed` orders.

| Table | Description |
|-------|-------------|
| `gold_sales_by_product` | Revenue and orders per product |
| `gold_revenue_by_customer` | Revenue per customer + `lifetime_value_actual` |
| `gold_customer_segmentation` | High-Value / Repeat / One-Time / Inactive |
| `gold_daily_weekly_trends` | Daily and weekly revenue trends |

**Segmentation rules** (mutually exclusive, High-Value first):  
High-Value if `total_revenue >= HIGH_VALUE_THRESHOLD` (default 5000); else Repeat if ≥2 orders; else One-Time if 1 order; else Inactive.

```python
from gold.create_gold_tables import create_gold_tables
create_gold_tables(spark)
```

### 5.5 Dashboard

SQL queries in `src/dashboard/dashboard_queries.sql`. Genie Space over `main.ecommerce.gold_*` views — see Section 6.

---

## 6. Dashboard assets

| # | Visualization | Chart type | Gold source |
|---|---------------|------------|-------------|
| 1 | Revenue by category | Bar | `gold_sales_by_product` |
| 2 | Customer revenue distribution | Histogram / bar | `gold_revenue_by_customer` |
| 3 | Customer segments | Pie | `gold_customer_segmentation` |
| 4 | Top 10 customers | Bar | `gold_revenue_by_customer` |
| 5 | Daily / weekly trends | Line | `gold_daily_weekly_trends` |

**Dependency:** Run Bronze → Silver → Gold before building the dashboard or views will be empty.

**Published dashboard:** Add your Databricks dashboard URL here after publishing.

---

## 7. Data quality strategy

Silver **flags, never deletes**. Full matrix: `data-quality-strategy.md`.

**Seeded defects (seed 42)**

| Check | Table | Issue | Count |
|-------|-------|-------|-------|
| Completeness | customers | null email | 50 |
| Completeness | orders | null customer_id | 100 |
| Completeness | orders | null product_id | 200 |
| Uniqueness | customers | duplicate customer_id | 20 rows (10 IDs × 2) |
| Uniqueness | orders | duplicate order_id | 40 rows (20 IDs × 2) |
| Referential integrity | orders | orphan customer_id | 50 |
| Referential integrity | orders | orphan product_id | 30 |

Gold revenue uses `quality_check_result = 'PASS'` and `order_status = 'Completed'`.

---

## 8. Testing

No `tests/` directory in this repository. Verification is via:

* Printed row counts and quality metrics report (Silver)
* Gold table previews in the notebook
* SQL spot-checks on Gold aggregations

---

## 9. Troubleshooting / known issues

### Read-only file system on `/Workspace/...`

**Cause:** Databricks CE cannot write Delta files under the Workspace user folder.

**Fix:** Use Unity Catalog Volume paths for `PIPELINE_DELTA_PATH` and `PIPELINE_DATA_PATH` (see Quick Start Step 2–3).

### `[DBFS_DISABLED] Public DBFS root is disabled`

**Cause:** `/FileStore/` is not available on CE.

**Fix:** Use `/Volumes/main/default/c1_assessment/` instead of `dbfs:/FileStore/`.

### `ImportError` from `pipeline_config`

**Cause:** Stale module cache or old `pipeline_config.py` on Databricks.

**Fix:** Restart Python kernel; ensure `pipeline_config.py` uses runtime path functions (`delta_base_path()`, `customers_csv()`, etc.). Pull latest from GitHub.

### `TABLE_OR_VIEW_NOT_FOUND` on Gold views

**Cause:** Gold layer not run, or UC views not created.

**Fix:** Run Gold cells in the notebook, then execute Step 4 SQL to create `main.ecommerce` views.

### Genie cannot find tables

Reference tables with `@main.ecommerce.gold_sales_by_product` in Agent mode. Ensure UC views exist and you have `SELECT` permission.

---

## 10. AI-assisted development

**Cursor IDE** generated the pipeline scaffold, data generator, Bronze/Silver/Gold code, and documentation. **Databricks Genie** was used to build the dashboard from Gold views.

| Resource | Description |
|----------|-------------|
| `ai-prompts/all-project-prompts.md` | 4 core project-creation prompts |
| `final-ai-usage-summary.md` | AI usage summary |
| `tool-specific/cursor-workflow/` | Project context and spec for Cursor |

---

## 11. Resetting the environment

Re-run the notebook cells (Bronze → Silver → Gold). Delta writes use `overwrite` mode — no manual cleanup required for a normal rebuild.

To fully reset Volume data:

```python
dbutils.fs.rm("/Volumes/main/default/c1_assessment/delta", recurse=True)
dbutils.fs.rm("/Volumes/main/default/c1_assessment/data", recurse=True)
```

Then re-copy CSVs and re-run the pipeline.

---

## Author

**GitHub:** [Rawat-A](https://github.com/Rawat-A)  
**Repository:** [C1-assessment](https://github.com/Rawat-A/C1-assessment)
