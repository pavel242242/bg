# DataTalk Event Sync

n8n workflow that scrapes DataTalk.cz events, extracts data via OpenAI, notifies subscribers via Email + Telegram.

## Quick Start

```bash
# 1. Copy and fill environment
cp .env.example .env
nano .env

# 2. Run tests
chmod +x tests/*.sh
./tests/run_tests.sh

# 3. Deploy to Hetzner
chmod +x deploy.sh
./deploy.sh --create   # First time: creates server + deploys
./deploy.sh            # Subsequent: just deploys
```

## Structure

```
.
├── .claude/skills/         # n8n skills for Claude Code
├── .github/workflows/      # CI/CD pipeline
├── datatalk-sync/          # Main application
│   ├── docker-compose.yml
│   ├── .env.example
│   └── workflows/          # n8n workflow JSONs
├── tests/                  # Test scripts
├── deploy.sh               # Manual deploy script
└── .env.example            # Root env template
```

## Env Vars

| Variable | Required | Description |
|----------|----------|-------------|
| `HCLOUD_TOKEN` | Yes | Hetzner Cloud API token |
| `N8N_USER` | Yes | n8n admin username |
| `N8N_PASSWORD` | Yes | n8n admin password |
| `N8N_ENCRYPTION_KEY` | Yes | 32-byte hex (`openssl rand -hex 32`) |
| `WEBHOOK_URL` | Yes | Public n8n URL |
| `OPENAI_API_KEY` | Yes | OpenAI API key |
| `TELEGRAM_BOT_TOKEN` | Yes | From @BotFather |
| `SMTP_HOST` | Yes | SMTP server |
| `SMTP_PORT` | No | Default: 587 |
| `SMTP_USER` | Yes | SMTP username |
| `SMTP_PASS` | Yes | SMTP password |
| `SMTP_SENDER` | Yes | From email |

## Deploy Commands

```bash
./deploy.sh              # Deploy to existing server
./deploy.sh --create     # Create server + deploy
./deploy.sh --status     # Show server info
./deploy.sh --destroy    # Delete server
```

## GitHub Actions

Triggers on push to `main` when `datatalk-sync/**` changes.

**Required secrets:** All env vars above + `DEPLOY_SSH_KEY` + `DEPLOY_SSH_KEY_PUB`

## Workflows

| File | Trigger | Function |
|------|---------|----------|
| `01-subscriber-signup.json` | Form | Signup + verification tokens |
| `02-email-verify.json` | Webhook | Verify email |
| `03-telegram-verify.json` | Webhook | Verify Telegram |
| `04-event-scraper.json` | Weekly | Scrape + extract + notify |

## Tests

```bash
./tests/run_tests.sh      # Run all
./tests/test_workflows.sh # Validate JSONs
./tests/test_docker.sh    # Check docker-compose
```

## Server

- **Name:** chochomesh
- **Type:** cx22 (2 vCPU, 4GB RAM, ~€4/mo)
- **Location:** Falkenstein (fsn1)
- **Max servers:** 3

## n8n Skills

7 Claude Code skills in `.claude/skills/` for building n8n workflows:

- `n8n-expression-syntax` - `{{ }}` patterns
- `n8n-mcp-tools-expert` - Tool usage
- `n8n-workflow-patterns` - Architectural patterns
- `n8n-validation-expert` - Error handling
- `n8n-node-configuration` - Node setup
- `n8n-code-javascript` - JS Code nodes
- `n8n-code-python` - Python Code nodes
