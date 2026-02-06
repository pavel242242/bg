# DataTalk Event Sync (Python)

Lightweight Python version - ~400 lines of code vs n8n's complexity.

## Features

- **Scraper**: Weekly scraping of datatalk.cz/events
- **LLM Extraction**: GPT-4o-mini for structured data
- **Email**: Via Resend.com (simpler than SMTP)
- **Telegram**: Optional notifications
- **SQLite**: Zero-config database
- **Scheduler**: Built-in APScheduler

## Quick Start

```bash
# 1. Setup
cp .env.example .env
# Edit .env with your API keys

# 2. Run with Docker
docker compose up -d

# 3. Check
curl http://localhost:8000/health
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | App info |
| `/health` | GET | Health check |
| `/subscribe` | POST | Subscribe email |
| `/verify` | GET | Verify email |
| `/unsubscribe` | POST | Unsubscribe |
| `/events` | GET | List events |
| `/scrape` | POST | Manual trigger |

## Configuration

All via environment variables:

```bash
# Required for full functionality
OPENAI_API_KEY=sk-...      # Event extraction
RESEND_API_KEY=re_...      # Email sending

# Optional
TELEGRAM_BOT_TOKEN=...     # Telegram notifications
SCRAPE_SCHEDULE=0 8 * * 1  # Cron schedule
```

## Development

```bash
# Install
pip install -r requirements.txt

# Run locally
uvicorn app.main:app --reload

# Test
pytest tests/
```

## Structure

```
app/
├── main.py      # FastAPI app + endpoints
├── config.py    # Settings (pydantic)
├── models.py    # Database models (SQLModel)
└── services.py  # Business logic (scraper, LLM, notifier)
```

## Comparison to n8n version

| Aspect | n8n | Python |
|--------|-----|--------|
| Image size | ~500MB | ~150MB |
| RAM usage | 200-500MB | 50-100MB |
| Lines of code | GUI config | ~400 |
| Flexibility | Limited | Full |
| Visual debugging | Yes | Logs only |

## License

MIT
