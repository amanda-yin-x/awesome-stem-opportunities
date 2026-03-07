"""Main enrichment pipeline: URL in -> validated Opportunity out.

Flow:
  1. Fetch the main page
  2. Discover and fetch related pages on the same domain
  3. Extract all opportunity fields from combined HTML
  4. Fall back to web search for missing critical fields
  5. Generate ID, set metadata
  6. Validate against schema
  7. Check for duplicates
  8. Add to CSV and regenerate README
"""

import asyncio
import re
from datetime import date
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..config import CSV_PATH
from ..models import Opportunity
from ..processor.normalize import generate_id
from ..processor.dedupe import find_duplicates
from ..processor.merge import load_existing, add_single_opportunity
from ..generator.readme import update_readme
from ..validate import validate_csv

from .fetcher import PageFetcher
from .explorer import find_related_pages
from .extractor import OpportunityExtractor
from .search import search_for_missing_fields


async def enrich_url(
    url: str,
    fetcher: Optional[PageFetcher] = None,
    use_search: bool = True,
) -> Dict[str, Any]:
    """
    Enrich a single URL into a dict of opportunity fields.

    Fetches the page, discovers related pages on the same domain,
    extracts structured fields, and optionally uses web search
    to fill missing critical information.

    Returns:
        Dict with extracted fields. Contains "_error" key if the
        page could not be fetched.
    """
    if fetcher is None:
        fetcher = PageFetcher()

    print(f"\n{'=' * 60}")
    print(f"Enriching: {url}")
    print(f"{'=' * 60}")

    # 1. Fetch main page
    print("  Fetching main page...")
    html = await fetcher.fetch(url)
    if not html:
        print("  ERROR: Could not fetch page")
        return {"url": url, "_error": "Could not fetch page"}

    extractor = OpportunityExtractor()
    extractor.add_page(url, html)

    # 2. Discover related pages
    print("  Discovering related pages...")
    related = find_related_pages(html, url)
    if related:
        print(f"  Found {len(related)} related pages:")
        for rel_url in related:
            print(f"    -> {rel_url}")
            rel_html = await fetcher.fetch(rel_url)
            if rel_html:
                extractor.add_page(rel_url, rel_html)
    else:
        print("  No related pages found on same domain")

    # 3. Extract fields
    print("  Extracting fields...")
    fields = extractor.extract_all()

    # 4. Web search fallback
    if use_search:
        name = fields.get("name", "")
        org = fields.get("organization", "")
        missing = []
        if not fields.get("deadline"):
            missing.append("deadline")
        if not fields.get("eligibility"):
            missing.append("eligibility")
        if not fields.get("compensation") and not fields.get("compensation_details"):
            missing.append("compensation")

        if missing and name:
            print(f"  Searching web for: {', '.join(missing)}")
            found = await search_for_missing_fields(name, org, missing)
            for key, value in found.items():
                if key not in fields or not fields[key]:
                    fields[key] = value
                    print(f"    Found {key}: {value[:60]}")

    # 5. Generate ID and metadata
    name = fields.get("name", "")
    org = fields.get("organization", "")
    if name:
        fields["id"] = generate_id(name, org)
    else:
        fields["id"] = "unknown"

    fields["source"] = "Official website"
    fields["source_type"] = "official"
    fields["date_added"] = date.today().isoformat()
    fields["last_verified"] = date.today().isoformat()

    # 6. Report results
    _print_results(fields)
    return fields


async def enrich_urls(
    urls: List[str],
    use_search: bool = True,
    check_duplicates: bool = True,
) -> List[Dict[str, Any]]:
    """
    Enrich multiple URLs.

    Returns:
        List of enriched field dicts.
    """
    fetcher = PageFetcher()
    results = []
    existing = load_existing() if check_duplicates else []

    for i, url in enumerate(urls, 1):
        print(f"\n[{i}/{len(urls)}]")
        fields = await enrich_url(url, fetcher=fetcher, use_search=use_search)

        if "_error" in fields:
            results.append(fields)
            continue

        # Duplicate check
        if check_duplicates and existing:
            opp = _fields_to_opportunity(fields)
            if opp:
                match, match_type = find_duplicates(opp, existing)
                if match_type != "none":
                    print(f"  DUPLICATE ({match_type}): matches '{match.get('name')}'")
                    fields["_duplicate"] = True
                    fields["_duplicate_match"] = match.get("name")

        results.append(fields)

    # Summary
    print(f"\n{'=' * 60}")
    print(f"Enrichment complete: {len(results)} URLs processed")
    ok = [r for r in results if "_error" not in r]
    dupes = [r for r in results if r.get("_duplicate")]
    print(f"  Successful: {len(ok)}")
    print(f"  Duplicates: {len(dupes)}")
    print(f"  New:        {len(ok) - len(dupes)}")
    print(f"{'=' * 60}")

    return results


def validate_and_add(
    fields: Dict[str, Any],
    csv_path: Path = CSV_PATH,
    dry_run: bool = False,
) -> bool:
    """
    Validate extracted fields and add to CSV if valid.

    Returns True if successfully added (or would be added in dry-run).
    """
    opp = _fields_to_opportunity(fields)
    if not opp:
        missing = []
        for f in ["id", "name", "organization", "category", "url"]:
            if not fields.get(f):
                missing.append(f)
        print(f"  Cannot add: missing required fields: {', '.join(missing)}")
        return False

    if dry_run:
        print(f"  [DRY RUN] Would add: {opp.name}")
        return True

    return add_single_opportunity(opp, csv_path)


def run_full_pipeline(
    urls: List[str],
    csv_path: Path = CSV_PATH,
    readme_path: Optional[Path] = None,
    use_search: bool = True,
    dry_run: bool = False,
) -> Dict[str, int]:
    """
    End-to-end: enrich URLs -> validate -> add to CSV -> regenerate README.

    Returns:
        Dict with counts: {"processed", "added", "duplicates", "errors"}
    """
    from ..config import README_PATH
    if readme_path is None:
        readme_path = README_PATH

    results = asyncio.run(enrich_urls(urls, use_search=use_search))

    counts = {"processed": len(results), "added": 0, "duplicates": 0, "errors": 0}

    for fields in results:
        if "_error" in fields:
            counts["errors"] += 1
            continue
        if fields.get("_duplicate"):
            counts["duplicates"] += 1
            continue

        if validate_and_add(fields, csv_path=csv_path, dry_run=dry_run):
            counts["added"] += 1

    if not dry_run and counts["added"] > 0:
        # Validate the updated CSV
        print("\nValidating updated CSV...")
        is_valid, errors = validate_csv(csv_path)
        if is_valid:
            print("  Validation passed!")
        else:
            print(f"  Validation warnings ({len(errors)}):")
            for e in errors[:5]:
                print(f"    - {e}")

        # Regenerate README
        print("Regenerating README...")
        update_readme(csv_path, readme_path)
        print("  README updated!")

    # Final summary
    print(f"\nPipeline summary:")
    print(f"  Processed:  {counts['processed']}")
    print(f"  Added:      {counts['added']}")
    print(f"  Duplicates: {counts['duplicates']}")
    print(f"  Errors:     {counts['errors']}")

    return counts


# ======================================================================
# Internal helpers
# ======================================================================

def _fields_to_opportunity(fields: Dict[str, Any]) -> Optional[Opportunity]:
    """Try to convert extracted fields dict to a validated Opportunity."""
    try:
        data = {k: v for k, v in fields.items() if not k.startswith("_")}

        # Must have all required fields
        for f in ["id", "name", "organization", "category", "url"]:
            if not data.get(f):
                return None

        data.setdefault("date_added", date.today().isoformat())
        data.setdefault("last_verified", date.today().isoformat())
        data.setdefault("status", "unknown")

        return Opportunity(**data)
    except Exception as e:
        print(f"  Validation error: {e}")
        return None


def _print_results(fields: Dict[str, Any]):
    """Print a formatted summary of extracted fields."""
    print(f"\n  Extracted fields:")
    # Show important fields first
    priority = [
        "name", "organization", "category", "url", "apply_url",
        "deadline", "deadline_type", "status",
        "eligibility", "audience", "region", "country",
        "compensation", "compensation_details",
        "location_type", "location", "duration", "cohort_season",
        "description", "tags",
    ]
    shown = set()
    for key in priority:
        if key in fields and fields[key]:
            val = str(fields[key])
            if len(val) > 80:
                val = val[:77] + "..."
            print(f"    {key}: {val}")
            shown.add(key)

    # Show any remaining fields not in priority list
    for key, val in sorted(fields.items()):
        if key not in shown and val and not key.startswith("_"):
            val_s = str(val)
            if len(val_s) > 80:
                val_s = val_s[:77] + "..."
            print(f"    {key}: {val_s}")

    filled = sum(1 for k, v in fields.items() if v and not k.startswith("_"))
    print(f"\n  Total fields filled: {filled}")
