# Keboola Practical Examples Guide

A comprehensive guide with complete, working examples for common Keboola use cases.

## Table of Contents

1. [Simple ETL Pipeline](#1-simple-etl-pipeline)
2. [Marketing Analytics Workflow](#2-marketing-analytics-workflow)
3. [E-Commerce Reporting](#3-e-commerce-reporting)
4. [Data Quality Checks](#4-data-quality-checks)
5. [Incremental Processing](#5-incremental-processing)
6. [Multi-Source Data Aggregation](#6-multi-source-data-aggregation)

---

## 1. Simple ETL Pipeline

### Overview
A basic ETL pipeline that extracts data from a CSV source, transforms it using SQL, and loads it into a destination table.

### Use Case
Extract customer data, clean it, and prepare it for analytics by standardizing fields and filtering invalid records.

### Configuration JSON

```json
{
  "storage": {
    "input": {
      "tables": [
        {
          "source": "in.c-raw-data.customers",
          "destination": "customers_raw.csv",
          "columns": ["customer_id", "name", "email", "created_at", "country"]
        }
      ]
    },
    "output": {
      "tables": [
        {
          "source": "customers_clean.csv",
          "destination": "out.c-analytics.customers",
          "incremental": false,
          "delete_where_column": "",
          "delete_where_values": [],
          "delete_where_operator": "eq",
          "primary_key": ["customer_id"]
        }
      ]
    }
  },
  "parameters": {
    "blocks": [
      {
        "name": "clean-customers",
        "codes": [
          {
            "name": "Clean and Transform",
            "script": [
              "SELECT",
              "  CAST(customer_id AS INTEGER) AS customer_id,",
              "  UPPER(TRIM(name)) AS customer_name,",
              "  LOWER(TRIM(email)) AS email,",
              "  DATE(created_at) AS registration_date,",
              "  UPPER(TRIM(country)) AS country_code",
              "FROM customers_raw",
              "WHERE email IS NOT NULL",
              "  AND email LIKE '%@%'",
              "  AND LENGTH(name) > 0",
              "ORDER BY customer_id;"
            ]
          }
        ]
      }
    ]
  }
}
```

### Explanation

**Input Configuration:**
- Source table: `in.c-raw-data.customers` from Storage
- Maps to local file: `customers_raw.csv`
- Selects specific columns to work with

**Transformation Logic:**
- Casts `customer_id` to integer for consistency
- Standardizes name to uppercase and removes whitespace
- Standardizes email to lowercase
- Converts timestamp to date format
- Filters out invalid records (null emails, missing names)
- Validates email format with basic pattern matching

**Output Configuration:**
- Writes to: `out.c-analytics.customers` in Storage
- Sets `incremental: false` to replace all data on each run
- Defines `customer_id` as primary key for data integrity

**Workflow:**
1. Extract raw customer data from Storage
2. Clean and standardize all fields
3. Validate data quality (email format, required fields)
4. Load cleaned data back to Storage

---

## 2. Marketing Analytics Workflow

### Overview
Combines marketing campaign data with conversion events to calculate campaign performance metrics including ROI, conversion rates, and customer acquisition costs.

### Use Case
Marketing team needs daily reports showing which campaigns are performing best, with metrics on spend, conversions, and revenue generated.

### Configuration JSON

```json
{
  "storage": {
    "input": {
      "tables": [
        {
          "source": "in.c-marketing.campaigns",
          "destination": "campaigns.csv",
          "columns": ["campaign_id", "campaign_name", "channel", "spend", "date"]
        },
        {
          "source": "in.c-marketing.conversions",
          "destination": "conversions.csv",
          "columns": ["conversion_id", "campaign_id", "user_id", "revenue", "conversion_date"]
        },
        {
          "source": "in.c-marketing.impressions",
          "destination": "impressions.csv",
          "columns": ["campaign_id", "date", "impressions", "clicks"]
        }
      ]
    },
    "output": {
      "tables": [
        {
          "source": "campaign_performance.csv",
          "destination": "out.c-analytics.campaign_performance",
          "incremental": true,
          "delete_where_column": "report_date",
          "delete_where_values": ["{{ date }}"],
          "delete_where_operator": "eq",
          "primary_key": ["campaign_id", "report_date"]
        }
      ]
    }
  },
  "parameters": {
    "blocks": [
      {
        "name": "calculate-campaign-metrics",
        "codes": [
          {
            "name": "Aggregate Campaign Data",
            "script": [
              "CREATE TABLE campaign_base AS",
              "SELECT",
              "  c.campaign_id,",
              "  c.campaign_name,",
              "  c.channel,",
              "  c.date AS report_date,",
              "  CAST(c.spend AS DECIMAL(10,2)) AS total_spend",
              "FROM campaigns c;"
            ]
          },
          {
            "name": "Calculate Conversions",
            "script": [
              "CREATE TABLE campaign_conversions AS",
              "SELECT",
              "  campaign_id,",
              "  conversion_date AS report_date,",
              "  COUNT(DISTINCT conversion_id) AS total_conversions,",
              "  COUNT(DISTINCT user_id) AS unique_customers,",
              "  CAST(SUM(revenue) AS DECIMAL(10,2)) AS total_revenue",
              "FROM conversions",
              "GROUP BY campaign_id, conversion_date;"
            ]
          },
          {
            "name": "Add Impression Data",
            "script": [
              "CREATE TABLE campaign_impressions AS",
              "SELECT",
              "  campaign_id,",
              "  date AS report_date,",
              "  SUM(impressions) AS total_impressions,",
              "  SUM(clicks) AS total_clicks",
              "FROM impressions",
              "GROUP BY campaign_id, date;"
            ]
          },
          {
            "name": "Calculate Final Metrics",
            "script": [
              "SELECT",
              "  cb.campaign_id,",
              "  cb.campaign_name,",
              "  cb.channel,",
              "  cb.report_date,",
              "  cb.total_spend,",
              "  COALESCE(ci.total_impressions, 0) AS impressions,",
              "  COALESCE(ci.total_clicks, 0) AS clicks,",
              "  COALESCE(cc.total_conversions, 0) AS conversions,",
              "  COALESCE(cc.unique_customers, 0) AS customers,",
              "  COALESCE(cc.total_revenue, 0.00) AS revenue,",
              "  CASE",
              "    WHEN ci.total_impressions > 0",
              "    THEN ROUND(CAST(ci.total_clicks AS DECIMAL) / ci.total_impressions * 100, 2)",
              "    ELSE 0",
              "  END AS ctr_percent,",
              "  CASE",
              "    WHEN ci.total_clicks > 0",
              "    THEN ROUND(CAST(cc.total_conversions AS DECIMAL) / ci.total_clicks * 100, 2)",
              "    ELSE 0",
              "  END AS conversion_rate_percent,",
              "  CASE",
              "    WHEN cc.unique_customers > 0",
              "    THEN ROUND(cb.total_spend / cc.unique_customers, 2)",
              "    ELSE 0",
              "  END AS cac,",
              "  CASE",
              "    WHEN cb.total_spend > 0",
              "    THEN ROUND((cc.total_revenue - cb.total_spend) / cb.total_spend * 100, 2)",
              "    ELSE 0",
              "  END AS roi_percent",
              "FROM campaign_base cb",
              "LEFT JOIN campaign_impressions ci",
              "  ON cb.campaign_id = ci.campaign_id",
              "  AND cb.report_date = ci.report_date",
              "LEFT JOIN campaign_conversions cc",
              "  ON cb.campaign_id = cc.campaign_id",
              "  AND cb.report_date = cc.report_date",
              "ORDER BY cb.report_date DESC, cb.campaign_id;"
            ]
          }
        ]
      }
    ]
  }
}
```

### Explanation

**Input Configuration:**
- **Campaigns table**: Contains spend data per campaign per day
- **Conversions table**: Individual conversion events with revenue
- **Impressions table**: Ad performance metrics (impressions and clicks)

**Transformation Steps:**

1. **Campaign Base**: Prepares core campaign information with spend data
2. **Conversions Aggregation**: Groups conversions by campaign and date, calculating unique customers and total revenue
3. **Impressions Aggregation**: Sums up impression and click data by campaign and date
4. **Final Metrics Calculation**:
   - **CTR (Click-Through Rate)**: (Clicks / Impressions) × 100
   - **Conversion Rate**: (Conversions / Clicks) × 100
   - **CAC (Customer Acquisition Cost)**: Total Spend / Unique Customers
   - **ROI**: ((Revenue - Spend) / Spend) × 100

**Output Configuration:**
- Uses incremental loading with date-based replacement
- Deletes existing data for the current date before inserting
- Primary key ensures no duplicate records per campaign per day
- Enables historical tracking while updating today's metrics

**Benefits:**
- Combines multiple data sources into unified reporting
- Calculates industry-standard marketing metrics
- Handles missing data gracefully with COALESCE
- Prevents division by zero errors
- Maintains historical data with incremental updates

---

## 3. E-Commerce Reporting

### Overview
Comprehensive e-commerce reporting that combines orders, products, and customer data to generate daily sales analytics with product performance metrics.

### Use Case
Daily executive dashboard showing revenue, order volume, average order value, top products, and customer segments.

### Configuration JSON

```json
{
  "storage": {
    "input": {
      "tables": [
        {
          "source": "in.c-ecommerce.orders",
          "destination": "orders.csv",
          "columns": ["order_id", "customer_id", "order_date", "total_amount", "status", "payment_method"],
          "where_column": "order_date",
          "where_values": ["{{ date }}"],
          "where_operator": "eq"
        },
        {
          "source": "in.c-ecommerce.order_items",
          "destination": "order_items.csv",
          "columns": ["order_item_id", "order_id", "product_id", "quantity", "unit_price", "discount"]
        },
        {
          "source": "in.c-ecommerce.products",
          "destination": "products.csv",
          "columns": ["product_id", "product_name", "category", "brand", "cost"]
        },
        {
          "source": "in.c-ecommerce.customers",
          "destination": "customers.csv",
          "columns": ["customer_id", "customer_name", "segment", "country", "first_order_date"]
        }
      ]
    },
    "output": {
      "tables": [
        {
          "source": "daily_sales_summary.csv",
          "destination": "out.c-reports.daily_sales_summary",
          "incremental": true,
          "delete_where_column": "report_date",
          "delete_where_values": ["{{ date }}"],
          "delete_where_operator": "eq",
          "primary_key": ["report_date"]
        },
        {
          "source": "product_performance.csv",
          "destination": "out.c-reports.product_performance",
          "incremental": true,
          "delete_where_column": "report_date",
          "delete_where_values": ["{{ date }}"],
          "delete_where_operator": "eq",
          "primary_key": ["report_date", "product_id"]
        },
        {
          "source": "customer_segment_analysis.csv",
          "destination": "out.c-reports.customer_segment_analysis",
          "incremental": true,
          "delete_where_column": "report_date",
          "delete_where_values": ["{{ date }}"],
          "delete_where_operator": "eq",
          "primary_key": ["report_date", "segment"]
        }
      ]
    }
  },
  "parameters": {
    "blocks": [
      {
        "name": "daily-sales-summary",
        "codes": [
          {
            "name": "Calculate Daily Metrics",
            "script": [
              "SELECT",
              "  DATE('{{ date }}') AS report_date,",
              "  COUNT(DISTINCT order_id) AS total_orders,",
              "  COUNT(DISTINCT customer_id) AS unique_customers,",
              "  CAST(SUM(total_amount) AS DECIMAL(12,2)) AS total_revenue,",
              "  CAST(AVG(total_amount) AS DECIMAL(10,2)) AS avg_order_value,",
              "  COUNT(DISTINCT CASE WHEN status = 'completed' THEN order_id END) AS completed_orders,",
              "  COUNT(DISTINCT CASE WHEN status = 'cancelled' THEN order_id END) AS cancelled_orders,",
              "  ROUND(CAST(COUNT(DISTINCT CASE WHEN status = 'completed' THEN order_id END) AS DECIMAL)",
              "    / NULLIF(COUNT(DISTINCT order_id), 0) * 100, 2) AS completion_rate_percent",
              "FROM orders",
              "WHERE status IN ('completed', 'cancelled', 'pending');"
            ]
          }
        ]
      },
      {
        "name": "product-performance",
        "codes": [
          {
            "name": "Join Order Items with Products",
            "script": [
              "CREATE TABLE order_products AS",
              "SELECT",
              "  oi.product_id,",
              "  p.product_name,",
              "  p.category,",
              "  p.brand,",
              "  oi.quantity,",
              "  oi.unit_price,",
              "  oi.discount,",
              "  p.cost,",
              "  o.order_id,",
              "  o.status",
              "FROM order_items oi",
              "JOIN orders o ON oi.order_id = o.order_id",
              "JOIN products p ON oi.product_id = p.product_id",
              "WHERE o.status = 'completed';"
            ]
          },
          {
            "name": "Calculate Product Metrics",
            "script": [
              "SELECT",
              "  DATE('{{ date }}') AS report_date,",
              "  product_id,",
              "  product_name,",
              "  category,",
              "  brand,",
              "  COUNT(DISTINCT order_id) AS orders_count,",
              "  SUM(quantity) AS units_sold,",
              "  CAST(SUM(quantity * unit_price) AS DECIMAL(12,2)) AS gross_revenue,",
              "  CAST(SUM(discount) AS DECIMAL(10,2)) AS total_discounts,",
              "  CAST(SUM(quantity * unit_price - discount) AS DECIMAL(12,2)) AS net_revenue,",
              "  CAST(SUM(quantity * cost) AS DECIMAL(12,2)) AS total_cost,",
              "  CAST(SUM(quantity * unit_price - discount - quantity * cost) AS DECIMAL(12,2)) AS gross_profit,",
              "  CASE",
              "    WHEN SUM(quantity * unit_price - discount) > 0",
              "    THEN ROUND((SUM(quantity * unit_price - discount - quantity * cost)",
              "      / SUM(quantity * unit_price - discount)) * 100, 2)",
              "    ELSE 0",
              "  END AS margin_percent",
              "FROM order_products",
              "GROUP BY product_id, product_name, category, brand",
              "ORDER BY net_revenue DESC;"
            ]
          }
        ]
      },
      {
        "name": "customer-segment-analysis",
        "codes": [
          {
            "name": "Segment Performance",
            "script": [
              "SELECT",
              "  DATE('{{ date }}') AS report_date,",
              "  c.segment,",
              "  COUNT(DISTINCT o.order_id) AS total_orders,",
              "  COUNT(DISTINCT o.customer_id) AS active_customers,",
              "  CAST(SUM(o.total_amount) AS DECIMAL(12,2)) AS segment_revenue,",
              "  CAST(AVG(o.total_amount) AS DECIMAL(10,2)) AS avg_order_value,",
              "  ROUND(CAST(COUNT(DISTINCT o.order_id) AS DECIMAL)",
              "    / NULLIF(COUNT(DISTINCT o.customer_id), 0), 2) AS orders_per_customer,",
              "  COUNT(DISTINCT CASE",
              "    WHEN DATE(c.first_order_date) = DATE('{{ date }}')",
              "    THEN o.customer_id END) AS new_customers",
              "FROM orders o",
              "JOIN customers c ON o.customer_id = c.customer_id",
              "WHERE o.status = 'completed'",
              "GROUP BY c.segment",
              "ORDER BY segment_revenue DESC;"
            ]
          }
        ]
      }
    ]
  }
}
```

### Explanation

**Input Configuration:**
- **Orders**: Filtered by date parameter for daily processing
- **Order Items**: Line-level transaction details
- **Products**: Product master data with costs
- **Customers**: Customer demographics and segmentation

**Three Output Tables:**

1. **Daily Sales Summary**:
   - High-level KPIs: revenue, order volume, AOV
   - Completion and cancellation rates
   - Single row per day for executive dashboards

2. **Product Performance**:
   - Revenue and profit by product
   - Margin analysis
   - Units sold and order frequency
   - Multiple rows (one per product per day)

3. **Customer Segment Analysis**:
   - Performance by customer segment
   - Orders per customer metric
   - New customer acquisition tracking
   - Multiple rows (one per segment per day)

**Key Calculations:**
- **Gross Revenue**: Sum of (Quantity × Unit Price)
- **Net Revenue**: Gross Revenue - Discounts
- **Gross Profit**: Net Revenue - (Quantity × Cost)
- **Margin %**: (Gross Profit / Net Revenue) × 100
- **Orders per Customer**: Total Orders / Unique Customers

**Advanced Features:**
- Parameter substitution with `{{ date }}` for dynamic filtering
- NULLIF to prevent division by zero
- CASE expressions for conditional aggregations
- Incremental loading with date-based replacement
- Multi-table output for different analytical needs

---

## 4. Data Quality Checks

### Overview
Automated data quality validation that checks for common issues like nulls, duplicates, format violations, and referential integrity problems.

### Use Case
Run daily quality checks on incoming data before it flows to downstream analytics, generating a quality report and flagging problematic records.

### Configuration JSON

```json
{
  "storage": {
    "input": {
      "tables": [
        {
          "source": "in.c-raw.customer_data",
          "destination": "customer_data.csv"
        },
        {
          "source": "in.c-raw.transaction_data",
          "destination": "transaction_data.csv"
        }
      ]
    },
    "output": {
      "tables": [
        {
          "source": "quality_report.csv",
          "destination": "out.c-quality.daily_quality_report",
          "incremental": true,
          "delete_where_column": "check_date",
          "delete_where_values": ["{{ date }}"],
          "delete_where_operator": "eq",
          "primary_key": ["check_date", "table_name", "check_name"]
        },
        {
          "source": "failed_records.csv",
          "destination": "out.c-quality.failed_records",
          "incremental": true,
          "delete_where_column": "check_date",
          "delete_where_values": ["{{ date }}"],
          "delete_where_operator": "eq",
          "primary_key": ["check_date", "record_id", "check_name"]
        },
        {
          "source": "clean_customers.csv",
          "destination": "out.c-clean.customer_data",
          "incremental": false,
          "primary_key": ["customer_id"]
        }
      ]
    }
  },
  "parameters": {
    "blocks": [
      {
        "name": "validate-customer-data",
        "codes": [
          {
            "name": "Null Checks",
            "script": [
              "CREATE TABLE null_check AS",
              "SELECT",
              "  DATE('{{ date }}') AS check_date,",
              "  'customer_data' AS table_name,",
              "  'null_check' AS check_name,",
              "  'customer_id' AS column_name,",
              "  COUNT(*) AS failed_count,",
              "  ROUND(CAST(COUNT(*) AS DECIMAL) / (SELECT COUNT(*) FROM customer_data) * 100, 2) AS failure_rate_percent",
              "FROM customer_data",
              "WHERE customer_id IS NULL",
              "UNION ALL",
              "SELECT",
              "  DATE('{{ date }}'),",
              "  'customer_data',",
              "  'null_check',",
              "  'email',",
              "  COUNT(*),",
              "  ROUND(CAST(COUNT(*) AS DECIMAL) / (SELECT COUNT(*) FROM customer_data) * 100, 2)",
              "FROM customer_data",
              "WHERE email IS NULL",
              "UNION ALL",
              "SELECT",
              "  DATE('{{ date }}'),",
              "  'customer_data',",
              "  'null_check',",
              "  'created_at',",
              "  COUNT(*),",
              "  ROUND(CAST(COUNT(*) AS DECIMAL) / (SELECT COUNT(*) FROM customer_data) * 100, 2)",
              "FROM customer_data",
              "WHERE created_at IS NULL;"
            ]
          },
          {
            "name": "Duplicate Checks",
            "script": [
              "CREATE TABLE duplicate_check AS",
              "SELECT",
              "  DATE('{{ date }}') AS check_date,",
              "  'customer_data' AS table_name,",
              "  'duplicate_check' AS check_name,",
              "  'customer_id' AS column_name,",
              "  COUNT(*) - COUNT(DISTINCT customer_id) AS failed_count,",
              "  ROUND((CAST(COUNT(*) - COUNT(DISTINCT customer_id) AS DECIMAL)",
              "    / NULLIF(COUNT(*), 0)) * 100, 2) AS failure_rate_percent",
              "FROM customer_data",
              "UNION ALL",
              "SELECT",
              "  DATE('{{ date }}'),",
              "  'customer_data',",
              "  'duplicate_check',",
              "  'email',",
              "  COUNT(*) - COUNT(DISTINCT email),",
              "  ROUND((CAST(COUNT(*) - COUNT(DISTINCT email) AS DECIMAL)",
              "    / NULLIF(COUNT(*), 0)) * 100, 2)",
              "FROM customer_data",
              "WHERE email IS NOT NULL;"
            ]
          },
          {
            "name": "Format Validation",
            "script": [
              "CREATE TABLE format_check AS",
              "SELECT",
              "  DATE('{{ date }}') AS check_date,",
              "  'customer_data' AS table_name,",
              "  'format_validation' AS check_name,",
              "  'email_format' AS column_name,",
              "  COUNT(*) AS failed_count,",
              "  ROUND(CAST(COUNT(*) AS DECIMAL) / (SELECT COUNT(*) FROM customer_data) * 100, 2) AS failure_rate_percent",
              "FROM customer_data",
              "WHERE email IS NOT NULL",
              "  AND (email NOT LIKE '%@%'",
              "    OR email NOT LIKE '%.%'",
              "    OR LENGTH(email) < 5)",
              "UNION ALL",
              "SELECT",
              "  DATE('{{ date }}'),",
              "  'customer_data',",
              "  'format_validation',",
              "  'phone_format',",
              "  COUNT(*),",
              "  ROUND(CAST(COUNT(*) AS DECIMAL) / (SELECT COUNT(*) FROM customer_data) * 100, 2)",
              "FROM customer_data",
              "WHERE phone IS NOT NULL",
              "  AND (LENGTH(REPLACE(REPLACE(REPLACE(phone, '-', ''), ' ', ''), '+', '')) < 10",
              "    OR LENGTH(REPLACE(REPLACE(REPLACE(phone, '-', ''), ' ', ''), '+', '')) > 15);"
            ]
          },
          {
            "name": "Range Checks",
            "script": [
              "CREATE TABLE range_check AS",
              "SELECT",
              "  DATE('{{ date }}') AS check_date,",
              "  'customer_data' AS table_name,",
              "  'range_check' AS check_name,",
              "  'future_dates' AS column_name,",
              "  COUNT(*) AS failed_count,",
              "  ROUND(CAST(COUNT(*) AS DECIMAL) / (SELECT COUNT(*) FROM customer_data) * 100, 2) AS failure_rate_percent",
              "FROM customer_data",
              "WHERE created_at > CURRENT_DATE",
              "UNION ALL",
              "SELECT",
              "  DATE('{{ date }}'),",
              "  'customer_data',",
              "  'range_check',",
              "  'ancient_dates',",
              "  COUNT(*),",
              "  ROUND(CAST(COUNT(*) AS DECIMAL) / (SELECT COUNT(*) FROM customer_data) * 100, 2)",
              "FROM customer_data",
              "WHERE created_at < '1900-01-01';"
            ]
          }
        ]
      },
      {
        "name": "validate-transactions",
        "codes": [
          {
            "name": "Referential Integrity",
            "script": [
              "CREATE TABLE referential_check AS",
              "SELECT",
              "  DATE('{{ date }}') AS check_date,",
              "  'transaction_data' AS table_name,",
              "  'referential_integrity' AS check_name,",
              "  'orphan_transactions' AS column_name,",
              "  COUNT(*) AS failed_count,",
              "  ROUND(CAST(COUNT(*) AS DECIMAL) / (SELECT COUNT(*) FROM transaction_data) * 100, 2) AS failure_rate_percent",
              "FROM transaction_data t",
              "LEFT JOIN customer_data c ON t.customer_id = c.customer_id",
              "WHERE c.customer_id IS NULL;"
            ]
          },
          {
            "name": "Business Logic Validation",
            "script": [
              "CREATE TABLE business_logic_check AS",
              "SELECT",
              "  DATE('{{ date }}') AS check_date,",
              "  'transaction_data' AS table_name,",
              "  'business_logic' AS check_name,",
              "  'negative_amounts' AS column_name,",
              "  COUNT(*) AS failed_count,",
              "  ROUND(CAST(COUNT(*) AS DECIMAL) / (SELECT COUNT(*) FROM transaction_data) * 100, 2) AS failure_rate_percent",
              "FROM transaction_data",
              "WHERE amount < 0",
              "UNION ALL",
              "SELECT",
              "  DATE('{{ date }}'),",
              "  'transaction_data',",
              "  'business_logic',",
              "  'excessive_amounts',",
              "  COUNT(*),",
              "  ROUND(CAST(COUNT(*) AS DECIMAL) / (SELECT COUNT(*) FROM transaction_data) * 100, 2)",
              "FROM transaction_data",
              "WHERE amount > 1000000;"
            ]
          }
        ]
      },
      {
        "name": "generate-reports",
        "codes": [
          {
            "name": "Consolidate Quality Report",
            "script": [
              "SELECT * FROM null_check",
              "WHERE failed_count > 0",
              "UNION ALL",
              "SELECT * FROM duplicate_check",
              "WHERE failed_count > 0",
              "UNION ALL",
              "SELECT * FROM format_check",
              "WHERE failed_count > 0",
              "UNION ALL",
              "SELECT * FROM range_check",
              "WHERE failed_count > 0",
              "UNION ALL",
              "SELECT * FROM referential_check",
              "WHERE failed_count > 0",
              "UNION ALL",
              "SELECT * FROM business_logic_check",
              "WHERE failed_count > 0",
              "ORDER BY table_name, check_name, column_name;"
            ]
          }
        ]
      },
      {
        "name": "extract-failed-records",
        "codes": [
          {
            "name": "Capture Failed Customer Records",
            "script": [
              "SELECT",
              "  DATE('{{ date }}') AS check_date,",
              "  customer_id AS record_id,",
              "  'null_email' AS check_name,",
              "  'customer_data' AS table_name,",
              "  'Email is required but missing' AS failure_reason",
              "FROM customer_data",
              "WHERE email IS NULL",
              "UNION ALL",
              "SELECT",
              "  DATE('{{ date }}'),",
              "  customer_id,",
              "  'invalid_email_format',",
              "  'customer_data',",
              "  'Email format is invalid: ' || COALESCE(email, 'NULL')",
              "FROM customer_data",
              "WHERE email IS NOT NULL",
              "  AND (email NOT LIKE '%@%' OR email NOT LIKE '%.%')",
              "UNION ALL",
              "SELECT",
              "  DATE('{{ date }}'),",
              "  customer_id,",
              "  'future_date',",
              "  'customer_data',",
              "  'Created date is in the future: ' || created_at",
              "FROM customer_data",
              "WHERE created_at > CURRENT_DATE",
              "ORDER BY record_id, check_name;"
            ]
          }
        ]
      },
      {
        "name": "create-clean-dataset",
        "codes": [
          {
            "name": "Filter Valid Records",
            "script": [
              "SELECT",
              "  customer_id,",
              "  TRIM(customer_name) AS customer_name,",
              "  LOWER(TRIM(email)) AS email,",
              "  phone,",
              "  created_at,",
              "  country",
              "FROM customer_data",
              "WHERE customer_id IS NOT NULL",
              "  AND email IS NOT NULL",
              "  AND email LIKE '%@%'",
              "  AND email LIKE '%.%'",
              "  AND LENGTH(email) >= 5",
              "  AND created_at IS NOT NULL",
              "  AND created_at <= CURRENT_DATE",
              "  AND created_at >= '1900-01-01'",
              "  AND customer_id NOT IN (",
              "    SELECT customer_id",
              "    FROM customer_data",
              "    GROUP BY customer_id",
              "    HAVING COUNT(*) > 1",
              "  )",
              "ORDER BY customer_id;"
            ]
          }
        ]
      }
    ]
  }
}
```

### Explanation

**Quality Check Types:**

1. **Null Checks**:
   - Identifies missing values in critical fields
   - Calculates percentage of nulls per column
   - Essential for required field validation

2. **Duplicate Checks**:
   - Detects duplicate primary keys
   - Finds duplicate business keys (like email)
   - Calculates duplication rate

3. **Format Validation**:
   - Email pattern validation (@ symbol, domain)
   - Phone number length validation
   - Custom format rules per field

4. **Range Checks**:
   - Prevents future dates in historical fields
   - Detects unrealistic dates (before 1900)
   - Validates data makes logical sense

5. **Referential Integrity**:
   - Finds orphan records (transactions without customers)
   - Ensures foreign key relationships are valid
   - Critical for data consistency

6. **Business Logic Validation**:
   - Checks for negative transaction amounts
   - Flags suspiciously high values
   - Domain-specific rules

**Output Tables:**

1. **Quality Report**: Summary of all failed checks with counts and percentages
2. **Failed Records**: Individual records that failed with specific reasons
3. **Clean Dataset**: Only valid records that passed all checks

**Benefits:**
- Automated quality monitoring
- Early detection of data issues
- Detailed failure tracking for debugging
- Clean data output for downstream processing
- Historical quality trends with incremental loading

---

## 5. Incremental Processing

### Overview
Efficiently process only new or changed records using various incremental loading strategies, reducing processing time and resource usage.

### Use Case
Daily processing of large transaction tables where only yesterday's data needs to be processed, using last modified timestamps and watermarks.

### Configuration JSON

```json
{
  "storage": {
    "input": {
      "tables": [
        {
          "source": "in.c-source.transactions",
          "destination": "transactions_new.csv",
          "columns": ["transaction_id", "customer_id", "amount", "transaction_date", "status", "last_modified"],
          "changed_since": "-1 days"
        },
        {
          "source": "out.c-processed.transactions_history",
          "destination": "transactions_history.csv",
          "columns": ["transaction_id", "customer_id", "amount", "transaction_date", "status", "processed_date"]
        },
        {
          "source": "out.c-processed.daily_aggregates",
          "destination": "daily_aggregates_existing.csv"
        }
      ]
    },
    "output": {
      "tables": [
        {
          "source": "transactions_processed.csv",
          "destination": "out.c-processed.transactions_history",
          "incremental": true,
          "primary_key": ["transaction_id"]
        },
        {
          "source": "daily_aggregates_new.csv",
          "destination": "out.c-processed.daily_aggregates",
          "incremental": true,
          "delete_where_column": "transaction_date",
          "delete_where_values": ["{{ date }}"],
          "delete_where_operator": "eq",
          "primary_key": ["transaction_date", "customer_id"]
        },
        {
          "source": "customer_running_totals.csv",
          "destination": "out.c-processed.customer_totals",
          "incremental": false,
          "primary_key": ["customer_id"]
        }
      ]
    }
  },
  "parameters": {
    "blocks": [
      {
        "name": "incremental-load-strategy-1",
        "codes": [
          {
            "name": "Identify New Records",
            "script": [
              "-- Strategy: Use changed_since to get new/modified records",
              "CREATE TABLE new_records AS",
              "SELECT",
              "  t.transaction_id,",
              "  t.customer_id,",
              "  t.amount,",
              "  t.transaction_date,",
              "  t.status,",
              "  t.last_modified,",
              "  CURRENT_TIMESTAMP AS processed_date",
              "FROM transactions_new t",
              "LEFT JOIN transactions_history h",
              "  ON t.transaction_id = h.transaction_id",
              "WHERE h.transaction_id IS NULL",
              "  OR t.last_modified > h.processed_date;"
            ]
          },
          {
            "name": "Process New Transactions",
            "script": [
              "-- Apply business logic to new records",
              "SELECT",
              "  transaction_id,",
              "  customer_id,",
              "  CAST(amount AS DECIMAL(10,2)) AS amount,",
              "  DATE(transaction_date) AS transaction_date,",
              "  UPPER(status) AS status,",
              "  processed_date",
              "FROM new_records",
              "WHERE status IN ('completed', 'pending')",
              "  AND amount > 0",
              "ORDER BY transaction_id;"
            ]
          }
        ]
      },
      {
        "name": "incremental-aggregates",
        "codes": [
          {
            "name": "Calculate Daily Aggregates",
            "script": [
              "-- Aggregate new transactions by date and customer",
              "SELECT",
              "  DATE(transaction_date) AS transaction_date,",
              "  customer_id,",
              "  COUNT(*) AS transaction_count,",
              "  CAST(SUM(amount) AS DECIMAL(12,2)) AS daily_total,",
              "  CAST(AVG(amount) AS DECIMAL(10,2)) AS daily_average,",
              "  CAST(MIN(amount) AS DECIMAL(10,2)) AS min_transaction,",
              "  CAST(MAX(amount) AS DECIMAL(10,2)) AS max_transaction,",
              "  MAX(processed_date) AS last_processed",
              "FROM new_records",
              "WHERE status = 'completed'",
              "GROUP BY DATE(transaction_date), customer_id;"
            ]
          }
        ]
      },
      {
        "name": "running-totals",
        "codes": [
          {
            "name": "Merge Historical and New Data",
            "script": [
              "-- Combine existing aggregates with new data",
              "CREATE TABLE all_aggregates AS",
              "SELECT",
              "  transaction_date,",
              "  customer_id,",
              "  transaction_count,",
              "  daily_total",
              "FROM daily_aggregates_existing",
              "WHERE transaction_date < DATE('{{ date }}')",
              "UNION ALL",
              "SELECT",
              "  transaction_date,",
              "  customer_id,",
              "  transaction_count,",
              "  daily_total",
              "FROM daily_aggregates_new;"
            ]
          },
          {
            "name": "Calculate Customer Running Totals",
            "script": [
              "-- Calculate cumulative metrics per customer",
              "SELECT",
              "  customer_id,",
              "  COUNT(DISTINCT transaction_date) AS active_days,",
              "  SUM(transaction_count) AS lifetime_transactions,",
              "  CAST(SUM(daily_total) AS DECIMAL(12,2)) AS lifetime_value,",
              "  CAST(AVG(daily_total) AS DECIMAL(10,2)) AS avg_daily_spend,",
              "  MIN(transaction_date) AS first_transaction_date,",
              "  MAX(transaction_date) AS last_transaction_date,",
              "  CURRENT_DATE AS calculated_date",
              "FROM all_aggregates",
              "GROUP BY customer_id",
              "ORDER BY lifetime_value DESC;"
            ]
          }
        ]
      }
    ]
  }
}
```

### Explanation

**Incremental Loading Strategies:**

1. **Changed Since Filter**:
   - Input table uses `changed_since: "-1 days"` parameter
   - Keboola automatically filters for records modified in last 24 hours
   - Most efficient for large tables with proper indexing

2. **Left Join Comparison**:
   - Compares new data against existing history
   - Identifies truly new records (no match in history)
   - Identifies modified records (newer last_modified timestamp)

3. **Incremental Output with Primary Key**:
   - `incremental: true` appends new records
   - Primary key prevents duplicates (upsert behavior)
   - Historical data accumulates over time

4. **Delete and Replace by Date**:
   - Deletes existing records for current date
   - Inserts fresh calculations
   - Allows reprocessing without duplicates

**Processing Workflow:**

1. **Identify New Records**: Filter for transactions not in history or recently modified
2. **Process New Data**: Apply transformations only to new records
3. **Incremental Aggregates**: Calculate metrics for new data only
4. **Merge and Recalculate**: Combine historical with new for running totals
5. **Full Replacement**: Recalculate complete customer totals

**Performance Benefits:**
- Processes only changed data (1% of table vs 100%)
- Reduces transformation time from hours to minutes
- Lower resource consumption
- Faster feedback loops

**Use Cases:**
- Daily transaction processing
- Event log aggregation
- Slowly changing dimension updates
- Real-time metric calculations

**Key Patterns:**
- Use `changed_since` for time-based filtering
- Use LEFT JOIN to find new records
- Mix incremental and full refresh as needed
- Delete-and-replace for date-partitioned data

---

## 6. Multi-Source Data Aggregation

### Overview
Combines data from multiple disparate sources (databases, APIs, files) into unified analytical tables with reconciliation and data consistency checks.

### Use Case
Create a unified customer 360 view by combining CRM data, web analytics, support tickets, and purchase history from different systems.

### Configuration JSON

```json
{
  "storage": {
    "input": {
      "tables": [
        {
          "source": "in.c-crm.customers",
          "destination": "crm_customers.csv",
          "columns": ["customer_id", "full_name", "email", "phone", "created_date", "account_status"]
        },
        {
          "source": "in.c-ecommerce.orders",
          "destination": "ecommerce_orders.csv",
          "columns": ["order_id", "customer_email", "order_date", "total_amount", "order_status"]
        },
        {
          "source": "in.c-analytics.web_sessions",
          "destination": "web_sessions.csv",
          "columns": ["session_id", "user_id", "session_date", "page_views", "session_duration", "device_type"]
        },
        {
          "source": "in.c-support.tickets",
          "destination": "support_tickets.csv",
          "columns": ["ticket_id", "customer_email", "created_date", "status", "priority", "category"]
        },
        {
          "source": "in.c-marketing.email_campaigns",
          "destination": "email_campaigns.csv",
          "columns": ["campaign_id", "email", "sent_date", "opened", "clicked", "converted"]
        }
      ]
    },
    "output": {
      "tables": [
        {
          "source": "customer_360.csv",
          "destination": "out.c-unified.customer_360",
          "incremental": false,
          "primary_key": ["customer_id"]
        },
        {
          "source": "data_reconciliation.csv",
          "destination": "out.c-quality.reconciliation_report",
          "incremental": true,
          "delete_where_column": "report_date",
          "delete_where_values": ["{{ date }}"],
          "delete_where_operator": "eq",
          "primary_key": ["report_date", "source_system", "metric_name"]
        },
        {
          "source": "customer_timeline.csv",
          "destination": "out.c-unified.customer_timeline",
          "incremental": false,
          "primary_key": ["customer_id", "event_date", "event_type", "event_id"]
        }
      ]
    }
  },
  "parameters": {
    "blocks": [
      {
        "name": "standardize-customer-keys",
        "codes": [
          {
            "name": "Create Master Customer List",
            "script": [
              "-- Standardize CRM data as the master source",
              "CREATE TABLE master_customers AS",
              "SELECT",
              "  customer_id,",
              "  LOWER(TRIM(email)) AS email,",
              "  TRIM(full_name) AS customer_name,",
              "  phone,",
              "  created_date,",
              "  account_status,",
              "  'CRM' AS source_system",
              "FROM crm_customers",
              "WHERE email IS NOT NULL;"
            ]
          },
          {
            "name": "Map Ecommerce Customers",
            "script": [
              "-- Create email-based mapping for ecommerce",
              "CREATE TABLE ecommerce_customer_map AS",
              "SELECT DISTINCT",
              "  mc.customer_id,",
              "  LOWER(TRIM(eo.customer_email)) AS email,",
              "  COUNT(DISTINCT eo.order_id) AS total_orders,",
              "  MIN(eo.order_date) AS first_order_date,",
              "  MAX(eo.order_date) AS last_order_date",
              "FROM ecommerce_orders eo",
              "LEFT JOIN master_customers mc",
              "  ON LOWER(TRIM(eo.customer_email)) = mc.email",
              "GROUP BY mc.customer_id, LOWER(TRIM(eo.customer_email));"
            ]
          },
          {
            "name": "Map Support Customers",
            "script": [
              "-- Aggregate support ticket data",
              "CREATE TABLE support_customer_map AS",
              "SELECT",
              "  mc.customer_id,",
              "  LOWER(TRIM(st.customer_email)) AS email,",
              "  COUNT(*) AS total_tickets,",
              "  SUM(CASE WHEN st.status = 'open' THEN 1 ELSE 0 END) AS open_tickets,",
              "  SUM(CASE WHEN st.priority = 'high' THEN 1 ELSE 0 END) AS high_priority_tickets,",
              "  MAX(st.created_date) AS last_ticket_date",
              "FROM support_tickets st",
              "LEFT JOIN master_customers mc",
              "  ON LOWER(TRIM(st.customer_email)) = mc.email",
              "GROUP BY mc.customer_id, LOWER(TRIM(st.customer_email));"
            ]
          }
        ]
      },
      {
        "name": "aggregate-multi-source-data",
        "codes": [
          {
            "name": "Calculate Order Metrics",
            "script": [
              "CREATE TABLE order_metrics AS",
              "SELECT",
              "  ecm.customer_id,",
              "  ecm.total_orders,",
              "  ecm.first_order_date,",
              "  ecm.last_order_date,",
              "  CAST(SUM(eo.total_amount) AS DECIMAL(12,2)) AS lifetime_revenue,",
              "  CAST(AVG(eo.total_amount) AS DECIMAL(10,2)) AS avg_order_value,",
              "  COUNT(DISTINCT CASE WHEN eo.order_status = 'completed' THEN eo.order_id END) AS completed_orders,",
              "  COUNT(DISTINCT CASE WHEN eo.order_status = 'cancelled' THEN eo.order_id END) AS cancelled_orders",
              "FROM ecommerce_customer_map ecm",
              "LEFT JOIN ecommerce_orders eo",
              "  ON LOWER(TRIM(eo.customer_email)) = ecm.email",
              "WHERE ecm.customer_id IS NOT NULL",
              "GROUP BY ecm.customer_id, ecm.total_orders, ecm.first_order_date, ecm.last_order_date;"
            ]
          },
          {
            "name": "Calculate Web Analytics Metrics",
            "script": [
              "CREATE TABLE web_metrics AS",
              "SELECT",
              "  mc.customer_id,",
              "  COUNT(DISTINCT ws.session_id) AS total_sessions,",
              "  SUM(ws.page_views) AS total_page_views,",
              "  CAST(AVG(ws.page_views) AS DECIMAL(8,2)) AS avg_pages_per_session,",
              "  CAST(SUM(ws.session_duration) AS DECIMAL(12,2)) AS total_time_minutes,",
              "  MAX(ws.session_date) AS last_visit_date,",
              "  COUNT(DISTINCT ws.device_type) AS device_types_used",
              "FROM web_sessions ws",
              "JOIN master_customers mc",
              "  ON ws.user_id = mc.customer_id",
              "GROUP BY mc.customer_id;"
            ]
          },
          {
            "name": "Calculate Marketing Engagement",
            "script": [
              "CREATE TABLE marketing_metrics AS",
              "SELECT",
              "  mc.customer_id,",
              "  COUNT(*) AS emails_sent,",
              "  SUM(CASE WHEN ec.opened = 1 THEN 1 ELSE 0 END) AS emails_opened,",
              "  SUM(CASE WHEN ec.clicked = 1 THEN 1 ELSE 0 END) AS emails_clicked,",
              "  SUM(CASE WHEN ec.converted = 1 THEN 1 ELSE 0 END) AS email_conversions,",
              "  ROUND(CAST(SUM(CASE WHEN ec.opened = 1 THEN 1 ELSE 0 END) AS DECIMAL)",
              "    / NULLIF(COUNT(*), 0) * 100, 2) AS open_rate_percent,",
              "  ROUND(CAST(SUM(CASE WHEN ec.clicked = 1 THEN 1 ELSE 0 END) AS DECIMAL)",
              "    / NULLIF(SUM(CASE WHEN ec.opened = 1 THEN 1 ELSE 0 END), 0) * 100, 2) AS click_rate_percent",
              "FROM email_campaigns ec",
              "JOIN master_customers mc",
              "  ON LOWER(TRIM(ec.email)) = mc.email",
              "GROUP BY mc.customer_id;"
            ]
          }
        ]
      },
      {
        "name": "create-unified-view",
        "codes": [
          {
            "name": "Build Customer 360",
            "script": [
              "SELECT",
              "  mc.customer_id,",
              "  mc.customer_name,",
              "  mc.email,",
              "  mc.phone,",
              "  mc.created_date AS crm_created_date,",
              "  mc.account_status,",
              "  -- Order metrics",
              "  COALESCE(om.total_orders, 0) AS total_orders,",
              "  COALESCE(om.completed_orders, 0) AS completed_orders,",
              "  COALESCE(om.lifetime_revenue, 0.00) AS lifetime_revenue,",
              "  COALESCE(om.avg_order_value, 0.00) AS avg_order_value,",
              "  om.first_order_date,",
              "  om.last_order_date,",
              "  -- Support metrics",
              "  COALESCE(scm.total_tickets, 0) AS support_tickets,",
              "  COALESCE(scm.open_tickets, 0) AS open_support_tickets,",
              "  COALESCE(scm.high_priority_tickets, 0) AS high_priority_tickets,",
              "  scm.last_ticket_date,",
              "  -- Web analytics",
              "  COALESCE(wm.total_sessions, 0) AS web_sessions,",
              "  COALESCE(wm.total_page_views, 0) AS page_views,",
              "  COALESCE(wm.avg_pages_per_session, 0.00) AS avg_pages_per_session,",
              "  wm.last_visit_date,",
              "  -- Marketing engagement",
              "  COALESCE(mm.emails_sent, 0) AS marketing_emails_sent,",
              "  COALESCE(mm.emails_opened, 0) AS marketing_emails_opened,",
              "  COALESCE(mm.open_rate_percent, 0.00) AS email_open_rate,",
              "  COALESCE(mm.click_rate_percent, 0.00) AS email_click_rate,",
              "  -- Calculated fields",
              "  CASE",
              "    WHEN om.lifetime_revenue > 10000 THEN 'VIP'",
              "    WHEN om.lifetime_revenue > 1000 THEN 'High Value'",
              "    WHEN om.lifetime_revenue > 100 THEN 'Medium Value'",
              "    WHEN om.lifetime_revenue > 0 THEN 'Low Value'",
              "    ELSE 'No Purchase'",
              "  END AS customer_segment,",
              "  CASE",
              "    WHEN om.last_order_date >= DATE('now', '-30 days') THEN 'Active'",
              "    WHEN om.last_order_date >= DATE('now', '-90 days') THEN 'At Risk'",
              "    WHEN om.last_order_date IS NOT NULL THEN 'Churned'",
              "    ELSE 'Prospect'",
              "  END AS lifecycle_stage,",
              "  CURRENT_TIMESTAMP AS last_updated",
              "FROM master_customers mc",
              "LEFT JOIN order_metrics om ON mc.customer_id = om.customer_id",
              "LEFT JOIN support_customer_map scm ON mc.customer_id = scm.customer_id",
              "LEFT JOIN web_metrics wm ON mc.customer_id = wm.customer_id",
              "LEFT JOIN marketing_metrics mm ON mc.customer_id = mm.customer_id",
              "ORDER BY mc.customer_id;"
            ]
          }
        ]
      },
      {
        "name": "data-reconciliation",
        "codes": [
          {
            "name": "Count Records Per Source",
            "script": [
              "-- Validate data counts across sources",
              "SELECT",
              "  DATE('{{ date }}') AS report_date,",
              "  'CRM' AS source_system,",
              "  'total_customers' AS metric_name,",
              "  COUNT(*) AS metric_value",
              "FROM crm_customers",
              "UNION ALL",
              "SELECT",
              "  DATE('{{ date }}'),",
              "  'Ecommerce',",
              "  'unique_customer_emails',",
              "  COUNT(DISTINCT customer_email)",
              "FROM ecommerce_orders",
              "UNION ALL",
              "SELECT",
              "  DATE('{{ date }}'),",
              "  'Support',",
              "  'unique_customer_emails',",
              "  COUNT(DISTINCT customer_email)",
              "FROM support_tickets",
              "UNION ALL",
              "SELECT",
              "  DATE('{{ date }}'),",
              "  'Customer 360',",
              "  'total_unified_customers',",
              "  COUNT(*)",
              "FROM master_customers",
              "UNION ALL",
              "SELECT",
              "  DATE('{{ date }}'),",
              "  'Customer 360',",
              "  'customers_with_orders',",
              "  COUNT(*)",
              "FROM master_customers mc",
              "WHERE EXISTS (",
              "  SELECT 1 FROM ecommerce_customer_map ecm",
              "  WHERE ecm.customer_id = mc.customer_id",
              ")",
              "UNION ALL",
              "SELECT",
              "  DATE('{{ date }}'),",
              "  'Data Quality',",
              "  'orphan_ecommerce_customers',",
              "  COUNT(DISTINCT customer_email)",
              "FROM ecommerce_orders eo",
              "WHERE NOT EXISTS (",
              "  SELECT 1 FROM master_customers mc",
              "  WHERE mc.email = LOWER(TRIM(eo.customer_email))",
              ")",
              "ORDER BY source_system, metric_name;"
            ]
          }
        ]
      },
      {
        "name": "create-customer-timeline",
        "codes": [
          {
            "name": "Unify All Customer Events",
            "script": [
              "-- Create unified timeline of all customer interactions",
              "SELECT",
              "  mc.customer_id,",
              "  DATE(eo.order_date) AS event_date,",
              "  'Order' AS event_type,",
              "  eo.order_id AS event_id,",
              "  'Order ' || eo.order_status || ': $' || CAST(eo.total_amount AS VARCHAR) AS event_description,",
              "  eo.total_amount AS event_value",
              "FROM ecommerce_orders eo",
              "JOIN master_customers mc ON LOWER(TRIM(eo.customer_email)) = mc.email",
              "UNION ALL",
              "SELECT",
              "  mc.customer_id,",
              "  DATE(st.created_date),",
              "  'Support Ticket',",
              "  st.ticket_id,",
              "  st.category || ' - ' || st.priority || ' priority',",
              "  0",
              "FROM support_tickets st",
              "JOIN master_customers mc ON LOWER(TRIM(st.customer_email)) = mc.email",
              "UNION ALL",
              "SELECT",
              "  mc.customer_id,",
              "  DATE(ec.sent_date),",
              "  'Email Campaign',",
              "  ec.campaign_id,",
              "  CASE",
              "    WHEN ec.converted = 1 THEN 'Converted'",
              "    WHEN ec.clicked = 1 THEN 'Clicked'",
              "    WHEN ec.opened = 1 THEN 'Opened'",
              "    ELSE 'Sent'",
              "  END,",
              "  0",
              "FROM email_campaigns ec",
              "JOIN master_customers mc ON LOWER(TRIM(ec.email)) = mc.email",
              "UNION ALL",
              "SELECT",
              "  customer_id,",
              "  DATE(session_date),",
              "  'Web Session',",
              "  session_id,",
              "  device_type || ' - ' || CAST(page_views AS VARCHAR) || ' pages',",
              "  0",
              "FROM web_sessions",
              "ORDER BY customer_id, event_date DESC, event_type;"
            ]
          }
        ]
      }
    ]
  }
}
```

### Explanation

**Multi-Source Integration Strategy:**

1. **Master Data Management**:
   - CRM system designated as master source for customer IDs
   - Email used as common key across systems
   - Standardization (lowercase, trim) ensures matching

2. **Source System Mapping**:
   - **CRM**: Authoritative customer records with IDs
   - **E-commerce**: Order data mapped via email
   - **Web Analytics**: Session data mapped via user ID
   - **Support**: Ticket data mapped via email
   - **Marketing**: Campaign engagement mapped via email

3. **Data Aggregation Layers**:

   **Layer 1 - Source Standardization**:
   - Clean and standardize each source independently
   - Create customer mappings for each system

   **Layer 2 - Metric Calculation**:
   - Calculate domain-specific metrics per source
   - Aggregate to customer level

   **Layer 3 - Unified View**:
   - Join all metrics to master customer list
   - Use COALESCE for null handling
   - Calculate derived segments and lifecycle stages

4. **Customer Segmentation**:
   - **Value-based**: VIP, High/Medium/Low Value, No Purchase
   - **Lifecycle-based**: Active, At Risk, Churned, Prospect
   - Calculated from unified metrics

5. **Data Quality & Reconciliation**:
   - Count records per source system
   - Identify orphan records (no CRM match)
   - Track mapping success rates
   - Daily reconciliation report

6. **Customer Timeline**:
   - Unified event stream across all sources
   - UNION ALL combines orders, tickets, emails, sessions
   - Chronological view of customer journey
   - Enables journey analysis and attribution

**Output Tables:**

1. **Customer 360**: Single row per customer with all metrics
2. **Reconciliation Report**: Data quality metrics per source
3. **Customer Timeline**: Event-level interaction history

**Advanced Features:**
- Left joins preserve all customers even without activity
- COALESCE provides default values for missing data
- EXISTS clauses for efficient orphan detection
- Composite primary keys for timeline uniqueness
- Parameter substitution for dynamic date filtering

**Benefits:**
- Single source of truth for customer data
- Cross-channel customer understanding
- Data quality monitoring
- Supports advanced analytics (churn prediction, LTV modeling)
- Enables personalization and segmentation

**Scalability Considerations:**
- Incremental processing for large sources
- Indexed join keys for performance
- Separate reconciliation from production views
- Modular design allows adding new sources easily

---

## Best Practices Summary

### Configuration Best Practices

1. **Always Define Primary Keys**: Ensures data integrity and enables upserts
2. **Use Incremental Loading**: Reduces processing time and costs for large datasets
3. **Implement Data Quality Checks**: Catch issues early before they propagate
4. **Parameterize Dates**: Use `{{ date }}` for dynamic, reusable configurations
5. **Handle Nulls Explicitly**: Use COALESCE and NULLIF to prevent errors
6. **Standardize Keys**: Lowercase and trim matching keys for reliability

### SQL Best Practices

1. **Cast Numeric Fields**: Ensure precision with DECIMAL(precision, scale)
2. **Prevent Division by Zero**: Use NULLIF in denominators
3. **Use Meaningful Aliases**: Make code self-documenting
4. **Comment Complex Logic**: Explain business rules and calculations
5. **Order Results**: Consistent ordering aids debugging and testing
6. **Create Intermediate Tables**: Break complex transformations into steps

### Performance Optimization

1. **Filter Early**: Apply WHERE clauses before joins when possible
2. **Use Changed Since**: Leverage Keboola's incremental loading features
3. **Index Join Keys**: Ensure primary and foreign keys are indexed
4. **Avoid SELECT ***: Specify only needed columns
5. **Aggregate Before Joining**: Reduce data volume before expensive joins
6. **Monitor Query Performance**: Review execution times and optimize slow queries

### Workflow Design

1. **Modular Blocks**: Separate extraction, transformation, and loading logic
2. **Idempotent Operations**: Ensure reruns produce same results
3. **Error Handling**: Design for graceful failure and recovery
4. **Logging and Monitoring**: Track metrics and execution status
5. **Version Control**: Maintain configuration history
6. **Documentation**: Comment complex business logic and data sources

---

## Conclusion

These six practical examples demonstrate real-world Keboola usage patterns for common data engineering scenarios. Each example includes production-ready configuration JSON and detailed explanations of the logic and design decisions.

**Key Takeaways:**

- **ETL Pipelines**: Start simple with clear extraction, transformation, and loading steps
- **Marketing Analytics**: Combine multiple sources to calculate business metrics
- **E-Commerce Reporting**: Build comprehensive reporting with multiple output tables
- **Data Quality**: Implement automated validation before downstream processing
- **Incremental Processing**: Optimize performance by processing only changed data
- **Multi-Source Aggregation**: Create unified views across disparate systems

These patterns can be adapted and combined for virtually any data integration and transformation use case in Keboola.
