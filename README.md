# Google Character Suggestions Scraper

A simple, functional web scraper that collects Google autocomplete suggestions for character-based queries and stores them in Keboola Storage, with an interactive data journalism visualization.

## Project: google-scraper

This project scrapes Google autocomplete suggestions for the pattern:
- `"i hate"`
- `"i hate a"` through `"i hate z"`

**Features:**
- Simple, modular architecture (2 main components + orchestrator)
- Apify SDK for robust web scraping
- Keboola SDK for data storage
- **Interactive HTML visualization** with word clouds and letter navigation
- Publicly accessible CSV output
- KISS principle - awesomely simple and functional

## 🎨 Interactive Visualization

**View the data story**: Open `google-scraper/index.html` in your browser

Features:
- Click letters A-Z to explore what people hate
- Dynamic word clouds showing frequency patterns
- Top 10 ranked suggestions for each query
- Beautiful, responsive design
- No backend required - pure static HTML

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
