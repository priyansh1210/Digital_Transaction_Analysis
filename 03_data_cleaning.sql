-- ============================================================================
-- FILE: 03_data_cleaning.sql
-- PROJECT: Digital Payment Transaction Analysis (Enhanced)
-- PURPOSE: Data validation, cleaning, and derived column creation
-- DATASET: 5,000 transactions × 20 columns + 500 user profiles × 8 columns
-- ============================================================================

USE digital_payments_db;

-- ============================================================================
-- STEP 1: DATA QUALITY CHECKS
-- ============================================================================

-- 1.1 Check for duplicate transaction IDs
SELECT transaction_id, COUNT(*) AS cnt
FROM transactions
GROUP BY transaction_id
HAVING COUNT(*) > 1;

-- 1.2 Check for invalid statuses
SELECT DISTINCT status FROM transactions;

-- 1.3 Check for negative or zero amounts
SELECT COUNT(*) AS invalid_amounts FROM transactions WHERE amount <= 0;

-- 1.4 Check for future-dated transactions
SELECT COUNT(*) AS future_txn FROM transactions WHERE transaction_datetime > NOW();

-- 1.5 Check for failed transactions without a failure reason
SELECT COUNT(*) AS missing_reasons
FROM transactions
WHERE status = 'Failed' AND (failure_reason IS NULL OR failure_reason = '');

-- 1.6 Check for successful transactions that incorrectly have a failure reason
SELECT COUNT(*) AS incorrect_reasons
FROM transactions
WHERE status = 'Success' AND failure_reason IS NOT NULL AND failure_reason != '';

-- 1.7 Check for negative cashback or discount (NEW)
SELECT COUNT(*) AS negative_cashback FROM transactions WHERE cashback_earned < 0;
SELECT COUNT(*) AS negative_discount FROM transactions WHERE discount_applied < 0;

-- 1.8 Check refund consistency (NEW)
-- Refunded transactions should have status = 'Success'
SELECT COUNT(*) AS invalid_refunds
FROM transactions
WHERE is_refunded = TRUE AND status != 'Success';

-- Refund amount should not exceed transaction amount
SELECT COUNT(*) AS over_refunds
FROM transactions
WHERE is_refunded = TRUE AND refund_amount > amount;

-- 1.9 Fraud flag consistency (NEW)
-- Non-flagged transactions should not have a fraud reason
SELECT COUNT(*) AS invalid_fraud_reasons
FROM transactions
WHERE is_flagged = FALSE AND fraud_reason IS NOT NULL AND fraud_reason != '';

-- 1.10 FK integrity: all transaction user_ids exist in user_profiles
SELECT COUNT(*) AS orphan_users
FROM transactions t
LEFT JOIN user_profiles u ON t.user_id = u.user_id
WHERE u.user_id IS NULL;

-- 1.11 Device type validation (NEW)
SELECT DISTINCT device_type, platform FROM transactions ORDER BY platform, device_type;

-- 1.12 Check is_weekend correctness (NEW)
SELECT 
    is_weekend,
    DAYNAME(transaction_datetime) AS day_name,
    COUNT(*) AS cnt
FROM transactions
GROUP BY is_weekend, DAYNAME(transaction_datetime)
ORDER BY is_weekend, day_name;


-- ============================================================================
-- STEP 2: DATA CLEANING (Fixes if issues found)
-- ============================================================================

-- 2.1 Fix null failure reasons for failed transactions
UPDATE transactions
SET failure_reason = 'Unknown'
WHERE status = 'Failed' AND (failure_reason IS NULL OR failure_reason = '');

-- 2.2 Clear failure reasons for successful transactions
UPDATE transactions
SET failure_reason = NULL
WHERE status = 'Success' AND failure_reason IS NOT NULL AND failure_reason != '';

-- 2.3 Clear fraud_reason for non-flagged transactions
UPDATE transactions
SET fraud_reason = NULL
WHERE is_flagged = FALSE AND fraud_reason IS NOT NULL;

-- 2.4 Fix refund inconsistencies
UPDATE transactions
SET is_refunded = FALSE, refund_amount = 0
WHERE status != 'Success' AND is_refunded = TRUE;

-- 2.5 Cap refund_amount to not exceed transaction amount
UPDATE transactions
SET refund_amount = amount
WHERE is_refunded = TRUE AND refund_amount > amount;

-- 2.6 Standardize text fields (trim whitespace)
UPDATE transactions SET payment_method = TRIM(payment_method);
UPDATE transactions SET category = TRIM(category);
UPDATE transactions SET merchant = TRIM(merchant);
UPDATE transactions SET city = TRIM(city);
UPDATE transactions SET platform = TRIM(platform);
UPDATE transactions SET device_type = TRIM(device_type);
UPDATE transactions SET failure_reason = TRIM(failure_reason);
UPDATE transactions SET fraud_reason = TRIM(fraud_reason);

-- 2.7 Standardize user_profiles text
UPDATE user_profiles SET city = TRIM(city);
UPDATE user_profiles SET age_group = TRIM(age_group);
UPDATE user_profiles SET gender = TRIM(gender);


-- ============================================================================
-- STEP 3: DERIVED COLUMNS (Computed/Generated)
-- ============================================================================

-- 3.1 Time-based dimension columns
ALTER TABLE transactions
ADD COLUMN txn_date DATE GENERATED ALWAYS AS (DATE(transaction_datetime)) STORED,
ADD COLUMN txn_hour INT GENERATED ALWAYS AS (HOUR(transaction_datetime)) STORED,
ADD COLUMN txn_day_of_week VARCHAR(10) GENERATED ALWAYS AS (DAYNAME(transaction_datetime)) STORED,
ADD COLUMN txn_month VARCHAR(7) GENERATED ALWAYS AS (DATE_FORMAT(transaction_datetime, '%Y-%m')) STORED,
ADD COLUMN txn_quarter INT GENERATED ALWAYS AS (QUARTER(transaction_datetime)) STORED;

-- 3.2 Amount bucket classification
ALTER TABLE transactions
ADD COLUMN amount_bucket VARCHAR(25) GENERATED ALWAYS AS (
    CASE 
        WHEN amount < 100 THEN 'Micro (<₹100)'
        WHEN amount < 500 THEN 'Small (₹100-500)'
        WHEN amount < 2000 THEN 'Medium (₹500-2K)'
        WHEN amount < 10000 THEN 'Large (₹2K-10K)'
        WHEN amount < 50000 THEN 'High (₹10K-50K)'
        ELSE 'Premium (₹50K+)'
    END
) STORED;

-- 3.3 Time-of-day classification
ALTER TABLE transactions
ADD COLUMN time_slot VARCHAR(15) GENERATED ALWAYS AS (
    CASE 
        WHEN HOUR(transaction_datetime) BETWEEN 5 AND 11 THEN 'Morning'
        WHEN HOUR(transaction_datetime) BETWEEN 12 AND 16 THEN 'Afternoon'
        WHEN HOUR(transaction_datetime) BETWEEN 17 AND 21 THEN 'Evening'
        ELSE 'Night'
    END
) STORED;

-- 3.4 Net amount after promotions (NEW)
ALTER TABLE transactions
ADD COLUMN net_amount DECIMAL(12,2) GENERATED ALWAYS AS (
    GREATEST(amount - discount_applied - cashback_earned, 0)
) STORED;

-- 3.5 Total savings per transaction (NEW)
ALTER TABLE transactions
ADD COLUMN total_savings DECIMAL(10,2) GENERATED ALWAYS AS (
    cashback_earned + discount_applied
) STORED;

-- 3.6 Festival season flag (NEW)
ALTER TABLE transactions
ADD COLUMN is_festival_season TINYINT(1) GENERATED ALWAYS AS (
    CASE WHEN MONTH(transaction_datetime) IN (10, 11) THEN 1 ELSE 0 END
) STORED;

-- 3.7 Processing speed category (NEW)
ALTER TABLE transactions
ADD COLUMN processing_speed VARCHAR(15) GENERATED ALWAYS AS (
    CASE 
        WHEN status = 'Failed' THEN 'Failed'
        WHEN processing_time_sec <= 1.0 THEN 'Instant'
        WHEN processing_time_sec <= 2.0 THEN 'Fast'
        WHEN processing_time_sec <= 5.0 THEN 'Normal'
        WHEN processing_time_sec <= 15.0 THEN 'Slow'
        ELSE 'Very Slow'
    END
) STORED;


-- ============================================================================
-- STEP 4: CREATE CLEAN EXPORT VIEW
-- ============================================================================

CREATE OR REPLACE VIEW v_clean_transactions AS
SELECT 
    t.transaction_id,
    t.user_id,
    t.transaction_datetime,
    DATE(t.transaction_datetime) AS txn_date,
    HOUR(t.transaction_datetime) AS txn_hour,
    DAYNAME(t.transaction_datetime) AS day_of_week,
    DATE_FORMAT(t.transaction_datetime, '%Y-%m') AS txn_month,
    MONTHNAME(t.transaction_datetime) AS month_name,
    QUARTER(t.transaction_datetime) AS txn_quarter,
    t.payment_method,
    t.category,
    t.merchant,
    t.platform,
    t.device_type,
    t.city,
    t.amount,
    CASE 
        WHEN t.amount < 100 THEN 'Micro (<₹100)'
        WHEN t.amount < 500 THEN 'Small (₹100-500)'
        WHEN t.amount < 2000 THEN 'Medium (₹500-2K)'
        WHEN t.amount < 10000 THEN 'Large (₹2K-10K)'
        WHEN t.amount < 50000 THEN 'High (₹10K-50K)'
        ELSE 'Premium (₹50K+)'
    END AS amount_bucket,
    t.discount_applied,
    t.cashback_earned,
    (t.cashback_earned + t.discount_applied) AS total_savings,
    GREATEST(t.amount - t.discount_applied - t.cashback_earned, 0) AS net_amount,
    t.status,
    t.failure_reason,
    t.processing_time_sec,
    CASE 
        WHEN t.status = 'Failed' THEN 'Failed'
        WHEN t.processing_time_sec <= 1.0 THEN 'Instant'
        WHEN t.processing_time_sec <= 2.0 THEN 'Fast'
        WHEN t.processing_time_sec <= 5.0 THEN 'Normal'
        WHEN t.processing_time_sec <= 15.0 THEN 'Slow'
        ELSE 'Very Slow'
    END AS processing_speed,
    t.is_weekend,
    t.is_flagged,
    t.fraud_reason,
    t.is_refunded,
    t.refund_amount,
    -- User demographics from JOIN
    u.age_group,
    u.gender,
    u.account_tenure,
    u.customer_tier,
    u.spending_persona,
    u.preferred_method,
    u.city AS user_home_city,
    CASE 
        WHEN MONTH(t.transaction_datetime) IN (10, 11) THEN 'Festival Season'
        WHEN MONTH(t.transaction_datetime) IN (1, 8, 12) THEN 'Sale Season'
        ELSE 'Normal'
    END AS season_type,
    CASE 
        WHEN HOUR(t.transaction_datetime) BETWEEN 5 AND 11 THEN 'Morning'
        WHEN HOUR(t.transaction_datetime) BETWEEN 12 AND 16 THEN 'Afternoon'
        WHEN HOUR(t.transaction_datetime) BETWEEN 17 AND 21 THEN 'Evening'
        ELSE 'Night'
    END AS time_slot
FROM transactions t
LEFT JOIN user_profiles u ON t.user_id = u.user_id;

-- ============================================================================
-- STEP 5: POST-CLEANING VALIDATION
-- ============================================================================

SELECT 'CLEANING COMPLETE — Final Checks:' AS message;

SELECT 
    COUNT(*) AS total_rows,
    SUM(CASE WHEN failure_reason IS NULL AND status = 'Failed' THEN 1 ELSE 0 END) AS failed_without_reason,
    SUM(CASE WHEN failure_reason IS NOT NULL AND status = 'Success' THEN 1 ELSE 0 END) AS success_with_reason,
    SUM(CASE WHEN is_refunded = TRUE AND status != 'Success' THEN 1 ELSE 0 END) AS invalid_refunds,
    SUM(CASE WHEN refund_amount > amount THEN 1 ELSE 0 END) AS over_refunds,
    SUM(CASE WHEN cashback_earned < 0 THEN 1 ELSE 0 END) AS negative_cashback,
    SUM(CASE WHEN is_flagged = FALSE AND fraud_reason IS NOT NULL THEN 1 ELSE 0 END) AS orphan_fraud_reasons
FROM transactions;
