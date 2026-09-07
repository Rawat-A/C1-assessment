# AI Prompts — Project Creation Only

Core prompts used to **build** the Databricks medallion pipeline.  
Excludes setup questions, Git troubleshooting, Databricks path/debugging prompts, and follow-up cross-questions.

**Repo:** https://github.com/Rawat-A/C1-assessment  
**Tool:** Cursor IDE (AI agent)  
**Total prompts:** 4

---

## Prompt 1 — Project scaffold & coding standards

```
I'm building a Databricks medallion architecture data pipeline (Bronze → Silver → Gold → Dashboard) 
for an e-commerce company. Source data: customers.csv, orders.csv, products.csv, ingested from S3/DBFS.

Create the following folder/file structure (empty placeholder files with a one-line comment describing 
their purpose — don't fill in content yet):

databricks-medallion-pipeline/
├── README.md
├── candidate-info.md
├── tool-workflow.md
├── requirements-analysis.md
├── design-notes.md
├── data-model.md
├── data-quality-strategy.md
├── src/
│   ├── data_generation/
│   │   ├── generate_sample_data.py
│   │   └── DATA_GENERATION_NOTES.md
│   ├── bronze/
│   │   ├── 01_ingest_customers.py
│   │   ├── 02_ingest_orders.py
│   │   ├── 03_ingest_products.py
│   │   └── ingest_all.py
│   ├── silver/
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
├── data/
├── database/
│   ├── schema.sql
│   ├── seed-data-notes.md
│   └── setup-notes.md
├── debugging-notes.md
├── reflection.md
├── final-ai-usage-summary.md
├── ai-prompts/
│   ├── data-generation.md
│   ├── bronze-layer.md
│   ├── silver-layer.md
│   ├── gold-layer.md
│   ├── dashboard.md
│   ├── debugging.md
│   └── documentation.md
└── tool-specific/
    └── cursor-workflow/
        ├── project-context.md
        ├── spec.md
        ├── cursor-rules-or-instructions.md
        └── task-breakdown.md

Also create a .cursorrules file at the root with these project standards:
- Language/stack: Python, PySpark, SQL, Delta Lake, Databricks
- Code style: PEP8, type hints where practical, docstrings on all functions
- Every script must include a comment block at the top explaining its purpose and inputs/outputs
- Silver layer must NEVER delete bad rows — always flag them with a quality_check_result column
- No hardcoded file paths — use config variables at the top of each script
- All SQL should be formatted with uppercase keywords and one clause per line
```

**Outcome:** Full folder structure, placeholder files, `.cursorrules`

---

## Prompt 2 — Project context & functional specification

```
Populate two files with real content (not placeholders):

1. tool-specific/cursor-workflow/project-context.md
   Write a concise project context brief I can paste at the start of future Cursor 
   conversations. Include:
   - One paragraph: what this pipeline does and why (e-commerce sales, medallion architecture)
   - The three source tables and their schemas (see below)
   - The four Silver-layer quality checks required: completeness, uniqueness, 
     referential integrity, and business-logic validation
   - The three Gold-layer aggregations required: Sales by Product, Revenue by Customer, 
     Customer Segmentation
   - Tech stack: Databricks Community Edition, PySpark, Delta Lake, SQL

2. tool-specific/cursor-workflow/spec.md
   Write a functional specification covering:
   - Bronze layer: read raw CSVs from a local/DBFS path into Delta tables, no transformation, 
     log row counts and ingestion timestamp
   - Silver layer: apply quality checks below, add a quality_check_result column 
     (PASS/FAIL + reason), never delete rows, output a quality metrics report (% passed per check)
   - Gold layer: three aggregation tables (schemas below)
   - Dashboard: 3+ SQL queries for Databricks SQL visualizations (bar, histogram, pie)

Schemas to use:

customers.csv: customer_id (INT, PK), customer_name (STRING), email (STRING), 
country (STRING), signup_date (DATE), customer_segment (STRING: Premium/Standard/Basic), 
lifetime_value (DECIMAL)

orders.csv: order_id (INT, PK), customer_id (INT, FK), order_date (DATE), 
product_id (INT, FK), quantity (INT), unit_price (DECIMAL), total_amount (DECIMAL), 
order_status (STRING: Pending/Completed/Cancelled), payment_date (DATE, nullable)

products.csv: product_id (INT, PK), product_name (STRING), category (STRING), 
price (DECIMAL), cost (DECIMAL), stock_quantity (INT), reorder_level (INT)

Gold table schemas:
A) sales_by_product: product_id, product_name, category, total_orders, total_revenue, avg_order_value
B) revenue_by_customer: customer_id, customer_name, customer_segment, total_orders, 
   total_revenue, avg_order_value, lifetime_value_actual
C) customer_segmentation: segment_type (High-Value/Repeat/One-Time/Inactive), 
   customer_count, avg_revenue, total_revenue

Keep both files under 500 words each — they're meant to be pasted as context, not read as essays.
```

**Outcome:** `project-context.md`, `spec.md`

---

## Prompt 3 — Sample data generation

```
Using the project context and spec above, write src/data_generation/generate_sample_data.py.

Requirements:
- Use pandas + Faker to generate three CSVs into a local ./data/ folder:
  1. customers.csv — 10,000 rows: customer_id (INT, PK, sequential), customer_name, email, 
     country, signup_date (DATE between 2020-01-01 and today), 
     customer_segment (Premium/Standard/Basic, weighted ~20/50/30), lifetime_value (DECIMAL)
  2. orders.csv — 100,000 rows: order_id (INT, PK, sequential), customer_id (FK), 
     order_date (DATE, must be >= that customer's signup_date), product_id (FK), 
     quantity (INT 1-10), unit_price (DECIMAL, from product), total_amount (= quantity * unit_price), 
     order_status (Pending/Completed/Cancelled, weighted ~15/75/10), 
     payment_date (DATE, nullable, null if status != Completed)
  3. products.csv — 500 rows: product_id (INT, PK, sequential), product_name, category, 
     price (DECIMAL), cost (DECIMAL, always < price), stock_quantity (INT), reorder_level (INT)

- After generating clean data, intentionally corrupt a copy to introduce these exact issues 
  (do this in a separate function, e.g. inject_quality_issues(), so the "clean generation" 
  and "issue injection" logic are clearly separated):
  
  customers.csv:
    - 50 rows: set email to NULL
    - 10 rows: duplicate an existing customer_id (append as extra rows, don't overwrite)
  
  orders.csv:
    - 100 rows: set customer_id to NULL
    - 200 rows: set product_id to NULL
    - 50 rows: set customer_id to a value that does NOT exist in customers.csv (e.g. 999999+)
    - 30 rows: set product_id to a value that does NOT exist in products.csv
    - 20 rows: duplicate an existing order_id (append as extra rows)

- Make the row selection for corruption random but reproducible (use a fixed random seed, e.g. 42)
- Print a summary at the end: total rows generated per file, and a breakdown of how many rows 
  have each type of intentional issue
- Add a header comment block explaining purpose/inputs/outputs, per .cursorrules
- Add type hints and docstrings on every function

Also create src/data_generation/DATA_GENERATION_NOTES.md explaining:
- Why each quality issue category was chosen (ties to real-world data quality problems)
- The exact counts injected (so Silver layer tests can assert against known numbers)
- The random seed used, for reproducibility
```

**Outcome:** `generate_sample_data.py`, `DATA_GENERATION_NOTES.md`, sample CSVs in `data/`

---

## Prompt 4 — Full pipeline implementation

```
Implement the complete medallion pipeline per project-context.md and spec.md:

1. Generate sample CSVs (customers, orders, products) if not already present
2. Bronze layer — ingest_all.py and per-table ingest scripts (raw CSV → Delta, _ingest_timestamp, log row counts)
3. Silver layer — five quality-check modules + create_silver_tables.py 
   (completeness, uniqueness, type validation, referential integrity, business logic; 
   quality_check_result column; never delete rows; quality metrics report)
4. Gold layer — four SQL aggregation files + create_gold_tables.py
5. Dashboard — dashboard_queries.sql (bar, histogram, pie) + DASHBOARD_GUIDE.md
6. database/schema.sql and README.md with setup instructions

Follow .cursorrules: config variables for paths, PEP8, type hints, docstrings, uppercase SQL.
```

**Outcome:** Bronze, Silver, Gold, dashboard, `pipeline_config.py`, `schema.sql`, `README.md`

---

## Summary

| # | Focus | Key deliverables |
|---|--------|------------------|
| 1 | Scaffold | Folder structure, `.cursorrules` |
| 2 | Design | `project-context.md`, `spec.md` |
| 3 | Data | `generate_sample_data.py`, CSVs with known defects |
| 4 | Pipeline | Bronze → Silver → Gold → Dashboard code |

**Note:** Prompt 4 was given as *"do it for me"* in the session, after reviewing the project status. It is expanded here to reflect the full implementation scope that was requested.
