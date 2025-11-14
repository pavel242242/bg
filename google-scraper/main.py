#!/usr/bin/env python3
"""
Google Autocomplete Scraper - Main Script
Scrapes "i hate [letter]" suggestions for all letters a-z
"""
import string
from src.scraper import GoogleScraper
from src.csv_writer import CSVWriter


def main():
    """Main orchestrator for the scraping process"""

    print("=" * 60)
    print("Google Autocomplete Scraper")
    print("Pattern: 'i hate [letter]' for a-z")
    print("=" * 60)

    # Initialize components
    scraper = GoogleScraper(delay=0.5)  # 0.5s delay between requests
    writer = CSVWriter(output_dir="data")

    # Define the base query and suffixes
    base_query = "i hate"
    suffixes = [''] + list(string.ascii_lowercase)  # '', 'a', 'b', ..., 'z'

    print(f"\nStarting scrape for {len(suffixes)} queries...")
    print(f"Base query: '{base_query}'")
    print(f"Suffixes: {suffixes}\n")

    # Scrape suggestions
    results = scraper.scrape_pattern(base_query, suffixes)

    # Display summary
    total_suggestions = sum(len(sugs) for sugs in results.values())
    print(f"\n{'=' * 60}")
    print(f"Scraping complete!")
    print(f"Total queries: {len(results)}")
    print(f"Total suggestions: {total_suggestions}")
    print(f"{'=' * 60}\n")

    # Write results to CSV (both formats)
    filepath_long = writer.write_results(results, "i_hate_suggestions.csv")
    filepath_flat = writer.write_flat_results(results, "i_hate_suggestions_flat.csv")

    print(f"\n✓ Files created:")
    print(f"  - {filepath_long}")
    print(f"  - {filepath_flat}")
    print(f"\nDone! Results are publicly accessible in the data/ directory.")


if __name__ == "__main__":
    main()
