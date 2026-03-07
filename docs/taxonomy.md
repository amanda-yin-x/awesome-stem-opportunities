# Taxonomy

This document defines the classification system for opportunities in this repository.

## Table of Contents

- [Categories](#categories)
- [Subcategories](#subcategories)
- [Audience](#audience)
- [Geography](#geography)
- [Compensation](#compensation)
- [Timing](#timing)
- [Status](#status)
- [Modality](#modality)
- [Schema Reference](#schema-reference)

---

## Categories

Primary classification for opportunities. Each entry has exactly one category.

| Value | Label | Description |
|-------|-------|-------------|
| `research` | Research | Research experiences including REUs, industry labs, academic placements |
| `fellowship` | Fellowship | Selective cohort-based programs with mentorship, funding, or community |
| `accelerator` | Accelerator | Startup accelerators, incubators, founder programs |
| `grant` | Grant | Direct funding for projects, research, travel, or ventures |
| `scholarship` | Scholarship | Merit or need-based financial awards for education |
| `ecosystem` | Ecosystem | VC fellowships, talent networks, investor-backed programs |
| `innovation` | Innovation | Hackathons, competitions, challenges, innovation programs |
| `leadership` | Leadership | Technical leadership, community building, ambassador programs |

### Category Selection Guide

**Research** — The primary purpose is conducting or contributing to research
- REU programs
- Industry research internships (MSR, Google Research, etc.)
- Academic lab placements
- Research mentorship programs

**Fellowship** — Selective cohort experience focused on development/community
- Programs like Interact, MLH Fellowship
- Technical fellowship programs
- Cohort-based learning experiences

**Accelerator** — Focus is on building/launching a startup or venture
- Y Combinator, Techstars (student programs)
- University incubators
- Founder residencies

**Grant** — Direct financial award for a project or purpose
- Thiel Fellowship, Emergent Ventures
- Research grants
- Travel grants for conferences
- Project funding

**Scholarship** — Financial award for educational expenses
- Merit scholarships
- Need-based financial aid programs
- Field-specific scholarships

**Ecosystem** — Connection to VC/startup ecosystem as primary value
- VC campus representative programs (Contrary, Rough Draft)
- Investor talent networks
- Founder community programs

**Innovation** — Event-based programs centered on building/competing
- Major hackathons (Hack the North, TreeHacks)
- Case competitions
- Innovation challenges

**Leadership** — Focus on building community or leadership skills
- Google Developer Student Clubs
- GitHub Campus Experts
- Technical ambassador programs

---

## Subcategories

More specific classification within categories. Optional but encouraged.

### Research Subcategories

| Value | Description |
|-------|-------------|
| `reu` | NSF Research Experiences for Undergraduates |
| `industry_research` | Research at industry labs (MSR, FAIR, etc.) |
| `academic_research` | University lab placements outside REU |

### Fellowship Subcategories

| Value | Description |
|-------|-------------|
| `cohort_fellowship` | Community-focused cohort experience |
| `technical_fellowship` | Skills/technical development focus |
| `founder_fellowship` | Fellowship for aspiring founders |

### Accelerator Subcategories

| Value | Description |
|-------|-------------|
| `startup_accelerator` | Traditional accelerator with funding |
| `student_incubator` | University-affiliated incubator |

### Grant Subcategories

| Value | Description |
|-------|-------------|
| `project_grant` | Funding for specific projects |
| `research_grant` | Research-focused funding |
| `travel_grant` | Conference/event travel support |

### Scholarship Subcategories

| Value | Description |
|-------|-------------|
| `merit_scholarship` | Achievement-based award |
| `need_based_scholarship` | Financial need-based award |
| `field_specific_scholarship` | Restricted to specific major/field |

### Ecosystem Subcategories

| Value | Description |
|-------|-------------|
| `vc_fellowship` | VC-sponsored fellowship/placement |
| `talent_network` | Talent identification program |
| `founder_network` | Community for founders |

### Innovation Subcategories

| Value | Description |
|-------|-------------|
| `hackathon` | Time-limited building event |
| `competition` | Competitive challenge with judging |
| `challenge` | Open-ended innovation challenge |

### Leadership Subcategories

| Value | Description |
|-------|-------------|
| `community_program` | Campus community building |
| `technical_leadership` | Technical mentorship/leadership |

### Universal

| Value | Description |
|-------|-------------|
| `other` | Doesn't fit other subcategories |

---

## Audience

Who is eligible to apply. Entries may have multiple values (pipe-separated).

| Value | Description |
|-------|-------------|
| `undergrad` | Currently enrolled undergraduate students |
| `masters` | Currently enrolled Master's students |
| `phd` | Currently enrolled PhD students |
| `recent_grad` | Graduated within past 1-2 years |
| `early_career` | Early career professionals (typically 0-5 years experience) |
| `founder` | Student or early-career founders |
| `high_school` | High school students |

### Audience Guidelines

- Use the most specific applicable values
- `undergrad` includes community college students
- `recent_grad` typically means 0-2 years post-graduation
- `founder` is additive — use alongside student status
- When uncertain, err toward inclusivity

---

## Geography

### Region

Broad geographic scope of eligibility or program location.

| Value | Description |
|-------|-------------|
| `us` | United States only |
| `canada` | Canada only |
| `us_canada` | United States and Canada |
| `north_america` | US, Canada, and Mexico |
| `global` | Open to all countries (or minimal restrictions) |
| `specific` | Specific country list (use country field) |

### Country

ISO 3166-1 alpha-2 country codes. Use for specific eligibility.

Common values:
- `US` — United States
- `CA` — Canada
- `MX` — Mexico
- `GB` — United Kingdom
- `DE` — Germany

Pipe-separated for multiple: `US|CA`

---

## Compensation

What participants receive.

| Value | Description |
|-------|-------------|
| `paid` | Direct payment (salary, hourly wage) |
| `stipend` | Fixed stipend amount |
| `grant` | Project or research funding |
| `scholarship` | Educational expense coverage |
| `equity` | Equity stake (accelerators) |
| `unpaid` | No direct financial compensation |
| `varies` | Depends on track, placement, or other factors |
| `unknown` | Compensation not specified |

### compensation_details

Free-text field for specifics:
- `$10,000 stipend`
- `$100K over 2 years`
- `Competitive salary + housing`
- `Up to $50K in funding`

---

## Timing

### deadline_type

Nature of the application deadline.

| Value | Description |
|-------|-------------|
| `fixed` | Single deadline per application cycle |
| `rolling` | Applications reviewed continuously |
| `multiple_rounds` | Several application windows |
| `tba` | Deadline not yet announced |
| `varies_by_track` | Different deadlines for different tracks |

### deadline

Application deadline in one of these formats:
- `YYYY-MM-DD` — Specific date (e.g., `2024-02-15`)
- Month name — Recurring annual (e.g., `February`)
- `rolling` — No fixed deadline
- `tba` — To be announced
- `varies` — Multiple deadlines (detail in notes)

### cohort_season

When the program runs.

| Value | Description |
|-------|-------------|
| `spring` | January - April |
| `summer` | May - August |
| `fall` | September - December |
| `winter` | December - February |
| `year_round` | Ongoing throughout year |
| `varies` | Different cohorts at different times |

### duration

Free-text field for program length:
- `10 weeks`
- `3 months`
- `1 year`
- `ongoing`
- `36 hours` (for hackathons)

---

## Status

Current application status.

| Value | Description |
|-------|-------------|
| `open` | Currently accepting applications |
| `closed` | Applications closed for current cycle |
| `upcoming` | Will open soon (announced) |
| `unknown` | Cannot determine current status |

### Status Update Cadence

- Update when deadlines pass
- Update when new cycles announced
- Mark `unknown` if status unclear for 3+ months

---

## Modality

### location_type

How participants engage with the program.

| Value | Description |
|-------|-------------|
| `in_person` | Must attend in physical location |
| `remote` | Fully remote participation |
| `hybrid` | Mix of in-person and remote |
| `varies` | Depends on track or cohort |

### location

Free-text field for physical location:
- `San Francisco`
- `New York, NY`
- `Multiple locations`
- `Stanford University`

---

## Schema Reference

Complete field list with requirements.

### Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique kebab-case identifier |
| `name` | string | Official program name |
| `organization` | string | Sponsoring organization |
| `category` | enum | Primary category |
| `url` | string | Official program URL |

### Recommended Fields

| Field | Type | Description |
|-------|------|-------------|
| `subcategory` | enum | Specific classification |
| `region` | enum | Geographic scope |
| `audience` | array | Target applicants |
| `deadline` | string | Application deadline |
| `status` | enum | Current status |

### Optional Fields

| Field | Type | Description |
|-------|------|-------------|
| `country` | array | Specific countries |
| `eligibility` | string | Brief eligibility summary |
| `apply_url` | string | Direct application URL |
| `deadline_type` | enum | Nature of deadline |
| `compensation` | enum | Compensation type |
| `compensation_details` | string | Specific compensation info |
| `location_type` | enum | Program modality |
| `location` | string | Physical location |
| `duration` | string | Program length |
| `cohort_season` | enum | When program runs |
| `tags` | array | Additional searchable tags |
| `description` | string | Brief description (max 300 chars) |
| `source` | string | Where listing was found |
| `source_type` | enum | Type of source |
| `date_added` | date | When entry was added |
| `last_verified` | date | When entry was last verified |
| `notes` | string | Internal notes |

---

## Adding New Enum Values

If an opportunity doesn't fit existing categories:

1. Check if it genuinely doesn't fit (not just unusual)
2. Open an issue proposing the new value
3. Include examples and justification
4. If approved, update:
   - This taxonomy document
   - `data/schema.json`
   - Any validation scripts
