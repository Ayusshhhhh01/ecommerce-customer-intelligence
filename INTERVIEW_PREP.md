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
> *"With ~68.4% churned vs 31.6% active customers, relying on accuracy alone would be misleading. We implemented **`class_weight='balanced'` in Logistic Regression** and **`scale_pos_weight` in XGBoost**, penalizing false negatives on the active class. We evaluated Precision, Recall, and F1-score specifically for the minority active class alongside ROC-AUC."*

---

### 4. How did you audit and prevent Data Leakage in your Churn Model?
> **Model Answer:**  
> *"When we initially tested snapshot ratio features like `days_since_last_vs_avg_gap` (`recency_days / avg_inter_gap`), the XGBoost ROC-AUC jumped to 0.998. Upon performing a SHAP audit, `days_since_last_vs_avg_gap` contributed over 63% of total model importance. Because churn was defined as `recency_days > 90`, feeding recency-derived ratios directly into a retrospective snapshot model constituted target leakage (the feature contained the target label definition).*
> 
> *To fix this fundamentally, we built a **Forward-Looking Temporal Churn Design**: we selected a cutoff date $T = \text{max\_order\_date} - 90 \text{ days}$, engineered all customer features using transaction history strictly up to $T$, and defined churn as zero order activity during $[T+1 \text{ to } T+90]$. This allowed pre-cutoff recency (`recency_days_at_T`) and cadence variance (`days_since_last_vs_avg_gap`) to be evaluated legitimately without target leakage, resulting in an un-leaked **ROC-AUC of 0.6220 (XGBoost) / 0.6256 (Logistic Regression)**."*

---

### 5. What did SHAP analysis reveal about forward-looking behavioral churn drivers?
> **Model Answer:**  
> *"TreeSHAP on the un-leaked forward-looking XGBoost model revealed that **City Tier (`is_tier1`: 0.2644)** and **Order Frequency Trend (`order_frequency_trend`: 0.1311)** were the top drivers. `order_frequency_trend` measures the ratio of the inter-purchase interval on the 2 most recent orders vs. historical baseline gap—capturing purchase velocity deceleration before churn occurs. Category diversity (0.0661) and pre-cutoff recency (0.0640) also provided significant signal."*

---

### 6. Why use BG/NBD and Gamma-Gamma for CLV instead of standard linear regression?
> **Model Answer:**  
> *"Standard linear regression assumes constant spending and ignores transaction timing. **BG/NBD (Beta-Geometric / Negative Binomial Distribution)** models the stochastic process of repeat transaction frequency and dropout rate, while the **Gamma-Gamma model** models monetary value independently. Combining them ($E[CLV_{12}] = E[N_{12}] \times E[M]$) accounts for customer heterogeneity and non-stationary purchasing behavior."*

---

### 7. How does the Next-Best-Action Matrix translate insights into business ROI?
> **Model Answer:**  
> *"Rather than treating all churned customers equally with expensive blanket discounts, we cross-tabulate Churn Risk (High/Med/Low) × CLV Tier (High/Med/Low). For high-value at-risk customers, we deploy high-touch VIP retention (concierge call + voucher), protecting at-risk revenue at a 20-30% win rate while avoiding unnecessary discount spend on low-value churners."*

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
> *"I would deploy the feature engineering and XGBoost inference pipeline as an automated Airflow batch job running weekly using a 90-day forward-looking target window. Churn risk scores and CLV tiers would be synced to our Customer Data Platform (CDP / Segment / Braze), automatically triggering dynamic SMS/Email win-back workflows when velocity shifts occur."*

---

### 11. Why did you use quantile-based terciles for churn risk tiering instead of fixed probability thresholds?
> **Model Answer:**  
> *"In rare-event classification (such as a forward-looking 90-day retention window where active buyers are a minority class), predicted probabilities from calibrated models cluster around the base rate. Applying fixed thresholds (e.g., $P \ge 0.60$ High, $P \ge 0.30$ Medium) collapses almost the entire customer base into High and Medium risk (sweeping >99% above 0.30), leaving the Low Risk bucket virtually empty.*
> 
> *To maintain an actionable 3-tier operational framework for marketing operations, we used **quantile-based terciles** (`pd.qcut` into top 33.3% High, middle 33.3% Medium, bottom 33.3% Low Risk). This relative rank-ordering ensures equal, balanced operational capacity allocation across marketing channels, exactly matching how CLV tiers are constructed."*

---

### 12. What did the cross-tabulation reveal about the relationship between customer value (CLV) and churn risk?
> **Model Answer:**  
> *"Our 3x3 matrix revealed that churn risk is statistically independent of customer Lifetime Value (CLV). High-CLV customers split almost evenly across risk tiers: **1,323 Low Risk (35.8%)**, **1,119 Medium Risk (30.2%)**, and **1,258 High Risk (34.0%)** out of 3,700 top spenders.*
> 
> *This provides a compelling business justification for systematic predictive scoring: leadership cannot assume top spenders are safe by default. Without proactive model scoring, 34% of High-CLV customers (1,258 VIPs representing ₹45.40 Lakhs in expected 12-month spend) would silently drift into dormancy without intervention."*
