# News Monitor

A simple app to monitor newsapi.org for configurable company names. Pings you every hour with news and lets you acknowledge them.

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Configure companies to monitor in `config.json`:
   ```json
   {
     "news_api_key": "your-api-key",
     "companies": ["Apple", "Google", "Microsoft"],
     "check_interval_minutes": 60,
     "max_articles_per_company": 5
   }
   ```

## Usage

### Start the monitor (runs hourly)
```bash
python news_monitor.py
```

### One-time check
```bash
python news_monitor.py check
```

### View unacknowledged news
```bash
python news_monitor.py list
```

### Acknowledge news
```bash
# Acknowledge a specific article (use first few chars of ID)
python news_monitor.py ack abc123

# Acknowledge all articles
python news_monitor.py ack-all

# Acknowledge all for a specific company
python news_monitor.py ack-all Google
```

### Manage companies
```bash
# List configured companies
python news_monitor.py companies

# Add a company
python news_monitor.py add Tesla

# Remove a company
python news_monitor.py remove Microsoft
```

## How it works

1. Every hour (configurable), the app fetches news from News API for each configured company
2. New articles are stored in a local SQLite database
3. A summary is printed showing unacknowledged articles
4. You can acknowledge articles individually or all at once
5. Acknowledged articles won't appear in future summaries

## Files

- `config.json` - Configuration (API key, companies, interval)
- `news_monitor.py` - Main application
- `news_data.db` - SQLite database (auto-created, gitignored)
