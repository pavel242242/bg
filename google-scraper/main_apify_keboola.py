#!/usr/bin/env python3
"""
Google Autocomplete Scraper - Apify + Keboola Version
Scrapes "i hate [letter]" suggestions using Apify and publishes to Keboola
"""
import string
import sys
from src.apify_scraper import ApifyScraper
from src.keboola_publisher import KeboolaPublisher
from src.csv_writer import CSVWriter


def main():
    """Main orchestrator using Apify for scraping and Keboola for publishing"""

    print("=" * 70)
    print("Google Autocomplete Scraper - Apify + Keboola Edition")
    print("Pattern: 'i hate [letter]' for a-z")
    print("=" * 70)

    # Check for required environment variables
    import os
    apify_token = os.getenv('APIFY_API_TOKEN')
    keboola_token = os.getenv('KEBOOLA_STORAGE_TOKEN')

    if not apify_token:
        print("\n❌ Error: APIFY_API_TOKEN environment variable not set")
        print("\nTo fix this:")
        print("1. Get your API token at: https://console.apify.com/account/integrations")
        print("2. Set the environment variable:")
        print("   export APIFY_API_TOKEN='your-token-here'")
        print("\nOr pass it directly in the code.")
        return 1

    if not keboola_token:
        print("\n⚠️  Warning: KEBOOLA_STORAGE_TOKEN not set - data will only be saved locally")
        print("\nTo enable Keboola publishing:")
        print("1. Get your token at: https://connection.keboola.com")
        print("2. Set the environment variable:")
        print("   export KEBOOLA_STORAGE_TOKEN='your-token-here'")
        print("\nContinuing without Keboola publishing...\n")
        use_keboola = False
    else:
        use_keboola = True

    try:
        # Initialize scraper
        print("\n[1/4] Initializing Apify scraper...")
        scraper = ApifyScraper(api_token=apify_token)
        print("✓ Apify scraper ready")

        # Initialize CSV writer (for local backup)
        writer = CSVWriter(output_dir="data")

        # Define the scraping pattern
        base_query = "i hate"
        suffixes = [''] + list(string.ascii_lowercase)  # '', 'a', 'b', ..., 'z'

        print(f"\n[2/4] Starting scrape...")
        print(f"  Base query: '{base_query}'")
        print(f"  Queries to scrape: {len(suffixes)}")
        print(f"  Mode: Sequential (one by one)\n")

        # Scrape suggestions
        results = scraper.scrape_pattern(base_query, suffixes)

        # Display summary
        total_suggestions = sum(len(sugs) for sugs in results.values())
        print(f"\n{'=' * 70}")
        print(f"[3/4] Scraping complete!")
        print(f"  Total queries: {len(results)}")
        print(f"  Total suggestions: {total_suggestions}")
        print(f"  Average per query: {total_suggestions / len(results):.1f}")
        print(f"{'=' * 70}\n")

        # Save locally
        print("[4/4] Saving results...")
        filepath_long = writer.write_results(results, "i_hate_apify_suggestions.csv")
        filepath_flat = writer.write_flat_results(results, "i_hate_apify_suggestions_flat.csv")

        print(f"\n✓ Local files created:")
        print(f"  - {filepath_long}")
        print(f"  - {filepath_flat}")

        # Publish to Keboola if token is available
        if use_keboola:
            try:
                print("\n")
                publisher = KeboolaPublisher(token=keboola_token)
                table_id = publisher.publish(results, incremental=False)

                print(f"\n✓ Data published to Keboola!")
                print(publisher.get_public_url(table_id))

            except Exception as e:
                print(f"\n⚠️  Keboola publishing failed: {e}")
                print("Data is still available in local CSV files.")

        print("\n" + "=" * 70)
        print("Done! ✨")
        print("=" * 70)

        return 0

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
