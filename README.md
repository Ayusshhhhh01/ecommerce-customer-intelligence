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
├── src/                                  # Modular Python Source Code
│   ├── data_loader.py                    # Fact table & dataset loading functions
│   └── rfm_analytics.py                  # RFM scoring & segmentation logic
├── dashboard/                            # Exported summary tables & visuals for Power BI
│   ├── powerbi_executive_dashboard.png   # 4-panel executive dashboard preview
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
├── generate_dashboard_preview.py         # Dashboard image generator script
├── EXECUTIVE_SUMMARY.md                  # 1-page business report for leadership
├── INTERVIEW_PREP.md                     # 10 interview Q&As, Data Leakage Audit, & model answers
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

### 2. Forward-Looking Temporal Churn Model Performance

| Model Configuration | Target Design | ROC-AUC | Active Class Precision | Active Class Recall | Active Class F1-Score | Overall Accuracy |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Logistic Regression (Forward)** | Temporal $T-90$ Cutoff | **0.6256** | **0.1582** | **0.5518** | **0.2459** | **63.47%** |
| **XGBoost Classifier (Forward)** | **Temporal $T-90$ Cutoff** | **0.6220** | **0.1600** | **0.5480** | **0.2477** | **64.10%** |

### 3. Prescriptive Next-Best-Action Matrix (Quantile Tercile Headcount & Strategy)

| Churn Risk Tier | Low CLV (Bottom 50%) | Medium CLV (Middle 30%) | High CLV (Top 20%) | Action Strategy | Total Headcount |
| :--- | :---: | :---: | :---: | :--- | :---: |
| **High Risk** (Top 33.3%) | 2,952 | 1,956 | **1,258** | **High CLV:** VIP Concierge Call + ₹1,500 Voucher<br>**Med CLV:** Win-Back 15% Discount Offer<br>**Low CLV:** Automated Low-Cost Push Series | **6,166** |
| **Medium Risk** (Middle 33.3%) | 2,943 | 2,103 | 1,119 | Proactive Product Cross-Sell & Engagement | **6,165** |
| **Low Risk** (Bottom 33.3%) | 3,354 | 1,489 | 1,323 | VIP Loyalty Program & Early Sale Access | **6,166** |
| **Total Customer Headcount** | **9,249** | **5,548** | **3,700** | **All Scored Delivered Customers** | **18,497** |

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
