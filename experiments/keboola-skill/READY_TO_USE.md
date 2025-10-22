# Your Keboola Skill is Ready! 🚀

## ✅ Configuration Complete

Your MCP server is tested and working with your Azure North Europe stack!

**Token:** 532-8013729-1UP98d2dn4koIkSF0HD2gR9PHGWj3QjO7pMlAuiC
**Stack:** https://connection.north-europe.azure.keboola.com

## Quick Setup (2 minutes)

### Step 1: Add to Claude Code Configuration

Your Claude Code configuration file is located at:
- **macOS/Linux:** `~/.config/claude-code/config.json`
- **Windows:** `%APPDATA%\claude-code\config.json`

**Open that file and add this:**

```json
{
  "mcpServers": {
    "keboola": {
      "command": "node",
      "args": ["/home/user/bg/experiments/keboola-skill/mcp-server/index.js"],
      "env": {
        "KEBOOLA_API_TOKEN": "532-8013729-1UP98d2dn4koIkSF0HD2gR9PHGWj3QjO7pMlAuiC",
        "KEBOOLA_STACK_URL": "https://connection.north-europe.azure.keboola.com"
      }
    }
  }
}
```

**If you already have other MCP servers**, just add the `keboola` section:

```json
{
  "mcpServers": {
    "existing-server": { ... },
    "keboola": {
      "command": "node",
      "args": ["/home/user/bg/experiments/keboola-skill/mcp-server/index.js"],
      "env": {
        "KEBOOLA_API_TOKEN": "532-8013729-1UP98d2dn4koIkSF0HD2gR9PHGWj3QjO7pMlAuiC",
        "KEBOOLA_STACK_URL": "https://connection.north-europe.azure.keboola.com"
      }
    }
  }
}
```

### Step 2: Restart Claude Code

Close and reopen Claude Code completely.

### Step 3: Test It!

Try these queries in Claude Code:

#### Test 1: List Your Buckets
```
List all my Keboola storage buckets
```

#### Test 2: Expert Advice
```
What's the best way to set up incremental loading in Keboola?
```

#### Test 3: Create a Pipeline
```
Help me design a MySQL to Snowflake data pipeline in Keboola
```

#### Test 4: Search Documentation
```
How do I configure a transformation in Keboola?
```

## What Claude Can Do Now

With the Keboola skill, Claude becomes your expert who can:

### 🔧 Configuration & Setup
- Design data pipeline architectures
- Generate component configurations (extractors, writers, transformations)
- Explain configuration options
- Validate and improve configs

### 📊 Data Engineering
- Write SQL transformations
- Create Python transformations
- Design incremental loading strategies
- Optimize pipeline performance

### 🔍 Operations
- List your buckets and tables
- Get table details and metadata
- Search Keboola documentation
- Run components (if token has write permissions)

### 🐛 Troubleshooting
- Debug failed jobs
- Analyze error messages
- Suggest fixes
- Optimize slow pipelines

### 📚 Knowledge
- Explain Keboola concepts
- Provide best practices
- Reference official documentation
- Show real examples

## Available MCP Tools

Claude has access to these tools:

1. **keboola_storage_api** - Call any Keboola Storage API endpoint
2. **keboola_list_buckets** - List all your storage buckets
3. **keboola_list_tables** - List tables in a bucket
4. **keboola_get_table** - Get detailed table information
5. **keboola_search_docs** - Search Keboola documentation

## Example Conversations

### Example 1: Pipeline Design
```
You: I need to extract data from MySQL and load it to Snowflake daily

Claude: I'll help you design a robust pipeline for MySQL to Snowflake.
Here's the recommended architecture:

1. MySQL Extractor (keboola.ex-db-mysql)
   - Configure incremental loading using updated_at timestamp
   - Set up appropriate primary keys
   - Schedule for daily execution

2. Transformation (optional)
   - Clean and validate data
   - Enrich with business logic
   - Add data quality checks

3. Snowflake Writer (keboola.wr-snowflake-blob-storage)
   - Configure table mappings
   - Set up upsert logic if needed

Let me show you the exact configurations...
[Claude provides complete JSON configs]
```

### Example 2: Troubleshooting
```
You: My MySQL extractor job failed with error X

Claude: Let me help you debug this. Let me check your configuration...
[Uses keboola_storage_api to get component config]

I see the issue. The error suggests...
[Analyzes and provides solution]

Here's how to fix it:
1. Update the configuration...
2. Test with a smaller dataset...
3. Monitor the next run...
```

### Example 3: Learning
```
You: Explain how Keboola storage works

Claude: Keboola Storage is organized in a hierarchy:

**Buckets** - Logical containers for tables
- in.c-* for input data
- out.c-* for output data
- sys.c-* for system data

**Tables** - CSV-based storage with metadata
- Support primary keys
- Track row counts and size
- Version controlled with snapshots

**Workspaces** - Temporary databases for transformations
[Continues with detailed explanation and examples]
```

## Troubleshooting

### MCP Server Not Showing Up

1. Check the config file path is correct
2. Verify the absolute path to index.js
3. Restart Claude Code completely
4. Check Claude Code logs

### Token Issues

If you get authentication errors:
1. Verify token in Keboola UI (Users & Settings → API Tokens)
2. Check token hasn't expired
3. Verify token has Storage: Read permissions
4. Try regenerating the token

### Tools Not Working

1. Check token permissions in Keboola
2. Verify stack URL is correct
3. Test MCP server manually:
   ```bash
   cd /home/user/bg/experiments/keboola-skill
   export KEBOOLA_API_TOKEN="532-8013729-1UP98d2dn4koIkSF0HD2gR9PHGWj3QjO7pMlAuiC"
   export KEBOOLA_STACK_URL="https://connection.north-europe.azure.keboola.com"
   npm run mcp-server
   ```

## Security Notes

⚠️ **Important:**
- Keep your token secure
- Don't commit it to git (already in .gitignore)
- Don't share it publicly
- Rotate it regularly
- Use minimum required permissions

## Next Steps

1. ✅ Configuration file updated
2. ✅ Claude Code restarted
3. ✅ Test with simple query
4. 🚀 Start building pipelines!

## Support

If you need help:
- Check TEST.md for detailed testing
- Review SETUP_GUIDE.md for more info
- Check Claude Code documentation
- Verify token permissions in Keboola UI

---

**Your Keboola skill is ready to use!** Just add the config to Claude Code, restart, and start asking questions! 🎉
