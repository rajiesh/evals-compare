"""
Web search functionality for research agents
Supports multiple search APIs: SerpAPI and Google Custom Search
"""

import os
import json
import hashlib
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime
import requests

from src.config.settings import settings


class SearchResult:
    """Represents a single search result"""

    def __init__(self, title: str, url: str, snippet: str, source: str = ""):
        self.title = title
        self.url = url
        self.snippet = snippet
        self.source = source

    def to_dict(self) -> dict:
        return {
            "title": self.title,
            "url": self.url,
            "snippet": self.snippet,
            "source": self.source
        }

    def __repr__(self) -> str:
        return f"SearchResult(title='{self.title}', url='{self.url}')"


class WebSearchTool:
    """Web search tool with caching and multiple API support"""

    def __init__(self, cache_enabled: bool = True, verbose: bool = False):
        self.cache_enabled = cache_enabled and settings.CACHE_ENABLED
        self.verbose = verbose
        self.cache_dir = settings.CACHE_DIR / "search_cache"

        if self.cache_enabled:
            self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _get_cache_key(self, query: str, max_results: int) -> str:
        """Generate cache key for a search query"""
        cache_str = f"{query}_{max_results}"
        return hashlib.md5(cache_str.encode()).hexdigest()

    def _load_from_cache(self, cache_key: str) -> Optional[List[SearchResult]]:
        """Load search results from cache"""
        if not self.cache_enabled:
            return None

        cache_file = self.cache_dir / f"{cache_key}.json"
        if not cache_file.exists():
            return None

        try:
            with open(cache_file, 'r') as f:
                data = json.load(f)
                if self.verbose:
                    print(f"  └─ Loaded from cache (saved: {data.get('timestamp', 'unknown')})")
                return [SearchResult(**r) for r in data['results']]
        except Exception as e:
            if self.verbose:
                print(f"  └─ Cache read error: {e}")
            return None

    def _save_to_cache(self, cache_key: str, results: List[SearchResult]):
        """Save search results to cache"""
        if not self.cache_enabled:
            return

        cache_file = self.cache_dir / f"{cache_key}.json"
        try:
            data = {
                "timestamp": datetime.now().isoformat(),
                "results": [r.to_dict() for r in results]
            }
            with open(cache_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            if self.verbose:
                print(f"  └─ Cache write error: {e}")

    def _search_serpapi(self, query: str, max_results: int) -> List[SearchResult]:
        """Search using SerpAPI"""
        if not settings.SERPAPI_KEY:
            raise ValueError("SERPAPI_KEY not configured")

        url = "https://serpapi.com/search"
        params = {
            "q": query,
            "api_key": settings.SERPAPI_KEY,
            "num": max_results,
            "engine": "google"
        }

        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            results = []
            for item in data.get("organic_results", [])[:max_results]:
                results.append(SearchResult(
                    title=item.get("title", ""),
                    url=item.get("link", ""),
                    snippet=item.get("snippet", ""),
                    source="serpapi"
                ))

            return results

        except Exception as e:
            if self.verbose:
                print(f"  └─ SerpAPI error: {e}")
            return []

    def _search_google_custom(self, query: str, max_results: int) -> List[SearchResult]:
        """Search using Google Custom Search API"""
        if not settings.GOOGLE_API_KEY or not settings.GOOGLE_CSE_ID:
            raise ValueError("GOOGLE_API_KEY or GOOGLE_CSE_ID not configured")

        url = "https://www.googleapis.com/customsearch/v1"
        results = []

        # Google API returns max 10 results per request
        for start_index in range(1, min(max_results + 1, 101), 10):
            params = {
                "key": settings.GOOGLE_API_KEY,
                "cx": settings.GOOGLE_CSE_ID,
                "q": query,
                "num": min(10, max_results - len(results)),
                "start": start_index
            }

            try:
                response = requests.get(url, params=params, timeout=10)
                response.raise_for_status()
                data = response.json()

                for item in data.get("items", []):
                    results.append(SearchResult(
                        title=item.get("title", ""),
                        url=item.get("link", ""),
                        snippet=item.get("snippet", ""),
                        source="google_custom"
                    ))

                if len(results) >= max_results:
                    break

            except Exception as e:
                if self.verbose:
                    print(f"  └─ Google Custom Search error: {e}")
                break

        return results[:max_results]

    def search(self, query: str, max_results: int = None) -> List[SearchResult]:
        """
        Perform web search with caching

        Args:
            query: Search query string
            max_results: Maximum number of results to return (default from settings)

        Returns:
            List of SearchResult objects
        """
        if max_results is None:
            max_results = settings.MAX_SEARCH_RESULTS

        if self.verbose:
            print(f"  └─ Searching for: '{query}' (max {max_results} results)")

        # Check cache first
        cache_key = self._get_cache_key(query, max_results)
        cached_results = self._load_from_cache(cache_key)
        if cached_results is not None:
            return cached_results

        # Try search APIs in order of preference
        results = []

        if settings.SERPAPI_KEY:
            try:
                results = self._search_serpapi(query, max_results)
                if self.verbose and results:
                    print(f"  └─ Found {len(results)} results via SerpAPI")
            except Exception as e:
                if self.verbose:
                    print(f"  └─ SerpAPI failed: {e}")

        if not results and settings.GOOGLE_API_KEY:
            try:
                results = self._search_google_custom(query, max_results)
                if self.verbose and results:
                    print(f"  └─ Found {len(results)} results via Google Custom Search")
            except Exception as e:
                if self.verbose:
                    print(f"  └─ Google Custom Search failed: {e}")

        if not results:
            if self.verbose:
                print("  └─ No search results found")
            return []

        # Save to cache
        self._save_to_cache(cache_key, results)

        return results

    def format_results_for_llm(self, results: List[SearchResult]) -> str:
        """Format search results for LLM consumption"""
        if not results:
            return "No search results found."

        formatted = f"Found {len(results)} search results:\n\n"
        for i, result in enumerate(results, 1):
            formatted += f"[{i}] {result.title}\n"
            formatted += f"    URL: {result.url}\n"
            formatted += f"    {result.snippet}\n\n"

        return formatted
