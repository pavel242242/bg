# DataTalk Event Sync

Self-hosted n8n workflow that scrapes DataTalk events, extracts structured data using AI, and notifies subscribers via Email and Telegram.

## Features

- Weekly scraping of https://www.datatalk.cz/kalendar-akci/
- LLM-powered extraction of event details (title, dates, location, speakers, summary)
- Double-verified subscriber system (email + Telegram)
- Notifications via Email and Telegram
- All data stored in n8n Tables (no external database needed)

## Prerequisites

- Docker and Docker Compose
- OpenAI API key
- Telegram Bot (create via [@BotFather](https://t.me/BotFather))
- SMTP server for sending emails
- Public URL for webhooks (or use ngrok for testing)

## Quick Start

### 1. Clone and Configure

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your credentials
nano .env
```

### 2. Generate Encryption Key

```bash
openssl rand -hex 32
```

Add the output to `N8N_ENCRYPTION_KEY` in `.env`.

### 3. Start n8n

```bash
docker-compose up -d
```

Access n8n at http://localhost:5678

### 4. Create n8n Tables

In n8n, go to **Tables** and create two tables:

**subscribers**
| Field | Type |
|-------|------|
| email | Text |
| telegram | Text |
| token | Text |
| token_expiry | Text |
| email_verified | Boolean |
| telegram_verified | Boolean |
| active | Boolean |
| created_at | Text |

**events**
| Field | Type |
|-------|------|
| url | Text |
| title | Text |
| start_date | Text |
| end_date | Text |
| location | Text |
| venue | Text |
| speakers | Text |
| summary | Text |
| created_at | Text |

### 5. Create Credentials

In n8n, go to **Credentials** and create:

**SMTP** (for email)
- Host: your SMTP server
- Port: 587 (or your SMTP port)
- User: your SMTP username
- Password: your SMTP password

**HTTP Header Auth** (for OpenAI)
- Name: `Authorization`
- Value: `Bearer YOUR_OPENAI_API_KEY`

### 6. Import Workflows

Import all workflow files from `workflows/` directory:

1. Go to **Workflows** → **Import from File**
2. Import each JSON file:
   - `01-subscriber-signup.json`
   - `02-email-verify.json`
   - `03-telegram-verify.json`
   - `04-event-scraper.json`

### 7. Activate Workflows

Activate all 4 workflows.

## Usage

### Subscribe to Events

Share the signup form URL with users:
```
https://your-n8n-url.com/form/datatalk-signup
```

Users will:
1. Fill in email and Telegram username
2. Receive verification email
3. Receive Telegram message from your bot
4. Click both links to activate subscription

### Manual Trigger

To run the scraper immediately (for testing):
1. Open "DataTalk - Event Scraper" workflow
2. Click "Execute Workflow"

## Environment Variables

| Variable | Description |
|----------|-------------|
| `N8N_USER` | n8n admin username |
| `N8N_PASSWORD` | n8n admin password |
| `N8N_ENCRYPTION_KEY` | 32-char encryption key |
| `WEBHOOK_URL` | Public URL for webhooks |
| `OPENAI_API_KEY` | OpenAI API key |
| `TELEGRAM_BOT_TOKEN` | Telegram bot token from BotFather |
| `SMTP_HOST` | SMTP server hostname |
| `SMTP_PORT` | SMTP port (usually 587) |
| `SMTP_USER` | SMTP username |
| `SMTP_PASS` | SMTP password |
| `SMTP_SENDER` | From address for emails |

## Telegram Bot Setup

1. Message [@BotFather](https://t.me/BotFather) on Telegram
2. Send `/newbot` and follow prompts
3. Copy the bot token to `TELEGRAM_BOT_TOKEN`
4. Users must start a chat with your bot before receiving messages

**Note:** The bot sends messages to usernames. Users need to have a public username set in Telegram settings.

## Troubleshooting

### Telegram messages not delivered

- Ensure users have started a conversation with the bot
- Verify the username is correct (without @)
- Check bot token is valid

### Email verification links not working

- Verify `WEBHOOK_URL` is publicly accessible
- Check SMTP credentials are correct
- Look at workflow execution logs in n8n

### Events not being scraped

- Verify OpenAI API key is valid
- Check the website structure hasn't changed
- Review the "Extract Event URLs" node for parsing errors

## Architecture

```
┌─────────────────┐    ┌──────────────────┐
│  Signup Form    │───▶│  Save Subscriber │
└─────────────────┘    └──────────────────┘
                              │
         ┌────────────────────┼────────────────────┐
         ▼                    ▼                    │
┌─────────────────┐    ┌──────────────────┐        │
│  Email Verify   │    │  Telegram Verify │        │
│    Webhook      │    │     Webhook      │        │
└─────────────────┘    └──────────────────┘        │
         │                    │                    │
         └────────────────────┼────────────────────┘
                              ▼
                    ┌──────────────────┐
                    │ Active Subscriber│
                    └──────────────────┘

┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│ Weekly Schedule │───▶│  Scrape Events   │───▶│  OpenAI Extract │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                                       │
                                                       ▼
                              ┌─────────────────────────────────────┐
                              │         For Each New Event          │
                              │  ┌──────────┐    ┌───────────────┐  │
                              │  │   Email  │    │   Telegram    │  │
                              │  │  Notify  │    │    Notify     │  │
                              │  └──────────┘    └───────────────┘  │
                              └─────────────────────────────────────┘
```

## License

MIT
