-- Purpose: Gold aggregation — customer segmentation (High-Value / Repeat / One-Time / Inactive).
-- Inputs:  silver_customers, silver_orders temp views; HIGH_VALUE_THRESHOLD set in Python.
-- Outputs: gold_customer_segmentation table columns per spec.

WITH customer_revenue AS (
    SELECT
        o.customer_id,
        COUNT(o.order_id) AS completed_orders,
        COALESCE(SUM(o.total_amount), 0) AS total_revenue
    FROM
        silver_orders AS o
    WHERE
        o.quality_check_result = 'PASS'
        AND o.order_status = 'Completed'
    GROUP BY
        o.customer_id
),
all_customers AS (
    SELECT
        c.customer_id
    FROM
        silver_customers AS c
    WHERE
        c.quality_check_result = 'PASS'
),
classified AS (
    SELECT
        ac.customer_id,
        COALESCE(cr.completed_orders, 0) AS completed_orders,
        COALESCE(cr.total_revenue, 0) AS total_revenue,
        CASE
            WHEN COALESCE(cr.total_revenue, 0) >= {high_value_threshold} THEN 'High-Value'
            WHEN COALESCE(cr.completed_orders, 0) >= 2 THEN 'Repeat'
            WHEN COALESCE(cr.completed_orders, 0) = 1 THEN 'One-Time'
            ELSE 'Inactive'
        END AS segment_type
    FROM
        all_customers AS ac
    LEFT JOIN
        customer_revenue AS cr
        ON ac.customer_id = cr.customer_id
)
SELECT
    segment_type,
    COUNT(customer_id) AS customer_count,
    ROUND(AVG(total_revenue), 2) AS avg_revenue,
    ROUND(SUM(total_revenue), 2) AS total_revenue
FROM
    classified
GROUP BY
    segment_type
ORDER BY
    total_revenue DESC
