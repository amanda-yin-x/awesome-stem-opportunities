"""Deduplication logic for opportunities."""

from typing import List, Tuple, Optional
from urllib.parse import urlparse
from difflib import SequenceMatcher

from ..models import Opportunity


def normalize_url(url: str) -> str:
    """Normalize URL for comparison."""
    try:
        parsed = urlparse(url.lower())
        # Remove trailing slashes, common tracking params
        path = parsed.path.rstrip('/')
        return f"{parsed.netloc}{path}"
    except Exception:
        return url.lower()


def similarity(a: str, b: str) -> float:
    """Calculate string similarity ratio."""
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def find_duplicates(
    new_entry: Opportunity,
    existing: List[dict],
    threshold: float = 0.85
) -> Tuple[Optional[dict], str]:
    """
    Find potential duplicates of a new entry.

    Returns:
        Tuple of (matching_entry_or_none, match_type)
        match_type: "exact_id", "exact_url", "fuzzy", "none"
    """
    new_url_normalized = normalize_url(str(new_entry.url))

    for entry in existing:
        # Exact ID match
        if entry.get('id') == new_entry.id:
            return (entry, "exact_id")

        # Exact URL match
        existing_url = entry.get('url', '')
        if existing_url and normalize_url(existing_url) == new_url_normalized:
            return (entry, "exact_url")

        # Fuzzy name + organization match
        existing_name = entry.get('name', '')
        existing_org = entry.get('organization', '')

        name_sim = similarity(new_entry.name, existing_name)
        org_sim = similarity(new_entry.organization, existing_org)

        # High similarity on both name and org
        if name_sim > threshold and org_sim > threshold:
            return (entry, "fuzzy")

        # Very high name similarity alone
        if name_sim > 0.95:
            return (entry, "fuzzy")

    return (None, "none")


def deduplicate(
    new_entries: List[Opportunity],
    existing: List[dict]
) -> Tuple[List[Opportunity], List[Tuple[Opportunity, dict, str]]]:
    """
    Deduplicate new entries against existing ones.

    Returns:
        Tuple of (unique_entries, potential_duplicates_with_match_info)
    """
    unique = []
    duplicates = []

    for entry in new_entries:
        match, match_type = find_duplicates(entry, existing)

        if match_type == "none":
            # Also check against already-added unique entries
            match2, match_type2 = find_duplicates(
                entry,
                [u.to_csv_row() for u in unique]
            )
            if match_type2 == "none":
                unique.append(entry)
            else:
                duplicates.append((entry, match2, match_type2))
        else:
            duplicates.append((entry, match, match_type))

    return (unique, duplicates)


def merge_entry(existing: dict, new: Opportunity) -> dict:
    """
    Merge new data into existing entry.

    Strategy: Prefer new non-empty values for most fields,
    but preserve date_added and id from existing.
    """
    merged = dict(existing)
    new_data = new.to_csv_row()

    # Fields to always preserve from existing
    preserve = ['id', 'date_added']

    # Fields to update if new value is non-empty
    for key, new_value in new_data.items():
        if key in preserve:
            continue

        if new_value and new_value != '':
            # Only update if existing is empty or new is different
            if not merged.get(key) or merged.get(key) != new_value:
                merged[key] = new_value

    # Always update last_verified to today
    merged['last_verified'] = new_data['last_verified']

    return merged
