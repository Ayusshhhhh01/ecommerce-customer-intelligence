import sqlite3
import pandas as pd
import numpy as np

conn = sqlite3.connect(':memory:')

customers = pd.read_csv(r'data\customers.csv')
orders = pd.read_csv(r'data\orders.csv')
order_items = pd.read_csv(r'data\order_items.csv')
delivery = pd.read_csv(r'data\delivery_info.csv')
reviews = pd.read_csv(r'data\reviews.csv')

customers.to_sql('customers', conn, index=False)
orders.to_sql('orders', conn, index=False)
order_items.to_sql('order_items', conn, index=False)
delivery.to_sql('delivery_info', conn, index=False)
reviews.to_sql('reviews', conn, index=False)

print('[OK] Loaded synthetic Indian dataset tables into SQLite.')

# SQL 1: Customer-Order Fact Table Construction
fact_sql = """
CREATE TABLE customer_order_fact AS
SELECT 
    c.customer_id,
    c.city,
    c.state,
    c.city_tier,
    o.order_id,
    o.order_date,
    o.order_status,
    o.payment_method,
    ROUND(SUM(oi.item_total), 2) AS order_total_amount,
    COUNT(oi.item_id) AS total_items,
    d.delivery_delay_days,
    r.review_score
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
JOIN order_items oi ON o.order_id = oi.order_id
LEFT JOIN delivery_info d ON o.order_id = d.order_id
LEFT JOIN reviews r ON o.order_id = r.order_id
WHERE o.order_status = 'delivered'
GROUP BY c.customer_id, c.city, c.state, c.city_tier, o.order_id, o.order_date, o.order_status, o.payment_method;
"""
conn.execute(fact_sql)

fact_df = pd.read_sql('SELECT * FROM customer_order_fact', conn)
print(f'[OK] Customer-Order Fact Table created with {len(fact_df):,} delivered order records.')
print(f'[OK] Total Unique Customers (customer_id): {fact_df["customer_id"].nunique():,}')

def fmt_inr(amt):
    if amt >= 10000000:
        return f"Rs. {amt / 10000000:.2f}Cr"
    elif amt >= 100000:
        return f"Rs. {amt / 100000:.2f}L"
    else:
        return f"Rs. {amt:,.2f}"

tot_rev = fact_df['order_total_amount'].sum()
print(f'[OK] Total Delivered Revenue: {fmt_inr(tot_rev)} (Exact: Rs. {tot_rev:,.2f})')

# SQL 2: Inter-purchase Interval & Repeat Purchase Rate via LAG() Window Function
repeat_sql = """
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
"""
inter_df = pd.read_sql(repeat_sql, conn)
avg_days = inter_df['avg_days_between_orders'].mean()
print(f'[OK] Average Inter-Purchase Interval for Repeat Buyers: {avg_days:.1f} days')

# SQL 3: RFM Aggregations per customer_id
rfm_sql = """
SELECT 
    customer_id,
    MAX(order_date) AS last_order_date,
    MIN(order_date) AS first_order_date,
    COUNT(DISTINCT order_id) AS frequency,
    ROUND(SUM(order_total_amount), 2) AS monetary
FROM customer_order_fact
GROUP BY customer_id;
"""
rfm = pd.read_sql(rfm_sql, conn)
max_dt = pd.to_datetime(rfm['last_order_date']).max() + pd.Timedelta(days=1)
rfm['recency'] = (max_dt - pd.to_datetime(rfm['last_order_date'])).dt.days

repeat_count = (rfm['frequency'] > 1).sum()
print(f'[OK] Repeat Customers (Frequency > 1): {repeat_count:,} ({round(repeat_count / len(rfm) * 100, 2)}% repeat rate)')

# Quantile-based RFM Scoring
rfm['r_score'] = pd.qcut(rfm['recency'], q=5, labels=[5, 4, 3, 2, 1]).astype(int)
rfm['f_score'] = pd.cut(rfm['frequency'], bins=[0, 1, 2, 3, 5, 100], labels=[1, 2, 3, 4, 5]).astype(int)
rfm['m_score'] = pd.qcut(rfm['monetary'].rank(method='first'), q=5, labels=[1, 2, 3, 4, 5]).astype(int)

def assign_segment(row):
    r, f, m = row['r_score'], row['f_score'], row['m_score']
    if r >= 4 and f >= 3:
        return 'Champions'
    elif r >= 3 and f >= 2:
        return 'Loyal Customers'
    elif r >= 4 and f == 1:
        return 'New Customers'
    elif r == 3 and f == 1:
        return 'Promising / Potential Loyalists'
    elif r == 2 and f >= 2:
        return 'At-Risk'
    elif r == 1 and f >= 3:
        return "Can't Lose Them"
    elif r == 2 and f == 1:
        return 'About to Sleep'
    else:
        return 'Hibernating / Lost'

rfm['segment'] = rfm.apply(assign_segment, axis=1)

summary = rfm.groupby('segment').agg(
    customer_count=('customer_id', 'count'),
    total_revenue=('monetary', 'sum'),
    avg_recency=('recency', 'mean'),
    avg_monetary=('monetary', 'mean')
).reset_index()

summary['pct_customers'] = round((summary['customer_count'] / len(rfm)) * 100, 2)
summary['pct_revenue'] = round((summary['total_revenue'] / tot_rev) * 100, 2)
summary = summary.sort_values(by='total_revenue', ascending=False)

summary['formatted_revenue'] = summary['total_revenue'].apply(fmt_inr)
summary['formatted_avg_monetary'] = summary['avg_monetary'].apply(fmt_inr)

print('\n=== INDIAN E-COMMERCE RFM SEGMENT SUMMARY TABLE ===')
print(summary[['segment', 'customer_count', 'pct_customers', 'formatted_revenue', 'pct_revenue', 'avg_recency', 'formatted_avg_monetary']].to_string(index=False))
