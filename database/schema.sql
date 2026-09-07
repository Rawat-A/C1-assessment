-- Purpose: Reference DDL for Bronze, Silver, and Gold Delta tables.
-- Run in Databricks SQL or adapt paths to your catalog.

-- Bronze (raw + ingest metadata)
CREATE TABLE IF NOT EXISTS bronze_customers (
    customer_id INT,
    customer_name STRING,
    email STRING,
    country STRING,
    signup_date DATE,
    customer_segment STRING,
    lifetime_value DECIMAL(18, 2),
    _ingest_timestamp TIMESTAMP
) USING DELTA;

CREATE TABLE IF NOT EXISTS bronze_orders (
    order_id INT,
    customer_id INT,
    order_date DATE,
    product_id INT,
    quantity INT,
    unit_price DECIMAL(18, 2),
    total_amount DECIMAL(18, 2),
    order_status STRING,
    payment_date DATE,
    _ingest_timestamp TIMESTAMP
) USING DELTA;

CREATE TABLE IF NOT EXISTS bronze_products (
    product_id INT,
    product_name STRING,
    category STRING,
    price DECIMAL(18, 2),
    cost DECIMAL(18, 2),
    stock_quantity INT,
    reorder_level INT,
    _ingest_timestamp TIMESTAMP
) USING DELTA;

-- Silver (all Bronze columns + quality flag; no rows deleted)
CREATE TABLE IF NOT EXISTS silver_customers (
    customer_id INT,
    customer_name STRING,
    email STRING,
    country STRING,
    signup_date DATE,
    customer_segment STRING,
    lifetime_value DECIMAL(18, 2),
    _ingest_timestamp TIMESTAMP,
    quality_check_result STRING
) USING DELTA;

CREATE TABLE IF NOT EXISTS silver_orders (
    order_id INT,
    customer_id INT,
    order_date DATE,
    product_id INT,
    quantity INT,
    unit_price DECIMAL(18, 2),
    total_amount DECIMAL(18, 2),
    order_status STRING,
    payment_date DATE,
    _ingest_timestamp TIMESTAMP,
    quality_check_result STRING
) USING DELTA;

CREATE TABLE IF NOT EXISTS silver_products (
    product_id INT,
    product_name STRING,
    category STRING,
    price DECIMAL(18, 2),
    cost DECIMAL(18, 2),
    stock_quantity INT,
    reorder_level INT,
    _ingest_timestamp TIMESTAMP,
    quality_check_result STRING
) USING DELTA;

-- Gold aggregations
CREATE TABLE IF NOT EXISTS gold_sales_by_product (
    product_id INT,
    product_name STRING,
    category STRING,
    total_orders BIGINT,
    total_revenue DECIMAL(18, 2),
    avg_order_value DECIMAL(18, 2)
) USING DELTA;

CREATE TABLE IF NOT EXISTS gold_revenue_by_customer (
    customer_id INT,
    customer_name STRING,
    customer_segment STRING,
    total_orders BIGINT,
    total_revenue DECIMAL(18, 2),
    avg_order_value DECIMAL(18, 2),
    lifetime_value_actual DECIMAL(18, 2)
) USING DELTA;

CREATE TABLE IF NOT EXISTS gold_daily_weekly_trends (
    grain STRING,
    period_start DATE,
    total_orders BIGINT,
    total_revenue DECIMAL(18, 2)
) USING DELTA;

CREATE TABLE IF NOT EXISTS gold_customer_segmentation (
    segment_type STRING,
    customer_count BIGINT,
    avg_revenue DECIMAL(18, 2),
    total_revenue DECIMAL(18, 2)
) USING DELTA;
