# Keboola Integration - Comprehensive Architecture

## Vision: Multi-Layer Integration Platform

Instead of choosing between MCP, API, or CLI - we build all of them as **layers of a unified system**.

```
┌─────────────────────────────────────────────────────────────┐
│                     CLAUDE CODE                             │
│                   (User Interface)                          │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                  MCP SERVER LAYER                           │
│  - Exposes tools, resources, prompts to Claude              │
│  - Real-time streaming capabilities                         │
│  - Interactive workflows                                    │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                    CLI LAYER                                │
│  - Standalone CLI tool (keboola-cli)                        │
│  - Used by MCP server OR directly by users                  │
│  - Interactive mode, batch mode, daemon mode                │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                API CLIENT LIBRARY                           │
│  - Robust TypeScript/JavaScript client                     │
│  - All Keboola APIs: Storage, Jobs, Components, etc.       │
│  - Retry logic, caching, rate limiting                      │
│  - Type-safe with full TypeScript definitions              │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│              DOCUMENTATION ENGINE                           │
│  - Indexes all Keboola docs from GitHub                    │
│  - Full-text search                                         │
│  - Semantic search with embeddings                          │
│  - Component catalog                                        │
│  - Real-time updates                                        │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│              INTELLIGENCE LAYER                             │
│  - Workflow templates                                       │
│  - Best practices database                                  │
│  - Error resolution knowledge                               │
│  - Performance optimization rules                           │
│  - Code generation templates                                │
└─────────────────────────────────────────────────────────────┘
```

## Why This Architecture?

### 1. Multiple Use Cases Supported

**Standalone CLI User:**
```bash
keboola storage list-buckets
keboola jobs run keboola.ex-db-mysql my-config
keboola transform create --sql "SELECT * FROM ..." --output table
```

**Developer Using Library:**
```typescript
import { KeboolaClient } from '@keboola/claude-sdk';
const client = new KeboolaClient({ token, stack });
const buckets = await client.storage.listBuckets();
```

**Claude Code User:**
```
User: "Show me all my Keboola buckets"
Claude: [Uses keboola_list_buckets MCP tool]

User: "Create a pipeline from MySQL to Snowflake"
Claude: [Uses multiple tools + templates to create config]

User: "Why is my job failing?"
Claude: [Analyzes logs, searches docs, suggests fixes]
```

### 2. Reusability & Testing

- CLI can be tested independently
- API client has unit tests
- MCP server integration tests
- Everything is modular and composable

### 3. Documentation Always Available

- All Keboola docs indexed and searchable
- Component schemas embedded
- Examples from all GitHub repos
- Real-time sync from upstream

### 4. Intelligence Built-In

- Not just API calls - actual expertise
- Pattern recognition for common tasks
- Automatic optimization suggestions
- Context-aware recommendations

## Component Breakdown

### 1. API Client Library (`@keboola/client`)

Full-featured API client for all Keboola APIs:

```typescript
// Storage API
client.storage.buckets.list()
client.storage.buckets.get(id)
client.storage.tables.list(bucketId)
client.storage.tables.get(tableId)
client.storage.tables.export(tableId, options)
client.storage.tables.import(tableId, data)
client.storage.workspaces.create(options)

// Jobs API
client.jobs.list(filters)
client.jobs.get(jobId)
client.jobs.create(componentId, configId)
client.jobs.cancel(jobId)
client.jobs.stream(jobId) // Stream logs in real-time

// Components API
client.components.list()
client.components.get(componentId)
client.components.configurations.list(componentId)
client.components.configurations.get(componentId, configId)
client.components.configurations.create(componentId, config)
client.components.configurations.update(componentId, configId, config)
client.components.configurations.delete(componentId, configId)

// Orchestrations API
client.orchestrations.list()
client.orchestrations.get(orchestrationId)
client.orchestrations.run(orchestrationId)
client.orchestrations.tasks.list(orchestrationId)

// Metadata API
client.metadata.search(query)
client.metadata.get(objectId)
client.metadata.set(objectId, metadata)
client.metadata.lineage(tableId)

// Admin API (for project management)
client.admin.projects.list()
client.admin.projects.get(projectId)
client.admin.users.list(projectId)
client.admin.features.list(projectId)

// Events API
client.events.list(filters)
client.events.stream() // Real-time event stream

// Queues API
client.queues.list()
client.queues.get(queueId)
client.queues.jobs.list(queueId)
```

**Features:**
- Automatic retry with exponential backoff
- Request/response caching
- Rate limiting
- Pagination helpers
- Type-safe with full TypeScript definitions
- Streaming support for large datasets
- WebSocket support for real-time updates
- Multi-stack support (US, EU, etc.)
- Token management and refresh

### 2. CLI Tool (`keboola-cli`)

Powerful CLI that works standalone or as library:

```bash
# Storage operations
keboola storage buckets list
keboola storage buckets get in.c-main
keboola storage tables list in.c-main
keboola storage tables export in.c-main.customers --format csv --output customers.csv
keboola storage tables import in.c-main.customers --file data.csv --incremental

# Job operations
keboola jobs list --limit 10
keboola jobs get 12345
keboola jobs run keboola.ex-db-mysql my-config --wait
keboola jobs logs 12345 --follow  # Stream logs in real-time
keboola jobs cancel 12345

# Component operations
keboola components list --filter extractor
keboola components get keboola.ex-db-mysql
keboola config list keboola.ex-db-mysql
keboola config get keboola.ex-db-mysql my-config
keboola config create keboola.ex-db-mysql --from-file config.json
keboola config run keboola.ex-db-mysql my-config --async

# Transformation operations
keboola transform create --name "Customer Analysis" --sql-file transform.sql
keboola transform run my-transformation --watch
keboola transform validate transformation.sql

# Orchestration operations
keboola orchestration list
keboola orchestration run my-flow --wait
keboola orchestration status flow-run-12345

# Metadata operations
keboola metadata search --tag "customer"
keboola metadata get in.c-main.customers
keboola metadata set in.c-main.customers --key "owner" --value "data-team"
keboola lineage show in.c-main.customers --depth 3

# Project operations
keboola project info
keboola project users list
keboola project features list

# Development helpers
keboola dev workspace create --type snowflake
keboola dev workspace load in.c-main.customers
keboola dev workspace query "SELECT * FROM customers LIMIT 10"
keboola dev workspace destroy

# Interactive mode
keboola interactive  # Start REPL-like interface

# Daemon mode (for MCP server)
keboola daemon --port 8080  # HTTP API for MCP server

# Configuration
keboola auth login  # Interactive login
keboola auth status
keboola config set default-project 12345
keboola config set default-stack us
```

**Features:**
- Beautiful formatted output (tables, JSON, YAML)
- Progress bars for long operations
- Interactive prompts for missing params
- Shell completion (bash, zsh, fish)
- Config file support (~/.keboola/config)
- Multiple output formats
- Verbose/debug modes
- Can run as HTTP server for MCP

### 3. Documentation Engine

Comprehensive documentation indexer and search:

```typescript
// Index all documentation sources
const docEngine = new DocumentationEngine({
  sources: [
    'https://github.com/keboola/developers-docs',
    'https://github.com/keboola/connection-docs',
    'https://github.com/keboola/component-examples',
    // All component repos
  ],
  embeddings: true, // Enable semantic search
  updateInterval: '1h', // Keep docs fresh
});

// Search capabilities
docEngine.search('how to create incremental load')
docEngine.findComponent('mysql extractor')
docEngine.getSchema('keboola.ex-db-mysql')
docEngine.findExample('snowflake transformation')
docEngine.semanticSearch('optimize pipeline performance')

// Component catalog
docEngine.components.list()
docEngine.components.get('keboola.ex-db-mysql')
docEngine.components.schema('keboola.ex-db-mysql')
docEngine.components.examples('keboola.ex-db-mysql')
```

**Indexed Content:**
- All markdown docs from GitHub repos
- Component schemas and specifications
- Code examples
- Best practices
- Troubleshooting guides
- API references
- Release notes

**Search Features:**
- Full-text search
- Semantic search with embeddings
- Component-specific search
- Tag-based filtering
- Relevance ranking
- Related content suggestions

### 4. MCP Server

Exposes everything to Claude Code:

**Tools (60+ tools organized by category):**

```typescript
// Storage Tools (15+)
keboola_storage_list_buckets
keboola_storage_get_bucket
keboola_storage_list_tables
keboola_storage_get_table
keboola_storage_export_table
keboola_storage_import_table
keboola_storage_create_table
keboola_storage_delete_table
keboola_storage_query_table
keboola_storage_table_snapshot
keboola_storage_workspace_create
keboola_storage_workspace_load
keboola_storage_workspace_query
keboola_storage_workspace_unload
keboola_storage_workspace_destroy

// Job Tools (10+)
keboola_jobs_list
keboola_jobs_get
keboola_jobs_run
keboola_jobs_cancel
keboola_jobs_logs
keboola_jobs_stream_logs
keboola_jobs_retry
keboola_jobs_history
keboola_jobs_stats
keboola_jobs_queue_status

// Component Tools (15+)
keboola_components_list
keboola_components_get
keboola_components_search
keboola_config_list
keboola_config_get
keboola_config_create
keboola_config_update
keboola_config_delete
keboola_config_run
keboola_config_validate
keboola_config_copy
keboola_config_export
keboola_config_import
keboola_config_versions
keboola_config_rollback

// Transformation Tools (8+)
keboola_transform_list
keboola_transform_get
keboola_transform_create
keboola_transform_update
keboola_transform_run
keboola_transform_validate
keboola_transform_preview
keboola_transform_debug

// Orchestration Tools (8+)
keboola_orchestration_list
keboola_orchestration_get
keboola_orchestration_run
keboola_orchestration_cancel
keboola_orchestration_status
keboola_orchestration_history
keboola_orchestration_create
keboola_orchestration_update

// Metadata Tools (6+)
keboola_metadata_search
keboola_metadata_get
keboola_metadata_set
keboola_metadata_delete
keboola_metadata_lineage
keboola_metadata_usage

// Project Tools (5+)
keboola_project_info
keboola_project_users
keboola_project_features
keboola_project_limits
keboola_project_stats
```

**Resources (Documentation):**

```
keboola://docs/{topic}
keboola://docs/api/{api}/{endpoint}
keboola://docs/components/{component-id}
keboola://docs/components/{component-id}/schema
keboola://docs/components/{component-id}/examples
keboola://docs/best-practices/{category}
keboola://docs/troubleshooting/{issue}
keboola://examples/{category}/{name}
keboola://schemas/{component-id}
keboola://templates/{template-id}
```

**Prompts (Workflow Templates):**

```typescript
// Pipeline creation
create_data_pipeline(source, destination, transformations)

// Data analysis
analyze_table_data(tableId, analysisType)

// Troubleshooting
debug_failed_job(jobId)
diagnose_performance_issue(componentId)

// Optimization
optimize_pipeline(orchestrationId)
optimize_transformation(transformationId)

// Configuration
configure_extractor(componentType, sourceSystem)
configure_writer(componentType, targetSystem)

// Development
create_dev_workspace(backend)
test_transformation(sql, testData)

// Monitoring
monitor_jobs(filters)
check_data_quality(tableId)

// Migration
migrate_configuration(fromProject, toProject)
export_project_config(projectId)
```

**Streaming Capabilities:**

```typescript
// Real-time job monitoring
streamJobLogs(jobId) // Stream logs as they appear

// Event streaming
streamEvents(filters) // Real-time event stream

// Progress updates
streamProgress(operationId) // Progress bars in Claude
```

### 5. Intelligence Layer

Built-in expertise and automation:

**Pattern Recognition:**
- Detects common pipeline patterns
- Suggests optimizations
- Identifies anti-patterns
- Recommends best practices

**Automatic Code Generation:**
- Generate SQL transformations from description
- Create component configurations from requirements
- Build orchestrations from workflow description
- Generate test data

**Error Resolution:**
- Analyzes error messages
- Searches knowledge base
- Suggests fixes
- Can apply fixes automatically

**Performance Optimization:**
- Analyzes job execution times
- Identifies bottlenecks
- Suggests configuration changes
- Estimates impact of changes

**Data Quality:**
- Automatic data profiling
- Anomaly detection
- Schema validation
- Data quality rules

## Project Structure

```
keboola-claude/
├── packages/
│   ├── client/                 # @keboola/client - API client library
│   │   ├── src/
│   │   │   ├── apis/
│   │   │   │   ├── storage.ts
│   │   │   │   ├── jobs.ts
│   │   │   │   ├── components.ts
│   │   │   │   ├── orchestrations.ts
│   │   │   │   ├── metadata.ts
│   │   │   │   └── admin.ts
│   │   │   ├── client.ts
│   │   │   ├── types.ts
│   │   │   └── index.ts
│   │   ├── tests/
│   │   └── package.json
│   │
│   ├── cli/                    # keboola-cli - CLI tool
│   │   ├── src/
│   │   │   ├── commands/
│   │   │   │   ├── storage/
│   │   │   │   ├── jobs/
│   │   │   │   ├── components/
│   │   │   │   ├── orchestrations/
│   │   │   │   └── metadata/
│   │   │   ├── daemon/         # HTTP server mode
│   │   │   ├── interactive/    # REPL mode
│   │   │   ├── output/         # Formatters
│   │   │   └── index.ts
│   │   ├── tests/
│   │   └── package.json
│   │
│   ├── docs-engine/            # Documentation indexer
│   │   ├── src/
│   │   │   ├── indexer/
│   │   │   ├── search/
│   │   │   ├── embeddings/
│   │   │   └── index.ts
│   │   ├── tests/
│   │   └── package.json
│   │
│   ├── mcp-server/             # MCP server
│   │   ├── src/
│   │   │   ├── tools/
│   │   │   ├── resources/
│   │   │   ├── prompts/
│   │   │   ├── streaming/
│   │   │   └── index.ts
│   │   ├── tests/
│   │   └── package.json
│   │
│   └── intelligence/           # Intelligence layer
│       ├── src/
│       │   ├── patterns/
│       │   ├── optimization/
│       │   ├── codegen/
│       │   ├── errors/
│       │   └── index.ts
│       ├── knowledge/          # Knowledge base
│       └── package.json
│
├── docs/                       # Cached documentation
│   ├── developers-docs/
│   ├── connection-docs/
│   └── component-repos/
│
├── examples/                   # Example usage
│   ├── cli-usage/
│   ├── api-usage/
│   └── claude-workflows/
│
├── scripts/                    # Build and deployment scripts
│   ├── build-all.sh
│   ├── sync-docs.sh
│   └── release.sh
│
├── lerna.json                  # Monorepo config
├── package.json
├── tsconfig.json
└── README.md
```

## Key Innovations

### 1. Daemon Mode for MCP

The CLI can run as a daemon, providing HTTP API for MCP server:

```bash
keboola daemon --port 8080
```

MCP server connects to daemon instead of spawning processes:
- Faster (no process startup overhead)
- Persistent connections
- Streaming support
- Better resource usage

### 2. Real-Time Streaming

Jobs, logs, and events stream in real-time to Claude:

```
User: "Run my MySQL extractor and show me the progress"
Claude:
  Starting job...
  ✓ Extracting table customers (1/5) - 1000 rows
  ✓ Extracting table orders (2/5) - 5000 rows
  ⚠ Warning: Table products has schema changes
  ✓ Extracting table products (3/5) - 500 rows
  ...
  ✓ Job completed in 2m 34s
```

### 3. Interactive Workflows

Claude can create multi-step workflows with user input:

```
User: "Help me set up a new data pipeline"

Claude: I'll help you create a pipeline. Let me ask a few questions:

1. What's your data source?
User: MySQL database

Claude: Great! I found the keboola.ex-db-mysql extractor.
2. Do you have the connection details?
User: Yes, host is db.example.com

Claude: [Creates configuration interactively...]
3. Which tables do you want to extract?
User: customers, orders, products

Claude: [Configures tables...]
Do you want incremental loading?
User: Yes

Claude: [Configures incremental loading...]
Pipeline created! Would you like me to run a test?
```

### 4. Semantic Search

Find docs and examples by meaning, not just keywords:

```
User: "How do I make my extractor faster?"

Claude: [Semantic search finds:]
- Best practices for incremental loading
- Configuration options for parallelism
- Workspace optimization techniques
- Caching strategies
[Provides synthesized answer from multiple sources]
```

### 5. Auto-Fix Capabilities

Claude can analyze and fix issues automatically:

```
User: "My job failed"

Claude:
Analyzing job 12345...
Error: Authentication failed for MySQL connection

I found the issue - the password may have expired.
Would you like me to:
1. Check the connection configuration
2. Test the connection
3. Update the credentials (interactive)

[With permission, Claude can fix the config]
```

## Implementation Priority

### Phase 1: Foundation (Weeks 1-3)
1. API Client Library - Core APIs
2. CLI Tool - Basic commands
3. Simple MCP server integration

### Phase 2: Documentation (Weeks 4-5)
4. Documentation engine
5. Indexing pipeline
6. Search capabilities

### Phase 3: Intelligence (Weeks 6-8)
7. Pattern recognition
8. Code generation
9. Error resolution

### Phase 4: Advanced (Weeks 9-12)
10. Streaming capabilities
11. Interactive workflows
12. Semantic search
13. Auto-fix features

## Success Metrics

- **CLI Adoption**: Downloads, active users
- **API Usage**: Requests per day, unique users
- **Claude Code Integration**: Tool calls, success rate
- **Documentation Access**: Search queries, resource reads
- **Automation**: Auto-generated configs, auto-fixes applied
- **User Satisfaction**: NPS, feedback, issues

## Distribution

### npm Packages
```bash
npm install -g keboola-cli
npm install @keboola/client
npm install @keboola/mcp-server
```

### Claude Code Integration
One-line setup in Claude Code config:
```json
{
  "mcpServers": {
    "keboola": {
      "command": "keboola",
      "args": ["daemon"]
    }
  }
}
```

### Docker
```bash
docker run -p 8080:8080 keboola/claude-mcp
```

## This Is The Way Forward

This architecture gives you:
✅ Standalone CLI for power users
✅ API library for developers
✅ Full Claude Code integration via MCP
✅ Real-time capabilities
✅ Intelligence and automation
✅ Always up-to-date documentation
✅ Multiple use cases, one codebase
✅ Testable, maintainable, scalable

Not three separate options - one comprehensive platform that works everywhere.
