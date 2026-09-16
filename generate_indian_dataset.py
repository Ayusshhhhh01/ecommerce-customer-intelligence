"""
Synthetic Indian E-Commerce Dataset Generator
Project: E-Commerce Customer Intelligence (Churn, CLV & Next-Best-Action)
Author: Antigravity Assistant

DISCLOSURE:
This dataset is synthetically generated to model realistic Indian e-commerce behavior patterns;
it is not derived from any real company's transaction data.
"""

import numpy as np
import pandas as pd
import random
import os
from datetime import datetime, timedelta

# Set fixed seed for perfect reproducibility
np.random.seed(42)
random.seed(42)

out_dir = r"D:\Ssshhhh\Projexts\E commerce\data"
os.makedirs(out_dir, exist_ok=True)

print("Starting generation of synthetic Indian E-Commerce dataset...")

# 1. GENERATE CUSTOMERS (20,000 Unique Customers)
NUM_CUSTOMERS = 20000

metro_cities = [
    ('Mumbai', 'Maharashtra', 'Tier 1'),
    ('Delhi NCR', 'Delhi', 'Tier 1'),
    ('Bangalore', 'Karnataka', 'Tier 1'),
    ('Hyderabad', 'Telangana', 'Tier 1'),
    ('Chennai', 'Tamil Nadu', 'Tier 1'),
    ('Kolkata', 'West Bengal', 'Tier 1'),
    ('Pune', 'Maharashtra', 'Tier 1')
]

tier2_cities = [
    ('Jaipur', 'Rajasthan', 'Tier 2'),
    ('Lucknow', 'Uttar Pradesh', 'Tier 2'),
    ('Ahmedabad', 'Gujarat', 'Tier 2'),
    ('Chandigarh', 'Punjab', 'Tier 2'),
    ('Kochi', 'Kerala', 'Tier 2'),
    ('Indore', 'Madhya Pradesh', 'Tier 2'),
    ('Patna', 'Bihar', 'Tier 2'),
    ('Bhopal', 'Madhya Pradesh', 'Tier 2'),
    ('Coimbatore', 'Tamil Nadu', 'Tier 2'),
    ('Nagpur', 'Maharashtra', 'Tier 2'),
    ('Bhubaneswar', 'Odisha', 'Tier 2'),
    ('Visakhapatnam', 'Andhra Pradesh', 'Tier 2')
]

all_cities = metro_cities + tier2_cities
city_weights = [0.65 / len(metro_cities)] * len(metro_cities) + [0.35 / len(tier2_cities)] * len(tier2_cities)

customer_ids = [f"CUST-{10000 + i}" for i in range(NUM_CUSTOMERS)]

selected_indices = np.random.choice(len(all_cities), size=NUM_CUSTOMERS, p=city_weights)
selected_cities = [all_cities[i][0] for i in selected_indices]
selected_states = [all_cities[i][1] for i in selected_indices]
selected_tiers = [all_cities[i][2] for i in selected_indices]

# Signup dates spread from Jan 1, 2024 to Dec 31, 2025
start_date = datetime(2024, 1, 1)
signup_days = np.random.randint(0, 700, size=NUM_CUSTOMERS)
signup_dates = [start_date + timedelta(days=int(d)) for d in signup_days]

customers_df = pd.DataFrame({
    'customer_id': customer_ids,
    'city': selected_cities,
    'state': selected_states,
    'city_tier': selected_tiers,
    'signup_date': [d.strftime('%Y-%m-%d') for d in signup_dates]
})

print(f"Generated {len(customers_df):,} customers.")

# 2. GENERATE ORDERS (Targeting ~25.8% Repeat Rate for realistic Horizontal E-Commerce)
customer_order_counts = np.ones(NUM_CUSTOMERS, dtype=int)
repeat_tier_prob = np.where(customers_df['city_tier'] == 'Tier 1', 0.28, 0.15)
repeat_eligible = np.random.choice(NUM_CUSTOMERS, size=5400, replace=False, p=repeat_tier_prob / repeat_tier_prob.sum())

for idx in repeat_eligible:
    customer_order_counts[idx] += np.random.choice([1, 2, 3], p=[0.70, 0.22, 0.08])

order_customer_list = []
for idx, count in enumerate(customer_order_counts):
    order_customer_list.extend([customer_ids[idx]] * count)

random.shuffle(order_customer_list)
NUM_ORDERS = len(order_customer_list)

# Generate order dates with seasonal festival spikes
date_pool = []
current = datetime(2024, 1, 1)
end_dt = datetime(2025, 12, 31)

while current <= end_dt:
    weight = 1.0
    if (current.month == 10 and current.day >= 15) or (current.month == 11 and current.day <= 15):
        weight = 3.5
    elif current.month == 1 and 20 <= current.day <= 28:
        weight = 2.5
    elif current.month == 8 and 10 <= current.day <= 18:
        weight = 2.0
    
    date_pool.append((current, weight))
    current += timedelta(days=1)

dates, weights = zip(*date_pool)
weights = np.array(weights) / sum(weights)

sampled_date_indices = np.random.choice(len(dates), size=NUM_ORDERS, p=weights)
order_dates = [dates[i] for i in sampled_date_indices]

cust_signup_dict = dict(zip(customers_df['customer_id'], signup_dates))
adjusted_order_dates = []
for cid, od in zip(order_customer_list, order_dates):
    sdate = cust_signup_dict[cid]
    if od < sdate:
        od = sdate + timedelta(days=int(np.random.randint(0, 30)))
    adjusted_order_dates.append(od)

order_ids = [f"ORD-{100000 + i}" for i in range(NUM_ORDERS)]

payment_methods = np.random.choice(
    ['UPI', 'COD', 'Credit Card', 'Net Banking', 'Wallet'],
    size=NUM_ORDERS,
    p=[0.55, 0.25, 0.12, 0.05, 0.03]
)

order_statuses = []
for pm in payment_methods:
    if pm == 'COD':
        status = np.random.choice(['delivered', 'cancelled', 'returned'], p=[0.80, 0.12, 0.08])
    else:
        status = np.random.choice(['delivered', 'cancelled', 'returned'], p=[0.94, 0.04, 0.02])
    order_statuses.append(status)

orders_df = pd.DataFrame({
    'order_id': order_ids,
    'customer_id': order_customer_list,
    'order_date': [d.strftime('%Y-%m-%d %H:%M:%S') for d in adjusted_order_dates],
    'order_status': order_statuses,
    'payment_method': payment_methods
})

print(f"Generated {len(orders_df):,} orders.")

# 3. GENERATE ORDER ITEMS
categories = ['Electronics', 'Apparel', 'Groceries', 'Home & Kitchen', 'Beauty & Personal Care']
cat_p = [0.25, 0.35, 0.20, 0.12, 0.08]

price_ranges = {
    'Electronics': (1500, 15000),
    'Apparel': (400, 2500),
    'Groceries': (200, 1200),
    'Home & Kitchen': (500, 4500),
    'Beauty & Personal Care': (250, 1800)
}

order_items_list = []
for oid in order_ids:
    num_items = np.random.choice([1, 2, 3], p=[0.75, 0.20, 0.05])
    for item_idx in range(1, num_items + 1):
        cat = np.random.choice(categories, p=cat_p)
        p_min, p_max = price_ranges[cat]
        price = round(np.random.uniform(p_min, p_max), 2)
        qty = np.random.choice([1, 2], p=[0.90, 0.10])
        product_id = f"PROD-{cat[:3].upper()}-{np.random.randint(100, 999)}"
        order_items_list.append({
            'order_id': oid,
            'item_id': item_idx,
            'product_id': product_id,
            'category': cat,
            'price': price,
            'quantity': qty,
            'item_total': round(price * qty, 2)
        })

order_items_df = pd.DataFrame(order_items_list)
print(f"Generated {len(order_items_df):,} order item records.")

# 4. GENERATE DELIVERY INFO
cust_tier_dict = dict(zip(customers_df['customer_id'], customers_df['city_tier']))

delivery_list = []
for oid, cid, od_str, status in zip(orders_df['order_id'], orders_df['customer_id'], orders_df['order_date'], orders_df['order_status']):
    od = datetime.strptime(od_str, '%Y-%m-%d %H:%M:%S')
    tier = cust_tier_dict[cid]
    
    promised_days = 3 if tier == 'Tier 1' else 6
    promised_date = od + timedelta(days=promised_days)
    
    if status == 'delivered':
        if tier == 'Tier 1':
            delay = np.random.choice([0, 1, 2, 3], p=[0.70, 0.20, 0.07, 0.03])
        else:
            delay = np.random.choice([0, 1, 2, 3, 5], p=[0.50, 0.25, 0.15, 0.07, 0.03])
        actual_date = promised_date + timedelta(days=int(delay))
        delivery_list.append({
            'order_id': oid,
            'promised_delivery_date': promised_date.strftime('%Y-%m-%d'),
            'actual_delivery_date': actual_date.strftime('%Y-%m-%d'),
            'delivery_delay_days': delay
        })
    else:
        delivery_list.append({
            'order_id': oid,
            'promised_delivery_date': promised_date.strftime('%Y-%m-%d'),
            'actual_delivery_date': None,
            'delivery_delay_days': None
        })

delivery_df = pd.DataFrame(delivery_list)

# 5. GENERATE REVIEWS
reviews_list = []
for oid, status in zip(orders_df['order_id'], orders_df['order_status']):
    if status == 'delivered':
        if np.random.rand() < 0.60:
            delay = delivery_df.loc[delivery_df['order_id'] == oid, 'delivery_delay_days'].values[0]
            if delay == 0:
                score = np.random.choice([5, 4, 3], p=[0.75, 0.20, 0.05])
            elif delay <= 2:
                score = np.random.choice([4, 3, 2], p=[0.50, 0.35, 0.15])
            else:
                score = np.random.choice([2, 1], p=[0.60, 0.40])
            
            reviews_list.append({
                'order_id': oid,
                'review_score': score
            })

reviews_df = pd.DataFrame(reviews_list)

# SAVE CSV FILES
customers_df.to_csv(os.path.join(out_dir, 'customers.csv'), index=False)
orders_df.to_csv(os.path.join(out_dir, 'orders.csv'), index=False)
order_items_df.to_csv(os.path.join(out_dir, 'order_items.csv'), index=False)
delivery_df.to_csv(os.path.join(out_dir, 'delivery_info.csv'), index=False)
reviews_df.to_csv(os.path.join(out_dir, 'reviews.csv'), index=False)

print(f"[SUCCESS] All synthetic Indian e-commerce CSV files saved to {out_dir}")
