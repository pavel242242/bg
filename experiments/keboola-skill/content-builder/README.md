# Keboola Skill - Automated Content Builder

## Concept: Haiku Agents as Content Curators

Instead of raw documentation indexing, use **specialized Haiku agents** to:
- Read Keboola's official documentation
- Extract key information
- Write curated guides
- Create practical examples
- Document patterns and best practices

## Why Haiku Agents?

✅ **Cost-effective:** Haiku is ~60x cheaper than Sonnet
✅ **Fast:** Processes documentation quickly
✅ **Parallel:** Run multiple agents simultaneously
✅ **Specialized:** Each agent has a specific task
✅ **Repeatable:** Can re-run as Keboola docs update

## Architecture

```
ORCHESTRATOR (Sonnet)
├─> Identifies what content is needed
├─> Spawns specialized Haiku agents in parallel
└─> Reviews and integrates results

HAIKU AGENTS (Running in Parallel)
├─> Component Guide Writer
│   └─> Reads: Component docs
│   └─> Writes: guides/components/{component}.md
│
├─> Pattern Extractor
│   └─> Reads: Multiple docs, examples
│   └─> Writes: patterns/{pattern}.md
│
├─> Example Creator
│   └─> Reads: Component schemas, docs
│   └─> Writes: examples/{component}-{scenario}.json
│
├─> Troubleshooting Specialist
│   └─> Reads: Error messages, support docs
│   └─> Writes: troubleshooting/{category}.md
│
├─> Best Practices Compiler
│   └─> Reads: Multiple sources
│   └─> Writes: best-practices/{topic}.md
│
└─> Concept Explainer
    └─> Reads: Architecture docs
    └─> Writes: concepts/{concept}.md
```

## Agent Specializations

### 1. Component Guide Writer
**Input:** Keboola component documentation URL
**Task:** Write comprehensive guide for using the component
**Output:** Structured markdown with:
- What is it?
- When to use it?
- How to configure it?
- Common patterns
- Complete examples
- Troubleshooting

### 2. Pattern Extractor
**Input:** Multiple related documents
**Task:** Identify and document proven patterns
**Output:** Pattern description with:
- Problem being solved
- Pattern implementation
- Working example
- Trade-offs
- Related patterns

### 3. Example Creator
**Input:** Component documentation + schema
**Task:** Create working configuration examples
**Output:** Valid JSON configurations for:
- Basic usage
- Incremental loading
- Complex scenarios
- With comments explaining each field

### 4. Troubleshooting Specialist
**Input:** Error messages, forum posts, support docs
**Task:** Create troubleshooting guides
**Output:** Problem → Solution mappings with:
- Symptom description
- Root cause
- Step-by-step fix
- Prevention tips

### 5. Best Practices Compiler
**Input:** Multiple documentation sources
**Task:** Extract and organize best practices
**Output:** Structured guidelines for:
- Naming conventions
- Security
- Performance
- Cost optimization
- Team collaboration

### 6. Concept Explainer
**Input:** Architecture documentation
**Task:** Explain core concepts clearly
**Output:** Educational content with:
- Clear definitions
- Mental models
- Visual analogies
- Common misconceptions
- Practical implications

## Implementation

### Phase 1: Build the Orchestrator

```javascript
// content-builder/orchestrator.js
class ContentOrchestrator {
  async buildComponent(componentName) {
    // Launch 3 agents in parallel
    const [guide, examples, troubleshooting] = await Promise.all([
      this.spawnGuideWriter(componentName),
      this.spawnExampleCreator(componentName),
      this.spawnTroubleshooter(componentName)
    ]);

    // Save results
    await this.saveContent(guide, examples, troubleshooting);
  }

  async spawnGuideWriter(component) {
    return agent.run({
      prompt: `Read Keboola documentation for ${component} and write...`,
      model: 'claude-haiku',
      tools: ['WebFetch', 'Read']
    });
  }
}
```

### Phase 2: Define Agent Prompts

Each agent gets a specialized prompt optimized for its task.

### Phase 3: Run in Batches

```bash
# Build content for top 10 components
npm run build-content -- --components mysql,postgresql,snowflake,salesforce...

# Build all guides
npm run build-content -- --all-guides

# Update specific section
npm run build-content -- --patterns
```

## Content Quality Control

### Agent Output → Review → Edit → Commit

1. **Agent generates** initial content (Haiku)
2. **Orchestrator reviews** for completeness
3. **Human reviews** and edits
4. **Commit** to skill knowledge base

## Example: Building MySQL Extractor Guide

### Step 1: Orchestrator decides what's needed
```
Need: guides/components/extractors/mysql.md
```

### Step 2: Spawn Guide Writer Agent
```javascript
agent.run({
  model: 'haiku',
  prompt: `
    You are a technical writer creating a guide for Keboola's MySQL Extractor.

    Read the documentation:
    - https://help.keboola.com/components/extractors/database/mysql/
    - https://developers.keboola.com/extend/component/

    Write a comprehensive guide following this structure:

    # MySQL Extractor Guide

    ## What is it?
    [2-3 paragraphs explaining the component]

    ## When to use it?
    [Use cases and scenarios]

    ## Configuration
    ### Connection Settings
    [Explain each field]

    ### Table Configuration
    [Explain table settings]

    ### Advanced Options
    [SSL, SSH, etc.]

    ## Common Patterns
    ### Basic Extraction
    [Simple example]

    ### Incremental Loading
    [Incremental example]

    ### Complex Queries
    [Advanced example]

    ## Complete Examples
    [3 working JSON configs]

    ## Troubleshooting
    [Common issues and solutions]

    ## Best Practices
    [What experienced users do]

    Write clear, actionable content with working examples.
  `,
  tools: ['WebFetch']
})
```

### Step 3: Agent writes the guide
Agent reads docs, extracts key info, writes structured guide.

### Step 4: Save to skill
```bash
skill/guides/components/extractors/mysql.md
```

## Parallel Processing

Run multiple agents simultaneously:

```javascript
// Build all database extractors in parallel
const extractors = ['mysql', 'postgresql', 'mssql', 'oracle', 'mongodb'];

const guides = await Promise.all(
  extractors.map(db => buildComponentGuide(db))
);

// Save all guides
guides.forEach(guide => saveToSkill(guide));
```

## Cost Estimation

### Per Component Guide:
- Input: ~10K tokens (reading docs)
- Output: ~5K tokens (writing guide)
- Cost: ~$0.01 per component

### Build 50 Components:
- 50 components × $0.01 = **$0.50**

### Build Complete Knowledge Base:
- 50 components
- 20 patterns
- 30 examples
- 10 troubleshooting guides
- 10 best practices

**Total: ~$1.50 to build comprehensive knowledge base!**

## Advantages Over Manual Writing

✅ **Faster:** Minutes instead of hours
✅ **Consistent:** Same structure for all guides
✅ **Comprehensive:** Reads all source docs
✅ **Maintainable:** Re-run to update
✅ **Scalable:** Add more components easily
✅ **Cost-effective:** ~$1-2 for entire knowledge base

## Disadvantages

❌ May need human review/editing
❌ Can miss nuance or context
❌ Needs good source documentation
❌ Requires oversight and validation

## Recommended Workflow

1. **Define structure** (what guides/patterns you need)
2. **Build agent prompts** (one per content type)
3. **Run agents in parallel** (fast bulk processing)
4. **Review output** (human-in-the-loop)
5. **Edit and refine** (add your experience)
6. **Commit to skill** (ready to use)
7. **Update periodically** (re-run when Keboola updates docs)

## Getting Started

```bash
# Setup
cd content-builder
npm install

# Build specific component
npm run build-component mysql

# Build category
npm run build-category extractors

# Build everything
npm run build-all

# Review generated content
ls -la ../skill/guides/
```

## Future Enhancements

- **Semantic analysis:** Agent analyzes patterns across docs
- **Example validation:** Test generated configs against Keboola API
- **Cross-referencing:** Link related guides automatically
- **Version tracking:** Track which Keboola version docs came from
- **Incremental updates:** Only regenerate changed components

## Next Steps

1. Create agent prompt templates
2. Build orchestrator script
3. Test with 2-3 components
4. Review quality
5. Scale to all components
6. Integrate into skill

This is a much better investment than simple indexing!
