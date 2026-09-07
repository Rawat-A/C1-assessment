-- Purpose: Dashboard SQL queries for Databricks SQL visualizations.
-- Inputs:  Gold Delta tables (register as views or query paths).
-- Outputs: Result sets for bar chart, histogram, and pie chart.

-- Query 1 (BAR): Total revenue by product category
SELECT
    category,
    ROUND(SUM(total_revenue), 2) AS total_revenue
FROM
    gold_sales_by_product
GROUP BY
    category
ORDER BY
    total_revenue DESC;

-- Query 2 (HISTOGRAM): Distribution of customer total_revenue in buckets
SELECT
    CASE
        WHEN total_revenue < 100 THEN '0-99'
        WHEN total_revenue < 500 THEN '100-499'
        WHEN total_revenue < 1000 THEN '500-999'
        WHEN total_revenue < 5000 THEN '1000-4999'
        ELSE '5000+'
    END AS revenue_bucket,
    COUNT(customer_id) AS customer_count
FROM
    gold_revenue_by_customer
GROUP BY
    CASE
        WHEN total_revenue < 100 THEN '0-99'
        WHEN total_revenue < 500 THEN '100-499'
        WHEN total_revenue < 1000 THEN '500-999'
        WHEN total_revenue < 5000 THEN '1000-4999'
        ELSE '5000+'
    END
ORDER BY
    revenue_bucket;

-- Query 3 (PIE): Customer count share by segment_type
SELECT
    segment_type,
    customer_count,
    ROUND(
        customer_count * 100.0 / SUM(customer_count) OVER (),
        2
    ) AS pct_of_customers
FROM
    gold_customer_segmentation
ORDER BY
    customer_count DESC;

-- Query 4 (BONUS BAR): Top 10 customers by total revenue
SELECT
    customer_name,
    customer_segment,
    total_revenue
FROM
    gold_revenue_by_customer
ORDER BY
    total_revenue DESC
LIMIT 10;
