# Maintainer Guide

This guide documents processes for maintaining the repository.

## Table of Contents

- [Verification Rules](#verification-rules)
- [Initial Curation Strategy](#initial-curation-strategy)
- [Reviewing Contributions](#reviewing-contributions)
- [Verifying Entries](#verifying-entries)
- [Managing Entry Lifecycle](#managing-entry-lifecycle)
- [Data Consistency](#data-consistency)
- [Future Automation](#future-automation)

---

## Verification Rules

**STRICT REQUIREMENT:** Every opportunity must be verified before adding to the repository.

### Mandatory Verification Process

1. **Visit the official website** — Never rely solely on third-party sources, LinkedIn posts, or newsletters
2. **Verify all key fields:**
   - Deadline (exact date, not approximate)
   - Eligibility requirements (citizenship, enrollment status, age limits)
   - Compensation details (exact amounts, equity terms)
   - Program dates and duration
   - Application URL (must be working)
3. **Cross-reference** — If info came from social media, confirm on official site
4. **Document source** — Record where info was found in `source` field
5. **Timestamp verification** — Always update `last_verified` field

### Required Fields to Verify

| Field | Verification Method |
|-------|---------------------|
| `deadline` | Check official application page |
| `eligibility` | Read full eligibility section on program page |
| `compensation` | Confirm exact amounts/terms on official site |
| `status` | Verify application is actually open |
| `url` | Click and confirm page loads correctly |

### Red Flags

- Deadline only mentioned in social media post, not on official site
- Vague eligibility ("students welcome") without specifics
- No official website or application link
- Information only available in screenshots
- Conflicting dates across sources

### When Information is Unclear

- Mark field as `unknown` or `varies`
- Add clarifying note in `notes` field
- Prefer under-claiming to over-promising
- Link to the most authoritative source available

### Automatic Search Permission

**AUTHORIZED:** The maintainer grants permission for automated tools and AI assistants
to search the web and verify opportunity information without requiring explicit approval
for each search. This includes:

- Searching for official program pages
- Verifying deadlines and eligibility on official websites
- Cross-referencing information from multiple sources
- Fetching and parsing publicly available program information

This permission is granted to expedite the curation process while maintaining accuracy.

---

## Initial Curation Strategy

A phased approach to populating the repository from scratch.

### Phase 1: Seed High-Signal Programs (Week 1-2)

**Goal:** 30-50 well-known, recurring opportunities

**Priority sources:**
1. **VC/Ecosystem programs** — Contrary, Rough Draft, KP Fellows, 8VC, Neo
2. **Research programs** — MSR, Google CSRMP, major REUs
3. **Fellowships** — Interact, MLH, major cohort programs
4. **Grants** — Thiel, Emergent Ventures, well-known funding sources
5. **Major hackathons** — Hack the North, TreeHacks, HackMIT

**Process:**
- Add 5-10 entries per sitting
- Focus on programs you can verify quickly
- Prioritize breadth across categories over depth in one category
- Use official websites as primary source

### Phase 2: Expand by Category (Week 3-4)

**Goal:** Fill gaps in each category

| Category | Target | Sources |
|----------|--------|---------|
| Research | 15-20 | NSF REU list, industry lab pages |
| Fellowship | 10-15 | Fellowship lists, university career pages |
| Ecosystem | 8-12 | VC websites, founder communities |
| Accelerator | 5-10 | Y Combinator, university incubators |
| Grant | 8-12 | Foundation websites, grant databases |
| Scholarship | 5-10 | Major STEM scholarships |
| Innovation | 5-8 | MLH, major hackathon calendars |

### Phase 3: Community Growth (Week 5-8)

**Goal:** Enable sustainable contributions

- Announce repository in relevant communities (Twitter, Reddit, Discord)
- Respond to initial issues and PRs promptly
- Refine contribution process based on feedback
- Identify recurring contributors

### Phase 4: Automation Foundations (Month 2-3)

**Goal:** Reduce manual maintenance burden

- Add link validation script
- Add CSV validation against schema
- Set up GitHub Actions for automated checks
- Create simple deduplication tooling

### Phase 5: Scraping Integration (Month 3+)

**Goal:** Automated discovery pipeline

- LinkedIn opportunity posts
- Newsletter parsing (tech newsletters with opportunity sections)
- Program page monitoring for deadline updates
- Integration with your ingestion engine

### Quality Thresholds by Phase

| Phase | Entry Count | Quality Bar |
|-------|-------------|-------------|
| 1 | 30-50 | Only well-known, verifiable programs |
| 2 | 80-100 | Good programs, may be less well-known |
| 3 | 100-150 | Community-contributed, verified |
| 4+ | 150+ | Mix of curated and scraped (flagged) |

---

## Reviewing Contributions

### Pull Request Review Checklist

Before merging a PR:

- [ ] **Scope check** — Is this an appropriate opportunity type?
- [ ] **Not a duplicate** — Search existing entries by name and organization
- [ ] **Valid CSV** — Entry parses correctly without syntax errors
- [ ] **Required fields** — id, name, organization, category, url are present
- [ ] **Correct enums** — All enum fields use valid values from schema
- [ ] **Working links** — Verify URL and apply_url are accessible
- [ ] **Official source** — Information matches official program page
- [ ] **ID format** — Kebab-case, unique across dataset
- [ ] **Reasonable description** — Under 300 chars, informative, not promotional

### Issue Triage

**For "Add Opportunity" issues:**
1. Verify the submission is in scope
2. Check for duplicates
3. Verify information on official website
4. Either convert to CSV entry and merge, or request more info

**For "Report Outdated" issues:**
1. Verify the reported issue
2. Check official source
3. Update entry or archive if program discontinued

### Common Rejection Reasons

- Internship or full-time job
- Cannot verify legitimacy
- Duplicate entry exists
- Self-promotional without track record
- Too niche or regional

Always explain rejection reason in comment.

---

## Verifying Entries

### Link Verification

Check periodically (monthly recommended):

```bash
# Simple link check (manual)
# For each URL in the CSV, verify:
# 1. URL resolves (no 404)
# 2. Page content matches entry description
# 3. Program is still active

# Future: Automated link checker script
```

### Information Verification

For each entry, verify on official site:
- Program still exists and is active
- Deadline information is current
- Eligibility requirements haven't changed
- Compensation details are accurate

### Verification Timestamps

Update `last_verified` field when you verify an entry:

```csv
last_verified,2024-03-15
```

Entries not verified in 6+ months should be prioritized for review.

---

## Managing Entry Lifecycle

### Status Updates

Update `status` field as application cycles change:

| Situation | Status |
|-----------|--------|
| Applications currently open | `open` |
| Deadline passed, awaiting next cycle | `closed` |
| Next cycle announced, not yet open | `upcoming` |
| Cannot determine current status | `unknown` |

### Archiving Discontinued Programs

If a program is permanently discontinued:

1. **Option A:** Remove the row entirely
2. **Option B:** Move to a separate `data/archived.csv` (if maintaining historical record)

For Option B, add an `archived_date` and `archive_reason` field.

### Handling Temporary Pauses

If a program is "paused" but may return:
- Keep the entry
- Set `status` to `unknown`
- Add note: "Program paused as of [date], may return"

---

## Data Consistency

### ID Conventions

Format: `{org-name}-{program-name}` in kebab-case

Examples:
- `neo-scholar` (not `neo_scholar` or `NeoScholar`)
- `kleiner-perkins-fellows`
- `msft-research-reu`

### Preventing Duplicates

Before adding entries, search by:
1. Organization name
2. Program name (including variations)
3. URL domain

### Enum Consistency

Reference `data/schema.json` for valid enum values. Don't introduce new values without updating schema.

### Empty Categories

When generating the README, categories with no opportunities are automatically hidden. Do not display empty category sections — the generator skips them. This keeps the README clean and focused on what's actually available.

### Multi-value Field Formatting

Use pipe separator `|` for arrays:
- `audience`: `undergrad|masters|phd`
- `country`: `US|CA`
- `tags`: `vc|startup|network`

Never use commas within pipe-separated values (causes CSV parsing issues).

---

## Future Automation

This section documents how the current structure supports planned automation.

### Ingestion Pipeline

The schema is designed to accept scraped data with minimal transformation:

```
[Scraped Data] → [Normalization] → [Deduplication] → [CSV Append]
```

**Normalization mapping:**
- Map scraped category names to enum values
- Parse deadline strings to standard format
- Extract country codes from location text
- Generate ID from org + program name

### Deduplication Keys

Primary key: `id`

Deduplication candidates (for fuzzy matching):
- `name` + `organization`
- `url` (exact match)

### Source Tracking

The `source` and `source_type` fields track provenance:

| source_type | source field contains |
|-------------|----------------------|
| `official` | "Official website" |
| `linkedin` | LinkedIn post URL |
| `newsletter` | Newsletter name |
| `community` | Community/forum source |
| `manual` | Contributor info |
| `scraped` | Scraper identifier |

### Freshness Tracking

- `date_added` — When entry was created
- `last_verified` — Last manual verification

Future: Automated verification that checks `last_verified` and flags stale entries.

### Migration Path

When scaling beyond CSV:

1. **Phase 1 (Current):** CSV as source of truth
2. **Phase 2:** JSON export generated from CSV
3. **Phase 3:** SQLite database with CSV import/export
4. **Phase 4:** Full database with API layer

The schema is designed to be compatible across all phases.

### Scripts Directory (Future)

When adding automation, create:

```
scripts/
  validate.py       # Validate CSV against schema
  check_links.py    # Verify URLs are accessible
  normalize.py      # Standardize field values
  dedupe.py         # Find potential duplicates
  export_json.py    # Generate JSON from CSV
  scrape/
    linkedin.py     # LinkedIn scraper
    newsletter.py   # Newsletter parser
```

---

## Regular Maintenance Tasks

### Weekly
- Review new issues and PRs
- Triage "Add Opportunity" submissions

### Monthly
- Spot-check 10-20 random entries for accuracy
- Update status for programs with known deadlines
- Review entries with `status: unknown`

### Quarterly
- Full link verification pass
- Update `last_verified` timestamps
- Archive discontinued programs
- Review and update taxonomy if needed

### Annually
- Major deadline updates (many programs are annual)
- Schema review and updates
- Contributor acknowledgments

---

## Questions?

Open an issue tagged `maintainer-question` for process clarifications.
