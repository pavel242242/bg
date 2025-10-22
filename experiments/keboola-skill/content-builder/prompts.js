/**
 * Agent Prompts for Content Generation
 *
 * Each prompt is optimized for Haiku to generate specific content types.
 */

export const PROMPTS = {

  componentGuide: (componentName, docUrls) => `
You are a technical documentation expert creating a comprehensive guide for Keboola's ${componentName}.

TASK: Read the provided documentation and create a detailed, practical guide.

DOCUMENTATION URLS:
${docUrls.map(url => `- ${url}`).join('\n')}

OUTPUT STRUCTURE:
# ${componentName} Guide

## Overview
- What is this component?
- What problem does it solve?
- When should you use it?

## Configuration

### Connection Settings
- Explain each required field
- Show example values
- Note common gotchas

### Table/Data Configuration
- How to specify what data to extract/load
- Options and their purposes
- Performance considerations

### Advanced Options
- Optional settings
- When to use them
- Trade-offs

## Common Patterns

### Pattern 1: Basic Usage
\`\`\`json
{
  // Working configuration
  // with inline comments
}
\`\`\`

### Pattern 2: Incremental Loading
\`\`\`json
{
  // Incremental configuration
}
\`\`\`

### Pattern 3: Complex Scenario
\`\`\`json
{
  // Advanced configuration
}
\`\`\`

## Troubleshooting

### Problem: [Common Issue 1]
**Symptoms:** [What user sees]
**Cause:** [Root cause]
**Solution:** [How to fix]

### Problem: [Common Issue 2]
...

## Best Practices
- [ ] Use descriptive names
- [ ] Enable incremental loading for large tables
- [ ] Set appropriate primary keys
- [ ] Add error notifications
- [ ] Test with sample data first

## See Also
- Related components
- Related guides

GUIDELINES:
- Be specific and actionable
- Include working code examples
- Explain the "why" not just "how"
- Cover common pitfalls
- Focus on practical use cases
- Use clear, simple language

Write the complete guide now.
`,

  patternExtractor: (patternName, context) => `
You are a data engineering expert documenting a proven pattern for Keboola pipelines.

TASK: Document the "${patternName}" pattern in detail.

CONTEXT:
${context}

OUTPUT STRUCTURE:
# ${patternName} Pattern

## Problem
What problem does this pattern solve?
When do you encounter this problem?

## Solution
High-level description of the pattern.
Key concepts and approach.

## Implementation in Keboola

### Architecture
[Describe component flow]

### Components Used
- Component 1: Purpose
- Component 2: Purpose
...

### Step-by-Step

#### Step 1: [Name]
[What to do]
[Why it matters]

#### Step 2: [Name]
...

## Complete Example

### Extractors
\`\`\`json
{
  // Configuration
}
\`\`\`

### Transformations
\`\`\`sql
-- SQL code with comments
\`\`\`

### Writers
\`\`\`json
{
  // Configuration
}
\`\`\`

### Orchestration
- Order of execution
- Dependencies
- Scheduling

## Trade-offs

### Pros
- Advantage 1
- Advantage 2

### Cons
- Limitation 1
- Limitation 2

## When to Use
✅ Use this pattern when...
❌ Don't use this pattern when...

## Variations
- Variation 1: [Description]
- Variation 2: [Description]

## Related Patterns
- Pattern A: [Relationship]
- Pattern B: [Relationship]

## Real-World Example
[Concrete scenario with specific numbers/tables]

Write the complete pattern documentation now.
`,

  exampleCreator: (componentType, scenario) => `
You are a Keboola configuration expert creating working examples.

TASK: Create a complete, working ${componentType} configuration for: ${scenario}

REQUIREMENTS:
1. Must be valid JSON
2. Must include all required fields
3. Must include inline comments explaining each section
4. Must follow Keboola best practices
5. Must be a realistic, practical example

OUTPUT FORMAT:
\`\`\`json
{
  "parameters": {
    // Configuration here
    // with detailed comments
  }
}
\`\`\`

FOLLOWED BY:

## About This Example
[2-3 paragraphs explaining:
- What this configuration does
- Key settings and why they're set that way
- How to adapt it to other scenarios]

## Key Points
- Point 1: [Explanation]
- Point 2: [Explanation]
...

## Common Modifications
- To do X: Change...
- To do Y: Add...

Create the complete example now.
`,

  troubleshootingGuide: (category) => `
You are a Keboola support engineer creating a troubleshooting guide for: ${category}

TASK: Create a comprehensive troubleshooting guide with problem → solution mappings.

OUTPUT STRUCTURE:
# Troubleshooting: ${category}

## Quick Diagnostics
- [ ] Check 1: [What to check]
- [ ] Check 2: [What to check]
- [ ] Check 3: [What to check]

## Common Issues

### Issue: [Problem Name]

**Symptoms:**
- What the user sees
- Error messages
- Unexpected behavior

**Root Cause:**
Why this happens

**Solution:**
1. Step 1
2. Step 2
3. Step 3

**Prevention:**
How to avoid this in the future

**Related Issues:**
- Issue A
- Issue B

---

[Repeat for 5-10 common issues]

## Debugging Process

### Step 1: Gather Information
- What information to collect
- Where to find it

### Step 2: Isolate the Problem
- How to narrow down the cause
- What to test

### Step 3: Apply Fix
- Common solutions
- How to verify

### Step 4: Prevent Recurrence
- Best practices
- Monitoring

## When to Contact Support
- Scenario 1
- Scenario 2

## Useful Tools
- Tool 1: [Purpose]
- Tool 2: [Purpose]

Create the complete troubleshooting guide now.
`,

  bestPractices: (topic) => `
You are a Keboola expert documenting best practices for: ${topic}

TASK: Create actionable best practices guide based on experience.

OUTPUT STRUCTURE:
# Best Practices: ${topic}

## Principles
Core principles that guide decisions in this area.

## Essential Practices

### Practice 1: [Name]
**What:** [Description]
**Why:** [Rationale]
**How:** [Implementation]
**Example:**
\`\`\`
// Code or configuration
\`\`\`

### Practice 2: [Name]
...

[Include 5-10 essential practices]

## Anti-Patterns (What NOT to Do)

### Anti-Pattern 1: [Name]
**Problem:** [What people do wrong]
**Why it's bad:** [Consequences]
**Instead:** [What to do instead]

### Anti-Pattern 2: [Name]
...

## Decision Framework

### When deciding X:
- If A, then do 1
- If B, then do 2
- If C, then do 3

## Checklist
- [ ] Item 1
- [ ] Item 2
- [ ] Item 3
...

## Common Mistakes
1. Mistake: [Description]
   Fix: [Solution]

2. Mistake: [Description]
   Fix: [Solution]

## Advanced Tips
- Tip 1: [For experienced users]
- Tip 2: [Optimization]
- Tip 3: [Edge cases]

## Resources
- Related guides
- External references

Create the complete best practices guide now.
`,

  conceptExplainer: (concept) => `
You are an educator explaining Keboola concepts clearly.

TASK: Explain the concept of "${concept}" in Keboola clearly and thoroughly.

OUTPUT STRUCTURE:
# Understanding ${concept}

## What Is It?
[2-3 paragraphs with clear definition]

## Why It Exists
- Problem it solves
- Context in Keboola architecture
- How it fits in the data pipeline

## How It Works

### Core Mechanism
[Explain the underlying mechanism]

### Key Components
- Component 1: [Role]
- Component 2: [Role]

### Visual Mental Model
[Describe using analogy or metaphor]

Example: "Think of X like a..."

## Practical Examples

### Example 1: Simple Case
\`\`\`
// Code or configuration
\`\`\`
[Explanation]

### Example 2: Real-World Scenario
\`\`\`
// Code or configuration
\`\`\`
[Explanation]

## Common Misconceptions

### Misconception 1
❌ What people think
✅ What's actually true

### Misconception 2
❌ What people think
✅ What's actually true

## When to Use

### Good For:
- Scenario A
- Scenario B

### Not Good For:
- Scenario X
- Scenario Y

## Related Concepts
- Concept A: [Relationship]
- Concept B: [Relationship]

## Deep Dive

### Advanced Details
[For users who want to understand deeper]

### Implementation Notes
[Technical details]

### Performance Considerations
[Optimization tips]

Create the complete concept explanation now.
`

};

export default PROMPTS;
