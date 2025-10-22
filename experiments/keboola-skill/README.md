# Keboola Skill for Claude Code

A skill that makes Claude Code an expert in Keboola data engineering.

## What This Is

A **focused skill** built on Keboola's existing infrastructure:

- **Documentation indexer** - Pulls Keboola docs from GitHub
- **Skill definition** - Pure knowledge (markdown) teaching Claude about Keboola
- **MCP server** - Thin wrapper exposing Keboola's APIs to Claude Code

**Total code: ~400 lines**
**No reimplementation of Keboola's platform**

## Project Structure

```
keboola-skill/
├── indexer/
│   └── index-docs.js           # Pulls and indexes Keboola documentation
├── skill/
│   ├── skill.json              # Skill metadata
│   ├── system-prompt.md        # Core Keboola expertise
│   ├── knowledge/              # Organized knowledge (storage, etc.)
│   └── examples/               # Real configurations and SQL
├── mcp-server/
│   └── index.js                # Simple MCP wrapper (~200 lines)
├── docs/
│   ├── index.json              # Indexed documentation
│   └── sample-index.json       # Sample for offline use
├── package.json
└── README.md
```

## Quick Start

### 1. Install Dependencies

```bash
cd experiments/keboola-skill
npm install
```

### 2. Index Documentation (Optional)

If you have internet access:

```bash
npm run index-docs
```

This pulls Keboola documentation from GitHub. If offline, the sample index will be used.

### 3. Get Keboola API Token

1. Log in to Keboola Connection
2. Go to **Users & Settings** > **API Tokens**
3. Create a new token with appropriate permissions
4. Copy the token

### 4. Configure Environment

```bash
export KEBOOLA_API_TOKEN="your-token-here"
export KEBOOLA_STACK_URL="https://connection.keboola.com"  # or your stack URL
```

### 5. Test MCP Server

```bash
npm run mcp-server
```

Should output:
```
Loaded 4 documentation files
Keboola MCP Server running on stdio
```

Press Ctrl+C to stop.

### 6. Configure Claude Code

Add to your Claude Code MCP configuration:

```json
{
  "mcpServers": {
    "keboola": {
      "command": "node",
      "args": ["/full/path/to/experiments/keboola-skill/mcp-server/index.js"],
      "env": {
        "KEBOOLA_API_TOKEN": "your-token",
        "KEBOOLA_STACK_URL": "https://connection.keboola.com"
      }
    }
  }
}
```

**Important**: Use the full absolute path!

### 7. Restart Claude Code

Restart Claude Code to load the MCP server.

## Using the Skill

Once configured, Claude will automatically have Keboola expertise:

### Example 1: List Buckets

```
You: "List all my Keboola storage buckets"

Claude: [Uses keboola_list_buckets tool]
Here are your storage buckets:
- in.c-main: Main input bucket
- in.c-mysql: MySQL extractor data
- out.c-analytics: Analytics output
...
```

### Example 2: Get Expert Advice

```
You: "What's the best way to set up a MySQL to Snowflake pipeline?"

Claude: [Uses skill knowledge]
I recommend this architecture:

1. MySQL Extractor (keboola.ex-db-mysql)
   - Use incremental loading with updated_at column
   - Configure appropriate primary keys

2. Snowflake Transformation
   - Transform and enrich data
   - Add data quality checks

3. Snowflake Writer (keboola.wr-snowflake-blob-storage)
   - Load to final tables

Here's a sample configuration...
[Provides actual JSON config from examples]
```

### Example 3: Search Documentation

```
You: "How do I configure incremental loading?"

Claude: [Uses keboola_search_docs tool]
Based on Keboola documentation:

Incremental loading allows you to load only new or changed data...
[Provides relevant docs with links]
```

### Example 4: Debug Issues

```
You: "My MySQL extractor is failing with authentication error"

Claude: [Uses skill troubleshooting knowledge]
Let me help you debug this. Common causes:

1. Check if password is properly encrypted (# prefix)
2. Verify user has SELECT permissions
3. Check if SSL is required
4. Test connection details

Let me check your configuration...
[Uses keboola_storage_api to get config]
```

## Available Tools

The MCP server provides:

- `keboola_storage_api` - Call any Storage API endpoint
- `keboola_list_buckets` - List all buckets
- `keboola_list_tables` - List tables in a bucket
- `keboola_get_table` - Get table details
- `keboola_search_docs` - Search indexed documentation

## Skill Knowledge

The skill teaches Claude about:

- Keboola architecture and concepts
- Storage (buckets, tables, workspaces)
- Components (extractors, writers, applications)
- Transformations (SQL, Python, R)
- Orchestrations and scheduling
- Best practices and patterns
- Common troubleshooting scenarios

## Extending the Skill

### Add More Knowledge

Create new files in `skill/knowledge/`:

```bash
echo "# Transformations Guide" > skill/knowledge/transformations.md
echo "# Components Catalog" > skill/knowledge/components.md
```

### Add More Examples

Add configurations in `skill/examples/`:

```bash
# Add a Python transformation example
cat > skill/examples/python-transformation.py << 'EOF'
# Customer segmentation
import pandas as pd

# Read input
customers = pd.read_csv('in/tables/customers.csv')
orders = pd.read_csv('in/tables/orders.csv')

# Calculate metrics
metrics = orders.groupby('customer_id').agg({
    'order_id': 'count',
    'amount': 'sum'
})

# Write output
metrics.to_csv('out/tables/customer_metrics.csv')
EOF
```

### Update Documentation Index

Run regularly to get latest Keboola docs:

```bash
npm run index-docs
```

## Troubleshooting

### MCP Server Not Starting

1. Check `KEBOOLA_API_TOKEN` is set
2. Verify node is installed: `node --version`
3. Check dependencies: `npm install`

### Tools Not Working

1. Verify token is valid
2. Check token permissions in Keboola UI
3. Verify stack URL is correct
4. Test API directly:
   ```bash
   curl -H "X-StorageApi-Token: $KEBOOLA_API_TOKEN" \
     https://connection.keboola.com/v2/storage/buckets
   ```

### Documentation Not Loading

1. Run indexer: `npm run index-docs`
2. Check `docs/index.json` exists
3. Use sample index if offline: `cp docs/sample-index.json docs/index.json`

### Claude Not Using Keboola Knowledge

1. Verify MCP server is configured with absolute path
2. Check MCP server is running: `ps aux | grep mcp-server`
3. Restart Claude Code
4. Check Claude Code logs for MCP connection errors

## Development

### Run Indexer

```bash
npm run index-docs
```

### Test MCP Server

```bash
KEBOOLA_API_TOKEN="test" npm run mcp-server
```

### Add New Tools

Edit `mcp-server/index.js` and add to the tools array:

```javascript
{
  name: 'keboola_my_new_tool',
  description: 'Description of what it does',
  inputSchema: { /* ... */ }
}
```

Then handle the tool in the `CallToolRequestSchema` handler.

## Architecture

```
Claude Code
    ↓
Keboola Skill (knowledge in markdown)
    ↓
MCP Server (thin wrapper)
    ↓
Keboola Storage API (existing)
```

- **Skill** = Pure knowledge, no code
- **MCP Server** = Simple wrapper, no reimplementation
- **Keboola APIs** = Use what Keboola already provides

## Files

- **400 lines of code total**
- **5 MB of skill knowledge**
- **2-10 MB documentation index**

Simple, maintainable, focused.

## What Makes This Correct

✅ Uses Keboola's existing APIs (not reimplemented)
✅ Uses Keboola's documentation (not rewritten)
✅ Skill is pure knowledge (markdown files)
✅ MCP server is thin wrapper (~200 lines)
✅ Stays in sync with Keboola automatically
✅ Minimal code to maintain
✅ Easy to extend and customize

## Resources

- Keboola Documentation: https://developers.keboola.com
- Keboola Connection: https://connection.keboola.com
- Storage API Reference: https://developers.keboola.com/integrate/storage/api/
- Claude Code: https://docs.claude.com/claude-code

## Testing

See [TEST.md](./TEST.md) for comprehensive testing guide.

## License

MIT
