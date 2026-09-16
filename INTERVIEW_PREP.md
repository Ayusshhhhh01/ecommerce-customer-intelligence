# Interview Preparation Guide: E-Commerce Customer Intelligence

This guide prepares you to present, justify, and answer tough technical & business questions about this project in **Product Analyst, Business Analyst, and Data Analyst** placement interviews.

---

## 🙋 Top 10 Interview Questions & Model Answers

### 1. How did you define Churn, and why 90 days?
> **Model Answer:**  
> *"In e-commerce, churn is unobserved (customers don't send a cancellation email; they simply stop buying). We calculated the empirical inter-purchase interval distribution for repeat buyers, which averaged **120.1 days (~4 months)**. We defined churn as no purchase activity within the last 90 days relative to observation max date. This threshold balances early detection of fading engagement with statistical confidence that the customer has passed their normal purchase cadence."*

---

### 2. Why is your repeat purchase rate ~25.5%, and how does it compare to industry benchmarks?
> **Model Answer:**  
> *"Our dataset models a horizontal e-commerce marketplace (like Flipkart or Amazon India), where high-intent category purchases (Electronics, Apparel, Home Goods) dominate customer acquisition. In horizontal marketplaces, initial acquisition drop-off is high, resulting in a **25.5% repeat purchase rate**, which aligns with industry benchmarks of 22%–28% for general e-commerce platforms."*

---

### 3. How did you handle class imbalance in churn prediction?
> **Model Answer:**  
> *"With ~68.4% churned vs 31.6% active customers, relying on accuracy alone would be misleading. We implemented **`class_weight='balanced'` in Logistic Regression** and **`scale_pos_weight=0.46` in XGBoost**, penalizing false negatives on the active class. We evaluated Precision, Recall, and F1-score specifically for the minority active class alongside ROC-AUC."*

---

### 4. Why did flat snapshot features result in ROC-AUC ~0.58, and how did trend features boost XGBoost to 0.998?
> **Model Answer:**  
> *"Flat features (`frequency`, `monetary`, `avg_order_val`) only measure historical volume, ignoring temporal momentum. We engineered 4 trend-based features—most notably `days_since_last_vs_avg_gap` (recency days divided by customer's own average gap) and `order_frequency_trend` (recent gap vs historical gap ratio). Because `days_since_last_vs_avg_gap` captures whether a customer is overdue relative to their personal baseline cadence, non-linear decision trees in XGBoost captured this threshold seamlessly, boosting ROC-AUC from 0.584 to 0.998."*

---

### 5. What did SHAP analysis reveal about behavioral churn drivers?
> **Model Answer:**  
> *"TreeSHAP revealed that the top 2 churn drivers were `days_since_last_vs_avg_gap` (SHAP 3.30) and `order_frequency_trend` (SHAP 1.44), showing that cadence extension is the strongest signal of churn. Additionally, logistics friction was a key operational driver: **delivery delays >2 days past promised delivery in Tier 2/3 cities increased churn velocity by 42%**."*

---

### 6. Why use BG/NBD and Gamma-Gamma for CLV instead of standard linear regression?
> **Model Answer:**  
> *"Standard linear regression assumes constant spending and ignores transaction timing. **BG/NBD (Beta-Geometric / Negative Binomial Distribution)** models the stochastic process of repeat transaction frequency and dropout rate, while the **Gamma-Gamma model** models monetary value independently. Combining them ($E[CLV_{12}] = E[N_{12}] \times E[M]$) accounts for customer heterogeneity and non-stationary purchasing behavior."*

---

### 7. How does the Next-Best-Action Matrix translate insights into business ROI?
> **Model Answer:**  
> *"Rather than treating all churned customers equally with expensive blanket discounts, we cross-tabulate Churn Risk (High/Med/Low) × CLV Tier (High/Med/Low). For the **1,286 High Risk + High CLV customers**, we deploy high-touch VIP retention (concierge call + ₹1,500 voucher), protecting **₹2.95L–₹4.43L in annual revenue** at a 20-30% win rate while avoiding unnecessary discount spend on low-value churners."*

---

### 8. What is the difference between single-month cohort active rate and cumulative repeat retention?
> **Model Answer:**  
> *"The monthly active cohort heatmap measures non-cumulative active customers in a single specific calendar month (showing 3.5%–5.7% active in Month 1). However, because repeat buyers take an average of **120.1 days** between orders, repeat purchases accumulate over time: Month 1 (6.1%) → Month 3 (9.8%) → Month 6 (17.6%) → Month 12+ (25.5%). Both metrics together provide a complete picture of active engagement vs lifetime repeat conversion."*

---

### 9. If you had access to real product clickstream data (cart additions, pageviews), how would you enhance this project?
> **Model Answer:**  
> *"I would engineer real-time funnel signals: search-to-cart conversion rate, session frequency decay, wishlist item drop-offs, and payment gateway abandonments. Incorporating session velocity prior to order placement would allow us to predict churn 30 days earlier before the customer misses their expected order date."*

---

### 10. How would you deploy this project into production?
> **Model Answer:**  
> *"I would deploy the feature engineering and XGBoost inference pipeline as an automated Airflow batch job running weekly. Churn risk scores and CLV tiers would be synced to our Customer Data Platform (CDP / Segment / Braze), automatically triggering dynamic SMS/Email win-back workflows when `days_since_last_vs_avg_gap > 1.2`."*
