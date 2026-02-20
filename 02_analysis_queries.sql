-- ============================================================================
-- FILE: 02_analysis_queries.sql
-- PROJECT: Digital Payment Transaction Analysis (Enhanced)
-- PURPOSE: 35+ analytical queries across 8 insight areas
-- DATASET: 5,000 transactions × 20 columns + 500 user profiles × 8 columns
-- ============================================================================

USE digital_payments_db;

-- ============================================================================
-- INSIGHT 1: TRANSACTION SUCCESS RATE ANALYSIS
-- ============================================================================

-- 1A. Overall Success Rate
SELECT 
    COUNT(*) AS total_transactions,
    SUM(CASE WHEN status = 'Success' THEN 1 ELSE 0 END) AS successful,
    SUM(CASE WHEN status = 'Failed' THEN 1 ELSE 0 END) AS failed,
    SUM(CASE WHEN status = 'Pending' THEN 1 ELSE 0 END) AS pending,
    ROUND(SUM(CASE WHEN status = 'Success' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS success_rate_pct,
    ROUND(SUM(CASE WHEN status = 'Failed' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS failure_rate_pct,
    ROUND(SUM(CASE WHEN status = 'Success' THEN amount ELSE 0 END), 2) AS total_successful_volume
FROM transactions;

-- 1B. Success Rate by Payment Method
SELECT 
    payment_method,
    COUNT(*) AS total_txn,
    SUM(CASE WHEN status = 'Success' THEN 1 ELSE 0 END) AS success_count,
    SUM(CASE WHEN status = 'Failed' THEN 1 ELSE 0 END) AS fail_count,
    ROUND(SUM(CASE WHEN status = 'Success' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS success_rate,
    ROUND(AVG(amount), 2) AS avg_txn_amount,
    ROUND(SUM(CASE WHEN status = 'Success' THEN amount ELSE 0 END), 2) AS total_successful_amount
FROM transactions
GROUP BY payment_method
ORDER BY success_rate DESC;

-- 1C. Success Rate by Month (Seasonal Trend)
SELECT 
    DATE_FORMAT(transaction_datetime, '%Y-%m') AS txn_month,
    MONTHNAME(transaction_datetime) AS month_name,
    COUNT(*) AS total_txn,
    SUM(CASE WHEN status = 'Success' THEN 1 ELSE 0 END) AS success_count,
    ROUND(SUM(CASE WHEN status = 'Success' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS success_rate,
    ROUND(SUM(amount), 2) AS total_volume
FROM transactions
GROUP BY DATE_FORMAT(transaction_datetime, '%Y-%m'), MONTHNAME(transaction_datetime)
ORDER BY txn_month;

-- 1D. Success Rate by City
SELECT 
    city,
    COUNT(*) AS total_txn,
    ROUND(SUM(CASE WHEN status = 'Success' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS success_rate,
    ROUND(AVG(amount), 2) AS avg_amount,
    ROUND(SUM(CASE WHEN status = 'Success' THEN amount ELSE 0 END), 2) AS successful_volume
FROM transactions
GROUP BY city
ORDER BY total_txn DESC;

-- 1E. Success Rate by Device Type (NEW)
SELECT 
    device_type,
    COUNT(*) AS total_txn,
    ROUND(SUM(CASE WHEN status = 'Success' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS success_rate,
    ROUND(AVG(processing_time_sec), 2) AS avg_processing_time
FROM transactions
GROUP BY device_type
ORDER BY total_txn DESC;

-- 1F. Weekend vs Weekday Success Rate (NEW)
SELECT 
    CASE WHEN is_weekend = 1 THEN 'Weekend' ELSE 'Weekday' END AS day_type,
    COUNT(*) AS total_txn,
    ROUND(SUM(CASE WHEN status = 'Success' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS success_rate,
    ROUND(AVG(amount), 2) AS avg_amount,
    ROUND(SUM(amount), 2) AS total_volume
FROM transactions
GROUP BY is_weekend;


-- ============================================================================
-- INSIGHT 2: PEAK TRANSACTION TIMES & PATTERNS
-- ============================================================================

-- 2A. Hourly Transaction Distribution
SELECT 
    HOUR(transaction_datetime) AS txn_hour,
    COUNT(*) AS total_txn,
    ROUND(SUM(amount), 2) AS total_volume,
    ROUND(AVG(amount), 2) AS avg_amount,
    ROUND(SUM(CASE WHEN status = 'Success' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS success_rate,
    ROUND(SUM(CASE WHEN status = 'Failed' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS failure_rate
FROM transactions
GROUP BY HOUR(transaction_datetime)
ORDER BY txn_hour;

-- 2B. Day of Week Analysis
SELECT 
    DAYNAME(transaction_datetime) AS day_name,
    DAYOFWEEK(transaction_datetime) AS day_num,
    COUNT(*) AS total_txn,
    ROUND(SUM(amount), 2) AS total_volume,
    ROUND(SUM(CASE WHEN status = 'Success' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS success_rate,
    COUNT(DISTINCT user_id) AS unique_users
FROM transactions
GROUP BY DAYNAME(transaction_datetime), DAYOFWEEK(transaction_datetime)
ORDER BY day_num;

-- 2C. Peak Hours by Payment Method (Heatmap Data)
SELECT 
    payment_method,
    HOUR(transaction_datetime) AS txn_hour,
    COUNT(*) AS txn_count,
    ROUND(SUM(amount), 2) AS volume
FROM transactions
WHERE status = 'Success'
GROUP BY payment_method, HOUR(transaction_datetime)
ORDER BY payment_method, txn_hour;

-- 2D. Monthly Volume Trend with Seasonal Flags
SELECT 
    DATE_FORMAT(transaction_datetime, '%Y-%m') AS txn_month,
    COUNT(*) AS txn_count,
    ROUND(SUM(amount), 2) AS total_volume,
    COUNT(DISTINCT user_id) AS unique_users,
    ROUND(AVG(amount), 2) AS avg_txn_value,
    CASE 
        WHEN MONTH(transaction_datetime) IN (10, 11) THEN 'Festival Season'
        WHEN MONTH(transaction_datetime) IN (1, 8, 12) THEN 'Sale Season'
        ELSE 'Normal'
    END AS season_type
FROM transactions
GROUP BY DATE_FORMAT(transaction_datetime, '%Y-%m'), MONTH(transaction_datetime)
ORDER BY txn_month;

-- 2E. Category Trends by Quarter (NEW)
SELECT 
    CONCAT('Q', QUARTER(transaction_datetime)) AS quarter,
    category,
    COUNT(*) AS txn_count,
    ROUND(SUM(CASE WHEN status = 'Success' THEN amount ELSE 0 END), 2) AS successful_volume
FROM transactions
GROUP BY QUARTER(transaction_datetime), category
ORDER BY quarter, txn_count DESC;


-- ============================================================================
-- INSIGHT 3: FAILED TRANSACTION DEEP DIVE
-- ============================================================================

-- 3A. Failure Reasons Breakdown
SELECT 
    failure_reason,
    COUNT(*) AS fail_count,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM transactions WHERE status = 'Failed'), 2) AS pct_of_failures,
    ROUND(AVG(amount), 2) AS avg_failed_amount,
    ROUND(AVG(processing_time_sec), 2) AS avg_processing_time
FROM transactions
WHERE status = 'Failed'
GROUP BY failure_reason
ORDER BY fail_count DESC;

-- 3B. Failure Rate by Payment Method and Reason (Cross-tab)
SELECT 
    payment_method,
    failure_reason,
    COUNT(*) AS fail_count,
    ROUND(AVG(amount), 2) AS avg_failed_amount,
    ROUND(AVG(processing_time_sec), 2) AS avg_proc_time
FROM transactions
WHERE status = 'Failed'
GROUP BY payment_method, failure_reason
ORDER BY payment_method, fail_count DESC;

-- 3C. Failure Rate by Hour (Peak Failure Windows)
SELECT 
    HOUR(transaction_datetime) AS txn_hour,
    COUNT(*) AS total_txn,
    SUM(CASE WHEN status = 'Failed' THEN 1 ELSE 0 END) AS failed_txn,
    ROUND(SUM(CASE WHEN status = 'Failed' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS failure_rate
FROM transactions
GROUP BY HOUR(transaction_datetime)
ORDER BY failure_rate DESC
LIMIT 10;

-- 3D. Revenue Impact of Failures
SELECT 
    payment_method,
    COUNT(*) AS failed_txn_count,
    ROUND(SUM(amount), 2) AS lost_revenue,
    ROUND(AVG(amount), 2) AS avg_failed_txn_value,
    ROUND(SUM(amount) * 100.0 / (SELECT SUM(amount) FROM transactions WHERE status = 'Failed'), 2) AS pct_of_total_lost
FROM transactions
WHERE status = 'Failed'
GROUP BY payment_method
ORDER BY lost_revenue DESC;

-- 3E. Failure Rate by Category
SELECT 
    category,
    COUNT(*) AS total_txn,
    SUM(CASE WHEN status = 'Failed' THEN 1 ELSE 0 END) AS failed_count,
    ROUND(SUM(CASE WHEN status = 'Failed' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS failure_rate,
    ROUND(SUM(CASE WHEN status = 'Failed' THEN amount ELSE 0 END), 2) AS lost_amount
FROM transactions
GROUP BY category
ORDER BY failure_rate DESC;

-- 3F. Failure Rate by Platform & Device (NEW)
SELECT 
    platform,
    device_type,
    COUNT(*) AS total_txn,
    SUM(CASE WHEN status = 'Failed' THEN 1 ELSE 0 END) AS failed_count,
    ROUND(SUM(CASE WHEN status = 'Failed' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS failure_rate
FROM transactions
GROUP BY platform, device_type
ORDER BY failure_rate DESC;


-- ============================================================================
-- INSIGHT 4: USER BEHAVIOR & SEGMENTATION
-- ============================================================================

-- 4A. User Segmentation by Transaction Frequency
SELECT 
    CASE 
        WHEN txn_count >= 20 THEN 'Power User (20+)'
        WHEN txn_count >= 10 THEN 'Regular User (10-19)'
        WHEN txn_count >= 5  THEN 'Occasional User (5-9)'
        ELSE 'Rare User (1-4)'
    END AS user_segment,
    COUNT(*) AS user_count,
    ROUND(AVG(txn_count), 1) AS avg_txn_per_user,
    ROUND(AVG(total_spent), 2) AS avg_spend,
    ROUND(AVG(failure_rate), 2) AS avg_failure_rate
FROM (
    SELECT 
        user_id,
        COUNT(*) AS txn_count,
        SUM(CASE WHEN status = 'Success' THEN amount ELSE 0 END) AS total_spent,
        SUM(CASE WHEN status = 'Failed' THEN 1 ELSE 0 END) * 100.0 / COUNT(*) AS failure_rate
    FROM transactions
    GROUP BY user_id
) AS user_stats
GROUP BY 
    CASE 
        WHEN txn_count >= 20 THEN 'Power User (20+)'
        WHEN txn_count >= 10 THEN 'Regular User (10-19)'
        WHEN txn_count >= 5  THEN 'Occasional User (5-9)'
        ELSE 'Rare User (1-4)'
    END
ORDER BY avg_txn_per_user DESC;

-- 4B. Top 20 Users by Spend
SELECT 
    t.user_id,
    u.age_group,
    u.customer_tier,
    u.spending_persona,
    COUNT(*) AS total_txn,
    ROUND(SUM(CASE WHEN t.status = 'Success' THEN t.amount ELSE 0 END), 2) AS total_spent,
    ROUND(AVG(t.amount), 2) AS avg_txn_value,
    COUNT(DISTINCT t.payment_method) AS methods_used,
    COUNT(DISTINCT t.category) AS categories_used,
    ROUND(SUM(t.cashback_earned), 2) AS total_cashback
FROM transactions t
JOIN user_profiles u ON t.user_id = u.user_id
GROUP BY t.user_id, u.age_group, u.customer_tier, u.spending_persona
ORDER BY total_spent DESC
LIMIT 20;

-- 4C. User Demographics × Payment Method Preference (NEW)
SELECT 
    u.age_group,
    t.payment_method,
    COUNT(*) AS txn_count,
    COUNT(DISTINCT t.user_id) AS unique_users,
    ROUND(AVG(t.amount), 2) AS avg_amount
FROM transactions t
JOIN user_profiles u ON t.user_id = u.user_id
GROUP BY u.age_group, t.payment_method
ORDER BY u.age_group, txn_count DESC;

-- 4D. Monthly Active Users (Retention Proxy)
SELECT 
    DATE_FORMAT(transaction_datetime, '%Y-%m') AS txn_month,
    COUNT(DISTINCT user_id) AS monthly_active_users,
    COUNT(*) AS total_txn,
    ROUND(COUNT(*) * 1.0 / COUNT(DISTINCT user_id), 1) AS txn_per_active_user,
    ROUND(SUM(CASE WHEN status = 'Success' THEN amount ELSE 0 END) / COUNT(DISTINCT user_id), 2) AS revenue_per_active_user
FROM transactions
GROUP BY DATE_FORMAT(transaction_datetime, '%Y-%m')
ORDER BY txn_month;

-- 4E. Customer Tier Performance (NEW)
SELECT 
    u.customer_tier,
    COUNT(*) AS total_txn,
    COUNT(DISTINCT t.user_id) AS unique_users,
    ROUND(AVG(t.amount), 2) AS avg_txn_value,
    ROUND(SUM(CASE WHEN t.status = 'Success' THEN t.amount ELSE 0 END), 2) AS total_revenue,
    ROUND(SUM(CASE WHEN t.status = 'Failed' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS failure_rate,
    ROUND(SUM(t.cashback_earned), 2) AS total_cashback_given
FROM transactions t
JOIN user_profiles u ON t.user_id = u.user_id
GROUP BY u.customer_tier
ORDER BY total_revenue DESC;

-- 4F. Spending Persona Analysis (NEW)
SELECT 
    u.spending_persona,
    COUNT(DISTINCT t.user_id) AS users,
    COUNT(*) AS total_txn,
    ROUND(AVG(t.amount), 2) AS avg_txn_amount,
    ROUND(SUM(CASE WHEN t.status = 'Success' THEN t.amount ELSE 0 END), 2) AS total_spent,
    ROUND(SUM(CASE WHEN t.status = 'Success' THEN t.amount ELSE 0 END) / COUNT(DISTINCT t.user_id), 2) AS spend_per_user
FROM transactions t
JOIN user_profiles u ON t.user_id = u.user_id
GROUP BY u.spending_persona
ORDER BY spend_per_user DESC;


-- ============================================================================
-- INSIGHT 5: CASHBACK & DISCOUNT EFFECTIVENESS (NEW)
-- ============================================================================

-- 5A. Cashback Summary by Payment Method
SELECT 
    payment_method,
    COUNT(*) AS total_txn,
    SUM(CASE WHEN cashback_earned > 0 THEN 1 ELSE 0 END) AS txn_with_cashback,
    ROUND(SUM(CASE WHEN cashback_earned > 0 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS cashback_rate_pct,
    ROUND(SUM(cashback_earned), 2) AS total_cashback,
    ROUND(AVG(CASE WHEN cashback_earned > 0 THEN cashback_earned END), 2) AS avg_cashback_per_txn
FROM transactions
WHERE status = 'Success'
GROUP BY payment_method
ORDER BY total_cashback DESC;

-- 5B. Discount Analysis by Category
SELECT 
    category,
    COUNT(*) AS total_txn,
    SUM(CASE WHEN discount_applied > 0 THEN 1 ELSE 0 END) AS txn_with_discount,
    ROUND(SUM(discount_applied), 2) AS total_discount_value,
    ROUND(AVG(CASE WHEN discount_applied > 0 THEN discount_applied * 100.0 / amount END), 2) AS avg_discount_pct
FROM transactions
WHERE status = 'Success'
GROUP BY category
ORDER BY total_discount_value DESC;

-- 5C. Total Savings Impact — Do promotions drive higher spend?
SELECT 
    CASE 
        WHEN (cashback_earned + discount_applied) = 0 THEN 'No Promotion'
        WHEN (cashback_earned + discount_applied) < 200 THEN 'Low Savings (<₹200)'
        WHEN (cashback_earned + discount_applied) < 500 THEN 'Medium Savings (₹200-500)'
        ELSE 'High Savings (₹500+)'
    END AS savings_tier,
    COUNT(*) AS txn_count,
    ROUND(AVG(amount), 2) AS avg_txn_amount,
    ROUND(SUM(amount), 2) AS total_volume
FROM transactions
WHERE status = 'Success'
GROUP BY 
    CASE 
        WHEN (cashback_earned + discount_applied) = 0 THEN 'No Promotion'
        WHEN (cashback_earned + discount_applied) < 200 THEN 'Low Savings (<₹200)'
        WHEN (cashback_earned + discount_applied) < 500 THEN 'Medium Savings (₹200-500)'
        ELSE 'High Savings (₹500+)'
    END
ORDER BY avg_txn_amount DESC;


-- ============================================================================
-- INSIGHT 6: FRAUD DETECTION ANALYSIS (NEW)
-- ============================================================================

-- 6A. Fraud Flag Overview
SELECT 
    is_flagged,
    COUNT(*) AS txn_count,
    ROUND(AVG(amount), 2) AS avg_amount,
    ROUND(SUM(amount), 2) AS total_amount,
    ROUND(SUM(CASE WHEN status = 'Failed' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS failure_rate
FROM transactions
GROUP BY is_flagged;

-- 6B. Fraud Reasons Breakdown
SELECT 
    fraud_reason,
    COUNT(*) AS flag_count,
    ROUND(AVG(amount), 2) AS avg_flagged_amount,
    ROUND(AVG(processing_time_sec), 2) AS avg_processing_time,
    GROUP_CONCAT(DISTINCT payment_method ORDER BY payment_method) AS methods_involved
FROM transactions
WHERE is_flagged = TRUE
GROUP BY fraud_reason
ORDER BY flag_count DESC;

-- 6C. Fraud Flags by Time of Day
SELECT 
    CASE 
        WHEN HOUR(transaction_datetime) BETWEEN 0 AND 4 THEN 'Late Night (12-5 AM)'
        WHEN HOUR(transaction_datetime) BETWEEN 5 AND 11 THEN 'Morning (5 AM-12 PM)'
        WHEN HOUR(transaction_datetime) BETWEEN 12 AND 16 THEN 'Afternoon (12-5 PM)'
        WHEN HOUR(transaction_datetime) BETWEEN 17 AND 21 THEN 'Evening (5-10 PM)'
        ELSE 'Night (10 PM-12 AM)'
    END AS time_slot,
    COUNT(*) AS flagged_count,
    ROUND(AVG(amount), 2) AS avg_flagged_amount
FROM transactions
WHERE is_flagged = TRUE
GROUP BY 
    CASE 
        WHEN HOUR(transaction_datetime) BETWEEN 0 AND 4 THEN 'Late Night (12-5 AM)'
        WHEN HOUR(transaction_datetime) BETWEEN 5 AND 11 THEN 'Morning (5 AM-12 PM)'
        WHEN HOUR(transaction_datetime) BETWEEN 12 AND 16 THEN 'Afternoon (12-5 PM)'
        WHEN HOUR(transaction_datetime) BETWEEN 17 AND 21 THEN 'Evening (5-10 PM)'
        ELSE 'Night (10 PM-12 AM)'
    END
ORDER BY flagged_count DESC;

-- 6D. Flagged Transactions by Customer Tier (NEW)
SELECT 
    u.customer_tier,
    COUNT(*) AS total_txn,
    SUM(CASE WHEN t.is_flagged = TRUE THEN 1 ELSE 0 END) AS flagged_count,
    ROUND(SUM(CASE WHEN t.is_flagged = TRUE THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS flag_rate_pct
FROM transactions t
JOIN user_profiles u ON t.user_id = u.user_id
GROUP BY u.customer_tier
ORDER BY flag_rate_pct DESC;


-- ============================================================================
-- INSIGHT 7: REFUND ANALYSIS (NEW)
-- ============================================================================

-- 7A. Refund Summary
SELECT 
    COUNT(*) AS total_refunds,
    SUM(CASE WHEN refund_amount = amount THEN 1 ELSE 0 END) AS full_refunds,
    SUM(CASE WHEN refund_amount < amount AND refund_amount > 0 THEN 1 ELSE 0 END) AS partial_refunds,
    ROUND(SUM(refund_amount), 2) AS total_refund_value,
    ROUND(AVG(refund_amount), 2) AS avg_refund_amount,
    ROUND(SUM(refund_amount) * 100.0 / (SELECT SUM(amount) FROM transactions WHERE status = 'Success'), 2) AS refund_as_pct_of_revenue
FROM transactions
WHERE is_refunded = TRUE;

-- 7B. Refunds by Category
SELECT 
    category,
    COUNT(*) AS refund_count,
    ROUND(SUM(refund_amount), 2) AS total_refunded,
    ROUND(AVG(refund_amount), 2) AS avg_refund,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM transactions WHERE is_refunded = TRUE), 2) AS pct_of_all_refunds
FROM transactions
WHERE is_refunded = TRUE
GROUP BY category
ORDER BY refund_count DESC;

-- 7C. Refund Rate by Payment Method
SELECT 
    payment_method,
    COUNT(*) AS total_successful,
    SUM(CASE WHEN is_refunded = TRUE THEN 1 ELSE 0 END) AS refunded,
    ROUND(SUM(CASE WHEN is_refunded = TRUE THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS refund_rate_pct,
    ROUND(SUM(CASE WHEN is_refunded = TRUE THEN refund_amount ELSE 0 END), 2) AS total_refund_value
FROM transactions
WHERE status = 'Success'
GROUP BY payment_method
ORDER BY refund_rate_pct DESC;


-- ============================================================================
-- INSIGHT 8: PLATFORM & DEVICE ANALYSIS (NEW)
-- ============================================================================

-- 8A. Platform Performance
SELECT 
    platform,
    COUNT(*) AS total_txn,
    COUNT(DISTINCT user_id) AS unique_users,
    ROUND(SUM(CASE WHEN status = 'Success' THEN amount ELSE 0 END), 2) AS successful_volume,
    ROUND(SUM(CASE WHEN status = 'Success' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS success_rate,
    ROUND(AVG(processing_time_sec), 2) AS avg_processing_time,
    ROUND(SUM(cashback_earned), 2) AS total_cashback
FROM transactions
GROUP BY platform
ORDER BY total_txn DESC;

-- 8B. Device Type Breakdown
SELECT 
    device_type,
    platform,
    COUNT(*) AS total_txn,
    ROUND(AVG(amount), 2) AS avg_amount,
    ROUND(SUM(CASE WHEN status = 'Success' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS success_rate,
    ROUND(AVG(processing_time_sec), 2) AS avg_proc_time
FROM transactions
GROUP BY device_type, platform
ORDER BY total_txn DESC;

-- 8C. Mobile OS Comparison: Android vs iOS (NEW)
SELECT 
    device_type AS mobile_os,
    COUNT(*) AS total_txn,
    ROUND(AVG(amount), 2) AS avg_txn_amount,
    ROUND(SUM(CASE WHEN status = 'Success' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS success_rate,
    ROUND(SUM(CASE WHEN status = 'Success' THEN amount ELSE 0 END), 2) AS total_volume,
    ROUND(SUM(cashback_earned), 2) AS total_cashback,
    ROUND(SUM(CASE WHEN is_flagged = TRUE THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS fraud_flag_rate
FROM transactions
WHERE device_type IN ('Android', 'iOS')
GROUP BY device_type;


-- ============================================================================
-- BONUS: EXECUTIVE SUMMARY VIEW (Updated)
-- ============================================================================

CREATE OR REPLACE VIEW v_executive_summary AS
SELECT 
    DATE_FORMAT(transaction_datetime, '%Y-%m') AS month,
    payment_method,
    category,
    platform,
    device_type,
    city,
    status,
    is_weekend,
    COUNT(*) AS txn_count,
    ROUND(SUM(amount), 2) AS total_amount,
    ROUND(AVG(amount), 2) AS avg_amount,
    ROUND(AVG(processing_time_sec), 2) AS avg_processing_time,
    ROUND(SUM(cashback_earned), 2) AS total_cashback,
    ROUND(SUM(discount_applied), 2) AS total_discount,
    SUM(CASE WHEN is_flagged = TRUE THEN 1 ELSE 0 END) AS flagged_count,
    SUM(CASE WHEN is_refunded = TRUE THEN 1 ELSE 0 END) AS refund_count,
    ROUND(SUM(refund_amount), 2) AS total_refund_amount,
    COUNT(DISTINCT user_id) AS unique_users
FROM transactions
GROUP BY 
    DATE_FORMAT(transaction_datetime, '%Y-%m'),
    payment_method, category, platform, device_type,
    city, status, is_weekend;


-- ============================================================================
-- BONUS: KPI SNAPSHOT VIEW (NEW)
-- ============================================================================

CREATE OR REPLACE VIEW v_kpi_snapshot AS
SELECT 
    (SELECT COUNT(*) FROM transactions) AS total_transactions,
    (SELECT ROUND(SUM(CASE WHEN status = 'Success' THEN amount ELSE 0 END), 2) FROM transactions) AS total_revenue,
    (SELECT ROUND(SUM(CASE WHEN status = 'Success' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) FROM transactions) AS success_rate,
    (SELECT ROUND(AVG(amount), 2) FROM transactions WHERE status = 'Success') AS avg_successful_txn,
    (SELECT COUNT(DISTINCT user_id) FROM transactions) AS total_active_users,
    (SELECT ROUND(SUM(cashback_earned + discount_applied), 2) FROM transactions) AS total_promotions_cost,
    (SELECT COUNT(*) FROM transactions WHERE is_flagged = TRUE) AS fraud_flags,
    (SELECT ROUND(SUM(refund_amount), 2) FROM transactions WHERE is_refunded = TRUE) AS total_refunds,
    (SELECT ROUND(AVG(processing_time_sec), 2) FROM transactions WHERE status = 'Success') AS avg_success_processing_time;
