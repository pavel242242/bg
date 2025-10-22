# Quick Setup Guide - Let's Get Your Keboola Skill Running

## Step 1: Get Your Keboola API Token

### Option A: You already have a token
Skip to Step 2 and use your existing token.

### Option B: Create a new token

1. Open Keboola Connection in your browser
2. Log in to your Keboola project
3. Go to **Users & Settings** (top right menu)
4. Click **API Tokens**
5. Click **New Token**
6. Give it a name like "Claude Code Integration"
7. Set permissions:
   - **Read**: Storage (buckets, tables)
   - **Write**: Optional (if you want Claude to create configs)
8. Click **Create Token**
9. **Copy the token** - you won't see it again!

### Required Permissions

Minimum permissions needed:
- ✅ Storage: Read buckets
- ✅ Storage: Read tables
- ✅ Jobs: Read (to check job status)

Optional (for full functionality):
- Components: Read/Write (to manage configurations)
- Jobs: Write (to run jobs)

## Step 2: Configure Environment Variables

We need to set two environment variables:

```bash
export KEBOOLA_API_TOKEN="your-token-here"
export KEBOOLA_STACK_URL="https://connection.keboola.com"
```

**Finding your stack URL:**
- US Stack: `https://connection.keboola.com`
- EU Stack: `https://connection.eu-central-1.keboola.com`
- Azure Stack: `https://connection.north-europe.azure.keboola.com`
- Your custom stack URL

**Tip:** Check your Keboola login URL to confirm your stack.

## Step 3: Test the Connection

Let's verify your token works:

```bash
cd /home/user/bg/experiments/keboola-skill

# Set your token (replace with your actual token)
export KEBOOLA_API_TOKEN="your-actual-token-here"
export KEBOOLA_STACK_URL="https://connection.keboola.com"

# Test with curl
curl -H "X-StorageApi-Token: $KEBOOLA_API_TOKEN" \
  ${KEBOOLA_STACK_URL}/v2/storage/buckets
```

**Expected result:**
- JSON array of your buckets
- Status 200 OK

**If it fails:**
- Check token is correct (no extra spaces)
- Verify stack URL
- Check token hasn't expired
- Verify permissions in Keboola UI

## Step 4: Test MCP Server Locally

```bash
cd /home/user/bg/experiments/keboola-skill

# Start the MCP server
npm run mcp-server
```

**Expected output:**
```
Loaded 2 documentation files
Keboola MCP Server running on stdio
```

**What this means:**
- ✅ MCP server is working
- ✅ Documentation index loaded
- ✅ Ready to connect to Claude Code

Press Ctrl+C to stop.

## Step 5: Configure Claude Code

Now we need to tell Claude Code about the MCP server.

### Find Claude Code Config Location

**macOS:**
```bash
~/.config/claude-code/config.json
```

**Linux:**
```bash
~/.config/claude-code/config.json
```

**Windows:**
```
%APPDATA%\claude-code\config.json
```

### Add MCP Server Configuration

Open the config file and add:

```json
{
  "mcpServers": {
    "keboola": {
      "command": "node",
      "args": ["/home/user/bg/experiments/keboola-skill/mcp-server/index.js"],
      "env": {
        "KEBOOLA_API_TOKEN": "your-actual-token-here",
        "KEBOOLA_STACK_URL": "https://connection.keboola.com"
      }
    }
  }
}
```

**Important:**
- Use **absolute path** to index.js
- Replace `your-actual-token-here` with your real token
- Update stack URL if not using US stack

**If you already have other MCP servers:**
Just add the `keboola` entry to your existing `mcpServers` object:

```json
{
  "mcpServers": {
    "existing-server": { ... },
    "keboola": {
      "command": "node",
      "args": ["/home/user/bg/experiments/keboola-skill/mcp-server/index.js"],
      "env": {
        "KEBOOLA_API_TOKEN": "your-token",
        "KEBOOLA_STACK_URL": "https://connection.keboola.com"
      }
    }
  }
}
```

## Step 6: Restart Claude Code

1. Close Claude Code completely
2. Reopen Claude Code
3. Check that Keboola MCP server is connected

**How to verify:**
- Look for MCP server indicators in Claude Code UI
- Check status bar or settings for connected servers

## Step 7: Test with Claude

Try these queries in Claude Code:

### Test 1: List Buckets
```
List all my Keboola storage buckets
```

**Expected:**
Claude uses `keboola_list_buckets` tool and shows your buckets.

### Test 2: Expert Advice
```
What's the best way to set up incremental loading in Keboola?
```

**Expected:**
Claude provides detailed answer using skill knowledge.

### Test 3: Get Table Info
```
Show me details about the table in.c-main.customers
```
(Replace with an actual table ID from your project)

**Expected:**
Claude uses `keboola_get_table` tool and shows table details.

### Test 4: Search Documentation
```
How do I configure a MySQL extractor?
```

**Expected:**
Claude uses `keboola_search_docs` and provides documentation.

### Test 5: Create Configuration
```
Help me create a MySQL to Snowflake pipeline
```

**Expected:**
Claude uses skill knowledge to:
- Ask clarifying questions
- Suggest architecture
- Provide example configurations
- Explain best practices

## Troubleshooting

### "MCP server not connecting"

1. Check config file path is correct
2. Verify absolute path to index.js
3. Check token is set in env
4. Look at Claude Code logs for errors

### "Token authentication failed"

1. Verify token in Keboola UI (Users & Settings → API Tokens)
2. Check token hasn't expired
3. Verify token has correct permissions
4. Try regenerating token

### "Cannot find module"

```bash
cd /home/user/bg/experiments/keboola-skill
npm install
```

### "Documentation not loaded"

```bash
cd /home/user/bg/experiments/keboola-skill
npm run index-docs
```

Or use the sample docs:
```bash
cp docs/sample-index.json docs/index.json
```

### "Tools not showing up"

1. Restart Claude Code completely
2. Check MCP server config syntax (valid JSON)
3. Verify node is in PATH: `which node`
4. Test MCP server manually first

## Security Best Practices

### 1. Token Storage
- ❌ Don't commit tokens to git
- ❌ Don't share tokens publicly
- ✅ Use environment variables
- ✅ Store in secure config files only

### 2. Token Permissions
- Use minimum required permissions
- Create separate tokens for different purposes
- Rotate tokens regularly
- Revoke unused tokens

### 3. Project Access
- Use read-only tokens when possible
- Don't use production tokens for testing
- Consider separate dev/prod projects

## What You Can Do Now

Once set up, Claude becomes a Keboola expert who can:

### Data Engineering
- Design data pipelines
- Write SQL transformations
- Configure extractors and writers
- Set up orchestrations
- Optimize performance

### Configuration
- Generate component configs
- Validate configurations
- Explain config options
- Suggest improvements

### Troubleshooting
- Debug failed jobs
- Analyze error messages
- Check data quality
- Optimize slow pipelines

### Best Practices
- Recommend incremental loading
- Suggest proper table design
- Implement error handling
- Add monitoring and alerts

### Learning
- Explain Keboola concepts
- Provide examples
- Reference documentation
- Answer technical questions

## Next Steps

1. ✅ Set up token (Step 1-2)
2. ✅ Test connection (Step 3-4)
3. ✅ Configure Claude Code (Step 5)
4. ✅ Restart and test (Step 6-7)
5. 🚀 Start using Claude as your Keboola expert!

## Support

If you run into issues:

1. Check TEST.md for detailed troubleshooting
2. Review logs in Claude Code
3. Test MCP server manually
4. Verify token and permissions
5. Check documentation is indexed

## Success Checklist

- [ ] Keboola token obtained
- [ ] Token permissions verified
- [ ] Environment variables set
- [ ] Connection tested with curl
- [ ] MCP server starts locally
- [ ] Claude Code config updated
- [ ] Claude Code restarted
- [ ] Can list buckets through Claude
- [ ] Can search documentation
- [ ] Claude provides expert advice

Once all checked, you're ready to go! 🎉
