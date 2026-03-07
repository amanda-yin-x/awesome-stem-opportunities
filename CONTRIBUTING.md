# Contributing to Awesome STEM Opportunities

Thank you for helping curate this resource! This document explains how to contribute effectively.

## Table of Contents

- [What Belongs Here](#what-belongs-here)
- [What Does Not Belong](#what-does-not-belong)
- [How to Contribute](#how-to-contribute)
- [Submission Checklist](#submission-checklist)
- [Formatting Guidelines](#formatting-guidelines)
- [Review Process](#review-process)

---

## What Belongs Here

We curate **selective, high-signal opportunities** for CS/STEM students. Good additions include:

| Type | Examples |
|------|----------|
| **Fellowships** | Interact, Neo Scholar, KPCB Fellows |
| **Research programs** | REUs, industry research internships, lab placements |
| **Accelerators** | Y Combinator, student incubators, founder programs |
| **Grants** | Thiel Fellowship, Emergent Ventures, project funding |
| **Scholarships** | Merit and need-based awards for STEM students |
| **VC/Ecosystem programs** | Contrary VP, Rough Draft, VC talent networks |
| **Innovation programs** | Major hackathons, competitions, challenges |
| **Leadership programs** | Technical community programs, cohort experiences |

**Quality bar:**
- Selective (not open enrollment)
- Established track record or credible new program
- Clear value proposition (funding, mentorship, network, experience)
- Verifiable via official sources

## What Does Not Belong

- **Internships** — Standard industry internships are out of scope
- **Full-time jobs** — This is not a job board
- **Generic courses** — MOOCs, certifications, bootcamps
- **Paid programs** — Programs requiring significant tuition/fees
- **Self-promotional listings** — Your own startup's "fellowship" without track record
- **Regional-only programs** — Unless exceptionally notable
- **Expired one-time programs** — Only recurring or active programs

When in doubt, ask: "Would a well-connected student in the target audience already know about this?" If yes, it probably belongs. If it's a generic opportunity anyone could find via Google, it probably doesn't.

---

## How to Contribute

### Option 1: Open an Issue (Easiest)

1. Go to [Issues → New Issue](../../issues/new/choose)
2. Select "Add New Opportunity" template
3. Fill out the form
4. Submit — a maintainer will add it

Best for: Quick submissions, uncertain about formatting

### Option 2: Submit a Pull Request

1. Fork the repository
2. Edit `data/opportunities.csv` to add your entry
3. Follow the [formatting guidelines](#formatting-guidelines)
4. Submit a PR with a clear description

Best for: Multiple additions, contributors comfortable with Git

### Option 3: Report Issues

- **Outdated listing?** Use the "Report Outdated Entry" issue template
- **Broken link?** Same template, note the broken URL
- **Incorrect info?** Open a PR with corrections

---

## Submission Checklist

Before submitting, verify:

- [ ] **Official source** — You've verified info on the program's official website
- [ ] **Not a duplicate** — Search existing entries in `data/opportunities.csv`
- [ ] **In scope** — Matches the opportunity types listed above
- [ ] **Complete info** — At minimum: name, organization, category, URL
- [ ] **Working links** — All URLs are valid and point to official pages
- [ ] **Current program** — Not a one-time event that has ended

### For Pull Requests

- [ ] **Valid CSV** — Entry parses correctly (no unescaped commas in fields)
- [ ] **Consistent formatting** — Follows existing conventions
- [ ] **Unique ID** — Format: `org-name-program-name` in kebab-case
- [ ] **Enum values** — Category, status, etc. match schema values

---

## Formatting Guidelines

### CSV Field Rules

| Field | Format | Example |
|-------|--------|---------|
| `id` | kebab-case, unique | `neo-scholar` |
| `name` | Official program name | `Neo Scholar` |
| `deadline` | `YYYY-MM-DD`, month name, or `rolling` | `February` or `2024-02-15` |
| `audience` | Pipe-separated | `undergrad\|masters` |
| `country` | ISO 3166-1 alpha-2, pipe-separated | `US\|CA` |
| `tags` | Lowercase, underscore-separated | `vc\|startup\|network` |

### Deadlines

- **Fixed annual deadline:** Use month name (e.g., `January`)
- **Specific date known:** Use `YYYY-MM-DD`
- **Rolling:** Use `rolling`
- **Unknown:** Use `tba`
- **Multiple rounds:** Use `varies` and note in `notes` field

### Descriptions

- Keep under 300 characters
- Focus on what makes the program distinctive
- Avoid marketing language
- Include concrete details (funding amount, duration, notable alumni)

**Good:** "Highly selective fellowship connecting technologists building impactful products. Strong alumni network in tech and startups."

**Bad:** "An amazing opportunity for passionate students who want to change the world!"

---

## Review Process

### What Maintainers Check

1. **Legitimacy** — Is this a real, established program?
2. **Scope fit** — Does it match our criteria?
3. **Accuracy** — Is the information correct and current?
4. **Formatting** — Does it follow conventions?
5. **Duplicates** — Is it already listed?

### Timeline

- Issues: Reviewed within 1-2 weeks
- PRs: Reviewed within 1 week
- High-quality submissions may be merged same-day

### Rejection Reasons

We'll explain if we decline a submission. Common reasons:
- Out of scope (internship, job, paid course)
- Insufficient track record
- Cannot verify legitimacy
- Duplicate entry
- Regional program without broad relevance

---

## Questions?

- Open a [discussion](../../discussions) for general questions
- Tag `@maintainer` in issues if something is urgent
- See [docs/submission-guide.md](docs/submission-guide.md) for detailed formatting help

Thank you for contributing!
