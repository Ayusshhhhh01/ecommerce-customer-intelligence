-- =============================================================================
-- SQL SCRIPT 02: RFM Aggregations & Repeat Purchase Metrics (Indian E-Commerce)
-- Project: E-Commerce Customer Intelligence (Churn, CLV & Next-Best-Action)
-- Dialect: SQLite / PostgreSQL ANSI SQL Compatible
-- =============================================================================
-- BUSINESS PURPOSE:
-- Computes per-customer Recency (days since last purchase), Frequency (total orders),
-- Monetary Value (total spend in ₹), repeat purchase rate, and inter-purchase interval 
-- using SQL window functions (LAG).
-- =============================================================================

-- 1. Base RFM Aggregations per customer_id
SELECT 
    customer_id,
    city_tier,
    MIN(order_date) AS first_order_date,
    MAX(order_date) AS last_order_date,
    COUNT(DISTINCT order_id) AS frequency,
    ROUND(SUM(order_total_amount), 2) AS monetary,
    ROUND(AVG(order_total_amount), 2) AS avg_order_value
FROM customer_order_fact
GROUP BY customer_id, city_tier;

-- 2. Inter-Purchase Days Calculation using LAG() Window Function
WITH customer_orders_ranked AS (
    SELECT 
        customer_id,
        order_date,
        LAG(order_date) OVER (
            PARTITION BY customer_id 
            ORDER BY order_date
        ) AS prev_order_date
    FROM customer_order_fact
)
SELECT 
    customer_id,
    ROUND(AVG(JULIANDAY(order_date) - JULIANDAY(prev_order_date)), 2) AS avg_days_between_orders
FROM customer_orders_ranked
WHERE prev_order_date IS NOT NULL
GROUP BY customer_id;

-- 3. Repeat Purchase Rate Summary
SELECT 
    COUNT(DISTINCT customer_id) AS total_customers,
    SUM(CASE WHEN frequency > 1 THEN 1 ELSE 0 END) AS repeat_customers,
    ROUND(100.0 * SUM(CASE WHEN frequency > 1 THEN 1 ELSE 0 END) / COUNT(DISTINCT customer_id), 2) AS repeat_purchase_rate_pct
FROM (
    SELECT customer_id, COUNT(DISTINCT order_id) AS frequency
    FROM customer_order_fact
    GROUP BY customer_id
);
