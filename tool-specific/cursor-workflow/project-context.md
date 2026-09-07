# Project context — Databricks e-commerce medallion pipeline

This repo builds a Databricks Community Edition pipeline for an e-commerce company: ingest `customers.csv`, `orders.csv`, and `products.csv` from a local/DBFS path, land them as Bronze Delta (raw), clean and flag quality in Silver (never drop rows), then publish Gold sales/revenue/segment tables for a SQL dashboard. Goal: trusted, auditable sales analytics from source CSVs to KPIs.

**Stack:** Databricks Community Edition, PySpark, Delta Lake, SQL. Config vars for paths (no hardcoded paths). PEP 8, type hints, docstrings, script header (purpose/inputs/outputs). SQL: uppercase keywords, one clause per line.

## Source schemas

**customers** — `customer_id` INT PK, `customer_name` STRING, `email` STRING, `country` STRING, `signup_date` DATE, `customer_segment` STRING (`Premium`/`Standard`/`Basic`), `lifetime_value` DECIMAL

**orders** — `order_id` INT PK, `customer_id` INT FK → customers, `order_date` DATE, `product_id` INT FK → products, `quantity` INT, `unit_price` DECIMAL, `total_amount` DECIMAL, `order_status` STRING (`Pending`/`Completed`/`Cancelled`), `payment_date` DATE nullable

**products** — `product_id` INT PK, `product_name` STRING, `category` STRING, `price` DECIMAL, `cost` DECIMAL, `stock_quantity` INT, `reorder_level` INT

## Silver quality (flag only)

Add `quality_check_result` (`PASS`/`FAIL` + reason). Never delete rows. Four required checks:

1. **Completeness** — required fields non-null/non-empty (incl. PKs; `payment_date` may be null).
2. **Uniqueness** — unique `customer_id`, `order_id`, `product_id`.
3. **Referential integrity** — `orders.customer_id` exists in customers; `orders.product_id` exists in products.
4. **Business logic** — `quantity` > 0; `unit_price`/`total_amount`/`price`/`cost` ≥ 0; `total_amount` ≈ `quantity * unit_price`; `order_status` and `customer_segment` in allowed sets; Completed orders should have `payment_date`; Cancelled may have null payment.

## Gold aggregations

1. **Sales by Product** — `product_id`, `product_name`, `category`, `total_orders`, `total_revenue`, `avg_order_value`
2. **Revenue by Customer** — `customer_id`, `customer_name`, `customer_segment`, `total_orders`, `total_revenue`, `avg_order_value`, `lifetime_value_actual`
3. **Customer Segmentation** — `segment_type` (`High-Value`/`Repeat`/`One-Time`/`Inactive`), `customer_count`, `avg_revenue`, `total_revenue`

Prefer Completed orders for revenue unless a script documents otherwise. Gold may filter to Silver `PASS` rows for metrics while keeping FAIL rows in Silver for audit.
