# How to Use Keboola Skill v4.1 with Claude Code

## Quick Setup (3 Steps)

### 1. Install the Skill

**Option A: Symlink** (Recommended - updates automatically)
```bash
# Create skills directory if it doesn't exist
mkdir -p ~/.claude/skills

# Symlink the skill directory
ln -s /home/user/bg/experiments/keboola-skill ~/.claude/skills/keboola

# Verify
ls -la ~/.claude/skills/
```

**Option B: Copy** (Static - won't auto-update)
```bash
mkdir -p ~/.claude/skills
cp -r /home/user/bg/experiments/keboola-skill ~/.claude/skills/keboola
```

### 2. Verify Skill Installation

Check that Claude Code can see the skill:
```bash
# The SKILL.md file should be at:
cat ~/.claude/skills/keboola/SKILL.md | head -20

# You should see:
# ---
# name: keboola-data-engineering
# description: Expert assistant for Keboola data platform...
# ---
```

### 3. Invoke the Skill

In Claude Code, type:
```
/skill keboola-data-engineering
```

Or just describe your task:
```
"I need to build a pipeline that extracts Salesforce data and creates a revenue dashboard"
```

Claude Code will automatically detect when to use the skill based on keywords: Keboola, data pipeline, extraction, transformation, etc.

---

## Full Setup (Includes Resources)

### Prerequisites

Ensure you have the Keboola documentation cloned:

```bash
cd /home/user/bg/experiments/keboola-skill/

# Clone official docs (if not already done)
git clone https://github.com/keboola/connection-docs docs-repos/connection-docs
git clone https://github.com/keboola/developers-docs docs-repos/developers-docs

# Verify
ls docs-repos/connection-docs/components/extractors/
ls docs-repos/developers-docs/
```

These provide the 85+ extractor docs, 29+ writer docs that the skill references.

---

## Optional: MCP Server Setup (Live API Access)

The skill works WITHOUT MCP (uses docs only), but MCP adds live API access to your Keboola project.

### Install MCP Server

```bash
# Install uvx (if not already installed)
pip install uvx

# Test MCP server installation
uvx keboola_mcp_server --help
```

### Configure Claude Code for MCP

Edit `~/.claude/settings.json`:

```json
{
  "$schema": "https://json.schemastore.org/claude-code-settings.json",
  "mcpServers": {
    "keboola": {
      "command": "uvx",
      "args": ["keboola_mcp_server", "--api-url", "https://connection.keboola.com"],
      "env": {
        "KBC_STORAGE_TOKEN": "your-keboola-api-token",
        "KBC_WORKSPACE_SCHEMA": "your-workspace-schema"
      }
    }
  },
  "hooks": {
    "Stop": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "~/.claude/stop-hook-git-check.sh"
          }
        ]
      }
    ]
  }
}
```

**Get your Keboola API token**:
1. Log into your Keboola project
2. Go to Settings → Tokens
3. Create new token (or use existing)
4. Copy token value

**Find your API URL** (depends on your stack):
- US Virginia AWS: `https://connection.keboola.com`
- US Virginia GCP: `https://connection.us-east4.gcp.keboola.com`
- EU Frankfurt AWS: `https://connection.eu-central-1.keboola.com`
- EU Ireland Azure: `https://connection.north-europe.azure.keboola.com`
- EU Frankfurt GCP: `https://connection.europe-west3.gcp.keboola.com`

### Restart Claude Code

After editing settings.json:
```bash
# Restart Claude Code to load MCP server
# (Close and reopen Claude Code application)
```

---

## Usage Examples

### Example 1: Simple Request

**You say:**
> "I need to extract MySQL sales data and load it into Snowflake"

**Claude Code with skill will:**
1. Ask 5 business questions (decision, metric, frequency, PII, success)
2. Save `project_context.json`
3. Find MySQL extractor in KNOWLEDGE_MAP
4. Read MySQL extractor docs
5. Generate extractor config JSON
6. Deploy via API
7. Create SQL transformation with validation
8. Test in sandbox
9. Show you the pipeline

### Example 2: Complex Request

**You say:**
> "Build a real-time customer churn prediction pipeline using Stripe and Salesforce data"

**Claude Code with skill will:**
1. Ask business questions
2. Use discovery agent to find Stripe + Salesforce extractors
3. Propose CDC architecture with mermaid diagram
4. Get your approval
5. Use SQL generation agent to create ML feature transforms
6. Test in sandbox
7. Validate business impact (simulation)
8. Create rollback plan
9. Deploy with monitoring

### Example 3: Troubleshooting

**You say:**
> "My Keboola pipeline is failing with 'validation failed' error"

**Claude Code with skill will:**
1. Get job ID from you
2. Query Keboola API for error logs
3. Read _validation table
4. Use error recovery workflow to diagnose
5. Spawn troubleshooting agent if complex
6. Provide fix (SQL change or config update)
7. Re-test

---

## What the Skill Does (v4.1 Features)

### 1. Context-Aware Design
- Saves your requirements to `project_context.json`
- Remembers PII needs, frequency, metric throughout workflow
- Reads context in Step 3 to ensure architecture matches Step 1

### 2. TodoWrite Tracking
- Tracks requirements as todos so nothing is forgotten
- Updates todos as workflow progresses
- Shows you clear progress

### 3. Business Impact Validation
- New Step 4.5 before deployment
- Simulates impact (current vs projected)
- Creates rollback plan
- Structured approval: "deploy" / "test" / "revise"

### 4. Sandbox Testing
- Tests SQL on sample data before production
- Creates temporary workspace
- Verifies transformations work
- Cleans up after testing

### 5. Multi-Agent Delegation
- Discovery agent: Finds components in 85+ extractors
- SQL generation agent: Applies DA/DE book concepts
- Troubleshooting agent: Auto-debugs failures

### 6. Error Recovery
- Decision tree for error diagnosis
- Automated fixes for common issues
- Spawns agent for complex problems

### 7. Visual Diagrams
- Generates mermaid diagrams for architecture
- Shows data flow visually

---

## Verification: Is It Working?

### Test 1: Check Skill is Loaded

In Claude Code, type:
```
/skill keboola-data-engineering
```

You should see the skill activate and Claude will follow the v4.1 workflow.

### Test 2: Ask a Keboola Question

Type:
```
"What Keboola extractors are available for CRM systems?"
```

Claude should:
1. Use Read tool on resources/KNOWLEDGE_MAP.md
2. Or spawn Explore agent to search
3. Return list of CRM extractors (Salesforce, HubSpot, etc.)

### Test 3: Check MCP (if configured)

Type:
```
"List my Keboola storage buckets"
```

If MCP is working, Claude will use `mcp__keboola_storage_api(endpoint="/buckets")`.

If MCP is NOT configured, Claude will ask for your Keboola API token to use curl.

---

## File Structure

After setup, your structure should look like:

```
~/.claude/
├── settings.json          # MCP config (optional)
├── skills/
│   └── keboola/           # Symlink or copy
│       ├── SKILL.md       # v4.1 main skill file (923 lines)
│       ├── resources/
│       │   ├── KNOWLEDGE_MAP.md            # 85+ extractors index
│       │   ├── Keboola_Data_Enablement_Guide.md  # 7 DA/DE books
│       │   └── templates/
│       ├── docs-repos/
│       │   ├── connection-docs/            # 252 markdown files
│       │   └── developers-docs/            # 199 markdown files
│       ├── V4.1_DESIGN.md                  # Feature design doc
│       ├── LESSONS_LEARNED.md              # Development journey
│       └── tests/
│           └── v4_pricing_optimization_test.md  # Test evaluation
```

---

## Troubleshooting Setup

### Issue: "Skill not found"

**Solution**:
```bash
# Check symlink exists
ls -la ~/.claude/skills/keboola

# If broken, recreate
rm ~/.claude/skills/keboola
ln -s /home/user/bg/experiments/keboola-skill ~/.claude/skills/keboola
```

### Issue: "Can't find KNOWLEDGE_MAP.md"

**Solution**:
```bash
# Verify resources exist
ls /home/user/bg/experiments/keboola-skill/resources/KNOWLEDGE_MAP.md

# Check from skill's perspective
ls ~/.claude/skills/keboola/resources/KNOWLEDGE_MAP.md
```

### Issue: "Docs not found"

**Solution**:
```bash
# Clone docs
cd /home/user/bg/experiments/keboola-skill/
git clone https://github.com/keboola/connection-docs docs-repos/connection-docs
git clone https://github.com/keboola/developers-docs docs-repos/developers-docs
```

### Issue: "MCP server not starting"

**Solution**:
```bash
# Test MCP manually
uvx keboola_mcp_server --api-url https://connection.keboola.com

# Check your token is valid
curl "https://connection.keboola.com/v2/storage/tokens/verify" \
  -H "X-StorageApi-Token: YOUR_TOKEN"

# Review settings.json syntax
cat ~/.claude/settings.json | jq .
```

---

## What Happens When You Use the Skill

### Step-by-Step Workflow

**Step 1: Understand (5 questions)**
- Claude asks: decision, metric, frequency, PII, success criteria
- Saves to `project_context.json`
- Tracks with TodoWrite

**Step 2: Discover**
- Claude uses Read tool on KNOWLEDGE_MAP.md
- Or spawns Explore agent for complex searches
- Finds relevant Keboola extractors
- Saves `data_inventory.json`

**Step 3: Propose**
- Reads `project_context.json` for requirements
- Generates architecture with PII handling if needed
- Creates mermaid diagram
- Asks for approval before building

**Step 4: Build**
- Generates extractor configs (JSON)
- Deploys via Keboola API (curl)
- Uses SQL generation agent for complex transforms
- Tests SQL in sandbox workspace
- Deploys transformation
- Creates Flow (you do UI, Claude does API scheduling)
- Tests end-to-end

**Step 4.5: Validate (NEW in v4.1)**
- Reads `project_context.json` for original goals
- Runs impact simulation if metric-driven
- Creates rollback plan
- Shows you results
- Asks: "deploy" / "test" / "revise"

**Step 5: Document**
- Creates DELIVERABLES.md with components, metrics, access links
- Shows you what was built
- Includes rollback plan

---

## Advanced: Environment Variables

For security, set Keboola tokens as environment variables:

```bash
# Add to ~/.bashrc or ~/.zshrc
export KEBOOLA_API_TOKEN="your-token"
export KEBOOLA_MASTER_TOKEN="master-token"  # For scheduler access

# Reload
source ~/.bashrc
```

Claude Code will use `$KEBOOLA_API_TOKEN` in curl commands instead of hardcoding.

---

## Quick Reference

| Task | Command |
|------|---------|
| **Invoke skill** | `/skill keboola-data-engineering` |
| **Check skill exists** | `ls ~/.claude/skills/keboola/SKILL.md` |
| **Update skill** | `cd /home/user/bg/experiments/keboola-skill && git pull` (if symlinked) |
| **Test MCP** | `uvx keboola_mcp_server --api-url https://connection.keboola.com` |
| **View skill version** | `cat ~/.claude/skills/keboola/SKILL.md | grep Version` |
| **See available extractors** | `cat ~/.claude/skills/keboola/resources/KNOWLEDGE_MAP.md | grep "→"` |

---

## Need Help?

**Skill Documentation**:
- `SKILL.md` - Main skill file (923 lines)
- `V4.1_DESIGN.md` - Feature design and rationale
- `LESSONS_LEARNED.md` - Development journey and best practices
- `tests/v4_pricing_optimization_test.md` - Example test evaluation

**Keboola Documentation**:
- Official docs: https://help.keboola.com/
- API reference: https://developers.keboola.com/
- Connection docs: `docs-repos/connection-docs/`
- Developer docs: `docs-repos/developers-docs/`

**Ask Claude**:
Just ask! Claude Code with the skill loaded can answer questions about:
- "How do I extract from X system?"
- "What's the best way to handle Y?"
- "Show me validation patterns for Z"

The skill has 85+ extractors, 29+ writers, 7 DA/DE books, and 451+ markdown files of knowledge at its disposal.
