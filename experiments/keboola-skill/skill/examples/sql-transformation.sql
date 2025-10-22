-- Customer Enrichment Transformation
-- Description: Combine customer data with order history and calculate metrics
-- Input: in.c-mysql.customers, in.c-mysql.orders
-- Output: out.c-analytics.customers_enriched

-- Step 1: Clean and validate customer data
CREATE TABLE staging_customers AS
SELECT
  CAST(id AS NUMBER) as customer_id,
  TRIM(name) as customer_name,
  LOWER(TRIM(email)) as email,
  UPPER(status) as status,
  TRY_TO_TIMESTAMP(created_at) as created_at,
  TRY_TO_TIMESTAMP(updated_at) as updated_at
FROM "in.c-mysql.customers"
WHERE id IS NOT NULL
  AND email IS NOT NULL
  AND status IN ('active', 'inactive', 'pending');

-- Step 2: Calculate order metrics per customer
CREATE TABLE customer_orders AS
SELECT
  customer_id,
  COUNT(*) as total_orders,
  SUM(amount) as lifetime_value,
  AVG(amount) as avg_order_value,
  MIN(order_date) as first_order_date,
  MAX(order_date) as last_order_date,
  DATEDIFF(day, MAX(order_date), CURRENT_DATE()) as days_since_last_order
FROM "in.c-mysql.orders"
WHERE status = 'completed'
GROUP BY customer_id;

-- Step 3: Segment customers
CREATE TABLE customer_segments AS
SELECT
  customer_id,
  CASE
    WHEN lifetime_value >= 10000 THEN 'VIP'
    WHEN lifetime_value >= 5000 THEN 'High Value'
    WHEN lifetime_value >= 1000 THEN 'Medium Value'
    ELSE 'Low Value'
  END as value_segment,
  CASE
    WHEN days_since_last_order <= 30 THEN 'Active'
    WHEN days_since_last_order <= 90 THEN 'At Risk'
    WHEN days_since_last_order <= 180 THEN 'Dormant'
    ELSE 'Lost'
  END as engagement_segment
FROM customer_orders;

-- Step 4: Data quality check
CREATE TABLE data_quality_check AS
SELECT
  (SELECT COUNT(*) FROM staging_customers) as total_customers,
  (SELECT COUNT(DISTINCT customer_id) FROM staging_customers) as unique_customers,
  (SELECT COUNT(*) FROM customer_orders) as customers_with_orders,
  CASE
    WHEN (SELECT COUNT(*) FROM staging_customers) = 0 THEN 'FAIL: No customers'
    WHEN (SELECT COUNT(*) FROM staging_customers) != (SELECT COUNT(DISTINCT customer_id) FROM staging_customers) THEN 'FAIL: Duplicate customer IDs'
    ELSE 'PASS'
  END as validation_status;

-- Step 5: Final enriched table (only if validation passes)
CREATE TABLE "out.c-analytics.customers_enriched" AS
SELECT
  c.customer_id,
  c.customer_name,
  c.email,
  c.status,
  c.created_at,
  c.updated_at,
  COALESCE(o.total_orders, 0) as total_orders,
  COALESCE(o.lifetime_value, 0) as lifetime_value,
  COALESCE(o.avg_order_value, 0) as avg_order_value,
  o.first_order_date,
  o.last_order_date,
  COALESCE(o.days_since_last_order, 999999) as days_since_last_order,
  COALESCE(s.value_segment, 'No Orders') as value_segment,
  COALESCE(s.engagement_segment, 'Never Ordered') as engagement_segment,
  CURRENT_TIMESTAMP() as enriched_at
FROM staging_customers c
LEFT JOIN customer_orders o ON c.customer_id = o.customer_id
LEFT JOIN customer_segments s ON c.customer_id = s.customer_id
CROSS JOIN data_quality_check q
WHERE q.validation_status = 'PASS';

-- Step 6: Output validation results
CREATE TABLE "out.c-analytics.customers_enriched_metadata" AS
SELECT * FROM data_quality_check;
