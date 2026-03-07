"""Link and content verification."""

import asyncio
import csv
from datetime import date
from typing import List, Tuple, Optional
from pathlib import Path
import httpx

from ..config import (
    CSV_PATH, REQUEST_TIMEOUT, MAX_RETRIES,
    STALE_THRESHOLD_DAYS, CSV_COLUMNS
)


class LinkVerifier:
    """Verify URLs are accessible and update verification timestamps."""

    def __init__(self, timeout: int = REQUEST_TIMEOUT):
        self.timeout = timeout
        self.results: List[dict] = []

    async def check_url(self, url: str) -> Tuple[bool, int, Optional[str]]:
        """
        Check if a URL is accessible.

        Returns:
            Tuple of (is_valid, status_code, error_message)
        """
        try:
            async with httpx.AsyncClient(
                timeout=self.timeout,
                follow_redirects=True
            ) as client:
                response = await client.head(url)
                # Some servers don't support HEAD, try GET
                if response.status_code == 405:
                    response = await client.get(url)

                is_valid = response.status_code < 400
                return (is_valid, response.status_code, None)

        except httpx.TimeoutException:
            return (False, 0, "Timeout")
        except httpx.ConnectError:
            return (False, 0, "Connection failed")
        except Exception as e:
            return (False, 0, str(e)[:100])

    async def verify_entry(self, entry: dict) -> dict:
        """Verify a single CSV entry and return updated version."""
        entry = dict(entry)  # Make a copy
        errors = []

        # Check main URL
        url = entry.get('url', '')
        if url:
            is_valid, status, error = await self.check_url(url)
            if not is_valid:
                errors.append(f"Main URL: {error or f'HTTP {status}'}")

        # Check apply URL if present
        apply_url = entry.get('apply_url', '')
        if apply_url:
            is_valid, status, error = await self.check_url(apply_url)
            if not is_valid:
                errors.append(f"Apply URL: {error or f'HTTP {status}'}")

        # Update verification status
        if not errors:
            entry['last_verified'] = date.today().isoformat()

        return {
            'entry': entry,
            'errors': errors,
            'id': entry.get('id', 'unknown')
        }

    async def verify_all(self, entries: List[dict], concurrency: int = 5) -> List[dict]:
        """
        Verify all entries with limited concurrency.

        Returns list of updated entries.
        """
        semaphore = asyncio.Semaphore(concurrency)

        async def verify_with_semaphore(entry):
            async with semaphore:
                return await self.verify_entry(entry)

        tasks = [verify_with_semaphore(e) for e in entries]
        self.results = await asyncio.gather(*tasks)

        return [r['entry'] for r in self.results]

    def get_errors(self) -> List[dict]:
        """Get entries that had verification errors."""
        return [r for r in self.results if r['errors']]

    def get_stale_entries(self, entries: List[dict]) -> List[dict]:
        """Get entries not verified within threshold."""
        stale = []
        today = date.today()

        for entry in entries:
            last_verified = entry.get('last_verified', '')
            if not last_verified:
                stale.append(entry)
                continue

            try:
                verified_date = date.fromisoformat(last_verified)
                days_since = (today - verified_date).days
                if days_since > STALE_THRESHOLD_DAYS:
                    stale.append(entry)
            except ValueError:
                stale.append(entry)

        return stale


def load_csv(path: Path = CSV_PATH) -> List[dict]:
    """Load CSV file."""
    with open(path, 'r', encoding='utf-8') as f:
        return list(csv.DictReader(f))


def save_csv(entries: List[dict], path: Path = CSV_PATH):
    """Save entries to CSV file."""
    with open(path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
        writer.writeheader()
        writer.writerows(entries)


async def verify_all_links(
    csv_path: Path = CSV_PATH,
    update_file: bool = True,
    concurrency: int = 5
) -> Tuple[int, int, List[dict]]:
    """
    Verify all links in CSV file.

    Returns:
        Tuple of (total_checked, errors_found, error_details)
    """
    entries = load_csv(csv_path)
    verifier = LinkVerifier()

    print(f"Verifying {len(entries)} entries...")
    updated_entries = await verifier.verify_all(entries, concurrency)

    errors = verifier.get_errors()

    if update_file and not errors:
        save_csv(updated_entries, csv_path)
        print(f"Updated {csv_path}")

    return (len(entries), len(errors), errors)


def main():
    """CLI entry point."""
    import sys

    print("Starting link verification...")
    total, error_count, errors = asyncio.run(verify_all_links())

    print(f"\nResults: {total} entries checked, {error_count} errors found")

    if errors:
        print("\nErrors:")
        for e in errors:
            print(f"  - {e['id']}: {', '.join(e['errors'])}")
        sys.exit(1)
    else:
        print("All links verified successfully!")
        sys.exit(0)


if __name__ == "__main__":
    main()
