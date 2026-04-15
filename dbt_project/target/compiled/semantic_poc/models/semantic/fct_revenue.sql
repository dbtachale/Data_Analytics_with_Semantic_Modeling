

-- This is the single source of truth for revenue.
-- All consumers (BI, LLM, APIs) should query THIS, not raw tables.


WITH orders AS (
    SELECT
        order_id,
        customer_id,
        product_id,
        order_date,
        DATE_TRUNC('month', order_date)  AS order_month,
        DATE_TRUNC('quarter', order_date) AS order_quarter,
        net_amount,
        gross_amount,
        discount,
        status,
        region
    FROM raw_orders
    WHERE status = 'completed'   -- REVENUE = completed orders only
),
enriched AS (
    SELECT
        o.*,
        c.segment      AS customer_segment,
        c.customer_name,
        p.category     AS product_category,
        p.list_price,
        p.cost,
        (o.net_amount - p.cost) AS gross_profit
    FROM orders o
    LEFT JOIN raw_customers c ON o.customer_id = c.customer_id
    LEFT JOIN raw_products  p ON o.product_id  = p.product_id
)
SELECT * FROM enriched