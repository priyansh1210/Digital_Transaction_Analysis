"""
Power BI Data Preparation Script
=================================
Converts transactions_cleaned.csv into a proper Star Schema:

    fact_transactions  ──┬── dim_date
                         ├── dim_users
                         ├── dim_payment_method
                         ├── dim_category
                         └── dim_platform

Output: powerbi_data/ folder (import all CSVs into Power BI Desktop)
"""

import pandas as pd
import numpy as np
import os

print("=" * 60)
print("  POWER BI DATA PREPARATION")
print("=" * 60)

# ── Load cleaned data ──────────────────────────────────────────
script_dir = os.path.dirname(os.path.abspath(__file__))
df = pd.read_csv(os.path.join(script_dir, "transactions_cleaned.csv"))
df["transaction_datetime"] = pd.to_datetime(df["transaction_datetime"])
df["date"] = pd.to_datetime(df["date"])

out_dir = os.path.join(script_dir, "powerbi_data")
os.makedirs(out_dir, exist_ok=True)

print(f"\n[1] Source: {len(df):,} rows × {df.shape[1]} columns")
print(f"    Output folder: {out_dir}\n")


# ══════════════════════════════════════════════════════════════
# DIM DATE
# ══════════════════════════════════════════════════════════════
print("[2] Building dim_date ...")

dim_date = df[["date", "year", "month", "month_name", "quarter",
               "quarter_label", "day", "day_of_week", "day_name",
               "week_number", "is_weekend", "is_month_start",
               "is_month_end", "is_festival_season"]].drop_duplicates("date").copy()

dim_date["date_key"] = dim_date["date"].dt.strftime("%Y%m%d").astype(int)
dim_date["month_year"] = dim_date["month_name"] + " " + dim_date["year"].astype(str)
dim_date = dim_date.sort_values("date").reset_index(drop=True)

# Reorder – date_key first for easy relationship creation
cols = ["date_key", "date", "year", "month", "month_name", "month_year",
        "quarter", "quarter_label", "day", "day_of_week", "day_name",
        "week_number", "is_weekend", "is_month_start", "is_month_end",
        "is_festival_season"]
dim_date = dim_date[cols]

path = os.path.join(out_dir, "dim_date.csv")
dim_date.to_csv(path, index=False)
print(f"    Saved dim_date.csv  ({len(dim_date):,} rows)")


# ══════════════════════════════════════════════════════════════
# DIM USERS
# ══════════════════════════════════════════════════════════════
print("[3] Building dim_users ...")

user_cols = ["user_id", "age_group", "gender", "account_tenure",
             "customer_tier", "spending_persona", "preferred_method",
             "user_home_city", "user_total_txns", "user_total_spend",
             "user_avg_txn_amount", "user_failure_rate_pct", "user_spending_tier"]
dim_users = df[user_cols].drop_duplicates("user_id").reset_index(drop=True)

path = os.path.join(out_dir, "dim_users.csv")
dim_users.to_csv(path, index=False)
print(f"    Saved dim_users.csv  ({len(dim_users):,} rows)")


# ══════════════════════════════════════════════════════════════
# DIM PAYMENT METHOD
# ══════════════════════════════════════════════════════════════
print("[4] Building dim_payment_method ...")

payment_type_map = {
    "UPI":           "Digital Wallet",
    "Credit Card":   "Card",
    "Debit Card":    "Card",
    "Net Banking":   "Banking",
    "Mobile Wallet": "Digital Wallet",
}
failure_rate_map = {
    "UPI": 0.06, "Credit Card": 0.04, "Debit Card": 0.08,
    "Net Banking": 0.10, "Mobile Wallet": 0.05,
}

dim_payment = pd.DataFrame({
    "payment_method":    list(payment_type_map.keys()),
    "payment_type":      list(payment_type_map.values()),
    "base_failure_rate": [failure_rate_map[m] for m in payment_type_map.keys()],
})

path = os.path.join(out_dir, "dim_payment_method.csv")
dim_payment.to_csv(path, index=False)
print(f"    Saved dim_payment_method.csv  ({len(dim_payment)} rows)")


# ══════════════════════════════════════════════════════════════
# DIM CATEGORY
# ══════════════════════════════════════════════════════════════
print("[5] Building dim_category ...")

category_group_map = {
    "Food & Dining":     "Lifestyle",
    "Shopping":          "Lifestyle",
    "Groceries":         "Lifestyle",
    "Entertainment":     "Lifestyle",
    "Travel":            "Travel & Utilities",
    "Bills & Utilities": "Travel & Utilities",
    "Health":            "Health & Education",
    "Education":         "Health & Education",
    "Transfers":         "Financial",
    "Investments":       "Financial",
}

dim_category = pd.DataFrame({
    "category":       list(category_group_map.keys()),
    "category_group": list(category_group_map.values()),
})

path = os.path.join(out_dir, "dim_category.csv")
dim_category.to_csv(path, index=False)
print(f"    Saved dim_category.csv  ({len(dim_category)} rows)")


# ══════════════════════════════════════════════════════════════
# DIM PLATFORM
# ══════════════════════════════════════════════════════════════
print("[6] Building dim_platform ...")

channel_map = {
    "Mobile App":    "Mobile",
    "QR Code":       "Mobile",
    "Web Browser":   "Web",
    "POS Terminal":  "Physical",
}

dim_platform = pd.DataFrame({
    "platform": list(channel_map.keys()),
    "channel":  list(channel_map.values()),
})

path = os.path.join(out_dir, "dim_platform.csv")
dim_platform.to_csv(path, index=False)
print(f"    Saved dim_platform.csv  ({len(dim_platform)} rows)")


# ══════════════════════════════════════════════════════════════
# FACT TRANSACTIONS  (lean – only foreign keys + measures)
# ══════════════════════════════════════════════════════════════
print("[7] Building fact_transactions ...")

fact = df.copy()

# Add date_key foreign key
fact["date_key"] = fact["date"].dt.strftime("%Y%m%d").astype(int)

# Add convenience flag columns (0/1 integers — easier in DAX)
fact["is_success"] = (fact["status"] == "Success").astype(int)
fact["is_failed"]  = (fact["status"] == "Failed").astype(int)
fact["is_pending"] = (fact["status"] == "Pending").astype(int)
fact["is_flagged_int"]  = fact["is_flagged"].astype(int)
fact["is_refunded_int"] = fact["is_refunded"].astype(int)

fact_cols = [
    # Keys
    "transaction_id", "user_id", "date_key",
    # Time (for slicer / drill-down without joining dim_date)
    "transaction_datetime", "hour", "time_bucket",
    # Dimensions (denormalized for convenience)
    "payment_method", "category", "merchant",
    "platform", "device_type", "city",
    # Amount measures
    "amount", "amount_bucket", "net_amount",
    "cashback_earned", "discount_applied", "total_savings", "savings_pct",
    # Status
    "status", "is_success", "is_failed", "is_pending",
    "failure_reason",
    # Processing
    "processing_time_sec", "processing_speed",
    # Fraud & refund
    "is_flagged", "is_flagged_int", "fraud_reason",
    "is_refunded", "is_refunded_int", "refund_amount",
]

fact = fact[fact_cols]

path = os.path.join(out_dir, "fact_transactions.csv")
fact.to_csv(path, index=False)
print(f"    Saved fact_transactions.csv  ({len(fact):,} rows × {len(fact_cols)} columns)")


# ══════════════════════════════════════════════════════════════
# SUMMARY
# ══════════════════════════════════════════════════════════════
print(f"\n{'=' * 60}")
print("  DONE — Power BI data model ready in /powerbi_data/")
print(f"{'=' * 60}")
print("""
  Tables created:
    fact_transactions.csv     — 60,000 rows  (main fact table)
    dim_date.csv              — 731 rows     (date dimension)
    dim_users.csv             — 500 rows     (user dimension)
    dim_payment_method.csv    — 5 rows       (payment lookup)
    dim_category.csv          — 10 rows      (category lookup)
    dim_platform.csv          — 4 rows       (platform lookup)

  Next steps:
    1. Open Power BI Desktop
    2. Get Data → Text/CSV → import all 6 files from /powerbi_data/
    3. Model view → create relationships:
         fact[date_key]       → dim_date[date_key]
         fact[user_id]        → dim_users[user_id]
         fact[payment_method] → dim_payment_method[payment_method]
         fact[category]       → dim_category[category]
         fact[platform]       → dim_platform[platform]
    4. Paste measures from powerbi_measures.dax
    5. Build visuals as described in POWERBI_GUIDE.md
""")
