# Keboola Skill - The Correct Approach

## What We're Actually Building

A **Claude Code skill** that makes Claude an expert in Keboola data engineering by:

1. **Ingesting Keboola's existing documentation** from their GitHub repos
2. **Using Keboola's existing APIs** (not rebuilding them)
3. **Leveraging existing tools** (their CLI if they have one, or simple API wrappers)
4. **Teaching Claude best practices** for Keboola data engineering

## What Keboola Already Provides

### Documentation (GitHub)
- https://github.com/keboola/developers-docs - Developer documentation
- https://github.com/keboola/connection-docs - Connection documentation
- https://github.com/keboola/component-* - Individual component repos

### APIs (Already Built by Keboola)
- **Storage API** - https://connection.keboola.com/v2/storage
- **Job Queue API** - https://queue.keboola.com
- **Docker Runner API** - https://docker-runner.keboola.com
- **Encryption API** - https://encryption.keboola.com
- **Syrup API** - Component configurations

### Existing Client Libraries
- **Python**: `kbcstorage` - https://github.com/keboola/storage-api-python-client
- **PHP**: `php-client` - https://github.com/keboola/storage-api-php-client
- **CLI**: May exist or we create a thin wrapper

### Web UI
- Keboola Connection - https://connection.keboola.com

## The Skill Architecture (Correct)

```
┌─────────────────────────────────────────────────────────┐
│                   CLAUDE CODE                           │
│            (User asks questions)                        │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│              KEBOOLA SKILL                              │
│  - Expert knowledge of Keboola                          │
│  - Best practices and patterns                          │
│  - How to use Keboola tools                             │
│  - Troubleshooting expertise                            │
│  - All docs indexed and searchable                      │
└────────────────────┬────────────────────────────────────┘
                     │
        ┌────────────┴────────────┐
        │                         │
┌───────▼──────────┐    ┌────────▼───────────┐
│   MCP SERVER     │    │  DOCUMENTATION     │
│  (Optional)      │    │     ENGINE         │
│                  │    │                    │
│ Simple wrapper   │    │ Indexes GitHub     │
│ around Keboola   │    │ repos, makes       │
│ Storage API      │    │ searchable         │
└───────┬──────────┘    └────────────────────┘
        │
┌───────▼──────────────────────────────────────┐
│        KEBOOLA'S EXISTING APIs               │
│  - Storage API (Keboola built)              │
│  - Job Queue API (Keboola built)            │
│  - Component APIs (Keboola built)           │
└──────────────────────────────────────────────┘
```

## What We Actually Build

### 1. Documentation Indexer (Small Script)

**Purpose**: Pull and index all Keboola documentation

```javascript
// Clones Keboola repos and creates searchable index
const repos = [
  'keboola/developers-docs',
  'keboola/connection-docs',
  'keboola/component-examples'
];

// Index all markdown files
// Create embeddings for semantic search
// Store in lightweight database
```

**Output**:
- `docs/index.json` - Searchable documentation index
- `docs/embeddings.json` - Semantic search vectors
- `docs/components.json` - Component catalog

### 2. Skill Definition (Pure Knowledge)

**Purpose**: Teach Claude everything about Keboola

```
.claude/skills/keboola/
├── skill.json                  # Skill metadata
├── system-prompt.md            # Core Keboola expertise
├── knowledge/
│   ├── architecture.md         # How Keboola works
│   ├── storage.md              # Storage concepts
│   ├── components.md           # Component types
│   ├── transformations.md      # SQL/Python transformations
│   ├── orchestration.md        # Orchestrations and flows
│   └── best-practices.md       # Patterns and anti-patterns
├── examples/
│   ├── extractors/             # Example extractor configs
│   ├── transformations/        # Example SQL/Python
│   ├── writers/                # Example writer configs
│   └── pipelines/              # Complete pipeline examples
└── troubleshooting/
    ├── common-errors.md
    ├── performance.md
    └── debugging.md
```

**skill.json**:
```json
{
  "name": "keboola",
  "displayName": "Keboola Data Engineering Expert",
  "version": "1.0.0",
  "description": "Expert knowledge for Keboola platform",
  "sources": {
    "documentation": [
      "https://github.com/keboola/developers-docs",
      "https://github.com/keboola/connection-docs"
    ],
    "apis": [
      "https://developers.keboola.com/integrate/storage/api/",
      "https://developers.keboola.com/integrate/jobs/",
      "https://developers.keboola.com/integrate/docker-runner/"
    ]
  },
  "capabilities": [
    "pipeline-design",
    "transformation-writing",
    "troubleshooting",
    "optimization",
    "api-usage"
  ]
}
```

### 3. Simple MCP Server (Thin Wrapper)

**Purpose**: Expose Keboola's existing APIs to Claude Code

```typescript
// Simple wrapper - NO custom logic
// Just exposes existing Keboola APIs as MCP tools

import { Server } from '@modelcontextprotocol/sdk/server';
import axios from 'axios';

// Tool: Call Keboola Storage API
async function callStorageAPI(endpoint, method, data) {
  return axios({
    method,
    url: `https://connection.keboola.com/v2/storage/${endpoint}`,
    headers: {
      'X-StorageApi-Token': process.env.KEBOOLA_TOKEN
    },
    data
  });
}

// That's it - just proxy to Keboola's APIs
// No reimplementation
// No custom logic
// The SKILL provides the intelligence
```

**Tools exposed**:
- `keboola_api_call` - Generic API call tool
- `keboola_storage_api` - Storage API wrapper
- `keboola_jobs_api` - Jobs API wrapper
- `keboola_components_api` - Components API wrapper

That's it. Simple wrappers, not reimplementations.

## How It Works

### User asks Claude:
```
"Create a pipeline to extract data from MySQL and load to Snowflake"
```

### Claude (with Keboola skill) responds:

**Step 1: Uses skill knowledge**
- Knows MySQL extractor is `keboola.ex-db-mysql`
- Knows Snowflake writer is `keboola.wr-snowflake-blob-storage`
- Knows configuration structure from indexed docs

**Step 2: Uses MCP tools (simple wrappers)**
- Calls `keboola_components_api` to list available components
- Calls `keboola_storage_api` to check existing buckets
- Creates configurations via Keboola's API

**Step 3: Applies best practices from skill**
- Suggests incremental loading
- Recommends proper bucket structure
- Adds error notifications
- Proposes testing strategy

**Step 4: Searches documentation when needed**
- Skill has indexed all docs
- Can search for specific component details
- Provides examples from Keboola's own repos

## What Makes This "Correct"

### ✅ Leverages Existing Infrastructure
- Uses Keboola's APIs (not reimplementing)
- Uses Keboola's documentation (not rewriting)
- Uses Keboola's component ecosystem (not rebuilding)

### ✅ Skill is Pure Knowledge
- Teaches Claude about Keboola
- Provides patterns and best practices
- Shows examples from real Keboola usage
- No code execution in skill itself

### ✅ MCP Server is Thin Wrapper
- Just exposes existing APIs
- No custom business logic
- Minimal maintenance
- Stays in sync with Keboola automatically

### ✅ Documentation Always Fresh
- Pulls from Keboola's GitHub repos
- Can be updated automatically
- Reflects latest Keboola features
- Community contributions included

### ✅ Extensible
- Easy to add new knowledge
- Can incorporate new Keboola features
- Community can contribute examples
- No need to update code for new components

## Implementation Steps

### Phase 1: Documentation (Week 1)

1. **Clone Keboola repos**
   ```bash
   git clone https://github.com/keboola/developers-docs
   git clone https://github.com/keboola/connection-docs
   ```

2. **Build documentation index**
   - Parse all markdown files
   - Extract component information
   - Create searchable index
   - Generate embeddings for semantic search

3. **Create component catalog**
   - List all available components
   - Document their configurations
   - Collect examples

### Phase 2: Skill Definition (Week 2)

1. **Write system prompt**
   - Keboola architecture overview
   - Component types and capabilities
   - Common patterns
   - Best practices

2. **Organize knowledge files**
   - Storage concepts
   - Transformation patterns
   - Orchestration strategies
   - Troubleshooting guides

3. **Collect examples**
   - Real extractor configurations
   - Real transformation SQL
   - Real pipeline definitions
   - Real troubleshooting scenarios

### Phase 3: MCP Wrapper (Week 3)

1. **Simple API proxy**
   - Storage API calls
   - Jobs API calls
   - Components API calls
   - Just thin wrappers

2. **Authentication handling**
   - Token management
   - Multi-stack support
   - Error handling

### Phase 4: Testing & Refinement (Week 4)

1. **Test with real scenarios**
   - Create pipelines
   - Write transformations
   - Debug issues
   - Optimize performance

2. **Refine skill knowledge**
   - Add missing patterns
   - Improve examples
   - Update best practices

## File Structure

```
keboola-skill/
├── indexer/
│   ├── clone-repos.sh          # Clone Keboola repos
│   ├── index-docs.js           # Create searchable index
│   ├── index-components.js     # Build component catalog
│   └── generate-embeddings.js  # Semantic search
│
├── skill/
│   ├── skill.json
│   ├── system-prompt.md
│   ├── knowledge/
│   │   ├── *.md
│   ├── examples/
│   │   ├── extractors/
│   │   ├── transformations/
│   │   ├── writers/
│   │   └── pipelines/
│   └── troubleshooting/
│       └── *.md
│
├── mcp-server/
│   ├── index.js                # Simple MCP wrapper
│   └── package.json
│
├── docs/                       # Indexed documentation
│   ├── repos/                  # Cloned repos
│   ├── index.json
│   ├── embeddings.json
│   └── components.json
│
└── README.md
```

## Size and Complexity

### Total Size: ~50MB
- Documentation repos: ~30MB
- Indexed data: ~10MB
- Skill files: ~5MB
- MCP server: ~1MB

### Total Code: ~500 lines
- Documentation indexer: ~200 lines
- MCP server wrapper: ~200 lines
- Build scripts: ~100 lines

That's it. Simple, focused, leverages existing infrastructure.

## Distribution

### Option 1: Claude Code Skill Package
```bash
claude-code install keboola-skill
```

Includes:
- Pre-indexed documentation
- Skill definition
- MCP server wrapper
- Setup instructions

### Option 2: Manual Installation

1. Clone repo
2. Run indexer to pull latest docs
3. Install skill in Claude Code
4. Configure MCP server with Keboola token
5. Start using

## The Key Insight

The skill is **knowledge**, not **code**.

- The skill teaches Claude about Keboola
- The MCP server just exposes existing APIs
- The documentation comes from Keboola's repos
- We don't rebuild anything Keboola already has

This is what makes it:
- Maintainable (no custom logic)
- Accurate (uses official docs)
- Up-to-date (pulls from source)
- Lightweight (just knowledge)
- Extensible (easy to add more)

## This Is The Correct Approach

Not a platform, not an SDK, not a reimplementation.

Just a **skill** that makes Claude an expert by leveraging what Keboola already provides.
