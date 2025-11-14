#!/usr/bin/env python3
"""
Google Character Suggestions Scraper - Main Orchestrator

Orchestrates the scraping of Google autocomplete suggestions
and uploading results to Keboola Storage.

Usage:
    python main.py

Environment variables required:
    APIFY_API_TOKEN - Apify API token
    KEBOOLA_TOKEN - Keboola Storage API token
    KEBOOLA_URL - Keboola Storage URL (optional, defaults to connection.keboola.com)
"""

import os
import sys
from dotenv import load_dotenv
from scraper import GoogleSuggestionsScraper
from keboola_writer import KeboolaWriter


def validate_env():
    """Validate required environment variables"""
    required_vars = ["APIFY_API_TOKEN", "KEBOOLA_TOKEN"]
    missing = [var for var in required_vars if not os.getenv(var)]

    if missing:
        print("❌ Missing required environment variables:")
        for var in missing:
            print(f"  - {var}")
        print("\nPlease set these in your .env file or environment")
        sys.exit(1)

    print("✓ Environment variables validated")


def main():
    """Main orchestration function"""
    print("=" * 60)
    print("Google Character Suggestions Scraper")
    print("=" * 60)
    print()

    # Load environment variables
    load_dotenv()
    validate_env()

    # Get credentials
    apify_token = os.getenv("APIFY_API_TOKEN")
    keboola_token = os.getenv("KEBOOLA_TOKEN")
    keboola_url = os.getenv("KEBOOLA_URL", "https://connection.keboola.com")

    try:
        # Step 1: Scrape Google suggestions
        print("Step 1: Scraping Google autocomplete suggestions")
        print("-" * 60)
        scraper = GoogleSuggestionsScraper(apify_token)
        results = scraper.scrape_all()
        print()

        if not results:
            print("❌ No data scraped. Exiting.")
            sys.exit(1)

        # Step 2: Upload to Keboola
        print("Step 2: Uploading to Keboola Storage")
        print("-" * 60)
        writer = KeboolaWriter(keboola_token, keboola_url)
        table_id = writer.upload_to_keboola(results)
        print()

        # Step 3: Success summary
        print("=" * 60)
        print("✓ COMPLETED SUCCESSFULLY")
        print("=" * 60)
        print(f"Queries scraped: {len(results)}")
        print(f"Total suggestions: {sum(r['suggestion_count'] for r in results)}")
        print(f"Keboola table: {table_id}")
        print()
        print("Access your data in Keboola Storage:")
        print(f"  → {keboola_url}")
        print(f"  → Table: {table_id}")
        print()

    except KeyboardInterrupt:
        print("\n\n❌ Interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
