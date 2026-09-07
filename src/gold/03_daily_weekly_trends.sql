-- Purpose: Gold aggregation — daily and weekly sales/revenue trends.
-- Inputs:  silver_orders temp view.
-- Outputs: gold_daily_weekly_trends with grain, period_start, orders, revenue.

SELECT
    'daily' AS grain,
    CAST(o.order_date AS DATE) AS period_start,
    COUNT(o.order_id) AS total_orders,
    ROUND(SUM(o.total_amount), 2) AS total_revenue
FROM
    silver_orders AS o
WHERE
    o.quality_check_result = 'PASS'
    AND o.order_status = 'Completed'
GROUP BY
    CAST(o.order_date AS DATE)

UNION ALL

SELECT
    'weekly' AS grain,
    DATE_TRUNC('week', o.order_date) AS period_start,
    COUNT(o.order_id) AS total_orders,
    ROUND(SUM(o.total_amount), 2) AS total_revenue
FROM
    silver_orders AS o
WHERE
    o.quality_check_result = 'PASS'
    AND o.order_status = 'Completed'
GROUP BY
    DATE_TRUNC('week', o.order_date)

ORDER BY
    grain,
    period_start
