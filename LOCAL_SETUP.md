# Local Setup & Architecture Guide

> Internal documentation for the awesome-stem-opportunities automation pipeline.

---

## Table of Contents

- [What We Built](#what-we-built)
- [Architecture Overview](#architecture-overview)
- [File Structure](#file-structure)
- [Setup Instructions](#setup-instructions)
- [Running the Scripts](#running-the-scripts)
- [GitHub Actions Workflows](#github-actions-workflows)
- [How Each Component Works](#how-each-component-works)
- [Data Flow](#data-flow)
- [Adding New Opportunities](#adding-new-opportunities)
- [Troubleshooting](#troubleshooting)

---

## What We Built

An end-to-end automated pipeline for curating STEM opportunities:

1. **Data Storage**: CSV as source of truth with JSON schema validation
2. **Validation**: Pydantic models ensure data integrity
3. **Link Verification**: Async HTTP checks for all URLs
4. **README Generation**: Auto-generates full opportunity tables from CSV
5. **Scraping Engine**: Discovers new opportunities from web sources
6. **Deduplication**: Prevents duplicate entries via fuzzy matching
7. **GitHub Actions**: Automated daily verification, weekly scraping, and README updates

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         DATA SOURCES                                     │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐                │
│  │ LinkedIn │  │ Web Pages│  │Newsletters│  │  Manual  │                │
│  │ (Google) │  │          │  │          │  │  Entry   │                │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘                │
│       │             │             │             │                        │
│       └─────────────┴─────────────┴─────────────┘                        │
│                           │                                              │
│                           ▼                                              │
│                  ┌────────────────┐                                      │
│                  │    SCRAPERS    │                                      │
│                  │  (base.py,     │                                      │
│                  │   web.py)      │                                      │
│                  └────────┬───────┘                                      │
│                           │                                              │
│                           ▼                                              │
│                  ┌────────────────┐                                      │
│                  │   NORMALIZER   │  Maps raw data to schema             │
│                  │ (normalize.py) │  Infers categories, parses dates     │
│                  └────────┬───────┘                                      │
│                           │                                              │
│                           ▼                                              │
│                  ┌────────────────┐                                      │
│                  │    DEDUPER     │  Exact ID, URL, fuzzy name match     │
│                  │  (dedupe.py)   │                                      │
│                  └────────┬───────┘                                      │
│                           │                                              │
│                           ▼                                              │
│                  ┌────────────────┐                                      │
│                  │     MERGER     │  Combines new + existing entries     │
│                  │   (merge.py)   │                                      │
│                  └────────┬───────┘                                      │
│                           │                                              │
│                           ▼                                              │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │                     CSV (Source of Truth)                          │ │
│  │                   data/opportunities.csv                           │ │
│  └────────────────────────────────────────────────────────────────────┘ │
│                           │                                              │
│            ┌──────────────┼──────────────┐                              │
│            │              │              │                              │
│            ▼              ▼              ▼                              │
│    ┌──────────────┐ ┌──────────────┐ ┌──────────────┐                   │
│    │  VALIDATOR   │ │   VERIFIER   │ │  GENERATOR   │                   │
│    │(validate.py) │ │ (verify.py)  │ │ (readme.py)  │                   │
│    │              │ │              │ │              │                   │
│    │ Schema check │ │ Link checker │ │ Markdown gen │                   │
│    └──────────────┘ └──────────────┘ └──────┬───────┘                   │
│                                             │                            │
│                                             ▼                            │
│                                    ┌──────────────┐                      │
│                                    │  README.md   │                      │
│                                    │ (Full table) │                      │
│                                    └──────────────┘                      │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## File Structure

```
awesome-stem-opportunities/
├── scripts/                    # Python automation scripts
│   ├── __init__.py
│   ├── config.py              # Constants, paths, enums
│   ├── models.py              # Pydantic data models
│   ├── validate.py            # CSV schema validation
│   ├── main.py                # CLI entry point
│   │
│   ├── scraper/               # Web scraping modules
│   │   ├── __init__.py
│   │   ├── base.py            # Base scraper with rate limiting
│   │   └── web.py             # Generic web page scraper
│   │
│   ├── verifier/              # Link verification
│   │   ├── __init__.py
│   │   └── verify.py          # Async URL checker
│   │
│   ├── processor/             # Data processing
│   │   ├── __init__.py
│   │   ├── normalize.py       # Map scraped data to schema
│   │   ├── dedupe.py          # Deduplication logic
│   │   └── merge.py           # Merge new + existing data
│   │
│   └── generator/             # README generation
│       ├── __init__.py
│       └── readme.py          # Generate markdown tables
│
├── data/
│   ├── opportunities.csv      # Source of truth (all entries)
│   └── schema.json            # JSON schema for validation
│
├── .github/
│   └── workflows/
│       ├── daily-verify.yml   # Daily link checks (6 AM UTC)
│       ├── weekly-scrape.yml  # Weekly discovery (Sun 8 AM UTC)
│       └── update-readme.yml  # Auto-update on CSV change
│
├── docs/
│   ├── taxonomy.md            # Category definitions
│   ├── submission-guide.md    # How to submit opportunities
│   └── maintainer-guide.md    # Maintenance procedures
│
├── requirements.txt           # Python dependencies
├── pyproject.toml             # Package configuration
├── venv/                      # Virtual environment (local only)
└── README.md                  # Auto-generated from CSV
```

---

## Setup Instructions

### Prerequisites

- Python 3.10+ (macOS: `brew install python@3.12`)
- Git

### Step 1: Clone the Repository

```bash
git clone https://github.com/amanda-yin-x/awesome-stem-opportunities.git
cd awesome-stem-opportunities
```

### Step 2: Create Virtual Environment

```bash
python3 -m venv venv
```

### Step 3: Activate Virtual Environment

```bash
# macOS/Linux
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### Step 4: Install Dependencies

```bash
pip install -r requirements.txt
```

### Verify Installation

```bash
python3 -m scripts.main validate
# Should output: ✓ Validation passed!
```

---

## Running the Scripts

**Always activate the virtual environment first:**

```bash
source venv/bin/activate
```

### Available Commands

| Command | Description |
|---------|-------------|
| `python3 -m scripts.main validate` | Validate CSV against schema |
| `python3 -m scripts.main verify` | Check all URLs are working |
| `python3 -m scripts.main generate` | Regenerate README from CSV |
| `python3 -m scripts.main scrape --sources web` | Run web scraper |

### Examples

```bash
# Full validation + regeneration workflow
python3 -m scripts.main validate && python3 -m scripts.main generate

# Verify links (takes ~30 seconds for 6 entries)
python3 -m scripts.main verify

# Check specific command help
python3 -m scripts.main --help
```

---

## GitHub Actions Workflows

### 1. Daily Link Verification (`daily-verify.yml`)

**Schedule:** Every day at 6 AM UTC

**What it does:**
1. Checkout repository
2. Install Python dependencies
3. Validate CSV schema
4. Verify all URLs (mark broken links)
5. Regenerate README
6. Commit and push changes (if any)

**Manual trigger:** Go to Actions → "Daily Link Verification" → "Run workflow"

### 2. Weekly Opportunity Discovery (`weekly-scrape.yml`)

**Schedule:** Every Sunday at 8 AM UTC

**What it does:**
1. Run scrapers (Google search for LinkedIn posts, web pages)
2. Normalize discovered opportunities
3. Deduplicate against existing entries
4. Verify new entries
5. Regenerate README
6. **Create a Pull Request** for human review

**Why PR instead of direct commit:** Scraped data needs human verification before going live.

### 3. README Auto-Update (`update-readme.yml`)

**Trigger:** Any push to `main` that modifies `data/opportunities.csv`

**What it does:**
1. Validate CSV
2. Regenerate README with latest data
3. Commit and push

---

## How Each Component Works

### 1. Data Models (`scripts/models.py`)

Pydantic models define the opportunity schema:

```python
class Opportunity(BaseModel):
    id: str                    # Unique kebab-case ID
    name: str                  # Program name
    organization: str          # Hosting org
    category: CategoryType     # research, fellowship, accelerator, etc.
    url: HttpUrl              # Official website
    deadline: Optional[str]    # YYYY-MM-DD or "rolling"
    status: StatusType         # open, closed, upcoming, unknown
    compensation: Optional[str]
    # ... 20+ more fields
```

### 2. Validator (`scripts/validate.py`)

- Loads `data/schema.json`
- Parses every row of `data/opportunities.csv`
- Validates field types, enum values, required fields
- Reports errors with line numbers
- Exits with code 1 if invalid (fails CI)

### 3. Verifier (`scripts/verifier/verify.py`)

- Uses `httpx` for async HTTP requests
- Checks both `url` and `apply_url` fields
- Handles redirects gracefully
- Updates `last_verified` timestamp for valid links
- Logs broken links for manual review

### 4. README Generator (`scripts/generator/readme.py`)

- Reads CSV and sorts by deadline (soonest first)
- Generates three sections:
  - **Upcoming Deadlines**: Fixed deadline opportunities
  - **Rolling / Ongoing**: Rolling deadline programs
  - **By Category**: Collapsible sections per category
- Empty categories are automatically hidden
- Preserves static sections (intro, contributing, etc.)

### 5. Scraper (`scripts/scraper/`)

- **Base scraper**: Rate limiting, retry logic, error handling
- **Web scraper**: Generic page fetcher with configurable selectors
- **LinkedIn (via Google)**: Searches `site:linkedin.com` for opportunity posts

### 6. Processor (`scripts/processor/`)

- **Normalizer**: Maps raw scraped data to schema format
  - Infers category from keywords
  - Parses various deadline formats
  - Generates ID from org + program name
- **Deduper**: Prevents duplicates via:
  - Exact ID match
  - Exact URL match
  - Fuzzy name + organization matching (>85% similarity)
- **Merger**: Combines new opportunities with existing CSV

---

## Data Flow

### Manual Entry Flow

```
1. Edit data/opportunities.csv directly
2. Run: python3 -m scripts.main validate
3. Run: python3 -m scripts.main generate
4. Commit and push
5. README auto-updates via GitHub Action
```

### Automated Discovery Flow

```
1. Weekly scrape workflow runs (Sunday 8 AM UTC)
2. Scrapers fetch from configured sources
3. Normalizer converts to schema format
4. Deduper checks against existing entries
5. Merger adds new entries to CSV
6. Verifier checks new links
7. Generator updates README
8. PR created for human review
9. Maintainer reviews and merges (or rejects)
```

---

## Adding New Opportunities

### Option 1: Direct CSV Edit

1. Open `data/opportunities.csv`
2. Add a new row with all required fields:
   - `id`: kebab-case unique identifier (e.g., `neo-scholar`)
   - `name`: Program name
   - `organization`: Hosting organization
   - `category`: One of: research, fellowship, accelerator, grant, scholarship, ecosystem, innovation, leadership
   - `url`: Official website URL
   - `date_added`: Today's date (YYYY-MM-DD)
   - `last_verified`: Today's date
3. Run validation: `python3 -m scripts.main validate`
4. Regenerate README: `python3 -m scripts.main generate`
5. Commit and push

### Option 2: Issue Template

1. Go to GitHub Issues
2. Click "New Issue"
3. Select "Add Opportunity" template
4. Fill out the form
5. Maintainer reviews and adds to CSV

---

## Troubleshooting

### "command not found: pip"

Use `pip3` instead, or activate the virtual environment first:

```bash
source venv/bin/activate
pip install -r requirements.txt
```

### "externally-managed-environment" error

macOS Homebrew Python requires a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Validation fails

Check the error message for line numbers. Common issues:
- Invalid category value (must be from allowed enum)
- Invalid URL format
- Missing required field

### Links showing as broken

Some sites block automated requests. The verifier logs these for manual review. Check:
- Is the URL actually broken?
- Does the site require JavaScript?
- Is there a CAPTCHA?

### README not updating

Ensure you:
1. Ran `python3 -m scripts.main generate`
2. Committed the changes
3. Pushed to main branch

---

## Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| pydantic | >=2.0 | Data validation |
| httpx | >=0.27 | Async HTTP client |
| beautifulsoup4 | >=4.12 | HTML parsing |
| lxml | >=5.0 | Fast XML/HTML parser |
| python-dateutil | >=2.9 | Date parsing |
| jsonschema | >=4.21 | JSON schema validation |
| PyYAML | >=6.0 | YAML configuration |

---

## Current Data

As of setup, 6 verified opportunities:

| Name | Category | Deadline |
|------|----------|----------|
| YC Startup School 2026 | Accelerator | Mar 8 |
| The Eigenprize | Grant | Mar 9 |
| Comma Zero 2.0 | Ecosystem | Mar 13 |
| AI4PH Internship | Research | Mar 16 |
| OSV Fellowship | Fellowship | Apr 30 |
| Founders Inc | Accelerator | Rolling |

---

## Next Steps

1. **Add more opportunities**: Populate with 30-50 high-signal programs
2. **Test GitHub Actions**: Push to trigger workflows
3. **Configure scraper sources**: Add specific program pages to monitor
4. **Set up notifications**: Get alerts when PRs are created

---

*Last updated: 2026-03-07*
