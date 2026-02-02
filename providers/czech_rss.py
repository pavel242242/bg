#!/usr/bin/env python3
"""
Czech RSS Feeds Provider
Fetches news from major Czech news sources via RSS.
"""

import feedparser
import re
from typing import List, Dict, Optional
from datetime import datetime


# Czech business/economy RSS feeds
CZECH_FEEDS = {
    'HN Byznys': 'https://byznys.hn.cz/?m=rss',
    'HN Investice': 'https://investice.hn.cz/?m=rss',
    'Ekonom': 'https://ekonom.cz/?m=rss',
    'iDNES Ekonomika': 'https://servis.idnes.cz/rss.aspx?c=ekonomikah',
    'Aktualne Ekonomika': 'https://www.aktualne.cz/rss/ekonomika/',
    'E15': 'https://www.e15.cz/rss',
    'Seznam Zpravy': 'https://www.seznamzpravy.cz/rss',
}


class CzechRSSProvider:
    """Provider for Czech news RSS feeds."""

    def __init__(self, feeds: Dict[str, str] = None):
        self.feeds = feeds or CZECH_FEEDS

    def fetch_feed(self, name: str, url: str, max_articles: int = 20) -> List[Dict]:
        """Fetch articles from a single RSS feed."""
        try:
            feed = feedparser.parse(url)

            if feed.bozo and not feed.entries:
                print(f"  Warning: {name} feed has issues")
                return []

            articles = []
            for entry in feed.entries[:max_articles]:
                articles.append({
                    'title': entry.get('title', ''),
                    'url': entry.get('link', ''),
                    'description': entry.get('summary', entry.get('description', '')),
                    'published_at': entry.get('published', entry.get('updated', '')),
                    'source': name,
                    'provider': 'czech_rss',
                })

            return articles

        except Exception as e:
            print(f"  Error fetching {name}: {e}")
            return []

    def fetch_all_feeds(self, max_per_feed: int = 20) -> List[Dict]:
        """Fetch articles from all configured Czech feeds."""
        all_articles = []

        for name, url in self.feeds.items():
            print(f"  Fetching {name}...")
            articles = self.fetch_feed(name, url, max_per_feed)
            all_articles.extend(articles)
            print(f"    Found {len(articles)} articles")

        return all_articles

    def search_articles(
        self,
        articles: List[Dict],
        keywords: List[str],
        case_sensitive: bool = False
    ) -> List[Dict]:
        """Search articles for keywords."""
        matching = []

        for article in articles:
            text = f"{article['title']} {article.get('description', '')}"
            if not case_sensitive:
                text = text.lower()
                keywords_check = [kw.lower() for kw in keywords]
            else:
                keywords_check = keywords

            if any(kw in text for kw in keywords_check):
                matching.append(article)

        return matching

    def fetch_company_news(self, company: str, max_per_feed: int = 20) -> List[Dict]:
        """Fetch news mentioning a specific company from all Czech feeds."""
        all_articles = self.fetch_all_feeds(max_per_feed)

        # Search for company name (and common variations)
        keywords = [company]
        # Add without diacritics for broader matching
        keywords.append(self._remove_diacritics(company))

        matching = self.search_articles(all_articles, keywords)
        return matching

    @staticmethod
    def _remove_diacritics(text: str) -> str:
        """Remove Czech diacritics for broader matching."""
        replacements = {
            'á': 'a', 'č': 'c', 'ď': 'd', 'é': 'e', 'ě': 'e',
            'í': 'i', 'ň': 'n', 'ó': 'o', 'ř': 'r', 'š': 's',
            'ť': 't', 'ú': 'u', 'ů': 'u', 'ý': 'y', 'ž': 'z',
            'Á': 'A', 'Č': 'C', 'Ď': 'D', 'É': 'E', 'Ě': 'E',
            'Í': 'I', 'Ň': 'N', 'Ó': 'O', 'Ř': 'R', 'Š': 'S',
            'Ť': 'T', 'Ú': 'U', 'Ů': 'U', 'Ý': 'Y', 'Ž': 'Z',
        }
        for cz, en in replacements.items():
            text = text.replace(cz, en)
        return text
