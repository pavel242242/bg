# Keboola MCP Server

A Model Context Protocol server that exposes Keboola platform capabilities to Claude Code.

## Architecture

```
keboola-mcp-server/
├── src/
│   ├── index.ts                 # MCP server entry point
│   ├── keboola-client.ts        # Keboola API client wrapper
│   ├── tools/
│   │   ├── storage.ts           # Storage API tools
│   │   │   - list-buckets
│   │   │   - list-tables
│   │   │   - get-table-info
│   │   │   - export-table
│   │   │   - import-data
│   │   ├── jobs.ts              # Job management
│   │   │   - run-component
│   │   │   - get-job-status
│   │   │   - list-jobs
│   │   ├── components.ts        # Component operations
│   │   │   - list-components
│   │   │   - get-configuration
│   │   │   - create-configuration
│   │   │   - update-configuration
│   │   ├── orchestration.ts     # Orchestrations
│   │   │   - list-orchestrations
│   │   │   - run-orchestration
│   │   │   - get-flow-status
│   │   └── metadata.ts          # Metadata operations
│   │       - get-metadata
│   │       - set-metadata
│   │       - search-metadata
│   ├── resources/
│   │   ├── documentation.ts     # Serve docs as resources
│   │   └── schemas.ts           # Component schemas
│   └── prompts/
│       ├── analysis.ts          # Data analysis templates
│       ├── pipeline.ts          # Pipeline creation templates
│       └── troubleshooting.ts   # Debugging templates
├── docs/                        # Cached documentation
│   ├── developer/
│   ├── connections/
│   └── components/
├── package.json
├── tsconfig.json
└── README.md
```

## Key Tools to Implement

### Storage Tools
- `keboola_list_buckets` - List all storage buckets
- `keboola_list_tables` - List tables in a bucket
- `keboola_get_table` - Get table data and metadata
- `keboola_query_table` - Query table with SQL
- `keboola_create_table` - Create new table

### Job Tools
- `keboola_run_component` - Execute a component
- `keboola_get_job` - Get job status and logs
- `keboola_list_jobs` - List recent jobs
- `keboola_cancel_job` - Cancel running job

### Component Tools
- `keboola_list_components` - List available components
- `keboola_get_config` - Get component configuration
- `keboola_create_config` - Create new configuration
- `keboola_run_config` - Run a configuration

### Orchestration Tools
- `keboola_list_orchestrations` - List all flows
- `keboola_run_orchestration` - Trigger orchestration
- `keboola_get_flow_status` - Get orchestration status

### Metadata Tools
- `keboola_search_metadata` - Search by metadata tags
- `keboola_get_lineage` - Get data lineage
- `keboola_get_usage` - Get usage statistics

## Resources to Expose

### Documentation Resources
```
keboola://docs/developer/{topic}
keboola://docs/components/{component-id}
keboola://docs/connection/{connector}
keboola://docs/api/{endpoint}
```

### Schema Resources
```
keboola://schema/component/{component-id}
keboola://schema/api/{version}
```

## Prompt Templates

### Data Analysis
```typescript
{
  name: "analyze_keboola_data",
  description: "Analyze data from Keboola storage",
  arguments: [
    { name: "bucket", description: "Storage bucket name" },
    { name: "table", description: "Table name" },
    { name: "analysis_type", description: "Type of analysis" }
  ]
}
```

### Pipeline Creation
```typescript
{
  name: "create_keboola_pipeline",
  description: "Create a data pipeline in Keboola",
  arguments: [
    { name: "source", description: "Data source" },
    { name: "transformations", description: "Transformation steps" },
    { name: "destination", description: "Output destination" }
  ]
}
```

## Setup

1. **Install dependencies:**
   ```bash
   npm init -y
   npm install @modelcontextprotocol/sdk axios
   npm install -D typescript @types/node
   ```

2. **Configure TypeScript:**
   ```json
   {
     "compilerOptions": {
       "target": "ES2022",
       "module": "Node16",
       "moduleResolution": "Node16",
       "outDir": "./build",
       "rootDir": "./src",
       "strict": true,
       "esModuleInterop": true
     }
   }
   ```

3. **Set environment variables:**
   ```bash
   export KEBOOLA_API_TOKEN="your-token"
   export KEBOOLA_STACK_URL="https://connection.keboola.com"
   ```

4. **Add to Claude Code config:**
   ```json
   {
     "mcpServers": {
       "keboola": {
         "command": "node",
         "args": ["./build/index.js"],
         "env": {
           "KEBOOLA_API_TOKEN": "${KEBOOLA_API_TOKEN}",
           "KEBOOLA_STACK_URL": "${KEBOOLA_STACK_URL}"
         }
       }
     }
   }
   ```

## Implementation Steps

1. Set up project structure
2. Implement Keboola API client
3. Create MCP server with storage tools
4. Add job management tools
5. Add component tools
6. Implement documentation resources
7. Add prompt templates
8. Test with Claude Code
9. Publish to npm

## Testing

```typescript
// Test storage tool
await mcp.callTool('keboola_list_buckets', {});

// Test job tool
await mcp.callTool('keboola_run_component', {
  component: 'keboola.ex-db-mysql',
  config: 'my-mysql-extractor'
});

// Test resource
await mcp.readResource('keboola://docs/developer/storage');
```

## Benefits

- Direct API access from Claude Code
- Real-time data operations
- Automated pipeline creation
- Job monitoring and debugging
- Metadata-driven workflows
- Documentation at your fingertips
