# Submission Guide

This guide explains how to add new opportunities to the repository with correct formatting.

## Adding a New Entry

### Step 1: Gather Information

Before adding an entry, collect:

- Official program name
- Sponsoring organization
- Official program URL
- Application URL (if separate)
- Deadline information
- Eligibility requirements
- Key details (funding, duration, location)

**Always verify on the official website.** Don't rely on third-party sources.

### Step 2: Choose Your Method

**Via Issue (Recommended for most contributors):**
1. Go to Issues → New Issue
2. Select "Add New Opportunity"
3. Fill out the form
4. A maintainer will add the entry

**Via Pull Request (For contributors comfortable with CSV):**
1. Fork the repository
2. Add a row to `data/opportunities.csv`
3. Submit a PR

### Step 3: Format Your Entry

If submitting via PR, follow these conventions:

---

## Field Reference

### Required Fields

| Field | Description | Example |
|-------|-------------|---------|
| `id` | Unique identifier (kebab-case) | `neo-scholar` |
| `name` | Official program name | `Neo Scholar` |
| `organization` | Sponsoring org | `Neo` |
| `category` | Primary category | `fellowship` |
| `url` | Official program page | `https://neo.com/scholars` |

### Category Values

Use exactly one of:
- `research` — REUs, industry research, lab placements
- `fellowship` — Selective cohort programs with mentorship/funding
- `accelerator` — Startup accelerators and incubators
- `grant` — Project funding, research grants, travel grants
- `scholarship` — Merit/need-based financial awards
- `ecosystem` — VC fellowships, talent networks, founder programs
- `innovation` — Hackathons, competitions, challenges
- `leadership` — Community and technical leadership programs

### Subcategory Values

Optional but encouraged. See [taxonomy.md](taxonomy.md) for full list.

### Deadline Formatting

| Situation | Format | Example |
|-----------|--------|---------|
| Recurring annual deadline | Month name | `February` |
| Specific date | YYYY-MM-DD | `2024-02-15` |
| Rolling applications | `rolling` | `rolling` |
| To be announced | `tba` | `tba` |
| Multiple rounds | `varies` | `varies` |

For `varies`, add details in the `notes` field.

### Deadline Type

- `fixed` — Single deadline per cycle
- `rolling` — Continuous applications
- `multiple_rounds` — Several application windows
- `tba` — Not yet announced
- `varies_by_track` — Different deadlines for different tracks

### Audience Values

Pipe-separated list of eligible groups:
- `undergrad`
- `masters`
- `phd`
- `recent_grad`
- `early_career`
- `founder`
- `high_school`

Example: `undergrad|masters|phd`

### Region and Country

**Region** (broad scope):
- `us` — United States only
- `canada` — Canada only
- `us_canada` — Both US and Canada
- `north_america` — US, Canada, Mexico
- `global` — No geographic restriction
- `specific` — Use country field for specifics

**Country** (ISO 3166-1 alpha-2 codes, pipe-separated):
- `US` — United States
- `CA` — Canada
- `US|CA` — Both

### Status Values

- `open` — Currently accepting applications
- `closed` — Applications closed for current cycle
- `upcoming` — Will open soon
- `unknown` — Status not confirmed

### Compensation Values

- `paid` — Direct payment/salary
- `stipend` — Fixed stipend amount
- `grant` — Project/research funding
- `scholarship` — Educational funding
- `equity` — Equity in company (for accelerators)
- `unpaid` — No direct compensation
- `varies` — Depends on track/placement
- `unknown` — Not specified

### Location Type

- `in_person` — Must attend in person
- `remote` — Fully remote
- `hybrid` — Mix of in-person and remote
- `varies` — Depends on track or cohort

---

## Writing Good Descriptions

**Length:** Max 300 characters

**Include:**
- What makes this program distinctive
- Concrete details (funding amount, duration)
- Notable outcomes or alumni if relevant

**Avoid:**
- Marketing language ("amazing opportunity")
- Vague claims ("great for your career")
- Excessive superlatives

**Good examples:**

> Highly selective fellowship connecting technologists building impactful products. Strong alumni network in tech and startups.

> $100K grant over 2 years for founders under 23. Must defer or leave college. Strong support network and mentorship.

> 12-week research internship at MSR labs. Work with world-class researchers on cutting-edge projects. Competitive stipend + housing.

**Bad examples:**

> An incredible opportunity for passionate students! → Too vague, marketing tone

> Great program, highly recommend! → No useful information

---

## Tags

Use lowercase with underscores. Keep tags specific and useful for filtering.

**Good tags:** `ml`, `research`, `vc`, `startup`, `diversity`, `canada`, `systems`

**Bad tags:** `opportunity`, `great`, `students` (too generic)

Separate with pipes: `vc|startup|network`

---

## Common Mistakes

1. **Unescaped commas** — If a field contains commas, wrap in quotes: `"San Francisco, CA"`
2. **Duplicate IDs** — Always check existing entries
3. **Missing required fields** — id, name, organization, category, url are mandatory
4. **Wrong enum values** — Use exact values from schema
5. **Broken URLs** — Verify links before submitting
6. **Outdated info** — Check official site for current details

---

## Example Entry

```csv
id,name,organization,category,subcategory,region,country,audience,eligibility,url,apply_url,deadline,deadline_type,status,compensation,compensation_details,location_type,location,duration,cohort_season,tags,description,source,source_type,date_added,last_verified,notes
example-fellowship,Example Fellowship,Example Org,fellowship,cohort_fellowship,us_canada,US|CA,undergrad|masters,Must be enrolled full-time,https://example.com/fellowship,https://example.com/apply,March,fixed,upcoming,stipend,$5000 stipend,hybrid,New York,6 months,summer,tech|mentorship,Selective fellowship for technical students with startup interests. Includes mentorship and project funding.,Official website,official,2024-01-15,2024-01-15,Applications open in January
```

---

## Questions?

- See [taxonomy.md](taxonomy.md) for detailed field definitions
- Open an issue for clarification
- Check existing entries for examples
