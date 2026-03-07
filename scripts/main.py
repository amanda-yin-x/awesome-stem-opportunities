"""Main CLI entry point for the automation scripts."""

import argparse
import asyncio
import sys
from pathlib import Path

from .config import CSV_PATH, README_PATH
from .validate import validate_csv
from .verifier.verify import verify_all_links
from .generator.readme import update_readme
from .enricher.pipeline import run_full_pipeline


def cmd_validate(args):
    """Validate CSV against schema."""
    print("Validating CSV...")
    is_valid, errors = validate_csv(CSV_PATH)

    if is_valid:
        print("✓ Validation passed!")
        return 0
    else:
        print(f"✗ Validation failed with {len(errors)} error(s):")
        for error in errors:
            print(f"  - {error}")
        return 1


def cmd_verify(args):
    """Verify all links in CSV."""
    print("Verifying links...")
    total, error_count, errors = asyncio.run(
        verify_all_links(CSV_PATH, update_file=not args.dry_run)
    )

    print(f"\nChecked {total} entries, {error_count} errors found")

    if errors:
        for e in errors:
            print(f"  - {e['id']}: {', '.join(e['errors'])}")
        return 1

    return 0


def cmd_generate(args):
    """Generate README from CSV."""
    print("Generating README...")
    update_readme(CSV_PATH, README_PATH)
    print("✓ README updated!")
    return 0


def cmd_scrape(args):
    """Run scrapers (placeholder for now)."""
    print("Scraping is not yet fully implemented.")
    print("Sources requested:", args.sources)
    return 0


def cmd_enrich(args):
    """Enrich URLs into full opportunity records."""
    # Collect URLs from args and/or file
    urls = list(args.urls) if args.urls else []

    if args.file:
        try:
            with open(args.file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and line.startswith('http'):
                        urls.append(line)
        except FileNotFoundError:
            print(f"File not found: {args.file}")
            return 1

    if not urls:
        print("No URLs provided. Use positional args or --file.")
        return 1

    print(f"Enriching {len(urls)} URL(s)...")

    counts = run_full_pipeline(
        urls=urls,
        csv_path=CSV_PATH,
        use_search=not args.no_search,
        dry_run=args.dry_run,
    )

    if counts["errors"] == len(urls):
        return 1
    return 0


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Awesome STEM Opportunities automation scripts"
    )
    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # Validate command
    validate_parser = subparsers.add_parser('validate', help='Validate CSV against schema')

    # Verify command
    verify_parser = subparsers.add_parser('verify', help='Verify all links')
    verify_parser.add_argument('--dry-run', action='store_true',
                               help="Don't update CSV file")
    verify_parser.add_argument('--new-only', action='store_true',
                               help="Only verify entries not recently checked")

    # Generate command
    generate_parser = subparsers.add_parser('generate', help='Generate README from CSV')

    # Scrape command
    scrape_parser = subparsers.add_parser('scrape', help='Run scrapers')
    scrape_parser.add_argument('--sources', type=str, default='web',
                               help="Comma-separated list of sources (web,google-linkedin)")

    # Enrich command
    enrich_parser = subparsers.add_parser(
        'enrich',
        help='Enrich URLs into full opportunity records and add to CSV',
    )
    enrich_parser.add_argument('urls', nargs='*', help='One or more URLs to enrich')
    enrich_parser.add_argument('--file', '-f', type=str,
                               help='File with one URL per line')
    enrich_parser.add_argument('--dry-run', action='store_true',
                               help='Show results without modifying CSV or README')
    enrich_parser.add_argument('--no-search', action='store_true',
                               help='Skip web search fallback for missing fields')

    args = parser.parse_args()

    if args.command == 'validate':
        sys.exit(cmd_validate(args))
    elif args.command == 'verify':
        sys.exit(cmd_verify(args))
    elif args.command == 'generate':
        sys.exit(cmd_generate(args))
    elif args.command == 'scrape':
        sys.exit(cmd_scrape(args))
    elif args.command == 'enrich':
        sys.exit(cmd_enrich(args))
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
