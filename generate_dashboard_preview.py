import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np

# Load summary CSVs
rfm_df = pd.read_csv('dashboard/rfm_segment_summary.csv')
funnel_df = pd.DataFrame({
    'Stage': ['1st Purchase', '2nd Purchase', '3rd Purchase', '4th+ Purchase'],
    'Customers': [18497, 4714, 1354, 316],
    'Pct': [100.0, 25.5, 7.3, 1.7]
})
matrix_df = pd.DataFrame({
    'CLV_Tier': ['Low CLV', 'Medium CLV', 'High CLV'],
    'High Risk': [2952, 1956, 1258],
    'Medium Risk': [2943, 2103, 1119],
    'Low Risk': [3354, 1489, 1323]
}).set_index('CLV_Tier')

fig = plt.figure(figsize=(16, 10), facecolor='#f8f9fa')
fig.suptitle('E-Commerce Customer Intelligence — Executive Power BI Dashboard Preview', fontsize=18, fontweight='bold', y=0.96)

# Panel 1: Top KPI Cards
ax1 = plt.subplot2grid((3, 3), (0, 0), colspan=3)
ax1.axis('off')

kpis = [
    ('Total Delivered Revenue', 'Rs. 11.03 Cr', '#1f77b4'),
    ('Delivered Customers', '18,497', '#2ca02c'),
    ('Repeat Purchase Rate', '25.49%', '#ff7f0e'),
    ('High Risk + High CLV Headcount', '1,258', '#d62728'),
    ('Protected Revenue (@20% Win Rate)', 'Rs. 9.08 Lakhs', '#9467bd')
]

for idx, (title, val, color) in enumerate(kpis):
    x_pos = 0.02 + idx * 0.195
    rect = plt.Rectangle((x_pos, 0.15), 0.18, 0.7, transform=ax1.transAxes, color=color, alpha=0.15, ec=color, lw=2)
    ax1.add_patch(rect)
    ax1.text(x_pos + 0.09, 0.60, title, transform=ax1.transAxes, ha='center', fontsize=10, fontweight='bold', color='#333333')
    ax1.text(x_pos + 0.09, 0.32, val, transform=ax1.transAxes, ha='center', fontsize=14, fontweight='bold', color=color)

# Panel 2: RFM Revenue Contribution Bar Chart
ax2 = plt.subplot2grid((3, 3), (1, 0), colspan=2)
sns.barplot(data=rfm_df, x='total_revenue', y='segment', palette='Blues_r', ax=ax2)
ax2.set_title('Revenue Contribution by RFM Segment (in Rs.)', fontsize=12, fontweight='bold')
ax2.set_xlabel('Total Spend (BRL/INR)', fontsize=10)
ax2.set_ylabel('')

for p in ax2.patches:
    width = p.get_width()
    ax2.annotate(f"Rs. {width/10000000:.2f}Cr" if width >= 10000000 else f"Rs. {width/100000:.2f}L",
                 (width, p.get_y() + p.get_height() / 2.),
                 ha='left', va='center', xytext=(5, 0), textcoords='offset points', fontsize=9, fontweight='bold')

# Panel 3: Funnel Retention Chart
ax3 = plt.subplot2grid((3, 3), (1, 2))
bars = ax3.bar(funnel_df['Stage'], funnel_df['Customers'], color='#3690c0', width=0.5)
ax3.set_title('Repeat Purchase Funnel', fontsize=12, fontweight='bold')
ax3.set_ylabel('Customers', fontsize=10)
plt.xticks(rotation=15)

for bar, pct in zip(bars, funnel_df['Pct']):
    height = bar.get_height()
    ax3.annotate(f"{pct}%", (bar.get_x() + bar.get_width() / 2, height), ha='center', va='bottom', fontsize=9, fontweight='bold')

# Panel 4: Next-Best-Action Matrix Heatmap
ax4 = plt.subplot2grid((3, 3), (2, 0), colspan=3)
sns.heatmap(matrix_df.T, annot=True, fmt='d', cmap='OrRd', cbar=False, ax=ax4, annot_kws={'fontsize': 11, 'fontweight': 'bold'})
ax4.set_title('Prescriptive Next-Best-Action Matrix (Churn Risk vs CLV Tier Headcount)', fontsize=12, fontweight='bold')
ax4.set_xlabel('CLV Tier', fontsize=10)
ax4.set_ylabel('Churn Risk Tier', fontsize=10)

plt.tight_layout(rect=[0, 0, 1, 0.94])
plt.savefig('dashboard/powerbi_executive_dashboard.png', dpi=300)
plt.close()

print('[SUCCESS] Generated dashboard/powerbi_executive_dashboard.png')
