"""Generate README.md from CSV data."""

import csv
import re
from datetime import date, datetime
from typing import List, Optional
from pathlib import Path

from ..config import CSV_PATH, README_PATH, CATEGORIES


def load_opportunities(path: Path = CSV_PATH) -> List[dict]:
    """Load opportunities from CSV."""
    with open(path, 'r', encoding='utf-8') as f:
        return list(csv.DictReader(f))


def parse_deadline_for_sort(deadline: str) -> tuple:
    """
    Parse deadline into sortable format.

    Returns tuple of (sort_key, is_rolling)
    Lower sort_key = sooner deadline
    """
    if not deadline:
        return (9999, 12, 31, True)

    deadline_lower = deadline.lower()

    if deadline_lower in ('rolling', 'tba', 'varies'):
        return (9999, 12, 31, True)

    # Try ISO format (YYYY-MM-DD)
    try:
        d = datetime.strptime(deadline, '%Y-%m-%d')
        return (d.year, d.month, d.day, False)
    except ValueError:
        pass

    # Try month name
    months = {
        'january': 1, 'february': 2, 'march': 3, 'april': 4,
        'may': 5, 'june': 6, 'july': 7, 'august': 8,
        'september': 9, 'october': 10, 'november': 11, 'december': 12
    }
    for month_name, month_num in months.items():
        if month_name in deadline_lower:
            # Assume current or next year
            current_year = date.today().year
            current_month = date.today().month
            year = current_year if month_num >= current_month else current_year + 1
            return (year, month_num, 15, False)  # Assume mid-month

    return (9998, 12, 31, False)  # Unknown but not rolling


def format_deadline(deadline: str) -> str:
    """Format deadline for display."""
    if not deadline:
        return "—"

    deadline_lower = deadline.lower()

    if deadline_lower == 'rolling':
        return "Rolling"
    if deadline_lower in ('tba', 'varies'):
        return deadline.upper()

    # Try ISO format
    try:
        d = datetime.strptime(deadline, '%Y-%m-%d')
        return d.strftime('%b %d')  # e.g., "Mar 08"
    except ValueError:
        pass

    # Return as-is if already formatted
    return deadline


def format_compensation(comp: str, details: str) -> str:
    """Format compensation for display."""
    if not comp:
        return "—"

    # If we have details with dollar amounts, use that
    if details and '$' in details:
        # Shorten if too long
        if len(details) > 30:
            # Extract just the dollar amount
            match = re.search(r'\$[\d,]+k?', details, re.IGNORECASE)
            if match:
                return match.group(0)
        return details

    # Map compensation types
    comp_display = {
        'paid': 'Paid',
        'stipend': 'Stipend',
        'grant': 'Grant',
        'scholarship': 'Scholarship',
        'equity': 'Equity',
        'unpaid': 'Unpaid',
        'varies': 'Varies',
        'unknown': '—'
    }

    return comp_display.get(comp.lower(), comp)


def generate_opportunity_table(opportunities: List[dict], include_status: bool = True) -> str:
    """Generate markdown table from opportunities."""
    if not opportunities:
        return "*No opportunities in this category yet.*\n"

    # Header
    if include_status:
        header = "| Name | Organization | Category | Deadline | Compensation | Status |\n"
        header += "|------|--------------|----------|----------|--------------|--------|\n"
    else:
        header = "| Name | Organization | Category | Deadline | Compensation |\n"
        header += "|------|--------------|----------|----------|---------------|\n"

    rows = []
    for opp in opportunities:
        name = opp.get('name', 'Unknown')
        url = opp.get('url', '#')
        org = opp.get('organization', '—')
        category = opp.get('category', '—').title()
        deadline = format_deadline(opp.get('deadline', ''))
        comp = format_compensation(
            opp.get('compensation', ''),
            opp.get('compensation_details', '')
        )
        status = opp.get('status', 'unknown').title()

        # Truncate long names
        if len(name) > 40:
            name = name[:37] + "..."

        if include_status:
            row = f"| [{name}]({url}) | {org} | {category} | {deadline} | {comp} | {status} |"
        else:
            row = f"| [{name}]({url}) | {org} | {category} | {deadline} | {comp} |"

        rows.append(row)

    return header + '\n'.join(rows) + '\n'


def generate_readme(opportunities: List[dict]) -> str:
    """Generate the full README content."""
    today = date.today().strftime('%Y-%m-%d')
    total = len(opportunities)

    # Sort opportunities
    sorted_opps = sorted(
        opportunities,
        key=lambda x: parse_deadline_for_sort(x.get('deadline', ''))
    )

    # Split into upcoming (fixed deadlines) and rolling
    upcoming = []
    rolling = []

    for opp in sorted_opps:
        deadline = opp.get('deadline', '').lower()
        deadline_type = opp.get('deadline_type', '').lower()
        status = opp.get('status', '').lower()

        # Skip closed opportunities from main display
        if status == 'closed':
            continue

        if deadline in ('rolling', 'tba', 'varies') or deadline_type == 'rolling':
            rolling.append(opp)
        else:
            upcoming.append(opp)

    # Group by category
    by_category = {}
    for opp in sorted_opps:
        cat = opp.get('category', 'other')
        if cat not in by_category:
            by_category[cat] = []
        by_category[cat].append(opp)

    # Build README
    readme = f"""# Awesome STEM Opportunities

> A curated list of fellowships, research programs, grants, accelerators, and selective opportunities for CS/STEM students in North America.

[![Awesome](https://awesome.re/badge.svg)](https://awesome.re)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

---

## Contents

- [What This Is](#what-this-is)
- [What This Is Not](#what-this-is-not)
- [Who This Is For](#who-this-is-for)
- [All Opportunities](#all-opportunities)
- [Contributing](#contributing)
- [Disclaimer](#disclaimer)
- [License](#license)

---

## What This Is

A carefully curated collection of **high-signal opportunities** for students and early-career individuals in CS and STEM fields:

- **Fellowships** — Selective programs offering mentorship, funding, and community
- **Research programs** — University and industry research experiences
- **Accelerators & incubators** — Startup-focused programs for student founders
- **Grants & funding** — Financial support for projects, research, or education
- **Scholarships** — Merit and need-based awards for STEM students
- **VC & startup ecosystem programs** — Investor-backed talent networks
- **Innovation & leadership programs** — Selective cohort-based experiences

## What This Is Not

- **Not an internship tracker.** There are excellent resources for internships elsewhere.
- **Not a job board.** Full-time roles are out of scope.
- **Not exhaustive.** Quality over quantity.

## Who This Is For

- **Undergraduate students** in CS, engineering, math, physics, and related fields
- **Graduate students** (Masters and PhD) seeking research or fellowship opportunities
- **Recent graduates** (within 1-2 years) eligible for early-career programs
- **Student founders** looking for accelerators, grants, or VC programs

Primary geographic focus: **United States and Canada**, though some programs have broader eligibility.

---

## All Opportunities

> **Last updated:** {today} | **Total:** {total} opportunities

"""

    # Upcoming deadlines section
    if upcoming:
        readme += "### Upcoming Deadlines\n\n"
        readme += generate_opportunity_table(upcoming[:20])  # Top 20
        if len(upcoming) > 20:
            readme += f"\n*...and {len(upcoming) - 20} more with fixed deadlines. See full list below.*\n"
        readme += "\n"

    # Rolling/ongoing section
    if rolling:
        readme += "### Rolling / Ongoing\n\n"
        readme += generate_opportunity_table(rolling, include_status=False)
        readme += "\n"

    # By category (collapsible)
    readme += "### By Category\n\n"

    category_emoji = {
        'research': '🔬',
        'fellowship': '🎓',
        'accelerator': '🚀',
        'grant': '💰',
        'scholarship': '📚',
        'ecosystem': '🌱',
        'innovation': '🏆',
        'leadership': '👥',
    }

    for cat in CATEGORIES:
        if cat in by_category:
            cat_opps = by_category[cat]
            emoji = category_emoji.get(cat, '📋')
            readme += f"""<details>
<summary>{emoji} {cat.title()} ({len(cat_opps)})</summary>

{generate_opportunity_table(cat_opps, include_status=True)}
</details>

"""

    # Footer sections
    readme += """---

## Contributing

We welcome contributions! Please read our [Contributing Guide](CONTRIBUTING.md) before submitting.

**Quick ways to help:**
- [Submit a new opportunity](../../issues/new?template=add-opportunity.yml)
- [Report an outdated listing](../../issues/new?template=report-outdated.yml)
- Fix typos or improve descriptions via PR

See [docs/submission-guide.md](docs/submission-guide.md) for formatting conventions.

---

## Disclaimer

> **Important:** Deadlines, eligibility requirements, and program details change frequently. This repository is maintained on a best-effort basis.

- Always verify information on the **official program website** before applying
- Deadline dates may refer to different years or cycles
- Eligibility criteria (citizenship, enrollment status, etc.) vary by program
- "Rolling" deadlines may close without notice when cohorts fill

This repository is not affiliated with any of the listed organizations.

---

## License

This project is licensed under the [MIT License](LICENSE).

---

**Maintainer:** [@amanda-yin-x](https://github.com/amanda-yin-x)

*Know a great opportunity that's missing? [Open an issue](../../issues/new?template=add-opportunity.yml) or submit a PR!*
"""

    return readme


def update_readme(csv_path: Path = CSV_PATH, readme_path: Path = README_PATH):
    """Update README.md from CSV data."""
    opportunities = load_opportunities(csv_path)
    readme_content = generate_readme(opportunities)

    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(readme_content)

    print(f"Updated {readme_path} with {len(opportunities)} opportunities")


def main():
    """CLI entry point."""
    update_readme()


if __name__ == "__main__":
    main()
