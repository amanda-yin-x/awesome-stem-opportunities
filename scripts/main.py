"""Main CLI entry point for the automation scripts."""

import argparse
import asyncio
import sys
from pathlib import Path

from .config import CSV_PATH, README_PATH
from .validate import validate_csv
from .verifier.verify import verify_all_links
from .generator.readme import update_readme


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

    # TODO: Implement scraping pipeline
    # For now, just validate that the infrastructure works

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

    args = parser.parse_args()

    if args.command == 'validate':
        sys.exit(cmd_validate(args))
    elif args.command == 'verify':
        sys.exit(cmd_verify(args))
    elif args.command == 'generate':
        sys.exit(cmd_generate(args))
    elif args.command == 'scrape':
        sys.exit(cmd_scrape(args))
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
