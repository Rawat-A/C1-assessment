-- Purpose: Gold aggregation — revenue metrics by customer from Silver PASS completed orders.
-- Inputs:  silver_orders, silver_customers temp views.
-- Outputs: gold_revenue_by_customer table columns per spec.

SELECT
    c.customer_id,
    c.customer_name,
    c.customer_segment,
    COUNT(o.order_id) AS total_orders,
    ROUND(SUM(o.total_amount), 2) AS total_revenue,
    ROUND(AVG(o.total_amount), 2) AS avg_order_value,
    ROUND(SUM(o.total_amount), 2) AS lifetime_value_actual
FROM
    silver_orders AS o
INNER JOIN
    silver_customers AS c
    ON o.customer_id = c.customer_id
WHERE
    o.quality_check_result = 'PASS'
    AND c.quality_check_result = 'PASS'
    AND o.order_status = 'Completed'
GROUP BY
    c.customer_id,
    c.customer_name,
    c.customer_segment
ORDER BY
    total_revenue DESC
