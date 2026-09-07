# All AI Prompts — C1 Assessment (Databricks Medallion Pipeline)

Chronological list of prompts given to Cursor AI to complete this project.  
**Repo:** https://github.com/Rawat-A/C1-assessment  
**Tool:** Cursor IDE (AI agent)

---

## Phase 1 — Project scaffold & standards

### Prompt 1
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

---

## Phase 2 — Project context & specification

### Prompt 2
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

[Schemas for customers, orders, products, and Gold tables included in prompt]
```

---

## Phase 3 — Sample data generation

### Prompt 3
```
Using the project context and spec above, write src/data_generation/generate_sample_data.py.

Requirements:
- Use pandas + Faker to generate three CSVs into a local ./data/ folder:
  1. customers.csv — 10,000 rows [schema details]
  2. orders.csv — 100,000 rows [schema details]
  3. products.csv — 500 rows [schema details]

- After generating clean data, intentionally corrupt a copy to introduce these exact issues 
  (do this in a separate function, e.g. inject_quality_issues()):

  customers.csv:
    - 50 rows: set email to NULL
    - 10 rows: duplicate an existing customer_id (append as extra rows, don't overwrite)
  
  orders.csv:
    - 100 rows: set customer_id to NULL
    - 200 rows: set product_id to NULL
    - 50 rows: set customer_id to a value that does NOT exist in customers.csv
    - 30 rows: set product_id to a value that does NOT exist in products.csv
    - 20 rows: duplicate an existing order_id (append as extra rows)

- Make the row selection for corruption random but reproducible (use a fixed random seed, e.g. 42)
- Print a summary at the end
- Add a header comment block explaining purpose/inputs/outputs, per .cursorrules
- Add type hints and docstrings on every function

Also create src/data_generation/DATA_GENERATION_NOTES.md explaining:
- Why each quality issue category was chosen
- The exact counts injected
- The random seed used, for reproducibility
```

---

## Phase 4 — Resume & full implementation

### Prompt 4
```
lets resume this project 
what to do next
```

### Prompt 5
```
do it for me
```
*(AI implemented: generate CSVs, Bronze, Silver, Gold, dashboard queries, schema.sql, README)*

---

## Phase 5 — Git & GitHub setup

### Prompt 6
```
can i create this repo in gitlab
```

### Prompt 7
```
i am using github 
my username is Rawat-A and repo name is C1-assessment
```

### Prompt 8
```
cd "c:\Users\Abhishek\Desktop\C1-assessment\databricks-medallion-pipeline"

git branch -M main

git remote add origin https://github.com/<YOUR_USERNAME>/databricks-medallion-pipeline.git

git push -u origin main

i want to run these commands 
my github username is Rawat-A and repo name is C1-assessment
```

### Prompt 9
```
i check my github i am signed in as Rawat-A and repo name is C1-assesment
```
*(Typo in repo name — later renamed to C1-assessment)*

### Prompt 10
```
repo name is renamed to C1-assessment
what next
```

---

## Phase 6 — Databricks setup & execution

### Prompt 11
```
how to setup databricks notebook
```

### Prompt 12
```
when i try to open git folder is databricks it is asking for git repository URL, git providrr and git folder name
```

### Prompt 13
```
i created a notebook in databricks now how to fetch the queries in it
```

### Prompt 14
```
path is like https://dbc-4a97fc9a-a0f3.cloud.databricks.com/browse/folders/repos?o=7474654002732453
```

### Prompt 15
```
it is like Workspace
Users
abhishek.rawat@tothenew.com
```

### Prompt 16
```
path is correct
```

---

## Phase 7 — Debugging (Databricks errors)

### Prompt 17
```
cell 2 output is [CLOUD_FILE_NOT_FOUND] Cloud file is not found. Reason: 
/Workspace/Users/abhishek.rawat@tothenew.com/C1-assessment/delta/bronze_customers/... 
(Read-only file system). SQLSTATE: 42K03
```

### Prompt 18
```
cell 1 b output is 
OSError: [Errno 95] Operation not supported: '/dbfs/FileStore'
```

### Prompt 19
```
cell 1 b output 
ExecutionError: [DBFS_DISABLED] Public DBFS root is disabled. Access is denied on path: 
/FileStore/C1-assessment/data SQLSTATE: 56038
```

### Prompt 20
```
cell 2 still showing error 
[CLOUD_FILE_NOT_FOUND] ... /Workspace/.../delta/bronze_customers/... (Read-only file system)
```

### Prompt 21
```
cell 2 bypass still showing error 
ImportError: cannot import name 'customers_csv' from 'pipeline_config'
correct it quickly i don't have enogh cursor token
```

### Prompt 22
```
from gold.create_gold_tables import create_gold_tables
create_gold_tables(spark) this outputs 
ImportError: cannot import name 'HIGH_VALUE_REVENUE_THRESHOLD' from 'pipeline_config'
```

### Prompt 23
```
gold command cell run successfully 
what next
```

### Prompt 24
```
cell 5-7 run scuuessfully and showing table in output
```

### Prompt 25
```
code is pushed to github
```

### Prompt 26
```
where ti find Assessment docs — reflection.md, candidate-info.md, debugging-notes.md, final-ai-usage-summary.md
```

### Prompt 27
```
now i want all the prompt is given to AI to completet this project so i can submit the prompts also 
give me all prompts in a file
```

---

## Summary

| Phase | Prompts | Main outcome |
|-------|---------|--------------|
| Scaffold | 1 | Folder structure, `.cursorrules` |
| Context & spec | 2 | `project-context.md`, `spec.md` |
| Data generation | 3 | `generate_sample_data.py`, CSVs with known defects |
| Implementation | 4–5 | Bronze, Silver, Gold, dashboard, README |
| Git/GitHub | 6–10 | Repo pushed to `Rawat-A/C1-assessment` |
| Databricks | 11–16 | Notebook setup, path config |
| Debugging | 17–22 | Unity Catalog Volumes, path/import fixes |
| Completion | 23–25 | Gold + dashboard queries validated |
| Submission | 26–27 | Assessment docs & prompt log |

**Total prompts:** 27  
**AI tool:** Cursor IDE (agent mode)  
**Project:** Databricks medallion e-commerce pipeline (Bronze → Silver → Gold → Dashboard)
