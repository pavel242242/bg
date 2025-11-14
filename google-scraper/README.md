# Google Character Suggestions Scraper

A simple, functional Google autocomplete scraper that collects suggestions for character-based queries and stores them in Keboola Storage as publicly accessible CSV.

## Overview

This tool scrapes Google autocomplete suggestions for the query pattern:
- `"i hate"`
- `"i hate a"`
- `"i hate b"`
- ...
- `"i hate z"`

**Total: 27 queries** (base + 26 alphabet characters)

## Architecture

Simple, modular design with 3 components:

```
┌─────────────┐      ┌──────────────────┐      ┌─────────────────┐
│   main.py   │─────▶│   scraper.py     │─────▶│ keboola_writer  │
│ Orchestrator│      │ Apify Integration│      │ Data Storage    │
└─────────────┘      └──────────────────┘      └─────────────────┘
```

### Components

1. **`scraper.py`** - Apify-based scraping engine
   - Generates character queries
   - Uses Apify Google Search Scraper
   - Returns structured data

2. **`keboola_writer.py`** - Keboola Storage integration
   - Writes data to Keboola Storage
   - Creates/updates tables automatically
   - Provides public access configuration

3. **`main.py`** - Simple orchestrator
   - Coordinates scraping → storage pipeline
   - Validates environment
   - Provides progress feedback

## Setup

### Prerequisites

- Python 3.9+
- Apify account ([sign up](https://apify.com))
- Keboola account ([sign up](https://www.keboola.com))

### Installation

1. **Clone and navigate**
   ```bash
   cd google-scraper
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   ```

4. **Set up credentials**

   Get your **Apify API Token**:
   - Go to [Apify Console](https://console.apify.com/account/integrations)
   - Copy your API token
   - Add to `.env`: `APIFY_API_TOKEN=your_token`

   Get your **Keboola Storage Token**:
   - Go to Keboola Connection → Storage → API Tokens
   - Create a new token with write permissions
   - Add to `.env`: `KEBOOLA_TOKEN=your_token`

## Usage

### Run the scraper

```bash
python main.py
```

### Output

Data is stored in Keboola Storage:
- **Bucket**: `in.c-google-suggestions`
- **Table**: `google_hate_suggestions`

**CSV Structure:**
```csv
query,suggestions,suggestion_count,timestamp
"i hate","monday|my job|mornings",3,"2025-11-14T10:30:00"
"i hate a","apples|airplanes",2,"2025-11-14T10:30:15"
...
```

### Test individual components

Test scraper only:
```bash
python scraper.py
```

Test Keboola writer only:
```bash
python keboola_writer.py
```

## Public Access

To make the CSV publicly accessible:

1. **Via Keboola Data Catalog**:
   - Go to Keboola → Data Catalog
   - Find your table: `in.c-google-suggestions.google_hate_suggestions`
   - Enable public sharing

2. **Via Export to Cloud Storage**:
   - Create a Keboola Writer component (e.g., Google Sheets, AWS S3)
   - Schedule automatic exports
   - Share the public URL

## Project Structure

```
google-scraper/
├── main.py              # Main orchestrator
├── scraper.py           # Apify scraping logic
├── keboola_writer.py    # Keboola Storage integration
├── requirements.txt     # Python dependencies
├── .env.example         # Environment template
└── README.md           # This file
```

## Tech Stack

- **apify-client** - Official Apify SDK for web scraping
- **kbcstorage** - Official Keboola Storage SDK
- **pandas** - Data manipulation and CSV handling
- **python-dotenv** - Environment configuration

## Configuration

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `APIFY_API_TOKEN` | Yes | Apify API token from console.apify.com |
| `KEBOOLA_TOKEN` | Yes | Keboola Storage API token |
| `KEBOOLA_URL` | No | Keboola API endpoint (default: connection.keboola.com) |

### Customization

**Change the base query:**
```python
# In scraper.py
self.base_query = "i hate"  # Change to your query
```

**Add more character patterns:**
```python
# In scraper.py, modify generate_queries()
for char in string.ascii_lowercase + string.digits:
    queries.append(f"{self.base_query} {char}")
```

## Troubleshooting

**Apify errors:**
- Check your API token is valid
- Verify you have enough Apify credits
- Check rate limits on your Apify plan

**Keboola errors:**
- Verify token has write permissions
- Check the correct KEBOOLA_URL for your region
- Ensure bucket/table names are valid

**No suggestions found:**
- Google may be rate limiting
- Try adding delays between queries
- Check Apify actor logs for details

## License

MIT

## Contributing

Feel free to open issues or submit pull requests!
