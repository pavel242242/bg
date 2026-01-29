# n8n-skills Repository Learnings

**Source:** https://github.com/czlonkowski/n8n-skills
**Author:** Romuald Czlonkowski (aiadvisors.pl)
**Purpose:** Claude Code skills for building production-ready n8n workflows

---

## Overview

A collection of **7 complementary Claude Code skills** that teach AI assistants how to build n8n workflows programmatically using the n8n-mcp MCP server.

### Key Statistics
- **525+ n8n nodes** supported
- **2,653+ workflow templates** referenced
- **10 production-tested Code patterns**
- **38,094 CODE node instances** analyzed across 15,202 workflows

---

## The 7 Skills

### 1. n8n Expression Syntax
Teaches correct `{{ }}` expression patterns for dynamic content.

**Core Rules:**
- All dynamic content requires double curly braces: `{{expression}}`
- Current node data: `{{$json.fieldName}}`
- Other nodes: `{{$node["Node Name"].json.fieldName}}`
- **Critical:** Webhook data is under `.body`: `{{$json.body.name}}` NOT `{{$json.name}}`

**Key Variables:**
- `$json` - Current node's output
- `$node["name"]` - Reference previous nodes (case-sensitive!)
- `$now` - Current timestamp
- `$env` - Environment variables

**Where NOT to use expressions:**
- Code nodes (use direct JavaScript: `$json.field`)
- Webhook paths (static only)
- Credential fields

### 2. n8n MCP Tools Expert (Highest Priority)
Guides proper use of n8n-mcp tools for workflow management.

**Critical NodeType Format Distinction:**
- **Search/Validate tools:** `nodes-base.slack`, `nodes-base.httpRequest`
- **Workflow tools:** `n8n-nodes-base.slack`, `@n8n/n8n-nodes-langchain.agent`

**Most-Used Tools:**
| Tool | Purpose | Success Rate |
|------|---------|--------------|
| `n8n_update_partial_workflow` | Edit workflows | 99.0% |
| `search_nodes` | Find nodes | <20ms |
| `get_node` | Get node details | <10ms |
| `validate_node` | Check configuration | <100ms |
| `validate_workflow` | Check entire workflow | 100-500ms |

**Detail Levels for `get_node`:**
- `minimal` (~200 tokens) - Basic metadata
- `standard` (~1-2K tokens) - **Recommended**, covers 95% of needs
- `full` (~3-8K tokens) - Complete schema, use sparingly

**Smart Parameters:**
- IF nodes: `branch: "true"` or `branch: "false"`
- Switch nodes: `case: 0`, `case: 1`, etc.

**Auto-Sanitization:**
- Binary operators (equals, contains): `singleValue` removed automatically
- Unary operators (isEmpty, true, false): `singleValue: true` added automatically

### 3. n8n Workflow Patterns
Five foundational architectural patterns:

1. **Webhook Processing** - Receive HTTP requests → Process → Output
2. **HTTP API Integration** - Fetch from REST APIs, transform, utilize
3. **Database Operations** - Read/write/sync database data
4. **AI Agent Workflow** - AI systems with tools and memory
5. **Scheduled Tasks** - Recurring automation on intervals

**Data Flow Models:**
- Linear (sequential path)
- Branching (conditional routing)
- Parallel (simultaneous operations)
- Looping (batch iterations)
- Error handling (separate error paths)

**Usage Statistics:**
- Webhooks: 35% of triggers
- Scheduled tasks: 28%
- Simple workflows (3-5 nodes): 42%

### 4. n8n Validation Expert
Error interpretation and fix strategies.

**Severity Tiers:**
- **Errors** - Block execution, must fix
- **Warnings** - Permit activation, potential issues
- **Suggestions** - Optional improvements

**Validation Profiles:**
- `minimal` - Fastest, during editing
- `runtime` - **Recommended**, balanced
- `ai-friendly` - Reduced false positives
- `strict` - Maximum rigor for production

**Validation Loop Pattern:**
Configure → Validate → Review Errors → Fix → Revalidate
(~23 seconds analyzing, ~58 seconds fixing per cycle)

**Common Error Types:**
- `missing_required` - Absent mandatory fields
- `invalid_value` - Configuration doesn't match allowed options
- `type_mismatch` - Wrong data types
- `invalid_expression` - Syntax issues
- `invalid_reference` - Non-existent node references

### 5. n8n Node Configuration
Operation-aware guidance with property dependency rules.

**Key Principle:** Not all fields are always required - it depends on operation!

**Configuration Workflow:**
1. Identify node type and operation
2. Use `get_node` with standard detail
3. Configure required fields
4. Validate configuration
5. Use `search_properties` mode if unclear
6. Add optional fields progressively
7. Validate again before deployment

**AI Connection Types (8 types for AI Agent workflows):**
1. Language models
2. Tools
3. Memory systems
4. Output parsers
5. Embeddings
6. Vector stores
7. Documents
8. Text splitters

### 6. n8n Code JavaScript
Data access patterns and return formats.

**Critical Return Format:**
```javascript
// ALWAYS return array of objects with json property
return [{json: {field: value}}];

// Multiple items
return items.map(item => ({json: item.json}));

// Empty result
return [];
```

**Data Access Methods:**
| Method | Purpose | Mode |
|--------|---------|------|
| `$input.all()` | All items (batch) | Run Once for All |
| `$input.first()` | Single item/API response | Run Once for All |
| `$input.item` | Current item | Run Once for Each |
| `$json` | Current field | Run Once for Each |
| `$node['name']` | Reference other nodes | Both |

**Top 5 Error Patterns (62%+ of failures):**
1. Empty Code (23%) - Always include logic
2. Missing Return (15%) - Must return array
3. Expression Syntax Confusion (8%) - Use backticks, not `{{}}`
4. Unmatched Brackets (6%) - Check quote/bracket balance
5. Incorrect Wrapper (5%) - Every item needs `{json: {...}}`

**Execution Modes:**
- **"Run Once for All Items"** - 78% of successful workflows, better performance
- **"Run Once for Each Item"** - 22%, slower for large datasets

### 7. n8n Code Python
Python-specific patterns with critical limitations.

**Critical Limitation:** **No external libraries** - Cannot import requests, pandas, numpy!

**Available Standard Libraries:**
- json, datetime, re, base64
- hashlib, urllib.parse
- math, random, statistics

**Return Format:**
```python
# Always return list of dicts with "json" key
return [{"json": {"field": "value"}}]
```

**Best Practices:**
- Use `.get()` for safe dictionary access
- Handle None explicitly: `value = item.get("field") or "default"`
- List comprehensions for filtering
- Webhook data is under `["body"]`: `_json["body"]["name"]`

**Recommendation:** Use JavaScript for 95% of use cases

---

## MCP Server Configuration

```json
{
  "mcpServers": {
    "n8n-mcp": {
      "command": "npx",
      "args": ["n8n-mcp"],
      "env": {
        "MCP_MODE": "stdio",
        "LOG_LEVEL": "error",
        "DISABLE_CONSOLE_OUTPUT": "true",
        "N8N_API_URL": "https://your-n8n-instance.com",
        "N8N_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

**Offline Tools (no API required):**
- search_nodes, get_node
- validate_node, validate_workflow
- search_templates, get_template
- tools_documentation, ai_agents_guide

**API-Dependent Tools:**
- Workflow creation/management
- Template deployment
- Execution testing

---

## AI Agent Workflow Architecture

**Core Pattern:** Trigger → AI Agent (Model + Tools + Memory) → Output

**Components:**
- **Language Models:** OpenAI, Anthropic, Google, Ollama
- **Tools:** Any n8n node can become a tool via `ai_tool` port
- **Memory:** Buffer (all), Window Buffer (last N - recommended), Summary (condensed)

**Security Guidelines:**
- Create read-only database users for AI tool access
- Validate all inputs
- Implement rate limiting
- Monitor suspicious patterns

---

## Common Mistakes Quick Reference

| Mistake | Solution |
|---------|----------|
| `$json.field` outside expression | `{{$json.field}}` |
| `{{$node.HTTP Request}}` | `{{$node["HTTP Request"]}}` |
| Webhook: `{{$json.name}}` | `{{$json.body.name}}` |
| Code node: `{{$json.field}}` | `$json.field` (no braces) |
| Missing `.json` in node ref | `{{$node["name"].json}}` |
| Wrong nodeType prefix | Search tools: `nodes-base.*`, Workflow tools: `n8n-nodes-base.*` |
| Overusing `detail: "full"` | Use `detail: "standard"` (95% coverage) |

---

## Development Best Practices

1. **Iterative Building** - Workflows built incrementally (~56 seconds between edits)
2. **Validate After Changes** - Every significant change should be validated
3. **Use Smart Parameters** - Semantic names over index calculations
4. **Include Intent** - Always specify intent for better AI responses
5. **Search → Get → Validate** - Standard discovery pattern
6. **Runtime Profile** - Default validation choice

---

## Repository Structure

```
n8n-skills/
├── .claude-plugin/          # Plugin configuration
├── dist/                    # Distribution builds
├── docs/
│   ├── CODE_NODE_BEST_PRACTICES.md
│   ├── DEVELOPMENT.md
│   ├── INSTALLATION.md
│   ├── MCP_TESTING_LOG.md
│   └── USAGE.md
├── evaluations/             # Test scenarios
├── skills/
│   ├── n8n-code-javascript/
│   ├── n8n-code-python/
│   ├── n8n-expression-syntax/
│   ├── n8n-mcp-tools-expert/
│   ├── n8n-node-configuration/
│   ├── n8n-validation-expert/
│   └── n8n-workflow-patterns/
├── .mcp.json.example
├── CLAUDE.md
├── README.md
└── build.sh
```

---

## Attribution

Created by **Romuald Czlonkowski** - www.aiadvisors.pl/en

All commits and PRs using this knowledge should credit the original author.
