---
title: Data Engineering Patterns Guide
permalink: /patterns/data-engineering/
---

* TOC
{:toc}

This comprehensive guide covers essential data engineering patterns for building robust, scalable data pipelines. These patterns are based on proven approaches for data integration, transformation, quality assurance, and delivery.

## Incremental Loading

Incremental loading is universally beneficial as it **speeds up data extraction**, **lowers the load** on source systems, and **reduces processing costs**. Instead of loading all data every time, incremental loading processes only new or changed records.

### When to Use Incremental Loading

- Source systems support change tracking (modified timestamps, change data capture)
- Data volumes are large and full loads are inefficient
- You want to minimize impact on source systems
- Processing costs need to be optimized
- Near real-time or frequent updates are required

### Implementation Patterns

#### Pattern 1: Timestamp-Based Incremental Load

This is the most common pattern using a `modified_since` or `updated_at` timestamp.

**Configuration Example:**

```json
{
    "config": {
        "incrementalOutput": true,
        "jobs": [
            {
                "endpoint": "customers",
                "dataType": "customers",
                "params": {
                    "modified_since": {
                        "time": "previousStart"
                    }
                }
            }
        ]
    }
}
```

The `previousStart` value contains the timestamp of the last **successful start** of the extraction. This introduces state management into your pipeline.

**SQL Implementation:**

```sql
-- Store last extraction timestamp
CREATE TABLE IF NOT EXISTS extraction_state (
    table_name VARCHAR(255),
    last_extraction TIMESTAMP,
    PRIMARY KEY (table_name)
);

-- Extract only new/modified records
SELECT *
FROM source_table
WHERE updated_at > (
    SELECT COALESCE(last_extraction, '1900-01-01')
    FROM extraction_state
    WHERE table_name = 'source_table'
);

-- Update state after successful extraction
MERGE INTO extraction_state AS target
USING (SELECT 'source_table' AS table_name, CURRENT_TIMESTAMP AS last_extraction) AS source
ON target.table_name = source.table_name
WHEN MATCHED THEN UPDATE SET last_extraction = source.last_extraction
WHEN NOT MATCHED THEN INSERT (table_name, last_extraction) VALUES (source.table_name, source.last_extraction);
```

#### Pattern 2: Date Range Incremental Load

Uses both `from` and `to` parameters for precise time window extraction.

**Configuration Example:**

```json
{
    "jobs": [
        {
            "endpoint": "transactions",
            "params": {
                "from": {
                    "function": "date",
                    "args": ["Y-m-d", {"time": "previousStart"}]
                },
                "to": {
                    "function": "date",
                    "args": ["Y-m-d", {"time": "currentStart"}]
                }
            }
        }
    ]
}
```

This generates requests like: `GET /transactions?from=2024-01-15&to=2024-01-16`

#### Pattern 3: Incremental Load with Primary Key

When loading data incrementally with a primary key defined, new rows are added and existing rows are **updated**.

**Storage Configuration:**

```json
{
    "destination": "in.c-main.customers",
    "incremental": true,
    "primary_key": ["customer_id"]
}
```

**Behavior:**

| Initial Table | Incremental Load | Result |
|---------------|------------------|--------|
| John, $150    | John, $200       | John, $200 (updated) |
| Peter, $340   | Annie, $500      | Peter, $340 (unchanged) |
| Darla, $600   | Darla, $600      | Annie, $500 (new) |

**Important Notes:**
- Records are updated only when values change
- Identical records don't update the `_timestamp` column (in non-native type tables)
- No rows are deleted; use full load for deletions
- Order of rows is not preserved

### Data Type Considerations

There are three main scenarios for incremental loading:

1. **Added entries only**: Simply append data with `incrementalOutput: true`
2. **Added and modified entries**: Use `incrementalOutput: true` with a primary key for deduplication
3. **All rows (full snapshot)**: Set a primary key or use full load; incremental without primary key creates duplicates

### Best Practices

1. **Always set a primary key** when loading data that can be updated
2. **Monitor state storage** to reset if needed (via API or configuration)
3. **Handle failures gracefully** - the system picks up from the last successful run
4. **Consider data volume** - incremental loads save significant processing costs
5. **Test edge cases** like DST changes, leap seconds, and timezone handling
6. **Document your incremental logic** for maintenance and troubleshooting

## Full Load Pattern

Full load involves replacing the entire target dataset with fresh data from the source. While less efficient than incremental loading, it's necessary in certain scenarios.

### When to Use Full Load

- Source system doesn't support change tracking
- Data volume is small enough for complete refresh
- You need to detect and handle deleted records
- Data quality requires complete refresh to avoid inconsistencies
- Simplicity is prioritized over efficiency
- Historical changes need to be completely overwritten

### Implementation Patterns

#### Pattern 1: Truncate and Load

**Configuration:**

```json
{
    "config": {
        "incrementalOutput": false,
        "destination": "in.c-main.products"
    }
}
```

When `incrementalOutput` is `false`, the target table contents are cleared before loading.

**SQL Implementation:**

```sql
-- Create staging table
CREATE OR REPLACE TABLE products_staging AS
SELECT *
FROM source_products;

-- Validate data quality
SELECT
    COUNT(*) as record_count,
    COUNT(DISTINCT product_id) as unique_products,
    SUM(CASE WHEN product_id IS NULL THEN 1 ELSE 0 END) as null_ids
FROM products_staging;

-- Replace production table
CREATE OR REPLACE TABLE products AS
SELECT * FROM products_staging;
```

#### Pattern 2: Swap Table Pattern

```sql
-- Load into temporary table
CREATE OR REPLACE TABLE products_new AS
SELECT * FROM source_products;

-- Perform validations
SET abort_on_validation_failure = (
    SELECT CASE
        WHEN COUNT(*) = 0 THEN 'No data loaded'
        WHEN COUNT(*) < (SELECT COUNT(*) * 0.5 FROM products) THEN 'Suspicious data drop'
        ELSE ''
    END
    FROM products_new
);

-- Swap tables atomically
ALTER TABLE products RENAME TO products_old;
ALTER TABLE products_new RENAME TO products;
DROP TABLE products_old;
```

#### Pattern 3: Scheduled Full Refresh

Combine incremental and full loads for optimal performance:

```sql
-- Daily incremental load
-- Scheduled every day at hourly intervals

-- Weekly full load
-- Scheduled every Sunday at 2 AM to catch any missed updates or deletions
```

### Full Load vs Incremental: Decision Matrix

| Criteria | Full Load | Incremental Load |
|----------|-----------|------------------|
| Data Volume | Small to Medium | Medium to Large |
| Change Frequency | Low | High |
| Deletion Detection | Required | Not supported |
| Source System Load | Higher | Lower |
| Processing Cost | Higher | Lower |
| Implementation Complexity | Simple | Moderate |
| Data Freshness | Batch windows | Near real-time |

### Best Practices

1. **Implement pre-load validations** to verify data quality
2. **Use staging tables** to avoid partial loads in production
3. **Schedule during off-peak hours** to minimize impact
4. **Monitor data volumes** for unexpected changes
5. **Maintain backups** before full loads
6. **Document refresh schedules** and dependencies

## Change Data Capture (CDC) Patterns

CDC captures and tracks data changes in real-time or near real-time, enabling efficient data synchronization and event-driven architectures.

### When to Use CDC

- Real-time or near real-time data synchronization required
- Source system supports CDC (database logs, triggers, timestamps)
- Need to track all changes (inserts, updates, deletes)
- Building event-driven data pipelines
- Minimizing source system impact is critical
- Compliance requires audit trails of all changes

### CDC Implementation Patterns

#### Pattern 1: Timestamp-Based CDC

Simplest form using `created_at` and `updated_at` timestamps.

**Source Table Structure:**

```sql
CREATE TABLE customers (
    customer_id INT PRIMARY KEY,
    name VARCHAR(255),
    email VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_deleted BOOLEAN DEFAULT FALSE
);
```

**CDC Extraction:**

```sql
-- Capture all changes since last run
SELECT
    customer_id,
    name,
    email,
    created_at,
    updated_at,
    is_deleted,
    CASE
        WHEN is_deleted = TRUE THEN 'DELETE'
        WHEN created_at = updated_at THEN 'INSERT'
        ELSE 'UPDATE'
    END as change_type,
    CURRENT_TIMESTAMP as extraction_timestamp
FROM customers
WHERE updated_at > :last_extraction_time
   OR (is_deleted = TRUE AND updated_at > :last_extraction_time);
```

#### Pattern 2: Log-Based CDC

Captures changes from database transaction logs (e.g., MySQL binlog, PostgreSQL WAL, SQL Server CDC).

**Configuration Example:**

```json
{
    "source": {
        "type": "mysql-cdc",
        "host": "source-db.example.com",
        "database": "production",
        "tables": ["customers", "orders", "products"],
        "capture_deletes": true,
        "output_format": "json"
    }
}
```

**CDC Output Format:**

```json
{
    "operation": "UPDATE",
    "timestamp": "2024-01-15T10:30:45Z",
    "table": "customers",
    "primary_key": {"customer_id": 12345},
    "before": {
        "customer_id": 12345,
        "email": "old@example.com",
        "status": "active"
    },
    "after": {
        "customer_id": 12345,
        "email": "new@example.com",
        "status": "active"
    }
}
```

#### Pattern 3: CDC Processing and Application

**Processing CDC Events:**

```sql
-- Create CDC staging table
CREATE TABLE customers_cdc_staging (
    customer_id INT,
    name VARCHAR(255),
    email VARCHAR(255),
    change_type VARCHAR(10),
    change_timestamp TIMESTAMP,
    extraction_timestamp TIMESTAMP
);

-- Apply CDC changes to target table
MERGE INTO customers AS target
USING (
    SELECT * FROM customers_cdc_staging
    WHERE change_type IN ('INSERT', 'UPDATE')
    QUALIFY ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY change_timestamp DESC) = 1
) AS source
ON target.customer_id = source.customer_id
WHEN MATCHED AND source.change_type = 'UPDATE' THEN
    UPDATE SET
        name = source.name,
        email = source.email,
        updated_at = source.change_timestamp
WHEN NOT MATCHED AND source.change_type = 'INSERT' THEN
    INSERT (customer_id, name, email, created_at, updated_at)
    VALUES (source.customer_id, source.name, source.email, source.change_timestamp, source.change_timestamp);

-- Handle deletions
DELETE FROM customers
WHERE customer_id IN (
    SELECT customer_id
    FROM customers_cdc_staging
    WHERE change_type = 'DELETE'
);
```

#### Pattern 4: CDC with History Tracking

Maintain complete history of all changes:

```sql
-- Create history table
CREATE TABLE customers_history (
    customer_id INT,
    name VARCHAR(255),
    email VARCHAR(255),
    valid_from TIMESTAMP,
    valid_to TIMESTAMP,
    change_type VARCHAR(10),
    is_current BOOLEAN
);

-- Populate history from CDC
INSERT INTO customers_history
SELECT
    customer_id,
    name,
    email,
    change_timestamp AS valid_from,
    LEAD(change_timestamp) OVER (PARTITION BY customer_id ORDER BY change_timestamp) AS valid_to,
    change_type,
    CASE WHEN LEAD(change_timestamp) OVER (PARTITION BY customer_id ORDER BY change_timestamp) IS NULL
         THEN TRUE ELSE FALSE END AS is_current
FROM customers_cdc_staging
ORDER BY customer_id, change_timestamp;
```

### CDC Best Practices

1. **Handle out-of-order events** with proper sequencing logic
2. **Implement idempotency** to safely reprocess events
3. **Monitor lag** between source changes and CDC processing
4. **Test failure scenarios** including network issues and restarts
5. **Maintain CDC metadata** for troubleshooting and auditing
6. **Plan for schema changes** in source systems
7. **Consider retention policies** for CDC logs and history tables

## Data Quality Checks

Data quality checks ensure that data meets defined standards before it's processed or delivered. Implementing comprehensive quality checks prevents corrupted data from propagating through your pipelines.

### When to Implement Data Quality Checks

- Data from external or untrusted sources
- Critical business decisions depend on the data
- Compliance and regulatory requirements
- Data transformations are complex
- Multiple data sources are being integrated
- Historical data quality issues have occurred

### Data Quality Check Patterns

#### Pattern 1: Schema Validation

Verify that data conforms to expected structure and types.

**SQL Implementation:**

```sql
-- Test column data types
CALL TEST_COLUMN_DATA_TYPE('customers', 'customer_id', 'NUMBER');
CALL TEST_COLUMN_DATA_TYPE('customers', 'email', 'VARCHAR');
CALL TEST_COLUMN_DATA_TYPE('customers', 'created_at', 'TIMESTAMP');

-- Test column value data types (for untyped tables)
CALL TEST_COLUMN_VALUE_DATA_TYPE('orders', 'total_amount', 'NUMERIC');
```

#### Pattern 2: Completeness Checks

Ensure required fields are populated.

**SQL Implementation:**

```sql
-- Test for NULL values
CALL TEST_COLUMN_NULL('customers', 'customer_id');
CALL TEST_COLUMN_NULL('customers', 'email');

-- Test for NULL or empty strings
CALL TEST_COLUMN_NULL_OR_EMPTY('customers', 'name');

-- Custom completeness check
CREATE OR REPLACE TABLE dq_completeness_check AS
SELECT
    'customers' AS table_name,
    COUNT(*) AS total_records,
    SUM(CASE WHEN customer_id IS NULL THEN 1 ELSE 0 END) AS null_customer_id,
    SUM(CASE WHEN email IS NULL OR email = '' THEN 1 ELSE 0 END) AS missing_email,
    SUM(CASE WHEN phone IS NULL OR phone = '' THEN 1 ELSE 0 END) AS missing_phone,
    ROUND(100.0 * SUM(CASE WHEN email IS NULL OR email = '' THEN 1 ELSE 0 END) / COUNT(*), 2) AS email_null_pct
FROM customers;

-- Validate completeness threshold
SET ABORT_TRANSFORMATION = (
    SELECT CASE
        WHEN email_null_pct > 5 THEN 'Email completeness below threshold: ' || email_null_pct || '%'
        ELSE ''
    END
    FROM dq_completeness_check
);
```

#### Pattern 3: Uniqueness Checks

Verify primary keys and unique constraints.

**SQL Implementation:**

```sql
-- Test column uniqueness
CALL TEST_COLUMN_UNIQUE('customers', ARRAY_CONSTRUCT('customer_id'));

-- Test composite uniqueness
CALL TEST_COLUMN_UNIQUE('order_items', ARRAY_CONSTRUCT('order_id', 'line_number'));

-- Custom uniqueness validation
CREATE OR REPLACE TABLE dq_uniqueness_check AS
SELECT
    customer_id,
    COUNT(*) AS occurrence_count
FROM customers
GROUP BY customer_id
HAVING COUNT(*) > 1;

-- Abort on duplicates
SET ABORT_TRANSFORMATION = (
    SELECT CASE
        WHEN COUNT(*) > 0 THEN 'Found ' || COUNT(*) || ' duplicate customer_id values'
        ELSE ''
    END
    FROM dq_uniqueness_check
);
```

#### Pattern 4: Referential Integrity Checks

Ensure foreign key relationships are valid.

**SQL Implementation:**

```sql
-- Test foreign key references
CALL TEST_COLUMN_FOREIGN_REF('orders', 'customers', 'customer_id', 'customer_id');

-- Custom referential integrity check
CREATE OR REPLACE TABLE dq_orphaned_records AS
SELECT o.*
FROM orders o
LEFT JOIN customers c ON o.customer_id = c.customer_id
WHERE c.customer_id IS NULL;

-- Log orphaned records
INSERT INTO dq_results_log (
    test_id,
    test_name,
    test_result,
    test_result_value,
    execution_time
)
SELECT
    'REF_INT_001',
    'Orders without valid customer',
    CASE WHEN COUNT(*) > 0 THEN 'error' ELSE 'success' END,
    OBJECT_CONSTRUCT('orphaned_count', COUNT(*)),
    CURRENT_TIMESTAMP
FROM dq_orphaned_records;
```

#### Pattern 5: Value Range and Format Checks

Validate that values fall within expected ranges and formats.

**SQL Implementation:**

```sql
-- Test value ranges
CALL TEST_VALUE_IN_RANGE('products', 'price', 0, 1000000);
CALL TEST_VALUE_GREATER_THAN('orders', 'quantity', 0);

-- Test value sets
CALL TEST_VALUE_IN_SET('customers', 'status', ARRAY_CONSTRUCT('active', 'inactive', 'pending'));

-- Test regular expressions
CALL TEST_VALUE_REGEXP('customers', 'email', '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Z|a-z]{2,}$');

-- Custom format validation
CREATE OR REPLACE TABLE dq_format_check AS
SELECT
    customer_id,
    email,
    phone,
    CASE
        WHEN email NOT RLIKE '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Z|a-z]{2,}$'
        THEN 'Invalid email format'
        ELSE NULL
    END AS email_issue,
    CASE
        WHEN phone NOT RLIKE '^\\+?[1-9]\\d{1,14}$'
        THEN 'Invalid phone format'
        ELSE NULL
    END AS phone_issue
FROM customers
WHERE email_issue IS NOT NULL OR phone_issue IS NOT NULL;
```

#### Pattern 6: Statistical Anomaly Detection

Detect outliers and anomalies in numeric data.

**SQL Implementation:**

```sql
-- Test for numeric anomalies
CALL TEST_ANOMALY_NUMERIC('orders', 'total_amount');

-- Custom anomaly detection
CREATE OR REPLACE TABLE dq_anomaly_check AS
WITH stats AS (
    SELECT
        AVG(total_amount) AS mean_amount,
        STDDEV(total_amount) AS stddev_amount
    FROM orders
    WHERE order_date >= DATEADD(day, -30, CURRENT_DATE)
)
SELECT
    o.order_id,
    o.total_amount,
    s.mean_amount,
    s.stddev_amount,
    ABS(o.total_amount - s.mean_amount) / NULLIF(s.stddev_amount, 0) AS z_score
FROM orders o
CROSS JOIN stats s
WHERE ABS(o.total_amount - s.mean_amount) > 3 * s.stddev_amount
  AND o.order_date >= DATEADD(day, -30, CURRENT_DATE);
```

#### Pattern 7: Time Series Completeness

Verify that time series data is complete without gaps.

**SQL Implementation:**

```sql
-- Test time series completeness
CALL TEST_TIME_SERIES_COMPLETE('daily_sales', 'sale_date', 'DAY', 1);

-- Test time series within a range
CALL TEST_TIME_SERIES_COMPLETE_RANGE(
    'hourly_metrics',
    'metric_hour',
    'HOUR',
    100,
    '2024-01-01',
    '2024-01-31'
);

-- Custom time series gap detection
CREATE OR REPLACE TABLE dq_timeseries_gaps AS
WITH date_range AS (
    SELECT
        DATEADD(day, ROW_NUMBER() OVER (ORDER BY NULL) - 1,
                (SELECT MIN(sale_date) FROM daily_sales)) AS expected_date
    FROM TABLE(GENERATOR(ROWCOUNT => 365))
),
actual_dates AS (
    SELECT DISTINCT sale_date
    FROM daily_sales
)
SELECT dr.expected_date AS missing_date
FROM date_range dr
LEFT JOIN actual_dates ad ON dr.expected_date = ad.sale_date
WHERE ad.sale_date IS NULL
  AND dr.expected_date <= CURRENT_DATE;
```

### Data Quality Results Logging

Implement centralized logging for all quality checks.

**DQ Results Log Table:**

```sql
CREATE TABLE IF NOT EXISTS dq_results_log (
    id VARCHAR(255),
    execution_time TIMESTAMP,
    component_id VARCHAR(255),
    configuration_id VARCHAR(255),
    run_id VARCHAR(255),
    job_url VARCHAR(1000),
    test_id VARCHAR(255),
    test_query VARCHAR(5000),
    test_name VARCHAR(255),
    test_result_value VARIANT,
    test_parameters VARIANT,
    test_result VARCHAR(50),
    test_level VARCHAR(20),
    PRIMARY KEY (id)
);
```

**Logging Implementation:**

```sql
-- Log test results
INSERT INTO dq_results_log
SELECT
    MD5(test_id || execution_time::VARCHAR) AS id,
    CURRENT_TIMESTAMP AS execution_time,
    'keboola.snowflake-transformation' AS component_id,
    '943845068' AS configuration_id,
    '943845595' AS run_id,
    'https://connection.keboola.com/admin/projects/9389/queue/943845595' AS job_url,
    'TEST_001' AS test_id,
    'TEST_COLUMN_NULL(''customers'', ''email'')' AS test_query,
    'Email Null Check' AS test_name,
    OBJECT_CONSTRUCT('null_count', null_count) AS test_result_value,
    OBJECT_CONSTRUCT('table', 'customers', 'column', 'email') AS test_parameters,
    CASE WHEN null_count = 0 THEN 'success' ELSE 'error' END AS test_result,
    'FAIL' AS test_level
FROM (SELECT COUNT(*) AS null_count FROM customers WHERE email IS NULL);
```

### Data Quality Check Best Practices

1. **Implement checks at multiple stages**: source, staging, and production
2. **Use appropriate test levels**: WARNING for non-critical, FAIL for critical
3. **Log all test results** for monitoring and troubleshooting
4. **Set up alerts** for failed critical tests
5. **Document quality rules** and their business justification
6. **Review and update checks** as data evolves
7. **Balance thoroughness with performance** - don't over-test
8. **Use shared code libraries** for reusable test procedures

## Error Handling Patterns

Robust error handling ensures pipelines fail gracefully, provide meaningful diagnostics, and enable quick recovery.

### When to Implement Error Handling

- Production pipelines with SLA requirements
- Complex transformations prone to data-related errors
- External API integrations with potential failures
- Pipelines processing critical business data
- Automated workflows requiring minimal manual intervention

### Error Handling Patterns

#### Pattern 1: Transformation Abort on Error

Stop processing when critical data quality issues are detected.

**SQL Implementation:**

```sql
-- Perform data quality check
CREATE OR REPLACE TABLE integrity_check AS
SELECT
    'missing_required_fields' AS check_name,
    COUNT(*) AS failure_count
FROM customers
WHERE email IS NULL OR customer_id IS NULL
HAVING COUNT(*) > 0

UNION ALL

SELECT
    'duplicate_primary_keys' AS check_name,
    COUNT(*) AS failure_count
FROM (
    SELECT customer_id, COUNT(*) AS cnt
    FROM customers
    GROUP BY customer_id
    HAVING COUNT(*) > 1
);

-- Abort transformation if checks fail
SET ABORT_TRANSFORMATION = (
    SELECT
        CASE
            WHEN SUM(failure_count) > 0 THEN
                'Data quality checks failed: ' ||
                LISTAGG(check_name || '(' || failure_count || ')', ', ')
            ELSE ''
        END
    FROM integrity_check
);
```

#### Pattern 2: Conditional Flow Error Handling

Use conditional logic to handle different error scenarios.

**Configuration:**

```json
{
    "phases": [
        {
            "id": "extract-data",
            "tasks": [{"component": "extractor", "config": "config-1"}]
        },
        {
            "id": "check-errors",
            "conditions": [
                {
                    "if": {
                        "operator": "eq",
                        "left": {"task": "extract-data", "value": "job.status"},
                        "right": {"const": "error"}
                    },
                    "then": {
                        "phase": "error-notification"
                    }
                },
                {
                    "if": {
                        "operator": "eq",
                        "left": {"task": "extract-data", "value": "job.status"},
                        "right": {"const": "success"}
                    },
                    "then": {
                        "phase": "transform-data"
                    }
                }
            ]
        },
        {
            "id": "error-notification",
            "tasks": [
                {
                    "type": "notification",
                    "channels": ["email"],
                    "recipients": ["data-team@example.com"],
                    "message": "Data extraction failed. Please investigate."
                }
            ]
        },
        {
            "id": "transform-data",
            "tasks": [{"component": "transformation", "config": "transform-1"}]
        }
    ]
}
```

#### Pattern 3: Retry Logic

Automatically retry failed operations with configurable delays.

**Configuration:**

```json
{
    "task": {
        "component": "external-api-extractor",
        "config": "api-config",
        "retry": {
            "max_attempts": 3,
            "delay_seconds": 10,
            "retry_on": ["timeout", "rate_limit"]
        }
    }
}
```

**SQL Retry Pattern:**

```sql
-- Implement retry logic in transformation
CREATE OR REPLACE PROCEDURE load_with_retry(
    source_table VARCHAR,
    target_table VARCHAR,
    max_retries INT
)
RETURNS VARCHAR
LANGUAGE SQL
AS
$$
DECLARE
    attempt INT DEFAULT 0;
    success BOOLEAN DEFAULT FALSE;
    error_msg VARCHAR;
BEGIN
    WHILE attempt < max_retries AND NOT success DO
        BEGIN
            -- Attempt the load
            EXECUTE IMMEDIATE 'INSERT INTO ' || target_table ||
                            ' SELECT * FROM ' || source_table;
            success := TRUE;
            RETURN 'Success after ' || attempt || ' retries';
        EXCEPTION
            WHEN OTHER THEN
                attempt := attempt + 1;
                error_msg := SQLERRM;
                IF attempt < max_retries THEN
                    CALL SYSTEM$WAIT(10); -- Wait 10 seconds
                END IF;
        END;
    END WHILE;

    IF NOT success THEN
        RETURN 'Failed after ' || max_retries || ' attempts: ' || error_msg;
    END IF;
END;
$$;
```

#### Pattern 4: Dead Letter Queue

Capture and isolate problematic records for later review.

**SQL Implementation:**

```sql
-- Create dead letter table
CREATE TABLE IF NOT EXISTS orders_dead_letter (
    record_data VARIANT,
    error_message VARCHAR(5000),
    error_timestamp TIMESTAMP,
    source_file VARCHAR(500),
    retry_count INT DEFAULT 0
);

-- Process with error isolation
INSERT INTO orders
SELECT
    order_id,
    customer_id,
    order_date,
    total_amount
FROM orders_staging
WHERE TRY_CAST(total_amount AS DECIMAL(10,2)) IS NOT NULL
  AND TRY_CAST(order_date AS DATE) IS NOT NULL;

-- Capture failed records
INSERT INTO orders_dead_letter (record_data, error_message, error_timestamp, source_file)
SELECT
    OBJECT_CONSTRUCT(*) AS record_data,
    CASE
        WHEN TRY_CAST(total_amount AS DECIMAL(10,2)) IS NULL THEN 'Invalid amount: ' || total_amount
        WHEN TRY_CAST(order_date AS DATE) IS NULL THEN 'Invalid date: ' || order_date
        ELSE 'Unknown error'
    END AS error_message,
    CURRENT_TIMESTAMP AS error_timestamp,
    METADATA$FILENAME AS source_file
FROM orders_staging
WHERE TRY_CAST(total_amount AS DECIMAL(10,2)) IS NULL
   OR TRY_CAST(order_date AS DATE) IS NULL;
```

#### Pattern 5: Graceful Degradation

Allow pipeline to continue with reduced functionality when non-critical components fail.

**Configuration:**

```json
{
    "phases": [
        {
            "id": "core-extraction",
            "tasks": [
                {"component": "critical-extractor", "config": "config-1"}
            ]
        },
        {
            "id": "enrichment",
            "tasks": [
                {
                    "component": "optional-enrichment",
                    "config": "enrichment-1",
                    "continue_on_failure": true
                }
            ]
        },
        {
            "id": "final-processing",
            "conditions": [
                {
                    "if": {
                        "operator": "in",
                        "left": {"task": "core-extraction", "value": "job.status"},
                        "right": {"const": ["success", "warning"]}
                    },
                    "then": {"phase": "load-data"}
                }
            ]
        }
    ]
}
```

#### Pattern 6: Error Logging and Monitoring

Comprehensive error tracking for debugging and alerting.

**SQL Implementation:**

```sql
-- Create error log table
CREATE TABLE IF NOT EXISTS pipeline_errors (
    error_id VARCHAR(255) PRIMARY KEY,
    pipeline_name VARCHAR(255),
    component_name VARCHAR(255),
    error_type VARCHAR(100),
    error_message VARCHAR(5000),
    error_details VARIANT,
    error_timestamp TIMESTAMP,
    severity VARCHAR(20),
    resolved BOOLEAN DEFAULT FALSE
);

-- Log errors during processing
CREATE OR REPLACE PROCEDURE log_error(
    p_pipeline VARCHAR,
    p_component VARCHAR,
    p_error_type VARCHAR,
    p_error_msg VARCHAR,
    p_details VARIANT,
    p_severity VARCHAR
)
RETURNS VARCHAR
LANGUAGE SQL
AS
$$
BEGIN
    INSERT INTO pipeline_errors (
        error_id,
        pipeline_name,
        component_name,
        error_type,
        error_message,
        error_details,
        error_timestamp,
        severity
    )
    VALUES (
        MD5(p_pipeline || p_component || CURRENT_TIMESTAMP::VARCHAR),
        p_pipeline,
        p_component,
        p_error_type,
        p_error_msg,
        p_details,
        CURRENT_TIMESTAMP,
        p_severity
    );
    RETURN 'Error logged';
END;
$$;

-- Usage in transformations
BEGIN
    -- Attempt risky operation
    INSERT INTO target_table SELECT * FROM source_table;
EXCEPTION
    WHEN OTHER THEN
        CALL log_error(
            'customer-pipeline',
            'data-transformation',
            'insert-failure',
            SQLERRM,
            OBJECT_CONSTRUCT('row_count', (SELECT COUNT(*) FROM source_table)),
            'ERROR'
        );
        -- Re-raise or handle
        RAISE;
END;
```

### Error Handling Best Practices

1. **Fail fast for critical errors**, degrade gracefully for non-critical ones
2. **Provide actionable error messages** with context
3. **Implement retry logic with exponential backoff** for transient failures
4. **Log all errors** with sufficient detail for debugging
5. **Set up monitoring and alerts** for error patterns
6. **Document error scenarios** and recovery procedures
7. **Test error handling** regularly
8. **Use write_always output mapping** to save logs even on failure

## Pipeline Design Patterns

Effective pipeline design determines the maintainability, scalability, and efficiency of your data platform.

### Pipeline Design Approaches

#### Approach 1: Result-Driven Pipelines

Each pipeline corresponds to a single data **destination**. The schedule is determined by the desired frequency of destination updates.

**When to Use:**
- Limited number of data destinations
- Destinations require mostly separate operations
- Quick iterations and prototyping needed
- Ad-hoc data processing
- Independent data products

**Example Architecture:**

```
Pipeline: Mailchimp Recipients Update
├── Extract: Google Analytics (Campaigns)
├── Extract: Snowflake DB (Email recipient index)
├── Transform: Campaign Performance
├── Transform: Campaign Recipient
└── Load: Mailchimp (New recipients)

Schedule: Every 6 hours
```

**Pros:**
- Straightforward and easy to understand
- Clear dependencies
- Easy to maintain
- Good for independent pipelines
- Data is always current
- Easy modifications

**Cons:**
- Overlapping pipelines reduce efficiency
- Difficult reusability
- Can become messy with many overlapping pipelines
- May cause unnecessary extractions

#### Approach 2: ETL-Based Design

Build pipelines around Extract, Transform, Load phases with centralized orchestration.

**When to Use:**
- Well-defined project requirements
- Single update schedule for all data
- Data must be current to same moment in time
- Credit optimization is priority
- Centralized data team management

**Example Architecture:**

```
Master ETL Pipeline (Daily at 2 AM)
├── Phase 1: Extract
│   ├── Salesforce Connector
│   ├── MySQL Database Connector
│   ├── Google Analytics Connector
│   └── API Extractors
├── Phase 2: Transform
│   ├── Data Cleaning
│   ├── Business Logic Transformations
│   ├── Data Quality Checks
│   └── Aggregations
└── Phase 3: Load
    ├── Data Warehouse Writer
    ├── BI Tool Connector
    └── Operational Database Writer

Schedule: Once daily
```

**Pros:**
- Centralized approach with single update schedule
- All data current to same moment
- No redundant extractions (credit efficient)
- Clear separation of concerns

**Cons:**
- Requires upfront planning
- Everything runs in sync with central schedule
- Harder to modify without side effects
- Less flexible for varying update frequencies

#### Approach 3: Mirroring (Hybrid Design)

Separate extraction orchestrations running at optimal frequencies, with downstream pipelines consuming the mirrored data.

**When to Use:**
- Data sources have varying update frequencies
- Need flexibility in downstream processing
- Building multiple data products
- Easy project evolution required
- Pipelines need to be added frequently

**Example Architecture:**

```
Extraction Layer (Mirroring)
├── O1: Email Index (every 5 minutes)
├── O2: Campaigns (every 30 minutes)
├── O3: Page Comments (hourly)
├── O4: Subsidiary IS (daily at 2 AM)
└── O5: Main IS (every 2 hours)

Processing Layer (Pipelines)
├── P1: Consistency Errors (hourly)
├── P2: Reporting Main (every 2 hours)
├── P3: Marketing Analytics (every 30 minutes)
└── P4: Executive Dashboard (daily)
```

**Configuration Example:**

```json
{
    "orchestrations": {
        "extraction": [
            {
                "name": "Mirror Google Analytics",
                "schedule": "*/30 * * * *",
                "tasks": [{"component": "google-analytics-extractor"}]
            },
            {
                "name": "Mirror Salesforce",
                "schedule": "0 */2 * * *",
                "tasks": [{"component": "salesforce-extractor"}]
            }
        ],
        "pipelines": [
            {
                "name": "Marketing Dashboard",
                "schedule": "*/30 * * * *",
                "tasks": [
                    {"component": "marketing-transformation"},
                    {"component": "dashboard-writer"}
                ]
            }
        ]
    }
}
```

**Pros:**
- Easy project evolution
- Pipelines don't interfere with each other
- All data reasonably current
- Easy to add new pipelines
- Flexible update frequencies

**Cons:**
- More complex setup
- May waste credits if extractions run too often
- Needs research about extraction times
- Requires organized storage structure

### Pipeline Design Best Practices

1. **Start simple**: Begin with result-driven pipelines, evolve to mirroring as needed
2. **Document dependencies**: Make pipeline relationships clear
3. **Use consistent naming**: Establish naming conventions for pipelines and components
4. **Implement monitoring**: Track pipeline execution times and failures
5. **Plan for growth**: Design with future scaling in mind
6. **Optimize schedules**: Balance freshness with cost
7. **Test thoroughly**: Validate pipeline logic before production
8. **Version control**: Track pipeline configuration changes

## Multi-Source Aggregation

Combining data from multiple sources into unified datasets for analysis and reporting.

### When to Use Multi-Source Aggregation

- Building 360-degree customer views
- Consolidating financial data from multiple systems
- Creating unified reporting across departments
- Combining online and offline data sources
- Merging data from acquisitions or subsidiaries

### Aggregation Patterns

#### Pattern 1: Union-Based Aggregation

Combine similar data from multiple sources vertically.

**SQL Implementation:**

```sql
-- Combine sales from multiple channels
CREATE OR REPLACE TABLE unified_sales AS
SELECT
    'online' AS source_channel,
    order_id,
    customer_id,
    order_date,
    total_amount,
    'web' AS acquisition_source
FROM online_sales

UNION ALL

SELECT
    'retail' AS source_channel,
    store_order_id AS order_id,
    customer_number AS customer_id,
    sale_date AS order_date,
    total AS total_amount,
    'store' AS acquisition_source
FROM retail_pos_sales

UNION ALL

SELECT
    'mobile' AS source_channel,
    transaction_id AS order_id,
    user_id AS customer_id,
    txn_date AS order_date,
    amount AS total_amount,
    'mobile_app' AS acquisition_source
FROM mobile_app_orders;

-- Add source tracking and data quality
ALTER TABLE unified_sales
ADD COLUMN source_load_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
```

#### Pattern 2: Join-Based Aggregation

Combine different attributes from multiple sources horizontally.

**SQL Implementation:**

```sql
-- Create 360-degree customer view
CREATE OR REPLACE TABLE customer_360 AS
SELECT
    -- Core identity from CRM
    c.customer_id,
    c.email,
    c.first_name,
    c.last_name,
    c.registration_date,

    -- Purchase behavior from transactions
    t.total_orders,
    t.total_spent,
    t.first_order_date,
    t.last_order_date,
    t.average_order_value,

    -- Marketing engagement from marketing platform
    m.email_opens,
    m.email_clicks,
    m.campaign_responses,
    m.last_engagement_date,

    -- Support interactions from support system
    s.support_tickets,
    s.last_ticket_date,
    s.satisfaction_score,

    -- Product usage from application logs
    u.login_count,
    u.feature_usage_score,
    u.last_login_date,

    -- Enrichment from third-party data
    e.industry,
    e.company_size,
    e.linkedin_profile

FROM crm_customers c
LEFT JOIN (
    SELECT
        customer_id,
        COUNT(*) AS total_orders,
        SUM(total_amount) AS total_spent,
        MIN(order_date) AS first_order_date,
        MAX(order_date) AS last_order_date,
        AVG(total_amount) AS average_order_value
    FROM orders
    GROUP BY customer_id
) t ON c.customer_id = t.customer_id

LEFT JOIN marketing_engagement m ON c.email = m.email_address
LEFT JOIN support_summary s ON c.customer_id = s.customer_id
LEFT JOIN usage_metrics u ON c.customer_id = u.user_id
LEFT JOIN external_enrichment e ON c.email = e.email;
```

#### Pattern 3: Incremental Multi-Source Aggregation

Efficiently update aggregated views with only changed data.

**SQL Implementation:**

```sql
-- Track last update time for each source
CREATE TABLE IF NOT EXISTS aggregation_state (
    source_name VARCHAR(255) PRIMARY KEY,
    last_aggregation_time TIMESTAMP
);

-- Incremental aggregation from source 1
CREATE OR REPLACE TEMPORARY TABLE new_online_sales AS
SELECT *
FROM online_sales
WHERE updated_at > (
    SELECT COALESCE(last_aggregation_time, '1900-01-01')
    FROM aggregation_state
    WHERE source_name = 'online_sales'
);

-- Incremental aggregation from source 2
CREATE OR REPLACE TEMPORARY TABLE new_retail_sales AS
SELECT *
FROM retail_pos_sales
WHERE updated_at > (
    SELECT COALESCE(last_aggregation_time, '1900-01-01')
    FROM aggregation_state
    WHERE source_name = 'retail_sales'
);

-- Merge into unified table
MERGE INTO unified_sales target
USING (
    SELECT * FROM new_online_sales
    UNION ALL
    SELECT * FROM new_retail_sales
) source
ON target.order_id = source.order_id
   AND target.source_channel = source.source_channel
WHEN MATCHED THEN UPDATE SET
    total_amount = source.total_amount,
    order_date = source.order_date,
    updated_at = CURRENT_TIMESTAMP
WHEN NOT MATCHED THEN INSERT VALUES (
    source.order_id,
    source.customer_id,
    source.order_date,
    source.total_amount,
    source.source_channel,
    CURRENT_TIMESTAMP
);

-- Update aggregation state
MERGE INTO aggregation_state target
USING (
    SELECT 'online_sales' AS source_name, CURRENT_TIMESTAMP AS last_aggregation_time
    UNION ALL
    SELECT 'retail_sales', CURRENT_TIMESTAMP
) source
ON target.source_name = source.source_name
WHEN MATCHED THEN UPDATE SET last_aggregation_time = source.last_aggregation_time
WHEN NOT MATCHED THEN INSERT VALUES (source.source_name, source.last_aggregation_time);
```

#### Pattern 4: Master Data Management (MDM)

Create golden records from multiple sources with conflict resolution.

**SQL Implementation:**

```sql
-- Define source priority and quality scores
CREATE OR REPLACE TABLE customer_mdm AS
WITH source_priority AS (
    SELECT 'crm' AS source, 1 AS priority, 95 AS quality_score
    UNION ALL SELECT 'salesforce', 2, 90
    UNION ALL SELECT 'marketing', 3, 85
    UNION ALL SELECT 'support', 4, 80
),
customer_sources AS (
    -- CRM source
    SELECT
        customer_id,
        email,
        phone,
        address,
        'crm' AS source
    FROM crm_customers

    UNION ALL

    -- Salesforce source
    SELECT
        account_id AS customer_id,
        email_address AS email,
        phone_number AS phone,
        billing_address AS address,
        'salesforce' AS source
    FROM salesforce_accounts

    UNION ALL

    -- Marketing platform
    SELECT
        contact_id AS customer_id,
        email,
        mobile AS phone,
        mailing_address AS address,
        'marketing' AS source
    FROM marketing_contacts
),
ranked_data AS (
    SELECT
        cs.*,
        sp.priority,
        sp.quality_score,
        -- Rank each attribute by source priority and data quality
        ROW_NUMBER() OVER (
            PARTITION BY cs.customer_id, 'email'
            ORDER BY sp.priority,
                     CASE WHEN cs.email IS NOT NULL THEN 0 ELSE 1 END
        ) AS email_rank,
        ROW_NUMBER() OVER (
            PARTITION BY cs.customer_id, 'phone'
            ORDER BY sp.priority,
                     CASE WHEN cs.phone IS NOT NULL THEN 0 ELSE 1 END
        ) AS phone_rank,
        ROW_NUMBER() OVER (
            PARTITION BY cs.customer_id, 'address'
            ORDER BY sp.priority,
                     CASE WHEN cs.address IS NOT NULL THEN 0 ELSE 1 END
        ) AS address_rank
    FROM customer_sources cs
    JOIN source_priority sp ON cs.source = sp.source
)
SELECT
    customer_id,
    MAX(CASE WHEN email_rank = 1 THEN email END) AS email,
    MAX(CASE WHEN phone_rank = 1 THEN phone END) AS phone,
    MAX(CASE WHEN address_rank = 1 THEN address END) AS address,
    CURRENT_TIMESTAMP AS last_updated,
    LISTAGG(DISTINCT source, ',') AS contributing_sources
FROM ranked_data
GROUP BY customer_id;
```

### Multi-Source Aggregation Best Practices

1. **Standardize identifiers** across sources early
2. **Implement data quality checks** before aggregation
3. **Track data lineage** to source systems
4. **Define conflict resolution rules** clearly
5. **Use incremental processing** where possible
6. **Monitor source data quality** continuously
7. **Document transformation logic** thoroughly
8. **Test edge cases** like missing data and duplicates

## Slowly Changing Dimensions (SCD)

SCDs track how dimension data changes over time, essential for historical analysis and point-in-time reporting.

### SCD Type Selection Guide

| Type | History | Storage | Complexity | Use Case |
|------|---------|---------|------------|----------|
| Type 0 | None | Minimal | Simple | Fixed attributes (birth date, SSN) |
| Type 1 | None | Minimal | Simple | Current values only (phone, address) |
| Type 2 | Full | High | Moderate | Full history (job title, pricing) |
| Type 3 | Limited | Low | Simple | Previous + current (prior address) |
| Type 4 | Full | High | Complex | Separate history table |
| Type 6 | Hybrid | High | Complex | Combination of 1+2+3 |

### SCD Pattern Implementations

#### Pattern 1: SCD Type 1 (Overwrite)

Simply overwrite old values with new ones. No history is maintained.

**SQL Implementation:**

```sql
-- SCD Type 1: Simple update
MERGE INTO dim_customer target
USING stage_customer source
ON target.customer_id = source.customer_id
WHEN MATCHED THEN UPDATE SET
    email = source.email,
    phone = source.phone,
    address = source.address,
    updated_at = CURRENT_TIMESTAMP
WHEN NOT MATCHED THEN INSERT (
    customer_id,
    email,
    phone,
    address,
    created_at,
    updated_at
) VALUES (
    source.customer_id,
    source.email,
    source.phone,
    source.address,
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP
);
```

**When to Use:**
- Historical values are not needed
- Storage optimization is important
- Corrections to incorrect data
- Attributes that change infrequently

#### Pattern 2: SCD Type 2 (Add New Row)

Create a new row for each change, maintaining full history.

**Table Structure:**

```sql
CREATE TABLE dim_customer (
    customer_key INT IDENTITY(1,1) PRIMARY KEY,  -- Surrogate key
    customer_id INT,                              -- Natural key
    email VARCHAR(255),
    phone VARCHAR(50),
    address VARCHAR(500),
    valid_from TIMESTAMP,
    valid_to TIMESTAMP,
    is_current BOOLEAN,
    version INT
);
```

**SQL Implementation:**

```sql
-- SCD Type 2: Full history tracking
MERGE INTO dim_customer target
USING (
    SELECT
        source.*,
        target.customer_key,
        target.valid_from AS current_valid_from,
        -- Check if any tracked columns changed
        CASE
            WHEN target.email <> source.email
              OR target.phone <> source.phone
              OR target.address <> source.address
            THEN TRUE
            ELSE FALSE
        END AS has_changes
    FROM stage_customer source
    LEFT JOIN dim_customer target
        ON source.customer_id = target.customer_id
       AND target.is_current = TRUE
) source
ON target.customer_key = source.customer_key
-- Close out old record
WHEN MATCHED AND source.has_changes THEN UPDATE SET
    valid_to = CURRENT_TIMESTAMP,
    is_current = FALSE
WHEN NOT MATCHED THEN INSERT (
    customer_id,
    email,
    phone,
    address,
    valid_from,
    valid_to,
    is_current,
    version
) VALUES (
    source.customer_id,
    source.email,
    source.phone,
    source.address,
    CURRENT_TIMESTAMP,
    '9999-12-31'::TIMESTAMP,
    TRUE,
    COALESCE((
        SELECT MAX(version) + 1
        FROM dim_customer
        WHERE customer_id = source.customer_id
    ), 1)
);

-- Insert new version for changed records
INSERT INTO dim_customer (
    customer_id,
    email,
    phone,
    address,
    valid_from,
    valid_to,
    is_current,
    version
)
SELECT
    source.customer_id,
    source.email,
    source.phone,
    source.address,
    CURRENT_TIMESTAMP,
    '9999-12-31'::TIMESTAMP,
    TRUE,
    COALESCE(source.version, 0) + 1
FROM stage_customer source
WHERE EXISTS (
    SELECT 1 FROM dim_customer target
    WHERE target.customer_id = source.customer_id
      AND target.is_current = FALSE
      AND target.valid_to = CURRENT_TIMESTAMP
);
```

**Querying SCD Type 2:**

```sql
-- Get current version
SELECT *
FROM dim_customer
WHERE is_current = TRUE;

-- Point-in-time query
SELECT *
FROM dim_customer
WHERE customer_id = 12345
  AND '2023-06-15'::DATE BETWEEN valid_from AND valid_to;

-- History of changes
SELECT
    customer_id,
    email,
    phone,
    valid_from,
    valid_to,
    version
FROM dim_customer
WHERE customer_id = 12345
ORDER BY version;
```

**When to Use:**
- Full audit trail required
- Regulatory compliance needs
- Historical analysis important
- Track changes in pricing, territories, managers

#### Pattern 3: SCD Type 3 (Add New Column)

Store limited history by adding columns for previous values.

**Table Structure:**

```sql
CREATE TABLE dim_customer (
    customer_key INT IDENTITY(1,1) PRIMARY KEY,
    customer_id INT,
    current_email VARCHAR(255),
    previous_email VARCHAR(255),
    current_address VARCHAR(500),
    previous_address VARCHAR(500),
    current_effective_date TIMESTAMP,
    previous_effective_date TIMESTAMP,
    updated_at TIMESTAMP
);
```

**SQL Implementation:**

```sql
-- SCD Type 3: Limited history
MERGE INTO dim_customer target
USING stage_customer source
ON target.customer_id = source.customer_id
WHEN MATCHED AND (
    target.current_email <> source.email
    OR target.current_address <> source.address
) THEN UPDATE SET
    previous_email = target.current_email,
    previous_address = target.current_address,
    previous_effective_date = target.current_effective_date,
    current_email = source.email,
    current_address = source.address,
    current_effective_date = CURRENT_TIMESTAMP,
    updated_at = CURRENT_TIMESTAMP
WHEN NOT MATCHED THEN INSERT (
    customer_id,
    current_email,
    current_address,
    current_effective_date,
    updated_at
) VALUES (
    source.customer_id,
    source.email,
    source.address,
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP
);
```

**When to Use:**
- Need to compare current vs. previous value
- Limited history is sufficient (e.g., previous address for shipping)
- Storage constraints exist
- Simplified queries preferred

#### Pattern 4: SCD Type 4 (History Table)

Maintain current data in main table, history in separate table.

**Table Structure:**

```sql
-- Current table
CREATE TABLE dim_customer_current (
    customer_key INT IDENTITY(1,1) PRIMARY KEY,
    customer_id INT UNIQUE,
    email VARCHAR(255),
    phone VARCHAR(50),
    address VARCHAR(500),
    updated_at TIMESTAMP
);

-- History table
CREATE TABLE dim_customer_history (
    history_key INT IDENTITY(1,1) PRIMARY KEY,
    customer_key INT,
    customer_id INT,
    email VARCHAR(255),
    phone VARCHAR(50),
    address VARCHAR(500),
    valid_from TIMESTAMP,
    valid_to TIMESTAMP,
    change_type VARCHAR(20)
);
```

**SQL Implementation:**

```sql
-- Insert changed records to history before updating
INSERT INTO dim_customer_history (
    customer_key,
    customer_id,
    email,
    phone,
    address,
    valid_from,
    valid_to,
    change_type
)
SELECT
    target.customer_key,
    target.customer_id,
    target.email,
    target.phone,
    target.address,
    target.updated_at,
    CURRENT_TIMESTAMP,
    'UPDATE'
FROM dim_customer_current target
JOIN stage_customer source ON target.customer_id = source.customer_id
WHERE target.email <> source.email
   OR target.phone <> source.phone
   OR target.address <> source.address;

-- Update current table
MERGE INTO dim_customer_current target
USING stage_customer source
ON target.customer_id = source.customer_id
WHEN MATCHED THEN UPDATE SET
    email = source.email,
    phone = source.phone,
    address = source.address,
    updated_at = CURRENT_TIMESTAMP
WHEN NOT MATCHED THEN INSERT (
    customer_id,
    email,
    phone,
    address,
    updated_at
) VALUES (
    source.customer_id,
    source.email,
    source.phone,
    source.address,
    CURRENT_TIMESTAMP
);
```

**When to Use:**
- Separate fast current lookups from historical analysis
- Different access patterns for current vs. historical
- Simplify queries on current data
- Large dimension with extensive history

### SCD Best Practices

1. **Choose the right type** based on business requirements
2. **Use surrogate keys** (not natural keys) in fact tables
3. **Index appropriately** for query patterns
4. **Consider performance** impact of Type 2 on joins
5. **Document business rules** for attribute changes
6. **Test edge cases** thoroughly
7. **Monitor table growth** for Type 2 dimensions
8. **Implement data quality checks** before SCD processing

## Star Schema Design

Star schema is the foundational dimensional modeling pattern for data warehouses, optimizing for query performance and business user understanding.

### Star Schema Components

A star schema consists of:
- **Fact Tables**: Contain measurements and foreign keys to dimensions
- **Dimension Tables**: Contain descriptive attributes
- **Relationships**: Denormalized for query simplicity

### Star Schema Pattern

#### Pattern 1: Basic Star Schema

**Dimension Tables:**

```sql
-- Date Dimension
CREATE TABLE dim_date (
    date_key INT PRIMARY KEY,
    date DATE,
    day_of_week VARCHAR(10),
    day_of_month INT,
    week_of_year INT,
    month INT,
    month_name VARCHAR(20),
    quarter INT,
    year INT,
    is_weekend BOOLEAN,
    is_holiday BOOLEAN,
    fiscal_period VARCHAR(20)
);

-- Customer Dimension
CREATE TABLE dim_customer (
    customer_key INT PRIMARY KEY,
    customer_id VARCHAR(50),
    customer_name VARCHAR(255),
    email VARCHAR(255),
    phone VARCHAR(50),
    segment VARCHAR(50),
    region VARCHAR(100),
    country VARCHAR(100),
    customer_since DATE,
    valid_from TIMESTAMP,
    valid_to TIMESTAMP,
    is_current BOOLEAN
);

-- Product Dimension
CREATE TABLE dim_product (
    product_key INT PRIMARY KEY,
    product_id VARCHAR(50),
    product_name VARCHAR(255),
    category VARCHAR(100),
    subcategory VARCHAR(100),
    brand VARCHAR(100),
    supplier VARCHAR(255),
    unit_price DECIMAL(10,2),
    valid_from TIMESTAMP,
    valid_to TIMESTAMP,
    is_current BOOLEAN
);

-- Sales Channel Dimension
CREATE TABLE dim_channel (
    channel_key INT PRIMARY KEY,
    channel_id VARCHAR(50),
    channel_name VARCHAR(100),
    channel_type VARCHAR(50),
    region VARCHAR(100)
);
```

**Fact Table:**

```sql
-- Sales Fact Table
CREATE TABLE fact_sales (
    sales_key BIGINT IDENTITY(1,1) PRIMARY KEY,
    date_key INT,
    customer_key INT,
    product_key INT,
    channel_key INT,
    -- Measures
    quantity INT,
    unit_price DECIMAL(10,2),
    discount_amount DECIMAL(10,2),
    sales_amount DECIMAL(10,2),
    cost_amount DECIMAL(10,2),
    profit_amount DECIMAL(10,2),
    tax_amount DECIMAL(10,2),
    -- Degenerate dimension (optional)
    order_number VARCHAR(50),
    line_number INT,
    -- Metadata
    created_at TIMESTAMP,
    -- Foreign keys
    FOREIGN KEY (date_key) REFERENCES dim_date(date_key),
    FOREIGN KEY (customer_key) REFERENCES dim_customer(customer_key),
    FOREIGN KEY (product_key) REFERENCES dim_product(product_key),
    FOREIGN KEY (channel_key) REFERENCES dim_channel(channel_key)
);
```

#### Pattern 2: Loading Dimension Tables

**Date Dimension Population:**

```sql
-- Populate date dimension for 10 years
INSERT INTO dim_date
WITH date_range AS (
    SELECT
        DATEADD(day, ROW_NUMBER() OVER (ORDER BY NULL) - 1, '2020-01-01'::DATE) AS date
    FROM TABLE(GENERATOR(ROWCOUNT => 3650))
)
SELECT
    TO_NUMBER(TO_CHAR(date, 'YYYYMMDD')) AS date_key,
    date,
    DAYNAME(date) AS day_of_week,
    DAYOFMONTH(date) AS day_of_month,
    WEEKOFYEAR(date) AS week_of_year,
    MONTH(date) AS month,
    MONTHNAME(date) AS month_name,
    QUARTER(date) AS quarter,
    YEAR(date) AS year,
    CASE WHEN DAYOFWEEK(date) IN (0, 6) THEN TRUE ELSE FALSE END AS is_weekend,
    FALSE AS is_holiday,
    'P' || CEIL(MONTH(date) / 3) || ' ' || YEAR(date) AS fiscal_period
FROM date_range;

-- Mark holidays
UPDATE dim_date
SET is_holiday = TRUE
WHERE (month = 12 AND day_of_month = 25) -- Christmas
   OR (month = 1 AND day_of_month = 1)   -- New Year
   OR (month = 7 AND day_of_month = 4);  -- Independence Day (US)
```

**Customer Dimension Load:**

```sql
-- Load customer dimension with SCD Type 2
MERGE INTO dim_customer target
USING (
    SELECT
        source.*,
        target.customer_key,
        CASE
            WHEN target.customer_name <> source.customer_name
              OR target.email <> source.email
              OR target.segment <> source.segment
            THEN TRUE
            ELSE FALSE
        END AS has_changes
    FROM stage_customers source
    LEFT JOIN dim_customer target
        ON source.customer_id = target.customer_id
       AND target.is_current = TRUE
) source
ON target.customer_key = source.customer_key
WHEN MATCHED AND source.has_changes THEN UPDATE SET
    valid_to = CURRENT_TIMESTAMP,
    is_current = FALSE;

-- Insert new versions
INSERT INTO dim_customer (
    customer_id,
    customer_name,
    email,
    phone,
    segment,
    region,
    country,
    customer_since,
    valid_from,
    valid_to,
    is_current
)
SELECT
    customer_id,
    customer_name,
    email,
    phone,
    segment,
    region,
    country,
    customer_since,
    CURRENT_TIMESTAMP,
    '9999-12-31'::TIMESTAMP,
    TRUE
FROM stage_customers source
WHERE NOT EXISTS (
    SELECT 1 FROM dim_customer target
    WHERE target.customer_id = source.customer_id
      AND target.is_current = TRUE
      AND target.customer_name = source.customer_name
      AND target.email = source.email
      AND target.segment = source.segment
);
```

#### Pattern 3: Loading Fact Tables

**Incremental Fact Load:**

```sql
-- Load fact table with dimension lookups
INSERT INTO fact_sales (
    date_key,
    customer_key,
    product_key,
    channel_key,
    quantity,
    unit_price,
    discount_amount,
    sales_amount,
    cost_amount,
    profit_amount,
    tax_amount,
    order_number,
    line_number,
    created_at
)
SELECT
    -- Dimension key lookups
    dd.date_key,
    dc.customer_key,
    dp.product_key,
    dch.channel_key,

    -- Measures
    s.quantity,
    s.unit_price,
    s.discount_amount,
    s.quantity * s.unit_price - s.discount_amount AS sales_amount,
    s.quantity * p.cost_price AS cost_amount,
    (s.quantity * s.unit_price - s.discount_amount) -
        (s.quantity * p.cost_price) AS profit_amount,
    s.tax_amount,

    -- Degenerate dimension
    s.order_number,
    s.line_number,

    -- Metadata
    CURRENT_TIMESTAMP

FROM stage_sales s

-- Join to dimensions
JOIN dim_date dd
    ON s.sale_date = dd.date

JOIN dim_customer dc
    ON s.customer_id = dc.customer_id
   AND s.sale_date BETWEEN dc.valid_from AND dc.valid_to
   AND dc.is_current = TRUE

JOIN dim_product dp
    ON s.product_id = dp.product_id
   AND s.sale_date BETWEEN dp.valid_from AND dp.valid_to
   AND dp.is_current = TRUE

JOIN dim_channel dch
    ON s.channel_id = dch.channel_id

JOIN products p
    ON s.product_id = p.product_id

-- Only load new records
WHERE NOT EXISTS (
    SELECT 1 FROM fact_sales f
    WHERE f.order_number = s.order_number
      AND f.line_number = s.line_number
);
```

#### Pattern 4: Analytics Queries on Star Schema

**Simple Aggregation:**

```sql
-- Total sales by product category and quarter
SELECT
    dp.category,
    dd.year,
    dd.quarter,
    SUM(fs.sales_amount) AS total_sales,
    SUM(fs.quantity) AS total_quantity,
    SUM(fs.profit_amount) AS total_profit,
    COUNT(DISTINCT fs.order_number) AS order_count
FROM fact_sales fs
JOIN dim_product dp ON fs.product_key = dp.product_key
JOIN dim_date dd ON fs.date_key = dd.date_key
WHERE dd.year = 2024
GROUP BY dp.category, dd.year, dd.quarter
ORDER BY dp.category, dd.quarter;
```

**Multi-Dimensional Analysis:**

```sql
-- Sales performance by customer segment, region, and product category
SELECT
    dc.segment AS customer_segment,
    dc.region AS customer_region,
    dp.category AS product_category,
    dd.year,
    dd.month_name,

    -- Aggregated measures
    COUNT(DISTINCT fs.order_number) AS order_count,
    COUNT(*) AS line_item_count,
    SUM(fs.quantity) AS units_sold,
    SUM(fs.sales_amount) AS gross_sales,
    SUM(fs.discount_amount) AS total_discounts,
    SUM(fs.sales_amount - fs.discount_amount) AS net_sales,
    SUM(fs.cost_amount) AS total_cost,
    SUM(fs.profit_amount) AS total_profit,
    ROUND(100.0 * SUM(fs.profit_amount) / NULLIF(SUM(fs.sales_amount), 0), 2) AS profit_margin_pct,
    ROUND(AVG(fs.sales_amount), 2) AS avg_line_value

FROM fact_sales fs
JOIN dim_customer dc ON fs.customer_key = dc.customer_key
JOIN dim_product dp ON fs.product_key = dp.product_key
JOIN dim_date dd ON fs.date_key = dd.date_key
JOIN dim_channel dch ON fs.channel_key = dch.channel_key

WHERE dd.year >= 2023
  AND dc.is_current = TRUE
  AND dp.is_current = TRUE

GROUP BY
    dc.segment,
    dc.region,
    dp.category,
    dd.year,
    dd.month_name

HAVING SUM(fs.sales_amount) > 10000

ORDER BY
    dd.year DESC,
    net_sales DESC;
```

#### Pattern 5: Handling Late-Arriving Facts

When fact records arrive after dimensions have been updated:

```sql
-- Handle late-arriving facts with point-in-time dimension lookup
INSERT INTO fact_sales (
    date_key,
    customer_key,
    product_key,
    channel_key,
    quantity,
    unit_price,
    sales_amount,
    order_number,
    line_number
)
SELECT
    dd.date_key,
    -- Use point-in-time lookup for SCD Type 2 dimensions
    dc.customer_key,
    dp.product_key,
    dch.channel_key,
    s.quantity,
    s.unit_price,
    s.sales_amount,
    s.order_number,
    s.line_number
FROM stage_late_sales s
JOIN dim_date dd ON s.sale_date = dd.date
-- Point-in-time lookup: dimension as it was on sale_date
JOIN dim_customer dc
    ON s.customer_id = dc.customer_id
   AND s.sale_date BETWEEN dc.valid_from AND dc.valid_to
JOIN dim_product dp
    ON s.product_id = dp.product_id
   AND s.sale_date BETWEEN dp.valid_from AND dp.valid_to
JOIN dim_channel dch ON s.channel_id = dch.channel_id;
```

### Star Schema Best Practices

1. **Use surrogate keys** for all dimension tables
2. **Denormalize dimensions** for query simplicity
3. **Implement SCD Type 2** for slowly changing attributes
4. **Separate dimensions and facts** clearly
5. **Pre-calculate measures** where appropriate
6. **Index foreign keys** in fact tables
7. **Partition large fact tables** by date
8. **Maintain conformed dimensions** across fact tables
9. **Document grain** of each fact table clearly
10. **Test query performance** with realistic data volumes

## Conclusion

These data engineering patterns provide a foundation for building robust, scalable, and maintainable data pipelines. The key to success is:

1. **Choose the right pattern** for your specific use case
2. **Start simple** and evolve as requirements grow
3. **Document thoroughly** for maintainability
4. **Monitor continuously** for performance and quality
5. **Test comprehensively** before production deployment
6. **Iterate and improve** based on real-world usage

Remember that patterns are guidelines, not rigid rules. Adapt them to your organization's specific needs, data characteristics, and technical constraints.

### Key Takeaways

- **Incremental loading** saves costs and improves efficiency
- **Full loads** are simpler but should be used judiciously
- **CDC patterns** enable real-time data synchronization
- **Data quality checks** prevent bad data from propagating
- **Error handling** ensures pipeline reliability
- **Pipeline design** should balance simplicity and efficiency
- **Multi-source aggregation** creates unified views
- **SCD patterns** preserve history appropriately
- **Star schema** optimizes for analytics and reporting

By mastering these patterns, you'll be well-equipped to design and implement enterprise-grade data engineering solutions.
