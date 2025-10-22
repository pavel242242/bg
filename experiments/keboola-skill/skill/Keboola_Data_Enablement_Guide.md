# Keboola Data Enablement Library & AI Assistant Kit (Full Guide)

*Audience:* Business-facing **data analysts** & **data engineers** working in **Keboola** to drive outcomes, add context, and proactively support growth.  
*Purpose:* Unify foundational books, Keboola concepts, and AI-assistant workflows to iteratively build **maintainable, explainable, trustworthy** data products.

---

## Table of Contents
- [Legend](#legend)
- [Keboola Dictionary (Anchored)](#keboola-dictionary-anchored)
- [AI Assistant Operating Kit](#ai-assistant-operating-kit)
  - [Operating Loop](#operating-loop)
  - [Quality Bar & Guardrails](#quality-bar--guardrails)
  - [Prompt Templates](#prompt-templates)
  - [Reusable Templates (Docs & Artifacts)](#reusable-templates-docs--artifacts)
  - [Assistant Checkpoints](#assistant-checkpoints)
- [Books (Annotated Extracts)](#books-annotated-extracts)
  - [ISL — An Introduction to Statistical Learning](#isl--an-introduction-to-statistical-learning)
  - [Storytelling with Data](#storytelling-with-data)
  - [Data Smart](#data-smart)
  - [Python for Data Analysis (3rd ed.)](#python-for-data-analysis-3rd-ed)
  - [Data Pipelines Pocket Reference](#data-pipelines-pocket-reference)
  - [Data Quality Fundamentals](#data-quality-fundamentals)
  - [Data Engineering Best Practices](#data-engineering-best-practices)
- [Merge Guidance (Maintainers)](#merge-guidance-maintainers)

---

## LEGEND
- ✅ Default — relevant for analysts/engineers  
- ❌ **Irrelevant** — too theoretical for day-to-day use  
- ⚙️ **Technology-Specific** — tool or language specific (Python, Excel, etc.)  
- 💡 **Keboola Note** — maps chapter to Keboola concepts (Flows, Components, Transformations, Data Apps, Contracts, SLIs/SLOs)

---

## Keboola Dictionary (Anchored)

> Use these stable anchors to link from chapters, runbooks, and app docs.

<a id="k:flow"></a>
### Flow / Orchestration
**Definition:** A scheduled, dependency-aware sequence of **Components** and **Transformations** (Extract → Load → Transform → Validate → Publish).  
**Use with:** Pipelines, reliability patterns, and alerts.  
**Related:** [Validation/Monitors](#k:validation), [SLIs/SLOs](#k:slislos), [Templates](#k:templates)

<a id="k:component"></a>
### Component (Extractor / Writer)
**Definition:** Packaged connector to a source/destination, configured by JSON **Configuration**.  
**Related:** [Flow](#k:flow), ingestion patterns.

<a id="k:transformation"></a>
### Transformation (SQL / Python)
**Definition:** A compute step producing tables/files; versioned, idempotent, and testable.  
**Related:** [Buckets](#k:buckets), [Validation](#k:validation)

<a id="k:buckets"></a>
### Buckets (Bronze / Silver / Gold)
**Definition:** Storage convention: **Bronze** (raw/staging), **Silver** (clean/standardized), **Gold** (modeled/serving).  
**Related:** [Data Contract](#k:data-contract), [Lineage](#k:catalog)

<a id="k:streams"></a>
### Data Streams / CDC
**Definition:** Low-latency change capture from operational systems into storage/warehouse.  
**Related:** [Flow](#k:flow), [Validation](#k:validation)

<a id="k:data-contract"></a>
### Data Contract
**Definition:** Producer–consumer agreement on **schema, types, enums, freshness, ownership** & SLOs.  
**Related:** [Validation](#k:validation), [SLIs/SLOs](#k:slislos)

<a id="k:validation"></a>
### Validation / Monitors
**Definition:** Automated checks (freshness, volume, schema, distribution) with **block vs. warn** policies.  
**Related:** [SLIs/SLOs](#k:slislos), [Flow](#k:flow)

<a id="k:slislos"></a>
### SLIs / SLOs
**Definition:** **Indicators** (e.g., freshness minutes, success rate, row deltas) and **Objectives** (targets) for pipelines & datasets.  
**Related:** [Validation](#k:validation), [Data Contract](#k:data-contract)

<a id="k:catalog"></a>
### Catalog & Lineage
**Definition:** Metadata (owners, purpose, tags) + visual upstream/downstream impact map.  
**Related:** [Buckets](#k:buckets), [Templates](#k:templates)

<a id="k:data-app"></a>
### Data App
**Definition:** Governed, business-facing UI (often Streamlit) for contextual insight & actions with narrative.  
**Related:** Storytelling, consistency of scales and definitions.

<a id="k:workspace"></a>
### Workspace
**Definition:** Safe environment for notebooks and development (Transformations, model training, app scaffolds).

<a id="k:metrics"></a>
### Metrics & Dimensions (Semantic-lite)
**Definition:** Standard KPI formulas & conformed attributes; consumed by apps and BI.  
**Related:** [Data Contract](#k:data-contract), [Catalog](#k:catalog)

<a id="k:runbook"></a>
### Runbook / Postmortem
**Definition:** Incident response steps; blameless learning document; links from Flows and alerts.

<a id="k:templates"></a>
### Templates / Blueprints
**Definition:** Reusable Flow/Transformation/Data App skeletons, with contracts, tests, docs, and owners.

---

## AI Assistant Operating Kit

### Operating Loop
1. **Discovery** → capture KPI(s), decision cadence, sources (owner, access, freshness), constraints (PII, budget), consumers & delivery (Data App/BI/export), SLAs.  
2. **Plan** → 1-page **Design Brief** (why/what/how/risks), thin-slice MVP (one KPI, one path), define **Data Contract** & acceptance tests.  
3. **Build** → small, idempotent **ELT units**: raw→staged→gold; add **Validation** tasks and logging; prepare **Data App** with narrative.  
4. **Review** → show diff tables & visuals; update contract/SLIs; record **post-demo notes**.  
5. **Iterate** → next highest-value slice.

### Quality Bar & Guardrails
- **Every Flow:** validation, retry policy, owner tag, rollback notes, and alert routes.  
- **Every Model:** training snapshot, metrics (AUC/PR for classifiers), threshold policy, explainability note.  
- **Every Data App:** KPI header, freshness indicator, short narrative, and 1–2 action buttons.

### Prompt Templates

**System Prompt (paste once per session)**
```
You are a senior data engineer/analyst working in Keboola. Produce small, composable ELT steps with tests, contracts, and docs. Prefer ELT (raw→staged→gold). Add validation tasks (freshness, volume, schema, distribution), define SLIs/SLOs, and deliver an explainable Data App. Use interpretable models first (linear/logistic/trees). Never handle PII without an explicit field policy. Map outputs to Keboola terms (Flows, Components, Transformations, Data Contracts, SLIs/SLOs, Data Apps).
```

**Discovery Prompt**
```
Project: {title}
Business outcome & KPI(s): {kpi}
Consumers & delivery mode: {Data App | BI | export}
Data sources (owner, access, freshness): {list}
Constraints (PII, budget, latency): {list}
Ask: 
1) Create a one-page design brief (why/what/how/risks).
2) Propose raw→staged→gold tables + a Data Contract.
3) List validation checks + SLIs/SLOs and alert policy.
4) Outline the Data App story (setup→insight→action).
```

**ELT Unit Prompt**
```
Create a STAGED table {schema}.{table} from RAW {raw.schema}.{source} with:
- explicit schema & types
- dedupe, null-policy, timezone normalization
- idempotent logic and partitioning where relevant
Provide: (a) SQL/Python code, (b) validation SQL (row count delta, duplicate keys, freshness), and (c) a docstring.
```

**Modeling Prompt (Explainable First)**
```
Train a logistic regression for {target} using features {list}. 
- Split and cross-validate; report AUC, PR, calibration.
- Emit inference SQL/Python to score into GOLD {schema}.{table}.
- Provide a threshold policy (optimize F1 or cost-weighted).
- Log params/metrics table schemas and a short caveat note.
```

**Data App Prompt**
```
Draft a Streamlit app with:
- KPI header + freshness indicator
- One key insight visual (trend/segment) with clear labeling
- Two action buttons (e.g., download segment, open runbook link)
- A concise narrative (3 paragraphs) applying Storytelling principles
```

### Reusable Templates (Docs & Artifacts)

**Design Brief.md (one page)**
```
# {Project Name}
**Outcome & KPI(s):** {goal, target}
**Consumers & Decisions:** {who, cadence}
**Scope (MVP):** {thin slice}
**Data Contract:** {inputs schema/types/PII policy, freshness SLO}
**Plan (ELT):** raw→staged→gold steps, owners, schedule
**Validation & SLIs:** checks, thresholds, alert routes
**Risks & Mitigations:** privacy, quality, latency
```

**Validation.md**
```
## Dataset: {name}
- Freshness (SLO: ≤ {min} mins)
- Volume delta (−{x}% … +{y}%)
- Schema check (types/enums)
- Distribution check (KS/quantiles)
Policy: {block | warn + ticket}
```

**Data App.md**
```
## App: {name}
KPI & Freshness: {field} / {minutes}
Views: {Insight 1, 2}
Narrative: {setup → insight → action}
Actions: {download segment, open runbook}
```

### Assistant Checkpoints
- **Before build:** KPI(s), contract, and acceptance tests exist.  
- **During:** tasks are small & idempotent; tests written; owner & alerts configured.  
- **Before ship:** docs + lineage updated; Data App narrative present; next iteration scoped.

---

## Books (Annotated Extracts)

> Chapters are marked for day-to-day relevance, tech specificity, and include Keboola mapping notes.

### ISL — An Introduction to Statistical Learning
**Chapters**
1 Intro ✅ · 2 Statistical Learning ✅ · 3 Linear Regression ✅ · 4 Classification ✅ · 5 Resampling ✅ · 6 Regularization ✅ · 7 Beyond Linearity ✅ · 8 Trees ✅ · 9 SVM ⚙️ ✅ · 10 Deep Learning ❌ · 11 Survival ❌ · 12 Unsupervised ✅ · 13 Multiple Testing ✅

**Keboola Notes**
- Ch.3–6 💡 **Transformations** (Python) for modeling; log metrics in **Tables**; publish **Gold** results to **Data Apps**.  
- Ch.5 💡 Cross-validation scheduled via **Flows**; persist fold metrics.  
- Ch.8 💡 Trees/ensembles for explainable performance; keep threshold policy & feature importance.  
- Ch.12 💡 Segmentation → **Dimensions**; expose segments in apps.  
- Ch.13 💡 FDR controls embedded in batched testing transformations.

---

### Storytelling with Data
**Chapters**
1 Context ✅ · 2 Choose Visuals ✅ · 3 Remove Clutter ✅ · 4 Focus Attention ✅ · 5 Think Like a Designer ✅ · 6 Dissecting Visuals ✅ · 7 Storytelling ✅ · 8 Putting It Together ✅ · 9 Case Studies ✅ · 10 Final ✅

**Keboola Notes**
- 💡 Use to design **Data Apps**: narrative blocks, consistent scales, preattentive cues.  
- 💡 Maintain a **visual QA checklist** before releases.

---

### Data Smart
**Chapters**
1 Spreadsheet Primer ⚙️ ❌ · 2 K-Means ✅ · 3 Naïve Bayes ✅ · 4 Forecasting ✅ · 5 Graphs ✅ · 6 Regression ✅ · 7 Optimization ✅ · 8 Simulation ✅ · 9 Outliers ✅ · 10 R Intro ⚙️ ❌

**Keboola Notes**
- 💡 Move spreadsheet logic into **Python Transformations**.  
- 💡 Forecast/optimize → gold outputs; Monte Carlo simulations for risk bands.  
- 💡 Outlier detection as **Validation** (warn vs. block).

---

### Python for Data Analysis (3rd ed)
**Chapters**
1–3 Python/IPython ⚙️ · 4 NumPy ⚙️ · 5 pandas ⚙️ · 6 Loading ✅ · 7 Cleaning ✅ · 8 Wrangling ✅ · 9 Plotting ⚙️ · 10 Groupby ✅ · 11 Time Series ✅ · 12 Modeling ⚙️ · 13 Case Studies ✅

**Keboola Notes**
- 💡 Ch.6–7 for resilient ingestion & cleaning; enforce types & naming standards.  
- 💡 Ch.10 for **metrics tables** powering apps/BI; Ch.11 for freshness/timezones policies.  
- 💡 Ch.13 as project templates.

---

### Data Pipelines Pocket Reference
**Chapters**
1 Intro ✅ · 2 Infra ✅ · 3 Patterns ✅ · 4 Extract ✅ · 5 Load ✅ · 6 Transform ✅ · 7 Orchestrate ✅ · 8 Validate ✅ · 9 Maintain ✅ · 10 Monitor ✅

**Keboola Notes**
- 💡 Map directly to **Flows**; prefer **ELT**; keep raw→staged→gold.  
- 💡 Use **Data Streams/CDC** for low-latency; add **Validation** tasks and **SLIs** dashboards.

---

### Data Quality Fundamentals
**Chapters**
1 Why Now ✅ · 2 Reliable Blocks ✅ · 3 Collect/Clean/Test ✅ · 4 Monitoring ✅ · 5 Architecting ✅ · 6 Incidents ✅ · 7 Lineage ✅ · 8 Democratize ✅ · 9 Cases ✅ · 10 Future ✅

**Keboola Notes**
- 💡 Define **Data Contracts**, SLIs/SLOs, and alert routes.  
- 💡 Persist monitors and show status in **Data Apps**; keep lineage and ownership current.

---

### Data Engineering Best Practices
**Chapters**
1 Problem ✅ · 2 Vision/Strategy ✅ · 3 Principles ✅ · 4 Conceptual ✅ · 5 Logical ✅ · 6 Physical ✅ · 7 Software Eng ✅ · 8 Agile ✅ · 9 Testing ✅ · 10 Ops ✅ · 11 Data Services ✅ · 12 Management ✅ · 13 Delivery ✅ · 14 Measures/Notebooks ✅ · 15 ML Pipelines ✅ · 16 Synthesis/Templates ✅

**Keboola Notes**
- 💡 Align Flows to **OKRs**; define **Bronze/Silver/Gold** zones; enforce CI/CD + rollback.  
- 💡 Publish **data products** with contracts & SLAs; govern metrics and notebooks.

---

## Merge Guidance (Maintainers)

- Keep this single file as your **source of truth** or break into sections (Dictionary, Kit, Books) and re-concatenate.  
- Use **stable anchors** (`#k:*`) for dictionary terms and link to them from Flows/Data Apps.  
- Add “From concept to action (Keboola)” boxes to team docs, pointing back to **Design Brief**, **ELT Unit**, **Validation**, and **Data App** templates.  
- On changes, update **tags** (relevance, tech-specific) and ensure **links** aren’t broken.

---

*End of Full Guide.*
