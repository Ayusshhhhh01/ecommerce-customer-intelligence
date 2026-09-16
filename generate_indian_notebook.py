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
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, roc_auc_score, confusion_matrix, ConfusionMatrixDisplay
import xgboost as xgb
import shap

# Configure plot styles
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['font.sans-serif'] = 'DejaVu Sans'
plt.rcParams['axes.edgecolor'] = '#cccccc'

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

# Step 3: Cohort Retention Analysis
add_md("""## 3. Cohort Retention Analysis & Cumulative Reconciliation

### 📖 How This Works (Interview Explanation)
**Cohort Retention Analysis** tracks how groups of customers (acquired in the same starting month) continue to purchase over time.
* **Monthly Active Rate (Heatmap):** Percentage of customers who purchased *specifically during month $k$* (showing 3.5%–5.7% active in Month 1).
* **Cumulative Repeat Retention:** Percentage of customers who have made *at least one repeat order by Month $k$*. Because the average inter-purchase interval is **120.1 days (~4 months)**, repeat orders trickle in gradually over time, accumulating to the full **25.49% lifetime repeat rate** by Month 12+.
""")

add_code("""# Cohort Retention Calculation
fact_df['order_dt'] = pd.to_datetime(fact_df['order_date'])
fact_df['order_month'] = fact_df['order_dt'].dt.to_period('M')
fact_df['cohort_month'] = fact_df.groupby('customer_id')['order_dt'].transform('min').dt.to_period('M')

fact_df['period_number'] = (fact_df['order_month'].dt.year - fact_df['cohort_month'].dt.year) * 12 + (fact_df['order_month'].dt.month - fact_df['cohort_month'].dt.month)

cohort_group = fact_df.groupby(['cohort_month', 'period_number'])['customer_id'].nunique().reset_index()
cohort_pivot = cohort_group.pivot(index='cohort_month', columns='period_number', values='customer_id')

cohort_size = cohort_pivot.iloc[:, 0]
retention_matrix = cohort_pivot.divide(cohort_size, axis=0) * 100

# Plot Cohort Retention Heatmap
plt.figure(figsize=(12, 7))
sns.heatmap(retention_matrix.iloc[:12, :8], annot=True, fmt='.1f', cmap='YlGnBu', vmin=0, vmax=15, cbar_kws={'label': 'Active Rate (%)'})
plt.title('Monthly Active Cohort Heatmap (%) — Indian E-Commerce', fontsize=14, fontweight='bold', pad=15)
plt.xlabel('Months Since Acquisition (Month 0 to Month 7)', fontsize=11)
plt.ylabel('Acquisition Cohort Month', fontsize=11)
plt.tight_layout()
os.makedirs('../dashboard', exist_ok=True)
plt.savefig('../dashboard/cohort_retention_heatmap.png', dpi=300)
plt.close()
print(' [OK] Saved cohort retention heatmap to dashboard/cohort_retention_heatmap.png')

# Cumulative Repeat Retention Table
cust_orders = fact_df.sort_values(['customer_id', 'order_dt'])
cust_orders['order_seq'] = cust_orders.groupby('customer_id').cumcount() + 1
order2 = cust_orders[cust_orders['order_seq'] == 2].copy()
order2['seq2_period'] = (order2['order_month'].dt.year - order2['cohort_month'].dt.year) * 12 + (order2['order_month'].dt.month - order2['cohort_month'].dt.month)

early_cohorts = fact_df[fact_df['cohort_month'] <= '2024-06']['customer_id'].nunique()
order2_early = order2[order2['cohort_month'] <= '2024-06']

cum_data = []
for k in range(0, 7):
    cum_repeat = (order2_early['seq2_period'] <= k).sum()
    pct = round(cum_repeat / early_cohorts * 100, 2)
    cum_data.append({'Month_Elapsed': f'Month {k}', 'Cumulative_Repeat_Customers': cum_repeat, 'Cumulative_Repeat_Rate_Pct': pct})

cum_df = pd.DataFrame(cum_data)
print('=== CUMULATIVE REPEAT RETENTION RECONCILIATION ===')
print(cum_df.to_string(index=False))
""")

# Step 4: Purchase Funnel Analysis
add_md("""## 4. Repeat Purchase Funnel Analysis

### 📖 How This Works (Interview Explanation)
The **Repeat Purchase Funnel** evaluates conversion rates between transactional milestones:
* **1st Order (100%):** Acquisition baseline (18,497 customers).
* **2nd Order:** 4,714 customers (**25.49% retention**, 74.51% drop-off).
* **3rd Order:** 1,354 customers (**28.72% conversion** from 2nd order).
* **4th+ Order:** 316 customers (**23.34% conversion** from 3rd order).
""")

add_code("""# Repeat Purchase Funnel Progression
orders_per_customer = fact_df.groupby('customer_id')['order_id'].nunique()
f1_cust = (orders_per_customer >= 1).sum()
f2_cust = (orders_per_customer >= 2).sum()
f3_cust = (orders_per_customer >= 3).sum()
f4_cust = (orders_per_customer >= 4).sum()

funnel_df = pd.DataFrame({
    'Stage': ['1st Purchase', '2nd Purchase', '3rd Purchase', '4th+ Purchase'],
    'Customers': [f1_cust, f2_cust, f3_cust, f4_cust],
    'Retention_from_Base': [100.0, round(f2_cust/f1_cust*100, 2), round(f3_cust/f1_cust*100, 2), round(f4_cust/f1_cust*100, 2)],
    'Stage_Conversion_Pct': [100.0, round(f2_cust/f1_cust*100, 2), round(f3_cust/f2_cust*100, 2), round(f4_cust/f3_cust*100, 2)],
    'Stage_Dropoff_Pct': [0.0, round((1-f2_cust/f1_cust)*100, 2), round((1-f3_cust/f2_cust)*100, 2), round((1-f4_cust/f3_cust)*100, 2)]
})

print('=== REPEAT PURCHASE FUNNEL METRICS ===')
print(funnel_df.to_string(index=False))

# Plot Funnel Chart
fig, ax = plt.subplots(figsize=(10, 5))
bars = ax.bar(funnel_df['Stage'], funnel_df['Customers'], color=['#2b5c8f', '#3690c0', '#67a9cf', '#02818a'], width=0.55)

for bar, cust, pct in zip(bars, funnel_df['Customers'], funnel_df['Retention_from_Base']):
    height = bar.get_height()
    ax.annotate(f"{cust:,} ({pct}%)",
                xy=(bar.get_x() + bar.get_width() / 2, height),
                xytext=(0, 5), textcoords="offset points",
                ha='center', va='bottom', fontsize=10, fontweight='bold')

ax.set_title('Repeat Purchase Funnel Progression & Retention Drop-Off', fontsize=13, fontweight='bold', pad=15)
ax.set_ylabel('Unique Customers', fontsize=11)
ax.set_ylim(0, f1_cust * 1.15)
plt.tight_layout()
plt.savefig('../dashboard/repeat_purchase_funnel.png', dpi=300)
plt.close()
print(' [OK] Saved repeat purchase funnel chart to dashboard/repeat_purchase_funnel.png')
""")

# Step 5: Churn Prediction Model
add_md("""## 5. Churn Prediction Model (Class-Weighted Logistic Regression & XGBoost)

### 📖 How This Works (Interview Explanation)
In e-commerce, **Churn** is defined as post-purchase inactivity exceeding **90 days** (aligned with our 120-day inter-purchase cycle). 
* **Class Imbalance:** 68.4% of customers are churned (>90 days inactive) vs. 31.6% active.
* **Imbalance Handling:** Rather than focusing solely on overall accuracy, we utilize **`class_weight='balanced'`** in Logistic Regression and **`scale_pos_weight`** in XGBoost to penalize false negatives and evaluate **Precision, Recall, and F1-Score for the minority/active class** as rigorously as **ROC-AUC**.
""")

add_code("""# Feature Engineering for Churn Prediction
max_dt = fact_df['order_dt'].max()

cust_features = fact_df.groupby('customer_id').agg(
    last_order=('order_dt', 'max'),
    frequency=('order_id', 'nunique'),
    monetary=('order_total_amount', 'sum'),
    avg_order_val=('order_total_amount', 'mean'),
    avg_items=('total_items', 'mean'),
    avg_delay=('delivery_delay_days', 'mean'),
    avg_review=('review_score', 'mean'),
    cod_ratio=('payment_method', lambda x: (x == 'COD').mean()),
    is_tier1=('city_tier', lambda x: 1 if (x.iloc[0] == 'Tier 1') else 0)
).reset_index()

cust_features['recency_days'] = (max_dt - cust_features['last_order']).dt.days
cust_features['avg_delay'] = cust_features['avg_delay'].fillna(0)
cust_features['avg_review'] = cust_features['avg_review'].fillna(4.0)

# Target: 1 = Churned (>90 days inactive), 0 = Active (<= 90 days)
cust_features['is_churned'] = (cust_features['recency_days'] > 90).astype(int)

feature_cols = ['frequency', 'monetary', 'avg_order_val', 'avg_items', 'avg_delay', 'avg_review', 'cod_ratio', 'is_tier1']
X = cust_features[feature_cols]
y = cust_features['is_churned']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42, stratify=y)

print(f'Train shape: {X_train.shape}, Test shape: {X_test.shape}')
print('Train Class Distribution:')
print(y_train.value_counts(normalize=True).round(4)*100)
""")

add_code("""# 1. Logistic Regression Baseline (Class-Weighted)
lr = LogisticRegression(class_weight='balanced', max_iter=1000, random_state=42)
lr.fit(X_train, y_train)
lr_preds = lr.predict(X_test)
lr_probs = lr.predict_proba(X_test)[:, 1]

print('=== MODEL 1: LOGISTIC REGRESSION BASELINE ===')
print('ROC-AUC Score:', round(roc_auc_score(y_test, lr_probs), 4))
print(classification_report(y_test, lr_preds, digits=4))

# 2. XGBoost Classifier (Class-Weighted via scale_pos_weight)
scale_pos_weight = (y_train == 0).sum() / (y_train == 1).sum()
xgb_model = xgb.XGBClassifier(
    n_estimators=100,
    max_depth=4,
    learning_rate=0.05,
    scale_pos_weight=scale_pos_weight,
    random_state=42
)
xgb_model.fit(X_train, y_train)
xgb_preds = xgb_model.predict(X_test)
xgb_probs = xgb_model.predict_proba(X_test)[:, 1]

print('=== MODEL 2: XGBOOST CLASSIFIER ===')
print('ROC-AUC Score:', round(roc_auc_score(y_test, xgb_probs), 4))
print(classification_report(y_test, xgb_preds, digits=4))

# Plot Confusion Matrices
fig, axes = plt.subplots(1, 2, figsize=(12, 5))
ConfusionMatrixDisplay.from_predictions(y_test, lr_preds, ax=axes[0], cmap='Blues', display_labels=['Active (0)', 'Churned (1)'])
axes[0].set_title('Logistic Regression Confusion Matrix', fontweight='bold')

ConfusionMatrixDisplay.from_predictions(y_test, xgb_preds, ax=axes[1], cmap='Blues', display_labels=['Active (0)', 'Churned (1)'])
axes[1].set_title('XGBoost Confusion Matrix', fontweight='bold')
plt.tight_layout()
plt.savefig('../dashboard/churn_confusion_matrices.png', dpi=300)
plt.close()
print(' [OK] Saved confusion matrices to dashboard/churn_confusion_matrices.png')
""")

# Step 6: SHAP Feature Importance
add_md("""## 6. SHAP Feature Importance & Driver Analysis

### 📖 How This Works (Interview Explanation)
**SHAP (SHapley Additive exPlanations)** applies game theory to measure how much each behavioral feature shifts a customer's churn probability relative to the baseline dataset prediction.
* **Beeswarm Summary Plot:** Shows feature impact magnitude and direction (e.g. higher delivery delay shifts prediction toward churn).
* **Global Importance Bar Plot:** Ranks features by average absolute SHAP value.
""")

add_code("""# TreeSHAP Explainer on XGBoost Model
explainer = shap.TreeExplainer(xgb_model)
shap_values = explainer.shap_values(X_test)

mean_abs_shap = np.abs(shap_values).mean(axis=0)
shap_summary = pd.DataFrame({'feature': feature_cols, 'shap_importance': mean_abs_shap}).sort_values('shap_importance', ascending=False)

print('=== SHAP GLOBAL FEATURE IMPORTANCE RANKING ===')
print(shap_summary.to_string(index=False))

# Export summary CSV for Power BI
shap_summary.to_csv('../dashboard/shap_driver_importance.csv', index=False)

# SHAP Beeswarm Summary Plot
plt.figure(figsize=(10, 6))
shap.summary_plot(shap_values, X_test, feature_names=feature_cols, show=False)
plt.title('SHAP Feature Importance Beeswarm Plot (Churn Drivers)', fontsize=13, fontweight='bold', pad=15)
plt.tight_layout()
plt.savefig('../dashboard/shap_beeswarm_summary.png', dpi=300)
plt.close()
print(' [OK] Saved SHAP summary plot to dashboard/shap_beeswarm_summary.png')
""")

os.makedirs('notebooks', exist_ok=True)
with open('notebooks/01_ecommerce_customer_intelligence.ipynb', 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=2)

print('[SUCCESS] Successfully updated notebooks/01_ecommerce_customer_intelligence.ipynb with Steps 1-6')
