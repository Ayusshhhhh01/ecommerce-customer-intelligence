-- =============================================================================
-- SQL SCRIPT 01: Customer-Order Fact Table Construction (Indian E-Commerce)
-- Project: E-Commerce Customer Intelligence (Churn, CLV & Next-Best-Action)
-- Dataset: Synthetic Indian E-Commerce Dataset (Explicitly Labeled Synthetic)
-- Dialect: SQLite / PostgreSQL ANSI SQL Compatible
-- =============================================================================
-- BUSINESS PURPOSE:
-- Joins customers, orders, order_items, delivery_info, and reviews to create a 
-- consolidated customer-order fact table covering order totals in INR (₹), 
-- payment methods (UPI, COD, Card), city tier, delivery delays, and review scores.
-- =============================================================================

DROP TABLE IF EXISTS customer_order_fact;

CREATE TABLE customer_order_fact AS
SELECT 
    c.customer_id,
    c.city,
    c.state,
    c.city_tier,
    c.signup_date,
    o.order_id,
    o.order_date,
    o.order_status,
    o.payment_method,
    ROUND(SUM(oi.item_total), 2) AS order_total_amount,
    COUNT(oi.item_id) AS total_items,
    d.delivery_delay_days,
    r.review_score
FROM orders o
JOIN customers c 
    ON o.customer_id = c.customer_id
JOIN order_items oi 
    ON o.order_id = oi.order_id
LEFT JOIN delivery_info d 
    ON o.order_id = d.order_id
LEFT JOIN reviews r 
    ON o.order_id = r.order_id
WHERE o.order_status = 'delivered'
GROUP BY 
    c.customer_id,
    c.city,
    c.state,
    c.city_tier,
    c.signup_date,
    o.order_id,
    o.order_date,
    o.order_status,
    o.payment_method,
    d.delivery_delay_days,
    r.review_score;
