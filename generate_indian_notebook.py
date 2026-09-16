import json
import os

nb = {
    'cells': [],
    'metadata': {
        'kernelspec': {'display_name': 'Python 3', 'language': 'python', 'name': 'python3'},
        'language_info': {'name': 'python', 'version': '3.12.10'}
    },
    'nbformat': 4,
    'nbformat_minor': 2
}

def add_md(text):
    nb['cells'].append({'cell_type': 'markdown', 'metadata': {}, 'source': text.splitlines(keepends=True)})

def add_code(text):
    nb['cells'].append({'cell_type': 'code', 'execution_count': None, 'metadata': {}, 'outputs': [], 'source': text.splitlines(keepends=True)})

# Title & Introduction
add_md("""# E-Commerce Customer Intelligence: Churn, CLV & Next-Best-Action
**Author:** Product Analyst / Business Analyst Candidate  
**Target Roles:** Product Analyst, Business Analyst, Data Analyst  
**Dataset:** Synthetic Indian E-Commerce Dataset  

---

## 📌 Business Context & Objective
Leadership in an e-commerce platform needs actionable answers to four core customer lifecycle questions:
1. **Which customers are going to leave?** (Churn Prediction)
2. **How valuable are they?** (RFM & Customer Lifetime Value in ₹ Lakhs/Crores)
3. **Why are they leaving?** (SHAP Feature Drivers, Payment Methods & Delivery Friction)
4. **What should we do about them?** (Prescriptive Next-Best-Action Framework)

---

## 🚨 DATASET DISCLOSURE (SYNTHETIC DATA)
> **Explicit Notice:** This dataset is synthetically generated to model realistic Indian e-commerce behavior patterns (including festival spikes like Diwali, UPI/COD payment distributions, metro vs tier-2 delivery latency, and return rates). **It is NOT derived from any real company's private transaction data.**
""")

# Step 1: SQL Layer & Fact Table Construction
add_md("""## 1. SQL Layer & Customer-Order Fact Table Construction

### 📖 How This Works (Interview Explanation)
In Indian e-commerce analytics, customer transactions span multiple operational domains (orders, payments, logistics delivery latency, review scores). We construct a unified `customer_order_fact` table in **SQLite** by joining `customers`, `orders`, `order_items`, `delivery_info`, and `reviews`. We also utilize SQL window functions (`LAG()`) to calculate customer repeat purchase rates and average inter-purchase intervals (days between consecutive orders).
""")

add_code("""import sqlite3
import pandas as pd
import numpy as np

# Helper function to format INR numbers into Lakhs (L) and Crores (Cr)
def format_inr(amount):
    if amount >= 10000000:
        return f"Rs. {amount / 10000000:.2f}Cr"
    elif amount >= 100000:
        return f"Rs. {amount / 100000:.2f}L"
    else:
        return f"Rs. {amount:,.2f}"

# Load synthetic Indian dataset tables into SQLite in-memory database
conn = sqlite3.connect(':memory:')

customers = pd.read_csv('../data/customers.csv')
orders = pd.read_csv('../data/orders.csv')
order_items = pd.read_csv('../data/order_items.csv')
delivery = pd.read_csv('../data/delivery_info.csv')
reviews = pd.read_csv('../data/reviews.csv')

customers.to_sql('customers', conn, index=False, if_exists='replace')
orders.to_sql('orders', conn, index=False, if_exists='replace')
order_items.to_sql('order_items', conn, index=False, if_exists='replace')
delivery.to_sql('delivery_info', conn, index=False, if_exists='replace')
reviews.to_sql('reviews', conn, index=False, if_exists='replace')

print(' [OK] Loaded 5 synthetic Indian dataset tables into SQLite database.')
""")

add_code("""# Execute SQL 01: Create Customer-Order Fact Table
fact_sql = \"\"\"
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
JOIN customers c ON o.customer_id = c.customer_id
JOIN order_items oi ON o.order_id = oi.order_id
LEFT JOIN delivery_info d ON o.order_id = d.order_id
LEFT JOIN reviews r ON o.order_id = r.order_id
WHERE o.order_status = 'delivered'
GROUP BY c.customer_id, c.city, c.state, c.city_tier, c.signup_date, o.order_id, o.order_date, o.order_status, o.payment_method;
\"\"\"
conn.execute('DROP TABLE IF EXISTS customer_order_fact;')
conn.execute(fact_sql)

fact_df = pd.read_sql('SELECT * FROM customer_order_fact', conn)
tot_rev = fact_df['order_total_amount'].sum()

print(f' [OK] Customer-Order Fact Table created with {len(fact_df):,} delivered order records.')
print(f' [OK] Total Unique Delivered Customers: {fact_df["customer_id"].nunique():,}')
print(f' [OK] Total Delivered Revenue: {format_inr(tot_rev)} (Exact: Rs. {tot_rev:,.2f})')
""")

add_code("""# Execute SQL 02: Inter-Purchase Days & Repeat Purchase Rate via LAG() Window Function
repeat_sql = \"\"\"
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
\"\"\"
inter_purchase_df = pd.read_sql(repeat_sql, conn)
avg_days = inter_purchase_df['avg_days_between_orders'].mean()
print(f' [OK] Average Inter-Purchase Interval for Repeat Buyers: {avg_days:.1f} days')
""")

# Step 2: RFM Segmentation
add_md("""## 2. RFM Segmentation & Revenue Contribution

### 📖 How This Works (Interview Explanation)
**RFM Segmentation** ranks customers based on their transactional history:
1. **Recency (R):** Days since the customer's last order (1–5 scale, 5 = most recent).
2. **Frequency (F):** Total number of completed orders (1–5 scale based on transaction count).
3. **Monetary (M):** Total monetary spend in ₹ INR (1–5 scale, 5 = highest spend).

#### Segment Definitions:
* **Champions:** R ≥ 4, F ≥ 3 (Top recent, high frequency, highest spenders).
* **Loyal Customers:** R ≥ 3, F ≥ 2 (Reliable repeat buyers).
* **New Customers:** R ≥ 4, F = 1 (Recent first-time buyers).
* **Promising / Potential Loyalists:** R = 3, F = 1 (Mid recency first-time buyers).
* **At-Risk:** R = 2, F ≥ 2 (Repeat buyers who haven't purchased recently).
* **Can't Lose Them:** R = 1, F ≥ 3 (High-frequency historical buyers who are slipping away).
* **About to Sleep:** R = 2, F = 1 (Single buyers showing signs of inactivity).
* **Hibernating / Lost:** R = 1, F = 1 (Dormant single buyers).
""")

add_code("""# Compute RFM metrics per customer_id
rfm_sql = \"\"\"
SELECT 
    customer_id,
    MAX(order_date) AS last_order_date,
    MIN(order_date) AS first_order_date,
    COUNT(DISTINCT order_id) AS frequency,
    ROUND(SUM(order_total_amount), 2) AS monetary
FROM customer_order_fact
GROUP BY customer_id;
\"\"\"
rfm = pd.read_sql(rfm_sql, conn)

max_dt = pd.to_datetime(rfm['last_order_date']).max() + pd.Timedelta(days=1)
rfm['recency'] = (max_dt - pd.to_datetime(rfm['last_order_date'])).dt.days

# Score Recency, Frequency, and Monetary (1-5 scale)
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

# Summary of RFM Segments with INR Lakh/Crore Formatting
segment_summary = rfm.groupby('segment').agg(
    customer_count=('customer_id', 'count'),
    total_revenue=('monetary', 'sum'),
    avg_recency=('recency', 'mean'),
    avg_monetary=('monetary', 'mean')
).reset_index()

total_cust = len(rfm)
total_rev = rfm['monetary'].sum()

segment_summary['pct_customers'] = round((segment_summary['customer_count'] / total_cust) * 100, 2)
segment_summary['pct_revenue'] = round((segment_summary['total_revenue'] / total_rev) * 100, 2)
segment_summary = segment_summary.sort_values(by='total_revenue', ascending=False)

segment_summary['formatted_revenue'] = segment_summary['total_revenue'].apply(format_inr)
segment_summary['formatted_avg_monetary'] = segment_summary['avg_monetary'].apply(format_inr)

print('=== INDIAN E-COMMERCE RFM SEGMENT SUMMARY TABLE ===')
print(segment_summary[['segment', 'customer_count', 'pct_customers', 'formatted_revenue', 'pct_revenue', 'avg_recency', 'formatted_avg_monetary']].to_string(index=False))
""")

os.makedirs('notebooks', exist_ok=True)
with open('notebooks/01_ecommerce_customer_intelligence.ipynb', 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=2)

print('[SUCCESS] Successfully generated notebooks/01_ecommerce_customer_intelligence.ipynb')
