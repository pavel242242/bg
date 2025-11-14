"""
Google Autocomplete Scraper Module
Fetches autocomplete suggestions from Google's API
"""
import requests
from typing import List, Optional
import time


class GoogleScraper:
    """Simple scraper for Google autocomplete suggestions"""

    def __init__(self, delay: float = 0.5):
        """
        Initialize scraper

        Args:
            delay: Delay between requests in seconds to be respectful
        """
        self.delay = delay
        self.base_url = "https://suggestqueries.google.com/complete/search"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Referer': 'https://www.google.com/',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin'
        })

    def get_suggestions(self, query: str) -> List[str]:
        """
        Fetch autocomplete suggestions for a query

        Args:
            query: Search query to get suggestions for

        Returns:
            List of suggestion strings
        """
        params = {
            'client': 'chrome',
            'q': query,
            'hl': 'en'
        }

        try:
            response = self.session.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()

            # Google returns JSON array: [query, [suggestions], ...]
            data = response.json()
            suggestions = data[1] if len(data) > 1 else []

            time.sleep(self.delay)  # Be respectful to the API
            return suggestions

        except Exception as e:
            print(f"Error fetching suggestions for '{query}': {e}")
            return []

    def scrape_pattern(self, base_query: str, suffixes: List[str]) -> dict:
        """
        Scrape suggestions for a base query + each suffix

        Args:
            base_query: Base search query (e.g., "i hate")
            suffixes: List of suffixes to append (e.g., ['', 'a', 'b', ...])

        Returns:
            Dictionary mapping query -> list of suggestions
        """
        results = {}

        for suffix in suffixes:
            query = f"{base_query} {suffix}".strip()
            print(f"Fetching suggestions for: '{query}'")
            suggestions = self.get_suggestions(query)
            results[query] = suggestions
            print(f"  Found {len(suggestions)} suggestions")

        return results
