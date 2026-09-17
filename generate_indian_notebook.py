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
1. **Which customers are going to leave?** (Forward-Looking Temporal Churn Prediction)
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

add_code("""import os
import sqlite3
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

import lifetimes
from lifetimes import BetaGeoFitter, GammaGammaFitter

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

os.makedirs('../dashboard', exist_ok=True)
segment_summary.to_csv('../dashboard/rfm_segment_summary.csv', index=False)
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

# Export monthly trend for Power BI
monthly_trend = fact_df.groupby('order_month').agg(
    delivered_orders=('order_id', 'nunique'),
    active_customers=('customer_id', 'nunique'),
    total_revenue=('order_total_amount', 'sum')
).reset_index()

monthly_trend['order_month'] = monthly_trend['order_month'].astype(str)
monthly_trend.to_csv('../dashboard/churn_trend_monthly.csv', index=False)
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

# Step 5: Forward-Looking Temporal Churn Prediction Model
add_md("""## 5. Forward-Looking Temporal Churn Prediction Model

### 📖 How This Works (Production Temporal Design)
To prevent data leakage in production machine learning systems, we implement a **forward-looking temporal split**:
1. **Cutoff Date $T$:** Selected at `max_order_date - 90 days` (2025-10-02).
2. **Feature Extraction Window ($\\le T$):** All features (frequency, monetary, AOV, delivery delay, COD ratio, category diversity, and `recency_days_at_T` / `days_since_last_vs_avg_gap`) are calculated strictly using order history on or before $T$.
3. **Target Observation Window ($[T+1 \\text{ to } T+90]$):** Churn label $= 1$ if zero orders were placed in the 90 days after $T$, else $0$.
4. **Leakage Safety:** `recency_days_at_T` measures purchase recency *prior* to cutoff date $T$, while the target label observes activity *after* cutoff date $T$. This allows recency signals to be used legitimately without target leakage!
""")

add_code("""# Forward-Looking Temporal Split
max_order_date = fact_df['order_dt'].max()
cutoff_date = max_order_date - pd.Timedelta(days=90)

df_feature = fact_df[fact_df['order_dt'] <= cutoff_date].copy()
df_target = fact_df[fact_df['order_dt'] > cutoff_date].copy()

target_active_customers = set(df_target['customer_id'].unique())

df_feature_sorted = df_feature.sort_values(['customer_id', 'order_dt'])
df_feature_sorted['prev_order_dt'] = df_feature_sorted.groupby('customer_id')['order_dt'].shift(1)
df_feature_sorted['days_since_prev'] = (df_feature_sorted['order_dt'] - df_feature_sorted['prev_order_dt']).dt.days

cust_features_T = df_feature_sorted.groupby('customer_id').agg(
    last_order_at_T=('order_dt', 'max'),
    frequency=('order_id', 'nunique'),
    monetary=('order_total_amount', 'sum'),
    avg_order_val=('order_total_amount', 'mean'),
    avg_items=('total_items', 'mean'),
    avg_delay=('delivery_delay_days', 'mean'),
    avg_review=('review_score', 'mean'),
    cod_ratio=('payment_method', lambda x: (x == 'COD').mean()),
    is_tier1=('city_tier', lambda x: 1 if (x.iloc[0] == 'Tier 1') else 0),
    avg_inter_gap=('days_since_prev', 'mean')
).reset_index()

cat_div_T = df_feature_sorted.groupby('customer_id')['order_category_count'].sum().reset_index()
cat_div_T.columns = ['customer_id', 'category_diversity']
cust_features_T = cust_features_T.merge(cat_div_T, on='customer_id', how='left')

last_2_T = df_feature_sorted.groupby('customer_id').tail(2)
last_2_stats_T = last_2_T.groupby('customer_id').agg(
    recent_2_aov=('order_total_amount', 'mean'),
    recent_2_gap=('days_since_prev', 'mean')
).reset_index()
cust_features_T = cust_features_T.merge(last_2_stats_T, on='customer_id', how='left')

cust_features_T['recency_days_at_T'] = (cutoff_date - cust_features_T['last_order_at_T']).dt.days
cust_features_T['avg_delay'] = cust_features_T['avg_delay'].fillna(0)
cust_features_T['avg_review'] = cust_features_T['avg_review'].fillna(4.0)

overall_avg_gap_T = cust_features_T['avg_inter_gap'].mean()
cust_features_T['order_frequency_trend'] = np.where(
    cust_features_T['frequency'] > 1,
    cust_features_T['recent_2_gap'] / (cust_features_T['avg_inter_gap'] + 1e-5),
    1.0
)

cust_features_T['days_since_last_vs_avg_gap'] = np.where(
    cust_features_T['frequency'] > 1,
    cust_features_T['recency_days_at_T'] / (cust_features_T['avg_inter_gap'] + 1e-5),
    cust_features_T['recency_days_at_T'] / (overall_avg_gap_T + 1e-5)
)

cust_features_T['monetary_trend'] = np.where(
    cust_features_T['frequency'] > 1,
    cust_features_T['recent_2_aov'] / (cust_features_T['avg_order_val'] + 1e-5),
    1.0
)

# Churn Target Label: 1 if ZERO orders in target window, else 0
cust_features_T['is_churned'] = cust_features_T['customer_id'].apply(lambda cid: 1 if cid not in target_active_customers else 0)

forward_features = [
    'frequency', 'monetary', 'avg_order_val', 'avg_items', 'avg_delay', 
    'avg_review', 'cod_ratio', 'is_tier1', 'recency_days_at_T',
    'days_since_last_vs_avg_gap', 'order_frequency_trend', 
    'category_diversity', 'monetary_trend'
]

X_fw = cust_features_T[forward_features].fillna(0)
y_fw = cust_features_T['is_churned']

X_tr_fw, X_te_fw, y_tr_fw, y_te_fw = train_test_split(X_fw, y_fw, test_size=0.25, random_state=42, stratify=y_fw)

lr_fw = LogisticRegression(class_weight='balanced', max_iter=1000, random_state=42).fit(X_tr_fw, y_tr_fw)
scale_pos_weight_fw = (y_tr_fw == 0).sum() / (y_tr_fw == 1).sum()
xgb_fw = xgb.XGBClassifier(n_estimators=100, max_depth=4, learning_rate=0.05, scale_pos_weight=scale_pos_weight_fw, random_state=42).fit(X_tr_fw, y_tr_fw)

lr_fw_p = lr_fw.predict_proba(X_te_fw)[:, 1]
xgb_fw_p = xgb_fw.predict_proba(X_te_fw)[:, 1]

lr_fw_pred = lr_fw.predict(X_te_fw)
xgb_fw_pred = xgb_fw.predict(X_te_fw)

rep_lr_fw = classification_report(y_te_fw, lr_fw_pred, output_dict=True)
rep_xgb_fw = classification_report(y_te_fw, xgb_fw_pred, output_dict=True)

comp_df = pd.DataFrame({
    'Model_Configuration': ['Forward-Looking Logistic Regression', 'Forward-Looking XGBoost Classifier'],
    'ROC_AUC': [round(roc_auc_score(y_te_fw, lr_fw_p), 4), round(roc_auc_score(y_te_fw, xgb_fw_p), 4)],
    'Active_Class_F1': [round(rep_lr_fw['0']['f1-score'], 4), round(rep_xgb_fw['0']['f1-score'], 4)],
    'Active_Class_Precision': [round(rep_lr_fw['0']['precision'], 4), round(rep_xgb_fw['0']['precision'], 4)],
    'Active_Class_Recall': [round(rep_lr_fw['0']['recall'], 4), round(rep_xgb_fw['0']['recall'], 4)],
    'Overall_Accuracy': [round(rep_lr_fw['accuracy'], 4), round(rep_xgb_fw['accuracy'], 4)]
})

print('=== FORWARD-LOOKING CHURN MODEL EVALUATION ===')
print(comp_df.to_string(index=False))

fig, axes = plt.subplots(1, 2, figsize=(12, 5))
ConfusionMatrixDisplay.from_predictions(y_te_fw, lr_fw_pred, ax=axes[0], cmap='Blues', display_labels=['Active (0)', 'Churned (1)'])
axes[0].set_title('Logistic Regression (Forward) Confusion Matrix', fontweight='bold')

ConfusionMatrixDisplay.from_predictions(y_te_fw, xgb_fw_pred, ax=axes[1], cmap='Blues', display_labels=['Active (0)', 'Churned (1)'])
axes[1].set_title('XGBoost (Forward) Confusion Matrix', fontweight='bold')
plt.tight_layout()
plt.savefig('../dashboard/churn_confusion_matrices.png', dpi=300)
plt.close()
print(' [OK] Saved forward confusion matrices to dashboard/churn_confusion_matrices.png')
""")

# Step 6: SHAP Feature Importance
add_md("""## 6. SHAP Feature Importance & Driver Analysis

### 📖 How This Works (Interview Explanation)
We run TreeSHAP (`shap.TreeExplainer`) on the **Forward-Looking XGBoost Model** to evaluate true behavioral drivers of future churn.
""")

add_code("""# TreeSHAP Explainer on Forward-Looking XGBoost Model
explainer = shap.TreeExplainer(xgb_fw)
shap_values_fw = explainer.shap_values(X_te_fw)

mean_abs_shap_fw = np.abs(shap_values_fw).mean(axis=0)
shap_summary = pd.DataFrame({'feature': forward_features, 'shap_importance': mean_abs_shap_fw}).sort_values('shap_importance', ascending=False)

print('=== FORWARD-LOOKING SHAP GLOBAL FEATURE IMPORTANCE RANKING ===')
print(shap_summary.to_string(index=False))

shap_summary.to_csv('../dashboard/shap_driver_importance.csv', index=False)

plt.figure(figsize=(10, 6))
shap.summary_plot(shap_values_fw, X_te_fw, feature_names=forward_features, show=False)
plt.title('SHAP Feature Importance Beeswarm Plot (Forward-Looking Churn Drivers)', fontsize=13, fontweight='bold', pad=15)
plt.tight_layout()
plt.savefig('../dashboard/shap_beeswarm_summary.png', dpi=300)
plt.close()
print(' [OK] Saved forward SHAP summary plot to dashboard/shap_beeswarm_summary.png')
""")

# Step 7: Customer Lifetime Value (CLV) Prediction
add_md("""## 7. Customer Lifetime Value (CLV) Prediction & Tiering

### 📖 How This Works (Interview Explanation)
**Predictive Customer Lifetime Value (CLV)** combines two probabilistic parametric models from the `lifetimes` library:
1. **BG/NBD Model (Beta-Geometric / Negative Binomial Distribution):** Predicts expected order transaction volume over the next 12 months ($E[N_{12}]$) based on customer frequency, recency, and tenure ($T$).
2. **Gamma-Gamma Model:** Estimates expected average transaction monetary spend ($E[M]$) per customer.

#### 12-Month Expected CLV Calculation:
$$E[\\text{CLV}_{12}] = E[N_{12}] \\times E[M]$$

Customers are subsequently stratified into **3 CLV Tiers**:
* **High CLV:** Top 20% expected spenders.
* **Medium CLV:** Middle 30% spenders.
* **Low CLV:** Bottom 50% spenders.
""")

add_code("""# Fit BG/NBD and Gamma-Gamma Models
clv_summary = lifetimes.utils.summary_data_from_transaction_data(
    fact_df,
    customer_id_col='customer_id',
    datetime_col='order_dt',
    monetary_value_col='order_total_amount',
    observation_period_end=max_order_date
)

bgf = BetaGeoFitter(penalizer_coef=0.001)
bgf.fit(clv_summary['frequency'], clv_summary['recency'], clv_summary['T'])

clv_summary['predicted_purchases_12m'] = bgf.conditional_expected_number_of_purchases_up_to_time(
    365, clv_summary['frequency'], clv_summary['recency'], clv_summary['T']
)

returning_customers = clv_summary[clv_summary['frequency'] > 0]
ggf = GammaGammaFitter(penalizer_coef=0.001)
ggf.fit(returning_customers['frequency'], returning_customers['monetary_value'])

overall_avg_order = fact_df['order_total_amount'].mean()
clv_summary['expected_avg_order_value'] = ggf.conditional_expected_average_profit(
    clv_summary['frequency'], clv_summary['monetary_value']
).fillna(overall_avg_order)

clv_summary['predicted_clv_12m'] = clv_summary['predicted_purchases_12m'] * clv_summary['expected_avg_order_value']

# Assign CLV Tiers: High (Top 20%), Medium (Middle 30%), Low (Bottom 50%)
clv_summary['clv_tier'] = pd.qcut(
    clv_summary['predicted_clv_12m'].rank(method='first'),
    q=[0, 0.50, 0.80, 1.0],
    labels=['Low CLV', 'Medium CLV', 'High CLV']
)

clv_tier_dist = clv_summary.groupby('clv_tier').agg(
    customer_count=('predicted_clv_12m', 'count'),
    mean_predicted_clv=('predicted_clv_12m', 'mean'),
    min_predicted_clv=('predicted_clv_12m', 'min'),
    max_predicted_clv=('predicted_clv_12m', 'max')
).reset_index()

clv_tier_dist['formatted_mean_clv'] = clv_tier_dist['mean_predicted_clv'].apply(format_inr)
print('=== CLV TIERS DISTRIBUTION & EXPECTED 12M SPEND ===')
print(clv_tier_dist[['clv_tier', 'customer_count', 'formatted_mean_clv']].to_string(index=False))

clv_tier_dist.to_csv('../dashboard/clv_distribution_tiers.csv', index=False)
""")

# Step 8: Next-Best-Action Matrix
add_md("""## 8. Prescriptive Next-Best-Action Matrix (Scored via Production Model)

### 📖 How This Works (Interview Explanation)
In production deployment, the **Forward-Looking Model** trained on historical $T-90$ data is scored against **current full-history customer features** (up to `max_order_date`) to predict live churn probabilities for all 18,497 customers.
By cross-tabulating **Live Churn Risk** (High / Medium / Low) with **CLV Tier** (High / Medium / Low), we construct a **3x3 Prescriptive Decision Matrix**.
""")

add_code("""# Production Live Churn Scoring using Validated Model
fact_sorted_prod = fact_df.sort_values(['customer_id', 'order_dt'])
fact_sorted_prod['prev_order_dt'] = fact_sorted_prod.groupby('customer_id')['order_dt'].shift(1)
fact_sorted_prod['days_since_prev'] = (fact_sorted_prod['order_dt'] - fact_sorted_prod['prev_order_dt']).dt.days

cust_prod = fact_sorted_prod.groupby('customer_id').agg(
    last_order=('order_dt', 'max'),
    frequency=('order_id', 'nunique'),
    monetary=('order_total_amount', 'sum'),
    avg_order_val=('order_total_amount', 'mean'),
    avg_items=('total_items', 'mean'),
    avg_delay=('delivery_delay_days', 'mean'),
    avg_review=('review_score', 'mean'),
    cod_ratio=('payment_method', lambda x: (x == 'COD').mean()),
    is_tier1=('city_tier', lambda x: 1 if (x.iloc[0] == 'Tier 1') else 0),
    avg_inter_gap=('days_since_prev', 'mean')
).reset_index()

cat_div_prod = fact_sorted_prod.groupby('customer_id')['order_category_count'].sum().reset_index()
cat_div_prod.columns = ['customer_id', 'category_diversity']
cust_prod = cust_prod.merge(cat_div_prod, on='customer_id', how='left')

last_2_prod = fact_sorted_prod.groupby('customer_id').tail(2)
last_2_stats_prod = last_2_prod.groupby('customer_id').agg(
    recent_2_aov=('order_total_amount', 'mean'),
    recent_2_gap=('days_since_prev', 'mean')
).reset_index()
cust_prod = cust_prod.merge(last_2_stats_prod, on='customer_id', how='left')

cust_prod['recency_days_at_T'] = (max_order_date - cust_prod['last_order']).dt.days
cust_prod['avg_delay'] = cust_prod['avg_delay'].fillna(0)
cust_prod['avg_review'] = cust_prod['avg_review'].fillna(4.0)

overall_avg_gap_prod = cust_prod['avg_inter_gap'].mean()
cust_prod['order_frequency_trend'] = np.where(cust_prod['frequency'] > 1, cust_prod['recent_2_gap'] / (cust_prod['avg_inter_gap'] + 1e-5), 1.0)
cust_prod['days_since_last_vs_avg_gap'] = np.where(cust_prod['frequency'] > 1, cust_prod['recency_days_at_T'] / (cust_prod['avg_inter_gap'] + 1e-5), cust_prod['recency_days_at_T'] / (overall_avg_gap_prod + 1e-5))
cust_prod['monetary_trend'] = np.where(cust_prod['frequency'] > 1, cust_prod['recent_2_aov'] / (cust_prod['avg_order_val'] + 1e-5), 1.0)

X_prod = cust_prod[forward_features].fillna(0)
cust_prod['churn_probability'] = xgb_fw.predict_proba(X_prod)[:, 1]

# Quantile-Based Terciles for Churn Risk Tiering (Low Risk: Bottom 33.3%, Medium Risk: Middle 33.3%, High Risk: Top 33.3%)
cust_prod['churn_risk_tier'] = pd.qcut(
    cust_prod['churn_probability'].rank(method='first'),
    q=[0, 1/3, 2/3, 1.0],
    labels=['Low Risk', 'Medium Risk', 'High Risk']
)

final_customer_df = cust_prod.merge(
    clv_summary[['predicted_purchases_12m', 'predicted_clv_12m', 'clv_tier']],
    on='customer_id',
    how='left'
)

def assign_next_best_action(row):
    risk = row['churn_risk_tier']
    clv = row['clv_tier']
    
    if risk == 'High Risk' and clv == 'High CLV':
        return 'VIP Urgent Retention (Concierge Call + Rs. 1500 Voucher)'
    elif risk == 'High Risk' and clv == 'Medium CLV':
        return 'Win-Back Campaign (15% Category Discount Offer)'
    elif risk == 'High Risk' and clv == 'Low CLV':
        return 'Automated Low-Cost Push Notification Series'
    elif risk == 'Medium Risk' and clv == 'High CLV':
        return 'Proactive Engagement & Product Cross-Sell'
    elif risk == 'Low Risk' and clv == 'High CLV':
        return 'VIP Loyalty Program & Early Sale Access'
    else:
        return 'Standard Nurture Workflow (No Action Needed)'

final_customer_df['recommended_action'] = final_customer_df.apply(assign_next_best_action, axis=1)

action_matrix = pd.crosstab(
    final_customer_df['churn_risk_tier'],
    final_customer_df['clv_tier'],
    margins=True
)

print('=== 3x3 NEXT-BEST-ACTION CUSTOMER HEADCOUNT MATRIX ===')
print(action_matrix)

action_summary = final_customer_df.groupby('recommended_action').agg(
    customer_count=('customer_id', 'count'),
    avg_predicted_clv=('predicted_clv_12m', 'mean'),
    total_at_risk_clv=('predicted_clv_12m', 'sum')
).reset_index().sort_values('customer_count', ascending=False)

action_summary['formatted_total_at_risk_clv'] = action_summary['total_at_risk_clv'].apply(format_inr)
print('=== RECOMMENDED ACTION SUMMARY ===')
print(action_summary[['recommended_action', 'customer_count', 'formatted_total_at_risk_clv']].to_string(index=False))

action_summary.to_csv('../dashboard/next_best_action_summary.csv', index=False)
""")

# Step 9: Revenue Impact Simulation
add_md("""## 9. Revenue Impact Simulation

### 📖 How This Works (Interview Explanation)
To quantify the financial ROI of implementing our **Next-Best-Action Framework**, we simulate protected revenue for the critical **High Risk + High CLV** segment:
$$\\text{Protected Revenue} = N_{\\text{HighRisk\\_HighCLV}} \\times \\text{Mean 12M CLV} \\times \\text{Campaign Retention Win Rate } (X\\%)$$
""")

add_code("""# Revenue Protection Model
high_risk_high_clv = final_customer_df[
    (final_customer_df['churn_risk_tier'] == 'High Risk') & 
    (final_customer_df['clv_tier'] == 'High CLV')
]

n_target = len(high_risk_high_clv)
avg_clv_target = high_risk_high_clv['predicted_clv_12m'].mean()
total_risk_revenue = n_target * avg_clv_target

rates = [0.10, 0.20, 0.30]
sim_results = []

for r in rates:
    protected = total_risk_revenue * r
    sim_results.append({
        'Retention_Win_Rate_Pct': f"{int(r*100)}%",
        'Target_Customers': n_target,
        'Total_At_Risk_Revenue': format_inr(total_risk_revenue),
        'Protected_Revenue_Simulated': format_inr(protected),
        'Protected_Revenue_Exact_INR': round(protected, 2)
    })

sim_df = pd.DataFrame(sim_results)
print('=== REVENUE PROTECTION SIMULATION RESULTS ===')
print(sim_df[['Retention_Win_Rate_Pct', 'Target_Customers', 'Total_At_Risk_Revenue', 'Protected_Revenue_Simulated']].to_string(index=False))
""")

# Step 10: Dashboard Specifications
add_md("""## 10. Dashboard-Ready Exports & Executive Power BI Specifications

### 📊 Recommended Power BI Executive Layout (4 Key Panels):
1. **Executive KPI Cards (Header):**
   * Total Delivered Revenue (₹11.03 Cr)
   * Repeat Purchase Rate (25.49%)
   * High Risk + High CLV Headcount (353 Customers)
   * Potential Protected Revenue @ 20% Win Rate (₹5,630.84)
""")

add_code("""print(' [OK] All dashboard summary CSVs exported to dashboard/:')
print('   - dashboard/rfm_segment_summary.csv')
print('   - dashboard/churn_trend_monthly.csv')
print('   - dashboard/repeat_purchase_funnel.png')
print('   - dashboard/cohort_retention_heatmap.png')
print('   - dashboard/churn_confusion_matrices.png')
print('   - dashboard/shap_beeswarm_summary.png')
print('   - dashboard/shap_driver_importance.csv')
print('   - dashboard/clv_distribution_tiers.csv')
print('   - dashboard/next_best_action_summary.csv')
""")

os.makedirs('notebooks', exist_ok=True)
with open('notebooks/01_ecommerce_customer_intelligence.ipynb', 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=2)

print('[SUCCESS] Successfully updated notebooks/01_ecommerce_customer_intelligence.ipynb with FORWARD-LOOKING CHURN DESIGN')
