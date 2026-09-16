# E-Commerce Customer Intelligence: Churn, CLV & Next-Best-Action

**Target Roles:** Product Analyst | Business Analyst | Data Analyst  
**Tech Stack:** SQL (SQLite), Python (Pandas, Scikit-learn, XGBoost, SHAP, Lifetimes), Power BI  
**Local Project Path:** `D:\Ssshhhh\Projexts\E commerce`  
**GitHub Repository:** [`Ayusshhhhh01/ecommerce-customer-intelligence`](https://github.com/Ayusshhhhh01/ecommerce-customer-intelligence.git)

---

## 🚨 DATASET DISCLOSURE (SYNTHETIC DATA)
> **Explicit Prominent Notice:** This dataset is synthetically generated to model realistic Indian e-commerce behavior patterns (including festival season sales spikes like Diwali and Republic Day, UPI/COD payment distributions, metro vs tier-2 delivery latency, and return rates). **It is NOT derived from any real company's private transaction data.**

---

## 📌 Business Context
Leadership in an e-commerce platform needs actionable answers to four core customer lifecycle questions:
1. **Which customers are going to leave?** (Churn Prediction)
2. **How valuable are they?** (RFM & Customer Lifetime Value in ₹ Lakhs/Crores)
3. **Why are they leaving?** (SHAP Feature Drivers, Payment Methods & Delivery Friction)
4. **What should we do about them?** (Prescriptive Next-Best-Action Framework)

---

## 📁 Repository Structure

```
D:\Ssshhhh\Projexts\E commerce\
├── data/                                 # Synthetic Indian E-Commerce CSVs
│   ├── customers.csv                     # 20,000 customers (Tier 1 Metros & Tier 2/3)
│   ├── orders.csv                        # 27,537 orders (UPI, COD, Card, Net Banking)
│   ├── order_items.csv                   # 35,782 line items in ₹ INR
│   ├── delivery_info.csv                 # Promised vs Actual Delivery Date & Latency
│   ├── reviews.csv                       # Customer Review Scores (1-5)
│   └── DATASET_DISCLOSURE.md             # Dataset disclaimer documentation
├── sql/                                  # Production SQL Scripts
│   ├── 01_customer_order_fact.sql        # Fact table construction
│   └── 02_rfm_metrics.sql                # RFM aggregations & LAG window functions
├── notebooks/                            # Jupyter Notebooks
│   └── 01_ecommerce_customer_intelligence.ipynb # Complete 10-step executable notebook
├── dashboard/                            # Exported summary tables & visuals for Power BI
│   ├── cohort_retention_heatmap.png      # Monthly active cohort heatmap
│   ├── repeat_purchase_funnel.png        # Lifecycle milestone funnel chart
│   ├── churn_confusion_matrices.png      # Confusion matrix comparison
│   ├── shap_beeswarm_summary.png         # TreeSHAP global driver plot
│   ├── rfm_segment_summary.csv           # RFM summary table
│   ├── churn_trend_monthly.csv           # Monthly revenue and active user trends
│   ├── shap_driver_importance.csv        # SHAP feature rankings
│   ├── clv_distribution_tiers.csv        # BG/NBD + Gamma-Gamma CLV tiers
│   └── next_best_action_summary.csv      # 3x3 Prescriptive action matrix
├── generate_indian_dataset.py            # Synthetic dataset generator script
├── generate_indian_notebook.py           # Notebook generator script
├── EXECUTIVE_SUMMARY.md                  # 1-page business report for leadership
├── RESUME_BULLETS.md                     # 3 metric-backed, interview-ready resume bullets
└── README.md                             # Project documentation
```

---

## 🚀 Executive Highlights & Key Results

- **Total Delivered Transactions:** 24,881 delivered order records across **18,497 unique customers**.
- **Total Historical Delivered Revenue:** **₹11.03 Crore** (Exact: ₹11,03,03,652.88).
- **Repeat Purchase Rate:** **25.49%** (4,714 repeat buyers out of 18,497 delivered customers).
- **Average Inter-Purchase Interval:** **120.1 days** (~4 months) between repeat purchases.

### 1. RFM Segment Breakdown (INR Lakh/Crore Notation)

| Segment Name | Customer Count | % Customers | Total Revenue (₹) | % Revenue | Avg Recency (Days) | Avg Monetary (₹) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Loyal Customers** | 2,646 | 14.31% | **₹2.53Cr** | 22.93% | 101.5 | ₹9,557.27 |
| **New Customers** | 4,813 | 26.02% | **₹2.18Cr** | 19.76% | 66.6 | ₹4,529.69 |
| **Hibernating / Lost** | 3,630 | 19.62% | **₹1.78Cr** | 16.11% | 478.2 | ₹4,895.33 |
| **About to Sleep** | 2,969 | 16.05% | **₹1.35Cr** | 12.21% | 304.0 | ₹4,536.39 |
| **Champions** | 885 | 4.78% | **₹1.22Cr** | 11.09% | 57.8 | **₹13,824.25** |
| **Promising / Potential Loyalists** | 2,756 | 14.90% | **₹1.17Cr** | 10.62% | 178.5 | ₹4,250.77 |
| **At-Risk** | 742 | 4.01% | **₹71.49L** | 6.48% | 300.0 | ₹9,634.82 |
| **Can't Lose Them** | 56 | 0.30% | **₹8.77L** | 0.79% | 425.8 | **₹15,652.58** |

### 2. Churn Model Performance (Flat vs. Trend-Augmented)

| Model Configuration | Feature Set | ROC-AUC | Active Class Precision | Active Class Recall | Active Class F1-Score | Overall Accuracy |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Logistic Regression (Baseline)** | Flat Snapshots | 0.5851 | 0.4602 | 0.3682 | 0.4091 | 66.40% |
| **Logistic Regression (+Trend)** | Trend-Augmented | 0.5813 | 0.4609 | 0.3669 | 0.4085 | 66.44% |
| **XGBoost Classifier (Baseline)** | Flat Snapshots | 0.5842 | 0.4441 | 0.3833 | 0.4115 | 65.36% |
| **XGBoost Classifier (+Trend)** | **Trend-Augmented** | **0.9982** | **0.9517** | **0.9836** | **0.9674** | **97.90%** |

### 3. Prescriptive Next-Best-Action Matrix (Headcount & Strategy)

| Churn Risk Tier | Low CLV (Bottom 50%) | Medium CLV (Middle 30%) | High CLV (Top 20%) | Action Strategy |
| :--- | :---: | :---: | :---: | :--- |
| **High Risk** | 5,548 | 5,355 | **1,286** | **High CLV:** VIP Concierge Call + ₹1,500 Voucher<br>**Med CLV:** Win-Back 15% Discount Email |
| **Medium Risk** | 33 | 64 | 397 | Proactive Product Cross-Sell Series |
| **Low Risk** | 3,668 | 129 | 2,017 | VIP Loyalty Program & Early Sale Access |

---

## 🛠️ How to Run
```bash
# 1. Generate Synthetic Dataset (if needed)
python generate_indian_dataset.py

# 2. Generate and Run Notebook
python generate_indian_notebook.py

# 3. Open Jupyter Notebook
jupyter notebook notebooks/01_ecommerce_customer_intelligence.ipynb
```
