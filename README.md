# 💳 Digital Payment Transaction Analysis

## Project Overview

An end-to-end data analytics project analyzing **5,000 synthetic digital payment transactions** across India's payment ecosystem — UPI, Credit Card, Debit Card, Net Banking, and Mobile Wallet. The project covers the full analytics lifecycle: data generation, cleaning, SQL analysis, EDA, Excel reporting, and an interactive Streamlit dashboard.

**What makes this project stand out:**
- **Self-designed dataset** with realistic Indian fintech patterns (seasonal spikes, user personas, fraud flags)
- **500 user profiles** with demographics, spending personas, and behavioral stickiness
- **52 engineered features** from 20 raw columns
- **8 analytical dimensions**: success rates, peak times, failures, user behavior, fraud, refunds, promotions, platform/device
- **Fully interactive Streamlit dashboard** with 6 tabs and real-time filtering

### Tools & Technologies

| Layer | Tools |
|-------|-------|
| **Data Generation** | Python (NumPy, Pandas, Random) |
| **Data Pipeline** | Python (Pandas, NumPy) — cleaning, feature engineering |
| **Database** | SQL (MySQL) — schema design, 35+ analytical queries |
| **EDA & Visualization** | Python (Matplotlib, Seaborn) — 17 publication-quality charts |
| **Excel Reporting** | Python (openpyxl) — 6-sheet workbook with charts |
| **Interactive Dashboard** | Python (Streamlit, Plotly) — 6-tab dark-themed dashboard |
| **Static Dashboard** | HTML/CSS/JS (Chart.js) — Power BI-style prototype |

---

## Key Insights

| # | Insight Area | Key Finding |
|---|-------------|-------------|
| 1 | **Success Rate** | 89.8% overall; Credit Card highest (92.3%), Net Banking lowest (88.7%) |
| 2 | **Peak Times** | Busiest: 12–1 PM and 6–8 PM; Quietest: 1–5 AM |
| 3 | **Failures** | ₹31.9L lost revenue; Bank Server Down is #1 reason; Net Banking most failure-prone |
| 4 | **Users** | 25–34 age group drives 32.3% of transactions; High Spenders avg ₹13,749/txn |
| 5 | **Fraud** | 4.6% flagged; "Unusually High Amount" is top reason; late-night txns most flagged |
| 6 | **Refunds** | 2.1% refund rate; ₹356.8K total; Food & Dining most refunded category |
| 7 | **Promotions** | ₹6.5L total savings; Credit Card & Wallet users get most cashback |
| 8 | **Platform** | Mobile App dominates (45.3%); Android:iOS = 2.6:1 |

---

## Directory Structure

```
project/
│
├── data/
│   ├── generate_data_enhanced.py      # Synthetic data generator (5,000 txns + 500 users)
│   ├── transactions_raw.csv           # Raw dataset (5,000 rows × 20 columns)
│   ├── user_profiles.csv              # User demographics (500 rows × 8 columns)
│   └── data_pipeline.py               # Cleaning & feature engineering pipeline
│
├── analysis/
│   ├── transactions_cleaned.csv       # Analysis-ready dataset (5,000 rows × 52 columns)
│   ├── eda_analysis.py                # EDA script — generates 17 charts
│   ├── eda_summary.txt                # Key findings summary
│   └── charts/                        # 17 PNG charts (150 DPI)
│
├── sql/
│   ├── 01_create_schema.sql           # Database + tables + indexes + FK
│   ├── 02_analysis_queries.sql        # 35+ analytical queries (8 insight areas)
│   └── 03_data_cleaning.sql           # Validation, cleaning, derived columns
│
├── excel/
│   ├── create_workbook.py             # Script to generate Excel workbook
│   └── Payment_Transaction_Analysis.xlsx
│
├── dashboard/
│   ├── app.py                         # Streamlit dashboard (6 tabs, dark theme)
│   ├── requirements.txt               # Python dependencies
│   └── Dashboard.html                 # Static HTML dashboard (Power BI-style)
│
└── README.md
```

---

## Dataset Schema

### `transactions_raw.csv` — 5,000 rows × 20 columns

| Column | Type | Description |
|--------|------|-------------|
| transaction_id | VARCHAR | Unique ID (TXN0000001 – TXN0005000) |
| user_id | VARCHAR | 500 unique users (USR00001 – USR00500) |
| transaction_datetime | DATETIME | Jan 1 – Dec 31, 2024 (peak-hour biased) |
| payment_method | VARCHAR | UPI, Credit Card, Debit Card, Net Banking, Mobile Wallet |
| category | VARCHAR | 10 categories: Food, Shopping, Bills, Travel, Entertainment, Health, Education, Transfers, Groceries, Investments |
| merchant | VARCHAR | 70+ real merchant names (Swiggy, Amazon, Netflix, Zerodha, etc.) |
| amount | DECIMAL | ₹50 – ₹176,364 (persona-influenced) |
| status | VARCHAR | Success (89.8%), Failed (7.7%), Pending (2.6%) |
| failure_reason | VARCHAR | Method-specific reasons (only for Failed) |
| platform | VARCHAR | Mobile App, Web Browser, POS Terminal, QR Code |
| device_type | VARCHAR | Android, iOS, Windows, Mac, Linux, POS |
| city | VARCHAR | 15 Indian cities (weighted distribution) |
| processing_time_sec | DECIMAL | 0.5s–30s (status-dependent) |
| is_weekend | INT | Weekend flag (0/1) |
| cashback_earned | DECIMAL | ₹0–₹amount × 10% (method-dependent) |
| discount_applied | DECIMAL | ₹0–₹amount × 20% (category-dependent) |
| is_flagged | BOOLEAN | Fraud flag (4.6% of transactions) |
| fraud_reason | VARCHAR | 7 fraud reasons (high amount, late night, velocity, etc.) |
| is_refunded | BOOLEAN | Refund flag (2.1% of successful transactions) |
| refund_amount | DECIMAL | Full or partial refund amount |

### `user_profiles.csv` — 500 rows × 8 columns

| Column | Values |
|--------|--------|
| user_id | USR00001 – USR00500 |
| city | 15 Indian cities |
| age_group | 18-24, 25-34, 35-44, 45-54, 55+ |
| gender | Male, Female, Other |
| account_tenure | 0-6 months to 5+ years |
| customer_tier | New, Regular, Premium, VIP |
| spending_persona | Budget, Moderate, High Spender, Impulse |
| preferred_method | User's preferred payment method (adds behavioral stickiness) |

### `transactions_cleaned.csv` — 5,000 rows × 52 columns

All raw columns plus 32 derived features including: time buckets, amount buckets, quarter labels, festival season flags, net amount, total savings, savings %, processing speed categories, user-level aggregates (total spend, avg transaction, failure rate), and merged demographics.

---

## Realistic Data Design Choices

The synthetic data was carefully designed with these real-world patterns:

| Pattern | Implementation |
|---------|---------------|
| **UPI dominance** | 40% market share (mirrors India's actual UPI adoption) |
| **Peak hours** | Lunch (12–1 PM) and evening (6–8 PM) spikes |
| **Festival season** | Oct–Nov transaction spike (Diwali, Big Billion Days) |
| **User stickiness** | Each user has a preferred payment method (2.5× weight) |
| **Spending personas** | Budget users spend 60% of base; High Spenders spend 180% |
| **Method-specific failures** | Net Banking: OTP/session issues; UPI: server timeouts |
| **Peak-hour failures** | 1.4× higher failure rate during rush hours |
| **Platform-device mapping** | Mobile App → Android/iOS; Web → Windows/Mac/Linux |
| **Cashback targeting** | Credit Card & Wallet users get 25% cashback chance vs 12% for others |
| **Fraud detection logic** | High amounts, late-night transactions, velocity checks |

---

## How to Run

### Step 1: Generate Data
```bash
python data/generate_data_enhanced.py
```
Creates `transactions_raw.csv` (5,000 transactions) and `user_profiles.csv` (500 users).

### Step 2: Run Data Pipeline
```bash
python data/data_pipeline.py
```
Creates `transactions_cleaned.csv` with 52 engineered features.

### Step 3: Run EDA
```bash
python analysis/eda_analysis.py
```
Generates 17 charts in the `charts/` folder and `eda_summary.txt`.

### Step 4: Run SQL Scripts
```
1. Open MySQL client
2. Run 01_create_schema.sql (creates database + tables)
3. Load CSVs using LOAD DATA commands in the script
4. Run 02_analysis_queries.sql for all insights
5. Run 03_data_cleaning.sql for validation & derived columns
```

### Step 5: Launch Streamlit Dashboard
```bash
pip install -r dashboard/requirements.txt
streamlit run dashboard/app.py
```

### Step 6: View Static Dashboard
Open `dashboard/Dashboard.html` in any browser — no server needed.

---

## Streamlit Dashboard Features

The interactive dashboard (`app.py`) includes:

| Tab | Contents |
|-----|----------|
| **📊 Overview** | 8 KPI cards, monthly trend with festival highlights, payment method donut, category revenue, city distribution |
| **💰 Transactions** | Hourly heatmap (day × hour), time-of-day analysis, weekend vs weekday, payment method success rates |
| **❌ Failures** | Failure KPIs, top reasons, lost revenue by method, hourly failure rate, method × reason heatmap |
| **👥 Users** | Age group analysis, customer tier breakdown, spending personas, gender split, monthly active users |
| **🛡️ Fraud & Refunds** | Fraud flag reasons, flagged vs normal amounts, refund breakdown by category and method |
| **📱 Platform & Device** | Platform pie chart, device distribution, Android vs iOS comparison, cashback & discount analysis |

**Sidebar filters:** Date range, payment method, status, city, category — all charts update in real-time.

---

## SQL Highlights

The SQL layer includes **35+ queries** across 8 insight areas:

1. **Transaction Success Rate** — overall, by method, by month, by city, by device, weekend vs weekday
2. **Peak Transaction Times** — hourly distribution, day-of-week, method × hour heatmap, seasonal trends
3. **Failed Transactions** — failure reasons, method × reason cross-tab, hourly failure windows, revenue impact
4. **User Segmentation** — frequency-based segments, top spenders, demographics × payment preference, MAU, customer tier
5. **Cashback & Discounts** — by method, by category, savings tier impact on spend
6. **Fraud Detection** — flag overview, reasons, time-of-day patterns, tier-based flag rates
7. **Refund Analysis** — full vs partial, by category, by method, refund-to-revenue ratio
8. **Platform & Device** — platform performance, device breakdown, Android vs iOS comparison

Plus: executive summary view and KPI snapshot view for BI tools.

---

## Data Summary

| Metric | Value |
|--------|-------|
| Total Transactions | 5,000 |
| Total Users | 500 |
| Date Range | Jan 1 – Dec 31, 2024 |
| Success Rate | 89.8% |
| Total Successful Volume | ₹3.38 Crore |
| Failure Rate | 7.7% |
| Lost Revenue (Failures) | ₹31.9 Lakhs |
| Top Payment Method | UPI (44.3%) |
| Top Category | Food & Dining (21.4%) |
| Fraud Flag Rate | 4.6% |
| Refund Rate | 2.1% |
| Total Savings (Cashback + Discount) | ₹6.5 Lakhs |
| Top City | Mumbai (16%) |
| Peak Hour | 12:00 PM |
