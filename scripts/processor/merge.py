"""Merge new opportunities with existing data."""

import csv
from typing import List, Tuple
from pathlib import Path

from ..config import CSV_PATH, CSV_COLUMNS
from ..models import Opportunity
from .dedupe import deduplicate, merge_entry


def load_existing(path: Path = CSV_PATH) -> List[dict]:
    """Load existing opportunities from CSV."""
    if not path.exists():
        return []

    with open(path, 'r', encoding='utf-8') as f:
        return list(csv.DictReader(f))


def save_opportunities(entries: List[dict], path: Path = CSV_PATH):
    """Save opportunities to CSV."""
    # Ensure all entries have all columns
    complete_entries = []
    for entry in entries:
        complete = {col: entry.get(col, '') for col in CSV_COLUMNS}
        complete_entries.append(complete)

    with open(path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
        writer.writeheader()
        writer.writerows(complete_entries)


def merge_opportunities(
    new_entries: List[Opportunity],
    csv_path: Path = CSV_PATH,
    dry_run: bool = False
) -> Tuple[int, int, int]:
    """
    Merge new opportunities into existing CSV.

    Returns:
        Tuple of (added_count, updated_count, duplicate_count)
    """
    existing = load_existing(csv_path)
    existing_by_id = {e.get('id'): e for e in existing}

    # Deduplicate
    unique, duplicates = deduplicate(new_entries, existing)

    added = 0
    updated = 0
    duplicate_count = len(duplicates)

    # Add unique new entries
    for entry in unique:
        row = entry.to_csv_row()
        existing.append(row)
        existing_by_id[entry.id] = row
        added += 1
        print(f"  + Added: {entry.name}")

    # Handle duplicates - update if exact match, flag if fuzzy
    for new_entry, match, match_type in duplicates:
        if match_type in ("exact_id", "exact_url"):
            # Update existing entry
            merged = merge_entry(match, new_entry)
            match_id = match.get('id')
            if match_id:
                existing_by_id[match_id] = merged
                # Update in list
                for i, e in enumerate(existing):
                    if e.get('id') == match_id:
                        existing[i] = merged
                        break
                updated += 1
                print(f"  ~ Updated: {new_entry.name}")
        else:
            # Fuzzy match - log but don't auto-merge
            print(f"  ? Potential duplicate: {new_entry.name} ~ {match.get('name')}")

    if not dry_run:
        save_opportunities(existing, csv_path)
        print(f"\nSaved {len(existing)} entries to {csv_path}")

    return (added, updated, duplicate_count)


def add_single_opportunity(
    entry: Opportunity,
    csv_path: Path = CSV_PATH
) -> bool:
    """
    Add a single opportunity to CSV.

    Returns True if added, False if duplicate.
    """
    existing = load_existing(csv_path)

    # Check for duplicates
    unique, duplicates = deduplicate([entry], existing)

    if not unique:
        print(f"Duplicate found: {entry.name}")
        return False

    # Add to CSV
    row = entry.to_csv_row()
    existing.append(row)
    save_opportunities(existing, csv_path)
    print(f"Added: {entry.name}")
    return True
