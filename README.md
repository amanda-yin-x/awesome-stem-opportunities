# Awesome STEM Opportunities

> A curated list of fellowships, research programs, grants, accelerators, and selective opportunities for CS/STEM students in North America.

[![Awesome](https://awesome.re/badge.svg)](https://awesome.re)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

---

## Contents

- [What This Is](#what-this-is)
- [What This Is Not](#what-this-is-not)
- [Who This Is For](#who-this-is-for)
- [Opportunity Categories](#opportunity-categories)
- [Featured Opportunities](#featured-opportunities)
- [Full Directory](#full-directory)
- [How to Use This Repo](#how-to-use-this-repo)
- [Contributing](#contributing)
- [Disclaimer](#disclaimer)
- [Roadmap](#roadmap)
- [License](#license)

---

## What This Is

A carefully curated collection of **high-signal opportunities** for students and early-career individuals in CS and STEM fields. This repository focuses on:

- **Fellowships** — Selective programs offering mentorship, funding, and community
- **Research programs** — University and industry research experiences
- **Accelerators & incubators** — Startup-focused programs for student founders
- **Grants & funding** — Financial support for projects, research, or education
- **Scholarships** — Merit and need-based awards for STEM students
- **VC & startup ecosystem programs** — Investor-backed talent networks
- **Innovation & leadership programs** — Selective cohort-based experiences

The goal is to surface opportunities that are **selective, impactful, and often under-discovered** — the kind you hear about through word of mouth or niche communities.

## What This Is Not

- **Not an internship tracker.** There are excellent resources for internships elsewhere. This repo focuses on opportunities that are harder to find and often more formative.
- **Not a job board.** Full-time roles are out of scope.
- **Not exhaustive.** Quality over quantity. Every listing should be worth applying to.

## Who This Is For

- **Undergraduate students** in CS, engineering, math, physics, and related fields
- **Graduate students** (Masters and PhD) seeking research or fellowship opportunities
- **Recent graduates** (within 1-2 years) eligible for early-career programs
- **Student founders** looking for accelerators, grants, or VC programs

Primary geographic focus: **United States and Canada**, though some programs have broader eligibility.

## Opportunity Categories

| Category | Description |
|----------|-------------|
| 🔬 Research | REUs, industry research programs, lab placements |
| 🎓 Fellowship | Selective cohort programs with mentorship/funding |
| 🚀 Accelerator | Startup accelerators and incubators for students |
| 💰 Grant | Project funding, research grants, travel grants |
| 📚 Scholarship | Merit/need-based financial awards |
| 🌱 Ecosystem | VC fellowships, founder networks, talent programs |
| 🏆 Innovation | Hackathons, competitions, innovation challenges |
| 👥 Leadership | Community building, technical leadership programs |

See [docs/taxonomy.md](docs/taxonomy.md) for detailed category definitions.

---

## Featured Opportunities

See the [full data file](data/opportunities.csv) for complete listings with all details.

| Opportunity | Organization | Category | Deadline | Compensation | Notes |
|-------------|--------------|----------|----------|--------------|-------|
| [YC Startup School 2026](https://events.ycombinator.com/startup-school-2026) | Y Combinator | Accelerator | Mar 8 | Travel covered | 2-day in-person event in SF (Jul 25-26) |
| [The Eigenprize](https://eigen.build) | Eigenprize | Grant | Mar 9 | Up to $100k | 10-min app, no strings attached |
| [Comma Zero 2.0](https://comma.vc) | Comma VC | Ecosystem | Mar 13 | Equity funding | First check for student/young founders |
| [AI4PH Internship](https://ai4ph-hrtp.ca/internships/) | AI4PH-HRTP | Research | Mar 16 | $10k CAD | Part-time, health AI, Canada only |
| [OSV Fellowship](https://www.osvfellowship.com/) | O'Shaughnessy Ventures | Fellowship | Apr 30 | $100k or $10k+ | Equity-free, rolling review |
| [Founders Inc](https://f.inc/about) | Founders Inc | Accelerator | Rolling | Up to $250k | Emerging tech, SF-based, no pitches |

---

## Full Directory

The complete, structured dataset lives in [`data/opportunities.csv`](data/opportunities.csv).

**Columns in the full dataset:**
- `id` — Unique identifier
- `name` — Program name
- `organization` — Sponsoring organization
- `category` / `subcategory` — Classification
- `region` / `country` — Geographic scope
- `audience` — Target applicants
- `deadline` / `deadline_type` — Application timing
- `url` / `apply_url` — Official links
- `status` — Current application status
- And more — see [schema documentation](docs/taxonomy.md#schema-reference)

**Filtering the data:**

```bash
# Find all fellowships
grep ",fellowship," data/opportunities.csv

# Find programs open to undergrads in Canada
grep "canada" data/opportunities.csv | grep "undergrad"
```

Or open in any spreadsheet application for sorting and filtering.

---

## How to Use This Repo

1. **Browse** — Scan the featured table above or explore [`data/opportunities.csv`](data/opportunities.csv)
2. **Filter** — Use your spreadsheet app or command-line tools to filter by category, deadline, or audience
3. **Verify** — Always check the official program page for current deadlines and eligibility
4. **Contribute** — Found something missing? [Add it!](CONTRIBUTING.md)

---

## Contributing

We welcome contributions! Please read our [Contributing Guide](CONTRIBUTING.md) before submitting.

**Quick ways to help:**
- 🆕 [Submit a new opportunity](../../issues/new?template=add-opportunity.yml)
- 🔄 [Report an outdated listing](../../issues/new?template=report-outdated.yml)
- ✏️ Fix typos or improve descriptions via PR

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

## Roadmap

This repo is designed to grow from manual curation to automated discovery.

**Current (v0.1)**
- [x] Manual curation of high-signal opportunities
- [x] Structured CSV data format
- [x] Contribution workflow via GitHub issues/PRs

**Planned**
- [ ] Scraping engine for LinkedIn, newsletters, program pages
- [ ] JSON/SQLite data backend for better querying
- [ ] Automated freshness checking and link validation
- [ ] Filters: country, stage, major, citizenship, deadline, compensation
- [ ] Ranking/recommendation layer based on selectivity, value, relevance
- [ ] Web frontend for browsing and filtering

See [docs/maintainer-guide.md](docs/maintainer-guide.md) for technical notes on future automation.

---

## License

This project is licensed under the [MIT License](LICENSE).

You are free to use, modify, and distribute this data. Attribution is appreciated but not required.

---

**Maintainer:** [@amanda-yin-x](https://github.com/amanda-yin-x)

*Know a great opportunity that's missing? [Open an issue](../../issues/new?template=add-opportunity.yml) or submit a PR!*
