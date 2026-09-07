-- Purpose: Gold aggregation — sales metrics by product from Silver PASS completed orders.
-- Inputs:  silver_orders, silver_products temp views.
-- Outputs: gold_sales_by_product table columns per spec.

SELECT
    p.product_id,
    p.product_name,
    p.category,
    COUNT(o.order_id) AS total_orders,
    ROUND(SUM(o.total_amount), 2) AS total_revenue,
    ROUND(AVG(o.total_amount), 2) AS avg_order_value
FROM
    silver_orders AS o
INNER JOIN
    silver_products AS p
    ON o.product_id = p.product_id
WHERE
    o.quality_check_result = 'PASS'
    AND p.quality_check_result = 'PASS'
    AND o.order_status = 'Completed'
GROUP BY
    p.product_id,
    p.product_name,
    p.category
ORDER BY
    total_revenue DESC
