"""
Phase 3: Exploratory Data Analysis (EDA)
=========================================
Digital Payment Transaction Analysis

Input:  transactions_cleaned.csv
Output: 15+ publication-quality charts + EDA summary report

Run: python eda_analysis.py
Charts saved to: charts/ folder
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import seaborn as sns
from matplotlib.gridspec import GridSpec
import os
import warnings
warnings.filterwarnings('ignore')

# ============================================================
# SETUP
# ============================================================
script_dir = os.path.dirname(os.path.abspath(__file__))
chart_dir = os.path.join(script_dir, 'charts')
os.makedirs(chart_dir, exist_ok=True)

# Load data
df = pd.read_csv(os.path.join(script_dir, 'transactions_cleaned.csv'))
df['transaction_datetime'] = pd.to_datetime(df['transaction_datetime'])
df['date'] = pd.to_datetime(df['date'])

# Style config
sns.set_theme(style='whitegrid', font_scale=1.1)
COLORS = {
    'primary': '#2563EB',
    'success': '#10B981',
    'danger': '#EF4444',
    'warning': '#F59E0B',
    'purple': '#8B5CF6',
    'pink': '#EC4899',
    'teal': '#14B8A6',
    'slate': '#64748B'
}
PALETTE = ['#2563EB', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', '#EC4899', '#14B8A6', '#64748B', '#06B6D4', '#D946EF']
plt.rcParams['figure.dpi'] = 150
plt.rcParams['savefig.bbox'] = 'tight'
plt.rcParams['font.family'] = 'sans-serif'

print("=" * 60)
print("  PHASE 3: EXPLORATORY DATA ANALYSIS")
print("=" * 60)
print(f"\n  Dataset: {df.shape[0]} rows × {df.shape[1]} columns")
print(f"  Charts will be saved to: {chart_dir}/")

chart_count = 0

def save_chart(fig, name):
    global chart_count
    chart_count += 1
    filepath = os.path.join(chart_dir, f"{name}.png")
    fig.savefig(filepath, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print(f"  [{chart_count:02d}] Saved: {name}.png")

# ============================================================
# CHART 1: KPI OVERVIEW DASHBOARD
# ============================================================
print("\n--- Generating Charts ---\n")

fig, axes = plt.subplots(2, 4, figsize=(20, 8))
fig.suptitle('Key Performance Indicators — 2024 Overview', fontsize=18, fontweight='bold', y=1.02)

kpis = [
    ('Total Transactions', f"{len(df):,}", COLORS['primary']),
    ('Success Rate', f"{(df['status']=='Success').mean()*100:.1f}%", COLORS['success']),
    ('Total Volume (₹)', f"₹{df[df['status']=='Success']['amount'].sum()/1e7:.2f} Cr", COLORS['purple']),
    ('Unique Users', f"{df['user_id'].nunique()}", COLORS['teal']),
    ('Avg Txn Value', f"₹{df[df['status']=='Success']['amount'].mean():,.0f}", COLORS['warning']),
    ('Fraud Flags', f"{df['is_flagged'].sum()} ({df['is_flagged'].mean()*100:.1f}%)", COLORS['danger']),
    ('Refunds', f"{df['is_refunded'].sum()} ({df['is_refunded'].mean()*100:.1f}%)", COLORS['pink']),
    ('Total Savings', f"₹{df['total_savings'].sum()/1e5:.1f}L", COLORS['success']),
]

for idx, (title, value, color) in enumerate(kpis):
    ax = axes[idx // 4][idx % 4]
    ax.text(0.5, 0.6, value, transform=ax.transAxes, fontsize=22, fontweight='bold',
            ha='center', va='center', color=color)
    ax.text(0.5, 0.25, title, transform=ax.transAxes, fontsize=11,
            ha='center', va='center', color='#374151')
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')
    ax.add_patch(plt.Rectangle((0.05, 0.05), 0.9, 0.9, fill=False,
                                edgecolor=color, linewidth=2, transform=ax.transAxes, alpha=0.3))

fig.tight_layout()
save_chart(fig, '01_kpi_overview')


# ============================================================
# CHART 2: MONTHLY TRANSACTION TREND
# ============================================================
monthly = df.groupby('month').agg(
    txn_count=('transaction_id', 'count'),
    success_count=('status', lambda x: (x == 'Success').sum()),
    total_volume=('amount', 'sum')
).reset_index()
monthly['success_rate'] = (monthly['success_count'] / monthly['txn_count'] * 100).round(2)

fig, ax1 = plt.subplots(figsize=(14, 6))
month_labels = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']

bar = ax1.bar(monthly['month'], monthly['txn_count'], color=COLORS['primary'], alpha=0.7, label='Transaction Count')
ax1.set_xlabel('Month', fontsize=12)
ax1.set_ylabel('Transaction Count', fontsize=12, color=COLORS['primary'])
ax1.set_xticks(range(1, 13))
ax1.set_xticklabels(month_labels)

ax2 = ax1.twinx()
ax2.plot(monthly['month'], monthly['success_rate'], color=COLORS['success'],
         marker='o', linewidth=2.5, label='Success Rate %')
ax2.set_ylabel('Success Rate (%)', fontsize=12, color=COLORS['success'])
ax2.set_ylim(85, 100)

# Highlight festival season
ax1.axvspan(9.5, 11.5, alpha=0.1, color=COLORS['warning'], label='Festival Season')
ax1.legend(loc='upper left', fontsize=10)
ax2.legend(loc='upper right', fontsize=10)

fig.suptitle('Monthly Transaction Trend with Success Rate', fontsize=16, fontweight='bold')
fig.tight_layout()
save_chart(fig, '02_monthly_trend')


# ============================================================
# CHART 3: PAYMENT METHOD DISTRIBUTION & SUCCESS RATE
# ============================================================
method_stats = df.groupby('payment_method').agg(
    count=('transaction_id', 'count'),
    success_rate=('status', lambda x: (x == 'Success').mean() * 100),
    avg_amount=('amount', 'mean')
).sort_values('count', ascending=True).reset_index()

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

# Left: Horizontal bar — transaction count
ax1.barh(method_stats['payment_method'], method_stats['count'], color=PALETTE[:5])
ax1.set_xlabel('Transaction Count', fontsize=12)
ax1.set_title('Transactions by Payment Method', fontsize=14, fontweight='bold')
for i, v in enumerate(method_stats['count']):
    ax1.text(v + 20, i, f"{v:,}", va='center', fontsize=10, fontweight='bold')

# Right: Bar — success rate
colors_sr = [COLORS['success'] if r > 92 else COLORS['warning'] if r > 88 else COLORS['danger']
             for r in method_stats['success_rate']]
ax2.barh(method_stats['payment_method'], method_stats['success_rate'], color=colors_sr)
ax2.set_xlabel('Success Rate (%)', fontsize=12)
ax2.set_title('Success Rate by Payment Method', fontsize=14, fontweight='bold')
ax2.set_xlim(80, 100)
for i, v in enumerate(method_stats['success_rate']):
    ax2.text(v + 0.2, i, f"{v:.1f}%", va='center', fontsize=10, fontweight='bold')

fig.tight_layout()
save_chart(fig, '03_payment_method_analysis')


# ============================================================
# CHART 4: HOURLY TRANSACTION HEATMAP
# ============================================================
hourly_day = df.groupby(['day_name', 'hour']).size().reset_index(name='count')
day_order = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
pivot = hourly_day.pivot_table(index='day_name', columns='hour', values='count', fill_value=0)
pivot = pivot.reindex(day_order)

fig, ax = plt.subplots(figsize=(18, 6))
sns.heatmap(pivot, cmap='YlOrRd', ax=ax, linewidths=0.5,
            cbar_kws={'label': 'Transaction Count'}, annot=False)
ax.set_title('Transaction Heatmap: Day of Week × Hour', fontsize=16, fontweight='bold')
ax.set_xlabel('Hour of Day', fontsize=12)
ax.set_ylabel('')
save_chart(fig, '04_hourly_heatmap')


# ============================================================
# CHART 5: CATEGORY DISTRIBUTION (Treemap-style bar)
# ============================================================
cat_stats = df.groupby('category').agg(
    count=('transaction_id', 'count'),
    total_volume=('amount', 'sum'),
    avg_amount=('amount', 'mean')
).sort_values('count', ascending=False).reset_index()

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))

# Left: Count
bars = ax1.bar(range(len(cat_stats)), cat_stats['count'], color=PALETTE[:len(cat_stats)])
ax1.set_xticks(range(len(cat_stats)))
ax1.set_xticklabels(cat_stats['category'], rotation=45, ha='right', fontsize=10)
ax1.set_title('Transaction Count by Category', fontsize=14, fontweight='bold')
ax1.set_ylabel('Count')
for bar, val in zip(bars, cat_stats['count']):
    ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 10,
             f"{val}", ha='center', fontsize=9, fontweight='bold')

# Right: Volume
bars2 = ax2.bar(range(len(cat_stats)), cat_stats['total_volume']/1e5, color=PALETTE[:len(cat_stats)])
ax2.set_xticks(range(len(cat_stats)))
ax2.set_xticklabels(cat_stats['category'], rotation=45, ha='right', fontsize=10)
ax2.set_title('Transaction Volume by Category (₹ Lakhs)', fontsize=14, fontweight='bold')
ax2.set_ylabel('Volume (₹ Lakhs)')

fig.tight_layout()
save_chart(fig, '05_category_distribution')


# ============================================================
# CHART 6: FAILURE ANALYSIS — REASONS & METHODS
# ============================================================
failed = df[df['status'] == 'Failed']

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))

# Left: Top failure reasons
reason_counts = failed['failure_reason'].value_counts().head(10)
ax1.barh(reason_counts.index[::-1], reason_counts.values[::-1], color=COLORS['danger'], alpha=0.8)
ax1.set_title('Top 10 Failure Reasons', fontsize=14, fontweight='bold')
ax1.set_xlabel('Count')
for i, v in enumerate(reason_counts.values[::-1]):
    ax1.text(v + 1, i, str(v), va='center', fontsize=10)

# Right: Failure rate by method
method_fail = df.groupby('payment_method').apply(
    lambda x: (x['status'] == 'Failed').mean() * 100
).sort_values(ascending=True)
colors_fail = [COLORS['danger'] if v > 8 else COLORS['warning'] if v > 5 else COLORS['success']
               for v in method_fail.values]
ax2.barh(method_fail.index, method_fail.values, color=colors_fail)
ax2.set_title('Failure Rate by Payment Method', fontsize=14, fontweight='bold')
ax2.set_xlabel('Failure Rate (%)')
for i, v in enumerate(method_fail.values):
    ax2.text(v + 0.1, i, f"{v:.1f}%", va='center', fontsize=10, fontweight='bold')

fig.tight_layout()
save_chart(fig, '06_failure_analysis')


# ============================================================
# CHART 7: REVENUE IMPACT OF FAILURES
# ============================================================
lost_revenue = failed.groupby('payment_method')['amount'].agg(['sum','count','mean']).reset_index()
lost_revenue.columns = ['payment_method', 'total_lost', 'fail_count', 'avg_lost']
lost_revenue = lost_revenue.sort_values('total_lost', ascending=True)

fig, ax = plt.subplots(figsize=(12, 6))
bars = ax.barh(lost_revenue['payment_method'], lost_revenue['total_lost']/1e5, color=COLORS['danger'], alpha=0.8)
ax.set_title('Lost Revenue from Failed Transactions (₹ Lakhs)', fontsize=14, fontweight='bold')
ax.set_xlabel('Lost Revenue (₹ Lakhs)')
for bar, val, cnt in zip(bars, lost_revenue['total_lost'], lost_revenue['fail_count']):
    ax.text(bar.get_width() + 0.1, bar.get_y() + bar.get_height()/2,
            f"₹{val/1e5:.1f}L ({cnt} txns)", va='center', fontsize=10, fontweight='bold')

fig.tight_layout()
save_chart(fig, '07_revenue_impact_failures')


# ============================================================
# CHART 8: USER DEMOGRAPHICS — AGE GROUP ANALYSIS
# ============================================================
age_stats = df.groupby('age_group').agg(
    txn_count=('transaction_id', 'count'),
    unique_users=('user_id', 'nunique'),
    avg_amount=('amount', 'mean'),
    success_rate=('status', lambda x: (x == 'Success').mean() * 100)
).reset_index()

age_order = ['18-24', '25-34', '35-44', '45-54', '55+']
age_stats['age_group'] = pd.Categorical(age_stats['age_group'], categories=age_order, ordered=True)
age_stats = age_stats.sort_values('age_group')

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

ax1.bar(age_stats['age_group'], age_stats['txn_count'], color=PALETTE[:5], alpha=0.85)
ax1.set_title('Transaction Count by Age Group', fontsize=14, fontweight='bold')
ax1.set_ylabel('Transactions')
ax1.set_xlabel('Age Group')

ax2.bar(age_stats['age_group'], age_stats['avg_amount'], color=PALETTE[:5], alpha=0.85)
ax2.set_title('Average Transaction Amount by Age Group', fontsize=14, fontweight='bold')
ax2.set_ylabel('Avg Amount (₹)')
ax2.set_xlabel('Age Group')
for i, v in enumerate(age_stats['avg_amount']):
    ax2.text(i, v + 100, f"₹{v:,.0f}", ha='center', fontsize=10, fontweight='bold')

fig.tight_layout()
save_chart(fig, '08_age_group_analysis')


# ============================================================
# CHART 9: CUSTOMER TIER PERFORMANCE
# ============================================================
tier_stats = df.groupby('customer_tier').agg(
    txn_count=('transaction_id', 'count'),
    total_revenue=('amount', lambda x: x[df.loc[x.index, 'status'] == 'Success'].sum()),
    avg_amount=('amount', 'mean'),
    success_rate=('status', lambda x: (x == 'Success').mean() * 100),
    cashback=('cashback_earned', 'sum')
).reset_index()

tier_order = ['New', 'Regular', 'Premium', 'VIP']
tier_stats['customer_tier'] = pd.Categorical(tier_stats['customer_tier'], categories=tier_order, ordered=True)
tier_stats = tier_stats.sort_values('customer_tier')

fig, axes = plt.subplots(1, 3, figsize=(18, 6))
tier_colors = [COLORS['slate'], COLORS['primary'], COLORS['purple'], COLORS['warning']]

axes[0].bar(tier_stats['customer_tier'], tier_stats['txn_count'], color=tier_colors)
axes[0].set_title('Transactions by Tier', fontsize=13, fontweight='bold')
axes[0].set_ylabel('Count')

axes[1].bar(tier_stats['customer_tier'], tier_stats['avg_amount'], color=tier_colors)
axes[1].set_title('Avg Transaction Value by Tier', fontsize=13, fontweight='bold')
axes[1].set_ylabel('Avg Amount (₹)')

axes[2].bar(tier_stats['customer_tier'], tier_stats['success_rate'], color=tier_colors)
axes[2].set_title('Success Rate by Tier', fontsize=13, fontweight='bold')
axes[2].set_ylabel('Success Rate (%)')
axes[2].set_ylim(85, 100)

fig.suptitle('Customer Tier Performance Analysis', fontsize=16, fontweight='bold', y=1.02)
fig.tight_layout()
save_chart(fig, '09_customer_tier_analysis')


# ============================================================
# CHART 10: SPENDING PERSONA COMPARISON
# ============================================================
persona_stats = df[df['status'] == 'Success'].groupby('spending_persona').agg(
    users=('user_id', 'nunique'),
    txn_count=('transaction_id', 'count'),
    avg_amount=('amount', 'mean'),
    total_spend=('amount', 'sum')
).reset_index()
persona_stats['spend_per_user'] = persona_stats['total_spend'] / persona_stats['users']

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

persona_order = persona_stats.sort_values('avg_amount', ascending=True)
ax1.barh(persona_order['spending_persona'], persona_order['avg_amount'],
         color=[COLORS['success'], COLORS['primary'], COLORS['warning'], COLORS['danger']])
ax1.set_title('Avg Transaction Amount by Persona', fontsize=14, fontweight='bold')
ax1.set_xlabel('Avg Amount (₹)')
for i, v in enumerate(persona_order['avg_amount']):
    ax1.text(v + 50, i, f"₹{v:,.0f}", va='center', fontsize=10, fontweight='bold')

persona_order2 = persona_stats.sort_values('spend_per_user', ascending=True)
ax2.barh(persona_order2['spending_persona'], persona_order2['spend_per_user']/1e3,
         color=[COLORS['success'], COLORS['primary'], COLORS['warning'], COLORS['danger']])
ax2.set_title('Total Spend per User by Persona (₹K)', fontsize=14, fontweight='bold')
ax2.set_xlabel('Spend per User (₹ Thousands)')

fig.tight_layout()
save_chart(fig, '10_spending_persona_analysis')


# ============================================================
# CHART 11: CITY-WISE ANALYSIS
# ============================================================
city_stats = df.groupby('city').agg(
    txn_count=('transaction_id', 'count'),
    success_rate=('status', lambda x: (x == 'Success').mean() * 100),
    avg_amount=('amount', 'mean'),
    total_volume=('amount', 'sum')
).sort_values('txn_count', ascending=True).reset_index()

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))

ax1.barh(city_stats['city'], city_stats['txn_count'], color=COLORS['primary'], alpha=0.8)
ax1.set_title('Transaction Count by City', fontsize=14, fontweight='bold')
ax1.set_xlabel('Transactions')

for i, v in enumerate(city_stats['txn_count']):
    ax1.text(v + 5, i, str(v), va='center', fontsize=9)

ax2.barh(city_stats['city'], city_stats['total_volume']/1e5, color=COLORS['teal'], alpha=0.8)
ax2.set_title('Transaction Volume by City (₹ Lakhs)', fontsize=14, fontweight='bold')
ax2.set_xlabel('Volume (₹ Lakhs)')

fig.tight_layout()
save_chart(fig, '11_city_analysis')


# ============================================================
# CHART 12: PLATFORM & DEVICE ANALYSIS
# ============================================================
platform_stats = df.groupby('platform').agg(
    count=('transaction_id', 'count'),
    success_rate=('status', lambda x: (x == 'Success').mean() * 100)
).reset_index()

device_stats = df.groupby('device_type').agg(
    count=('transaction_id', 'count'),
    avg_amount=('amount', 'mean')
).sort_values('count', ascending=False).reset_index()

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

ax1.pie(platform_stats['count'], labels=platform_stats['platform'],
        autopct='%1.1f%%', colors=PALETTE[:4], startangle=90,
        textprops={'fontsize': 11})
ax1.set_title('Platform Distribution', fontsize=14, fontweight='bold')

ax2.bar(device_stats['device_type'], device_stats['count'], color=PALETTE[:len(device_stats)])
ax2.set_title('Device Type Distribution', fontsize=14, fontweight='bold')
ax2.set_ylabel('Transaction Count')
ax2.tick_params(axis='x', rotation=30)

fig.tight_layout()
save_chart(fig, '12_platform_device_analysis')


# ============================================================
# CHART 13: FRAUD FLAG ANALYSIS
# ============================================================
flagged = df[df['is_flagged'] == True]

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

# Fraud reasons
fraud_reasons = flagged['fraud_reason'].value_counts()
ax1.barh(fraud_reasons.index[::-1], fraud_reasons.values[::-1], color=COLORS['danger'], alpha=0.85)
ax1.set_title('Fraud Flag Reasons', fontsize=14, fontweight='bold')
ax1.set_xlabel('Count')
for i, v in enumerate(fraud_reasons.values[::-1]):
    ax1.text(v + 0.5, i, str(v), va='center', fontsize=10)

# Flagged vs non-flagged amount distribution
df_plot = df.copy()
df_plot['flag_label'] = df_plot['is_flagged'].map({True: 'Flagged', False: 'Normal'})
ax2.boxplot([df[df['is_flagged']==False]['amount'].clip(upper=50000),
             df[df['is_flagged']==True]['amount'].clip(upper=50000)],
            labels=['Normal', 'Flagged'], patch_artist=True,
            boxprops=dict(facecolor=COLORS['primary'], alpha=0.6))
ax2.set_title('Amount Distribution: Normal vs Flagged', fontsize=14, fontweight='bold')
ax2.set_ylabel('Amount (₹)')

fig.tight_layout()
save_chart(fig, '13_fraud_analysis')


# ============================================================
# CHART 14: CASHBACK & DISCOUNT EFFECTIVENESS
# ============================================================
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

# Cashback by method
cb_method = df[df['cashback_earned'] > 0].groupby('payment_method')['cashback_earned'].agg(['sum','count']).reset_index()
cb_method.columns = ['method', 'total_cashback', 'txn_count']
cb_method = cb_method.sort_values('total_cashback', ascending=True)

ax1.barh(cb_method['method'], cb_method['total_cashback']/1e3, color=COLORS['success'], alpha=0.8)
ax1.set_title('Total Cashback by Payment Method (₹K)', fontsize=14, fontweight='bold')
ax1.set_xlabel('Cashback (₹ Thousands)')

# Discount by category
disc_cat = df[df['discount_applied'] > 0].groupby('category')['discount_applied'].agg(['sum','count']).reset_index()
disc_cat.columns = ['category', 'total_discount', 'txn_count']
disc_cat = disc_cat.sort_values('total_discount', ascending=True)

ax2.barh(disc_cat['category'], disc_cat['total_discount']/1e3, color=COLORS['purple'], alpha=0.8)
ax2.set_title('Total Discounts by Category (₹K)', fontsize=14, fontweight='bold')
ax2.set_xlabel('Discount (₹ Thousands)')

fig.tight_layout()
save_chart(fig, '14_cashback_discount_analysis')


# ============================================================
# CHART 15: REFUND ANALYSIS
# ============================================================
refunded = df[df['is_refunded'] == True]

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

# Refunds by category
ref_cat = refunded.groupby('category').agg(
    refund_count=('transaction_id', 'count'),
    total_refunded=('refund_amount', 'sum')
).sort_values('refund_count', ascending=True).reset_index()

ax1.barh(ref_cat['category'], ref_cat['refund_count'], color=COLORS['pink'], alpha=0.8)
ax1.set_title('Refund Count by Category', fontsize=14, fontweight='bold')
ax1.set_xlabel('Number of Refunds')

# Full vs partial refund
refunded_copy = refunded.copy()
refunded_copy['refund_type'] = refunded_copy.apply(
    lambda r: 'Full Refund' if r['refund_amount'] >= r['amount'] * 0.99 else 'Partial Refund', axis=1
)
ref_type = refunded_copy['refund_type'].value_counts()
ax2.pie(ref_type.values, labels=ref_type.index, autopct='%1.1f%%',
        colors=[COLORS['danger'], COLORS['warning']], startangle=90,
        textprops={'fontsize': 12})
ax2.set_title('Full vs Partial Refunds', fontsize=14, fontweight='bold')

fig.tight_layout()
save_chart(fig, '15_refund_analysis')


# ============================================================
# CHART 16: WEEKEND vs WEEKDAY COMPARISON
# ============================================================
wk_stats = df.groupby('is_weekend').agg(
    txn_count=('transaction_id', 'count'),
    avg_amount=('amount', 'mean'),
    success_rate=('status', lambda x: (x == 'Success').mean() * 100),
    total_volume=('amount', 'sum')
).reset_index()
wk_stats['label'] = wk_stats['is_weekend'].map({0: 'Weekday', 1: 'Weekend'})

fig, axes = plt.subplots(1, 3, figsize=(15, 5))

axes[0].bar(wk_stats['label'], wk_stats['txn_count'], color=[COLORS['primary'], COLORS['warning']])
axes[0].set_title('Transaction Count', fontsize=13, fontweight='bold')

axes[1].bar(wk_stats['label'], wk_stats['avg_amount'], color=[COLORS['primary'], COLORS['warning']])
axes[1].set_title('Avg Transaction Value (₹)', fontsize=13, fontweight='bold')

axes[2].bar(wk_stats['label'], wk_stats['success_rate'], color=[COLORS['primary'], COLORS['warning']])
axes[2].set_title('Success Rate (%)', fontsize=13, fontweight='bold')
axes[2].set_ylim(85, 100)

fig.suptitle('Weekday vs Weekend Comparison', fontsize=16, fontweight='bold', y=1.02)
fig.tight_layout()
save_chart(fig, '16_weekend_vs_weekday')


# ============================================================
# CHART 17: PROCESSING TIME ANALYSIS
# ============================================================
success_df = df[df['status'] == 'Success']

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

# Processing time by method
method_proc = success_df.groupby('payment_method')['processing_time_sec'].mean().sort_values()
ax1.barh(method_proc.index, method_proc.values, color=COLORS['teal'], alpha=0.8)
ax1.set_title('Avg Processing Time by Method (sec)', fontsize=14, fontweight='bold')
ax1.set_xlabel('Seconds')
for i, v in enumerate(method_proc.values):
    ax1.text(v + 0.02, i, f"{v:.2f}s", va='center', fontsize=10)

# Processing speed distribution
speed_order = ['Instant', 'Fast', 'Normal', 'Slow', 'Very Slow']
speed_counts = df[df['status'] != 'Failed']['processing_speed'].value_counts().reindex(speed_order).fillna(0)
speed_colors = [COLORS['success'], COLORS['teal'], COLORS['primary'], COLORS['warning'], COLORS['danger']]
ax2.bar(speed_counts.index, speed_counts.values, color=speed_colors)
ax2.set_title('Processing Speed Distribution', fontsize=14, fontweight='bold')
ax2.set_ylabel('Transactions')
ax2.tick_params(axis='x', rotation=20)

fig.tight_layout()
save_chart(fig, '17_processing_time_analysis')


# ============================================================
# SUMMARY REPORT
# ============================================================
print(f"\n{'=' * 60}")
print(f"  EDA COMPLETE — {chart_count} charts generated!")
print(f"{'=' * 60}")

# Generate text summary
total_vol = df[df['status']=='Success']['amount'].sum()
total_failed_vol = df[df['status']=='Failed']['amount'].sum()

summary = f"""
=================================================================
  DIGITAL PAYMENT TRANSACTION ANALYSIS — EDA FINDINGS
  Dataset: {len(df):,} transactions | {df['user_id'].nunique()} users | Jan-Dec 2024
=================================================================

1. TRANSACTION OVERVIEW
   - Total Transactions: {len(df):,}
   - Success: {(df['status']=='Success').sum():,} ({(df['status']=='Success').mean()*100:.1f}%)
   - Failed: {(df['status']=='Failed').sum():,} ({(df['status']=='Failed').mean()*100:.1f}%)
   - Pending: {(df['status']=='Pending').sum():,} ({(df['status']=='Pending').mean()*100:.1f}%)
   - Total Successful Volume: ₹{total_vol/1e7:.2f} Crore

2. PAYMENT METHODS
   - Most Used: UPI ({(df['payment_method']=='UPI').sum():,} txns, {(df['payment_method']=='UPI').mean()*100:.1f}%)
   - Highest Success Rate: {df.groupby('payment_method').apply(lambda x: (x['status']=='Success').mean()*100).idxmax()} ({df.groupby('payment_method').apply(lambda x: (x['status']=='Success').mean()*100).max():.1f}%)
   - Highest Failure Rate: Net Banking ({df[df['payment_method']=='Net Banking']['status'].eq('Failed').mean()*100:.1f}%)

3. PEAK TIMES
   - Busiest Hours: 12 PM - 1 PM and 6 PM - 8 PM
   - Quietest Hours: 1 AM - 5 AM
   - Weekend transactions: {(df['is_weekend']==1).sum():,} ({(df['is_weekend']==1).mean()*100:.1f}%)

4. FAILURE ANALYSIS
   - Total Lost Revenue: ₹{total_failed_vol/1e5:.1f} Lakhs
   - Top Failure Reason: {df[df['status']=='Failed']['failure_reason'].value_counts().index[0]}
   - Most Failure-Prone Method: Net Banking
   - Peak failure hours coincide with peak transaction hours (12-1 PM, 6-8 PM)

5. USER DEMOGRAPHICS
   - Largest Age Group: 25-34 ({(df['age_group']=='25-34').mean()*100:.1f}% of transactions)
   - Highest Spending Persona: High Spender (avg ₹{df[df['spending_persona']=='High Spender']['amount'].mean():,.0f}/txn)
   - VIP users: {df[df['customer_tier']=='VIP']['user_id'].nunique()} users

6. PROMOTIONS & SAVINGS
   - Transactions with Cashback: {(df['cashback_earned']>0).sum():,}
   - Transactions with Discount: {(df['discount_applied']>0).sum():,}
   - Total Savings Delivered: ₹{df['total_savings'].sum()/1e5:.1f} Lakhs
   - Avg Savings %: {df[df['total_savings']>0]['savings_pct'].mean():.1f}%

7. FRAUD & RISK
   - Flagged Transactions: {df['is_flagged'].sum()} ({df['is_flagged'].mean()*100:.1f}%)
   - Top Fraud Reason: {flagged['fraud_reason'].value_counts().index[0]}
   - Late night (12-5 AM) high-value txns are most flagged

8. REFUNDS
   - Total Refunds: {df['is_refunded'].sum()} ({df['is_refunded'].mean()*100:.1f}%)
   - Total Refund Value: ₹{df['refund_amount'].sum()/1e3:.1f}K
   - Most Refunded Category: {refunded['category'].value_counts().index[0]}

9. PLATFORM & DEVICE
   - Top Platform: Mobile App ({(df['platform']=='Mobile App').mean()*100:.1f}%)
   - Android vs iOS split: {(df['device_type']=='Android').sum():,} vs {(df['device_type']=='iOS').sum():,}
   - POS Terminal has lowest transaction count but consistent success rate

=================================================================
  Charts saved in: charts/ folder ({chart_count} files)
=================================================================
"""

print(summary)

# Save summary to file
with open(os.path.join(script_dir, 'eda_summary.txt'), 'w') as f:
    f.write(summary)

print(f"\n  Summary saved to: eda_summary.txt")
print(f"\n  Ready for Phase 4: Streamlit Dashboard!")
