"""Async page fetcher with in-memory caching and rate limiting."""

import asyncio
import random
from typing import Optional, Dict

import httpx

from ..config import DEFAULT_RATE_LIMIT, REQUEST_TIMEOUT, MAX_RETRIES


class PageFetcher:
    """Fetches web pages with caching, rate limiting, and retries."""

    def __init__(
        self,
        rate_limit: float = DEFAULT_RATE_LIMIT,
        timeout: int = REQUEST_TIMEOUT,
        max_retries: int = MAX_RETRIES,
    ):
        self.rate_limit = rate_limit
        self.timeout = timeout
        self.max_retries = max_retries
        self._cache: Dict[str, Optional[str]] = {}
        self._final_urls: Dict[str, str] = {}
        self._last_request_time = 0.0

    async def _wait_for_rate_limit(self):
        now = asyncio.get_event_loop().time()
        elapsed = now - self._last_request_time
        if elapsed < self.rate_limit:
            jitter = random.uniform(0.1, 0.5)
            await asyncio.sleep(self.rate_limit - elapsed + jitter)
        self._last_request_time = asyncio.get_event_loop().time()

    async def fetch(self, url: str) -> Optional[str]:
        """Fetch a URL and return HTML. Uses cache for repeated requests."""
        if url in self._cache:
            return self._cache[url]

        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
        }

        for attempt in range(self.max_retries):
            await self._wait_for_rate_limit()
            try:
                async with httpx.AsyncClient(
                    timeout=self.timeout, follow_redirects=True
                ) as client:
                    response = await client.get(url, headers=headers)
                    response.raise_for_status()
                    html = response.text
                    self._cache[url] = html
                    self._final_urls[url] = str(response.url)
                    return html
            except httpx.TimeoutException:
                print(f"  Timeout: {url} (attempt {attempt + 1}/{self.max_retries})")
            except httpx.HTTPStatusError as e:
                code = e.response.status_code
                print(f"  HTTP {code}: {url}")
                if code in (403, 429):
                    await asyncio.sleep(self.rate_limit * 3)
                elif code >= 500:
                    continue
                else:
                    self._cache[url] = None
                    return None
            except Exception as e:
                print(f"  Error: {url} - {e}")

        self._cache[url] = None
        return None

    def get_final_url(self, url: str) -> str:
        """Return the URL after any redirects."""
        return self._final_urls.get(url, url)
