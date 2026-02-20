-- ============================================================================
-- FILE: 01_create_schema.sql
-- PROJECT: Digital Payment Transaction Analysis (Enhanced)
-- PURPOSE: Create database schema, tables, indexes, and load data
-- DATASET: 5,000 transactions (20 columns) + 500 user profiles (8 columns)
-- ============================================================================

-- Create Database
CREATE DATABASE IF NOT EXISTS digital_payments_db;
USE digital_payments_db;

-- ============================================================================
-- TABLE 1: user_profiles (Dimension Table — 500 users)
-- ============================================================================
DROP TABLE IF EXISTS user_profiles;

CREATE TABLE user_profiles (
    user_id             VARCHAR(10)     PRIMARY KEY,
    city                VARCHAR(30)     NOT NULL,
    age_group           VARCHAR(10)     NOT NULL,
    gender              VARCHAR(10)     NOT NULL,
    account_tenure      VARCHAR(15)     NOT NULL,
    customer_tier       VARCHAR(10)     NOT NULL,
    spending_persona    VARCHAR(15)     NOT NULL,
    preferred_method    VARCHAR(20)     NOT NULL,
    
    CONSTRAINT chk_age CHECK (age_group IN ('18-24','25-34','35-44','45-54','55+')),
    CONSTRAINT chk_gender CHECK (gender IN ('Male','Female','Other')),
    CONSTRAINT chk_tier CHECK (customer_tier IN ('New','Regular','Premium','VIP')),
    CONSTRAINT chk_persona CHECK (spending_persona IN ('Budget','Moderate','High Spender','Impulse'))
);

-- ============================================================================
-- TABLE 2: transactions (Fact Table — 5,000 rows, 20 columns)
-- ============================================================================
DROP TABLE IF EXISTS transactions;

CREATE TABLE transactions (
    transaction_id       VARCHAR(15)     PRIMARY KEY,
    user_id              VARCHAR(10)     NOT NULL,
    transaction_datetime DATETIME        NOT NULL,
    payment_method       VARCHAR(20)     NOT NULL,
    category             VARCHAR(30)     NOT NULL,
    merchant             VARCHAR(50)     NOT NULL,
    amount               DECIMAL(12,2)   NOT NULL,
    status               VARCHAR(10)     NOT NULL,
    failure_reason       VARCHAR(50)     NULL,
    platform             VARCHAR(20)     NOT NULL,
    device_type          VARCHAR(15)     NOT NULL,
    city                 VARCHAR(30)     NOT NULL,
    processing_time_sec  DECIMAL(5,2)    NOT NULL,
    is_weekend           TINYINT(1)      NOT NULL DEFAULT 0,
    cashback_earned      DECIMAL(10,2)   NOT NULL DEFAULT 0.00,
    discount_applied     DECIMAL(10,2)   NOT NULL DEFAULT 0.00,
    is_flagged           BOOLEAN         NOT NULL DEFAULT FALSE,
    fraud_reason         VARCHAR(50)     NULL,
    is_refunded          BOOLEAN         NOT NULL DEFAULT FALSE,
    refund_amount        DECIMAL(12,2)   NOT NULL DEFAULT 0.00,
    
    -- Constraints
    CONSTRAINT chk_status CHECK (status IN ('Success', 'Failed', 'Pending')),
    CONSTRAINT chk_amount CHECK (amount > 0),
    CONSTRAINT chk_processing CHECK (processing_time_sec > 0),
    CONSTRAINT chk_cashback CHECK (cashback_earned >= 0),
    CONSTRAINT chk_discount CHECK (discount_applied >= 0),
    CONSTRAINT chk_refund CHECK (refund_amount >= 0),
    
    -- Foreign Key
    CONSTRAINT fk_user FOREIGN KEY (user_id) REFERENCES user_profiles(user_id)
);

-- ============================================================================
-- INDEXES for Query Performance
-- ============================================================================
CREATE INDEX idx_txn_datetime     ON transactions(transaction_datetime);
CREATE INDEX idx_txn_status       ON transactions(status);
CREATE INDEX idx_txn_method       ON transactions(payment_method);
CREATE INDEX idx_txn_user         ON transactions(user_id);
CREATE INDEX idx_txn_city         ON transactions(city);
CREATE INDEX idx_txn_category     ON transactions(category);
CREATE INDEX idx_txn_flagged      ON transactions(is_flagged);
CREATE INDEX idx_txn_refunded     ON transactions(is_refunded);
CREATE INDEX idx_txn_device       ON transactions(device_type);
CREATE INDEX idx_txn_platform     ON transactions(platform);

-- Composite indexes for common query patterns
CREATE INDEX idx_txn_status_method ON transactions(status, payment_method);
CREATE INDEX idx_txn_user_status   ON transactions(user_id, status);
CREATE INDEX idx_txn_date_status   ON transactions(transaction_datetime, status);

-- ============================================================================
-- DATA LOADING
-- ============================================================================

-- MySQL: Load user profiles first (referenced by FK)
-- LOAD DATA INFILE '/path/to/user_profiles.csv'
-- INTO TABLE user_profiles
-- FIELDS TERMINATED BY ',' ENCLOSED BY '"'
-- LINES TERMINATED BY '\n'
-- IGNORE 1 ROWS;

-- MySQL: Load transactions
-- LOAD DATA INFILE '/path/to/transactions_raw.csv'
-- INTO TABLE transactions
-- FIELDS TERMINATED BY ',' ENCLOSED BY '"'
-- LINES TERMINATED BY '\n'
-- IGNORE 1 ROWS;

-- SQL Server: Load user profiles
-- BULK INSERT user_profiles FROM '/path/to/user_profiles.csv'
-- WITH (FIRSTROW = 2, FIELDTERMINATOR = ',', ROWTERMINATOR = '\n');

-- SQL Server: Load transactions
-- BULK INSERT transactions FROM '/path/to/transactions_raw.csv'
-- WITH (FIRSTROW = 2, FIELDTERMINATOR = ',', ROWTERMINATOR = '\n');

-- ============================================================================
-- VERIFICATION QUERIES
-- ============================================================================

-- Row count check
SELECT 'user_profiles' AS table_name, COUNT(*) AS row_count FROM user_profiles
UNION ALL
SELECT 'transactions', COUNT(*) FROM transactions;

-- Null check on critical columns
SELECT 
    SUM(CASE WHEN transaction_id IS NULL THEN 1 ELSE 0 END) AS null_txn_id,
    SUM(CASE WHEN user_id IS NULL THEN 1 ELSE 0 END) AS null_user_id,
    SUM(CASE WHEN amount IS NULL THEN 1 ELSE 0 END) AS null_amount,
    SUM(CASE WHEN status IS NULL THEN 1 ELSE 0 END) AS null_status,
    SUM(CASE WHEN device_type IS NULL THEN 1 ELSE 0 END) AS null_device
FROM transactions;

-- FK integrity check
SELECT COUNT(*) AS orphan_transactions
FROM transactions t
LEFT JOIN user_profiles u ON t.user_id = u.user_id
WHERE u.user_id IS NULL;

-- Status distribution
SELECT status, COUNT(*) AS cnt, 
       ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM transactions), 2) AS pct
FROM transactions
GROUP BY status
ORDER BY cnt DESC;

-- Payment method distribution
SELECT payment_method, COUNT(*) AS cnt,
       ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM transactions), 2) AS pct
FROM transactions
GROUP BY payment_method
ORDER BY cnt DESC;

-- Category distribution
SELECT category, COUNT(*) AS cnt
FROM transactions
GROUP BY category
ORDER BY cnt DESC;

-- User profile summary
SELECT 
    age_group, customer_tier, spending_persona,
    COUNT(*) AS user_count
FROM user_profiles
GROUP BY age_group, customer_tier, spending_persona
ORDER BY user_count DESC
LIMIT 15;
