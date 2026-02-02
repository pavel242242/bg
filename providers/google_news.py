#!/usr/bin/env python3
"""
Google News RSS Provider
Fetches news from Google News RSS feeds with Czech and English support.
"""

import feedparser
import urllib.parse
import time
from typing import List, Dict, Optional


class GoogleNewsProvider:
    """Google News RSS feed provider."""

    BASE_URL = "https://news.google.com/rss/search"

    CONFIGS = {
        'czech': {'hl': 'cs', 'gl': 'CZ', 'ceid': 'CZ:cs'},
        'english': {'hl': 'en-US', 'gl': 'US', 'ceid': 'US:en'},
        'german': {'hl': 'de', 'gl': 'DE', 'ceid': 'DE:de'},
        'slovak': {'hl': 'sk', 'gl': 'SK', 'ceid': 'SK:sk'},
    }

    def __init__(self, delay: float = 1.0):
        self.delay = delay
        self.last_request = 0

    def _rate_limit(self):
        elapsed = time.time() - self.last_request
        if elapsed < self.delay:
            time.sleep(self.delay - elapsed)
        self.last_request = time.time()

    def _build_url(self, query: str, language: str = 'czech', when: str = '7d') -> str:
        config = self.CONFIGS.get(language, self.CONFIGS['czech'])
        full_query = f'{query} when:{when}' if when else query

        params = {
            'q': full_query,
            'hl': config['hl'],
            'gl': config['gl'],
            'ceid': config['ceid'],
        }
        return f"{self.BASE_URL}?{urllib.parse.urlencode(params)}"

    def fetch_news(
        self,
        query: str,
        language: str = 'czech',
        when: str = '7d',
        max_results: int = 10
    ) -> List[Dict]:
        """
        Fetch news for a search query.

        Args:
            query: Search query (company name)
            language: 'czech', 'english', 'german', 'slovak'
            when: Time filter - '1h', '1d', '7d', '1m'
            max_results: Max articles to return

        Returns:
            List of article dicts
        """
        self._rate_limit()

        url = self._build_url(query, language, when)
        feed = feedparser.parse(url)

        articles = []
        for entry in feed.entries[:max_results]:
            # Google News format: "Title - Source"
            title = entry.get('title', '')
            source = ''
            if ' - ' in title:
                title, source = title.rsplit(' - ', 1)

            articles.append({
                'title': title,
                'source': source,
                'url': entry.get('link', ''),
                'published_at': entry.get('published', ''),
                'description': entry.get('summary', ''),
                'provider': f'google_news_{language}',
            })

        return articles

    def fetch_company_news(
        self,
        company: str,
        languages: List[str] = None,
        when: str = '7d',
        max_per_lang: int = 5
    ) -> List[Dict]:
        """Fetch news for a company in multiple languages."""
        if languages is None:
            languages = ['czech', 'english']

        all_articles = []
        for lang in languages:
            articles = self.fetch_news(
                query=f'"{company}"',
                language=lang,
                when=when,
                max_results=max_per_lang
            )
            all_articles.extend(articles)

        return all_articles
