# Keboola Claude - Unified Project Structure

## Monorepo Setup

Using Lerna/Turborepo for managing multiple packages:

```bash
# Initialize the monorepo
mkdir keboola-claude && cd keboola-claude
npm init -y
npm install -D lerna typescript @types/node
npx lerna init
```

## Complete Directory Structure

```
keboola-claude/
│
├── packages/
│   │
│   ├── client/                          # @keboola/client
│   │   ├── src/
│   │   │   ├── apis/
│   │   │   │   ├── storage/
│   │   │   │   │   ├── buckets.ts
│   │   │   │   │   ├── tables.ts
│   │   │   │   │   ├── workspaces.ts
│   │   │   │   │   └── index.ts
│   │   │   │   ├── jobs/
│   │   │   │   │   ├── jobs.ts
│   │   │   │   │   ├── queues.ts
│   │   │   │   │   └── index.ts
│   │   │   │   ├── components/
│   │   │   │   │   ├── components.ts
│   │   │   │   │   ├── configurations.ts
│   │   │   │   │   └── index.ts
│   │   │   │   ├── orchestrations/
│   │   │   │   │   ├── orchestrations.ts
│   │   │   │   │   ├── tasks.ts
│   │   │   │   │   └── index.ts
│   │   │   │   ├── metadata/
│   │   │   │   │   ├── metadata.ts
│   │   │   │   │   ├── lineage.ts
│   │   │   │   │   └── index.ts
│   │   │   │   ├── admin/
│   │   │   │   │   ├── projects.ts
│   │   │   │   │   ├── users.ts
│   │   │   │   │   └── index.ts
│   │   │   │   └── events/
│   │   │   │       ├── events.ts
│   │   │   │       └── index.ts
│   │   │   ├── core/
│   │   │   │   ├── client.ts           # Base HTTP client
│   │   │   │   ├── auth.ts             # Authentication
│   │   │   │   ├── retry.ts            # Retry logic
│   │   │   │   ├── cache.ts            # Caching
│   │   │   │   ├── ratelimit.ts        # Rate limiting
│   │   │   │   ├── streaming.ts        # Streaming support
│   │   │   │   └── websocket.ts        # WebSocket client
│   │   │   ├── types/
│   │   │   │   ├── storage.ts
│   │   │   │   ├── jobs.ts
│   │   │   │   ├── components.ts
│   │   │   │   ├── common.ts
│   │   │   │   └── index.ts
│   │   │   ├── utils/
│   │   │   │   ├── pagination.ts
│   │   │   │   ├── filters.ts
│   │   │   │   └── validators.ts
│   │   │   ├── index.ts
│   │   │   └── client.ts               # Main KeboolaClient export
│   │   ├── tests/
│   │   │   ├── unit/
│   │   │   ├── integration/
│   │   │   └── fixtures/
│   │   ├── docs/
│   │   │   ├── api.md
│   │   │   └── examples.md
│   │   ├── package.json
│   │   ├── tsconfig.json
│   │   └── README.md
│   │
│   ├── cli/                             # keboola-cli
│   │   ├── src/
│   │   │   ├── commands/
│   │   │   │   ├── storage/
│   │   │   │   │   ├── buckets.ts      # bucket list/get commands
│   │   │   │   │   ├── tables.ts       # table operations
│   │   │   │   │   ├── export.ts       # export command
│   │   │   │   │   ├── import.ts       # import command
│   │   │   │   │   ├── workspaces.ts   # workspace commands
│   │   │   │   │   └── index.ts
│   │   │   │   ├── jobs/
│   │   │   │   │   ├── list.ts
│   │   │   │   │   ├── get.ts
│   │   │   │   │   ├── run.ts
│   │   │   │   │   ├── logs.ts
│   │   │   │   │   ├── cancel.ts
│   │   │   │   │   └── index.ts
│   │   │   │   ├── components/
│   │   │   │   │   ├── list.ts
│   │   │   │   │   ├── get.ts
│   │   │   │   │   └── index.ts
│   │   │   │   ├── config/
│   │   │   │   │   ├── list.ts
│   │   │   │   │   ├── get.ts
│   │   │   │   │   ├── create.ts
│   │   │   │   │   ├── update.ts
│   │   │   │   │   ├── delete.ts
│   │   │   │   │   ├── run.ts
│   │   │   │   │   └── index.ts
│   │   │   │   ├── transform/
│   │   │   │   │   ├── create.ts
│   │   │   │   │   ├── run.ts
│   │   │   │   │   ├── validate.ts
│   │   │   │   │   └── index.ts
│   │   │   │   ├── orchestration/
│   │   │   │   │   ├── list.ts
│   │   │   │   │   ├── run.ts
│   │   │   │   │   ├── status.ts
│   │   │   │   │   └── index.ts
│   │   │   │   ├── metadata/
│   │   │   │   │   ├── search.ts
│   │   │   │   │   ├── get.ts
│   │   │   │   │   ├── set.ts
│   │   │   │   │   ├── lineage.ts
│   │   │   │   │   └── index.ts
│   │   │   │   ├── project/
│   │   │   │   │   ├── info.ts
│   │   │   │   │   ├── users.ts
│   │   │   │   │   └── index.ts
│   │   │   │   ├── auth/
│   │   │   │   │   ├── login.ts
│   │   │   │   │   ├── status.ts
│   │   │   │   │   └── index.ts
│   │   │   │   ├── dev/
│   │   │   │   │   ├── workspace.ts
│   │   │   │   │   └── index.ts
│   │   │   │   └── index.ts
│   │   │   ├── daemon/
│   │   │   │   ├── server.ts           # HTTP server
│   │   │   │   ├── routes.ts           # API routes
│   │   │   │   ├── middleware.ts       # Express middleware
│   │   │   │   └── index.ts
│   │   │   ├── interactive/
│   │   │   │   ├── repl.ts             # REPL implementation
│   │   │   │   ├── completer.ts        # Tab completion
│   │   │   │   ├── history.ts          # Command history
│   │   │   │   └── index.ts
│   │   │   ├── output/
│   │   │   │   ├── formatters/
│   │   │   │   │   ├── table.ts        # Table format
│   │   │   │   │   ├── json.ts         # JSON format
│   │   │   │   │   ├── yaml.ts         # YAML format
│   │   │   │   │   ├── csv.ts          # CSV format
│   │   │   │   │   └── index.ts
│   │   │   │   ├── theme.ts            # Color themes
│   │   │   │   ├── progress.ts         # Progress bars
│   │   │   │   └── index.ts
│   │   │   ├── config/
│   │   │   │   ├── manager.ts          # Config file manager
│   │   │   │   ├── schema.ts           # Config schema
│   │   │   │   └── index.ts
│   │   │   ├── utils/
│   │   │   │   ├── prompts.ts          # Interactive prompts
│   │   │   │   ├── validation.ts       # Input validation
│   │   │   │   └── index.ts
│   │   │   ├── index.ts                # CLI entry point
│   │   │   └── cli.ts                  # Command parser
│   │   ├── completions/                # Shell completions
│   │   │   ├── bash.sh
│   │   │   ├── zsh.sh
│   │   │   └── fish.fish
│   │   ├── tests/
│   │   ├── package.json
│   │   ├── tsconfig.json
│   │   └── README.md
│   │
│   ├── docs-engine/                     # @keboola/docs-engine
│   │   ├── src/
│   │   │   ├── indexer/
│   │   │   │   ├── github-indexer.ts   # Index GitHub repos
│   │   │   │   ├── markdown-parser.ts  # Parse markdown
│   │   │   │   ├── component-indexer.ts # Index components
│   │   │   │   ├── scheduler.ts        # Update scheduler
│   │   │   │   └── index.ts
│   │   │   ├── search/
│   │   │   │   ├── full-text.ts        # Full-text search
│   │   │   │   ├── semantic.ts         # Semantic search
│   │   │   │   ├── filters.ts          # Search filters
│   │   │   │   ├── ranking.ts          # Relevance ranking
│   │   │   │   └── index.ts
│   │   │   ├── embeddings/
│   │   │   │   ├── generator.ts        # Generate embeddings
│   │   │   │   ├── store.ts            # Vector store
│   │   │   │   ├── similarity.ts       # Similarity search
│   │   │   │   └── index.ts
│   │   │   ├── catalog/
│   │   │   │   ├── components.ts       # Component catalog
│   │   │   │   ├── schemas.ts          # Schema registry
│   │   │   │   ├── examples.ts         # Example registry
│   │   │   │   └── index.ts
│   │   │   ├── storage/
│   │   │   │   ├── database.ts         # SQLite/PostgreSQL
│   │   │   │   ├── cache.ts            # Cache layer
│   │   │   │   └── index.ts
│   │   │   ├── engine.ts               # Main DocumentationEngine
│   │   │   └── index.ts
│   │   ├── data/                       # Indexed data
│   │   │   ├── docs.db
│   │   │   └── embeddings.db
│   │   ├── tests/
│   │   ├── package.json
│   │   ├── tsconfig.json
│   │   └── README.md
│   │
│   ├── mcp-server/                      # @keboola/mcp-server
│   │   ├── src/
│   │   │   ├── tools/
│   │   │   │   ├── storage-tools.ts    # Storage tools
│   │   │   │   ├── job-tools.ts        # Job tools
│   │   │   │   ├── component-tools.ts  # Component tools
│   │   │   │   ├── transform-tools.ts  # Transformation tools
│   │   │   │   ├── orchestration-tools.ts
│   │   │   │   ├── metadata-tools.ts   # Metadata tools
│   │   │   │   ├── project-tools.ts    # Project tools
│   │   │   │   ├── registry.ts         # Tool registry
│   │   │   │   └── index.ts
│   │   │   ├── resources/
│   │   │   │   ├── documentation.ts    # Doc resources
│   │   │   │   ├── schemas.ts          # Schema resources
│   │   │   │   ├── examples.ts         # Example resources
│   │   │   │   ├── templates.ts        # Template resources
│   │   │   │   └── index.ts
│   │   │   ├── prompts/
│   │   │   │   ├── pipeline.ts         # Pipeline prompts
│   │   │   │   ├── analysis.ts         # Analysis prompts
│   │   │   │   ├── troubleshooting.ts  # Debug prompts
│   │   │   │   ├── optimization.ts     # Optimization prompts
│   │   │   │   ├── configuration.ts    # Config prompts
│   │   │   │   └── index.ts
│   │   │   ├── streaming/
│   │   │   │   ├── job-stream.ts       # Job log streaming
│   │   │   │   ├── event-stream.ts     # Event streaming
│   │   │   │   ├── progress-stream.ts  # Progress updates
│   │   │   │   └── index.ts
│   │   │   ├── daemon-client/
│   │   │   │   ├── http-client.ts      # HTTP client for daemon
│   │   │   │   └── index.ts
│   │   │   ├── server.ts               # MCP server implementation
│   │   │   └── index.ts
│   │   ├── tests/
│   │   ├── package.json
│   │   ├── tsconfig.json
│   │   └── README.md
│   │
│   └── intelligence/                    # @keboola/intelligence
│       ├── src/
│       │   ├── patterns/
│       │   │   ├── detector.ts         # Pattern detection
│       │   │   ├── pipeline-patterns.ts
│       │   │   ├── anti-patterns.ts
│       │   │   └── index.ts
│       │   ├── optimization/
│       │   │   ├── analyzer.ts         # Performance analysis
│       │   │   ├── suggestions.ts      # Optimization suggestions
│       │   │   ├── estimator.ts        # Impact estimation
│       │   │   └── index.ts
│       │   ├── codegen/
│       │   │   ├── sql-generator.ts    # SQL generation
│       │   │   ├── config-generator.ts # Config generation
│       │   │   ├── pipeline-generator.ts
│       │   │   ├── templates.ts        # Code templates
│       │   │   └── index.ts
│       │   ├── errors/
│       │   │   ├── analyzer.ts         # Error analysis
│       │   │   ├── resolution.ts       # Resolution suggestions
│       │   │   ├── knowledge-base.ts   # Error KB
│       │   │   └── index.ts
│       │   ├── quality/
│       │   │   ├── profiler.ts         # Data profiling
│       │   │   ├── anomaly.ts          # Anomaly detection
│       │   │   ├── validation.ts       # Validation rules
│       │   │   └── index.ts
│       │   ├── workflows/
│       │   │   ├── interactive.ts      # Interactive workflows
│       │   │   ├── templates.ts        # Workflow templates
│       │   │   └── index.ts
│       │   ├── intelligence.ts         # Main IntelligenceEngine
│       │   └── index.ts
│       ├── knowledge/                  # Knowledge base
│       │   ├── best-practices/
│       │   ├── common-errors/
│       │   ├── patterns/
│       │   └── optimizations/
│       ├── tests/
│       ├── package.json
│       ├── tsconfig.json
│       └── README.md
│
├── docs/                               # Cached documentation
│   ├── repos/                         # Cloned GitHub repos
│   │   ├── developers-docs/
│   │   ├── connection-docs/
│   │   └── components/
│   └── generated/                     # Generated docs
│       ├── api/
│       └── cli/
│
├── examples/                           # Example usage
│   ├── client-usage/
│   │   ├── basic-operations.ts
│   │   ├── streaming.ts
│   │   └── advanced.ts
│   ├── cli-usage/
│   │   ├── basic-commands.sh
│   │   ├── workflows.sh
│   │   └── automation.sh
│   └── claude-workflows/
│       ├── pipeline-creation.md
│       ├── data-analysis.md
│       └── troubleshooting.md
│
├── scripts/                            # Build and deployment
│   ├── build-all.sh
│   ├── test-all.sh
│   ├── sync-docs.sh
│   ├── release.sh
│   └── dev-setup.sh
│
├── .github/
│   ├── workflows/
│   │   ├── ci.yml
│   │   ├── release.yml
│   │   └── docs-sync.yml
│   └── ISSUE_TEMPLATE/
│
├── lerna.json
├── package.json
├── tsconfig.json
├── .gitignore
├── LICENSE
└── README.md
```

## Package Dependencies

### Root package.json

```json
{
  "name": "keboola-claude",
  "version": "1.0.0",
  "private": true,
  "workspaces": [
    "packages/*"
  ],
  "scripts": {
    "build": "lerna run build",
    "test": "lerna run test",
    "lint": "lerna run lint",
    "clean": "lerna run clean",
    "dev": "lerna run dev --parallel",
    "release": "lerna publish"
  },
  "devDependencies": {
    "lerna": "^8.0.0",
    "typescript": "^5.3.0",
    "@types/node": "^20.0.0",
    "eslint": "^8.0.0",
    "prettier": "^3.0.0",
    "jest": "^29.0.0",
    "@types/jest": "^29.0.0"
  }
}
```

### packages/client/package.json

```json
{
  "name": "@keboola/client",
  "version": "1.0.0",
  "main": "dist/index.js",
  "types": "dist/index.d.ts",
  "scripts": {
    "build": "tsc",
    "test": "jest",
    "dev": "tsc --watch"
  },
  "dependencies": {
    "axios": "^1.6.0",
    "ws": "^8.14.0"
  },
  "devDependencies": {
    "typescript": "^5.3.0",
    "@types/node": "^20.0.0",
    "@types/ws": "^8.5.0",
    "jest": "^29.0.0"
  }
}
```

### packages/cli/package.json

```json
{
  "name": "keboola-cli",
  "version": "1.0.0",
  "bin": {
    "keboola": "dist/index.js"
  },
  "scripts": {
    "build": "tsc",
    "test": "jest",
    "dev": "tsc --watch"
  },
  "dependencies": {
    "@keboola/client": "^1.0.0",
    "commander": "^11.0.0",
    "inquirer": "^9.2.0",
    "chalk": "^5.3.0",
    "ora": "^7.0.0",
    "cli-table3": "^0.6.3",
    "yaml": "^2.3.0",
    "express": "^4.18.0"
  },
  "devDependencies": {
    "typescript": "^5.3.0",
    "@types/node": "^20.0.0",
    "@types/inquirer": "^9.0.0",
    "@types/express": "^4.17.0",
    "jest": "^29.0.0"
  }
}
```

### packages/docs-engine/package.json

```json
{
  "name": "@keboola/docs-engine",
  "version": "1.0.0",
  "main": "dist/index.js",
  "types": "dist/index.d.ts",
  "scripts": {
    "build": "tsc",
    "test": "jest",
    "dev": "tsc --watch"
  },
  "dependencies": {
    "@octokit/rest": "^20.0.0",
    "markdown-it": "^13.0.0",
    "better-sqlite3": "^9.0.0",
    "openai": "^4.0.0",
    "lunr": "^2.3.9"
  },
  "devDependencies": {
    "typescript": "^5.3.0",
    "@types/node": "^20.0.0",
    "@types/better-sqlite3": "^7.6.0",
    "@types/markdown-it": "^13.0.0",
    "jest": "^29.0.0"
  }
}
```

### packages/mcp-server/package.json

```json
{
  "name": "@keboola/mcp-server",
  "version": "1.0.0",
  "bin": {
    "keboola-mcp": "dist/index.js"
  },
  "scripts": {
    "build": "tsc",
    "test": "jest",
    "dev": "tsc --watch"
  },
  "dependencies": {
    "@keboola/client": "^1.0.0",
    "@keboola/docs-engine": "^1.0.0",
    "@keboola/intelligence": "^1.0.0",
    "@modelcontextprotocol/sdk": "^1.0.0",
    "axios": "^1.6.0"
  },
  "devDependencies": {
    "typescript": "^5.3.0",
    "@types/node": "^20.0.0",
    "jest": "^29.0.0"
  }
}
```

### packages/intelligence/package.json

```json
{
  "name": "@keboola/intelligence",
  "version": "1.0.0",
  "main": "dist/index.js",
  "types": "dist/index.d.ts",
  "scripts": {
    "build": "tsc",
    "test": "jest",
    "dev": "tsc --watch"
  },
  "dependencies": {
    "@keboola/client": "^1.0.0",
    "openai": "^4.0.0"
  },
  "devDependencies": {
    "typescript": "^5.3.0",
    "@types/node": "^20.0.0",
    "jest": "^29.0.0"
  }
}
```

## Build Configuration

### Root tsconfig.json

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "Node16",
    "moduleResolution": "Node16",
    "lib": ["ES2022"],
    "declaration": true,
    "declarationMap": true,
    "sourceMap": true,
    "outDir": "./dist",
    "rootDir": "./src",
    "composite": true,
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "resolveJsonModule": true
  },
  "exclude": ["node_modules", "dist", "build"]
}
```

### lerna.json

```json
{
  "version": "independent",
  "npmClient": "npm",
  "command": {
    "publish": {
      "conventionalCommits": true,
      "message": "chore(release): publish"
    }
  },
  "packages": [
    "packages/*"
  ]
}
```

## Development Workflow

### Initial Setup

```bash
# Clone and setup
git clone <repo>
cd keboola-claude
npm install
npm run build

# Sync documentation
./scripts/sync-docs.sh

# Start development
npm run dev
```

### Testing Individual Packages

```bash
# Test client
cd packages/client
npm test

# Test CLI
cd packages/cli
npm test

# Run CLI locally
npm link
keboola --help
```

### Running MCP Server

```bash
# Build all packages
npm run build

# Run MCP server
cd packages/mcp-server
node dist/index.js

# Or via CLI daemon mode
keboola daemon --port 8080
```

## CI/CD Pipeline

### GitHub Actions Workflow

```yaml
# .github/workflows/ci.yml
name: CI

on: [push, pull_request]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
      - run: npm ci
      - run: npm run build
      - run: npm test

  docs-sync:
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v4
      - run: ./scripts/sync-docs.sh
```

This monorepo structure provides:
- Clear separation of concerns
- Shared code between packages
- Independent versioning
- Easy development workflow
- Comprehensive testing
- Automated documentation sync
