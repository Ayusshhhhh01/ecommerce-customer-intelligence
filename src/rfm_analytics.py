"""
RFM Analytics & Segmentation Module
Project: E-Commerce Customer Intelligence
"""

import pandas as pd
import numpy as np

def compute_rfm_segments(fact_df, conn):
    rfm_sql = """
    SELECT 
        customer_id,
        MAX(order_date) AS last_order_date,
        MIN(order_date) AS first_order_date,
        COUNT(DISTINCT order_id) AS frequency,
        ROUND(SUM(order_total_amount), 2) AS monetary
    FROM customer_order_fact
    GROUP BY customer_id;
    """
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
    return rfm
