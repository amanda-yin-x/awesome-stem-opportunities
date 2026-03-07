"""Generic web scraper for opportunity pages."""

import re
from typing import List, Optional
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup

from .base import BaseScraper
from ..models import RawOpportunity


class WebScraper(BaseScraper):
    """Scraper for generic web pages with opportunity listings."""

    # Keywords that suggest an opportunity
    OPPORTUNITY_KEYWORDS = [
        "fellowship", "grant", "scholarship", "accelerator",
        "application", "apply", "deadline", "program",
        "funding", "award", "competition", "hackathon"
    ]

    # Patterns to extract deadline-like text
    DEADLINE_PATTERNS = [
        r'deadline[:\s]+([A-Za-z]+\s+\d{1,2}(?:,?\s+\d{4})?)',
        r'(?:apply by|due by|closes?)[:\s]+([A-Za-z]+\s+\d{1,2}(?:,?\s+\d{4})?)',
        r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
        r'((?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2}(?:,?\s+\d{4})?)',
    ]

    def __init__(self, urls: Optional[List[str]] = None, **kwargs):
        """
        Initialize with list of URLs to scrape.

        Args:
            urls: List of URLs to scrape. If None, must be set later.
        """
        super().__init__(**kwargs)
        self.urls = urls or []

    async def scrape(self) -> List[RawOpportunity]:
        """Scrape all configured URLs and return opportunities."""
        all_opportunities = []

        for url in self.urls:
            print(f"Scraping: {url}")
            html = await self.fetch(url)
            if html:
                opportunities = self.extract(html, url)
                all_opportunities.extend(opportunities)
                print(f"  Found {len(opportunities)} potential opportunities")

        return all_opportunities

    def extract(self, html: str, source_url: str) -> List[RawOpportunity]:
        """Extract opportunities from HTML content."""
        soup = BeautifulSoup(html, 'lxml')
        opportunities = []

        # Look for links that might be opportunities
        for link in soup.find_all('a', href=True):
            href = link.get('href', '')
            text = link.get_text(strip=True)

            # Skip empty or navigation links
            if not text or len(text) < 5 or len(text) > 200:
                continue

            # Check if text contains opportunity keywords
            text_lower = text.lower()
            if not any(kw in text_lower for kw in self.OPPORTUNITY_KEYWORDS):
                continue

            # Build absolute URL
            full_url = urljoin(source_url, href)

            # Skip if not http/https
            if not full_url.startswith('http'):
                continue

            # Try to find surrounding context for more info
            parent = link.parent
            context_text = parent.get_text(strip=True) if parent else ""

            # Try to extract deadline from context
            deadline = self._extract_deadline(context_text)

            opportunity = RawOpportunity(
                name=text,
                url=full_url,
                deadline_text=deadline,
                description=context_text[:300] if len(context_text) > 300 else context_text,
                source_url=source_url,
            )

            if opportunity.is_valid():
                opportunities.append(opportunity)

        return opportunities

    def _extract_deadline(self, text: str) -> Optional[str]:
        """Try to extract deadline from text."""
        for pattern in self.DEADLINE_PATTERNS:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        return None

    @staticmethod
    def extract_organization_from_url(url: str) -> Optional[str]:
        """Try to extract organization name from URL domain."""
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()

            # Remove common prefixes
            for prefix in ['www.', 'apply.', 'jobs.', 'careers.']:
                if domain.startswith(prefix):
                    domain = domain[len(prefix):]

            # Get the main part before TLD
            parts = domain.split('.')
            if len(parts) >= 2:
                return parts[0].replace('-', ' ').title()

            return None
        except Exception:
            return None
