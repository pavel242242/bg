# Google Character Suggestions Scraper

A simple, functional web scraper that collects Google autocomplete suggestions for character-based queries and stores them in Keboola Storage.

## Project: google-scraper

This project scrapes Google autocomplete suggestions for the pattern:
- `"i hate"`
- `"i hate a"` through `"i hate z"`

**Features:**
- Simple, modular architecture (2 main components + orchestrator)
- Apify SDK for robust web scraping
- Keboola SDK for data storage
- Publicly accessible CSV output
- KISS principle - awesomely simple and functional

## Quick Start

```bash
cd google-scraper
pip install -r requirements.txt
cp .env.example .env
# Add your APIFY_API_TOKEN and KEBOOLA_TOKEN to .env
python main.py
```

See `google-scraper/README.md` for detailed documentation.

## Architecture

- **scraper.py** - Apify-based Google autocomplete scraper
- **keboola_writer.py** - Keboola Storage integration
- **main.py** - Simple orchestrator

Clean, functional, production-ready code.
