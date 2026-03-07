"""CSV validation against schema."""

import csv
import sys
import json
from pathlib import Path
from typing import List, Tuple
from datetime import date

from .config import CSV_PATH, SCHEMA_PATH, CSV_COLUMNS
from .models import Opportunity


def load_csv(path: Path) -> List[dict]:
    """Load CSV file and return list of rows as dicts."""
    with open(path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        return list(reader)


def validate_row(row: dict, line_num: int) -> List[str]:
    """Validate a single CSV row. Returns list of error messages."""
    errors = []

    # Check required fields
    required = ['id', 'name', 'organization', 'category', 'url']
    for field in required:
        if not row.get(field, '').strip():
            errors.append(f"Line {line_num}: Missing required field '{field}'")

    # Try to parse as Opportunity model
    try:
        # Prepare data for model
        data = {k: v if v else None for k, v in row.items()}

        # Handle dates
        if data.get('date_added'):
            data['date_added'] = data['date_added']
        else:
            data['date_added'] = date.today().isoformat()

        if data.get('last_verified'):
            data['last_verified'] = data['last_verified']
        else:
            data['last_verified'] = date.today().isoformat()

        Opportunity(**data)
    except Exception as e:
        errors.append(f"Line {line_num}: Validation error - {str(e)}")

    return errors


def validate_csv(path: Path = CSV_PATH) -> Tuple[bool, List[str]]:
    """
    Validate entire CSV file.

    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors = []

    # Check file exists
    if not path.exists():
        return False, [f"CSV file not found: {path}"]

    # Load and validate
    rows = load_csv(path)

    if not rows:
        return False, ["CSV file is empty (no data rows)"]

    # Check for duplicate IDs
    ids_seen = {}
    for i, row in enumerate(rows, start=2):  # Start at 2 (1 is header)
        row_id = row.get('id', '')
        if row_id in ids_seen:
            errors.append(f"Line {i}: Duplicate ID '{row_id}' (first seen on line {ids_seen[row_id]})")
        else:
            ids_seen[row_id] = i

        # Validate row
        row_errors = validate_row(row, i)
        errors.extend(row_errors)

    is_valid = len(errors) == 0
    return is_valid, errors


def main():
    """CLI entry point for validation."""
    print(f"Validating {CSV_PATH}...")

    is_valid, errors = validate_csv()

    if is_valid:
        rows = load_csv(CSV_PATH)
        print(f"✓ Valid! {len(rows)} opportunities validated successfully.")
        sys.exit(0)
    else:
        print(f"✗ Validation failed with {len(errors)} error(s):\n")
        for error in errors:
            print(f"  - {error}")
        sys.exit(1)


if __name__ == "__main__":
    main()
