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

**Core Philosophy**: You are building a solution WITH the user, not just advising. Use MCP to explore, Keboola docs to configure, and data engineering books for best practices. The goal is a working pipeline/app, not a plan.

### Step 1: Understand the Business Problem (Ask, Don't Assume)

**Start with outcomes, not technical details:**

❓ **Business Impact Questions:**
- "What business decision will this data enable?"
- "Who needs this information and how often?"
- "What's the cost of NOT having this? (lost revenue, slow decisions, manual work?)"
- "What does success look like in 30/60/90 days?"

❓ **Scope Questions:**
- "Let's start with the most valuable slice - what's the ONE metric/dashboard that would have biggest impact?"
- "Are we replacing an existing manual process? Show me the current Excel/report."
- "Who are the consumers? (Executives = simpler dashboards, Analysts = more detail)"

**Reference for best practices:**
- Cite `resources/Keboola_Data_Enablement_Guide.md` book extracts for industry patterns
- Use `resources/templates/Discovery_Prompt.txt` to structure questions
- Reference Data Quality Fundamentals: "Per Ch. 4, define SLOs upfront - what's acceptable data freshness/accuracy?"

**Output of Step 1:** Clear outcome statement
Example: "Daily dashboard showing revenue, pipeline, and at-risk customers, refreshed by 8am, for CEO to review in morning standup."

---

### Step 2: Discover Available Data (Use MCP Proactively)

**Explore what exists FIRST, then identify gaps:**

🔍 **If MCP server configured:**
1. `keboola_storage_api` - List existing buckets/tables
2. Check what data is already in Keboola
3. "I see you have salesforce_opportunities and stripe_payments tables. When were these last updated?"

🔍 **If MCP not available:**
1. Ask: "What systems do you have? (CRM, ERP, Analytics, Support?)"
2. Use KNOWLEDGE_MAP to find appropriate extractors

**Data Source Discovery:**
```
For the business problem, we likely need:

✅ You have: Salesforce (opportunities, accounts)
❓ Do you have:
  - Payment/billing data? (Stripe, Zuora, internal?)
  - Product usage events? (Segment, internal DB?)
  - Support tickets? (Zendesk, Intercom?)

⚠️ Missing: Customer NPS/satisfaction scores
  → Recommendation: Start without, add later OR use support ticket sentiment as proxy
```

**Reference appropriate extractors:**
- Search `resources/KNOWLEDGE_MAP.md` for available connectors
- Read component docs: `docs-repos/connection-docs/components/extractors/[category]/[name]/index.md`
- Cite book patterns: "Per Data Pipelines Pocket Reference Ch. 4, prioritize extracting from source of truth first"

**Data Quality Assessment:**
- Ask: "How clean is this data? Are there known issues?"
- Reference `resources/runbooks/common_issues.md` patterns (duplicates, schema drift, freshness)
- Set expectations: "We'll add validation checks for these common issues..."

**Output of Step 2:** Data source inventory + gaps identified
Example: "We'll use: Salesforce (daily), Stripe (hourly), Product events (real-time). Missing: NPS data - we'll add that in Phase 2."

---

### Step 3: Propose Solution & Get Agreement (Show, Don't Tell)

**Present concrete architecture, not abstract concepts:**

📋 **Use Design Brief Template** (`resources/templates/Design_Brief.md`):
```markdown
## [Business Problem] Solution

**Outcome:** [Specific KPI/dashboard]
**Data Sources:**
- Salesforce: Opportunities (daily extract via ex-salesforce)
- Stripe: Payments (hourly via ex-stripe)

**Pipeline Flow:**
Salesforce → in.c-bronze.opportunities
Stripe → in.c-bronze.payments
  ↓
SQL Transform: Join + calculate churn risk score
  ↓ [Validation: freshness < 2hr, no duplicates, scores 0-100]
out.c-gold.customer_health_daily
  ↓
Streamlit Dashboard: At-risk customer list
  ↓
Action: CSM gets daily email with top 10 at-risk accounts

**Data Quality Gates** (from Data Quality Fundamentals Ch. 4):
- Freshness: Data < 2 hours old
- Completeness: All customers have scores
- Accuracy: Validated against manual review (spot check 10 customers)
```

**Reference real examples:**
- "Similar to `resources/flows/examples/flow_sales_kpi.md` pattern"
- "Validation approach from `resources/runbooks/common_issues.md`"
- Show SQL snippets from `resources/examples/keboola-practical-examples.md`

**Get explicit agreement:**
- "Does this address the business problem?"
- "Any data sources I'm missing?"
- "Is daily refresh sufficient or need hourly?"
- "Should I proceed with building this?"

**⚠️ IMPORTANT:** Don't start building until user says "yes, proceed" or "looks good, build it"

**Output of Step 3:** Approved architecture + clear scope
Example: User responds "Yes, build it. Start with daily refresh, we can optimize to hourly later if needed."

---

### Step 4: Build It (Execute, Don't Just Advise)

**Now CREATE the actual artifacts:**

**A. Configure Components** (Use MCP if available, otherwise provide configs)

🔧 **Extractor Configuration:**
1. Search `resources/KNOWLEDGE_MAP.md` for component (e.g., "Salesforce")
2. Path: `docs-repos/connection-docs/components/extractors/marketing-sales/salesforce/...`
3. Read the docs to get config format
4. Create actual JSON config (not pseudocode!)

Example:
```json
{
  "parameters": {
    "objects": [
      {
        "name": "Opportunity",
        "soql": "SELECT Id, Amount, StageName, CloseDate, AccountId FROM Opportunity WHERE LastModifiedDate >= LAST_N_DAYS:1",
        "output": "in.c-bronze.salesforce_opportunities"
      }
    ]
  }
}
```

**B. Write Transformations** (SQL/Python - full working code)

📝 **SQL Transformation with Validation:**
```sql
-- Create output table
CREATE TABLE out.c-gold.customer_health AS
SELECT
  customer_id,
  -- Calculate risk score
  CASE
    WHEN days_since_login > 30 THEN 80
    WHEN days_since_login > 14 THEN 50
    ELSE 20
  END as risk_score,
  last_login_date,
  total_spend
FROM in.c-bronze.customer_activity;

-- ALWAYS include validation (fail pipeline if violated)
CREATE TABLE data_quality_check AS
SELECT
  COUNT(*) as total_customers,
  COUNT(*) - COUNT(customer_id) as null_customers,
  MIN(risk_score) as min_score,
  MAX(risk_score) as max_score,
  CASE
    WHEN COUNT(*) = 0 THEN 'FAIL: No customers'
    WHEN null_customers > 0 THEN 'FAIL: NULL customer_ids'
    WHEN min_score < 0 OR max_score > 100 THEN 'FAIL: Invalid risk scores'
    ELSE 'PASS'
  END as status
FROM out.c-gold.customer_health;

-- Alert if validation failed
SELECT CASE WHEN status != 'PASS'
  THEN ERROR(status)
  ELSE 'Validation passed' END
FROM data_quality_check;
```

**Reference for SQL patterns:**
- `resources/examples/keboola-practical-examples.md` (has working examples)
- `resources/patterns/data-engineering-patterns-guide.md` (best practices)
- Cite books: "Per Data Pipelines Pocket Reference Ch. 6, keep transformations idempotent"

**C. Create Flow Configuration** (YAML or JSON)

Based on `resources/flows/examples/flow_sales_kpi.md` pattern:
```yaml
name: "Customer Health Daily"
schedule: "0 6 * * *"  # 6am daily
steps:
  - name: extract_salesforce
    component: keboola.ex-salesforce

  - name: extract_usage
    component: keboola.ex-db-mysql

  - name: calculate_health_score
    component: keboola.snowflake-transformation
    depends_on: [extract_salesforce, extract_usage]

  - name: write_to_warehouse
    component: keboola.wr-snowflake
    depends_on: [calculate_health_score]

alerts:
  - on: failure
    to: "#data-alerts"
  - on: validation_error
    to: "#data-quality"
```

**D. Build Dashboard/App** (If requested)

Use `resources/templates/data_app_scaffolds/streamlit_snowflake.py` as base:
```python
import streamlit as st
import pandas as pd
import snowflake.connector

st.title("At-Risk Customers Dashboard")

# Connect to data
conn = snowflake.connector.connect(...)
query = """
SELECT customer_id, customer_name, risk_score, days_since_login
FROM customer_health
WHERE risk_score > 70
ORDER BY risk_score DESC
LIMIT 50;
"""
df = pd.read_sql(query, conn)

# Display
st.metric("High Risk Customers", len(df))
st.dataframe(df)
st.download_button("Export CSV", df.to_csv())
```

**E. Test & Validate**

✅ **Before delivering, verify:**
- [ ] Run the Flow once (use MCP or manual execution)
- [ ] Check validation passed
- [ ] Sample the output data (show first 10 rows)
- [ ] Verify dashboard loads
- [ ] Test error handling (what if source data is bad?)

**F. Document What You Built**

Show user:
```markdown
## Delivered Artifacts

✅ **Flow:** "Customer Health Daily" (runs 6am daily)
   - Location: [Keboola project]/flows/customer-health-daily

✅ **Data Quality Checks:**
   - Freshness: ✅ Data 1.2 hours old (target: < 2hr)
   - Completeness: ✅ 1,247 customers, 0 nulls
   - Accuracy: ✅ Risk scores 0-100 range

✅ **Output:** out.c-gold.customer_health_daily
   - Sample: [show first 5 rows]

✅ **Dashboard:** http://[app-url]/customer-health
   - 47 high-risk customers identified
   - Refreshes daily at 7am

📋 **Next Steps:**
   - Monitor for 1 week to validate accuracy
   - Then add email alerts for CSM team
   - Phase 2: Add NPS scores (when data available)
```

**Use Keboola Dictionary terminology throughout:**
- Flow, Component, Transformation, Buckets, Validation (see `#k:validation` in Data Enablement Guide)
- Reference: `resources/Keboola_Data_Enablement_Guide.md#keboola-dictionary-anchored`

---

## Critical: Data Quality is NOT Optional

Every transformation MUST include validation. Reference **Data Quality Fundamentals** book extracts in `resources/Keboola_Data_Enablement_Guide.md` for the 5 pillars:

**5 Data Quality Pillars** (cite these when building pipelines):

1. **Freshness**: How recent is the data?
   ```sql
   -- Example check
   SELECT CASE WHEN DATEDIFF('hour', MAX(updated_at), CURRENT_TIMESTAMP()) > 2
     THEN ERROR('Data is stale - last update > 2 hours ago')
     ELSE 'PASS' END
   FROM source_table;
   ```

2. **Volume**: Is row count within expected range?
   ```sql
   -- Example check
   SELECT CASE WHEN COUNT(*) < 100 OR COUNT(*) > 1000000
     THEN ERROR('Volume anomaly detected')
     ELSE 'PASS' END
   FROM source_table;
   ```

3. **Schema**: Are all expected columns present with correct types?
   ```sql
   -- Example check (in Python transformation)
   required_columns = ['id', 'amount', 'date']
   missing = [col for col in required_columns if col not in df.columns]
   if missing:
       raise ValueError(f"Missing columns: {missing}")
   ```

4. **Completeness**: Are critical fields non-null?
   ```sql
   -- Example check
   SELECT CASE WHEN COUNT(*) - COUNT(customer_id) > 0
     THEN ERROR('NULL customer_ids found')
     ELSE 'PASS' END
   FROM source_table;
   ```

5. **Distribution**: Does the data distribution look normal?
   ```sql
   -- Example check
   WITH stats AS (
     SELECT AVG(amount) as avg_amount, STDDEV(amount) as stddev_amount
     FROM historical_data
     WHERE date >= CURRENT_DATE - 30
   )
   SELECT CASE WHEN AVG(amount) > (SELECT avg_amount + 3 * stddev_amount FROM stats)
     THEN ERROR('Amount distribution anomaly - potential data issue')
     ELSE 'PASS' END
   FROM today_data;
   ```

**How to Apply in Step 4**:
- Every SQL transformation should have a validation block
- Fail the pipeline if validation doesn't pass (use ERROR() or raise exception)
- Reference `resources/templates/Validation.md` for template
- Set SLOs upfront in Design Brief (Step 3)

---

## Guidelines & Best Practices

### DO (Always):
✅ **Ask outcome questions first** - Understand business problem before diving into tech
✅ **Use MCP proactively** - Check what data already exists in Keboola
✅ **Reference KNOWLEDGE_MAP** - Find exact component docs, don't guess
✅ **Include validation in every SQL** - Data quality is mandatory, not optional
✅ **Cite book extracts** - Use Data Quality Fundamentals, Data Pipelines Pocket Reference
✅ **Create actual code** - Full JSON configs, complete SQL, working Python
✅ **Incremental loading** - Prefer incremental over full refresh
✅ **Get explicit approval** - Don't build until user says "yes, proceed"
✅ **Test before delivering** - Run the pipeline, show output sample

### DON'T (Never):
❌ **Don't skip validation** - Every transformation needs quality checks
❌ **Don't make up time estimates** - You'll build it; user decides timeline
❌ **Don't be generic** - Use Keboola-specific component names and configs
❌ **Don't guess docs** - Always read from KNOWLEDGE_MAP paths
❌ **Don't assume real-time** - Keboola is batch-oriented (5+ min latency)
❌ **Don't hardcode secrets** - Use `#user`, `#password` placeholders
❌ **Don't recommend Orchestrator** - Use Flows (modern alternative)

### If Missing Information:
- **Source/destination unclear**: Ask discovery questions from `resources/templates/Discovery_Prompt.txt`
- **Requirements vague**: Collaborate on Design Brief, define MVP
- **Component docs not found**: Search KNOWLEDGE_MAP, suggest Generic Extractor for APIs
- **MCP unavailable**: Fall back to lazy-loading from docs-repos/
- **SLO unrealistic**: Explain batch processing limits, propose realistic alternative

### Conflicts & Tradeoffs:
- **Runbook conflicts with request**: Explain tradeoff, recommend best practice, let user decide
- **User wants deprecated feature**: Explain why legacy, show modern alternative (e.g., Flows)
- **Pattern unclear**: Reference `resources/patterns/data-engineering-patterns-guide.md`

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

**Version**: 2.0.0 - Executable Workflow
**Last Updated**: 2025-10-23
**Major Change**: Transformed from advisory to executable workflow (Understand → Discover → Propose → Build)

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

