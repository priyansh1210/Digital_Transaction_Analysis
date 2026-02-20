"""
Phase 2: Data Cleaning & Feature Engineering Pipeline
=====================================================
Input:  transactions_raw.csv, user_profiles.csv
Output: transactions_cleaned.csv (enriched with derived features)

This pipeline:
1. Loads and validates raw data
2. Fixes data types and handles nulls
3. Derives time-based features
4. Creates spending tiers and behavioral features
5. Merges user demographics
6. Adds derived KPI columns
7. Exports clean, analysis-ready dataset
"""

import pandas as pd
import numpy as np
import os
import warnings
warnings.filterwarnings('ignore')

# ============================================================
# 1. LOAD RAW DATA
# ============================================================
print("=" * 60)
print("  PHASE 2: DATA CLEANING & FEATURE ENGINEERING")
print("=" * 60)

script_dir = os.path.dirname(os.path.abspath(__file__))
txn_path = os.path.join(script_dir, 'transactions_raw.csv')
user_path = os.path.join(script_dir, 'user_profiles.csv')

df = pd.read_csv(txn_path)
users = pd.read_csv(user_path)

print(f"\n[1] Raw data loaded:")
print(f"    Transactions: {df.shape[0]} rows x {df.shape[1]} columns")
print(f"    User profiles: {users.shape[0]} rows x {users.shape[1]} columns")

# ============================================================
# 2. DATA TYPE FIXES & VALIDATION
# ============================================================
print(f"\n[2] Fixing data types...")

# Parse datetime
df['transaction_datetime'] = pd.to_datetime(df['transaction_datetime'])

# Ensure numeric columns
numeric_cols = ['amount', 'processing_time_sec', 'cashback_earned',
                'discount_applied', 'refund_amount']
for col in numeric_cols:
    df[col] = pd.to_numeric(df[col], errors='coerce')

# Ensure boolean columns
bool_cols = ['is_flagged', 'is_refunded']
for col in bool_cols:
    df[col] = df[col].astype(bool)

df['is_weekend'] = df['is_weekend'].astype(int)

# Validate: no duplicate transaction IDs
dupes = df['transaction_id'].duplicated().sum()
print(f"    Duplicate transaction IDs: {dupes}")

# Validate: all user_ids in transactions exist in profiles
missing_users = set(df['user_id']) - set(users['user_id'])
print(f"    Orphan user IDs (not in profiles): {len(missing_users)}")

print("    Data types fixed ✓")

# ============================================================
# 3. HANDLE NULLS & CLEAN TEXT
# ============================================================
print(f"\n[3] Handling nulls and cleaning...")

# failure_reason: fill NaN for Success/Pending with 'None'
df['failure_reason'] = df['failure_reason'].fillna('None')

# fraud_reason: fill NaN with 'None'
df['fraud_reason'] = df['fraud_reason'].fillna('None')

# Strip whitespace from string columns
str_cols = ['transaction_id', 'user_id', 'payment_method', 'category',
            'merchant', 'status', 'failure_reason', 'platform',
            'device_type', 'city', 'fraud_reason']
for col in str_cols:
    df[col] = df[col].str.strip()

# Validate nulls
remaining_nulls = df.isnull().sum()
if remaining_nulls.sum() > 0:
    print(f"    Remaining nulls:\n{remaining_nulls[remaining_nulls > 0]}")
else:
    print("    No nulls remaining ✓")

# ============================================================
# 4. TIME-BASED FEATURE ENGINEERING
# ============================================================
print(f"\n[4] Engineering time-based features...")

df['date'] = df['transaction_datetime'].dt.date
df['year'] = df['transaction_datetime'].dt.year
df['month'] = df['transaction_datetime'].dt.month
df['month_name'] = df['transaction_datetime'].dt.strftime('%b')
df['day'] = df['transaction_datetime'].dt.day
df['day_of_week'] = df['transaction_datetime'].dt.dayofweek  # 0=Mon, 6=Sun
df['day_name'] = df['transaction_datetime'].dt.strftime('%A')
df['hour'] = df['transaction_datetime'].dt.hour
df['week_number'] = df['transaction_datetime'].dt.isocalendar().week.astype(int)

# Quarter
df['quarter'] = df['transaction_datetime'].dt.quarter
df['quarter_label'] = 'Q' + df['quarter'].astype(str)

# Time of day buckets
def get_time_bucket(hour):
    if 5 <= hour < 12:
        return 'Morning'
    elif 12 <= hour < 17:
        return 'Afternoon'
    elif 17 <= hour < 21:
        return 'Evening'
    else:
        return 'Night'

df['time_bucket'] = df['hour'].apply(get_time_bucket)

# Is month end (last 5 days) — salary spending pattern
df['is_month_end'] = (df['day'] >= 26).astype(int)

# Is month start (first 5 days) — post-salary spending
df['is_month_start'] = (df['day'] <= 5).astype(int)

# Festival season flag (Oct-Nov)
df['is_festival_season'] = df['month'].isin([10, 11]).astype(int)

print(f"    Added: date, year, month, month_name, day, day_of_week, day_name,")
print(f"           hour, week_number, quarter, quarter_label, time_bucket,")
print(f"           is_month_end, is_month_start, is_festival_season ✓")

# ============================================================
# 5. AMOUNT-BASED FEATURES
# ============================================================
print(f"\n[5] Engineering amount-based features...")

# Amount buckets
def get_amount_bucket(amount):
    if amount < 100:
        return 'Micro (<₹100)'
    elif amount < 500:
        return 'Small (₹100-500)'
    elif amount < 2000:
        return 'Medium (₹500-2K)'
    elif amount < 10000:
        return 'Large (₹2K-10K)'
    elif amount < 50000:
        return 'High (₹10K-50K)'
    else:
        return 'Premium (₹50K+)'

df['amount_bucket'] = df['amount'].apply(get_amount_bucket)

# Net amount after discount and cashback
df['net_amount'] = df['amount'] - df['discount_applied'] - df['cashback_earned']
df['net_amount'] = df['net_amount'].clip(lower=0).round(2)

# Effective savings
df['total_savings'] = (df['discount_applied'] + df['cashback_earned']).round(2)

# Savings percentage
df['savings_pct'] = np.where(
    df['amount'] > 0,
    (df['total_savings'] / df['amount'] * 100).round(2),
    0
)

print(f"    Added: amount_bucket, net_amount, total_savings, savings_pct ✓")

# ============================================================
# 6. MERGE USER DEMOGRAPHICS
# ============================================================
print(f"\n[6] Merging user demographics...")

# Rename user city to avoid conflict
users_merge = users.rename(columns={'city': 'user_home_city'})

df = df.merge(users_merge, on='user_id', how='left')

print(f"    Merged columns: age_group, gender, account_tenure, customer_tier,")
print(f"                    spending_persona, preferred_method, user_home_city ✓")

# ============================================================
# 7. USER-LEVEL BEHAVIORAL FEATURES
# ============================================================
print(f"\n[7] Computing user-level behavioral features...")

# Transaction count per user
user_txn_count = df.groupby('user_id')['transaction_id'].count().reset_index()
user_txn_count.columns = ['user_id', 'user_total_txns']

# Total spend per user
user_total_spend = df[df['status'] == 'Success'].groupby('user_id')['amount'].sum().reset_index()
user_total_spend.columns = ['user_id', 'user_total_spend']

# Avg spend per transaction
user_avg_spend = df[df['status'] == 'Success'].groupby('user_id')['amount'].mean().reset_index()
user_avg_spend.columns = ['user_id', 'user_avg_txn_amount']
user_avg_spend['user_avg_txn_amount'] = user_avg_spend['user_avg_txn_amount'].round(2)

# Failure rate per user
user_fail = df.groupby('user_id').apply(
    lambda x: (x['status'] == 'Failed').sum() / len(x) * 100
).reset_index()
user_fail.columns = ['user_id', 'user_failure_rate_pct']
user_fail['user_failure_rate_pct'] = user_fail['user_failure_rate_pct'].round(2)

# Merge all user features
for feat_df in [user_txn_count, user_total_spend, user_avg_spend, user_fail]:
    df = df.merge(feat_df, on='user_id', how='left')

# Fill NaN for users with no successful transactions
df['user_total_spend'] = df['user_total_spend'].fillna(0)
df['user_avg_txn_amount'] = df['user_avg_txn_amount'].fillna(0)

# User spending tier based on total spend
def get_spending_tier(spend):
    if spend < 10000:
        return 'Low'
    elif spend < 50000:
        return 'Medium'
    elif spend < 200000:
        return 'High'
    else:
        return 'Very High'

df['user_spending_tier'] = df['user_total_spend'].apply(get_spending_tier)

print(f"    Added: user_total_txns, user_total_spend, user_avg_txn_amount,")
print(f"           user_failure_rate_pct, user_spending_tier ✓")

# ============================================================
# 8. PROCESSING TIME CATEGORY
# ============================================================
print(f"\n[8] Categorizing processing times...")

def get_speed_category(row):
    if row['status'] == 'Failed':
        return 'Failed'
    elif row['processing_time_sec'] <= 1.0:
        return 'Instant'
    elif row['processing_time_sec'] <= 2.0:
        return 'Fast'
    elif row['processing_time_sec'] <= 5.0:
        return 'Normal'
    elif row['processing_time_sec'] <= 15.0:
        return 'Slow'
    else:
        return 'Very Slow'

df['processing_speed'] = df.apply(get_speed_category, axis=1)

print(f"    Added: processing_speed ✓")

# ============================================================
# 9. FINAL COLUMN ORDERING & EXPORT
# ============================================================
print(f"\n[9] Finalizing and exporting...")

# Organize columns into logical groups
column_order = [
    # Identifiers
    'transaction_id', 'user_id',

    # Timestamp & derived time features
    'transaction_datetime', 'date', 'year', 'month', 'month_name',
    'quarter', 'quarter_label', 'day', 'day_of_week', 'day_name',
    'hour', 'time_bucket', 'week_number',
    'is_weekend', 'is_month_start', 'is_month_end', 'is_festival_season',

    # Transaction details
    'payment_method', 'category', 'merchant', 'platform', 'device_type', 'city',

    # Amount features
    'amount', 'amount_bucket', 'discount_applied', 'cashback_earned',
    'total_savings', 'savings_pct', 'net_amount',

    # Status & processing
    'status', 'failure_reason', 'processing_time_sec', 'processing_speed',

    # Fraud & refund
    'is_flagged', 'fraud_reason', 'is_refunded', 'refund_amount',

    # User demographics (from profiles)
    'age_group', 'gender', 'account_tenure', 'customer_tier',
    'spending_persona', 'preferred_method', 'user_home_city',

    # User behavioral features
    'user_total_txns', 'user_total_spend', 'user_avg_txn_amount',
    'user_failure_rate_pct', 'user_spending_tier'
]

df = df[column_order]

# Save cleaned dataset
output_path = os.path.join(script_dir, 'transactions_cleaned.csv')
df.to_csv(output_path, index=False)

# ============================================================
# 10. VALIDATION SUMMARY
# ============================================================
print(f"\n{'=' * 60}")
print(f"  PHASE 2 COMPLETE — DATASET SUMMARY")
print(f"{'=' * 60}")

print(f"\n  Output: transactions_cleaned.csv")
print(f"  Shape:  {df.shape[0]} rows x {df.shape[1]} columns")
print(f"  Size:   {os.path.getsize(output_path) / (1024*1024):.2f} MB")

print(f"\n  Column Groups:")
print(f"    Identifiers:        2")
print(f"    Time features:      16")
print(f"    Transaction detail:  6")
print(f"    Amount features:     7")
print(f"    Status/processing:   4")
print(f"    Fraud & refund:      4")
print(f"    User demographics:   7")
print(f"    User behavioral:     5")
print(f"    TOTAL:              {len(column_order)}")

print(f"\n  Data Quality Checks:")
print(f"    Null values:        {df.isnull().sum().sum()}")
print(f"    Duplicate IDs:      {df['transaction_id'].duplicated().sum()}")
print(f"    Date range:         {df['date'].min()} to {df['date'].max()}")
print(f"    Amount range:       ₹{df['amount'].min():.2f} to ₹{df['amount'].max():,.2f}")

print(f"\n  Feature Distributions:")
print(f"    Time Buckets:       {df['time_bucket'].value_counts().to_dict()}")
print(f"    Amount Buckets:     {df['amount_bucket'].value_counts().to_dict()}")
print(f"    Processing Speed:   {df['processing_speed'].value_counts().to_dict()}")
print(f"    User Spend Tiers:   {df['user_spending_tier'].value_counts().to_dict()}")

print(f"\n  Savings Summary:")
print(f"    Txns with cashback:   {(df['cashback_earned'] > 0).sum()}")
print(f"    Txns with discount:   {(df['discount_applied'] > 0).sum()}")
print(f"    Total savings value:  ₹{df['total_savings'].sum():,.2f}")
print(f"    Avg savings %:        {df[df['total_savings'] > 0]['savings_pct'].mean():.2f}%")

print(f"\n{'=' * 60}")
print(f"  Ready for Phase 3: EDA & Analysis!")
print(f"{'=' * 60}")
