# Keboola Skill - Complete Knowledge Base

## Overview
Comprehensive Keboola data engineering skill combining official documentation, practical runbooks, real-world examples, and AI-assisted workflows.

## Knowledge Sources

### 1. Official Documentation (docs-repos/)
- **connection-docs**: 252 markdown files of user-facing documentation
- **developers-docs**: Complete developer documentation
- **Source**: Cloned from GitHub for reference

### 2. Knowledge Map (KNOWLEDGE_MAP.md - 896 lines)
- **85+ Extractors** across 8 categories
- **29+ Writers** across 4 categories
- **Complete platform architecture**
- **4-tier content prioritization**
- **Learning paths** for different roles

### 3. Data Enablement Guide (skill/Keboola_Data_Enablement_Guide.md)
- **Keboola Dictionary** - Anchored definitions for all concepts
- **AI Assistant Operating Kit** - Workflows for AI-assisted data engineering
- **Annotated book extracts** from 7 key data engineering books:
  - Introduction to Statistical Learning
  - Storytelling with Data
  - Data Smart
  - Python for Data Analysis
  - Data Pipelines Pocket Reference
  - Data Quality Fundamentals
  - Data Engineering Best Practices

### 4. Operational Runbooks (skill/runbooks/)
- **Common Issues**: Authentication, freshness SLA, schema drift, duplicates, cost spikes, orchestration failures
- **Incident Response**:
  - Pipeline failure runbook
  - Data quality breach runbook
- **Debugging Cheatsheet**: Systematic debugging approach

### 5. Flow Examples (skill/flows/examples/)
- **CDC Orders**: Near-real-time CDC flow with data contracts
- **Model Scoring**: ML model scoring pipeline
- **Sales KPIs**: Business metrics calculation flow

### 6. Templates (skill/templates/)
- **Design Brief**: Project planning template
- **ELT Unit**: Data pipeline specification
- **Data App**: Data application template
- **Validation**: Data quality validation template
- **AI Prompts**: System, Discovery, Modeling, ELT Unit prompts
- **Data App Scaffolds**:
  - Streamlit + Snowflake template (Python)
  - Streamlit + BigQuery template (Python)

### 7. Generated Guides
- **Storage Guide**: Tables, buckets, incremental loading, workspaces
- **Flows & Orchestration**: Flow builder, scheduling, triggers, parallelization
- **Jobs Guide**: Monitoring, troubleshooting, debugging
- **Component Catalog**: Complete reference for all 114+ components
- **Transformations Guide**: SQL, Python, R, dbt (from Haiku agent)
- **Data Engineering Patterns**: Incremental loading, CDC, SCD, star schema
- **Practical Examples**: 6 end-to-end configurations with explanations

## Skill Structure

```
skill/
├── Keboola_Data_Enablement_Guide.md    # 13KB - Full library + AI kit
├── README.md                            # Skill overview
├── system-prompt.md                     # Core Keboola expertise
│
├── concepts/                            # Fundamental concepts
├── storage/                             # Storage guide
│   └── storage.md
│
├── components/                          # Extractors & writers
│   ├── extractors/
│   └── writers/
│
├── transformations/                     # SQL, Python, R, dbt
│
├── flows/                               # Real-world flow examples
│   └── examples/
│       ├── flow_cdc_orders.md
│       ├── flow_model_scoring.md
│       └── flow_sales_kpi.md
│
├── flows-orchestration/                 # Orchestration guides
│
├── runbooks/                            # Operational knowledge
│   ├── common_issues.md
│   ├── checklists/
│   │   └── debugging_cheatsheet.md
│   └── incidents/
│       ├── pipeline_failure.md
│       └── data_quality_breach.md
│
├── templates/                           # Reusable templates
│   ├── Design_Brief.md
│   ├── ELT_Unit.md
│   ├── Data_App.md
│   ├── Validation.md
│   ├── System_Prompt.txt
│   ├── Discovery_Prompt.txt
│   ├── Modeling_Prompt.txt
│   ├── ELT_Unit_Prompt.txt
│   └── data_app_scaffolds/
│       ├── streamlit_snowflake.py
│       └── streamlit_bigquery.py
│
├── patterns/                            # Data engineering patterns
├── examples/                            # Working configurations
├── knowledge/                           # Additional knowledge
│   └── storage.md
└── troubleshooting/                     # Issue resolution

```

## Key Features

### Comprehensive Coverage
- **Platform Architecture**: Complete understanding of Keboola components
- **All Extractors & Writers**: 85+ extractors, 29+ writers fully documented
- **Real-World Examples**: Production-ready flow configurations
- **Operational Knowledge**: Runbooks for common issues and incidents

### Practical Focus
- **Templates**: Copy-paste design briefs, ELT units, validation specs
- **Runbooks**: Step-by-step incident response procedures
- **Debugging**: Systematic checklists and troubleshooting guides
- **Code Scaffolds**: Working Streamlit templates for data apps

### AI-Assisted Workflows
- **Operating Loop**: Iterative development with AI assistance
- **Quality Guardrails**: Standards for maintainable data products
- **Prompt Templates**: Structured prompts for discovery, modeling, ELT
- **Checkpoints**: Assistant validation at key milestones

### Best Practices
- **Data Contracts**: Producer-consumer agreements with SLOs
- **SLIs/SLOs**: Service level indicators and objectives
- **Validation**: Automated checks with block vs. warn policies
- **Bronze/Silver/Gold**: Layered storage convention

## Content Statistics

- **Total Files**: 23 (17 markdown + 6 code/text)
- **Total Size**: 131KB of curated knowledge
- **Knowledge Map**: 896 lines covering entire platform
- **Enablement Guide**: 13KB of operational wisdom
- **Flow Examples**: 3 production-ready patterns
- **Runbooks**: 4 operational guides
- **Templates**: 10+ reusable templates

## Usage

This skill enables Claude to:

1. **Design Data Pipelines**: Using templates and best practices
2. **Write Configurations**: For extractors, transformations, writers
3. **Troubleshoot Issues**: Using runbooks and debugging checklists
4. **Build Data Apps**: Using Streamlit scaffolds and templates
5. **Implement Patterns**: Incremental loading, CDC, SCD, star schema
6. **Ensure Quality**: Data contracts, validation, SLIs/SLOs
7. **Respond to Incidents**: Following structured runbooks

## Next Steps

- Skill is complete and ready for use
- All content committed and pushed to repository
- Can be deployed as Claude Code skill
- MCP server integration ready (configurations in YOUR_CONFIG.json)

