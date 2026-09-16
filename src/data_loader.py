"""
Data Loader & Fact Table Construction Module
Project: E-Commerce Customer Intelligence
"""

import sqlite3
import pandas as pd

def load_data_and_create_fact(data_dir=r'data'):
    conn = sqlite3.connect(':memory:')
    
    customers = pd.read_csv(f'{data_dir}/customers.csv')
    orders = pd.read_csv(f'{data_dir}/orders.csv')
    order_items = pd.read_csv(f'{data_dir}/order_items.csv')
    delivery = pd.read_csv(f'{data_dir}/delivery_info.csv')
    reviews = pd.read_csv(f'{data_dir}/reviews.csv')
    
    customers.to_sql('customers', conn, index=False, if_exists='replace')
    orders.to_sql('orders', conn, index=False, if_exists='replace')
    order_items.to_sql('order_items', conn, index=False, if_exists='replace')
    delivery.to_sql('delivery_info', conn, index=False, if_exists='replace')
    reviews.to_sql('reviews', conn, index=False, if_exists='replace')
    
    fact_sql = """
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
        COUNT(DISTINCT oi.category) AS order_category_count,
        d.delivery_delay_days,
        r.review_score
    FROM orders o
    JOIN customers c ON o.customer_id = c.customer_id
    JOIN order_items oi ON o.order_id = oi.order_id
    LEFT JOIN delivery_info d ON o.order_id = d.order_id
    LEFT JOIN reviews r ON o.order_id = r.order_id
    WHERE o.order_status = 'delivered'
    GROUP BY c.customer_id, c.city, c.state, c.city_tier, c.signup_date, o.order_id, o.order_date, o.order_status, o.payment_method;
    """
    conn.execute('DROP TABLE IF EXISTS customer_order_fact;')
    conn.execute(fact_sql)
    
    fact_df = pd.read_sql('SELECT * FROM customer_order_fact', conn)
    return fact_df, conn

def format_inr(amount):
    if amount >= 10000000:
        return f"Rs. {amount / 10000000:.2f}Cr"
    elif amount >= 100000:
        return f"Rs. {amount / 100000:.2f}L"
    else:
        return f"Rs. {amount:,.2f}"
