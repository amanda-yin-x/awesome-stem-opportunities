"""Normalize scraped data to schema format."""

import re
from datetime import date
from typing import Optional
from urllib.parse import urlparse

from ..models import RawOpportunity, Opportunity
from ..config import CATEGORIES


# Keyword mappings for category inference
CATEGORY_KEYWORDS = {
    "research": ["research", "reu", "lab", "scientist", "phd", "postdoc"],
    "fellowship": ["fellowship", "fellow", "cohort", "mentorship"],
    "accelerator": ["accelerator", "incubator", "startup school", "yc", "y combinator"],
    "grant": ["grant", "funding", "prize", "award", "$"],
    "scholarship": ["scholarship", "tuition", "financial aid"],
    "ecosystem": ["vc", "venture", "investor", "partner program", "talent network"],
    "innovation": ["hackathon", "hack", "competition", "challenge", "demo day"],
    "leadership": ["ambassador", "campus rep", "community", "leader"],
}


def generate_id(name: str, organization: Optional[str] = None) -> str:
    """Generate kebab-case ID from name and organization."""
    parts = []

    if organization:
        # Simplify org name
        org_simple = re.sub(r'[^a-zA-Z0-9\s]', '', organization)
        org_words = org_simple.lower().split()[:2]  # First 2 words
        parts.extend(org_words)

    # Simplify program name
    name_simple = re.sub(r'[^a-zA-Z0-9\s]', '', name)
    name_words = name_simple.lower().split()[:3]  # First 3 words
    parts.extend(name_words)

    # Remove duplicates while preserving order
    seen = set()
    unique_parts = []
    for p in parts:
        if p not in seen and len(p) > 1:
            seen.add(p)
            unique_parts.append(p)

    return '-'.join(unique_parts[:4]) or 'unknown'


def infer_category(text: str) -> str:
    """Infer category from text content."""
    text_lower = text.lower()

    # Score each category
    scores = {}
    for category, keywords in CATEGORY_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in text_lower)
        if score > 0:
            scores[category] = score

    if scores:
        return max(scores, key=scores.get)

    return "fellowship"  # Default


def parse_deadline(text: Optional[str]) -> tuple[Optional[str], Optional[str]]:
    """
    Parse deadline text into standardized format.

    Returns:
        Tuple of (deadline, deadline_type)
    """
    if not text:
        return (None, None)

    text_lower = text.lower()

    # Check for rolling
    if "rolling" in text_lower:
        return ("rolling", "rolling")

    # Check for TBA
    if any(x in text_lower for x in ["tba", "tbd", "to be announced"]):
        return ("tba", "tba")

    # Try to parse date patterns
    # Month Day, Year
    match = re.search(
        r'(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{1,2})(?:,?\s+(\d{4}))?',
        text,
        re.IGNORECASE
    )
    if match:
        month = match.group(1).capitalize()
        day = match.group(2)
        year = match.group(3) or str(date.today().year)

        # Convert to ISO format
        month_num = {
            'january': '01', 'february': '02', 'march': '03', 'april': '04',
            'may': '05', 'june': '06', 'july': '07', 'august': '08',
            'september': '09', 'october': '10', 'november': '11', 'december': '12'
        }[month.lower()]

        return (f"{year}-{month_num}-{day.zfill(2)}", "fixed")

    # Just month name
    months = ['january', 'february', 'march', 'april', 'may', 'june',
              'july', 'august', 'september', 'october', 'november', 'december']
    for month in months:
        if month in text_lower:
            return (month.capitalize(), "fixed")

    # Return original if can't parse
    return (text.strip(), "fixed")


def extract_organization_from_url(url: str) -> Optional[str]:
    """Extract organization name from URL."""
    try:
        parsed = urlparse(url)
        domain = parsed.netloc.lower()

        # Remove common prefixes
        for prefix in ['www.', 'apply.', 'jobs.', 'careers.', 'events.']:
            if domain.startswith(prefix):
                domain = domain[len(prefix):]

        # Get main part
        parts = domain.split('.')
        if len(parts) >= 2:
            name = parts[0].replace('-', ' ').replace('_', ' ')
            return name.title()

    except Exception:
        pass

    return None


def normalize_opportunity(raw: RawOpportunity) -> Optional[Opportunity]:
    """
    Normalize a raw scraped opportunity into schema format.

    Returns None if data is insufficient.
    """
    if not raw.is_valid():
        return None

    # Generate ID
    org = raw.organization or extract_organization_from_url(raw.url or '')
    opp_id = generate_id(raw.name or '', org)

    # Infer category
    combined_text = f"{raw.name or ''} {raw.description or ''}"
    category = infer_category(combined_text)

    # Parse deadline
    deadline, deadline_type = parse_deadline(raw.deadline_text)

    today = date.today()

    try:
        opportunity = Opportunity(
            id=opp_id,
            name=raw.name or '',
            organization=org or 'Unknown',
            category=category,
            url=raw.url,
            apply_url=raw.apply_url,
            deadline=deadline,
            deadline_type=deadline_type,
            status="unknown",
            description=raw.description[:300] if raw.description else None,
            source=raw.source_url,
            source_type="scraped",
            date_added=today,
            last_verified=today,
        )
        return opportunity
    except Exception as e:
        print(f"Failed to normalize opportunity: {e}")
        return None
