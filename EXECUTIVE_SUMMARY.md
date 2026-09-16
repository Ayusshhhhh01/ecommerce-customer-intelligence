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

### 3. Predictive Model Performance
- **XGBoost Churn Model:** Achieves **0.9982 ROC-AUC** and an **F1-score of 0.9674** by leveraging trend-based velocity features (`days_since_last_vs_avg_gap`, `order_frequency_trend`).

---

## 🎯 Prescriptive Next-Best-Action Strategy

| Customer Segment | Risk & Value Quadrant | Headcount | Prescriptive Strategy & Action | Projected Impact |
| :--- | :--- | :---: | :--- | :--- |
| **High Risk + High CLV** | Critical At-Risk VIPs | **1,286** | **VIP Urgent Retention:** Dedicated concierge outreach + ₹1,500 exclusive category voucher. | Protects **₹2.95 Lakhs – ₹4.43 Lakhs** in annual revenue @ 20-30% win rate. |
| **High Risk + Medium CLV** | Win-Back Targets | **5,355** | **Automated Win-Back Campaign:** Targeted 15% category discount via SMS & Email. | Re-engages mid-tier buyers before complete dormancy. |
| **Low Risk + High CLV** | Brand Champions | **2,017** | **VIP Loyalty Program:** Early sale access, priority delivery, & referral incentives. | Increases average order frequency by 15-20%. |
| **High Risk + Low CLV** | Low-Value Churners | **5,548** | **Low-Cost Push Series:** Automated lifecycle notifications (zero discount spend). | Cost-effective passive re-engagement. |

---

## 💰 Projected Financial Impact
By executing the **VIP Urgent Retention Strategy** on the 1,286 High Risk + High CLV customers:
- **At 10% Campaign Win Rate:** Protects **₹1.48 Lakhs** in annual net revenue.
- **At 20% Campaign Win Rate:** Protects **₹2.95 Lakhs** in annual net revenue.
- **At 30% Campaign Win Rate:** Protects **₹4.43 Lakhs** in annual net revenue.

---

## 🛠️ Immediate 90-Day Implementation Roadmap
1. **Days 1–30:** Integrate XGBoost churn scoring script into marketing automation tools (Klaviyo/WebEngage) to trigger alerts when `days_since_last_vs_avg_gap > 1.2`.
2. **Days 31–60:** Deploy automated 30-day post-first-purchase onboarding series offering a 10% UPI-only discount to address the 74.5% first-to-second order drop-off.
3. **Days 61–90:** Launch Tier 2/3 delivery tracking SLA alerts to trigger proactive ₹100 wallet credit for orders delayed past promised dates.
