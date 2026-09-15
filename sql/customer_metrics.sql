-- First draft of the customer-level analysis layer.
-- Column names will be aligned after the raw dataset is loaded.

SELECT
    customer_id,
    COUNT(DISTINCT order_id) AS order_count,
    SUM(order_value) AS total_spend,
    MAX(order_date) AS last_order_date
FROM orders
GROUP BY customer_id;

-- Next: add recency, frequency, monetary scores and cohort fields.
