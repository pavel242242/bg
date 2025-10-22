# Keboola Claude - Quick Start Guide

## 30-Minute Setup

Get the Keboola Claude integration running in 30 minutes.

## Prerequisites

```bash
node --version  # v18 or higher
npm --version   # v9 or higher
git --version
```

## Step 1: Create the Monorepo (5 minutes)

```bash
# Create project directory
mkdir keboola-claude && cd keboola-claude

# Initialize npm project
npm init -y

# Install lerna for monorepo management
npm install -D lerna typescript

# Initialize lerna
npx lerna init

# Create package directories
mkdir -p packages/{client,cli,mcp-server}
```

## Step 2: Build the API Client (10 minutes)

```bash
cd packages/client
npm init -y
npm install axios
npm install -D typescript @types/node

# Create src directory
mkdir -p src/{apis,core,types}
```

Create `packages/client/src/client.ts`:

```typescript
import axios, { AxiosInstance } from 'axios';

export interface KeboolaClientOptions {
  token: string;
  stack?: string;
}

export class KeboolaClient {
  private http: AxiosInstance;

  constructor(options: KeboolaClientOptions) {
    const baseURL = options.stack || 'https://connection.keboola.com';

    this.http = axios.create({
      baseURL,
      headers: {
        'X-StorageApi-Token': options.token,
        'Content-Type': 'application/json',
      },
    });
  }

  // Storage API
  async listBuckets() {
    const { data } = await this.http.get('/v2/storage/buckets');
    return data;
  }

  async listTables(bucketId: string) {
    const { data } = await this.http.get(`/v2/storage/buckets/${bucketId}/tables`);
    return data;
  }

  async getTable(tableId: string) {
    const { data } = await this.http.get(`/v2/storage/tables/${tableId}`);
    return data;
  }

  // Jobs API
  async listJobs(limit = 20) {
    const { data } = await this.http.get('/v2/storage/jobs', {
      params: { limit },
    });
    return data;
  }

  async getJob(jobId: string) {
    const { data } = await this.http.get(`/v2/storage/jobs/${jobId}`);
    return data;
  }

  async runComponent(componentId: string, configId: string) {
    const { data } = await this.http.post('/v2/storage/jobs', {
      component: componentId,
      config: configId,
    });
    return data;
  }

  // Components API
  async listComponents() {
    const { data } = await this.http.get('/v2/storage/components');
    return data;
  }

  async getConfiguration(componentId: string, configId: string) {
    const { data } = await this.http.get(
      `/v2/storage/components/${componentId}/configs/${configId}`
    );
    return data;
  }
}

export default KeboolaClient;
```

Create `packages/client/src/index.ts`:

```typescript
export { KeboolaClient } from './client';
export type { KeboolaClientOptions } from './client';
```

Create `packages/client/tsconfig.json`:

```json
{
  "extends": "../../tsconfig.json",
  "compilerOptions": {
    "outDir": "./dist",
    "rootDir": "./src"
  },
  "include": ["src/**/*"]
}
```

Update `packages/client/package.json`:

```json
{
  "name": "@keboola/client",
  "version": "0.1.0",
  "main": "dist/index.js",
  "types": "dist/index.d.ts",
  "scripts": {
    "build": "tsc",
    "dev": "tsc --watch"
  },
  "dependencies": {
    "axios": "^1.6.0"
  },
  "devDependencies": {
    "typescript": "^5.3.0",
    "@types/node": "^20.0.0"
  }
}
```

Build it:

```bash
npm run build
```

## Step 3: Build the CLI (10 minutes)

```bash
cd ../cli
npm init -y
npm install commander chalk
npm install -D typescript @types/node

mkdir -p src/commands
```

Create `packages/cli/src/cli.ts`:

```typescript
#!/usr/bin/env node
import { Command } from 'commander';
import { KeboolaClient } from '@keboola/client';
import chalk from 'chalk';

const program = new Command();

program
  .name('keboola')
  .description('Keboola CLI for data engineering')
  .version('0.1.0');

// Helper to get client
function getClient(): KeboolaClient {
  const token = process.env.KEBOOLA_API_TOKEN;
  const stack = process.env.KEBOOLA_STACK_URL;

  if (!token) {
    console.error(chalk.red('Error: KEBOOLA_API_TOKEN environment variable is required'));
    process.exit(1);
  }

  return new KeboolaClient({ token, stack });
}

// Storage commands
const storage = program.command('storage').description('Storage operations');

storage
  .command('list-buckets')
  .description('List all storage buckets')
  .action(async () => {
    try {
      const client = getClient();
      const buckets = await client.listBuckets();

      console.log(chalk.bold('\nBuckets:'));
      buckets.forEach((bucket: any) => {
        console.log(`  ${chalk.cyan(bucket.id)} - ${bucket.description || 'No description'}`);
      });
    } catch (error: any) {
      console.error(chalk.red('Error:'), error.message);
      process.exit(1);
    }
  });

storage
  .command('list-tables')
  .argument('<bucket-id>', 'Bucket ID')
  .description('List tables in a bucket')
  .action(async (bucketId) => {
    try {
      const client = getClient();
      const tables = await client.listTables(bucketId);

      console.log(chalk.bold(`\nTables in ${bucketId}:`));
      tables.forEach((table: any) => {
        console.log(`  ${chalk.cyan(table.id)} - ${table.rowsCount || 0} rows`);
      });
    } catch (error: any) {
      console.error(chalk.red('Error:'), error.message);
      process.exit(1);
    }
  });

storage
  .command('get-table')
  .argument('<table-id>', 'Table ID')
  .description('Get table details')
  .action(async (tableId) => {
    try {
      const client = getClient();
      const table = await client.getTable(tableId);

      console.log(chalk.bold(`\nTable: ${table.id}`));
      console.log(`  Rows: ${table.rowsCount || 0}`);
      console.log(`  Size: ${table.dataSizeBytes || 0} bytes`);
      console.log(`  Columns: ${table.columns?.join(', ') || 'None'}`);
    } catch (error: any) {
      console.error(chalk.red('Error:'), error.message);
      process.exit(1);
    }
  });

// Jobs commands
const jobs = program.command('jobs').description('Job operations');

jobs
  .command('list')
  .option('-l, --limit <number>', 'Number of jobs to show', '20')
  .description('List recent jobs')
  .action(async (options) => {
    try {
      const client = getClient();
      const jobsList = await client.listJobs(parseInt(options.limit));

      console.log(chalk.bold('\nRecent Jobs:'));
      jobsList.forEach((job: any) => {
        const status = job.status === 'success'
          ? chalk.green(job.status)
          : chalk.red(job.status);
        console.log(`  ${job.id} - ${status} - ${job.component || 'Unknown'}`);
      });
    } catch (error: any) {
      console.error(chalk.red('Error:'), error.message);
      process.exit(1);
    }
  });

jobs
  .command('get')
  .argument('<job-id>', 'Job ID')
  .description('Get job details')
  .action(async (jobId) => {
    try {
      const client = getClient();
      const job = await client.getJob(jobId);

      console.log(chalk.bold(`\nJob: ${job.id}`));
      console.log(`  Status: ${job.status}`);
      console.log(`  Component: ${job.component || 'Unknown'}`);
      console.log(`  Started: ${job.startTime || 'N/A'}`);
      console.log(`  Duration: ${job.durationSeconds || 0}s`);
    } catch (error: any) {
      console.error(chalk.red('Error:'), error.message);
      process.exit(1);
    }
  });

jobs
  .command('run')
  .argument('<component-id>', 'Component ID')
  .argument('<config-id>', 'Configuration ID')
  .description('Run a component configuration')
  .action(async (componentId, configId) => {
    try {
      const client = getClient();
      const job = await client.runComponent(componentId, configId);

      console.log(chalk.green(`✓ Job started: ${job.id}`));
      console.log(`  Status: ${job.status}`);
      console.log(`  URL: ${job.url || 'N/A'}`);
    } catch (error: any) {
      console.error(chalk.red('Error:'), error.message);
      process.exit(1);
    }
  });

// Components commands
const components = program.command('components').description('Component operations');

components
  .command('list')
  .description('List all components')
  .action(async () => {
    try {
      const client = getClient();
      const componentsList = await client.listComponents();

      console.log(chalk.bold('\nComponents:'));
      componentsList.forEach((component: any) => {
        console.log(`  ${chalk.cyan(component.id)} - ${component.name || 'No name'}`);
      });
    } catch (error: any) {
      console.error(chalk.red('Error:'), error.message);
      process.exit(1);
    }
  });

program.parse();
```

Create `packages/cli/tsconfig.json`:

```json
{
  "extends": "../../tsconfig.json",
  "compilerOptions": {
    "outDir": "./dist",
    "rootDir": "./src"
  },
  "include": ["src/**/*"]
}
```

Update `packages/cli/package.json`:

```json
{
  "name": "keboola-cli",
  "version": "0.1.0",
  "bin": {
    "keboola": "./dist/cli.js"
  },
  "scripts": {
    "build": "tsc",
    "dev": "tsc --watch"
  },
  "dependencies": {
    "@keboola/client": "^0.1.0",
    "commander": "^11.0.0",
    "chalk": "^5.3.0"
  },
  "devDependencies": {
    "typescript": "^5.3.0",
    "@types/node": "^20.0.0"
  }
}
```

Make the CLI executable:

```bash
chmod +x src/cli.ts
```

Build and link:

```bash
npm run build
npm link
```

## Step 4: Build MCP Server (5 minutes)

```bash
cd ../mcp-server
npm init -y
npm install @modelcontextprotocol/sdk
npm install -D typescript @types/node

mkdir -p src
```

Create `packages/mcp-server/src/index.ts`:

```typescript
#!/usr/bin/env node
import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from '@modelcontextprotocol/sdk/types.js';
import { KeboolaClient } from '@keboola/client';

const server = new Server(
  {
    name: 'keboola-mcp-server',
    version: '0.1.0',
  },
  {
    capabilities: {
      tools: {},
    },
  }
);

const token = process.env.KEBOOLA_API_TOKEN;
const stack = process.env.KEBOOLA_STACK_URL;

if (!token) {
  console.error('KEBOOLA_API_TOKEN environment variable is required');
  process.exit(1);
}

const keboola = new KeboolaClient({ token, stack });

// Register tools
server.setRequestHandler(ListToolsRequestSchema, async () => ({
  tools: [
    {
      name: 'keboola_list_buckets',
      description: 'List all storage buckets in your Keboola project',
      inputSchema: {
        type: 'object',
        properties: {},
      },
    },
    {
      name: 'keboola_list_tables',
      description: 'List all tables in a storage bucket',
      inputSchema: {
        type: 'object',
        properties: {
          bucketId: {
            type: 'string',
            description: 'The bucket ID (e.g., in.c-main)',
          },
        },
        required: ['bucketId'],
      },
    },
    {
      name: 'keboola_get_table',
      description: 'Get detailed information about a table',
      inputSchema: {
        type: 'object',
        properties: {
          tableId: {
            type: 'string',
            description: 'The table ID (e.g., in.c-main.customers)',
          },
        },
        required: ['tableId'],
      },
    },
    {
      name: 'keboola_run_component',
      description: 'Run a component configuration',
      inputSchema: {
        type: 'object',
        properties: {
          componentId: {
            type: 'string',
            description: 'Component ID (e.g., keboola.ex-db-mysql)',
          },
          configId: {
            type: 'string',
            description: 'Configuration ID',
          },
        },
        required: ['componentId', 'configId'],
      },
    },
    {
      name: 'keboola_list_jobs',
      description: 'List recent jobs',
      inputSchema: {
        type: 'object',
        properties: {
          limit: {
            type: 'number',
            description: 'Number of jobs to return (default 20)',
          },
        },
      },
    },
    {
      name: 'keboola_get_job',
      description: 'Get job status and details',
      inputSchema: {
        type: 'object',
        properties: {
          jobId: {
            type: 'string',
            description: 'Job ID',
          },
        },
        required: ['jobId'],
      },
    },
  ],
}));

// Handle tool calls
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  try {
    const { name, arguments: args } = request.params;

    switch (name) {
      case 'keboola_list_buckets': {
        const buckets = await keboola.listBuckets();
        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify(buckets, null, 2),
            },
          ],
        };
      }

      case 'keboola_list_tables': {
        const tables = await keboola.listTables(args.bucketId);
        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify(tables, null, 2),
            },
          ],
        };
      }

      case 'keboola_get_table': {
        const table = await keboola.getTable(args.tableId);
        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify(table, null, 2),
            },
          ],
        };
      }

      case 'keboola_run_component': {
        const job = await keboola.runComponent(args.componentId, args.configId);
        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify(job, null, 2),
            },
          ],
        };
      }

      case 'keboola_list_jobs': {
        const jobs = await keboola.listJobs(args.limit || 20);
        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify(jobs, null, 2),
            },
          ],
        };
      }

      case 'keboola_get_job': {
        const job = await keboola.getJob(args.jobId);
        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify(job, null, 2),
            },
          ],
        };
      }

      default:
        throw new Error(`Unknown tool: ${name}`);
    }
  } catch (error: any) {
    return {
      content: [
        {
          type: 'text',
          text: `Error: ${error.message}`,
        },
      ],
      isError: true,
    };
  }
});

// Start the server
async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error('Keboola MCP Server running on stdio');
}

main().catch((error) => {
  console.error('Fatal error:', error);
  process.exit(1);
});
```

Update `packages/mcp-server/package.json`:

```json
{
  "name": "@keboola/mcp-server",
  "version": "0.1.0",
  "type": "module",
  "bin": {
    "keboola-mcp": "./dist/index.js"
  },
  "scripts": {
    "build": "tsc",
    "dev": "tsc --watch"
  },
  "dependencies": {
    "@keboola/client": "^0.1.0",
    "@modelcontextprotocol/sdk": "^1.0.0"
  },
  "devDependencies": {
    "typescript": "^5.3.0",
    "@types/node": "^20.0.0"
  }
}
```

Build it:

```bash
npm run build
```

## Step 5: Test Everything

### Test the CLI:

```bash
export KEBOOLA_API_TOKEN="your-token"
export KEBOOLA_STACK_URL="https://connection.keboola.com"

# List buckets
keboola storage list-buckets

# List tables
keboola storage list-tables in.c-main

# List jobs
keboola jobs list
```

### Test with Claude Code:

Add to your Claude Code config:

```json
{
  "mcpServers": {
    "keboola": {
      "command": "node",
      "args": ["/path/to/keboola-claude/packages/mcp-server/dist/index.js"],
      "env": {
        "KEBOOLA_API_TOKEN": "your-token",
        "KEBOOLA_STACK_URL": "https://connection.keboola.com"
      }
    }
  }
}
```

Restart Claude Code and try:

```
"List all my Keboola buckets"
"Show me the tables in bucket in.c-main"
"Run my MySQL extractor configuration"
```

## Next Steps

Now that you have the basics working:

1. **Add more tools** to MCP server (see ARCHITECTURE.md)
2. **Enhance CLI** with interactive mode, progress bars
3. **Add documentation engine** for searchable docs
4. **Build intelligence layer** for smart suggestions
5. **Add streaming** for real-time job monitoring

## Troubleshooting

**CLI not found:**
```bash
cd packages/cli
npm link
```

**MCP server not connecting:**
- Check that all packages are built: `cd ../.. && npm run build`
- Verify token is set: `echo $KEBOOLA_API_TOKEN`
- Check Claude Code config path

**Import errors:**
- Make sure all packages are built
- Check package.json dependencies
- Run `npm install` in each package

**Token issues:**
- Get token from Keboola Connection UI
- Check token has required permissions
- Verify stack URL is correct

## Success!

You now have:
✅ Working API client
✅ Functional CLI tool
✅ MCP server integrated with Claude Code
✅ Foundation for adding more features

Total time: ~30 minutes

Next: See ARCHITECTURE.md for the full vision and IMPLEMENTATION_GUIDE.md for next steps!
