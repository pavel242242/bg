# Google Autocomplete Scraper

A modular Google autocomplete scraper that collects suggestions for "i hate [letter]" patterns (a-z) and publishes them to publicly accessible storage.

## 🎯 Features

- **Two scraping modes**:
  - Direct scraping (simple, may face rate limits)
  - Apify-powered scraping (reliable, production-ready)
- **Keboola integration** for public data publishing
- **Smart result limiting**: Returns top 5 suggestions per query (configurable)
- **Official SDKs**: Uses `apify-client` and `kbcstorage` Python SDKs
- **Modular architecture** with 2-3 simple components
- **Multiple output formats** (long format and flat format CSVs)
- Error handling and progress reporting

## 📁 Project Structure

```
google-scraper/
├── main.py                      # Simple direct scraper
├── main_apify_keboola.py       # Production scraper (Apify + Keboola)
├── demo.py                      # Demo with sample data
├── src/
│   ├── scraper.py              # Direct Google API scraper
│   ├── apify_scraper.py        # Apify-powered scraper
│   ├── keboola_publisher.py    # Keboola data publisher
│   └── csv_writer.py           # CSV output handler
├── data/                        # Output directory
├── requirements.txt             # Python dependencies
└── .env.example                # Environment variables template
```

## 🏗️ Architecture: 3 Core Components

### 1. Scraper Module (`src/apify_scraper.py`)
Handles fetching Google autocomplete suggestions using Apify platform for reliability.

### 2. Publisher Module (`src/keboola_publisher.py`)
Publishes scraped data to Keboola Storage for public access.

### 3. Orchestrator (`main_apify_keboola.py`)
Coordinates scraping and publishing with progress reporting.

## 🚀 Quick Start

### Option 1: Production Setup (Recommended)

**Prerequisites:**
- Apify account with API token
- Keboola account with Storage token

**Setup:**

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export APIFY_API_TOKEN='your_apify_token'
export KEBOOLA_STORAGE_TOKEN='your_keboola_token'

# Or copy .env.example to .env and fill in your tokens
cp .env.example .env
# Edit .env with your tokens

# Run the scraper
python main_apify_keboola.py
```

**Get Your Tokens:**
- Apify: https://console.apify.com/account/integrations
- Keboola: https://connection.keboola.com/admin/projects

### Option 2: Simple Direct Scraper

```bash
# Install dependencies
pip install -r requirements.txt

# Run direct scraper (may face 403 errors from some IPs)
python main.py
```

### Option 3: Demo Mode

```bash
# See how it works with sample data (no API keys needed)
python demo.py
```

## 📊 Output Formats

### Long Format CSV
```csv
query,suggestion_rank,suggestion_text,scraped_at
i hate,1,i hate my life,2024-11-14T10:30:00
i hate,2,i hate everything,2024-11-14T10:30:00
i hate a,1,i hate ads,2024-11-14T10:30:00
```

### Flat Format CSV
```csv
i hate,i hate a,i hate b,...
i hate my life,i hate ads,i hate being broke,...
i hate everything,i hate ai,i hate being sad,...
```

## 🔧 Customization

Edit `main_apify_keboola.py` to change:

```python
# Change the base query
base_query = "i love"  # instead of "i hate"

# Change the pattern
suffixes = [''] + list(string.ascii_lowercase)  # a-z
# Or use specific suffixes:
suffixes = ['coding', 'python', 'javascript']
```

## 📦 Components Documentation

### ApifyScraper
```python
from src.apify_scraper import ApifyScraper

# Default: Returns top 5 suggestions per query
scraper = ApifyScraper(api_token="your_token")
results = scraper.scrape_pattern("i hate", ['', 'a', 'b', 'c'])
# Returns: {'i hate': [5 suggestions], 'i hate a': [5 suggestions], ...}

# Custom limit (e.g., top 10)
scraper = ApifyScraper(api_token="your_token", max_suggestions=10)
```

### KeboolaPublisher
```python
from src.keboola_publisher import KeboolaPublisher

publisher = KeboolaPublisher(token="your_token")
table_id = publisher.publish(results, incremental=False)
# Publishes to: in.c-google-scraper.google_autocomplete_suggestions
```

### CSVWriter
```python
from src.csv_writer import CSVWriter

writer = CSVWriter(output_dir="data")
writer.write_results(results, "output.csv")
writer.write_flat_results(results, "output_flat.csv")
```

## 🌐 Accessing Published Data

Data published to Keboola can be accessed via:

1. **Keboola UI**: https://connection.keboola.com/admin/projects
2. **Keboola Storage API**: Export tables programmatically
3. **Keboola Data Apps**: Create public dashboards
4. **Data Sharing**: Set up public access via Keboola's sharing features

## 🐛 Troubleshooting

### 403 Forbidden Errors (Direct Scraper)
The direct scraper may face 403 errors from certain IPs (data centers, VPNs).
**Solution**: Use the Apify version (`main_apify_keboola.py`) which bypasses these restrictions.

### Apify Token Issues
- Verify token at: https://console.apify.com/account/integrations
- Check token has not expired
- Ensure sufficient Apify credits

### Keboola Token Issues
- Verify token at: https://connection.keboola.com
- Check token has write permissions
- Ensure bucket can be created/accessed

## 💡 Use Cases

- **SEO Research**: Understand search patterns and user intent
- **Content Ideas**: Generate content topics based on popular searches
- **Sentiment Analysis**: Analyze what people dislike
- **Market Research**: Track changes in search suggestions over time

## 📝 Notes

- **Result Limit**: Default is top 5 suggestions per query (configurable)
- **SDKs Used**:
  - `apify-client` - Official Apify Python SDK
  - `kbcstorage` - Official Keboola Storage Python SDK
  - `requests` - For direct scraping mode
- **Rate Limiting**: Built-in delays (0.5s) to be respectful to APIs
- **Data Freshness**: Google suggestions change based on trends
- **Privacy**: Be mindful when scraping and sharing data
- **Cost**: Apify has usage-based pricing; monitor your consumption

## 🔄 Running Periodically

Set up a cron job or GitHub Action to run the scraper regularly:

```bash
# Cron example (daily at 2 AM)
0 2 * * * cd /path/to/google-scraper && python main_apify_keboola.py
```

## 📄 License

This project is for educational and research purposes. Respect Google's Terms of Service and robots.txt.
