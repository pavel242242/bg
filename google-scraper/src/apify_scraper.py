"""
Apify-based Google Autocomplete Scraper
Uses Apify platform to scrape Google suggestions reliably
"""
from apify_client import ApifyClient
from typing import List, Dict
import time
import os


class ApifyScraper:
    """Scraper using Apify platform for Google autocomplete"""

    def __init__(self, api_token: str = None):
        """
        Initialize Apify scraper

        Args:
            api_token: Apify API token (or set APIFY_API_TOKEN env var)
        """
        self.api_token = api_token or os.getenv('APIFY_API_TOKEN')
        if not self.api_token:
            raise ValueError(
                "Apify API token required. Set APIFY_API_TOKEN env var or pass api_token parameter.\n"
                "Get your token at: https://console.apify.com/account/integrations"
            )

        self.client = ApifyClient(self.api_token)

    def get_suggestions(self, query: str) -> List[str]:
        """
        Fetch autocomplete suggestions for a single query using Apify

        Args:
            query: Search query to get suggestions for

        Returns:
            List of suggestion strings
        """
        try:
            # Using a simple HTTP request actor to call Google Suggest API
            # This is more reliable than direct requests
            run_input = {
                "url": f"https://suggestqueries.google.com/complete/search?client=chrome&q={query}&hl=en",
                "method": "GET",
                "headers": {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                }
            }

            # Run the actor and wait for results
            run = self.client.actor("apify/http-request").call(run_input=run_input)

            # Get the results from dataset
            dataset_items = list(self.client.dataset(run["defaultDatasetId"]).iterate_items())

            if dataset_items and len(dataset_items) > 0:
                response_data = dataset_items[0]

                # Parse the response body (it's JSON)
                if 'body' in response_data:
                    import json
                    body = response_data['body']
                    data = json.loads(body) if isinstance(body, str) else body

                    # Google returns [query, [suggestions], ...]
                    if isinstance(data, list) and len(data) > 1:
                        return data[1]

            return []

        except Exception as e:
            print(f"Error fetching suggestions for '{query}': {e}")
            return []

    def scrape_pattern(self, base_query: str, suffixes: List[str]) -> Dict[str, List[str]]:
        """
        Scrape suggestions for a base query + each suffix

        Args:
            base_query: Base search query (e.g., "i hate")
            suffixes: List of suffixes to append (e.g., ['', 'a', 'b', ...])

        Returns:
            Dictionary mapping query -> list of suggestions
        """
        results = {}

        for i, suffix in enumerate(suffixes):
            query = f"{base_query} {suffix}".strip()
            print(f"[{i+1}/{len(suffixes)}] Fetching suggestions for: '{query}'")

            suggestions = self.get_suggestions(query)
            results[query] = suggestions

            print(f"  ✓ Found {len(suggestions)} suggestions")

            # Small delay to be respectful
            if i < len(suffixes) - 1:
                time.sleep(0.5)

        return results

    def scrape_pattern_parallel(self, base_query: str, suffixes: List[str]) -> Dict[str, List[str]]:
        """
        Scrape suggestions in parallel using Apify's batch processing

        Args:
            base_query: Base search query
            suffixes: List of suffixes

        Returns:
            Dictionary mapping query -> list of suggestions
        """
        print("Using parallel scraping mode...")

        # Prepare all queries
        queries = [f"{base_query} {suffix}".strip() for suffix in suffixes]

        # Create a batch request dataset
        requests = []
        for query in queries:
            requests.append({
                "url": f"https://suggestqueries.google.com/complete/search?client=chrome&q={query}&hl=en",
                "uniqueKey": query
            })

        try:
            # Run Web Scraper actor with all requests at once
            run_input = {
                "startUrls": [{"url": req["url"], "userData": {"query": req["uniqueKey"]}} for req in requests],
                "pageFunction": """
                    async function pageFunction(context) {
                        return {
                            query: context.request.userData.query,
                            body: context.body
                        };
                    }
                """
            }

            print(f"Starting Apify run for {len(queries)} queries...")
            run = self.client.actor("apify/web-scraper").call(run_input=run_input, timeout_secs=300)

            # Get results
            dataset_items = list(self.client.dataset(run["defaultDatasetId"]).iterate_items())

            results = {}
            for item in dataset_items:
                query = item.get('query', '')
                body = item.get('body', '')

                try:
                    import json
                    data = json.loads(body) if isinstance(body, str) else body
                    suggestions = data[1] if isinstance(data, list) and len(data) > 1 else []
                    results[query] = suggestions
                except:
                    results[query] = []

            # Fill in any missing queries with empty lists
            for query in queries:
                if query not in results:
                    results[query] = []

            return results

        except Exception as e:
            print(f"Error in parallel scraping: {e}")
            print("Falling back to sequential scraping...")
            return self.scrape_pattern(base_query, suffixes)
