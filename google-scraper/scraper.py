"""
Google Autocomplete Scraper using Apify

Fetches Google autocomplete suggestions for character-based queries.
Generates queries like: "i hate", "i hate a", "i hate b", ..., "i hate z"
"""

import string
from typing import List, Dict
from datetime import datetime
from apify_client import ApifyClient


class GoogleSuggestionsScraper:
    """Scrapes Google autocomplete suggestions using Apify"""

    def __init__(self, apify_token: str):
        """
        Initialize scraper with Apify credentials

        Args:
            apify_token: Apify API token
        """
        self.client = ApifyClient(apify_token)
        self.base_query = "i hate"

    def generate_queries(self) -> List[str]:
        """
        Generate all search queries

        Returns:
            List of queries: ["i hate", "i hate a", "i hate b", ..., "i hate z"]
        """
        queries = [self.base_query]  # Start with base query

        # Add character variations
        for char in string.ascii_lowercase:
            queries.append(f"{self.base_query} {char}")

        return queries

    def scrape_suggestions(self, query: str, max_results: int = 10) -> List[str]:
        """
        Scrape Google autocomplete suggestions for a single query

        Args:
            query: Search query to get suggestions for
            max_results: Maximum number of suggestions to return

        Returns:
            List of suggestion strings
        """
        try:
            # Use Apify's Google Search Scraper
            # Actor ID: apify/google-search-scraper
            run_input = {
                "queries": query,
                "maxPagesPerQuery": 1,
                "resultsPerPage": 10,
                "mobileResults": False,
                "languageCode": "en",
                "includeUnfilteredResults": False,
            }

            # Run the actor and wait for it to finish
            run = self.client.actor("apify/google-search-scraper").call(run_input=run_input)

            # Fetch results from the dataset
            suggestions = []
            for item in self.client.dataset(run["defaultDatasetId"]).iterate_items():
                # Extract search queries from results
                if "searchQuery" in item:
                    suggestions.append(item["searchQuery"]["term"])
                elif "organicResults" in item:
                    # Sometimes suggestions come in organic results
                    for result in item["organicResults"][:max_results]:
                        if "title" in result:
                            suggestions.append(result["title"])

            return suggestions[:max_results]

        except Exception as e:
            print(f"Error scraping query '{query}': {str(e)}")
            return []

    def scrape_all(self) -> List[Dict]:
        """
        Scrape suggestions for all character variations

        Returns:
            List of dictionaries with query, suggestions, and timestamp
        """
        queries = self.generate_queries()
        results = []

        print(f"Starting scrape for {len(queries)} queries...")

        for i, query in enumerate(queries, 1):
            print(f"[{i}/{len(queries)}] Scraping: {query}")

            suggestions = self.scrape_suggestions(query)

            result = {
                "query": query,
                "suggestions": "|".join(suggestions) if suggestions else "",
                "suggestion_count": len(suggestions),
                "timestamp": datetime.utcnow().isoformat()
            }

            results.append(result)
            print(f"  → Found {len(suggestions)} suggestions")

        print(f"\nCompleted! Scraped {len(results)} queries with {sum(r['suggestion_count'] for r in results)} total suggestions")

        return results


def main():
    """Test the scraper standalone"""
    import os
    from dotenv import load_dotenv

    load_dotenv()

    apify_token = os.getenv("APIFY_API_TOKEN")
    if not apify_token:
        raise ValueError("APIFY_API_TOKEN not found in environment")

    scraper = GoogleSuggestionsScraper(apify_token)
    results = scraper.scrape_all()

    print("\nSample results:")
    for result in results[:3]:
        print(f"  {result}")


if __name__ == "__main__":
    main()
