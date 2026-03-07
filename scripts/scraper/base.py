"""Base scraper class with rate limiting and retry logic."""

import asyncio
import random
from abc import ABC, abstractmethod
from typing import List, Optional
import httpx

from ..config import DEFAULT_RATE_LIMIT, REQUEST_TIMEOUT, MAX_RETRIES
from ..models import RawOpportunity


class BaseScraper(ABC):
    """Abstract base class for all scrapers."""

    def __init__(
        self,
        rate_limit: float = DEFAULT_RATE_LIMIT,
        timeout: int = REQUEST_TIMEOUT,
        max_retries: int = MAX_RETRIES,
    ):
        self.rate_limit = rate_limit
        self.timeout = timeout
        self.max_retries = max_retries
        self._last_request_time = 0.0

    async def _rate_limit_wait(self):
        """Wait to respect rate limits with some randomization."""
        now = asyncio.get_event_loop().time()
        elapsed = now - self._last_request_time
        if elapsed < self.rate_limit:
            # Add some randomization to appear more human
            jitter = random.uniform(0.1, 0.5)
            await asyncio.sleep(self.rate_limit - elapsed + jitter)
        self._last_request_time = asyncio.get_event_loop().time()

    async def fetch(self, url: str, headers: Optional[dict] = None) -> Optional[str]:
        """
        Fetch a URL with rate limiting and retries.

        Returns HTML content or None if failed.
        """
        default_headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
        }
        if headers:
            default_headers.update(headers)

        for attempt in range(self.max_retries):
            await self._rate_limit_wait()

            try:
                async with httpx.AsyncClient(
                    timeout=self.timeout,
                    follow_redirects=True
                ) as client:
                    response = await client.get(url, headers=default_headers)
                    response.raise_for_status()
                    return response.text
            except httpx.TimeoutException:
                print(f"Timeout fetching {url} (attempt {attempt + 1}/{self.max_retries})")
            except httpx.HTTPStatusError as e:
                print(f"HTTP error {e.response.status_code} for {url}")
                if e.response.status_code in (403, 429):
                    # Rate limited or blocked, wait longer
                    await asyncio.sleep(self.rate_limit * 3)
                elif e.response.status_code >= 500:
                    # Server error, retry
                    continue
                else:
                    # Client error, don't retry
                    return None
            except Exception as e:
                print(f"Error fetching {url}: {e}")

        return None

    @abstractmethod
    async def scrape(self) -> List[RawOpportunity]:
        """
        Run the scraper and return list of raw opportunities.

        Must be implemented by subclasses.
        """
        pass

    @abstractmethod
    def extract(self, html: str, source_url: str) -> List[RawOpportunity]:
        """
        Extract opportunities from HTML content.

        Must be implemented by subclasses.
        """
        pass
