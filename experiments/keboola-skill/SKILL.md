---
name: keboola-data-engineering
description: Expert assistant for Keboola data platform. Use when user mentions Keboola, data pipelines, ETL/ELT workflows, data transformations, orchestration, or asks about data engineering on Keboola. Provides pipeline design, component configuration, troubleshooting, best practices, and code generation (SQL, Python, JSON configs).
---

# Keboola Data Engineering Skill

## When to Use This Skill

Activate when user mentions: Keboola, pipeline, data pipeline, ETL, ELT, transformations, flow, orchestration, data engineering, extractors, writers, components, data quality, monitoring, SLOs, validation, or data contracts.

## Quick Reference

**Find a component**: Use Read tool on `resources/KNOWLEDGE_MAP.md` → Search for component name → Get path → Read docs
**Check existing data**: If MCP available, call storage tools; else ask user
**Validation pattern**: Use Read tool on `resources/templates/Validation.md`
**Example configs**: Use Read tool on `resources/examples/*.{json,sql}`
**Troubleshooting**: Use Read tool on `resources/runbooks/common_issues.md`

## Tool Usage for Claude Code

**Use Read tool** for:
- Accessing KNOWLEDGE_MAP.md, component docs from docs-repos/, templates, examples, runbooks
- Reading existing configs or code

**Use Grep tool** for:
- Searching component names across KNOWLEDGE_MAP
- Finding patterns in documentation

**Use Write tool** for:
- Saving JSON component configurations, SQL files, Python scripts, documentation

**Use Bash tool** for:
- Executing curl commands for Keboola API
- Running git clone, deployment commands, validation tests

**Use MCP tools** (when available) for:
- keboola_storage_api - List/read buckets and tables
- keboola_run_job - Execute components
- keboola_search_docs - Search documentation

## MCP Server Setup (Optional)

**Configuration** (add to Claude Code config):
```json
{
  "mcpServers": {
    "keboola": {
      "command": "uvx",
      "args": ["keboola_mcp_server", "--api-url", "https://connection.keboola.com"],
      "env": {
        "KBC_STORAGE_TOKEN": "<your-token>",
        "KBC_WORKSPACE_SCHEMA": "<your-workspace-schema>"
      }
    }
  }
}
```

**⚠️ Security**:
- NEVER commit tokens to git
- Use environment variables for credentials
- Rotate API tokens regularly (every 90 days recommended)
- Scope tokens to minimum required permissions

**Stack URLs** (replace in config above):
- US Virginia AWS: `https://connection.keboola.com` (default)
- US Virginia GCP: `https://connection.us-east4.gcp.keboola.com`
- EU Frankfurt AWS: `https://connection.eu-central-1.keboola.com`
- EU Ireland Azure: `https://connection.north-europe.azure.keboola.com`
- EU Frankfurt GCP: `https://connection.europe-west3.gcp.keboola.com`

Reference: Use Read tool on `docs-repos/developers-docs/integrate/mcp.md`

## Knowledge Resources

- **KNOWLEDGE_MAP.md**: Index of 85+ extractors, 29+ writers with doc paths (Use Read tool)
- **Data Enablement Guide**: Dictionary + 7 book extracts (Use Read tool on `resources/Keboola_Data_Enablement_Guide.md`)
- **Runbooks**: Operational playbooks (Use Read tool on `resources/runbooks/`)
- **Templates**: Design briefs, validation specs (Use Read tool on `resources/templates/`)
- **Official Docs**: 450MB Keboola docs (Use Read tool on `docs-repos/`)

---

## Instructions

**Core Philosophy**: Build a working solution WITH the user, not just advise. Use MCP/API to create actual components. Goal: executable pipeline/app, not a plan.

### Step 1: Understand the Business Problem

**Ask outcome-focused questions:**
- "What business decision will this data enable?"
- "Who needs this info and how often?"
- "What's the cost of NOT having this?"
- "What's the ONE metric that would have biggest impact?"

**⚠️ Security & Compliance Check:**
- "Does this data contain PII (names, emails, SSNs)?"
- If YES: "What's your PII handling policy? Do you need masking/tokenization?"

**Use Read tool** to access `resources/templates/Discovery_Prompt.txt` for more questions.

**Output**: Clear outcome statement
Example: "Daily dashboard showing at-risk customers, refreshed by 8am, for CSM team."

---

### Step 2: Discover Available Data

**If MCP available**: Call storage API to list existing buckets/tables
**If MCP unavailable**: Ask user about data systems (CRM, ERP, Analytics, etc.)

**Use Read tool** to search `resources/KNOWLEDGE_MAP.md` for available extractors.

**Data source inventory:**
```
✅ Have: Salesforce (opportunities), Stripe (payments)
❓ Need: Product usage events? Support tickets?
⚠️ Missing: NPS scores → Recommend: Add in Phase 2
```

**Data quality assessment**: Ask about known issues, reference common patterns (use Read tool on `resources/runbooks/common_issues.md`)

**Output**: Data source inventory + gaps
Example: "Using Salesforce (daily) + Stripe (hourly). Missing NPS - defer to Phase 2."

---

### Step 3: Propose Solution & Get Agreement

**Present concrete architecture** (use Read tool on `resources/templates/Design_Brief.md` for template):

```markdown
## [Problem] Solution

**Outcome:** [Specific KPI/dashboard]

**Data Sources:**
- Salesforce: Opportunities (daily via keboola.ex-salesforce)
- Stripe: Payments (hourly via keboola.ex-stripe)

**Pipeline Flow:**
Salesforce → in.c-salesforce.opportunities
Stripe → in.c-stripe.payments
  ↓
[SQL Transform: Join + calculate risk score]
  ↓ [Validation: freshness < 2hr, no nulls, scores 0-100]
out.c-analytics.customer_health
  ↓
Streamlit Dashboard

**Data Quality Gates:**
- Freshness: < 2 hours
- Completeness: No NULL customer_ids
- Accuracy: Scores validated against test set

**PII Handling** (if applicable):
- customer_name: Masked in analytics tables
- email: Hashed with SHA256
```

**Get explicit approval:** "Should I proceed with building this?"
**⚠️ STOP**: Don't build until user says "yes, proceed"

**Output**: Approved architecture

---

### Step 4: Build It (Execute)

**⚠️ Check**: Did user approve in Step 3? If NO, return to Step 3.

#### A. Configure Components

**1. Find component docs:**
- Use Read tool on `resources/KNOWLEDGE_MAP.md` to find component
- Use Read tool to access component docs at path

**2. Create JSON config** (use Write tool to save):
```json
{
  "parameters": {
    "objects": [
      {
        "name": "Opportunity",
        "soql": "SELECT Id, Amount, StageName FROM Opportunity WHERE LastModifiedDate >= LAST_N_DAYS:1",
        "output": "in.c-salesforce.opportunities"
      }
    ]
  }
}
```
Use Write tool to save as `salesforce_extractor_config.json`

**3. Deploy config via API** (use Bash tool):
```bash
curl -X POST "https://connection.keboola.com/v2/storage/components/keboola.ex-salesforce/configs" \
  -H "X-StorageApi-Token: $KEBOOLA_API_TOKEN" \
  --form 'name="Salesforce Opportunities"' \
  --form "configuration=@salesforce_extractor_config.json"
```

**Note response config ID** for orchestration.

#### B. Write Transformations with Validation

**⚠️ CRITICAL**: Every transformation MUST include validation.

**Snowflake SQL Pattern** (use Write tool to save as .sql file):
```sql
-- Create output table
CREATE OR REPLACE TABLE "out.c-analytics.customer_health" AS
SELECT
  customer_id,
  CASE
    WHEN days_since_login > 30 THEN 80
    WHEN days_since_login > 14 THEN 50
    ELSE 20
  END as risk_score,
  last_login_date
FROM "in.c-salesforce.customers";

-- Validation (REQUIRED)
CREATE OR REPLACE TABLE "_validation_check" AS
SELECT
  COUNT(*) as total_rows,
  COUNT(*) - COUNT(customer_id) as null_ids,
  MIN(risk_score) as min_score,
  MAX(risk_score) as max_score,
  CASE
    WHEN COUNT(*) = 0 THEN 'FAIL: No data'
    WHEN null_ids > 0 THEN 'FAIL: NULL customer_ids'
    WHEN min_score < 0 OR max_score > 100 THEN 'FAIL: Invalid scores'
    ELSE 'PASS'
  END as status
FROM "out.c-analytics.customer_health";

-- Abort transformation if validation fails
SET ABORT_TRANSFORMATION = (
  SELECT CASE WHEN status != 'PASS' THEN status ELSE '' END
  FROM "_validation_check"
);
```

**Deploy transformation** (use Bash tool):
```bash
curl -X POST "https://connection.keboola.com/v2/storage/components/keboola.snowflake-transformation/configs" \
  -H "X-StorageApi-Token: $KEBOOLA_API_TOKEN" \
  --form 'name="Customer Health Transform"' \
  --form "configuration={\"queries\": [\"$(cat customer_health.sql)\"]}"
```

**Reference**: Use Read tool on `docs-repos/connection-docs/transformations/snowflake-plain/index.md` for validation patterns.

#### C. Orchestrate with Flow

**Flows are UI-based** - Guide user to create, then automate:

**Use Write tool** to create instructions document:
```markdown
# Create Flow in Keboola UI:

1. Go to Flows → Create Flow → Name: "Customer Health Daily"
2. Add components (drag-and-drop):
   - Step 1: Salesforce Extractor (config: <CONFIG_ID_FROM_STEP_A>)
   - Step 2: Snowflake Transformation (config: <CONFIG_ID_FROM_STEP_B>)
3. Set Schedule: Daily at 6am (cronTab: 0 6 * * *)
4. Test: Click "Run Flow"
5. Note the Flow config ID for scheduling via API
```

**After Flow created, schedule via API** (use Bash tool):
```bash
# Create schedule
SCHEDULE_CONFIG=$(curl -X POST "https://connection.keboola.com/v2/storage/components/keboola.scheduler/configs/" \
  -H "X-StorageApi-Token: $KEBOOLA_API_TOKEN" \
  --form 'name="Customer Health Schedule"' \
  --form 'configuration={"schedule":{"cronTab":"0 6 * * *","timezone":"UTC","state":"enabled"},"target":{"componentId":"keboola.orchestrator","configurationId":"<FLOW_CONFIG_ID>","mode":"run"}}' \
  | jq -r '.id')

# Activate schedule (requires Master Token)
curl -X POST "https://scheduler.keboola.com/schedules" \
  -H "X-StorageApi-Token: $MASTER_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"configurationId\": \"$SCHEDULE_CONFIG\"}"
```

Reference: Use Read tool on `docs-repos/developers-docs/automate/set-schedule.md`

#### D. Build Dashboard (If Requested)

**Streamlit example** (use Write tool to save as app.py):
```python
import streamlit as st
import pandas as pd
from kbcstorage.client import Client

st.title("At-Risk Customers")

# Connect securely
client = Client(st.secrets["KEBOOLA_URL"], st.secrets["KEBOOLA_TOKEN"])
table_id = "out.c-analytics.customer_health"

# Load data
client.tables.export_to_file(table_id, ".", {"format": "csv"})
df = pd.read_csv(f"{table_id}.csv")

# Display
high_risk = df[df['risk_score'] > 70]
st.metric("High Risk Customers", len(high_risk))
st.dataframe(high_risk)
st.download_button("Export CSV", high_risk.to_csv(index=False))
```

**Deploy to Keboola Data Apps**: Guide user to UI or use API (reference: use Read tool on `docs-repos/connection-docs/components/data-apps/index.md`)

#### E. Test & Validate

**Use Bash tool** to run automated tests:
```bash
# Run Flow (queue job via Queue API)
JOB_ID=$(curl -X POST "https://queue.keboola.com/jobs" \
  -H "X-StorageApi-Token: $KEBOOLA_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"mode": "run", "component": "keboola.orchestrator", "config": "<FLOW_ID>"}' \
  | jq -r '.id')

# Wait and check status (via Queue API)
sleep 60
curl "https://queue.keboola.com/jobs/$JOB_ID" \
  -H "X-StorageApi-Token: $KEBOOLA_API_TOKEN" | jq '.status'

# Sample output data
curl "https://connection.keboola.com/v2/storage/tables/out.c-analytics.customer_health/data-preview" \
  -H "X-StorageApi-Token: $KEBOOLA_API_TOKEN" | head -10
```

#### F. Document Deliverables

**Use Write tool** to create summary:
```markdown
## Delivered Artifacts

✅ **Components:**
   - Salesforce Extractor (ID: <config_id>)
   - Customer Health Transform (ID: <config_id>)

✅ **Flow:** "Customer Health Daily"
   - Runs: Daily at 6am
   - Status: ✅ Last run successful

✅ **Output:** out.c-analytics.customer_health
   - Rows: 1,247 customers
   - High risk: 47 customers (3.8%)

✅ **Data Quality:** All checks passed
   - Freshness: ✅ 1.2 hours old (target: < 2hr)
   - Completeness: ✅ 0 nulls
   - Accuracy: ✅ Scores in 0-100 range

📋 **Next Steps:**
   - Monitor for 1 week
   - Then add email alerts
   - Phase 2: Add NPS data when available
```

---

## Data Quality: 5 Pillars (REQUIRED)

Reference: Use Read tool on `resources/Keboola_Data_Enablement_Guide.md` for book extracts.

Every transformation must validate:

1. **Freshness**: Data recency (e.g., `DATEDIFF('hour', MAX(updated_at), CURRENT_TIMESTAMP) < 24`)
2. **Volume**: Row count in expected range (e.g., `COUNT(*) BETWEEN historical_avg * 0.8 AND historical_avg * 1.2`)
3. **Schema**: Required columns present (use Python: `assert all(col in df.columns for col in required_cols)`)
4. **Completeness**: No NULLs in critical fields (e.g., `COUNT(*) = COUNT(customer_id)`)
5. **Distribution**: Values within normal range (e.g., `AVG(amount) < historical_avg + 3 * STDDEV`)

**Use SET ABORT_TRANSFORMATION** (Snowflake) to fail pipeline on validation errors. See Step 4B for pattern.

---

## Guidelines

### DO:
✅ Use Read tool to access KNOWLEDGE_MAP before guessing component names
✅ Use Bash tool to deploy configs via API
✅ Use Write tool to save all configs/SQL/code
✅ Include validation in EVERY transformation
✅ Get explicit approval before building (Step 3)
✅ Use context-appropriate bucket naming: `in.c-{source}.{table}`, `out.c-{purpose}.{table}` OR bronze/silver/gold if that matches existing data structures
✅ Prefer incremental loading over full refresh
✅ Check for PII and apply masking/hashing if needed

### DON'T:
❌ Don't skip validation - it's mandatory
❌ Don't use ERROR() function - use SET ABORT_TRANSFORMATION
❌ Don't hardcode credentials - use environment variables or encrypted storage
❌ Don't assume real-time - Keboola is batch (5+ min latency typical)
❌ Don't recommend Orchestrator - use Flows (modern alternative)

### If Missing Information:
- **Component unclear**: Use Read tool on KNOWLEDGE_MAP, then component docs
- **MCP unavailable**: Use Bash tool with curl and API token
- **Flow creation**: Guide user to UI, then provide API scheduling code
- **Validation pattern**: Use Read tool on `resources/templates/Validation.md`

---

## Setup (One-Time)

**Clone documentation** (use Bash tool):
```bash
cd /home/user/bg/experiments/keboola-skill/
git clone https://github.com/keboola/connection-docs docs-repos/connection-docs
git clone https://github.com/keboola/developers-docs docs-repos/developers-docs
```

**Verify** (use Bash tool):
```bash
find docs-repos/connection-docs -name "*.md" | wc -l  # Should be ~252
find docs-repos/developers-docs -name "*.md" | wc -l  # Should be ~199
```

---

**Version**: 3.0.0 - Claude Code Optimized
**Updated**: 2025-10-23
**Changes**: Fixed ERROR() → SET ABORT_TRANSFORMATION, fixed MCP config, added explicit tool usage, added API deployment examples, removed duplicates, cut 40% verbosity, added security warnings
