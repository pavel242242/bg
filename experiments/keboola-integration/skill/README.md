# Keboola Skill for Claude Code

A Claude Code skill that provides expert knowledge about Keboola platform for data engineering and analysis.

## What is a Skill?

Skills are specialized knowledge modules that enhance Claude Code's capabilities in specific domains. This Keboola skill provides:

- Deep knowledge of Keboola platform architecture
- Best practices for data engineering
- Common patterns and workflows
- Troubleshooting guidance
- Component-specific expertise

## Skill Structure

```
skill/
├── skill.json              # Skill metadata and configuration
├── system-prompt.md        # Core knowledge and expertise
├── knowledge/
│   ├── architecture.md     # Platform architecture
│   ├── storage.md          # Storage concepts
│   ├── transformations.md  # Transformation patterns
│   ├── components.md       # Component catalog
│   └── best-practices.md   # Best practices
├── examples/
│   ├── data-pipeline.md    # Example pipeline
│   ├── transformation.md   # Example transformation
│   ├── orchestration.md    # Example orchestration
│   └── troubleshooting.md  # Common issues
└── tools-guide.md          # Which tools to use for tasks
```

## skill.json Example

```json
{
  "name": "keboola",
  "displayName": "Keboola Data Engineering",
  "version": "1.0.0",
  "description": "Expert knowledge for Keboola platform data engineering and analysis",
  "author": "Your Team",
  "keywords": ["keboola", "data-engineering", "etl", "data-pipelines"],
  "systemPrompt": "system-prompt.md",
  "knowledge": "knowledge/",
  "examples": "examples/",
  "tools": {
    "preferred": ["Bash", "Read", "Write", "Edit", "Grep", "Glob"],
    "mcpServers": ["keboola"]
  },
  "capabilities": [
    "pipeline-design",
    "transformation-writing",
    "component-configuration",
    "data-analysis",
    "troubleshooting",
    "optimization"
  ]
}
```

## System Prompt Template

The system prompt gives Claude deep expertise in Keboola:

```markdown
# Keboola Data Engineering Expert

You are an expert in Keboola platform for data engineering and analysis.

## Core Expertise

### Platform Knowledge
- Keboola Connection architecture and components
- Storage layer: buckets, tables, workspaces
- Component types: extractors, transformations, writers, applications
- Job execution and orchestration
- Data governance and metadata

### Technical Skills
- Designing efficient data pipelines
- Writing SQL and Python transformations
- Configuring extractors and writers
- Optimizing performance and costs
- Debugging failed jobs
- Managing data lineage

### Best Practices
- Incremental loading strategies
- Proper table design and indexing
- Error handling and monitoring
- Testing and validation
- Documentation standards
- Security and access control

## Interaction Guidelines

When helping users:
1. Ask clarifying questions about their data architecture
2. Recommend appropriate components and patterns
3. Provide working configuration examples
4. Explain trade-offs and alternatives
5. Suggest optimizations and best practices
6. Help troubleshoot issues systematically

## Common Tasks

### Pipeline Design
- Analyze source and destination requirements
- Select appropriate extractors and writers
- Design transformation logic
- Plan orchestration and scheduling
- Consider error handling and monitoring

### Transformation Development
- Write clean, efficient SQL
- Use Python for complex logic
- Implement incremental processing
- Add data quality checks
- Document transformation logic

### Troubleshooting
- Analyze error messages and logs
- Check job history and timeline
- Verify configurations
- Test components in isolation
- Recommend fixes and improvements

## Tool Usage

- Use MCP tools (when available) for live Keboola operations
- Use Bash for local data processing and testing
- Use Read/Write/Edit for configuration files
- Use Grep/Glob to search documentation and code
```

## Knowledge Files

### architecture.md
```markdown
# Keboola Platform Architecture

## Core Components

### Storage
- **Buckets**: Logical containers for tables
  - Input buckets (in.*)
  - Output buckets (out.*)
  - System buckets (sys.*)

### Transformations
- **SQL**: Snowflake, Redshift, Synapse
- **Python**: Jupyter notebooks and scripts
- **R**: Statistical computing
- **Julia**: Scientific computing
- **OpenRefine**: Data cleaning

### Components
- **Extractors**: Pull data from sources
- **Writers**: Push data to destinations
- **Applications**: Custom processing logic

...
```

### best-practices.md
```markdown
# Keboola Best Practices

## Pipeline Design

### 1. Use Incremental Loading
```sql
-- Good: Incremental load with timestamp
SELECT *
FROM source_table
WHERE updated_at > ?last_updated
```

### 2. Proper Table Organization
- Group related tables in buckets
- Use consistent naming conventions
- Add descriptions and metadata
- Document data lineage

### 3. Error Handling
- Configure notification rules
- Add data quality checks
- Use validation transformations
- Monitor job failures

...
```

## Examples

### data-pipeline.md
```markdown
# Example: Customer Data Pipeline

## Scenario
Extract customer data from MySQL, transform, and load to Snowflake.

## Pipeline Steps

1. **Extract from MySQL**
   - Component: keboola.ex-db-mysql
   - Tables: customers, orders, products
   - Schedule: Every 6 hours

2. **Transform Data**
   - Join customers with orders
   - Calculate customer lifetime value
   - Enrich with product categories

3. **Load to Snowflake**
   - Component: keboola.wr-db-snowflake
   - Destination: analytics.customers_enriched

## Configuration Examples

### MySQL Extractor Config
```json
{
  "parameters": {
    "db": {
      "host": "mysql.example.com",
      "port": 3306,
      "database": "production",
      "#user": "keboola",
      "#password": "encrypted_password"
    },
    "tables": [
      {
        "name": "customers",
        "outputTable": "in.c-mysql.customers",
        "incremental": true,
        "incrementalFetchingColumn": "updated_at"
      }
    ]
  }
}
```

...
```

## Installation

1. **Package the skill** with all knowledge and examples
2. **Place in Claude Code skills directory** (location TBD)
3. **Activate the skill** in Claude Code settings
4. **Invoke with** `/skill keboola` or automatic activation

## Usage

Once installed, the skill provides:

- **Automatic expertise** when working with Keboola projects
- **Context-aware suggestions** based on your task
- **Quick access** to patterns and examples
- **Integration** with MCP tools if available

## Benefits

- Works offline (no API needed for documentation)
- Fast responses for common questions
- Consistent best practices
- Reduces need to search docs manually
- Can be version-controlled and shared with team
