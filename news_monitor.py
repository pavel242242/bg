#!/usr/bin/env python3
"""
News Monitor - Monitor multiple sources for configurable company names.
Supports: NewsAPI.org, Google News RSS, Czech RSS feeds.
Pings you every hour with news and lets you acknowledge them.
"""

import json
import sqlite3
import hashlib
import time
import sys
from datetime import datetime, timedelta
from pathlib import Path
import requests
import schedule

# Configuration
CONFIG_FILE = Path(__file__).parent / "config.json"
DB_FILE = Path(__file__).parent / "news_data.db"


def load_config():
    """Load configuration from config.json"""
    with open(CONFIG_FILE, 'r') as f:
        return json.load(f)


def init_db():
    """Initialize SQLite database for storing news and acknowledgements"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS news_articles (
            id TEXT PRIMARY KEY,
            company TEXT NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            url TEXT NOT NULL,
            source TEXT,
            provider TEXT,
            published_at TEXT,
            fetched_at TEXT NOT NULL,
            acknowledged INTEGER DEFAULT 0,
            acknowledged_at TEXT
        )
    ''')

    conn.commit()
    return conn


def generate_article_id(url):
    """Generate a unique ID for an article based on URL"""
    return hashlib.md5(url.encode()).hexdigest()


# =============================================================================
# NEWS PROVIDERS
# =============================================================================

def fetch_newsapi(api_key, company, max_articles=5):
    """Fetch news from NewsAPI.org"""
    url = "https://newsapi.org/v2/everything"
    from_date = (datetime.utcnow() - timedelta(days=1)).strftime('%Y-%m-%d')

    params = {
        'q': company,
        'apiKey': api_key,
        'language': 'en',
        'sortBy': 'publishedAt',
        'pageSize': max_articles,
        'from': from_date
    }

    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()

        if data.get('status') == 'ok':
            articles = []
            for item in data.get('articles', []):
                articles.append({
                    'title': item.get('title', 'No title'),
                    'description': item.get('description', ''),
                    'url': item.get('url', ''),
                    'source': item.get('source', {}).get('name', 'Unknown'),
                    'published_at': item.get('publishedAt', ''),
                    'provider': 'newsapi',
                })
            return articles
        return []
    except requests.RequestException as e:
        print(f"    NewsAPI error: {e}")
        return []


def parse_rss(url):
    """Parse RSS feed using xml.etree (no external dependencies)"""
    import xml.etree.ElementTree as ET

    try:
        response = requests.get(url, timeout=30, headers={
            'User-Agent': 'Mozilla/5.0 (compatible; NewsBot/1.0)'
        })
        response.raise_for_status()

        root = ET.fromstring(response.content)
        items = []

        # Handle both RSS 2.0 and Atom feeds
        for item in root.findall('.//item'):
            items.append({
                'title': item.findtext('title', ''),
                'link': item.findtext('link', ''),
                'description': item.findtext('description', ''),
                'pubDate': item.findtext('pubDate', ''),
            })

        return items
    except Exception as e:
        return []


def fetch_google_news(company, language='czech', max_articles=5):
    """Fetch news from Google News RSS"""
    import urllib.parse

    configs = {
        'czech': {'hl': 'cs', 'gl': 'CZ', 'ceid': 'CZ:cs'},
        'english': {'hl': 'en-US', 'gl': 'US', 'ceid': 'US:en'},
    }

    all_articles = []

    for lang_name, config in configs.items():
        query = f'"{company}" when:7d'
        params = {
            'q': query,
            'hl': config['hl'],
            'gl': config['gl'],
            'ceid': config['ceid'],
        }
        url = f"https://news.google.com/rss/search?{urllib.parse.urlencode(params)}"

        try:
            items = parse_rss(url)

            for item in items[:max_articles]:
                title = item.get('title', '')
                source = ''
                if ' - ' in title:
                    title, source = title.rsplit(' - ', 1)

                all_articles.append({
                    'title': title,
                    'description': item.get('description', ''),
                    'url': item.get('link', ''),
                    'source': source,
                    'published_at': item.get('pubDate', ''),
                    'provider': f'google_{lang_name}',
                })

            time.sleep(0.5)  # Rate limiting
        except Exception as e:
            print(f"    Google News ({lang_name}) error: {e}")

    return all_articles


def fetch_czech_rss(company, max_per_feed=10):
    """Fetch news from Czech RSS feeds and search for company mentions"""
    feeds = {
        'HN Byznys': 'https://byznys.hn.cz/?m=rss',
        'HN Investice': 'https://investice.hn.cz/?m=rss',
        'Ekonom': 'https://ekonom.cz/?m=rss',
        'iDNES Ekonomika': 'https://servis.idnes.cz/rss.aspx?c=ekonomikah',
        'Aktualne': 'https://www.aktualne.cz/rss/ekonomika/',
        'E15': 'https://www.e15.cz/rss',
    }

    matching_articles = []
    company_lower = company.lower()

    # Also search without diacritics
    diacritics = {'á': 'a', 'č': 'c', 'ď': 'd', 'é': 'e', 'ě': 'e',
                  'í': 'i', 'ň': 'n', 'ó': 'o', 'ř': 'r', 'š': 's',
                  'ť': 't', 'ú': 'u', 'ů': 'u', 'ý': 'y', 'ž': 'z'}
    company_nodiac = company_lower
    for cz, en in diacritics.items():
        company_nodiac = company_nodiac.replace(cz, en)

    for feed_name, feed_url in feeds.items():
        try:
            items = parse_rss(feed_url)

            for item in items[:max_per_feed]:
                title = item.get('title', '')
                description = item.get('description', '')
                text = f"{title} {description}".lower()

                if company_lower in text or company_nodiac in text:
                    matching_articles.append({
                        'title': title,
                        'description': description,
                        'url': item.get('link', ''),
                        'source': feed_name,
                        'published_at': item.get('pubDate', ''),
                        'provider': 'czech_rss',
                    })

        except Exception as e:
            print(f"    {feed_name} error: {e}")

    return matching_articles


# =============================================================================
# DATABASE OPERATIONS
# =============================================================================

def store_articles(conn, company, articles):
    """Store articles in the database, returns count of new articles"""
    cursor = conn.cursor()
    new_count = 0

    for article in articles:
        if not article.get('url'):
            continue

        article_id = generate_article_id(article['url'])

        cursor.execute('SELECT id FROM news_articles WHERE id = ?', (article_id,))
        if cursor.fetchone():
            continue

        cursor.execute('''
            INSERT INTO news_articles (id, company, title, description, url, source, provider, published_at, fetched_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            article_id,
            company,
            article.get('title', 'No title'),
            article.get('description', ''),
            article.get('url', ''),
            article.get('source', 'Unknown'),
            article.get('provider', 'unknown'),
            article.get('published_at', ''),
            datetime.utcnow().isoformat()
        ))
        new_count += 1

    conn.commit()
    return new_count


def get_unacknowledged_news(conn, company=None):
    """Get all unacknowledged news articles"""
    cursor = conn.cursor()

    if company:
        cursor.execute('''
            SELECT id, company, title, description, url, source, published_at, provider
            FROM news_articles
            WHERE acknowledged = 0 AND company = ?
            ORDER BY fetched_at DESC
        ''', (company,))
    else:
        cursor.execute('''
            SELECT id, company, title, description, url, source, published_at, provider
            FROM news_articles
            WHERE acknowledged = 0
            ORDER BY fetched_at DESC
        ''')

    return cursor.fetchall()


def acknowledge_article(conn, article_id):
    """Mark an article as acknowledged"""
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE news_articles
        SET acknowledged = 1, acknowledged_at = ?
        WHERE id = ?
    ''', (datetime.utcnow().isoformat(), article_id))
    conn.commit()
    return cursor.rowcount > 0


def acknowledge_all(conn, company=None):
    """Mark all articles as acknowledged"""
    cursor = conn.cursor()

    if company:
        cursor.execute('''
            UPDATE news_articles
            SET acknowledged = 1, acknowledged_at = ?
            WHERE acknowledged = 0 AND company = ?
        ''', (datetime.utcnow().isoformat(), company))
    else:
        cursor.execute('''
            UPDATE news_articles
            SET acknowledged = 1, acknowledged_at = ?
            WHERE acknowledged = 0
        ''', (datetime.utcnow().isoformat(),))

    conn.commit()
    return cursor.rowcount


# =============================================================================
# NEWS CHECK
# =============================================================================

def check_news():
    """Check for new news for all configured companies from all sources"""
    config = load_config()
    conn = init_db()

    providers_enabled = config.get('providers', ['newsapi', 'google_news', 'czech_rss'])

    total_new = 0
    for company in config['companies']:
        print(f"\n📡 Checking: {company}")
        company_articles = []

        # NewsAPI
        if 'newsapi' in providers_enabled and config.get('news_api_key'):
            print(f"  [NewsAPI]", end=" ")
            articles = fetch_newsapi(
                config['news_api_key'],
                company,
                config.get('max_articles_per_company', 5)
            )
            company_articles.extend(articles)
            print(f"found {len(articles)}")

        # Google News RSS
        if 'google_news' in providers_enabled:
            print(f"  [Google News]", end=" ")
            articles = fetch_google_news(
                company,
                max_articles=config.get('max_articles_per_company', 5)
            )
            company_articles.extend(articles)
            print(f"found {len(articles)}")

        # Czech RSS feeds
        if 'czech_rss' in providers_enabled:
            print(f"  [Czech RSS]", end=" ")
            articles = fetch_czech_rss(company)
            company_articles.extend(articles)
            print(f"found {len(articles)}")

        # Store all articles
        new_count = store_articles(conn, company, company_articles)
        total_new += new_count
        print(f"  → {new_count} new articles stored")

    print(f"\n{'='*60}")
    print(f"Total new articles: {total_new}")
    print_news_summary(conn)
    conn.close()


def print_news_summary(conn):
    """Print a summary of unacknowledged news"""
    articles = get_unacknowledged_news(conn)

    if not articles:
        print("\n✓ No new unacknowledged news!")
        return

    print(f"\n{'='*60}")
    print(f"📰 NEWS ALERT - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"{'='*60}")
    print(f"You have {len(articles)} unacknowledged article(s):\n")

    for i, row in enumerate(articles, 1):
        id, company, title, description, url, source, published_at, provider = row
        print(f"{i}. [{company}] {title}")
        print(f"   Source: {source} ({provider})")
        if description:
            desc_preview = description[:100] + "..." if len(description) > 100 else description
            print(f"   {desc_preview}")
        print(f"   ID: {id[:8]}...")
        print()

    print(f"{'='*60}")
    print("Commands: ack <id> | ack-all | list")
    print(f"{'='*60}\n")


# =============================================================================
# SCHEDULER
# =============================================================================

def run_scheduler():
    """Run the scheduler for periodic news checks"""
    config = load_config()
    interval = config.get('check_interval_minutes', 60)
    providers = config.get('providers', ['newsapi', 'google_news', 'czech_rss'])

    print(f"🔔 News Monitor Started!")
    print(f"   Companies: {', '.join(config['companies'])}")
    print(f"   Providers: {', '.join(providers)}")
    print(f"   Interval: every {interval} minutes")
    print(f"   Press Ctrl+C to stop\n")

    check_news()
    schedule.every(interval).minutes.do(check_news)

    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n👋 News Monitor stopped.")


# =============================================================================
# CLI
# =============================================================================

def show_help():
    print("""
News Monitor - Multi-source company news monitoring

Usage:
  python news_monitor.py              Start monitor (hourly checks)
  python news_monitor.py check        Check news once
  python news_monitor.py list         List unacknowledged news
  python news_monitor.py ack <id>     Acknowledge article
  python news_monitor.py ack-all      Acknowledge all articles
  python news_monitor.py companies    List configured companies
  python news_monitor.py add <name>   Add company to monitor
  python news_monitor.py remove <name> Remove company
  python news_monitor.py help         Show this help

Sources:
  - NewsAPI.org (requires API key)
  - Google News RSS (free, Czech + English)
  - Czech RSS feeds (HN, iDNES, Aktualne, E15, Ekonom)

Config (config.json):
  - companies: List of company names
  - providers: ["newsapi", "google_news", "czech_rss"]
  - check_interval_minutes: Check frequency (default: 60)
""")


def list_companies():
    config = load_config()
    print("\nConfigured companies:")
    for i, company in enumerate(config['companies'], 1):
        print(f"  {i}. {company}")
    print()


def add_company(company_name):
    config = load_config()
    if company_name in config['companies']:
        print(f"'{company_name}' is already in the list.")
        return
    config['companies'].append(company_name)
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)
    print(f"✓ Added '{company_name}' to monitoring list.")


def remove_company(company_name):
    config = load_config()
    if company_name not in config['companies']:
        print(f"'{company_name}' is not in the list.")
        return
    config['companies'].remove(company_name)
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)
    print(f"✓ Removed '{company_name}' from monitoring list.")


def main():
    if len(sys.argv) < 2:
        run_scheduler()
        return

    command = sys.argv[1].lower()

    if command == 'help':
        show_help()
    elif command == 'check':
        check_news()
    elif command == 'list':
        conn = init_db()
        print_news_summary(conn)
        conn.close()
    elif command == 'ack':
        if len(sys.argv) < 3:
            print("Usage: python news_monitor.py ack <article_id>")
            return
        article_id = sys.argv[2]
        conn = init_db()
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM news_articles WHERE id LIKE ?', (f'{article_id}%',))
        matches = cursor.fetchall()
        if len(matches) == 0:
            print(f"No article found with ID starting with '{article_id}'")
        elif len(matches) > 1:
            print(f"Multiple articles match '{article_id}'. Be more specific.")
        else:
            if acknowledge_article(conn, matches[0][0]):
                print(f"✓ Article {matches[0][0][:8]}... acknowledged")
        conn.close()
    elif command == 'ack-all':
        conn = init_db()
        company = sys.argv[2] if len(sys.argv) > 2 else None
        count = acknowledge_all(conn, company)
        print(f"✓ Acknowledged {count} article(s)")
        conn.close()
    elif command == 'companies':
        list_companies()
    elif command == 'add':
        if len(sys.argv) < 3:
            print("Usage: python news_monitor.py add <company_name>")
            return
        add_company(sys.argv[2])
    elif command == 'remove':
        if len(sys.argv) < 3:
            print("Usage: python news_monitor.py remove <company_name>")
            return
        remove_company(sys.argv[2])
    else:
        print(f"Unknown command: {command}")
        show_help()


if __name__ == '__main__':
    main()
