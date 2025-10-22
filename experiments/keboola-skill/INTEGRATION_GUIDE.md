# Keboola Skill - Knowledge Integration Guide

## Overview

This document explains how the Keboola skill incorporates multiple knowledge sources to provide comprehensive support for data engineering tasks.

## Knowledge Sources Integrated

We have successfully integrated content from **two ZIP archives**:

1. **keboola_kb_starter.zip** - Base knowledge package
   - Keboola_Data_Enablement_Guide.md (13KB)
   - Core templates (Design Brief, ELT Unit, Validation, Data App)
   - AI-assisted workflow prompts

2. **keboola_kb_plus_apps_flows_runbooks.zip** - Extended knowledge package
   - All content from starter package PLUS:
   - Operational runbooks (common_issues.md, incident response, debugging checklists)
   - Production flow examples (CDC orders, model scoring, sales KPIs)
   - Data app scaffolds (Streamlit + Snowflake/BigQuery templates)

Both packages have been fully integrated into the `skill/` directory.

## How Knowledge Components Are Incorporated

### 1. Prompts (AI-Assisted Workflows)

**Location**: `skill/templates/*.txt`

The skill includes four specialized AI prompt templates that guide Claude through different phases of data engineering work:

#### System_Prompt.txt
- **Purpose**: Establishes Claude as a Keboola data engineering expert
- **Usage**: Sets the context for all Keboola-related conversations
- **Key Features**:
  - Deep knowledge of Keboola components, APIs, and workflows
  - Ability to reference the anchored dictionary for consistent terminology
  - Focus on data contracts, SLIs/SLOs, and operational excellence

#### Discovery_Prompt.txt
- **Purpose**: Guides discovery phase of new data projects
- **Usage**: When starting a new project or analyzing data sources
- **Key Questions**:
  - What data sources exist?
  - What are the business outcomes?
  - Who are the consumers and what decisions will they make?
  - What are the data quality requirements?

#### Modeling_Prompt.txt
- **Purpose**: Assists in designing data models
- **Usage**: When creating dimensional models, facts, or aggregates
- **Key Guidance**:
  - Star schema patterns
  - Slowly changing dimensions (SCD Type 1, 2, 3)
  - Grain definition
  - Conformity across subject areas

#### ELT_Unit_Prompt.txt
- **Purpose**: Designs individual ELT pipeline units
- **Usage**: When creating specific data transformation steps
- **Key Elements**:
  - Input/output contracts
  - Transformation logic
  - Data quality tests
  - Incremental loading strategy

**How Claude Uses These**:
- Claude can reference these prompts when users ask for help with specific phases
- Users can copy/paste these prompts to guide Claude's responses
- The prompts ensure consistent, best-practice approaches across projects

### 2. Books (Expert Knowledge Extracts)

**Location**: `skill/Keboola_Data_Enablement_Guide.md` (Section: "Annotated Extracts from Data Engineering Books")

The skill incorporates curated extracts from **7 authoritative data engineering books**:

1. **An Introduction to Statistical Learning (ISL)** - Gareth James et al.
   - Model validation, overfitting, bias-variance tradeoff
   - Cross-validation techniques
   - Statistical foundations for ML pipelines

2. **Storytelling with Data** - Cole Nussbaumer Knaflic
   - Data visualization best practices
   - Choosing the right chart types
   - Designing for decision-making audiences

3. **Data Smart** - John W. Foreman
   - Practical data science with spreadsheets
   - Clustering, classification, optimization
   - Business-focused analytics patterns

4. **Python for Data Analysis** - Wes McKinney
   - pandas best practices
   - Data wrangling techniques
   - Performance optimization for large datasets

5. **Data Pipelines Pocket Reference** - James Densmore
   - Pipeline architecture patterns
   - Idempotency and reproducibility
   - Monitoring and alerting strategies

6. **Data Quality Fundamentals** - Barr Moses et al.
   - Data observability principles
   - Freshness, volume, schema, distribution metrics
   - Incident response for data quality issues

7. **Data Engineering Best Practices** - Joe Reis & Matt Housley
   - Modern data stack patterns
   - DataOps and data lifecycle management
   - Team collaboration and governance

**How Claude Uses These**:
- When users ask about best practices, Claude can reference specific book concepts
- Provides authoritative backing for recommendations
- Connects theoretical knowledge to practical Keboola implementations
- Example: When discussing data quality, Claude can cite the "5 pillars of data observability" from Data Quality Fundamentals

### 3. Dictionary (Anchored Terminology)

**Location**: `skill/Keboola_Data_Enablement_Guide.md` (Section: "Keboola Dictionary (Anchored)")

The dictionary provides **stable, hyperlinked definitions** for all core Keboola concepts:

#### Key Terms Defined:

- **Flow / Orchestration** (`#k:flow`)
  - Scheduled, dependency-aware sequence of components
  - Related to: Validation, SLIs/SLOs

- **Component** (`#k:component`)
  - Reusable building block (extractor, writer, transformation)
  - Versioned, configurable via JSON

- **Transformation** (`#k:transformation`)
  - SQL, Python, R, or dbt code that processes data
  - Runs in sandboxed environment

- **Buckets** (`#k:buckets`)
  - Storage containers for tables
  - in.c- (input/clean), out.c- (output/curated)

- **Data Contract** (`#k:contract`)
  - Producer-consumer agreement
  - Includes schema, types, PII policy, freshness SLO

- **Validation / Monitors** (`#k:validation`)
  - Tests for duplicate keys, nulls, freshness, distribution
  - Fails fast before propagating bad data

- **SLIs / SLOs** (`#k:slislos`)
  - Service Level Indicators (actual metrics)
  - Service Level Objectives (target thresholds)
  - Examples: freshness_minutes < 15, duplicate_rate = 0%

- **Runbook** (`#k:runbook`)
  - Step-by-step playbook for incidents
  - Links symptoms → debug → fix → prevention

**How Claude Uses the Dictionary**:
- **Consistent Terminology**: Claude uses exact definitions from the dictionary
- **Cross-References**: When explaining a concept, Claude can link to related terms
- **Context Awareness**: Dictionary entries include "Use with" and "Related" sections
- **User Education**: Users can be directed to specific anchor links (e.g., "See `#k:contract`")

**Example Usage**:
```
User: "What's the difference between a Flow and a Component?"
Claude: "A Flow (#k:flow) is a scheduled orchestration that chains together
multiple Components (#k:component). Components are the individual building
blocks (extractors, writers, transformations), while Flows define the
execution order, dependencies, and schedule."
```

## Integration Architecture

### Skill Directory Structure

```
skill/
├── Keboola_Data_Enablement_Guide.md  ← Core knowledge: dictionary + book extracts
├── templates/
│   ├── System_Prompt.txt              ← AI context setting
│   ├── Discovery_Prompt.txt           ← Project discovery guidance
│   ├── Modeling_Prompt.txt            ← Data modeling guidance
│   ├── ELT_Unit_Prompt.txt           ← Pipeline design guidance
│   ├── Design_Brief.md               ← Project planning template
│   ├── ELT_Unit.md                   ← Pipeline specification template
│   ├── Validation.md                 ← Data quality template
│   ├── Data_App.md                   ← Data app design template
│   └── data_app_scaffolds/           ← Working code templates
│       ├── streamlit_snowflake.py
│       └── streamlit_bigquery.py
├── runbooks/
│   ├── common_issues.md              ← Operational troubleshooting
│   ├── incidents/                    ← Incident response playbooks
│   └── checklists/                   ← Debugging workflows
├── flows/examples/                    ← Production-ready flow configs
│   ├── flow_cdc_orders.md
│   ├── flow_model_scoring.md
│   └── flow_sales_kpi.md
├── patterns/
│   └── data-engineering-patterns-guide.md  ← AI-generated patterns
├── examples/
│   └── keboola-practical-examples.md       ← AI-generated examples
└── knowledge/                         ← Component-specific guides
    └── storage.md
```

### How Claude Code Uses This Skill

1. **Context Loading**: The skill.json file tells Claude Code to load all markdown files as context
2. **Semantic Search**: When users ask questions, Claude searches across all integrated knowledge
3. **Prompt Injection**: System_Prompt.txt can be used to set Claude's persona and capabilities
4. **Template Expansion**: Users can ask Claude to "create a Design Brief" and Claude will use the template
5. **Runbook Execution**: When incidents occur, Claude can walk through relevant runbooks step-by-step
6. **Pattern Recognition**: Claude recognizes common data engineering patterns and suggests appropriate solutions

## Usage Examples

### Example 1: Using the Dictionary
```
User: "How do I set up data contracts for my pipeline?"
Claude: [References #k:contract in the dictionary]
"A Data Contract defines the agreement between data producers and consumers.
Key elements include:
- Schema: column names, types, constraints
- PII Policy: which fields contain sensitive data
- Freshness SLO: max acceptable lag (e.g., freshness_minutes < 15)
- Tests: validations to ensure contract compliance

See the ELT_Unit template for how to document contracts in your pipeline spec."
```

### Example 2: Using Book Knowledge
```
User: "What tests should I add to my pipeline?"
Claude: [References Data Quality Fundamentals book]
"Based on the 5 pillars of data observability:
1. Freshness: freshness_minutes < threshold
2. Volume: row_count within expected range
3. Schema: no unexpected columns or type changes
4. Distribution: check for anomalies in value distributions
5. Lineage: verify upstream dependencies

See runbooks/common_issues.md for how to debug test failures."
```

### Example 3: Using Prompts
```
User: "Help me design a new analytics pipeline"
Claude: [Uses Discovery_Prompt.txt guidance]
"Let's start with discovery. I'll need to understand:
1. Business Outcome: What decisions will this data enable?
2. Data Sources: Which systems contain the raw data?
3. Consumers: Who will use this data and how often?
4. Quality Requirements: What's your tolerance for late/incomplete data?
5. Security: Any PII or compliance requirements?

Once we have these answers, I'll help you create a Design Brief."
```

### Example 4: Using Runbooks
```
User: "My pipeline freshness SLO is breached!"
Claude: [References runbooks/common_issues.md - Freshness SLA Breach]
"Let's debug systematically:
1. Check upstream source lags: Are source systems delayed?
2. Check orchestration queue: Is there a backlog of jobs?
3. Check long-running steps: Any transformations taking unusually long?

Fix options:
- Increase parallelism in Flow orchestration
- Optimize slow transformations (use EXPLAIN on SQL)
- Backfill missing time windows

Prevention: Set up early warning alerts when lag > 50% of SLO."
```

## Benefits of This Integration

1. **Comprehensive Coverage**: Combines official docs, expert knowledge, operational runbooks, and AI guidance
2. **Consistent Terminology**: Anchored dictionary ensures all concepts are defined uniformly
3. **Actionable Patterns**: Real production examples and templates that can be directly used
4. **Incident Response**: Step-by-step runbooks for common operational issues
5. **Best Practices**: Book extracts provide authoritative backing for recommendations
6. **AI-Assisted Workflows**: Prompts guide Claude through structured phases of data work

## Maintenance and Updates

To keep the skill current:

1. **Dictionary**: Update `Keboola_Data_Enablement_Guide.md` when new Keboola features are released
2. **Prompts**: Refine prompt templates based on user feedback and evolving best practices
3. **Runbooks**: Add new incident scenarios as they're encountered in production
4. **Examples**: Expand flow examples to cover more use cases (streaming, ML, reverse ETL)
5. **Books**: Add new extracts as relevant data engineering books are published

## Summary

The Keboola skill successfully integrates:
- **2 ZIP archives** with complete content extraction
- **4 AI prompt templates** for structured workflows
- **7 data engineering books** with curated extracts
- **1 anchored dictionary** with 20+ core terms and cross-references
- **Production runbooks** for operational excellence
- **Real flow examples** for quick-start templates

All knowledge is organized for efficient retrieval by Claude Code, enabling expert-level support for Keboola data engineering tasks.
