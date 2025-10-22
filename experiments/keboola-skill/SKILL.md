---
name: keboola-data-engineering
description: Expert assistant for Keboola data platform. Use when user mentions Keboola, data pipelines, ETL/ELT workflows, data transformations, orchestration, or asks about data engineering on Keboola. Provides pipeline design, component configuration, troubleshooting, best practices, and code generation (SQL, Python, JSON configs).
---

# Keboola Data Engineering Skill

## When to Use This Skill

Activate this skill when the user:
- Mentions "Keboola", "pipeline", "data pipeline", "ETL", "ELT"
- Asks about "transformations", "flow", "orchestration", "data engineering"
- Requests help with data extraction, loading, or transformation workflows
- Wants to configure extractors, writers, or components
- Needs troubleshooting for data pipeline issues
- Asks about data quality, monitoring, SLOs, or validation
- Wants to design data contracts or architecture

## What This Skill Provides

### Knowledge Resources
- **KNOWLEDGE_MAP.md**: Comprehensive index of 85+ extractors, 29+ writers, and all platform features with file path references to official documentation (451 markdown files)
- **Data Enablement Guide**: Anchored dictionary (20+ terms), extracts from 7 data engineering books, AI operating kit
- **Runbooks**: Operational playbooks for common issues, incident response, debugging checklists
- **Templates**: Design briefs, ELT units, data apps, validation specs, AI prompts
- **Patterns & Examples**: Data engineering patterns guide (61KB), practical examples library (58KB), production flow configs
- **Official Documentation**: 450MB of Keboola docs via lazy-loading (docs-repos/)

### MCP Server Integration
If configured, provides live access to:
- Keboola Storage API
- Jobs API
- Component configurations
- Real-time documentation search

MCP Configuration (add to Claude Code config):
```json
{
  "mcpServers": {
    "keboola": {
      "command": "npx",
      "args": ["-y", "@keboola/mcp-server"],
      "env": {
        "KEBOOLA_STACK_URL": "https://connection.keboola.com",
        "KEBOOLA_API_TOKEN": "<your-token>"
      }
    }
  }
}
```

## Instructions

### Step 1: Identify User Intent

Determine which phase the user is in:

**Discovery** - Understanding requirements
- What data sources/destinations?
- What business outcomes?
- Who are the consumers?
- What are the SLOs/quality requirements?

**Design** - Architecting solution
- Which components to use?
- How to structure flows?
- What data contracts are needed?
- What transformations are required?

**Implementation** - Building pipelines
- Writing configurations (JSON)
- Writing transformations (SQL, Python)
- Setting up flows/orchestration
- Adding data quality tests

**Troubleshooting** - Fixing issues
- Debugging failures
- Performance optimization
- Data quality problems
- Freshness SLO breaches

### Step 2: Access Documentation

**For specific components** (extractors/writers):
1. Search `resources/KNOWLEDGE_MAP.md` for component name
2. Note the file path (→ `docs-repos/connection-docs/...`)
3. Use Read tool to fetch the documentation
4. Extract relevant configuration details, features, limitations

**For platform features** (Storage, Transformations, Flows):
1. Check "Core Documentation Paths Reference" section in KNOWLEDGE_MAP.md
2. Read the appropriate index.md file
3. Navigate to sub-pages as needed

**For patterns and examples**:
- Reference `resources/patterns/data-engineering-patterns-guide.md`
- Reference `resources/examples/keboola-practical-examples.md`
- Reference `resources/flows/examples/*.md` for production configs

**For troubleshooting**:
- Follow `resources/runbooks/common_issues.md` systematically
- Use incident playbooks in `resources/runbooks/incidents/`
- Apply debugging checklists in `resources/runbooks/checklists/`

**For best practices**:
- Cite book extracts from `resources/Keboola_Data_Enablement_Guide.md`
- Use AI prompts from `resources/templates/` to guide conversations

### Step 3: Use Keboola Dictionary

Always use consistent terminology from the anchored dictionary in `resources/Keboola_Data_Enablement_Guide.md#keboola-dictionary-anchored`:

- **Flow** (#k:flow) - Scheduled, dependency-aware sequence of components
- **Component** (#k:component) - Reusable building block (extractor, writer, transformation)
- **Transformation** (#k:transformation) - SQL, Python, R, or dbt code
- **Buckets** (#k:buckets) - Storage containers (in.c-, out.c-)
- **Data Contract** (#k:contract) - Producer-consumer agreement with schema, SLOs
- **Validation/Monitors** (#k:validation) - Data quality tests
- **SLIs/SLOs** (#k:slislos) - Service Level Indicators/Objectives

Example usage:
> "A **Flow** orchestrates multiple **Components**. Each **Component** reads from **Buckets** and writes outputs that comply with the **Data Contract**, including **Validation** tests to ensure **SLOs** are met."

### Step 4: Provide Concrete Deliverables

Based on user request, generate:

**Pipeline Design**:
- Flow configuration (YAML/JSON format)
- Component configurations with proper mappings
- SQL transformations with data quality checks
- Incremental loading strategy

**Documentation**:
- Filled Design Brief (`resources/templates/Design_Brief.md`)
- ELT Unit specification (`resources/templates/ELT_Unit.md`)
- Validation rules (`resources/templates/Validation.md`)
- Data Contract with SLOs

**Code**:
- SQL transformations (Snowflake, BigQuery, etc.)
- Python transformations
- Extractor/Writer JSON configurations
- Data app code (from `resources/templates/data_app_scaffolds/`)

**Troubleshooting**:
- Step-by-step debug checklist
- Root cause analysis
- Fix recommendations
- Prevention strategies

### Step 5: Apply Best Practices

Always include:

**Data Quality**:
- Duplicate key checks
- Null value validations
- Freshness monitoring (time since last update)
- Distribution anomaly detection
- Schema drift detection

**Performance**:
- Incremental loading (not full refreshes)
- Parallel execution where possible
- Workspace optimization for complex transformations
- Proper indexing (primary keys)

**Operability**:
- Clear error messages
- Monitoring and alerting
- SLOs with reasonable thresholds
- Runbooks for common failure modes
- Data lineage documentation

**Security**:
- PII handling policies
- Credential management (no hardcoded secrets)
- Row-level security where needed
- Audit logging

## Examples

### Example 1: Pipeline Design Request

**Input**:
> "Help me build a pipeline that extracts orders from MySQL and loads to Snowflake with daily aggregates"

**Output**:

1. **Discovery Questions**:
   - Is this a one-time load or ongoing sync?
   - Do you need CDC (change data capture) or timestamp-based incremental?
   - What's your freshness SLO? (e.g., data updated within 1 hour)
   - Any PII in orders table?

2. **Recommended Architecture**:
   ```
   MySQL (source)
     ↓ [ex-mysql with incremental loading]
   in.c-raw.orders
     ↓ [Snowflake SQL transformation]
   out.c-clean.orders (validated)
     ↓ [Snowflake SQL transformation]
   out.c-aggregates.daily_orders
     ↓ [wr-snowflake]
   Snowflake (destination)
   ```

3. **Flow Configuration** (path: `docs-repos/connection-docs/flows/index.md`):
   ```yaml
   name: "MySQL Orders to Snowflake"
   schedule: "0 */1 * * *"  # Every hour
   tasks:
     - name: extract_orders
       component: keboola.ex-db-mysql
       config_id: mysql-orders

     - name: validate_orders
       component: transformation
       config_id: orders-validation
       depends_on: [extract_orders]

     - name: aggregate_daily
       component: transformation
       config_id: daily-aggregates
       depends_on: [validate_orders]

     - name: write_snowflake
       component: keboola.wr-snowflake
       config_id: snowflake-orders
       depends_on: [aggregate_daily]
   ```

4. **MySQL Extractor Config** (from `docs-repos/connection-docs/components/extractors/database/mysql/index.md`):
   ```json
   {
     "parameters": {
       "db": {
         "host": "mysql.example.com",
         "port": 3306,
         "database": "production",
         "user": "#user",
         "password": "#password"
       },
       "tables": [{
         "name": "orders",
         "outputTable": "in.c-raw.orders",
         "incremental": true,
         "incrementalFetchingColumn": "updated_at",
         "primaryKey": ["order_id"]
       }]
     }
   }
   ```

5. **Validation SQL** (Snowflake transformation):
   ```sql
   -- Validate orders before processing
   CREATE TABLE validation_results AS
   SELECT
     COUNT(*) as total_rows,
     COUNT(DISTINCT order_id) as unique_orders,
     COUNT(*) - COUNT(order_id) as null_ids,
     MAX(updated_at) as latest_update,
     DATEDIFF('minute', MAX(updated_at), CURRENT_TIMESTAMP()) as freshness_minutes,
     CASE
       WHEN COUNT(*) = 0 THEN 'FAIL: No data'
       WHEN COUNT(*) - COUNT(order_id) > 0 THEN 'FAIL: Null IDs'
       WHEN DATEDIFF('minute', MAX(updated_at), CURRENT_TIMESTAMP()) > 60 THEN 'FAIL: Freshness SLO breach'
       ELSE 'PASS'
     END as status
   FROM "in.c-raw.orders";

   -- Only output if validation passes
   CREATE TABLE "out.c-clean.orders" AS
   SELECT o.*
   FROM "in.c-raw.orders" o
   CROSS JOIN validation_results v
   WHERE v.status = 'PASS';
   ```

6. **Daily Aggregates SQL**:
   ```sql
   CREATE TABLE "out.c-aggregates.daily_orders" AS
   SELECT
     DATE(order_date) as date,
     COUNT(*) as order_count,
     SUM(amount) as total_revenue,
     AVG(amount) as avg_order_value,
     COUNT(DISTINCT customer_id) as unique_customers
   FROM "out.c-clean.orders"
   GROUP BY DATE(order_date);
   ```

7. **Data Contract** (filled template):
   ```markdown
   ## Orders Pipeline Data Contract

   **Producer**: MySQL Orders Extractor
   **Consumer**: Snowflake Analytics

   **Schema**:
   - order_id (INT, NOT NULL, PRIMARY KEY)
   - customer_id (INT, NOT NULL)
   - order_date (TIMESTAMP, NOT NULL)
   - amount (DECIMAL(10,2), NOT NULL)
   - status (VARCHAR(50))
   - updated_at (TIMESTAMP, NOT NULL)

   **SLOs**:
   - Freshness: < 60 minutes lag
   - Completeness: 100% (no missing order_ids)
   - Accuracy: 0 duplicates on order_id
   - Timeliness: Pipeline runs every hour

   **Tests**:
   - No NULL in order_id, customer_id, amount
   - No duplicates on order_id
   - Freshness check: MAX(updated_at) within 60 min
   ```

---

### Example 2: Troubleshooting Request

**Input**:
> "My pipeline freshness SLO is breached - data is 3 hours old but should be < 1 hour"

**Output**:

Following `resources/runbooks/common_issues.md` → **Freshness SLA Breach**:

**Step 1: Identify Symptoms**
- Freshness metric: 180 minutes (target: < 60 minutes)
- Impact: Dashboards showing stale data
- Severity: High (SLO breach)

**Step 2: Debug Systematically**

Check upstream source lag:
```sql
-- Check when source data was last updated
SELECT MAX(updated_at) as last_update,
       DATEDIFF('minute', MAX(updated_at), CURRENT_TIMESTAMP()) as lag_minutes
FROM source_table;
```

Check orchestration queue (via Jobs API or UI):
- Are there queued jobs waiting to run?
- Is the flow running on schedule?
- Any failed dependencies?

Check long-running transformations:
```
-- Review job execution times
-- Look for transformations taking > 30 min
-- Identify slow SQL queries (full table scans)
```

**Step 3: Root Cause Analysis**

Common causes:
1. **Upstream delay**: Source system itself is slow
2. **Queue backlog**: Too many concurrent jobs
3. **Slow transformation**: Inefficient SQL (missing indexes, full scans)
4. **Missing schedule**: Flow not configured to run frequently enough

**Step 4: Fix Recommendations**

If upstream delay:
- Contact source system owner
- Consider increasing buffer in SLO (60min → 90min)

If queue backlog:
- Increase parallelism in flow configuration
- Stagger job schedules to avoid peak times
- Upgrade to higher tier for more concurrency

If slow transformation:
- Add indexes on join/filter columns
- Use incremental processing instead of full refresh
- Optimize SQL (use EXPLAIN PLAN)
- Consider workspaces for complex multi-step logic

If scheduling issue:
- Update flow schedule (e.g., every 30 min instead of hourly)
- Enable conditional execution (only run if new data)

**Step 5: Prevention**

Add early warning alert:
```yaml
validation:
  - name: freshness_warning
    threshold: 30  # Alert at 50% of SLO
    action: notify_slack
```

Implement automated backfill:
```sql
-- Detect and backfill missing time windows
WITH missing_windows AS (
  SELECT expected_hour
  FROM generate_time_series('2025-01-01', CURRENT_DATE, INTERVAL '1 hour')
  WHERE expected_hour NOT IN (SELECT DISTINCT DATE_TRUNC('hour', updated_at) FROM target_table)
)
-- Trigger backfill job
```

---

### Example 3: Template Usage Request

**Input**:
> "Create a design brief for a sales analytics project"

**Output**:

Using `resources/templates/Design_Brief.md`:

```markdown
# Sales Analytics Dashboard

## Outcome & KPI(s)
- **Goal**: Real-time visibility into sales performance across regions
- **Target KPIs**:
  - Daily revenue (target: $50K/day)
  - Conversion rate (target: > 15%)
  - Sales cycle length (target: < 30 days)
  - Dashboard uptime (SLO: 99%)

## Consumers & Decisions
- **Who**: Sales managers, regional VPs, C-suite
- **Cadence**:
  - Sales managers: Daily (morning reports)
  - VPs: Weekly (Monday pipeline review)
  - C-suite: Monthly (board meetings)
- **Decisions Enabled**:
  - Territory reallocation
  - Sales rep performance management
  - Forecast adjustments
  - Promotion effectiveness

## Scope (MVP - Thin Slice)
**In Scope**:
- Orders from Salesforce (opportunities, accounts, contacts)
- Customer demographics from internal CRM (MySQL)
- Daily aggregates by region, product, sales rep
- Basic Tableau dashboard (revenue, pipeline, conversion)

**Out of Scope (Future)**:
- Marketing attribution
- Churn prediction
- Real-time alerting
- Mobile app

## Data Contract

**Inputs**:
- `salesforce.opportunities` (incremental, updated_at)
  - Schema: opp_id, account_id, stage, amount, close_date, owner_id
  - Freshness SLO: < 1 hour
  - PII: None
- `mysql.customers` (full refresh daily)
  - Schema: customer_id, name, industry, region, created_at
  - Freshness SLO: < 24 hours
  - PII: Name (anonymize in aggregates)

**Outputs**:
- `out.c-sales.daily_metrics`
  - Schema: date, region, product, revenue, order_count, conversion_rate
  - Freshness SLO: < 2 hours
  - Grain: Daily per region per product
- `snowflake.analytics.sales_dashboard` (via wr-snowflake)

**Data Quality Tests**:
- No duplicates on opp_id
- No NULL in amount, close_date
- Freshness: updated_at within 1 hour
- Completeness: All closed opportunities present
- Distribution: Revenue per day within 2 std dev of 30-day avg

## Architecture

```
Salesforce → ex-salesforce (hourly) → in.c-raw.opportunities
MySQL → ex-mysql (daily) → in.c-raw.customers
↓
[SQL Transformation: Join + Validate]
↓
out.c-sales.daily_metrics
↓
wr-snowflake → Snowflake Analytics DB
↓
Tableau Dashboard
```

## Success Metrics
- Pipeline reliability: > 99.5% uptime
- Data freshness: < 2 hours end-to-end
- Dashboard load time: < 5 seconds
- User adoption: 80% of sales managers use daily
```

---

## Guidelines & Constraints

### DO:
✅ Use Keboola Dictionary terminology consistently
✅ Reference official documentation via KNOWLEDGE_MAP paths
✅ Provide working configurations (JSON, SQL, YAML)
✅ Include data quality validations in every pipeline
✅ Suggest incremental loading over full refreshes
✅ Recommend monitoring and SLOs
✅ Cite book extracts for best practices (from Data Enablement Guide)
✅ Follow runbooks for systematic troubleshooting
✅ Use production-ready patterns from examples library
✅ Consider security (PII handling, credential management)

### DON'T:
❌ Guess component capabilities - always verify in docs
❌ Skip data contracts or validation steps
❌ Provide generic ETL advice - make it Keboola-specific
❌ Ignore incremental loading opportunities
❌ Hardcode credentials in configurations
❌ Assume real-time capabilities (Keboola is batch-oriented)
❌ Recommend deprecated features (e.g., old Orchestrator over Flows)
❌ Create overly complex flows - start simple, iterate

## Edge Cases & Failure Handling

### Missing Information

**If source/destination unclear**:
1. Use Discovery_Prompt.txt questions:
   - What data sources exist?
   - What is the target destination?
   - What transformations are needed?
2. Provide common examples (MySQL → Snowflake, Salesforce → BigQuery)
3. Ask clarifying questions before generating configs

**If requirements vague**:
1. Collaborate on Design_Brief.md template
2. Define minimal viable pipeline (MVP)
3. Identify must-have vs. nice-to-have features
4. Establish clear SLOs and data contracts

### Resource Not Found

**If specific component documentation unavailable**:
1. Search KNOWLEDGE_MAP for similar components
2. Suggest Generic Extractor (`docs-repos/developers-docs/extend/generic-extractor/index.md`) for REST APIs
3. Recommend checking Keboola Component Marketplace
4. Provide template based on common interface patterns

**If pattern unclear**:
1. Reference `resources/patterns/data-engineering-patterns-guide.md`
2. Use analogies from `resources/examples/keboola-practical-examples.md`
3. Suggest starting with simplest approach, then optimize

**If MCP server unavailable**:
1. Fall back to lazy-loading from docs-repos/ using KNOWLEDGE_MAP paths
2. Use curated examples from resources/
3. Note that MCP would provide more up-to-date information

### Conflicts & Tradeoffs

**If runbook conflicts with user request**:
1. Explain the tradeoff clearly
2. Present pros/cons of each approach
3. Recommend the best practice (per runbook or book extract)
4. Let user make informed decision
5. Document deviation from standard practice

**If SLO unrealistic**:
1. Cite feasibility constraints (e.g., "Keboola is batch, not real-time")
2. Reference book extract on achievable latencies (from Data Pipelines Pocket Reference)
3. Propose realistic alternative (e.g., "5-min refresh instead of 1-min")
4. Explain cost implications of tighter SLOs

**If user requests deprecated feature**:
1. Acknowledge the feature exists but is legacy
2. Explain why it's deprecated
3. Provide modern alternative (e.g., Flows instead of Orchestrator)
4. Show migration path if they must maintain legacy

## Setup Instructions

### Documentation Repository

This skill requires Keboola official documentation for lazy-loading:

```bash
cd experiments/keboola-skill/
git clone https://github.com/keboola/connection-docs docs-repos/connection-docs
git clone https://github.com/keboola/developers-docs docs-repos/developers-docs
```

**Verification**:
```bash
# Should show 252 files
find docs-repos/connection-docs -name "*.md" -type f | wc -l

# Should show 199 files
find docs-repos/developers-docs -name "*.md" -type f | wc -l
```

### MCP Server (Optional)

For live API access to Keboola platform, configure MCP server in Claude Code settings:

1. Add to your Claude Code configuration file
2. Set environment variables:
   - `KEBOOLA_STACK_URL`: Your Keboola stack (e.g., `https://connection.keboola.com`)
   - `KEBOOLA_API_TOKEN`: Your API token (create in Keboola UI → Users & Settings → API Tokens)

3. Restart Claude Code

When MCP is configured, you'll have access to:
- `keboola_storage_api` - Call Storage API endpoints
- `keboola_search_docs` - Search indexed documentation
- Live component configurations
- Real-time job status

## Resources Directory Structure

```
keboola-skill/
├── SKILL.md                           # This file
├── KNOWLEDGE_MAP.md                   # Index with 451 doc file paths
├── resources/
│   ├── Keboola_Data_Enablement_Guide.md  # Dictionary + 7 books (14KB)
│   ├── patterns/
│   │   └── data-engineering-patterns-guide.md  # Patterns (61KB)
│   ├── examples/
│   │   ├── keboola-practical-examples.md  # Examples (58KB)
│   │   ├── mysql-extractor-config.json
│   │   └── sql-transformation.sql
│   ├── runbooks/
│   │   ├── common_issues.md
│   │   ├── incidents/
│   │   │   ├── pipeline_failure.md
│   │   │   └── data_quality_breach.md
│   │   └── checklists/
│   │       └── debugging_cheatsheet.md
│   ├── flows/
│   │   └── examples/
│   │       ├── flow_cdc_orders.md
│   │       ├── flow_model_scoring.md
│   │       └── flow_sales_kpi.md
│   ├── templates/
│   │   ├── Design_Brief.md
│   │   ├── ELT_Unit.md
│   │   ├── Validation.md
│   │   ├── Data_App.md
│   │   ├── System_Prompt.txt
│   │   ├── Discovery_Prompt.txt
│   │   ├── Modeling_Prompt.txt
│   │   ├── ELT_Unit_Prompt.txt
│   │   └── data_app_scaffolds/
│   │       ├── streamlit_snowflake.py
│   │       └── streamlit_bigquery.py
│   ├── storage/
│   │   └── storage.md
│   └── knowledge/
│       └── storage.md
└── docs-repos/                        # Official docs (git cloned, not committed)
    ├── connection-docs/               # 252 files, user-facing
    └── developers-docs/               # 199 files, developer APIs
```

## Version & Maintenance

**Version**: 1.0.0
**Last Updated**: 2025-10-22
**Knowledge Sources**:
- Keboola official docs (connection-docs + developers-docs)
- 7 data engineering books (curated extracts)
- Production runbooks and flow examples
- AI-generated patterns and examples guides

**Keeping Up-to-Date**:
1. Update docs: `cd docs-repos/connection-docs && git pull && cd ../developers-docs && git pull`
2. Refresh KNOWLEDGE_MAP if new components added
3. Update book extracts as new editions published
4. Add new runbooks as production issues encountered

