# Testing the Keboola Skill

## Setup Steps

### 1. Install Dependencies

```bash
cd experiments/keboola-skill
npm install
```

### 2. Index Documentation

```bash
npm run index-docs
```

This will:
- Clone Keboola's documentation from GitHub
- Create searchable index in `docs/index.json`
- Extract component information
- Takes ~2-3 minutes

### 3. Set Up Environment

```bash
export KEBOOLA_API_TOKEN="your-keboola-token"
export KEBOOLA_STACK_URL="https://connection.keboola.com"  # or your stack
```

To get a token:
1. Log in to Keboola Connection
2. Go to Users & Settings > API Tokens
3. Create a new token with appropriate permissions

### 4. Test MCP Server Directly

```bash
npm run mcp-server
```

The server should start and show:
```
Loaded X documentation files
Keboola MCP Server running on stdio
```

Test by sending MCP messages via stdin (or use with Claude Code).

### 5. Configure Claude Code

Add to your Claude Code configuration:

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

### 6. Restart Claude Code

Restart Claude Code to load the new MCP server.

## Testing in Claude Code

### Test 1: List Buckets

```
You: "List all my Keboola storage buckets"

Expected: Claude uses keboola_list_buckets tool and shows bucket list
```

### Test 2: Get Table Info

```
You: "Show me details about the table in.c-main.customers"

Expected: Claude uses keboola_get_table tool and displays table info
```

### Test 3: Search Documentation

```
You: "How do I configure incremental loading in Keboola?"

Expected: Claude uses keboola_search_docs to find relevant documentation
```

### Test 4: Expert Knowledge

```
You: "What's the best way to design a MySQL to Snowflake pipeline in Keboola?"

Expected: Claude uses skill knowledge to provide architecture recommendations,
          best practices, and example configurations
```

### Test 5: Configuration Help

```
You: "Create a MySQL extractor configuration for me"

Expected: Claude provides JSON configuration using examples from skill
```

## Manual Testing (Without Claude Code)

### Test Documentation Indexer

```bash
node indexer/index-docs.js
```

Check output:
```bash
cat docs/index.json | jq '.documents | length'
cat docs/index.json | jq '.components | keys'
```

### Test MCP Server Tools

Create a test script `test-mcp.js`:

```javascript
import { Client } from '@modelcontextprotocol/sdk/client/index.js';
import { StdioClientTransport } from '@modelcontextprotocol/sdk/client/stdio.js';

const transport = new StdioClientTransport({
  command: 'node',
  args: ['./mcp-server/index.js'],
  env: {
    KEBOOLA_API_TOKEN: process.env.KEBOOLA_API_TOKEN,
    KEBOOLA_STACK_URL: process.env.KEBOOLA_STACK_URL,
  },
});

const client = new Client({
  name: 'test-client',
  version: '1.0.0',
}, {
  capabilities: {},
});

await client.connect(transport);

// List available tools
const tools = await client.listTools();
console.log('Available tools:', tools.tools.map(t => t.name));

// Call keboola_list_buckets
const result = await client.callTool({
  name: 'keboola_list_buckets',
  arguments: {},
});
console.log('Buckets:', result.content[0].text);

await client.close();
```

Run:
```bash
node test-mcp.js
```

## Validation Checklist

- [ ] npm install completes without errors
- [ ] Documentation indexer runs and creates docs/index.json
- [ ] docs/index.json contains documents array
- [ ] MCP server starts without errors
- [ ] MCP server loads documentation index
- [ ] Claude Code shows keboola in MCP server list
- [ ] keboola_list_buckets tool works
- [ ] keboola_get_table tool works
- [ ] keboola_search_docs tool works
- [ ] Skill knowledge is accessible to Claude
- [ ] Claude provides Keboola-specific advice

## Expected File Sizes

```
docs/index.json: ~2-10 MB (depending on how many docs indexed)
skill/: ~100 KB (markdown files)
mcp-server/index.js: ~10 KB
indexer/index-docs.js: ~5 KB
```

## Troubleshooting

### "Cannot find module @modelcontextprotocol/sdk"

```bash
npm install
```

### "KEBOOLA_API_TOKEN environment variable is required"

Set the environment variable:
```bash
export KEBOOLA_API_TOKEN="your-token"
```

### "Could not load documentation index"

Run the indexer:
```bash
npm run index-docs
```

### "Rate limit exceeded" (GitHub API)

The indexer limits to 50 files per repo to avoid rate limits. This is normal.
For more complete indexing, add a GitHub token:

```javascript
const octokit = new Octokit({
  auth: 'your-github-token'
});
```

### MCP Server not showing in Claude Code

1. Check the path in Claude Code config is absolute
2. Verify node is in your PATH
3. Check MCP server starts without errors manually
4. Restart Claude Code

### Tools not working

1. Verify KEBOOLA_API_TOKEN is valid
2. Check token has necessary permissions
3. Verify KEBOOLA_STACK_URL is correct
4. Test API calls directly with curl

## Success Criteria

The skill is working when:

1. ✅ Documentation is indexed and searchable
2. ✅ MCP server connects to Keboola API successfully
3. ✅ Claude can list buckets, tables, etc.
4. ✅ Claude provides Keboola-specific expertise
5. ✅ Claude references documentation when needed
6. ✅ Claude generates valid Keboola configurations
7. ✅ Claude follows Keboola best practices

## What You Should See

When working correctly, Claude will:

- Know about Keboola concepts (buckets, tables, components)
- Provide accurate SQL transformation examples
- Generate valid component configurations
- Reference official documentation
- Apply best practices (incremental loading, etc.)
- Troubleshoot issues systematically
- Use MCP tools to interact with your Keboola project

## Next Steps

Once basic testing works:

1. Add more knowledge files (transformations, components, etc.)
2. Index more documentation
3. Add more example configurations
4. Create troubleshooting guides
5. Add component-specific knowledge
6. Build out best practices
7. Share with team
