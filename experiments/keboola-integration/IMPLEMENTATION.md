# Keboola Skill - Practical Implementation

## Three Simple Components

### 1. Documentation Indexer (~200 lines)

Pull Keboola's docs and make them searchable.

```javascript
// indexer/index-docs.js
const { Octokit } = require('@octokit/rest');
const fs = require('fs').promises;
const path = require('path');

const REPOS = [
  'keboola/developers-docs',
  'keboola/connection-docs',
];

async function cloneAndIndexDocs() {
  const octokit = new Octokit();
  const index = {
    documents: [],
    components: {},
    topics: {}
  };

  for (const repo of REPOS) {
    const [owner, repoName] = repo.split('/');

    // Get all markdown files
    const { data: tree } = await octokit.rest.git.getTree({
      owner,
      repo: repoName,
      tree_ref: 'main',
      recursive: true
    });

    const mdFiles = tree.tree.filter(file =>
      file.path.endsWith('.md') && file.type === 'blob'
    );

    for (const file of mdFiles) {
      // Get file content
      const { data: content } = await octokit.rest.repos.getContent({
        owner,
        repo: repoName,
        path: file.path
      });

      const markdown = Buffer.from(content.content, 'base64').toString();

      // Index the document
      index.documents.push({
        path: file.path,
        repo: repo,
        content: markdown,
        url: `https://github.com/${repo}/blob/main/${file.path}`
      });

      // Extract component info if it's a component doc
      if (file.path.includes('components/')) {
        const componentId = extractComponentId(file.path);
        if (componentId) {
          index.components[componentId] = {
            path: file.path,
            content: markdown,
            url: `https://github.com/${repo}/blob/main/${file.path}`
          };
        }
      }
    }
  }

  // Save index
  await fs.writeFile(
    'docs/index.json',
    JSON.stringify(index, null, 2)
  );

  console.log(`Indexed ${index.documents.length} documents`);
  console.log(`Found ${Object.keys(index.components).length} components`);
}

function extractComponentId(path) {
  const match = path.match(/components\/([^\/]+)/);
  return match ? match[1] : null;
}

cloneAndIndexDocs().catch(console.error);
```

**Output**: `docs/index.json` with all Keboola documentation

### 2. Skill Definition (Pure Markdown)

Teach Claude about Keboola through markdown files.

```
skill/
├── skill.json
├── system-prompt.md
├── knowledge/
│   ├── 01-architecture.md
│   ├── 02-storage.md
│   ├── 03-components.md
│   ├── 04-transformations.md
│   ├── 05-orchestration.md
│   └── 06-best-practices.md
└── examples/
    ├── mysql-extractor.json
    ├── snowflake-writer.json
    ├── sql-transformation.sql
    ├── python-transformation.py
    └── complete-pipeline.md
```

**skill/system-prompt.md** (excerpt):

```markdown
# Keboola Data Engineering Expert

You are an expert in the Keboola data platform. You help users design
data pipelines, write transformations, configure components, and
troubleshoot issues.

## Core Concepts

### Storage
Keboola Storage is organized into:
- **Buckets**: Logical containers (in.c-*, out.c-*, sys.c-*)
- **Tables**: CSV files with metadata
- **Workspaces**: Temporary databases for transformations

### Components
Three main types:
- **Extractors**: Pull data from sources (prefix: ex-)
- **Writers**: Push data to destinations (prefix: wr-)
- **Applications**: Custom processing (no prefix)

### Transformations
Keboola supports:
- SQL transformations (Snowflake, Redshift, Synapse)
- Python transformations
- R transformations
- OpenRefine transformations

### Orchestrations
Orchestrations (now called "Flows") define the order of component
execution. Each orchestration contains tasks that run sequentially
or in parallel.

## Using Keboola APIs

When you need to interact with Keboola, use these APIs:

**Storage API**: `https://connection.keboola.com/v2/storage`
- GET /buckets - List buckets
- GET /tables/{tableId} - Get table info
- POST /tables/{tableId}/export-async - Export table

**Job Queue API**: `https://queue.keboola.com`
- POST /jobs - Create job
- GET /jobs/{jobId} - Get job status

For API calls, you can:
1. Use the `keboola_api` MCP tool if available
2. Suggest using `curl` commands
3. Show Python code with `kbcstorage` library
4. Show example API requests

## Best Practices

### Pipeline Design
- Use incremental loading when possible
- Organize tables in logical buckets
- Add descriptions and metadata
- Document data lineage

### Transformations
- Keep SQL transformations simple and focused
- Use workspace for complex multi-step logic
- Add data quality checks
- Test with sample data first

### Error Handling
- Configure notifications for failed jobs
- Add validation transformations
- Monitor job duration and resource usage
- Set up alerting for data freshness

## Common Patterns

### Incremental Extraction
```sql
-- Use a state column to track progress
SELECT *
FROM source_table
WHERE updated_at > ?last_run_timestamp
```

### Data Quality Check
```sql
-- Validate before proceeding
SELECT
  COUNT(*) as total_rows,
  COUNT(DISTINCT customer_id) as unique_customers,
  COUNT(*) - COUNT(customer_id) as null_customer_ids
FROM input_table
```

### Upsert Pattern
```sql
-- Merge new and existing data
MERGE INTO target_table t
USING staging_table s ON t.id = s.id
WHEN MATCHED THEN UPDATE SET ...
WHEN NOT MATCHED THEN INSERT ...
```

## Troubleshooting

### Job Failed
1. Check job logs via Storage API
2. Verify configuration (especially credentials)
3. Check input data format
4. Review component-specific requirements
5. Test with smaller dataset

### Slow Performance
1. Review table sizes and row counts
2. Check for full table scans
3. Enable incremental loading
4. Use workspace for complex logic
5. Consider parallelization

### Data Quality Issues
1. Add validation transformations
2. Check source data format
3. Verify column mappings
4. Review null handling
5. Add data profiling step

## How to Help Users

When a user asks for help:

1. **Understand the goal**: Ask clarifying questions
2. **Suggest architecture**: Recommend components and flow
3. **Provide configuration**: Show exact JSON configs
4. **Explain trade-offs**: Discuss alternatives
5. **Add best practices**: Suggest improvements
6. **Help troubleshoot**: Analyze errors systematically

You have access to:
- Full Keboola documentation (indexed)
- Component configurations and examples
- API references
- Best practices and patterns
- Common error resolutions

Use this knowledge to provide expert guidance on any Keboola-related task.
```

**skill/knowledge/06-best-practices.md**:

```markdown
# Keboola Best Practices

## Pipeline Design

### 1. Use Meaningful Names
- Buckets: `in.c-marketing`, `out.c-analytics`
- Tables: `customers`, `orders`, `customer_orders_enriched`
- Configs: `mysql-production-daily`, `snowflake-analytics-hourly`

### 2. Organize by Domain
```
in.c-sales/         # Sales data from various sources
  - sfdc_accounts
  - sfdc_opportunities
  - salesforce_contacts

in.c-marketing/     # Marketing data
  - hubspot_contacts
  - google_analytics
  - facebook_ads
```

### 3. Incremental Loading
Always use incremental loading for large tables:

```json
{
  "parameters": {
    "tables": [{
      "name": "customers",
      "incremental": true,
      "incrementalFetchingColumn": "updated_at",
      "incrementalFetchingLimit": 100000
    }]
  }
}
```

## Transformation Patterns

### Pattern 1: Staging → Processing → Output
```sql
-- Step 1: Staging (validate and clean)
CREATE TABLE staging_customers AS
SELECT
  id,
  TRIM(name) as name,
  LOWER(email) as email,
  updated_at
FROM "in.c-main.customers"
WHERE updated_at IS NOT NULL;

-- Step 2: Processing (business logic)
CREATE TABLE processed_customers AS
SELECT
  s.id,
  s.name,
  s.email,
  COUNT(o.id) as order_count,
  SUM(o.amount) as lifetime_value
FROM staging_customers s
LEFT JOIN "in.c-main.orders" o ON s.id = o.customer_id
GROUP BY s.id, s.name, s.email;

-- Step 3: Output
CREATE TABLE "out.c-analytics.customers_enriched" AS
SELECT * FROM processed_customers;
```

### Pattern 2: Incremental Processing
```sql
-- Only process new/changed records
CREATE TABLE "out.c-main.customers_processed" AS
SELECT
  c.*,
  CURRENT_TIMESTAMP() as processed_at
FROM "in.c-main.customers" c
LEFT JOIN "out.c-main.customers_processed" p
  ON c.id = p.id AND c.updated_at <= p.updated_at
WHERE p.id IS NULL;  -- Only new or updated records
```

### Pattern 3: Data Quality Checks
```sql
-- Validate before processing
CREATE TABLE data_quality_check AS
SELECT
  'customers' as table_name,
  COUNT(*) as total_rows,
  COUNT(DISTINCT id) as unique_ids,
  COUNT(*) - COUNT(id) as null_ids,
  COUNT(*) - COUNT(email) as null_emails,
  COUNT(*) - COUNT(DISTINCT id) as duplicate_ids
FROM "in.c-main.customers";

-- Fail if quality is bad
-- (Keboola can stop orchestration if this table is empty)
CREATE TABLE quality_passed AS
SELECT * FROM data_quality_check
WHERE duplicate_ids = 0
  AND null_ids = 0
  AND total_rows > 0;
```

## Component Configuration

### MySQL Extractor Example
```json
{
  "parameters": {
    "db": {
      "host": "mysql.example.com",
      "port": 3306,
      "database": "production",
      "#user": "keboola_reader",
      "#password": "encrypted_password"
    },
    "tables": [
      {
        "name": "customers",
        "outputTable": "in.c-mysql.customers",
        "incremental": true,
        "incrementalFetchingColumn": "updated_at",
        "primaryKey": ["id"],
        "columns": ["id", "name", "email", "updated_at"]
      }
    ]
  }
}
```

### Snowflake Writer Example
```json
{
  "parameters": {
    "db": {
      "host": "account.snowflakecomputing.com",
      "database": "ANALYTICS",
      "schema": "PUBLIC",
      "#user": "KEBOOLA_WRITER",
      "#password": "encrypted_password",
      "warehouse": "COMPUTE_WH"
    },
    "tables": [
      {
        "tableId": "out.c-analytics.customers_enriched",
        "dbName": "CUSTOMERS",
        "incremental": false,
        "primaryKey": ["id"],
        "items": [
          {"name": "id", "dbName": "ID", "type": "NUMBER"},
          {"name": "name", "dbName": "NAME", "type": "VARCHAR"},
          {"name": "order_count", "dbName": "ORDER_COUNT", "type": "NUMBER"}
        ]
      }
    ]
  }
}
```

## Error Handling

### 1. Notifications
Configure notifications for each orchestration:
- Slack channel for failures
- Email for warnings
- PagerDuty for critical pipelines

### 2. Retry Logic
Use orchestration retry settings:
- Retry failed tasks up to 3 times
- Exponential backoff between retries
- Stop orchestration on persistent failures

### 3. Validation Steps
Add validation transformations:
```sql
-- Check row counts
CREATE TABLE validation AS
SELECT
  (SELECT COUNT(*) FROM input_table) as input_count,
  (SELECT COUNT(*) FROM output_table) as output_count,
  CASE
    WHEN input_count = 0 THEN 'ERROR: No input data'
    WHEN output_count = 0 THEN 'ERROR: No output data'
    WHEN output_count < input_count * 0.9 THEN 'WARNING: Significant data loss'
    ELSE 'OK'
  END as status;
```

## Performance Optimization

### 1. Use Workspaces for Complex Logic
When you have many transformation steps, use a workspace:
- Load tables into workspace once
- Run all transformations in workspace
- Export only final results
- Much faster than separate transformations

### 2. Parallel Execution
Configure tasks to run in parallel when possible:
```
Task 1: Extract from MySQL      }
Task 2: Extract from PostgreSQL  } Run in parallel
Task 3: Extract from Salesforce }
  ↓
Task 4: Transform and join (waits for 1-3)
  ↓
Task 5: Load to Snowflake
```

### 3. Incremental Everything
- Incremental extraction
- Incremental transformation
- Incremental loading

Reduces processing time from hours to minutes.

## Monitoring

### Key Metrics to Track
1. Job duration trends
2. Data volume changes
3. Error rates
4. Data freshness
5. Resource usage (credits)

### Alerting Rules
- Job failed → Immediate alert
- Job duration > 2x normal → Warning
- Data volume changed > 50% → Warning
- No data received in 24h → Alert
- Credit usage spike → Warning

## Security

### 1. Credentials
- Never store passwords in plaintext
- Use Keboola's encryption (# prefix)
- Rotate credentials regularly
- Use read-only accounts for extractors

### 2. Access Control
- Limit project access
- Use separate projects for dev/prod
- Audit user actions regularly

### 3. Data Governance
- Tag sensitive data
- Document data lineage
- Set retention policies
- Comply with GDPR/CCPA

## Common Mistakes to Avoid

### ❌ Full table loads for large tables
Use incremental loading instead.

### ❌ No error handling
Always add validation and notifications.

### ❌ Hardcoded values in transformations
Use variables and configuration tables.

### ❌ No testing
Test with sample data before production.

### ❌ Poor naming conventions
Use clear, consistent names.

### ❌ No documentation
Document your pipelines and transformations.

### ❌ Ignoring performance
Monitor and optimize regularly.

### ❌ No backup strategy
Export configurations and data regularly.

## Resources

- Keboola Developer Documentation: https://developers.keboola.com
- Component Catalog: https://components.keboola.com
- API Reference: https://developers.keboola.com/integrate/storage/api/
- Community Forum: https://community.keboola.com
- Support: https://support.keboola.com
```

### 3. Simple MCP Wrapper (~200 lines)

Just expose Keboola's APIs to Claude.

```javascript
// mcp-server/index.js
#!/usr/bin/env node
import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
  ListResourcesRequestSchema,
  ReadResourceRequestSchema,
} from '@modelcontextprotocol/sdk/types.js';
import axios from 'axios';
import fs from 'fs/promises';

const KEBOOLA_TOKEN = process.env.KEBOOLA_API_TOKEN;
const KEBOOLA_URL = process.env.KEBOOLA_STACK_URL || 'https://connection.keboola.com';

// Load indexed documentation
const docsIndex = JSON.parse(
  await fs.readFile('./docs/index.json', 'utf-8')
);

const server = new Server({
  name: 'keboola',
  version: '1.0.0',
}, {
  capabilities: {
    tools: {},
    resources: {},
  },
});

// Helper: Call Keboola API
async function callKeboolaAPI(endpoint, method = 'GET', data = null) {
  return axios({
    method,
    url: `${KEBOOLA_URL}/v2/storage/${endpoint}`,
    headers: {
      'X-StorageApi-Token': KEBOOLA_TOKEN,
      'Content-Type': 'application/json',
    },
    data,
  });
}

// Register tools - simple wrappers around Keboola APIs
server.setRequestHandler(ListToolsRequestSchema, async () => ({
  tools: [
    {
      name: 'keboola_storage_api',
      description: 'Call Keboola Storage API',
      inputSchema: {
        type: 'object',
        properties: {
          endpoint: { type: 'string', description: 'API endpoint (e.g., "buckets", "tables/in.c-main.customers")' },
          method: { type: 'string', enum: ['GET', 'POST', 'PUT', 'DELETE'], default: 'GET' },
          data: { type: 'object', description: 'Request body for POST/PUT' },
        },
        required: ['endpoint'],
      },
    },
    {
      name: 'keboola_search_docs',
      description: 'Search Keboola documentation',
      inputSchema: {
        type: 'object',
        properties: {
          query: { type: 'string', description: 'Search query' },
        },
        required: ['query'],
      },
    },
  ],
}));

// Handle tool calls
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  try {
    if (name === 'keboola_storage_api') {
      const response = await callKeboolaAPI(
        args.endpoint,
        args.method || 'GET',
        args.data
      );
      return {
        content: [{
          type: 'text',
          text: JSON.stringify(response.data, null, 2),
        }],
      };
    }

    if (name === 'keboola_search_docs') {
      const results = docsIndex.documents.filter(doc =>
        doc.content.toLowerCase().includes(args.query.toLowerCase())
      );
      return {
        content: [{
          type: 'text',
          text: JSON.stringify(results.slice(0, 5), null, 2),
        }],
      };
    }
  } catch (error) {
    return {
      content: [{
        type: 'text',
        text: `Error: ${error.message}`,
      }],
      isError: true,
    };
  }
});

// Expose documentation as resources
server.setRequestHandler(ListResourcesRequestSchema, async () => ({
  resources: docsIndex.documents.map(doc => ({
    uri: `keboola://docs/${doc.path}`,
    name: doc.path,
    mimeType: 'text/markdown',
  })),
}));

server.setRequestHandler(ReadResourceRequestSchema, async (request) => {
  const doc = docsIndex.documents.find(d =>
    `keboola://docs/${d.path}` === request.params.uri
  );

  return {
    contents: [{
      uri: request.params.uri,
      mimeType: 'text/markdown',
      text: doc ? doc.content : 'Not found',
    }],
  };
});

// Start server
const transport = new StdioServerTransport();
await server.connect(transport);
console.error('Keboola MCP server running');
```

## That's It

**Total code**: ~400 lines
**Total size**: ~50MB (mostly docs)
**Complexity**: Minimal
**Maintenance**: Low (just sync docs)

The skill is pure knowledge. The MCP server is a simple wrapper. Everything leverages what Keboola already built.
