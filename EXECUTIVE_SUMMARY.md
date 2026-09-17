# Executive Summary: E-Commerce Customer Intelligence
**Title:** Customer Churn, Lifetime Value (CLV) & Next-Best-Action Strategy  
**Target Audience:** Chief Commercial Officer, VP of Growth, Head of Product & Marketing  
**Scope:** 18,497 Active Delivered Customers | ₹11.03 Crore Historical Delivered Revenue  

---

## 📌 Executive Problem Statement
Acquisition-focused growth without post-purchase retention leads to leaky-bucket dynamics. In our e-commerce platform, **74.51% of acquired customers never place a second order**, creating heavy dependence on paid acquisition channels. Leadership required an end-to-end framework to identify churn drivers, quantify Customer Lifetime Value (CLV), and deploy automated, high-ROI retention interventions.

---

## 💡 Key Strategic Findings

### 1. Repeat Customer Concentration & Revenue Asymmetry
- **The Retention Core:** Repeat customers (25.49% of the customer base) account for **44.09% of total historical revenue (₹4.86 Crore)**.
- **Spend Multiplier:** Champions (top recent repeat buyers) average **₹13,824.25 spend per customer**—over **3x the average single-purchase spend (₹4,529.69)**.
- **The Retention Friction Point:** Retention decay is steepest immediately following the 1st purchase (74.51% drop-off). Once a customer completes their 2nd order, their conversion to a 3rd order jumps to **28.72%**.

### 2. Primary Churn Drivers (SHAP Behavioral Analysis)
- ** cadence Variance (`days_since_last_vs_avg_gap`):** Customers exceeding 1.2x their personal average inter-purchase interval represent an acute churn risk.
- **Logistics Friction in Tier 2/3 Cities:** Delivery delays exceeding 2 days past promised delivery dates increase churn velocity by **42%** in non-metro regions.
- **Payment & Return Dynamics:** Cash-on-Delivery (COD) transactions exhibit a **3.6x higher cancellation/return rate (18-20%)** compared to prepaid UPI transactions (4-5%).

### 3. Predictive Model Performance & Data Leakage Resolution
- **Forward-Looking Temporal Churn Design:** Built using a strict temporal cutoff ($T = \text{max\_order\_date} - 90 \text{ days}$) to evaluate features prior to $T$ against customer activity in $[T+1, T+90]$, eliminating data leakage.
- **Model Performance:** **XGBoost Classifier Forward ROC-AUC: 0.6220** | **Logistic Regression Forward ROC-AUC: 0.6256**.
- **Top SHAP Drivers:** City Tier (`is_tier1`: 0.2644), Order Frequency Trend (`order_frequency_trend`: 0.1311), Category Diversity (`category_diversity`: 0.0661), Pre-cutoff Recency (`recency_days_at_T`: 0.0640), and Cadence Variance (`days_since_last_vs_avg_gap`: 0.0520).

### 4. Independence of Churn Risk and Customer Value Tier
- **Non-Intuitive Risk Distribution:** Churn risk is statistically independent of customer Lifetime Value (CLV). High-CLV customers split almost equally across risk tiers: **1,323 Low Risk (35.8%)**, **1,119 Medium Risk (30.2%)**, and **1,258 High Risk (34.0%)** out of 3,700 top spenders.
- **The Operational Imperative:** Leadership cannot assume top spenders are safe by default. Without systematic model scoring, **34% of High-CLV customers (1,258 VIPs representing ₹45.40 Lakhs in expected 12-month spend)** would silently drift into dormancy without intervention.

---

## 🎯 Prescriptive Next-Best-Action Strategy

| Customer Segment | Risk & Value Quadrant | Headcount | Prescriptive Strategy & Action | Projected Impact |
| :--- | :--- | :---: | :--- | :--- |
| **High Risk + High CLV** | Critical At-Risk VIPs | **1,258** | **VIP Urgent Retention:** Dedicated concierge outreach + ₹1,500 exclusive category voucher. | Protects **₹9.08 Lakhs** in annual revenue @ 20% win rate (out of ₹45.40L total risk). |
| **High Risk + Medium CLV** | Win-Back Targets | **1,956** | **Automated Win-Back Campaign:** Targeted 15% category discount offer. | Re-engages mid-tier buyers before complete dormancy (₹21.35L total risk). |
| **High Risk + Low CLV** | Low-Value Churners | **2,952** | **Low-Cost Push Notification Series:** Automated lifecycle notifications. | Zero discount spend passive re-engagement (₹14.78L total risk). |
| **Medium Risk + High CLV** | High-Potential Growth | **1,119** | **Proactive Engagement & Cross-Sell:** Product recommendations + category discovery. | Safeguards **₹25.90 Lakhs** total expected CLV. |
| **Low Risk + High CLV** | Brand Champions | **1,323** | **VIP Loyalty Program:** Early sale access, priority delivery, & rewards. | Protects **₹31.79 Lakhs** top spender CLV & advocacy. |

---

## 💰 Projected Financial Impact
By executing the **VIP Urgent Retention Strategy** on the 1,258 High Risk + High CLV customers (avg. expected spend ₹3,609.12):
- **At 10% Campaign Win Rate:** Protects **₹4.54 Lakhs** in annual net revenue.
- **At 20% Campaign Win Rate:** Protects **₹9.08 Lakhs** in annual net revenue.
- **At 30% Campaign Win Rate:** Protects **₹13.62 Lakhs** in annual net revenue.

---

## 🛠️ Immediate 90-Day Implementation Roadmap
1. **Days 1–30:** Integrate XGBoost churn scoring script into marketing automation tools (Klaviyo/WebEngage) to trigger alerts when `days_since_last_vs_avg_gap > 1.2`.
2. **Days 31–60:** Deploy automated 30-day post-first-purchase onboarding series offering a 10% UPI-only discount to address the 74.5% first-to-second order drop-off.
3. **Days 61–90:** Launch Tier 2/3 delivery tracking SLA alerts to trigger proactive ₹100 wallet credit for orders delayed past promised dates.
