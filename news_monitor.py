#!/usr/bin/env python3
"""
News Monitor - Monitor newsapi.org for configurable company names.
Pings you every hour with news and lets you acknowledge them.
"""

import json
import sqlite3
import hashlib
import time
import sys
import os
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
            published_at TEXT,
            fetched_at TEXT NOT NULL,
            acknowledged INTEGER DEFAULT 0,
            acknowledged_at TEXT
        )
    ''')

    conn.commit()
    return conn


def generate_article_id(article):
    """Generate a unique ID for an article based on URL"""
    return hashlib.md5(article['url'].encode()).hexdigest()


def fetch_news(api_key, company, max_articles=5):
    """Fetch news for a specific company from News API"""
    url = "https://newsapi.org/v2/everything"

    # Search for news from the last 24 hours
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
            return data.get('articles', [])
        else:
            print(f"API Error: {data.get('message', 'Unknown error')}")
            return []
    except requests.RequestException as e:
        print(f"Request failed: {e}")
        return []


def store_articles(conn, company, articles):
    """Store articles in the database, returns count of new articles"""
    cursor = conn.cursor()
    new_count = 0

    for article in articles:
        article_id = generate_article_id(article)

        # Check if article already exists
        cursor.execute('SELECT id FROM news_articles WHERE id = ?', (article_id,))
        if cursor.fetchone():
            continue

        cursor.execute('''
            INSERT INTO news_articles (id, company, title, description, url, source, published_at, fetched_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            article_id,
            company,
            article.get('title', 'No title'),
            article.get('description', ''),
            article.get('url', ''),
            article.get('source', {}).get('name', 'Unknown'),
            article.get('publishedAt', ''),
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
            SELECT id, company, title, description, url, source, published_at
            FROM news_articles
            WHERE acknowledged = 0 AND company = ?
            ORDER BY published_at DESC
        ''', (company,))
    else:
        cursor.execute('''
            SELECT id, company, title, description, url, source, published_at
            FROM news_articles
            WHERE acknowledged = 0
            ORDER BY published_at DESC
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
    """Mark all articles as acknowledged, optionally filtered by company"""
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

    for i, (id, company, title, description, url, source, published_at) in enumerate(articles, 1):
        print(f"{i}. [{company}] {title}")
        print(f"   Source: {source}")
        if description:
            desc_preview = description[:100] + "..." if len(description) > 100 else description
            print(f"   {desc_preview}")
        print(f"   ID: {id[:8]}...")
        print()

    print(f"{'='*60}")
    print("Use 'python news_monitor.py ack <id>' to acknowledge")
    print("Use 'python news_monitor.py ack-all' to acknowledge all")
    print(f"{'='*60}\n")


def check_news():
    """Check for new news for all configured companies"""
    config = load_config()
    conn = init_db()

    total_new = 0
    for company in config['companies']:
        print(f"Checking news for: {company}...")
        articles = fetch_news(
            config['news_api_key'],
            company,
            config.get('max_articles_per_company', 5)
        )
        new_count = store_articles(conn, company, articles)
        total_new += new_count
        print(f"  Found {len(articles)} articles, {new_count} new")

    print(f"\nTotal new articles: {total_new}")
    print_news_summary(conn)
    conn.close()


def run_scheduler():
    """Run the scheduler for periodic news checks"""
    config = load_config()
    interval = config.get('check_interval_minutes', 60)

    print(f"🔔 News Monitor Started!")
    print(f"   Monitoring: {', '.join(config['companies'])}")
    print(f"   Check interval: every {interval} minutes")
    print(f"   Press Ctrl+C to stop\n")

    # Run immediately on start
    check_news()

    # Schedule periodic checks
    schedule.every(interval).minutes.do(check_news)

    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n👋 News Monitor stopped.")


def show_help():
    """Show help message"""
    print("""
News Monitor - Monitor newsapi.org for company news

Usage:
  python news_monitor.py                  Start the monitor (runs every hour)
  python news_monitor.py check            Check for news once
  python news_monitor.py list             List unacknowledged news
  python news_monitor.py ack <id>         Acknowledge a specific article
  python news_monitor.py ack-all          Acknowledge all articles
  python news_monitor.py ack-all <company> Acknowledge all for a company
  python news_monitor.py companies        List configured companies
  python news_monitor.py add <company>    Add a company to monitor
  python news_monitor.py remove <company> Remove a company from monitoring
  python news_monitor.py help             Show this help message

Configuration:
  Edit config.json to modify:
  - companies: List of company names to monitor
  - check_interval_minutes: How often to check (default: 60)
  - max_articles_per_company: Max articles per company per check
""")


def list_companies():
    """List configured companies"""
    config = load_config()
    print("\nConfigured companies:")
    for i, company in enumerate(config['companies'], 1):
        print(f"  {i}. {company}")
    print()


def add_company(company_name):
    """Add a company to the monitoring list"""
    config = load_config()

    if company_name in config['companies']:
        print(f"'{company_name}' is already in the list.")
        return

    config['companies'].append(company_name)

    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)

    print(f"✓ Added '{company_name}' to monitoring list.")


def remove_company(company_name):
    """Remove a company from the monitoring list"""
    config = load_config()

    if company_name not in config['companies']:
        print(f"'{company_name}' is not in the list.")
        return

    config['companies'].remove(company_name)

    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)

    print(f"✓ Removed '{company_name}' from monitoring list.")


def main():
    """Main entry point"""
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

        # Support partial ID matching
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM news_articles WHERE id LIKE ?', (f'{article_id}%',))
        matches = cursor.fetchall()

        if len(matches) == 0:
            print(f"No article found with ID starting with '{article_id}'")
        elif len(matches) > 1:
            print(f"Multiple articles match '{article_id}'. Please be more specific.")
        else:
            full_id = matches[0][0]
            if acknowledge_article(conn, full_id):
                print(f"✓ Article {full_id[:8]}... acknowledged")
            else:
                print(f"Failed to acknowledge article")

        conn.close()

    elif command == 'ack-all':
        conn = init_db()
        company = sys.argv[2] if len(sys.argv) > 2 else None
        count = acknowledge_all(conn, company)

        if company:
            print(f"✓ Acknowledged {count} article(s) for {company}")
        else:
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
