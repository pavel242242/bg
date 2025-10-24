# Keboola Skill for Claude Code

Make Claude Code an expert in Keboola data engineering by leveraging Keboola's existing documentation, APIs, and tools.

## What This Is

A **skill** that teaches Claude about Keboola - not a reimplementation of Keboola's platform.

## Three Simple Components

### 1. Documentation Indexer
- Pulls Keboola's docs from GitHub
- Creates searchable index
- Builds component catalog
- **Size**: ~200 lines of code

### 2. Skill Definition
- Pure knowledge (markdown files)
- Best practices and patterns
- Examples and troubleshooting
- **Size**: ~5MB of markdown

### 3. MCP Server
- Thin wrapper around Keboola's APIs
- No custom business logic
- Just exposes existing functionality
- **Size**: ~200 lines of code

## Why This Approach

### ✅ Leverages Existing Infrastructure
- Uses Keboola's Storage API
- Uses Keboola's Job Queue API
- Uses Keboola's documentation
- Uses Keboola's component ecosystem

### ✅ Minimal Code
- ~400 lines total
- No reimplementation
- Easy to maintain
- Stays in sync with Keboola

### ✅ Pure Knowledge Skill
- Teaches Claude about Keboola
- Provides best practices
- Shows real examples
- Searchable documentation

### ✅ Always Up-to-Date
- Pulls docs from Keboola's GitHub
- Reflects latest features
- Community contributions included
- Can auto-update daily

## How It Works

1. **User asks**: "Create a MySQL to Snowflake pipeline"

2. **Claude (with skill)**:
   - Knows about MySQL extractor and Snowflake writer (from skill knowledge)
   - Can search docs for configuration details (from indexed docs)
   - Calls Keboola API to create configs (via MCP wrapper)
   - Applies best practices (from skill patterns)

3. **Result**: Complete pipeline with proper configuration, following Keboola best practices

## File Structure

```
keboola-skill/
├── indexer/
│   └── index-docs.js           # Pull and index Keboola docs
├── skill/
│   ├── skill.json              # Skill metadata
│   ├── system-prompt.md        # Core expertise
│   ├── knowledge/              # Organized knowledge
│   └── examples/               # Real examples
├── mcp-server/
│   └── index.js                # Simple API wrapper
├── docs/
│   └── index.json              # Indexed documentation
└── README.md
```

## Setup

```bash
# 1. Clone and install
git clone <repo>
cd keboola-skill
npm install

# 2. Index Keboola documentation
node indexer/index-docs.js

# 3. Install skill in Claude Code
cp -r skill ~/.claude/skills/keboola

# 4. Configure MCP server
# Add to Claude Code config:
{
  "mcpServers": {
    "keboola": {
      "command": "node",
      "args": ["./mcp-server/index.js"],
      "env": {
        "KEBOOLA_API_TOKEN": "your-token"
      }
    }
  }
}

# 5. Restart Claude Code
```

## Usage

Once installed, Claude will automatically use Keboola expertise:

```
You: "How do I create an incremental MySQL extractor?"

Claude: [Uses skill knowledge to explain incremental loading,
         searches docs for MySQL extractor details,
         provides example configuration]

You: "Create it for me"

Claude: [Uses MCP tool to call Keboola API,
         creates the configuration,
         confirms success]
```

## What You Get

- **Keboola expertise** - Claude knows Keboola concepts, patterns, best practices
- **Searchable docs** - All Keboola docs indexed and searchable
- **API access** - Call any Keboola API through Claude
- **Real examples** - Actual configurations and transformations
- **Troubleshooting** - Common errors and resolutions

## Maintenance

```bash
# Update documentation (run weekly or daily)
node indexer/index-docs.js

# That's it - no code changes needed
```

## Size

- Documentation: ~30MB (Keboola's docs)
- Index: ~10MB
- Skill: ~5MB
- Code: ~400 lines
- **Total**: ~45MB

## See Also

- [CORRECT_APPROACH.md](./CORRECT_APPROACH.md) - Why this approach works
- [IMPLEMENTATION.md](./IMPLEMENTATION.md) - Detailed implementation guide

## Key Insight

The skill is **knowledge**, not **code**.

We don't rebuild Keboola - we teach Claude how to use what Keboola already provides.
