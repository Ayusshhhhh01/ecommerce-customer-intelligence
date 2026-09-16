# E-Commerce Customer Intelligence: Churn, CLV & Next-Best-Action

**Target Roles:** Product Analyst | Business Analyst | Data Analyst  
**Tech Stack:** SQL (SQLite), Python (Pandas, Scikit-learn, XGBoost, SHAP, Lifetimes), Power BI  
**Local Project Path:** `D:\Ssshhhh\Projexts\E commerce`

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
│   ├── orders.csv                        # 35,000 orders (UPI, COD, Card, Net Banking)
│   ├── order_items.csv                   # 45,400+ line items in ₹ INR
│   ├── delivery_info.csv                 # Promised vs Actual Delivery Date & Latency
│   ├── reviews.csv                       # Customer Review Scores (1-5)
│   └── DATASET_DISCLOSURE.md             # Dataset disclaimer documentation
├── sql/                                  # Production SQL Scripts
│   ├── 01_customer_order_fact.sql        # Fact table construction
│   └── 02_rfm_metrics.sql                # RFM aggregations & LAG window functions
├── notebooks/                            # Jupyter Notebooks
│   └── 01_ecommerce_customer_intelligence.ipynb
├── generate_indian_dataset.py            # Synthetic dataset generator script
├── generate_indian_notebook.py           # Notebook generator script
└── README.md                             # Project documentation
```

---

## 🚀 Key Results (Steps 1 & 2 Completed)

- **Total Delivered Transactions:** 31,716 delivered order records across **18,934 unique customers**.
- **Total Historical Delivered Revenue:** **₹14.12 Crore** (Exact: ₹14,11,68,546.87).
- **Repeat Purchase Rate:** **42.79%** (8,102 repeat buyers out of 18,934 delivered customers).
- **Average Inter-Purchase Interval:** **114.4 days** for repeat buyers.

### RFM Segment Breakdown (INR Lakh/Crore Notation)

| Segment Name | Customer Count | % Customers | Total Revenue (₹) | % Revenue | Avg Recency (Days) | Avg Monetary (₹) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Loyal Customers** | 4,031 | 21.29% | **₹3.99Cr** | 28.26% | 96.9 | ₹9,895.38 |
| **Champions** | 1,823 | 9.63% | **₹2.99Cr** | 21.16% | 53.1 | **₹16,384.95** |
| **Hibernating / Lost** | 3,585 | 18.93% | **₹1.86Cr** | 13.20% | 463.2 | ₹5,199.43 |
| **New Customers** | 3,363 | 17.76% | **₹1.52Cr** | 10.78% | 59.6 | ₹4,523.35 |
| **At-Risk** | 1,393 | 7.36% | **₹1.44Cr** | 10.21% | 276.8 | ₹10,349.66 |
| **About to Sleep** | 2,401 | 12.68% | **₹1.08Cr** | 7.64% | 280.3 | ₹4,491.84 |
| **Promising / Potential Loyalists** | 2,154 | 11.38% | **₹97.34L** | 6.90% | 160.5 | ₹4,518.93 |
| **Can't Lose Them** | 184 | 0.97% | **₹26.23L** | 1.86% | 414.8 | **₹14,254.13** |

---

## 🛠️ How to Run
```bash
# 1. Generate Synthetic Dataset (if needed)
python generate_indian_dataset.py

# 2. Run Step 1 & 2 Test Script
python test_rfm_indian.py

# 3. Open Jupyter Notebook
jupyter notebook notebooks/01_ecommerce_customer_intelligence.ipynb
```
