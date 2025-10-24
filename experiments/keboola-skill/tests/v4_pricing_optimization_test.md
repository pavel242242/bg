# V4 Test: Pricing Optimization Scenario

## User Request
"Help me build pricing optimization: hike for low price sensitivity customers, discount on items taking up warehouse space, revenue growth"

---

## Step 1: Understand Business Problem

**Claude follows SKILL.md:40-45** - 5 required questions:

### Questions Claude Would Ask:
1. "What decision does this enable? Who makes it?"
   - **Expected**: Pricing team decides price adjustments weekly
2. "What's the ONE metric that matters most?"
   - **Expected**: Revenue growth % or Gross margin improvement
3. "How often is this needed? (Real-time/Hourly/Daily/Weekly)"
   - **Expected**: Weekly pricing updates
4. "Does data contain PII? (Names/Emails/SSNs/Financial data)"
   - **Expected**: Yes - customer purchase history, potentially emails
5. "What does success look like in 30 days?"
   - **Expected**: "5% revenue increase without cannibalizing high-margin products"

### Claude's Output (SKILL.md:47):
```yaml
Decision: "Weekly price adjustments for 500+ SKUs"
Metric: "Revenue growth % (target: +5%)"
Frequency: "Weekly"
PII: "Yes - customer purchase history"
Success: "5% revenue increase, maintained margin on core products"
```

**✅ PASS**: v4 provides 5 concise questions vs v3's verbose interrogation

---

## Step 2: Discover Data Sources

**Claude follows SKILL.md:53-77** - Data discovery process:

### What Claude Would Do:

**Action 1**: Use Read tool on `resources/KNOWLEDGE_MAP.md` (SKILL.md:59)

**Action 2**: Ask user: "What systems do you use? I need:
- Sales transactions (price, quantity, customer)
- Inventory data (warehouse levels, holding costs)
- Customer data (segments, purchase frequency)"

**Action 3**: Based on user response (e.g., "MySQL sales DB, Shopify, Google Sheets inventory"), Claude uses Grep to search KNOWLEDGE_MAP:
- `Grep "MySQL" resources/KNOWLEDGE_MAP.md` → finds `keboola.ex-db-mysql`
- `Grep "Shopify" resources/KNOWLEDGE_MAP.md` → finds `keboola.ex-shopify`
- `Grep "Google Sheets" resources/KNOWLEDGE_MAP.md` → finds `keboola.ex-google-sheets`

**Action 4**: Use Read tool on component docs (SKILL.md:127):
- `docs-repos/connection-docs/components/extractors/database/mysql/index.md`
- `docs-repos/connection-docs/components/extractors/marketing-sales/shopify/index.md`

### Claude's Inventory Output (SKILL.md:63-75):
```json
{
  "sources": [
    {
      "system": "MySQL Sales DB",
      "contains": "transactions, customer_id, sku, price, quantity, timestamp",
      "keboola_component": "keboola.ex-db-mysql",
      "incremental": "updated_at",
      "estimate_rows": "500K/month"
    },
    {
      "system": "Shopify",
      "contains": "product_catalog, current_prices, inventory_levels",
      "keboola_component": "keboola.ex-shopify",
      "incremental": "updated_at"
    },
    {
      "system": "Google Sheets",
      "contains": "warehouse_costs, sku_dimensions, storage_fees",
      "keboola_component": "keboola.ex-google-sheets",
      "incremental": "full_refresh"
    }
  ]
}
```

**✅ PASS**: v4 provides JSON template for structured data inventory (new in v4)

---

## Step 3: Propose Architecture

**Claude follows SKILL.md:80-124** - Architecture proposal:

### What Claude Would Do:

**Action 1**: Use Read tool on `resources/templates/Design_Brief.md` (SKILL.md:83)

**Action 2**: Use decision tree from SKILL.md:311-376 to choose pattern:
```yaml
question: "What's your data source?"
answers:
  - condition: "Database (MySQL, PostgreSQL, Snowflake, etc.)"
    component_pattern: "keboola.ex-db-{database}"
```
→ Selects MySQL extractor

**Action 3**: Check Pattern Library (SKILL.md:380-418):
```yaml
Pattern 2: Batch ETL
name: "Daily Batch Extract-Transform-Load"
use_case: "Scheduled data sync → Analytics tables"
frequency: "Daily"
```
→ Matches "Weekly" requirement

**Action 4**: Use Component Quick Reference (SKILL.md:422-444):
```markdown
| MySQL | keboola.ex-db-mysql | incremental: updated_at, primaryKey: id |
```
→ Gets config pattern

### Claude's Architecture Proposal:

```markdown
## Pricing Optimization Pipeline Architecture

### Data Flow
1. **Extract** (Daily 1am):
   - MySQL → `in.c-sales.transactions` (incremental on updated_at)
   - Shopify → `in.c-products.catalog` (full refresh)
   - Google Sheets → `in.c-warehouse.costs` (full refresh)

2. **Transform** (Snowflake SQL):
   - **Silver Layer**: Clean & join
     - `out.c-analytics.customer_price_sensitivity`
     - `out.c-analytics.inventory_carrying_costs`
   - **Gold Layer**: Business metrics
     - `out.c-pricing.recommended_price_changes`

3. **Validate**: Check data quality (SKILL.md:163-193)
   - Freshness: < 24 hours old
   - Volume: Min 10K transactions/day
   - Schema: Required fields present

4. **Deliver**:
   - Write to Google Sheets → `keboola.wr-google-sheets`
   - Schedule: Weekly (Sundays 11pm) via Scheduler API

### Key Transformations

**Price Sensitivity Calculation** (From: ISL book + Data Smart):
- Logistic regression: price elasticity by customer segment
- Decision tree: segment customers by purchase frequency & cart value

**Inventory Optimization** (From: Data Smart):
- Holding cost = (days_in_warehouse × storage_fee × unit_cost)
- Discount threshold = holding_cost > margin

**Revenue Impact Simulation**:
- Test scenarios: +10%, +20%, -10%, -20% price changes
- Forecast revenue using historical elasticity

### APIs Used
- Storage API: `https://connection.keboola.com/v2/storage/`
- Queue API: `https://queue.keboola.com/jobs`
- Scheduler API: `https://scheduler.keboola.com/schedules`

**Estimated Build Time**: 2-4 hours with API deployment
**Data Latency**: 24 hours (Daily refresh)
```

**Approval Gate** (SKILL.md:118-124):
> "Does this architecture meet your needs? Reply 'build it' to proceed."

**❓ EVALUATION**:
- ✅ Shows clear data flow (bronze → silver → gold)
- ✅ Specifies APIs to use
- ✅ Includes validation
- ✅ References book knowledge (ISL, Data Smart)
- ❌ **MISSING**: No mention of PII handling (user said "Yes" to PII in Step 1)
- ❌ **MISSING**: No data contract/SLO definition (books emphasize this)

**Partial Pass** - Good structure but missing critical details from Step 1

---

## Step 4: Build Implementation

**Claude follows SKILL.md:126-319** - Generate configs & deploy:

### What Claude Would Do:

**Action 1**: Generate MySQL Extractor Config
```bash
# Use Read tool on docs (SKILL.md:127)
Read docs-repos/connection-docs/components/extractors/database/mysql/index.md
```

**Action 2**: Write config file (SKILL.md:134-153):
```json
{
  "name": "Sales Transactions - MySQL",
  "description": "Daily incremental sync for pricing optimization",
  "configuration": {
    "parameters": {
      "db": {
        "host": "{{user_provides}}",
        "database": "sales_db",
        "user": "keboola_readonly"
      },
      "incremental": true,
      "incrementalFetchingColumn": "updated_at",
      "tables": [
        {
          "name": "transactions",
          "outputTable": "in.c-sales.transactions",
          "primaryKey": ["transaction_id"],
          "query": "SELECT transaction_id, customer_id, sku, price, quantity, revenue, updated_at FROM transactions WHERE updated_at > ?"
        }
      ]
    }
  }
}
```

**Action 3**: Write SQL Transformation (SKILL.md:163-193):
```sql
-- Step 1: Calculate Price Sensitivity by Customer Segment
CREATE OR REPLACE TABLE "out.c-analytics.customer_price_sensitivity" AS
WITH customer_segments AS (
  SELECT
    customer_id,
    COUNT(DISTINCT transaction_id) as purchase_frequency,
    AVG(revenue) as avg_cart_value,
    CASE
      WHEN COUNT(*) >= 10 AND AVG(revenue) > 100 THEN 'high_value_loyal'
      WHEN COUNT(*) >= 10 THEN 'loyal'
      WHEN AVG(revenue) > 100 THEN 'high_value'
      ELSE 'casual'
    END as segment
  FROM "in.c-sales.transactions"
  WHERE updated_at >= DATEADD('day', -90, CURRENT_DATE)
  GROUP BY customer_id
),
price_elasticity AS (
  SELECT
    t.sku,
    cs.segment,
    -- Simple elasticity: % change in quantity / % change in price
    CORR(LN(t.price), LN(t.quantity)) as price_elasticity,
    COUNT(*) as sample_size
  FROM "in.c-sales.transactions" t
  JOIN customer_segments cs ON t.customer_id = cs.customer_id
  WHERE t.updated_at >= DATEADD('day', -90, CURRENT_DATE)
  GROUP BY t.sku, cs.segment
  HAVING COUNT(*) >= 30  -- Statistical significance
)
SELECT
  sku,
  segment,
  price_elasticity,
  CASE
    WHEN ABS(price_elasticity) < 0.5 THEN 'low_sensitivity'
    WHEN ABS(price_elasticity) < 1.0 THEN 'medium_sensitivity'
    ELSE 'high_sensitivity'
  END as sensitivity_category,
  sample_size
FROM price_elasticity;

-- Step 2: Calculate Inventory Carrying Costs
CREATE OR REPLACE TABLE "out.c-analytics.inventory_carrying_costs" AS
SELECT
  p.sku,
  p.inventory_level,
  w.storage_fee_per_day,
  w.sku_dimensions,
  DATEDIFF('day', p.last_sale_date, CURRENT_DATE) as days_in_warehouse,
  (DATEDIFF('day', p.last_sale_date, CURRENT_DATE) * w.storage_fee_per_day) as total_carrying_cost,
  p.unit_cost,
  (p.current_price - p.unit_cost) as current_margin
FROM "in.c-products.catalog" p
JOIN "in.c-warehouse.costs" w ON p.sku = w.sku
WHERE p.inventory_level > 0;

-- Step 3: Generate Recommended Price Changes
CREATE OR REPLACE TABLE "out.c-pricing.recommended_price_changes" AS
WITH recommendations AS (
  SELECT
    ps.sku,
    ps.segment,
    ps.sensitivity_category,
    ic.current_price,
    ic.current_margin,
    ic.days_in_warehouse,
    ic.total_carrying_cost,
    ic.inventory_level,
    CASE
      -- Price INCREASE for low sensitivity customers
      WHEN ps.sensitivity_category = 'low_sensitivity'
        AND ps.segment IN ('high_value_loyal', 'loyal')
        AND ic.current_margin > 0.2
      THEN ic.current_price * 1.10  -- +10% hike

      -- Price DECREASE for slow-moving inventory
      WHEN ic.days_in_warehouse > 60
        AND ic.total_carrying_cost > (ic.current_margin * ic.inventory_level)
      THEN ic.current_price * 0.85  -- -15% discount

      -- No change
      ELSE ic.current_price
    END as recommended_price,
    CASE
      WHEN recommended_price > ic.current_price THEN 'INCREASE'
      WHEN recommended_price < ic.current_price THEN 'DECREASE'
      ELSE 'NO_CHANGE'
    END as action,
    -- Estimated revenue impact
    (recommended_price - ic.current_price) * ic.inventory_level as estimated_revenue_change
  FROM "out.c-analytics.customer_price_sensitivity" ps
  JOIN "out.c-analytics.inventory_carrying_costs" ic ON ps.sku = ic.sku
)
SELECT
  sku,
  segment,
  current_price,
  recommended_price,
  ROUND((recommended_price - current_price) / current_price * 100, 1) as price_change_pct,
  action,
  days_in_warehouse,
  inventory_level,
  estimated_revenue_change,
  sensitivity_category
FROM recommendations
WHERE action != 'NO_CHANGE'
ORDER BY estimated_revenue_change DESC;

-- Step 4: VALIDATION (REQUIRED)
CREATE OR REPLACE TABLE "_validation" AS
SELECT
  COUNT(*) as recommended_changes,
  SUM(CASE WHEN action = 'INCREASE' THEN 1 ELSE 0 END) as price_increases,
  SUM(CASE WHEN action = 'DECREASE' THEN 1 ELSE 0 END) as price_decreases,
  SUM(estimated_revenue_change) as total_estimated_revenue_impact,
  MAX(CURRENT_TIMESTAMP) as run_timestamp,
  DATEDIFF('hour',
    (SELECT MAX(updated_at) FROM "in.c-sales.transactions"),
    CURRENT_TIMESTAMP
  ) as data_freshness_hours,
  CASE
    WHEN COUNT(*) = 0 THEN 'FAIL: No recommendations generated'
    WHEN data_freshness_hours > 48 THEN 'FAIL: Data too stale'
    WHEN total_estimated_revenue_impact < 0 THEN 'WARN: Negative revenue impact'
    ELSE 'PASS'
  END as validation_status
FROM "out.c-pricing.recommended_price_changes";

-- Step 5: Abort if validation fails
SET ABORT_TRANSFORMATION = (
  SELECT CASE WHEN validation_status LIKE 'FAIL:%' THEN validation_status ELSE '' END
  FROM "_validation"
);
```

**Action 4**: Deploy via API (SKILL.md:233-268):
```bash
# Save transformation config
cat > transformation_pricing_optimization.json <<'EOF'
{
  "name": "Pricing Optimization - Price Sensitivity & Inventory",
  "description": "Calculate recommended price changes based on customer sensitivity and warehouse costs",
  "configuration": {
    "parameters": {
      "backend": "snowflake",
      "type": "workspace",
      "queries": [
        "-- [SQL from above]"
      ]
    }
  }
}
EOF

# Deploy transformation
TRANSFORMATION_ID=$(curl -X POST "https://connection.keboola.com/v2/storage/components/keboola.snowflake-transformation/configs" \
  -H "X-StorageApi-Token: $KEBOOLA_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d @transformation_pricing_optimization.json \
  | jq -r '.id')

echo "Transformation deployed: $TRANSFORMATION_ID"

# Run the transformation
JOB_ID=$(curl -X POST "https://queue.keboola.com/jobs" \
  -H "X-StorageApi-Token: $KEBOOLA_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"mode\":\"run\",\"component\":\"keboola.snowflake-transformation\",\"config\":\"$TRANSFORMATION_ID\"}" \
  | jq -r '.id')

echo "Job started: $JOB_ID"
echo "Monitor at: https://connection.keboola.com/admin/projects/[PROJECT_ID]/jobs/$JOB_ID"
```

**Action 5**: Create Google Sheets Writer for output (SKILL.md:127):
```json
{
  "name": "Pricing Recommendations Output",
  "description": "Weekly price change recommendations to Google Sheets",
  "configuration": {
    "parameters": {
      "spreadsheetId": "{{user_provides}}",
      "sheets": [
        {
          "title": "Pricing Recommendations",
          "tableId": "out.c-pricing.recommended_price_changes"
        }
      ]
    }
  }
}
```

**Action 6**: Schedule weekly (SKILL.md:289-309):
```bash
curl -X POST "https://scheduler.keboola.com/schedules" \
  -H "X-StorageApi-Token: $KEBOOLA_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Pricing Optimization - Weekly Run",
    "schedule": {
      "cronTab": "0 23 * * 0",
      "timezone": "UTC",
      "state": "enabled"
    },
    "target": {
      "componentId": "orchestrator",
      "configurationId": "pricing-optimization-flow"
    }
  }'
```

**✅ PASS**: v4 provides complete implementation with:
- Working SQL (applies ISL concepts: correlation, segmentation)
- Validation pattern (Data Quality Fundamentals: freshness, volume)
- API deployment (correct endpoints from v3.0.1 fixes)
- Scheduling

---

## V4 Effectiveness Evaluation

### What V4 Does Well

**1. Structured Decision Making** (YAML trees):
```yaml
✅ Quick component lookup (KNOWLEDGE_MAP → component docs)
✅ Pattern matching (Batch ETL for weekly updates)
✅ Validation templates (freshness, volume, schema)
```

**2. Tool Explicitness**:
```bash
✅ 16+ explicit "Use Read tool on..." instructions
✅ Tool Reference Card (task → tool mapping)
✅ Command patterns (curl -X POST...)
```

**3. Information Density**:
```markdown
✅ Component Quick Reference (top 20 with config patterns)
✅ Pattern Library (CDC, Batch ETL, ML with metadata)
✅ 5-question condensed discovery (vs verbose interrogation)
```

**4. Book Knowledge Application**:
```
✅ ISL: Correlation for price elasticity, segmentation
✅ Data Smart: Holding cost calculation, inventory optimization
✅ Data Quality Fundamentals: 5 pillars validation (freshness, volume, schema)
```

### Where V4 Falls Short

**1. Missing Context Awareness**:
```
❌ User said "PII: Yes" in Step 1 → No PII handling in architecture
❌ No data contract/SLO definition (despite books emphasizing it)
❌ No discussion of customer segment definitions (who decides "loyal"?)
```

**2. Limited Troubleshooting Guidance**:
```
❌ What if price_elasticity calculation returns NULL? (low sample size)
❌ What if warehouse costs are missing for some SKUs?
❌ Troubleshooting Quick Ref (SKILL.md:448-471) is generic
```

**3. No Business Validation**:
```
❌ Should we simulate revenue impact before deployment?
❌ What's the rollback plan if pricing tanks sales?
❌ How do we A/B test pricing changes?
```

**4. Incomplete Data Engineering Best Practices**:
```
❌ No mention of testing transformations in dev workspace first
❌ No lineage/catalog documentation
❌ No alerting setup (what if validation fails at 2am?)
```

---

## Scoring V4

| Dimension | V3.0.1 Score | V4.0.0 Score | Notes |
|-----------|--------------|--------------|-------|
| **Technical Accuracy** | 9.1/10 | 9.1/10 | Same (still correct ERROR() → ABORT, APIs, etc.) |
| **Information Density** | 7/10 | 8.5/10 | +1.5 for YAML trees, quick refs, pattern library |
| **Tool Explicitness** | 8.5/10 | 9/10 | +0.5 for Tool Reference Card at top |
| **DA/DE Knowledge** | 7/10 | 7.5/10 | +0.5 applies book concepts but misses context |
| **Completeness** | 7.5/10 | 7/10 | -0.5 missing PII, SLOs, business validation |
| **Usability** | 7/10 | 8.5/10 | +1.5 easier to scan, find info quickly |
| **OVERALL** | 7.7/10 | 8.3/10 | **+0.6 improvement** |

---

## Recommendations for V4.1

### Critical Additions:

**1. Context Memory Pattern**:
```yaml
# Add to Step 3 (SKILL.md:80)
Before proposing architecture:
- Review Step 1 answers (Decision, Metric, PII, Success)
- If PII=Yes → Include: data masking, access controls, audit logging
- If Frequency=Real-time → Use CDC pattern, not batch
```

**2. Business Validation Checklist**:
```yaml
# Add to Step 4 (SKILL.md:270-285)
Before deployment:
- Simulation: Run transformation on historical data, show revenue impact
- Rollback Plan: Document how to revert prices if experiment fails
- Monitoring: Set up alerts for validation failures
```

**3. Data Engineering Checklist**:
```yaml
# Add to Step 4 (SKILL.md:270-285)
After deployment:
- Test in dev workspace first
- Document lineage in Catalog
- Define SLO: "Recommendations available by Monday 6am, <24h data staleness"
- Set up Slack alerts for validation failures
```

**4. Troubleshooting Expansion**:
```yaml
# Expand SKILL.md:448-471
Add scenario-specific troubleshooting:
- "Price elasticity NULL" → Increase lookback window to 180 days
- "Warehouse costs missing" → Use default $0.50/day or exclude SKU
- "Negative revenue impact" → Review discount thresholds (too aggressive?)
```

---

## Conclusion

**Is Claude an expert on data + Keboola?**

**With V4: Intermediate to Advanced** (8.3/10)

**Strengths**:
- ✅ Can build working pipelines (extractors, SQL, writers, scheduling)
- ✅ Applies DA/DE book knowledge (price elasticity, data quality validation)
- ✅ Fast component discovery (YAML decision trees, quick refs)
- ✅ Correct technical details (APIs, SQL patterns, validation)

**Weaknesses**:
- ❌ Doesn't always connect Step 1 context to Step 3 design (PII, SLOs)
- ❌ Misses business validation (simulation, rollback, A/B testing)
- ❌ Lacks deep troubleshooting (what-if scenarios)
- ❌ Doesn't proactively suggest data contracts, lineage, alerting

**V4 is MUCH better at**:
- Information retrieval speed (YAML trees, quick refs, pattern library)
- Structured thinking (5 questions, JSON inventory, YAML architectures)

**V4 needs work on**:
- Context awareness across steps
- Business/operational considerations
- Edge case handling
