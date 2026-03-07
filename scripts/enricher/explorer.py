"""Discover related pages on the same domain that may contain opportunity details."""

from typing import List, Set
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup

# Keywords in link text or href that indicate pages with useful info
RELEVANT_LINK_KEYWORDS = [
    "apply", "application", "register", "sign up", "signup",
    "about", "overview", "details", "information", "learn more",
    "eligibility", "requirements", "qualifications", "who can apply",
    "faq", "frequently asked", "questions",
    "timeline", "schedule", "dates", "deadline",
    "funding", "stipend", "compensation", "benefits", "perks",
    "fellows", "alumni", "cohort", "participants", "scholars",
    "program", "fellowship", "scholarship", "grant",
    "how to apply", "how it works",
]

# File extensions to skip
SKIP_EXTENSIONS = {
    ".pdf", ".jpg", ".jpeg", ".png", ".gif", ".svg",
    ".css", ".js", ".zip", ".doc", ".docx", ".xlsx",
    ".mp4", ".mp3", ".mov", ".webp", ".ico",
}


def find_related_pages(
    html: str,
    base_url: str,
    max_pages: int = 8,
) -> List[str]:
    """
    Find related pages on the same domain that likely contain
    useful opportunity information (eligibility, deadlines, etc.).

    Args:
        html: HTML content of the main page
        base_url: URL of the main page
        max_pages: Maximum number of related pages to return

    Returns:
        List of URLs ordered by relevance score (highest first)
    """
    soup = BeautifulSoup(html, "lxml")
    base_parsed = urlparse(base_url)
    base_domain = _clean_domain(base_parsed.netloc)

    candidates: List[tuple] = []  # (score, url)
    seen_urls: Set[str] = set()
    seen_urls.add(_normalize_url(base_url))

    for link in soup.find_all("a", href=True):
        href = link.get("href", "").strip()
        if not href or href.startswith(("#", "mailto:", "javascript:", "tel:")):
            continue

        full_url = urljoin(base_url, href)
        parsed = urlparse(full_url)

        # Must be same domain (or subdomain)
        link_domain = _clean_domain(parsed.netloc)
        if link_domain != base_domain and not link_domain.endswith("." + base_domain):
            continue

        if parsed.scheme not in ("http", "https"):
            continue

        # Skip non-page resources
        path_lower = parsed.path.lower()
        if any(path_lower.endswith(ext) for ext in SKIP_EXTENSIONS):
            continue

        normalized = _normalize_url(full_url)
        if normalized in seen_urls:
            continue
        seen_urls.add(normalized)

        # Score by relevance
        score = _score_link(link, parsed)
        if score > 0:
            candidates.append((score, full_url))

    candidates.sort(key=lambda x: x[0], reverse=True)
    return [url for _, url in candidates[:max_pages]]


def _clean_domain(netloc: str) -> str:
    """Remove www. prefix for comparison."""
    d = netloc.lower()
    return d[4:] if d.startswith("www.") else d


def _normalize_url(url: str) -> str:
    """Normalize URL for deduplication."""
    parsed = urlparse(url)
    path = parsed.path.rstrip("/")
    base = f"{parsed.scheme}://{parsed.netloc}{path}"
    if parsed.query:
        base += f"?{parsed.query}"
    return base.lower()


def _score_link(link, parsed) -> int:
    """Score a link by how likely it is to contain useful opportunity info."""
    score = 0
    link_text = link.get_text(strip=True).lower()
    path_lower = parsed.path.lower()

    for keyword in RELEVANT_LINK_KEYWORDS:
        if keyword in link_text:
            score += 2
        if keyword.replace(" ", "-") in path_lower or keyword.replace(" ", "") in path_lower:
            score += 1

    # Boost shorter paths (closer to main page, less likely to be blog posts etc.)
    path_depth = len([p for p in parsed.path.split("/") if p])
    if path_depth <= 2:
        score += 1
    elif path_depth >= 5:
        score -= 1

    return score
