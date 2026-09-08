# Databricks notebook source
# MAGIC %md
# MAGIC # E-Commerce Medallion Pipeline
# MAGIC Bronze → Silver → Gold → Dashboard preview
# MAGIC
# MAGIC **Paths:** Unity Catalog Volume (Databricks CE — Workspace is read-only for Delta writes)
# MAGIC
# MAGIC Run cells top to bottom. Update `REPO_PATH` if your clone path differs.

# COMMAND ----------

# MAGIC %md
# MAGIC ## Cell 1 — Setup

# COMMAND ----------

import os
import sys

# Update if your repo lives under Repos instead of Users
REPO_PATH = "/Workspace/Users/abhishek.rawat@tothenew.com/C1-assessment"
SRC_PATH = f"{REPO_PATH}/src"

# Writable paths on Unity Catalog Volume
DATA_PATH = "/Volumes/main/default/c1_assessment/data"
DELTA_PATH = "/Volumes/main/default/c1_assessment/delta"

os.environ["PIPELINE_DATA_PATH"] = DATA_PATH
os.environ["PIPELINE_DELTA_PATH"] = DELTA_PATH
sys.path.insert(0, SRC_PATH)

print("REPO:", REPO_PATH)
print("DATA:", DATA_PATH)
print("DELTA:", DELTA_PATH)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Cell 1b — Copy CSVs to Volume (run once)

# COMMAND ----------

dbutils.fs.mkdirs("/Volumes/main/default/c1_assessment/data")

for name in ["customers.csv", "orders.csv", "products.csv"]:
    dbutils.fs.cp(
        f"file:{REPO_PATH}/data/{name}",
        f"/Volumes/main/default/c1_assessment/data/{name}",
        True,
    )
    print(f"Copied {name}")

display(dbutils.fs.ls("/Volumes/main/default/c1_assessment/data"))

# COMMAND ----------

# MAGIC %md
# MAGIC ## Cell 2 — Bronze ingestion

# COMMAND ----------

from bronze.ingest_utils import ingest_csv_to_delta

DATA = "/Volumes/main/default/c1_assessment/data"
DELTA = "/Volumes/main/default/c1_assessment/delta"

ingest_csv_to_delta(spark, f"{DATA}/customers.csv", f"{DELTA}/bronze_customers", "customers")
ingest_csv_to_delta(spark, f"{DATA}/orders.csv", f"{DELTA}/bronze_orders", "orders")
ingest_csv_to_delta(spark, f"{DATA}/products.csv", f"{DELTA}/bronze_products", "products")

print("Bronze complete")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Cell 3 — Silver quality checks

# COMMAND ----------

from silver.create_silver_tables import create_silver_tables

create_silver_tables(spark)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Cell 4 — Gold aggregations

# COMMAND ----------

from pathlib import Path
from pipeline_config import gold_path, silver_path

REPO = REPO_PATH
GOLD_DIR = Path(f"{REPO}/src/gold")
THRESHOLD = 5000

for entity in ("customers", "orders", "products"):
    spark.read.format("delta").load(silver_path(entity)).createOrReplaceTempView(
        f"silver_{entity}"
    )

for sql_file, entity in [
    ("01_sales_by_product.sql", "sales_by_product"),
    ("02_revenue_by_customer.sql", "revenue_by_customer"),
    ("03_daily_weekly_trends.sql", "daily_weekly_trends"),
    ("04_customer_segmentation.sql", "customer_segmentation"),
]:
    sql = (GOLD_DIR / sql_file).read_text().format(high_value_threshold=THRESHOLD)
    df = spark.sql(sql)
    df.write.format("delta").mode("overwrite").save(gold_path(entity))
    print(f"gold_{entity}: {df.count()} rows")

print("Gold complete")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Cell 5 — Register Gold views (for SQL / dashboard)

# COMMAND ----------

from pipeline_config import gold_path

for entity, view in [
    ("sales_by_product", "gold_sales_by_product"),
    ("revenue_by_customer", "gold_revenue_by_customer"),
    ("daily_weekly_trends", "gold_daily_weekly_trends"),
    ("customer_segmentation", "gold_customer_segmentation"),
]:
    spark.read.format("delta").load(gold_path(entity)).createOrReplaceTempView(view)
    print(f"Registered {view}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Cell 6 — Preview Gold tables

# COMMAND ----------

display(spark.table("gold_sales_by_product").limit(10))
display(spark.table("gold_customer_segmentation"))
display(
    spark.table("gold_revenue_by_customer")
    .orderBy("total_revenue", ascending=False)
    .limit(10)
)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Cell 7 — Dashboard queries
# MAGIC Run each query below in **SQL** cells or Databricks SQL / Genie dashboard.

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Bar: revenue by category
# MAGIC SELECT
# MAGIC     category,
# MAGIC     ROUND(SUM(total_revenue), 2) AS total_revenue
# MAGIC FROM
# MAGIC     gold_sales_by_product
# MAGIC GROUP BY
# MAGIC     category
# MAGIC ORDER BY
# MAGIC     total_revenue DESC

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Pie: customer segments
# MAGIC SELECT
# MAGIC     segment_type,
# MAGIC     customer_count
# MAGIC FROM
# MAGIC     gold_customer_segmentation
# MAGIC ORDER BY
# MAGIC     customer_count DESC

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Histogram: customer revenue buckets
# MAGIC SELECT
# MAGIC     CASE
# MAGIC         WHEN total_revenue < 100 THEN '0-99'
# MAGIC         WHEN total_revenue < 500 THEN '100-499'
# MAGIC         WHEN total_revenue < 1000 THEN '500-999'
# MAGIC         WHEN total_revenue < 5000 THEN '1000-4999'
# MAGIC         ELSE '5000+'
# MAGIC     END AS revenue_bucket,
# MAGIC     COUNT(customer_id) AS customer_count
# MAGIC FROM
# MAGIC     gold_revenue_by_customer
# MAGIC GROUP BY
# MAGIC     1
# MAGIC ORDER BY
# MAGIC     1

# COMMAND ----------

# MAGIC %md
# MAGIC ## Optional — Unity Catalog views for Genie / AI BI Dashboard
# MAGIC Run in SQL Editor to expose Gold tables to Genie (`@main.ecommerce.gold_*`).

# COMMAND ----------

# MAGIC %sql
# MAGIC CREATE SCHEMA IF NOT EXISTS main.ecommerce;
# MAGIC
# MAGIC CREATE OR REPLACE VIEW main.ecommerce.gold_sales_by_product AS
# MAGIC SELECT * FROM delta.`/Volumes/main/default/c1_assessment/delta/gold_sales_by_product`;
# MAGIC
# MAGIC CREATE OR REPLACE VIEW main.ecommerce.gold_revenue_by_customer AS
# MAGIC SELECT * FROM delta.`/Volumes/main/default/c1_assessment/delta/gold_revenue_by_customer`;
# MAGIC
# MAGIC CREATE OR REPLACE VIEW main.ecommerce.gold_customer_segmentation AS
# MAGIC SELECT * FROM delta.`/Volumes/main/default/c1_assessment/delta/gold_customer_segmentation`;
# MAGIC
# MAGIC CREATE OR REPLACE VIEW main.ecommerce.gold_daily_weekly_trends AS
# MAGIC SELECT * FROM delta.`/Volumes/main/default/c1_assessment/delta/gold_daily_weekly_trends`;
