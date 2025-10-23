# Keboola Skill - Repository Setup Guide

Quick guide to prepare this repository for others to use the Keboola data engineering skill with Claude Code.

---

## What to Include in Repo

### Essential Files (Must Have)
```
keboola-skill/
├── SKILL.md                           # Main skill file (923 lines) - REQUIRED
├── README.md                          # Quick start guide
├── resources/
│   ├── KNOWLEDGE_MAP.md               # Index of 85+ extractors, 29+ writers
│   └── Keboola_Data_Enablement_Guide.md  # 7 DA/DE books
└── docs-repos/                        # Clone these, or document how to get them
    ├── connection-docs/               # Official Keboola docs (252 files)
    └── developers-docs/               # Developer docs (199 files)
```

### Optional (Nice to Have)
```
├── V4.1_DESIGN.md                     # Feature design rationale
├── LESSONS_LEARNED.md                 # Development journey
├── SETUP_FOR_CLAUDE_CODE.md           # Installation instructions
└── tests/
    └── v4_pricing_optimization_test.md  # Example evaluation
```

---

## Repo Structure Options

### Option 1: With Docs (Large ~50MB)
**Pros**: Works immediately, no extra setup
**Cons**: Large repo size

```bash
# Include everything
git add SKILL.md resources/ docs-repos/
```

### Option 2: Without Docs (Small ~2MB) - RECOMMENDED
**Pros**: Small, fast clone
**Cons**: Users must clone docs separately

```bash
# Add docs-repos/ to .gitignore
echo "docs-repos/" >> .gitignore

# Include setup instructions in README
```

**README should document:**
```bash
# Setup
git clone <your-repo>
cd keboola-skill

# Clone Keboola docs
git clone https://github.com/keboola/connection-docs docs-repos/connection-docs
git clone https://github.com/keboola/developers-docs docs-repos/developers-docs
```

---

## Create User-Friendly README.md

### Minimal README Structure

```markdown
# Keboola Data Engineering Skill for Claude Code

Expert Claude Code skill for building Keboola data pipelines. Supports 85+ data sources, 29+ destinations, with built-in validation and DA/DE best practices.

## Features (v4.1)
- Context-aware design (remembers PII, frequency, metrics)
- Multi-agent delegation (discovery, SQL generation, troubleshooting)
- Sandbox testing before production
- Business impact validation with rollback plans
- Visual architecture diagrams
- Error recovery workflows
- 7 DA/DE books knowledge (ISL, Data Smart, etc.)

## Quick Install

### 1. Clone this repo
git clone <repo-url> ~/.claude/skills/keboola

### 2. Get Keboola docs
cd ~/.claude/skills/keboola
git clone https://github.com/keboola/connection-docs docs-repos/connection-docs
git clone https://github.com/keboola/developers-docs docs-repos/developers-docs

### 3. Use with Claude Code
Just ask Claude Code about Keboola tasks:
"I need to extract Salesforce data and create a revenue dashboard"

Claude Code will automatically use this skill.

## What It Does

**4-Step Workflow:**
1. Understand: Asks business questions, saves context
2. Discover: Finds relevant extractors from 85+ options
3. Propose: Shows architecture + diagram, gets approval
4. Build: Generates configs, tests in sandbox, validates impact, deploys

**Outputs:** Extractor configs, SQL transformations, architecture docs, rollback plans

## Documentation
- `SKILL.md` - Full skill specification (923 lines)
- `SETUP_FOR_CLAUDE_CODE.md` - Detailed setup instructions
- `V4.1_DESIGN.md` - Feature design and rationale
- `LESSONS_LEARNED.md` - Development best practices

## Requirements
- Claude Code (latest version)
- (Optional) Keboola account for API access
- (Optional) MCP server for live API integration

## License
[Your license]

## Support
[How to get help]
```

---

## Testing Before Publishing

### 1. Test Clean Install

```bash
# Simulate user experience
rm -rf /tmp/test-keboola-skill
git clone /home/user/bg/experiments/keboola-skill /tmp/test-keboola-skill
cd /tmp/test-keboola-skill

# Follow your own README instructions
# Does it work?
```

### 2. Check File Sizes

```bash
# Check what's large
du -sh * | sort -h

# If docs-repos/ is huge, consider .gitignore
du -sh docs-repos/  # Likely ~50MB
```

### 3. Verify All References Work

```bash
# Check SKILL.md references exist
grep "Use Read tool on" SKILL.md | while read line; do
  file=$(echo "$line" | grep -oP '`\K[^`]+' | head -1)
  [ -f "$file" ] && echo "✅ $file" || echo "❌ MISSING: $file"
done
```

---

## .gitignore Recommendations

```gitignore
# Large docs (users clone separately)
docs-repos/

# Test files
tests/v4_pricing_optimization_test.md

# User-specific configs
YOUR_CONFIG.json
*_config.json
project_context.json
data_inventory.json
architecture_proposal.md
rollback_plan.md
DELIVERABLES.md
transform.sql

# MCP secrets
*.env

# OS files
.DS_Store
Thumbs.db
```

---

## Publishing Checklist

### Before Push to GitHub/GitLab

- [ ] README.md with quick install instructions
- [ ] .gitignore excludes large docs (or include them if you prefer)
- [ ] SKILL.md is present and valid (check frontmatter)
- [ ] KNOWLEDGE_MAP.md exists
- [ ] Keboola_Data_Enablement_Guide.md exists
- [ ] LICENSE file included
- [ ] Remove any API tokens or secrets
- [ ] Test clean install works

### Repository Settings

- [ ] Add topics/tags: `claude-code`, `keboola`, `data-engineering`, `skill`
- [ ] Write clear repo description
- [ ] Add link to Claude Code docs: https://docs.claude.com/claude-code
- [ ] Enable issues (for user questions)

### Documentation Links

Add to README:
- Link to Keboola docs: https://help.keboola.com/
- Link to Claude Code: https://docs.claude.com/claude-code
- Link to MCP protocol: https://modelcontextprotocol.io/

---

## How Users Will Install

### Typical User Flow

```bash
# 1. Clone your repo
git clone https://github.com/yourname/keboola-skill ~/.claude/skills/keboola

# 2. Get docs
cd ~/.claude/skills/keboola
git clone https://github.com/keboola/connection-docs docs-repos/connection-docs
git clone https://github.com/keboola/developers-docs docs-repos/developers-docs

# 3. Use in Claude Code
# Just start describing Keboola tasks
```

### How Claude Code Finds Skills

Claude Code automatically scans `~/.claude/skills/` for directories containing `SKILL.md`.

**Important**: The skill activates based on:
- Task keywords (Keboola, data pipeline, extractor, transformation)
- Skill description match
- User context

**NOT** via `/skill` command (that's not a real command in Claude Code).

---

## Updating the Skill (For You)

When you improve the skill:

```bash
# 1. Edit SKILL.md
vim experiments/keboola-skill/SKILL.md

# 2. Commit
git add experiments/keboola-skill/SKILL.md
git commit -m "v4.2: Add feature X"

# 3. Push to your repo
git push

# Users update with:
cd ~/.claude/skills/keboola
git pull
```

---

## Optional: Create Install Script

Make it even easier:

```bash
#!/bin/bash
# install.sh

echo "Installing Keboola skill for Claude Code..."

# Create skills directory
mkdir -p ~/.claude/skills

# Clone skill
git clone https://github.com/yourname/keboola-skill ~/.claude/skills/keboola

# Clone docs
cd ~/.claude/skills/keboola
git clone https://github.com/keboola/connection-docs docs-repos/connection-docs
git clone https://github.com/keboola/developers-docs docs-repos/developers-docs

echo "✅ Installation complete!"
echo "Start using Claude Code and ask about Keboola tasks."
```

Users run:
```bash
curl -sSL https://raw.githubusercontent.com/yourname/keboola-skill/main/install.sh | bash
```

---

## Minimal Working Example

For absolute minimal repo (only essential files):

```
keboola-skill/
├── README.md              # Quick start
├── SKILL.md               # Main skill (923 lines)
└── resources/
    ├── KNOWLEDGE_MAP.md   # Component index
    └── Keboola_Data_Enablement_Guide.md  # DA/DE books

Users must:
1. Clone this repo
2. Clone docs separately (instructions in README)
3. Use with Claude Code
```

**Total size**: ~2MB (vs ~50MB with docs)

---

## Quick Commands

```bash
# Count lines
wc -l SKILL.md resources/*.md

# Check repo size
du -sh .

# Test skill structure
ls SKILL.md && echo "✅ Main skill exists" || echo "❌ Missing SKILL.md"

# List what's tracked by git
git ls-files

# Check for secrets
grep -r "token\|password\|secret" --exclude-dir=.git --exclude-dir=node_modules .
```

---

## Summary: Ship It

**Minimum viable repo:**
1. SKILL.md (main file)
2. README.md (install instructions)
3. resources/KNOWLEDGE_MAP.md
4. resources/Keboola_Data_Enablement_Guide.md
5. .gitignore (exclude docs-repos/)

**Users install with:**
```bash
git clone <your-repo> ~/.claude/skills/keboola
cd ~/.claude/skills/keboola
git clone https://github.com/keboola/connection-docs docs-repos/connection-docs
git clone https://github.com/keboola/developers-docs docs-repos/developers-docs
```

**Size**: 2MB (without docs) or 50MB (with docs)

**Works immediately** once in `~/.claude/skills/` directory.
