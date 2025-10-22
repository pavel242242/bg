# Keboola Knowledge Map

## Executive Summary

Keboola is a cloud-based data integration, transformation, and orchestration platform. The documentation is split into two main repositories:
- **connection-docs**: User-facing documentation (~1,629 lines)
- **developers-docs**: Developer documentation (~1,164 lines)

The platform consists of 85+ data source connectors (extractors), 29+ data destination connectors (writers), transformations with multiple backends, orchestration/flows, storage management, and extensibility through custom components.

---

## Core Platform Concepts

### Fundamental Architecture
- **Projects**: Basic organizational unit in Keboola; all work happens within projects
- **Jobs**: Asynchronous batch operations executed in the background
- **Tokens**: Authorization mechanism for API access; can be restricted for specific resources
- **Stacks**: Deployment instances (multi-tenant across AWS, Azure, GCP regions; single-tenant available)
- **Components**: Modular units that extract, transform, write, or enhance data

### Key Principles
1. **Multi-tenant deployment model**: Projects grouped into Organizations
2. **Data safety through isolation**: All transformations work on copies of data in isolated workspaces
3. **Input/Output mapping**: Secure separation between source data and transformation environment
4. **Versioning & rollback**: All configurations automatically versioned
5. **Pay-as-you-go model**: Available alongside subscription plans
6. **Data governance**: Complete tracking of all operations with metadata collection

---

## Components Overview

Keboola components are modular units that can be:
- **Extractors (Data Source Connectors)**: Import data from external sources (85+ available)
- **Writers (Data Destination Connectors)**: Export data to external systems (29+ available)
- **Transformations**: Manipulate data using SQL, Python, R, Julia, or dbt
- **Applications**: Pre-built blocks for advanced tasks (sentiment analysis, geocoding, etc.)
- **Data Apps**: Web applications built with Streamlit
- **Custom Components**: User-created or third-party components

### Component Configuration
- Stored in Storage with JSON schema
- Support for configuration rows (for repeated tasks with different parameters)
- Common interface shared across all Docker-based components
- API-driven (can be created, run, and managed programmatically)

---

## Data Source Connectors (Extractors)

### 85+ Total Extractors Organized by Category

#### Communication (7 extractors)
- Email Attachments
- Email IMAP
- Gmail
- Google Calendar
- Intercom
- MS Outlook
- Slack

#### Database (10 extractors)
- Azure Storage Table
- BigQuery
- CosmosDB
- FileMaker
- MongoDB (with mapping support)
- MS SQL
- MySQL
- Oracle
- PostgreSQL
- SQL DB

#### ERP (2 extractors)
- K2
- NetSuite

#### Marketing & Sales (27+ extractors)
Major platforms:
- Google Ads, Google Analytics, Google AdManager, Google DV360, Google CM360
- Facebook Ads, LinkedIn Pages, TikTok Ads, Pinterest Ads
- Bing Ads
- Salesforce
- HubSpot (via generic extractor)
- Mailchimp
- Stripe, Pipedrive, Zoho, ServiceNow
- BigCommerce, Shoptet
- Adform DSP Reports, Criteo, Babelforce
- ChartMogul, Customer.io
- Market Vision, Sklik
- GoodData Reports

#### Social Networks (4 extractors)
- Facebook
- Instagram
- YouTube
- YouTube Reporting

#### Storage Services (8 extractors)
- AWS S3
- Azure Data Lake Gen2
- Google Drive
- FTP
- HTTP
- OneDrive Excel Sheets
- OneDrive Files
- Storage API

#### Other/Specialized (23+ extractors)
- Airtable
- AWS CUR Reports
- Azure Cost
- CEPS
- Currency Rates
- Dark Sky / Weather API
- DynamoDB Streams
- Generic extractor (for custom APIs)
- Geocoding Augmentation
- GitHub
- Google Search Console
- HiBob
- Mapbox
- Okta
- Papertrail
- Pingdom
- ServiceNow
- Stripe
- Telemetry Data
- Time Doctor 2
- What3Words
- YourPass

---

## Data Destination Connectors (Writers)

### 29+ Total Writers Organized by Category

#### Business Intelligence (4 writers)
- GoodData
- Looker
- Tableau
- ThoughtSpot

#### Databases (7 writers)
- BigQuery
- Exasol
- Firebolt
- MS SQL
- MySQL
- Oracle
- PostgreSQL
- Redshift
- Snowflake
- Synapse

#### Storage Services (8 writers)
- AWS S3
- Google Cloud Storage
- Google Drive
- Google Sheets
- Dropbox
- OneDrive
- SFTP
- Keboola Storage API

#### Other (2 writers)
- Azure Event Hub
- YourPass

---

## Transformations & Workspaces

### Transformation Backends
Keboola supports multiple SQL and scripting backends for transformations:

#### SQL Backends
- **Snowflake** (default, recommended)
- **Amazon Redshift** (custom cluster)
- **Google BigQuery**
- **Microsoft Synapse** (Azure)
- **Oracle** (available)

#### Scripting Backends
- **Python** (popular for data processing)
- **R** (statistical analysis)
- **Julia** (planned)

### Key Transformation Features
- **Mapping**: Input/output mapping for data isolation
- **Staging**: Temporary storage during transformation execution
- **Versioning**: Automatic versioning of all changes with rollback capability
- **Workspaces**: Isolated environments for interactive development
- **Code organization**: Support for blocks and code pieces within transformations
- **Shared Code**: Reusable code blocks across transformations
- **Variables**: Parametrization support
- **Code Patterns**: Pre-built patterns for common tasks
- **dbt Integration**: Native support for dbt transformations

### Workspace Types
- **SQL Workspaces**: Via database provider IDE or SQL IDE (Snowflake web interface available)
- **Python/R/Julia Workspaces**: JupyterLab environment (managed, hosted)
- **Features**: Load/unload data, resume capability, auto-sleep after 1 hour inactivity

---

## Storage

### Storage Architecture
The central component for data management, consisting of:

#### Table Storage
- **Buckets**: Containers for tables, organized into stages
- **In stage**: Raw data (typically from extractors)
- **Out stage**: Processed data (typically from transformations)
- **Tables**: Data organized in rows and columns
- **Aliases**: View-like references to existing tables (read-only, can be filtered)
- **Primary Keys**: Can be defined on one or more columns
- **Metadata**: Key-value storage for arbitrary metadata (including column data types)

#### File Storage
- Storage for raw files uploaded to the project
- Can be accessed by transformations and applications

#### Advanced Features
- **Column Data Types**: Native type support for various data types
- **Table Snapshots**: Ability to revert to earlier versions
- **Backend Properties**: Choose appropriate backend for bucket creation (Snowflake, Redshift, BigQuery, etc.)
- **Data Lineage**: Automatic tracking of data origin and usage

### Storage Data Flows
1. Extractors → In-stage buckets
2. Transformations → Tables (with input/output mapping)
3. Writers → External systems

---

## Flows & Orchestration

### Flows (Modern Approach - Recommended)
Automate data pipelines with:
- **Flow Builder**: Drag-and-drop visual interface
- **Steps/Phases**: Sequential steps, parallel tasks within steps
- **Component chaining**: Chain extractors, transformations, writers
- **Scheduling**: Time-based or trigger-based execution
- **Parallelization**: Execute independent tasks in parallel
- **Control**: Skip tasks, continue on failure, set advanced parameters
- **Monitoring**: Real-time status, run history, detailed job breakdown

### Orchestrator (Legacy - For Legacy Components Only)
Earlier automation approach:
- Define dependencies between components
- Organize components into logical blocks/pipelines
- Schedule automated and repeated execution
- Single task orchestrations available via "Automate" button

### Scheduling Options
- Predefined intervals (hourly, daily, weekly, monthly, etc.)
- Custom schedules (cron-like specification)
- Trigger-based (when tables are updated)
- Manual execution

---

## Applications

### Purpose
Pre-defined blocks with set functionality for advanced tasks:
- Sentiment analysis
- Association discovery
- Histogram grouping
- Data enrichment (weather, exchange rates)
- Geocoding augmentation
- Data validation and quality checks

### Application Types

#### AI Applications
- **Generative AI**: Integration of LLM-based capabilities
- **AI Component Suggestions**: Intelligent recommendations for components

#### Trigger Applications
- dbt Cloud Job Trigger
- Deepnote Notebook Execution Trigger
- Exasol Cluster Starter
- Orchestration Trigger Queue v2

### Characteristics
- Created by Keboola or third parties
- Can be billed separately (some free, some paid)
- Can send data to external services
- Can be created by users (if published, registered in Developer Portal)
- Support provided by authors
- Terms and conditions may vary

### Applications vs. Transformations
| Feature | Transformations | Applications |
|---------|-----------------|--------------|
| Code visibility | Public in project | Can be hidden |
| Scope | Project-specific | Can be shared across projects |
| Versioning | Configuration-based | External versioning |
| Creator | Any user | Keboola, 3rd parties, users |
| Code sharing | Via shared code | Via component publication |

---

## Data Apps

### Overview
Simple interactive web applications built with Streamlit for:
- Recommendation engines
- Interactive segmentation
- Data visualization
- Custom reporting tools
- Financial analysis apps

### Deployment Options
1. **Code**: Direct Streamlit code paste (simple, one-page apps)
2. **Git Repository**: Git-based deployment (complex apps)
   - GitHub, Bitbucket, or other providers
   - Supports private keys/access tokens for authentication

### Features
- Accessible inside project and publicly from outside
- Additional Python packages support
- Base image management
- Terminal log tab for debugging
- OIDC authentication options (Auth0, Okta, Microsoft Entra ID, Google Cloud Platform)

---

## Management & Governance

### Project Management
- **Projects**: Basic organizational unit (1 on Free Plan, multiple on subscription)
- **Organizations**: Group multiple projects with shared management
- **Users**: Administrators, Guest Users, Service Accounts/Tokens
- **Roles**: Admin, Guest, Limited (via tokens)
- **User limits**: Count quota for Admins/Guests; service accounts don't count

### Data Governance
- **Jobs**: Complete tracking of all operations (data modified, time, resources)
- **Storage Jobs**: Specific tracking of uploads/downloads
- **Table Snapshots**: Revert to previous table versions
- **Data Takeout**: Export all project data for compliance/migration
- **Trash tab**: Restore accidentally deleted configurations
- **Metadata**: Operational data on component creation, data flow, pipeline performance

### Cost Monitoring
- **Telemetry**: Job execution and user activity tracking
- **Credit tracking**: Per-job credit consumption
- **Cost attribution**: By department, team, use case, user
- **Pay-as-you-go**: Detailed billing for cloud resources

### Notifications
- Job failure/success notifications
- Integration with Slack, email, webhooks
- Event-driven monitoring

### Project Features
- **Development Branches**: Safe modification environment without affecting production
- **Global Search**: Find any configuration or data across project
- **Multi-project support**: Manage multiple stacks separately (account per stack)
- **Limits**: Monitor and control usage (measured billable metrics)

### Data Catalog (Sharing)
- **Shared Buckets**: Source buckets with sharing enabled
- **Linked Buckets**: References in destination projects
- **Datashare Owner**: Responsible party for shared data
- **Multi-project architecture**: Support for Data Mesh strategy
- **Live sharing**: Data automatically propagates to linked buckets

---

## Advanced Features

### Branches & Development
- **Development Branches**: Isolated environments for safe configuration changes
- **Version control**: Git-like branching for project configurations
- **Merge capabilities**: Merge branches back to main

### Data Quality & Monitoring
- **Operational metadata**: User activity, job status, data flow, schema evolution
- **Data lineage**: Automatic real-time tracking of data origin and usage
- **Search attributes**: Find jobs by various criteria
- **Event-driven actions**: Trigger actions based on data events

### AI Capabilities
- **AI-Generated Descriptions**: Automatic description generation for configurations
- **Error Explanation**: AI explanation of job failures
- **MCP Server**: Model Context Protocol integration for AI agents
- **AI Component Suggestions**: Intelligent component recommendations
- **AI Rules**: Define specific instructions for AI functionality

### Security & IP Management
- **IP Addresses**: Stack-specific dedicated IP ranges for firewall configuration
- **OAuth Support**: Secure third-party authentication (OAuth 2.0)
- **Token management**: Create limited-scope tokens for shared access
- **Encryption**: Data encryption in transit and at rest

---

## Transformation Patterns & Best Practices

### Code Patterns
- Pre-built code snippets for common transformations
- Available in documentation under "Code Patterns"

### Input/Output Mapping Patterns
- **Standard mapping**: Typical table mapping
- **Read-only input mapping**: Access all buckets without explicit input mapping
- **Output staging**: Various output options for different backends

### Variable Support
- **Shared variables**: Reusable across transformations
- **User variables**: For parametrization
- **System variables**: Automatic variables like execution date/time

---

## Development & Extension

### Keboola CLI ("Keboola as Code")
Command-line interface for:
- **Pull/Push**: Sync project to/from local directory
- **Local development**: Bulk editing configurations in IDE
- **Diff checking**: Compare local vs. remote state
- **Git integration**: Full version control support
- **CI/CD pipelines**: GitHub Actions integration
- **Multi-environment**: Manage configurations across environments

### CLI Command Categories
- **Sync**: init, pull, push, diff
- **Local**: create, validate, persist, encrypt, fix-paths, template management
- **Remote**: workspace, job, table, file, bucket operations
- **Status**: Check configuration status
- **Templates**: List, create, describe, test templates
- **dbt integration**: dbt-specific commands for local development

### CLI Structure
Project represented as local directory with:
- Configuration files (JSON)
- Transformations (SQL/Python/R files)
- Variables and shared code
- Schedules and orchestrations

### Component Development
Framework for creating custom components:
- **Common Interface**: Standardized data exchange via CSV files and designated directories
- **Component types**: Extractor, Writer, Application, Processor, Code Pattern, Transformation, Other
- **Docker-based**: Components run in isolated Docker containers
- **Language agnostic**: Python, R, PHP, Node.js, Go, Scala, etc.
- **Helper libraries**: Python, R, and PHP libraries available
- **Component generators**: Cookiecutter templates for quick setup
- **Publishing**: Publish components to marketplace via Developer Portal

### Workspace Isolation
- **Docker Runner**: Executes components in isolated environments
- **S3/ABS staging**: Options for file staging areas
- **Database workspaces**: Isolated database schemas for SQL transformations

---

## APIs & Integration

### Core APIs

#### Storage API
- Primary Keboola API
- Manages tables, files, buckets, configurations
- Job creation and monitoring
- Most fundamental API for platform integration

#### Management API
- Manage projects, users, organizations
- Features and notifications
- Account management

#### Specialized APIs
- **Transformations API**: Dedicated API for transformation operations
- **Orchestrator API** (legacy): v2 orchestrator operations
- **Queue API**: Job execution and management
- **Scheduler API**: Automation and scheduling
- **Workspaces API**: v2 workspace management
- **Stream API**: Ingest frequent events into storage
- **Templates API**: Apply project templates
- **Query API**: Run SQL on Snowflake/BigQuery
- **Developer Portal API**: Component management
- **Encryption API**: Data encryption services
- **Importer API**: Simplified table import

#### Support APIs
- **OAuth Broker**: OAuth integration
- **Notifications API**: Event subscriptions
- **Vault**: Credentials and variables storage
- **Editor API**: SQL editor session management
- **Billing API**: Pay-as-you-go billing
- **AI API**: AI features integration

### API Features
- Mostly REST-based with JSON payloads
- Token-based authentication (X-StorageApi-Token header)
- Multi-stack support with endpoint routing
- Asynchronous job operations
- Comprehensive error handling

### Model Context Protocol (MCP)
- Integration with AI agents
- Exposes Keboola features as callable tools
- Documentation queries using natural language
- Component discovery and exploration

---

## Templates

The documentation lists 20+ templates for specific use cases:
- **Ecommerce**: eCommerce KPI Dashboard, eCommerce platform setup
- **Marketing**: Marketing Platforms, Google Analytics 4, Mailchimp integration
- **CRM**: Customer Relationship Management
- **Analytics**: UA and GA4 Comparison, Social Media Engagement
- **Data Quality**: Data quality checks
- **AI/ML**: Generative AI, Kai SQL Bot, AI SMS Campaign
- **Finance**: Media Cashflow, Snowflake Security Checkup
- **Project Management**: Project management templates
- **Repository**: Template repository structure
- **DataHub**: Data hub setup
- **Surveys**: Survey data integration
- **Interactive Tools**: Keboola Sheets, Interactive dashboards

---

## Documentation Structure

### connection-docs (User-Facing Documentation)
Contains comprehensive guides for platform users:

**Main Sections:**
- `/overview/` - Platform overview and architecture
- `/components/extractors/` - Data source connectors (85+ with guides)
- `/components/writers/` - Data destination connectors (29+ with guides)
- `/components/applications/` - Application types and AI features
- `/components/data-apps/` - Streamlit-based app development
- `/components/branches/` - Development branches
- `/transformations/` - SQL, Python, R transformation guides
  - `/transformations/snowflake-plain/`
  - `/transformations/bigquery/`
  - `/transformations/python-plain/`
  - `/transformations/r-plain/`
  - `/transformations/dbt/`
  - `/transformations/oracle/`
  - `/transformations/workspace/`
  - `/transformations/mappings/`
  - `/transformations/variables/`
  - `/transformations/code-patterns/`
- `/storage/` - Data management
  - `/storage/tables/` - Table management
  - `/storage/buckets/` - Bucket organization
  - `/storage/files/` - File storage
  - `/storage/jobs/` - Job monitoring
  - `/storage/data-streams/` - Stream ingestion
  - `/storage/byobq/` - Bring-your-own BigQuery
  - `/storage/byodb/` - Bring-your-own database
- `/flows/` - Flow builder and automation
- `/orchestrator/` - Legacy orchestrator (deprecated)
- `/management/` - Project and user management
  - `/management/project/` - Project settings
  - `/management/organization/` - Organization management
  - `/management/jobs/` - Job monitoring
  - `/management/notifications/` - Alert configuration
  - `/management/account/` - Account settings
  - `/management/support/` - Support information
  - `/management/telemetry/` - Data collection
  - `/management/pay-as-you-go/` - Billing
- `/catalog/` - Data sharing and governance
- `/ai/` - AI features
  - `/ai/mcp-server/` - MCP integration
- `/tutorial/` - Getting started guides
  - `/tutorial/onboarding/` - Initial setup
  - `/tutorial/load/` - Data loading
  - `/tutorial/manipulate/` - Data transformation
  - `/tutorial/write/` - Data output
  - `/tutorial/automate/` - Automation
  - `/tutorial/branches/` - Branch usage
  - `/tutorial/ad-hoc/` - Ad-hoc operations
- `/templates/` - Project templates (20+ available)

### developers-docs (Developer Documentation)
Contains technical guides for extending and integrating:

**Main Sections:**
- `/overview/` - Architecture and APIs
  - `/overview/api/` - Complete API reference
- `/integrate/` - Integration guides
  - `/integrate/storage/` - Storage API usage
  - `/integrate/jobs/` - Job execution
  - `/integrate/orchestrator/` - Orchestrator API
  - `/integrate/variables/` - Variables and secrets
  - `/integrate/data-streams/` - Event streaming
  - `/integrate/database/` - Database integration
  - `/integrate/artifacts/` - Artifact management
  - `/integrate/mcp/` - MCP integration
- `/extend/` - Component development
  - `/extend/component/` - Component creation guide
  - `/extend/common-interface/` - Standard interface specification
    - Environment setup
    - Config file format
    - Manifest files
    - Input/output mapping
    - OAuth integration
    - Logging
    - Actions API
    - Staging options
  - `/extend/docker-runner/` - Docker execution environment
  - `/extend/generic-extractor/` - Generic API extractor
  - `/extend/generic-writer/` - Generic data writer
  - `/extend/publish/` - Component publishing guide
- `/cli/` - Command-line interface
  - `/cli/installation/` - Setup guide
  - `/cli/getting-started/` - Quick start
  - `/cli/structure/` - Project directory structure
  - `/cli/commands/` - Command reference
    - Sync (init, pull, push, diff)
    - Local (create, validate, persist)
    - Remote (workspace, job, table operations)
    - Template management
    - dbt commands
    - CI/CD workflows
  - `/cli/templates/` - Template system
  - `/cli/github-integration/` - GitHub Actions
  - `/cli/devops-use-cases/` - CI/CD examples
  - `/cli/dbt/` - dbt integration
- `/automate/` - Automation guide
  - Scheduling jobs
  - Running orchestrations
  - Job execution

---

## Recommended Skill Structure

Based on the comprehensive documentation, here's an optimal organization for a Keboola skill:

```
skill/
├── README.md
├── system-prompt.md
│   └── (core platform context and principles)
│
├── concepts/
│   ├── architecture.md (projects, stacks, jobs)
│   ├── components.md (extractor/writer/app overview)
│   ├── data-flow.md (storage, transformations, flows)
│   ├── governance.md (metadata, lineage, audit)
│   └── security.md (tokens, OAuth, encryption)
│
├── components/
│   ├── extractors/
│   │   ├── DATABASE.md (10 extractors)
│   │   ├── MARKETING_SALES.md (27+ platforms)
│   │   ├── COMMUNICATION.md (7 platforms)
│   │   ├── STORAGE.md (8 services)
│   │   ├── SOCIAL.md (4 platforms)
│   │   ├── OTHER.md (23+ specialized)
│   │   └── ERP.md (2 systems)
│   ├── writers/
│   │   ├── DATABASE.md (10 databases)
│   │   ├── BI_TOOLS.md (4 platforms)
│   │   ├── STORAGE.md (8 services)
│   │   └── OTHER.md (2 specialized)
│   ├── applications/
│   │   ├── AI_APPLICATIONS.md
│   │   ├── TRIGGERS.md
│   │   └── APPLICATIONS_VS_TRANSFORMATIONS.md
│   └── data-apps/
│       ├── STREAMLIT.md
│       └── DEPLOYMENT.md
│
├── transformations/
│   ├── BACKENDS.md (SQL: Snowflake, Redshift, BigQuery, Synapse, Oracle)
│   │                (Script: Python, R, Julia)
│   ├── MAPPINGS.md (input/output mapping)
│   ├── SQL_PATTERNS.md
│   ├── PYTHON_PATTERNS.md
│   ├── R_PATTERNS.md
│   ├── DBT_INTEGRATION.md
│   ├── WORKSPACES.md (development environment)
│   └── ADVANCED.md (versioning, shared code, variables)
│
├── storage/
│   ├── ARCHITECTURE.md (tables, buckets, files)
│   ├── TABLE_MANAGEMENT.md (aliases, primary keys, metadata)
│   ├── BUCKETS.md (in/out stages, backend selection)
│   ├── DATA_LINEAGE.md
│   └── SHARING.md (data catalog, linked buckets)
│
├── flows-orchestration/
│   ├── FLOWS.md (modern approach)
│   ├── FLOW_BUILDER.md (UI concepts)
│   ├── SCHEDULING.md (time-based, triggers)
│   ├── PARALLELIZATION.md
│   ├── MONITORING.md (run history, jobs)
│   └── ORCHESTRATOR_LEGACY.md
│
├── management/
│   ├── PROJECTS.md
│   ├── USERS_ACCESS.md (roles, tokens)
│   ├── ORGANIZATIONS.md
│   ├── MONITORING.md (jobs, storage jobs)
│   ├── BILLING.md (pay-as-you-go, cost tracking)
│   ├── NOTIFICATIONS.md
│   ├── DATA_GOVERNANCE.md (metadata, audit)
│   └── SUPPORT.md
│
├── development/
│   ├── CLI/
│   │   ├── INSTALLATION.md
│   │   ├── GETTING_STARTED.md
│   │   ├── PROJECT_STRUCTURE.md
│   │   ├── SYNC_COMMANDS.md (pull, push, diff)
│   │   ├── LOCAL_COMMANDS.md (create, validate)
│   │   ├── REMOTE_COMMANDS.md (storage operations)
│   │   └── CI_CD_INTEGRATION.md (GitHub Actions)
│   ├── component-development/
│   │   ├── OVERVIEW.md
│   │   ├── COMMON_INTERFACE.md
│   │   ├── DOCKER_RUNNER.md
│   │   ├── COMPONENT_TYPES.md
│   │   ├── CONFIGURATION.md
│   │   ├── TESTING.md
│   │   ├── PUBLISHING.md
│   │   └── HELPERS.md (Python, R, PHP libraries)
│   ├── generic-components/
│   │   ├── GENERIC_EXTRACTOR.md
│   │   └── GENERIC_WRITER.md
│   └── templates/
│       ├── TEMPLATE_SYSTEM.md
│       ├── TEMPLATE_STRUCTURE.md
│       └── TEMPLATE_TESTING.md
│
├── apis/
│   ├── STORAGE_API.md (primary API)
│   ├── MANAGEMENT_API.md
│   ├── SPECIALIZED_APIS.md (transformations, queue, scheduler)
│   ├── SUPPORT_APIS.md (OAuth, notifications, vault)
│   ├── AUTHENTICATION.md (tokens, endpoints)
│   ├── MULTI_STACK.md (regions, endpoints)
│   └── MCP_INTEGRATION.md (AI agents)
│
├── patterns/
│   ├── COMMON_WORKFLOWS.md
│   ├── DATA_PIPELINE_DESIGN.md
│   ├── ERROR_HANDLING.md
│   ├── PERFORMANCE_OPTIMIZATION.md
│   ├── COST_OPTIMIZATION.md
│   └── MULTI_PROJECT_ARCHITECTURE.md
│
├── examples/
│   ├── SIMPLE_ETL.md
│   ├── DATA_QUALITY_CHECK.md
│   ├── MARKETING_ANALYTICS.md
│   ├── FINANCIAL_REPORTING.md
│   ├── CUSTOM_COMPONENT.md
│   └── MULTI_ENVIRONMENT_CI_CD.md
│
└── reference/
    ├── COMPONENT_CATALOG.md (all 85 extractors, 29 writers)
    ├── TEMPLATE_CATALOG.md (20+ templates)
    ├── TERMINOLOGY.md
    ├── QUICK_LINKS.md
    └── TROUBLESHOOTING.md
```

---

## Content Priorities

### Tier 1: Critical (Used Daily)
1. **Projects & Stacks** - Basic working knowledge
2. **Storage** - Where all data lives
3. **Components** - Core to all operations
   - Popular extractors (Google Ads, Salesforce, BigQuery, S3, etc.)
   - Popular writers (Snowflake, Redshift, Tableau, etc.)
4. **Transformations** - Core data manipulation
   - SQL (most common for aggregations/joins)
   - Python (common for processing)
   - Mappings (essential safety feature)
5. **Flows** - Automation backbone
6. **Jobs** - Monitor execution and troubleshoot
7. **Storage Jobs** - Track data movement

### Tier 2: Important (Used Weekly)
1. **Workspaces** - Development/testing environment
2. **Applications** - Advanced data enrichment
3. **Branching** - Safe configuration changes
4. **Data Catalog** - Multi-project data sharing
5. **Notifications** - Monitor pipeline health
6. **CLI** - Local development and GitOps
7. **Key extractors** for specific industries
8. **Key writers** for common destinations
9. **dbt Integration** - If using dbt
10. **Variables** - Parametrization for transformations

### Tier 3: Useful (Used Occasionally)
1. **Data Apps** - Custom interactive apps
2. **Triggers** - Event-driven automation
3. **Read-only input mapping** - Advanced safety
4. **Table Snapshots** - Recovery operations
5. **Component Development** - Custom solutions
6. **Generic Extractor/Writer** - For unsupported systems
7. **Multi-stack management** - Multi-region deployments
8. **Payment/Billing** - Cost management
9. **OAuth Integration** - Secure third-party auth
10. **Template system** - Project templates and CI/CD
11. **Specialized applications** - Sentiment analysis, geocoding, etc.
12. **MCP Integration** - AI agent integration

### Tier 4: Reference (Used During Setup)
1. **IP Addresses** - Firewall configuration
2. **Encryption** - Data protection setup
3. **Support channels** - When assistance needed
4. **Metadata format** - For advanced customization
5. **Component publishing** - Marketplace submission
6. **Docker Runner** - Container execution details
7. **Less common components** - Specialized platforms

---

## Key Learning Paths

### For Data Engineers
1. Storage architecture → Flows/Orchestration → Monitoring
2. Popular extractors → Transformations → Popular writers
3. CLI for version control → Multi-project architecture

### For Analytics/Business Users
1. Projects & basic navigation
2. Pre-built extractors for their data sources
3. Simple transformations (SQL)
4. Tableau/BI tool integration

### For DevOps/Platform Teams
1. CLI & project structure
2. Multi-environment management
3. CI/CD integration (GitHub Actions)
4. Custom component development
5. API integration

### For Developers Extending Platform
1. Component common interface
2. Docker Runner
3. Component development framework
4. Publishing to marketplace
5. Testing and deployment

---

## Critical Context to Include

### Design Principles
- **Data safety first**: All transformations work on isolated copies
- **Modularity**: Components are independent, reusable units
- **Auditability**: Every action is tracked with metadata
- **Scalability**: Automatic resource scaling for pipelines
- **Flexibility**: Support for multiple languages and backends

### Platform Assumptions
- Batch processing (not real-time)
- Asynchronous job execution
- Multi-project organization (with shared data catalog)
- API-first architecture (everything programmable)
- Cloud-native (multi-tenant or single-tenant deployment)

### Common Workflows
1. Extract → Transform → Load
2. Data enrichment (add external data via APIs)
3. Data quality checks (validations)
4. Multi-source aggregation
5. Custom business logic application

---

## Statistics Summary

- **85+ Data Source Connectors** across 8 categories
- **29+ Data Destination Connectors** across 4 categories
- **5 SQL Backends** (Snowflake, Redshift, BigQuery, Synapse, Oracle)
- **3 Scripting Backends** (Python, R, Julia)
- **20+ Project Templates** for common use cases
- **5 Stacks** available globally (multi-tenant)
- **Multiple Cloud Providers** (AWS, Azure, GCP)
- **2 Main Documentation Sites** (user-facing + developer)
- **~2,800 total lines** of documentation

