# Keboola Skill - Content Strategy

## TL;DR

**Documentation indexer:** Nice to have, but not essential.
**Focus instead on:** Curated guides, working examples, and proven patterns.

## The Problem with Indexing Raw Docs

### What we built:
- Indexer pulls from GitHub repos
- Creates searchable index
- Simple text search
- Returns doc excerpts

### Why it's limited:
- ❌ Only indexes 50 files (rate limits)
- ❌ Simple keyword search (not semantic)
- ❌ Raw docs not optimized for AI
- ❌ No context about what's important
- ❌ Maintenance overhead

## What Actually Empowers the Skill

### Priority Ranking (what Claude uses most):

1. **System Prompt** ⭐⭐⭐⭐⭐
   - Always loaded, most influential
   - Core concepts and mental models
   - Common patterns
   - How to think about problems

2. **Examples** ⭐⭐⭐⭐⭐
   - Working, tested code
   - Can be adapted to user's needs
   - Shows best practices in action
   - Immediate value

3. **Knowledge Files** ⭐⭐⭐⭐
   - Deep dives on specific topics
   - Comprehensive guides
   - Structured learning
   - Reference material

4. **MCP Tools** ⭐⭐⭐⭐
   - Live access to user's project
   - Real-time data
   - Current state
   - Interactive debugging

5. **Indexed Docs** ⭐⭐
   - Fallback for edge cases
   - Comprehensive reference
   - Optional, not essential

## Recommended Structure

```
skill/
├── system-prompt.md          # Entry point, core concepts
│
├── concepts/                 # Foundational knowledge
│   ├── architecture.md
│   ├── storage.md
│   ├── components.md
│   ├── transformations.md
│   └── orchestrations.md
│
├── guides/                   # Practical how-tos
│   ├── incremental-loading.md
│   ├── data-quality.md
│   ├── error-handling.md
│   ├── performance.md
│   └── testing.md
│
├── components/               # Component deep dives
│   ├── extractors/
│   │   ├── mysql.md
│   │   ├── postgresql.md
│   │   └── salesforce.md
│   └── writers/
│       ├── snowflake.md
│       └── redshift.md
│
├── patterns/                 # Proven patterns
│   ├── cdc-pipeline.md
│   ├── star-schema.md
│   ├── incremental-merge.md
│   └── slowly-changing-dimensions.md
│
├── examples/                 # Working code
│   ├── extractors/
│   │   ├── mysql-basic.json
│   │   ├── mysql-incremental.json
│   │   └── postgresql.json
│   ├── transformations/
│   │   ├── customer-360.sql
│   │   ├── data-quality-checks.sql
│   │   └── python-enrichment.py
│   └── complete-pipelines/
│       ├── crm-to-warehouse.md
│       └── ecommerce-analytics.md
│
├── troubleshooting/          # Problem solving
│   ├── common-errors.md
│   ├── performance-issues.md
│   └── debugging-guide.md
│
└── best-practices/           # Wisdom
    ├── naming-conventions.md
    ├── security.md
    ├── monitoring.md
    └── cost-optimization.md
```

## Growth Strategy

### Phase 1: Start Simple (Current)
✅ System prompt with core concepts
✅ One deep dive (storage.md)
✅ Two working examples
✅ MCP tools for live API access

**Result:** Already useful!

### Phase 2: Add Common Scenarios (Next 2-4 weeks)
- Add 3-4 practical guides (incremental loading, data quality, etc.)
- Add 5-10 more examples (different extractors/writers)
- Add troubleshooting guide with common errors
- Add 2-3 proven patterns

**How:** Add content as you encounter real problems

### Phase 3: Expand Coverage (Next 2-3 months)
- Add component-specific deep dives
- Add more complex patterns
- Add best practices documentation
- Organize by use case

**How:** Build incrementally based on usage

### Phase 4: Optional - Advanced Search (Maybe never)
Only if needed:
- Semantic search with embeddings
- Vector database integration
- Better ranking and relevance
- Comprehensive doc coverage

**How:** Only if curated content isn't sufficient

## What Makes Content Valuable

### ✅ Good Content:
- **Actionable:** "Here's exactly how to do it"
- **Complete:** Includes context, rationale, gotchas
- **Practical:** Solves real problems
- **Structured:** Easy to navigate and understand
- **Examples:** Working code that can be adapted

### ❌ Less Valuable Content:
- Raw API reference (link to official docs instead)
- Every possible option (focus on common cases)
- Theoretical without examples
- Comprehensive but shallow

## Content Guidelines

### For Guides (guides/*.md):

```markdown
# [Topic] Guide

## What is it?
[1-2 paragraph explanation with mental model]

## When to use it?
[Decision criteria, use cases]

## How to configure it?
[Step-by-step with rationale for each step]

## Common patterns:
[2-3 proven approaches with pros/cons]

## Complete example:
[Working configuration that can be copy-pasted]

## Gotchas and troubleshooting:
[Common issues and how to solve them]

## Best practices:
[What experienced users do]

## See also:
[Related guides and examples]
```

### For Examples (examples/*.json, *.sql):

- Must be complete and working
- Include comments explaining why
- Cover common scenarios
- Show best practices
- Can be adapted to user's needs

### For Patterns (patterns/*.md):

- Explain the problem being solved
- Show the pattern with rationale
- Provide working example
- Discuss trade-offs
- Link to related patterns

## Evolution Over Time

### Week 1-2: Use what we have
- Test with real questions
- Note what's missing
- Identify gaps

### Week 3-4: Fill critical gaps
- Add guides for common tasks
- Add examples for your components
- Document solutions to problems you face

### Month 2: Refine organization
- Reorganize based on usage patterns
- Add cross-references
- Improve examples

### Month 3+: Expand coverage
- Add more components
- Add more patterns
- Add advanced topics
- Maybe consider advanced search

## Measuring Success

### Good indicators:
✅ Claude answers questions accurately without searching
✅ Users find examples that match their needs
✅ Troubleshooting guides resolve real issues
✅ Patterns are referenced and adapted
✅ You're adding content based on actual use

### Bad indicators:
❌ Need to search external docs frequently
❌ Examples don't cover real scenarios
❌ Content is comprehensive but not helpful
❌ Adding content "just in case"

## Key Principle

**"Add content when you need it, not when you might need it"**

Build the skill organically:
1. Start minimal (we have this)
2. Add as you use it
3. Focus on quality over quantity
4. Curate, don't dump
5. Examples > documentation
6. Practical > comprehensive

## Current Status

✅ **Phase 1 Complete:** Minimal but functional skill
⏭️ **Next:** Add 2-3 guides and 5-10 examples as you use Keboola
⏸️ **Later:** Expand based on real needs
❓ **Maybe:** Advanced search if curated content isn't enough

## Recommendation

1. **Keep the indexer code** (it's there if you need it)
2. **Don't rely on it** (focus on curated content)
3. **Start using the skill now** (it's already useful)
4. **Add content incrementally** (as you encounter needs)
5. **Focus on examples and guides** (highest value)

Your skill is ready to use. Don't let perfect be the enemy of good!
