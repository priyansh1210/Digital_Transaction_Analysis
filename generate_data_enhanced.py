import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import calendar
import random
import os

np.random.seed(42)
random.seed(42)

# ============================================================
# CONFIGURATION
# ============================================================
N = 60000
start_date = datetime(2024, 1, 1)
end_date = datetime(2025, 12, 31)

# ============================================================
# 1. USER PROFILES (500 users with demographics)
# ============================================================
age_groups = ['18-24', '25-34', '35-44', '45-54', '55+']
age_weights = [0.18, 0.35, 0.25, 0.14, 0.08]

genders = ['Male', 'Female', 'Other']
gender_weights = [0.52, 0.46, 0.02]

account_tenures = ['0-6 months', '6-12 months', '1-2 years', '2-5 years', '5+ years']
tenure_weights = [0.12, 0.15, 0.25, 0.30, 0.18]

customer_tiers = ['New', 'Regular', 'Premium', 'VIP']
tier_weights = [0.15, 0.45, 0.28, 0.12]

cities = ['Mumbai', 'Delhi', 'Bangalore', 'Hyderabad', 'Chennai',
          'Pune', 'Kolkata', 'Ahmedabad', 'Jaipur', 'Lucknow',
          'Chandigarh', 'Indore', 'Coimbatore', 'Kochi', 'Guwahati']
city_weights = [0.16, 0.14, 0.14, 0.10, 0.09,
                0.07, 0.06, 0.05, 0.04, 0.04,
                0.03, 0.03, 0.02, 0.02, 0.01]

# Build user profiles
user_ids = [f"USR{str(i).zfill(5)}" for i in range(1, 501)]
user_profiles = {}
for uid in user_ids:
    city = random.choices(cities, weights=city_weights, k=1)[0]
    age_group = random.choices(age_groups, weights=age_weights, k=1)[0]
    gender = random.choices(genders, weights=gender_weights, k=1)[0]
    tenure = random.choices(account_tenures, weights=tenure_weights, k=1)[0]
    tier = random.choices(customer_tiers, weights=tier_weights, k=1)[0]

    # Spending persona — influences amount and frequency
    persona = random.choices(
        ['Budget', 'Moderate', 'High Spender', 'Impulse'],
        weights=[0.30, 0.40, 0.20, 0.10], k=1
    )[0]

    # Preferred payment method per user (adds realistic stickiness)
    preferred_method = random.choices(
        ['UPI', 'Credit Card', 'Debit Card', 'Net Banking', 'Mobile Wallet'],
        weights=[0.40, 0.18, 0.15, 0.12, 0.15], k=1
    )[0]

    user_profiles[uid] = {
        'city': city,
        'age_group': age_group,
        'gender': gender,
        'account_tenure': tenure,
        'customer_tier': tier,
        'spending_persona': persona,
        'preferred_method': preferred_method
    }

# Save user profiles
user_df = pd.DataFrame([
    {'user_id': uid, **profile} for uid, profile in user_profiles.items()
])

# ============================================================
# 2. PAYMENT METHODS & CATEGORIES
# ============================================================
payment_methods = ['UPI', 'Credit Card', 'Debit Card', 'Net Banking', 'Mobile Wallet']
method_weights = [0.40, 0.18, 0.15, 0.12, 0.15]

categories = ['Food & Dining', 'Shopping', 'Bills & Utilities', 'Travel',
              'Entertainment', 'Health', 'Education', 'Transfers', 'Groceries', 'Investments']
cat_weights = [0.20, 0.17, 0.15, 0.10, 0.09, 0.06, 0.04, 0.06, 0.08, 0.05]

merchants = {
    'Food & Dining': ['Swiggy', 'Zomato', 'Dominos', 'McDonalds', 'Starbucks', 'KFC', 'Pizza Hut', 'Haldirams'],
    'Shopping': ['Amazon', 'Flipkart', 'Myntra', 'Ajio', 'Meesho', 'Nykaa', 'Croma', 'Reliance Digital'],
    'Bills & Utilities': ['Jio Recharge', 'Airtel', 'Electricity Board', 'Gas Agency', 'Water Board', 'Broadband Bill', 'DTH Recharge'],
    'Travel': ['IRCTC', 'MakeMyTrip', 'Uber', 'Ola', 'RedBus', 'Yatra', 'GoIbibo', 'Rapido'],
    'Entertainment': ['Netflix', 'Spotify', 'BookMyShow', 'Hotstar', 'Amazon Prime', 'YouTube Premium', 'Sony LIV'],
    'Health': ['Pharmeasy', 'Apollo Pharmacy', '1mg', 'Practo', 'Netmeds', 'MediBuddy', 'Tata Health'],
    'Education': ['Udemy', 'Coursera', 'Unacademy', "BYJU'S", 'Skillshare', 'Simplilearn', 'upGrad'],
    'Transfers': ['Google Pay P2P', 'PhonePe P2P', 'Paytm P2P', 'NEFT Transfer', 'IMPS Transfer', 'UPI Transfer'],
    'Groceries': ['BigBasket', 'Blinkit', 'Zepto', 'JioMart', 'DMart', 'Swiggy Instamart'],
    'Investments': ['Zerodha', 'Groww', 'CAMS Mutual Fund', 'Paytm Money', 'Coin by Zerodha']
}

amount_ranges = {
    'Food & Dining': (50, 2500),
    'Shopping': (200, 15000),
    'Bills & Utilities': (100, 5000),
    'Travel': (150, 12000),
    'Entertainment': (99, 1500),
    'Health': (50, 8000),
    'Education': (500, 20000),
    'Transfers': (100, 50000),
    'Groceries': (80, 4000),
    'Investments': (500, 100000)
}

# ============================================================
# 3. FAILURE CONFIGURATION
# ============================================================
failure_rates = {
    'UPI': 0.06,
    'Credit Card': 0.04,
    'Debit Card': 0.08,
    'Net Banking': 0.10,
    'Mobile Wallet': 0.05
}

failure_reasons = {
    'UPI': ['Server Timeout', 'Insufficient Balance', 'Invalid UPI ID', 'Bank Server Down', 'Transaction Limit Exceeded'],
    'Credit Card': ['Card Declined', 'Insufficient Limit', 'CVV Mismatch', 'Card Expired', '3D Auth Failed'],
    'Debit Card': ['Insufficient Balance', 'Card Blocked', 'PIN Incorrect', 'Daily Limit Exceeded', 'Bank Server Down'],
    'Net Banking': ['Session Expired', 'OTP Failed', 'Bank Server Down', 'Authentication Failed', 'Timeout'],
    'Mobile Wallet': ['Insufficient Balance', 'Wallet Limit Exceeded', 'KYC Pending', 'Server Error', 'Invalid PIN']
}

# ============================================================
# 4. PLATFORMS & SEASONAL CONFIG
# ============================================================
platforms = ['Mobile App', 'Web Browser', 'POS Terminal', 'QR Code']
platform_weights = [0.45, 0.25, 0.15, 0.15]

# Monthly multipliers for seasonal patterns
# Spikes: Jan (New Year sales), Mar (Holi), Aug (Independence Day sales),
# Oct-Nov (Diwali/festive), Dec (Christmas/year-end)
monthly_multiplier = {
    1: 1.15, 2: 0.90, 3: 1.05, 4: 0.95, 5: 0.90, 6: 0.85,
    7: 1.00, 8: 1.10, 9: 1.05, 10: 1.30, 11: 1.35, 12: 1.20
}

# Category-specific seasonal boosts
seasonal_category_boost = {
    10: {'Shopping': 1.6, 'Food & Dining': 1.3, 'Entertainment': 1.2},
    11: {'Shopping': 1.8, 'Food & Dining': 1.4, 'Travel': 1.3, 'Entertainment': 1.3},
    12: {'Shopping': 1.3, 'Travel': 1.4, 'Food & Dining': 1.2},
    3:  {'Shopping': 1.2, 'Food & Dining': 1.3},
    8:  {'Shopping': 1.4},
}

# ============================================================
# 5. GENERATE TRANSACTIONS
# ============================================================
hour_weights = [0.5, 0.3, 0.2, 0.2, 0.2, 0.3, 0.8, 1.5, 2.5, 3.5,
                4.0, 4.5, 5.0, 4.5, 3.5, 3.0, 3.5, 4.0, 4.5, 5.0,
                4.5, 3.5, 2.5, 1.5]

# Distribute transactions across 24 months (2024 + 2025) using monthly_multiplier
all_months = [(y, m) for y in [2024, 2025] for m in range(1, 13)]
total_weight = sum(monthly_multiplier[m] for _, m in all_months)
monthly_txn_counts = {}
remaining = N
for i, (year, month) in enumerate(all_months):
    if i == len(all_months) - 1:
        monthly_txn_counts[(year, month)] = remaining
    else:
        count = int(N * (monthly_multiplier[month] / total_weight))
        monthly_txn_counts[(year, month)] = count
        remaining -= count

records = []
txn_counter = 0

for (year, month), count in monthly_txn_counts.items():
    # Calculate days in month (handles leap years automatically)
    days_in_month = calendar.monthrange(year, month)[1]

    for _ in range(count):
        txn_counter += 1
        txn_id = f"TXN{str(txn_counter).zfill(7)}"
        user_id = random.choice(user_ids)
        profile = user_profiles[user_id]

        # --- Date & Time ---
        day = random.randint(1, days_in_month)
        hour = random.choices(range(24), weights=hour_weights, k=1)[0]
        minute = random.randint(0, 59)
        second = random.randint(0, 59)
        txn_datetime = datetime(year, month, day, hour, minute, second)

        # --- Day type ---
        day_of_week = txn_datetime.weekday()
        is_weekend = 1 if day_of_week >= 5 else 0

        # --- Payment Method (biased toward user's preferred method) ---
        user_method_weights = list(method_weights)
        pref_idx = payment_methods.index(profile['preferred_method'])
        user_method_weights[pref_idx] *= 2.5  # boost preferred method
        method = random.choices(payment_methods, weights=user_method_weights, k=1)[0]

        # --- Category (with seasonal boost) ---
        adjusted_cat_weights = list(cat_weights)
        if month in seasonal_category_boost:
            for cat, boost in seasonal_category_boost[month].items():
                idx = categories.index(cat)
                adjusted_cat_weights[idx] *= boost
        # Weekend boost for Food, Entertainment, Shopping
        if is_weekend:
            for cat in ['Food & Dining', 'Entertainment', 'Shopping']:
                idx = categories.index(cat)
                adjusted_cat_weights[idx] *= 1.2

        category = random.choices(categories, weights=adjusted_cat_weights, k=1)[0]
        merchant = random.choice(merchants[category])

        # --- Amount (influenced by persona) ---
        lo, hi = amount_ranges[category]
        persona_multiplier = {
            'Budget': 0.6, 'Moderate': 1.0, 'High Spender': 1.8, 'Impulse': 1.3
        }
        base_amount = random.uniform(lo, hi)
        amount = round(base_amount * persona_multiplier[profile['spending_persona']], 2)
        amount = max(lo, min(amount, hi * 2))  # cap but allow some overflow for high spenders

        # --- Status ---
        # Higher failure rates during peak hours (12-14, 18-21)
        peak_failure_boost = 1.4 if hour in [12, 13, 18, 19, 20] else 1.0
        fail_rate = failure_rates[method] * peak_failure_boost

        is_failed = random.random() < fail_rate
        if is_failed:
            status = 'Failed'
            reason = random.choice(failure_reasons[method])
        else:
            if random.random() < 0.03:
                status = 'Pending'
                reason = 'Processing'
            else:
                status = 'Success'
                reason = None

        # --- Platform ---
        platform = random.choices(platforms, weights=platform_weights, k=1)[0]

        # --- City (from user profile) ---
        city = profile['city']

        # --- Processing Time ---
        if status == 'Success':
            processing_time = round(random.uniform(0.5, 3.0), 2)
        elif status == 'Failed':
            processing_time = round(random.uniform(2.0, 15.0), 2)
        else:
            processing_time = round(random.uniform(5.0, 30.0), 2)

        # --- Cashback / Discount ---
        cashback = 0.0
        discount_applied = 0.0
        if status == 'Success':
            cashback_chance = 0.25 if method in ['Credit Card', 'Mobile Wallet'] else 0.12
            if random.random() < cashback_chance:
                cashback = round(amount * random.uniform(0.01, 0.10), 2)
            if category in ['Shopping', 'Food & Dining', 'Groceries'] and random.random() < 0.30:
                discount_applied = round(amount * random.uniform(0.05, 0.20), 2)

        # --- Fraud Flag ---
        is_flagged = False
        fraud_reason = None

        high_threshold = {
            'Food & Dining': 2000, 'Shopping': 12000, 'Bills & Utilities': 4000,
            'Travel': 10000, 'Entertainment': 1200, 'Health': 6000,
            'Education': 15000, 'Transfers': 40000, 'Groceries': 3000, 'Investments': 80000
        }
        if amount > high_threshold.get(category, 50000):
            if random.random() < 0.15:
                is_flagged = True
                fraud_reason = 'Unusually High Amount'

        if hour in [0, 1, 2, 3, 4] and amount > 5000:
            if random.random() < 0.20:
                is_flagged = True
                fraud_reason = 'Suspicious Late Night Transaction'

        if not is_flagged and random.random() < 0.008:
            is_flagged = True
            fraud_reason = random.choice([
                'Multiple Failed Attempts', 'Velocity Check Triggered',
                'Device Mismatch', 'Location Anomaly', 'New Device Login'
            ])

        # --- Refund ---
        is_refunded = False
        refund_amount = 0.0
        if status == 'Success' and category in ['Shopping', 'Travel', 'Food & Dining', 'Entertainment']:
            if random.random() < 0.04:
                is_refunded = True
                if random.random() < 0.6:
                    refund_amount = amount
                else:
                    refund_amount = round(amount * random.uniform(0.3, 0.8), 2)

        # --- Device Type ---
        if platform == 'Mobile App':
            device_type = random.choices(['Android', 'iOS'], weights=[0.72, 0.28], k=1)[0]
        elif platform == 'Web Browser':
            device_type = random.choices(['Windows', 'Mac', 'Linux'], weights=[0.65, 0.25, 0.10], k=1)[0]
        elif platform == 'POS Terminal':
            device_type = 'POS'
        else:
            device_type = random.choices(['Android', 'iOS'], weights=[0.72, 0.28], k=1)[0]

        records.append({
            'transaction_id': txn_id,
            'user_id': user_id,
            'transaction_datetime': txn_datetime,
            'payment_method': method,
            'category': category,
            'merchant': merchant,
            'amount': amount,
            'status': status,
            'failure_reason': reason,
            'platform': platform,
            'device_type': device_type,
            'city': city,
            'processing_time_sec': processing_time,
            'is_weekend': is_weekend,
            'cashback_earned': cashback,
            'discount_applied': discount_applied,
            'is_flagged': is_flagged,
            'fraud_reason': fraud_reason,
            'is_refunded': is_refunded,
            'refund_amount': refund_amount
        })

# ============================================================
# 6. SAVE OUTPUTS
# ============================================================
df = pd.DataFrame(records)
df = df.sort_values('transaction_datetime').reset_index(drop=True)

output_dir = os.getcwd()

# Main transactions file
txn_path = os.path.join(output_dir, 'transactions_raw.csv')
df.to_csv(txn_path, index=False)

# User profiles file
user_path = os.path.join(output_dir, 'user_profiles.csv')
user_df.to_csv(user_path, index=False)

print("=" * 60)
print("  DATASET GENERATION COMPLETE")
print("=" * 60)

print(f"\n  Files Created:")
print(f"    1. transactions_raw.csv  ({len(df)} records, {len(df.columns)} columns)")
print(f"    2. user_profiles.csv     ({len(user_df)} users, {len(user_df.columns)} columns)")

print(f"\n  Transaction Columns: {list(df.columns)}")
print(f"  User Profile Columns: {list(user_df.columns)}")

print(f"\n--- Quick Validation ---")
print(f"\nStatus Distribution:")
print(df['status'].value_counts().to_string())

print(f"\nPayment Method Distribution:")
print(df['payment_method'].value_counts().to_string())

print(f"\nCategory Distribution:")
print(df['category'].value_counts().to_string())

print(f"\nDate Range: {df['transaction_datetime'].min()} to {df['transaction_datetime'].max()}")

print(f"\nAmount Stats:")
print(df['amount'].describe().to_string())

print(f"\nMonthly Transaction Counts:")
df['month'] = pd.to_datetime(df['transaction_datetime']).dt.month
print(df['month'].value_counts().sort_index().to_string())
df.drop(columns=['month'], inplace=True)

print(f"\nFraud Flags: {df['is_flagged'].sum()} ({df['is_flagged'].mean()*100:.1f}%)")
print(f"Refunds: {df['is_refunded'].sum()} ({df['is_refunded'].mean()*100:.1f}%)")
print(f"Cashback Given: {(df['cashback_earned'] > 0).sum()} txns, Total: Rs.{df['cashback_earned'].sum():,.2f}")
print(f"Discounts Given: {(df['discount_applied'] > 0).sum()} txns, Total: Rs.{df['discount_applied'].sum():,.2f}")
print(f"\nNull failure_reason for Success: {df[df['status']=='Success']['failure_reason'].isna().sum()}")
print(f"Non-null failure_reason for Failed: {df[df['status']=='Failed']['failure_reason'].notna().sum()}")

print(f"\nAge Group Distribution (Users):")
print(user_df['age_group'].value_counts().to_string())

print(f"\nCustomer Tier Distribution (Users):")
print(user_df['customer_tier'].value_counts().to_string())

print(f"\nSpending Persona Distribution (Users):")
print(user_df['spending_persona'].value_counts().to_string())

print("\n" + "=" * 60)
print("  Ready for Phase 2: Data Cleaning & Feature Engineering!")
print("=" * 60)
