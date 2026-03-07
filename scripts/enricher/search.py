"""Web search fallback using DuckDuckGo HTML (no API key required).

Used when the official page is missing critical fields like
deadline, eligibility, or compensation information.
"""

import re
from typing import Dict, List, Optional
from urllib.parse import quote_plus, parse_qs, unquote, urlparse

import httpx
from bs4 import BeautifulSoup


async def search_duckduckgo(query: str, max_results: int = 5) -> List[Dict[str, str]]:
    """
    Search DuckDuckGo HTML lite and return results.

    Returns:
        List of {"title": ..., "url": ..., "snippet": ...}
    """
    url = f"https://html.duckduckgo.com/html/?q={quote_plus(query)}"
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
    }

    try:
        async with httpx.AsyncClient(timeout=15, follow_redirects=True) as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "lxml")
            results = []

            for result_el in soup.select(".result"):
                title_el = result_el.select_one(".result__title a")
                snippet_el = result_el.select_one(".result__snippet")

                if not title_el:
                    continue

                result_url = title_el.get("href", "")
                # DuckDuckGo wraps URLs in a redirect — extract actual URL
                if "uddg=" in result_url:
                    parsed = urlparse(result_url)
                    params = parse_qs(parsed.query)
                    if "uddg" in params:
                        result_url = unquote(params["uddg"][0])

                results.append({
                    "title": title_el.get_text(strip=True),
                    "url": result_url,
                    "snippet": snippet_el.get_text(strip=True) if snippet_el else "",
                })

                if len(results) >= max_results:
                    break

            return results
    except Exception as e:
        print(f"  Search failed: {e}")
        return []


async def search_for_missing_fields(
    name: str,
    organization: Optional[str],
    missing_fields: List[str],
) -> Dict[str, str]:
    """
    Search the web for specific missing information about an opportunity.

    Args:
        name: Program name
        organization: Organization name (optional)
        missing_fields: List of field names to search for

    Returns:
        Dict mapping field names to discovered snippets
    """
    found: Dict[str, str] = {}
    base_query = f"{name} {organization}" if organization else name

    field_search_terms = {
        "deadline": "deadline application due date",
        "eligibility": "eligibility requirements who can apply",
        "compensation": "funding stipend compensation amount",
    }

    for field in missing_fields:
        search_term = field_search_terms.get(field, field)
        query = f"{base_query} {search_term}"
        results = await search_duckduckgo(query, max_results=3)

        if not results:
            continue

        snippets = " ".join(r.get("snippet", "") for r in results)

        if field == "deadline":
            # Look for dates in snippets
            m = re.search(
                r'(?:deadline|due|closes?)[:\s]+([A-Z][a-z]+\s+\d{1,2}(?:,?\s+\d{4})?)',
                snippets, re.IGNORECASE,
            )
            if m:
                found["deadline"] = m.group(1).strip()

        elif field == "eligibility":
            for sent in re.split(r'[.!?]', snippets):
                if any(kw in sent.lower() for kw in ["eligible", "open to", "must be", "applicants"]):
                    clean = sent.strip()
                    if 10 < len(clean) < 200:
                        found["eligibility"] = clean
                        break

        elif field == "compensation":
            m = re.search(r'\$[\d,]+(?:\.\d{2})?(?:\s*[kK])?', snippets)
            if m:
                found["compensation_details"] = m.group(0)

    return found
