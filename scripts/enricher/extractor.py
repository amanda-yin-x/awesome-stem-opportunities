"""Extract structured opportunity fields from HTML pages.

Each extraction method returns a value or None. The extractor never
guesses — if it cannot find reliable evidence for a field, it returns
None so the field is left blank.
"""

import json
import re
from datetime import date
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

from bs4 import BeautifulSoup

from ..config import SUBCATEGORIES


class OpportunityExtractor:
    """Extract structured opportunity data from one or more fetched pages."""

    def __init__(self):
        self.pages: List[Dict[str, str]] = []  # [{"url": ..., "html": ...}]

    def add_page(self, url: str, html: str):
        self.pages.append({"url": url, "html": html})

    def extract_all(self) -> Dict[str, Any]:
        """Run all extraction methods and return a dict of field values."""
        if not self.pages:
            return {}

        soups = []
        all_text = ""
        for page in self.pages:
            soup = BeautifulSoup(page["html"], "lxml")
            soups.append({"url": page["url"], "soup": soup})
            all_text += "\n" + _get_clean_text(soup)

        main_soup = soups[0]["soup"]
        main_url = self.pages[0]["url"]

        result: Dict[str, Any] = {}
        result["url"] = main_url
        result["name"] = self._extract_name(main_soup)
        result["organization"] = self._extract_organization(main_soup, main_url)
        result["description"] = self._extract_description(main_soup)
        result["category"] = self._infer_category(all_text)
        result["subcategory"] = self._infer_subcategory(all_text)
        result["apply_url"] = self._extract_apply_url(soups, main_url)

        dl = self._extract_deadline(all_text, soups)
        result["deadline"] = dl.get("deadline")
        result["deadline_type"] = dl.get("deadline_type")

        result["status"] = self._infer_status(all_text, result.get("deadline"))
        result["eligibility"] = self._extract_eligibility(all_text, soups)
        result["audience"] = self._infer_audience(all_text)

        geo = self._infer_region(all_text)
        result["region"] = geo.get("region")
        result["country"] = geo.get("country")

        comp = self._extract_compensation(all_text, soups)
        result["compensation"] = comp.get("compensation")
        result["compensation_details"] = comp.get("compensation_details")

        result["location_type"] = self._infer_location_type(all_text)
        result["location"] = self._extract_location(all_text)
        result["duration"] = self._extract_duration(all_text)
        result["cohort_season"] = self._infer_cohort_season(all_text)
        result["tags"] = self._generate_tags(all_text, result)

        # Remove None values
        return {k: v for k, v in result.items() if v is not None}

    # ------------------------------------------------------------------
    # Name
    # ------------------------------------------------------------------
    def _extract_name(self, soup: BeautifulSoup) -> Optional[str]:
        candidates: List[tuple] = []

        og = soup.find("meta", property="og:title")
        if og and og.get("content", "").strip():
            candidates.append((0, og["content"].strip()))

        tw = soup.find("meta", attrs={"name": "twitter:title"})
        if tw and tw.get("content", "").strip():
            candidates.append((3, tw["content"].strip()))

        h1 = soup.find("h1")
        if h1:
            t = h1.get_text(strip=True)
            if t and len(t) < 150:
                candidates.append((1, t))

        title_tag = soup.find("title")
        if title_tag and title_tag.string:
            raw = title_tag.string.strip()
            for sep in [" | ", " — ", " - ", " :: ", " · "]:
                if sep in raw:
                    raw = raw.split(sep)[0].strip()
                    break
            candidates.append((2, raw))

        candidates.sort(key=lambda x: x[0])
        if candidates:
            name = candidates[0][1]
            # Strip common page-type prefixes that leak into titles
            for prefix in ["About ", "About | ", "Home | ", "Home - "]:
                if name.startswith(prefix) and len(name) > len(prefix) + 3:
                    name = name[len(prefix):]
                    break
            return name[:100] if len(name) > 100 else name
        return None

    # ------------------------------------------------------------------
    # Organization
    # ------------------------------------------------------------------
    def _extract_organization(self, soup: BeautifulSoup, url: str) -> Optional[str]:
        candidates: List[tuple] = []

        og = soup.find("meta", property="og:site_name")
        if og and og.get("content", "").strip():
            val = og["content"].strip()
            # Strip tagline suffixes: "Kleiner Perkins | Make History" -> "Kleiner Perkins"
            for sep in [" | ", " — ", " - ", " :: "]:
                if sep in val:
                    val = val.split(sep)[0].strip()
                    break
            if len(val) > 1:
                candidates.append((0, val))

        # JSON-LD structured data
        for script in soup.find_all("script", type="application/ld+json"):
            try:
                data = json.loads(script.string or "")
                if isinstance(data, list):
                    data = data[0] if data else {}
                if isinstance(data, dict):
                    org_name = None
                    if data.get("@type") == "Organization":
                        org_name = data.get("name")
                    elif isinstance(data.get("publisher"), dict):
                        org_name = data["publisher"].get("name")
                    elif isinstance(data.get("author"), dict):
                        org_name = data["author"].get("name")
                    if org_name and 2 < len(org_name) < 80:
                        candidates.append((1, org_name.strip()))
            except (json.JSONDecodeError, TypeError, AttributeError):
                pass

        # Copyright notice
        text = _get_clean_text(soup)
        m = re.search(
            r'(?:©|\bcopyright\b)\s*(?:\d{4}\s*)?([A-Z][A-Za-z\s&.,]+?)(?:\.|,|\s+All|\s*\||\s*[-–])',
            text, re.IGNORECASE,
        )
        if m:
            org = m.group(1).strip().rstrip(",. ")
            if 2 < len(org) < 60:
                candidates.append((2, org))

        # Domain name fallback (skip very short names like "F" from f.inc)
        domain_org = _org_from_url(url)
        if domain_org and len(domain_org) > 2:
            candidates.append((3, domain_org))

        candidates.sort(key=lambda x: x[0])
        return candidates[0][1] if candidates else None

    # ------------------------------------------------------------------
    # Description
    # ------------------------------------------------------------------
    def _extract_description(self, soup: BeautifulSoup) -> Optional[str]:
        for meta in [
            soup.find("meta", property="og:description"),
            soup.find("meta", attrs={"name": "description"}),
        ]:
            if meta and meta.get("content", "").strip():
                desc = meta["content"].strip()
                if len(desc) > 20:
                    return desc[:300]

        main = _get_main_content_text(soup)
        if main and len(main) > 30:
            text = main[:350]
            for i in range(min(300, len(text)), 50, -1):
                if text[i] in ".!?":
                    return text[: i + 1]
            return text[:300]
        return None

    # ------------------------------------------------------------------
    # Category / subcategory
    # ------------------------------------------------------------------
    _CATEGORY_KEYWORDS = {
        "research": [
            "research experience", "reu ", "research program",
            "lab placement", "research intern", "principal investigator",
        ],
        "fellowship": [
            "fellowship", "fellows program", "cohort-based",
            "fellow program", "the fellowship",
        ],
        "accelerator": [
            "accelerator", "incubator", "startup school",
            "demo day", "y combinator",
        ],
        "grant": [
            "grant program", "prize money", "award money",
            "funding opportunity", "no strings", "project funding",
        ],
        "scholarship": [
            "scholarship", "tuition", "financial aid", "merit award",
        ],
        "ecosystem": [
            "venture capital", "vc fellowship", "talent network",
            "investor program",
        ],
        "innovation": [
            "hackathon", "competition", "challenge",
        ],
        "leadership": [
            "ambassador", "campus rep", "community leader",
        ],
    }

    def _infer_category(self, text: str) -> str:
        t = text.lower()
        scores: Dict[str, float] = {}
        for cat, kws in self._CATEGORY_KEYWORDS.items():
            score = sum(2 for kw in kws if kw in t)
            if score > 0:
                scores[cat] = score
        return max(scores, key=scores.get) if scores else "fellowship"

    _SUBCATEGORY_KEYWORDS = {
        "reu": ["reu program", "research experience for undergrad", "nsf reu"],
        "industry_research": ["industry research", "corporate research"],
        "academic_research": ["academic research", "university research"],
        "cohort_fellowship": ["cohort", "community of fellows"],
        "technical_fellowship": ["technical fellowship", "engineering fellowship"],
        "founder_fellowship": ["founder fellowship", "entrepreneur fellowship"],
        "startup_accelerator": ["startup accelerator", "seed funding", "accelerator program"],
        "student_incubator": ["student incubator", "university incubator"],
        "project_grant": ["project grant", "project funding", "build grant"],
        "research_grant": ["research grant", "research funding"],
        "travel_grant": ["travel grant", "conference travel"],
        "merit_scholarship": ["merit scholarship", "merit-based"],
        "need_based_scholarship": ["need-based scholarship", "financial need"],
        "vc_fellowship": ["vc fellowship", "venture fellow"],
        "talent_network": ["talent network", "talent program"],
        "founder_network": ["founder network", "founder community"],
        "hackathon": ["hackathon"],
        "competition": ["competition", "contest"],
        "challenge": ["innovation challenge"],
        "community_program": ["community program", "ambassador program"],
        "technical_leadership": ["technical leadership"],
    }

    def _infer_subcategory(self, text: str) -> Optional[str]:
        t = text.lower()
        for sub, kws in self._SUBCATEGORY_KEYWORDS.items():
            if any(kw in t for kw in kws) and sub in SUBCATEGORIES:
                return sub
        return None

    # ------------------------------------------------------------------
    # Apply URL
    # ------------------------------------------------------------------
    def _extract_apply_url(self, soups: List[Dict], main_url: str) -> Optional[str]:
        apply_words = ["apply", "application", "register", "sign up", "submit application"]
        from urllib.parse import urljoin

        for soup_info in soups:
            soup = soup_info["soup"]
            for link in soup.find_all("a", href=True):
                href = link.get("href", "").strip()
                text = link.get_text(strip=True).lower()

                is_apply_text = any(kw in text for kw in apply_words)
                is_apply_href = any(
                    kw in href.lower() for kw in ["apply", "application", "register"]
                )

                if is_apply_text or is_apply_href:
                    full = urljoin(soup_info["url"], href)
                    if full != main_url and full.startswith("http"):
                        return full
        return None

    # ------------------------------------------------------------------
    # Deadline
    # ------------------------------------------------------------------
    _ROLLING_PATTERNS = [
        r"rolling\s+(?:admission|application|basis|deadline)",
        r"(?:applications?\s+(?:are\s+)?accepted|apply)\s+on\s+a\s+rolling",
        r"no\s+(?:fixed\s+)?deadline",
        r"accept(?:ing)?\s+applications?\s+year[\s-]?round",
    ]

    _DEADLINE_PATTERNS = [
        # "Deadline: March 15, 2024"
        r'(?:deadline|due(?:\s+date)?|closes?|closing(?:\s+date)?|apply\s+by|'
        r'applications?\s+(?:due|close))[:\s]+([A-Z][a-z]+\s+\d{1,2}(?:,?\s+\d{4})?)',
        # "Deadline: 2024-03-15"
        r'(?:deadline|due(?:\s+date)?|closes?|apply\s+by)[:\s]+(\d{4}[-/]\d{1,2}[-/]\d{1,2})',
        # "Deadline: March 2024"
        r'(?:deadline|due(?:\s+date)?|closes?|apply\s+by)[:\s]+([A-Z][a-z]+\s+\d{4})',
        # "Applications close March 15"
        r'applications?\s+close\s+(?:on\s+)?([A-Z][a-z]+\s+\d{1,2}(?:,?\s+\d{4})?)',
    ]

    def _extract_deadline(self, all_text: str, soups: List[Dict]) -> Dict[str, Optional[str]]:
        result: Dict[str, Optional[str]] = {"deadline": None, "deadline_type": None}
        t = all_text.lower()

        # Rolling?
        for pat in self._ROLLING_PATTERNS:
            if re.search(pat, t):
                return {"deadline": "rolling", "deadline_type": "rolling"}

        # Structured data (schema.org applicationDeadline)
        for soup_info in soups:
            for script in soup_info["soup"].find_all("script", type="application/ld+json"):
                try:
                    data = json.loads(script.string or "")
                    if isinstance(data, list):
                        data = data[0] if data else {}
                    if isinstance(data, dict):
                        dl = data.get("applicationDeadline") or data.get("endDate")
                        if dl:
                            parsed = self._parse_deadline_text(dl)
                            if parsed:
                                return {"deadline": parsed, "deadline_type": "fixed"}
                except (json.JSONDecodeError, TypeError):
                    pass

        # Regex patterns against full text
        for pat in self._DEADLINE_PATTERNS:
            m = re.search(pat, all_text, re.IGNORECASE)
            if m:
                parsed = self._parse_deadline_text(m.group(1).strip())
                if parsed:
                    return {"deadline": parsed, "deadline_type": "fixed"}

        # Broader: sentences containing "deadline" with a date
        for sent in re.split(r'[.!?\n]', all_text):
            sent_lower = sent.lower()
            if any(kw in sent_lower for kw in ["deadline", "due date", "closes", "apply by"]):
                dm = re.search(
                    r'([A-Z][a-z]+\s+\d{1,2}(?:,?\s+\d{4})?|\d{4}[-/]\d{1,2}[-/]\d{1,2})',
                    sent,
                )
                if dm:
                    parsed = self._parse_deadline_text(dm.group(1))
                    if parsed:
                        return {"deadline": parsed, "deadline_type": "fixed"}

        return result

    _MONTH_MAP = {
        "january": "01", "february": "02", "march": "03", "april": "04",
        "may": "05", "june": "06", "july": "07", "august": "08",
        "september": "09", "october": "10", "november": "11", "december": "12",
    }

    def _parse_deadline_text(self, text: str) -> Optional[str]:
        text = text.strip()

        # ISO: 2024-03-15
        m = re.match(r'(\d{4})[-/](\d{1,2})[-/](\d{1,2})', text)
        if m:
            y, mo, d = m.groups()
            return f"{y}-{mo.zfill(2)}-{d.zfill(2)}"

        # "March 15, 2024" or "March 15"
        m = re.match(
            r'(January|February|March|April|May|June|July|August|'
            r'September|October|November|December)\s+(\d{1,2})(?:,?\s+(\d{4}))?',
            text, re.IGNORECASE,
        )
        if m:
            mo = self._MONTH_MAP.get(m.group(1).lower())
            day = m.group(2)
            year = m.group(3) or str(date.today().year)
            if mo:
                return f"{year}-{mo}-{day.zfill(2)}"

        # "March 2024" → just month name
        m = re.match(
            r'(January|February|March|April|May|June|July|August|'
            r'September|October|November|December)\s+\d{4}',
            text, re.IGNORECASE,
        )
        if m:
            return m.group(0)

        # Bare month name
        _months = set(self._MONTH_MAP.keys())
        if text.lower() in _months:
            return text.capitalize()

        return None

    # ------------------------------------------------------------------
    # Status
    # ------------------------------------------------------------------
    def _infer_status(self, text: str, deadline: Optional[str]) -> Optional[str]:
        t = text.lower()

        closed_signals = [
            "applications are closed", "application closed",
            "no longer accepting", "applications have closed",
            "deadline has passed", "program is closed",
        ]
        if any(s in t for s in closed_signals):
            return "closed"

        open_signals = [
            "now accepting", "applications are open", "apply now",
            "accepting applications", "application is open",
            "currently accepting",
        ]
        if any(s in t for s in open_signals):
            return "open"

        upcoming_signals = [
            "coming soon", "applications will open", "opening soon",
            "check back", "will be announced",
        ]
        if any(s in t for s in upcoming_signals):
            return "upcoming"

        if deadline and re.match(r'\d{4}-\d{2}-\d{2}', deadline):
            try:
                if date.fromisoformat(deadline) >= date.today():
                    return "open"
                else:
                    return "closed"
            except ValueError:
                pass

        return "unknown"

    # ------------------------------------------------------------------
    # Eligibility
    # ------------------------------------------------------------------
    def _extract_eligibility(self, text: str, soups: List[Dict]) -> Optional[str]:
        headings = [
            "eligibility", "who can apply", "requirements",
            "qualifications", "who should apply", "who is eligible",
            "applicant requirements", "eligibility criteria",
        ]

        for soup_info in soups:
            section = _find_section_text(soup_info["soup"], headings)
            if section and len(section) > 10:
                clean = re.sub(r'\s+', ' ', section).strip()
                return clean[:200]

        # Fallback: sentences with eligibility-related keywords
        for sent in re.split(r'[.!?\n]', text):
            sl = sent.lower()
            if any(kw in sl for kw in ["eligible", "must be", "open to", "applicants must"]):
                clean = sent.strip()
                if 10 < len(clean) < 200:
                    return clean
        return None

    # ------------------------------------------------------------------
    # Audience
    # ------------------------------------------------------------------
    _AUDIENCE_KEYWORDS = {
        "undergrad": ["undergraduate", "undergrad student", "bachelor's", "college student"],
        "masters": ["master's student", "masters student", "ms student", "graduate student"],
        "phd": ["phd", "ph.d", "doctoral student", "doctoral candidate"],
        "recent_grad": ["recent graduate", "recent grad", "new graduate"],
        "early_career": ["early career", "early-career", "young professional"],
        "founder": ["aspiring founder", "student founder", "startup founder"],
        "high_school": ["high school student", "secondary school student", "pre-college student"],
    }

    def _infer_audience(self, text: str) -> Optional[str]:
        t = text.lower()
        matched = [aud for aud, kws in self._AUDIENCE_KEYWORDS.items()
                    if any(kw in t for kw in kws)]
        return "|".join(matched) if matched else None

    # ------------------------------------------------------------------
    # Region / country
    # ------------------------------------------------------------------
    def _infer_region(self, text: str) -> Dict[str, Optional[str]]:
        t = text.lower()
        result: Dict[str, Optional[str]] = {"region": None, "country": None}

        if any(p in t for p in [
            "open to all countries", "no geographic restriction",
            "worldwide", "international applicants welcome",
            "open internationally",
        ]):
            result["region"] = "global"
            return result

        countries: List[str] = []
        if any(p in t for p in ["united states", "u.s.", "us citizen", "us resident"]):
            countries.append("US")
        if any(p in t for p in ["canada", "canadian"]):
            countries.append("CA")

        if countries:
            result["country"] = "|".join(countries)
            s = set(countries)
            if s == {"US"}:
                result["region"] = "us"
            elif s == {"CA"}:
                result["region"] = "canada"
            elif s == {"US", "CA"}:
                result["region"] = "us_canada"
            else:
                result["region"] = "specific"

        return result

    # ------------------------------------------------------------------
    # Compensation
    # ------------------------------------------------------------------
    def _extract_compensation(self, text: str, soups: List[Dict]) -> Dict[str, Optional[str]]:
        result: Dict[str, Optional[str]] = {"compensation": None, "compensation_details": None}
        t = text.lower()

        # Look in compensation-related sections first
        comp_headings = [
            "compensation", "funding", "stipend", "benefits",
            "what you get", "perks", "financial support", "prize", "award",
        ]
        comp_text = text
        for soup_info in soups:
            section = _find_section_text(soup_info["soup"], comp_headings)
            if section:
                comp_text = section + " " + comp_text
                break

        # Find dollar amounts with surrounding context
        # Match sentences containing $ amounts
        for sent in re.split(r'[.!?\n]', comp_text):
            if "$" in sent:
                amounts = re.findall(
                    r'(?:up\s+to\s+)?\$[\d,]+(?:\.\d{2})?(?:\s*[kK])?'
                    r'(?:\s*(?:USD|CAD|per\s+\w+))?',
                    sent,
                )
                if amounts:
                    # Take the best (longest / most descriptive) amount match
                    best = max(amounts, key=len)
                    # Capture some context around it
                    detail = sent.strip()
                    if len(detail) > 100:
                        detail = best
                    result["compensation_details"] = detail[:100]
                    break

        # Determine compensation type
        if result["compensation_details"]:
            if any(kw in t for kw in ["stipend"]):
                result["compensation"] = "stipend"
            elif any(kw in t for kw in ["grant", "prize", "award"]):
                result["compensation"] = "grant"
            elif any(kw in t for kw in ["scholarship", "tuition"]):
                result["compensation"] = "scholarship"
            elif any(kw in t for kw in ["salary", "paid position"]):
                result["compensation"] = "paid"
            else:
                result["compensation"] = "paid"
        elif any(kw in t for kw in ["equity", "equity stake"]):
            result["compensation"] = "equity"
        elif any(kw in t for kw in ["unpaid", "volunteer", "no compensation"]):
            result["compensation"] = "unpaid"
        elif any(kw in t for kw in ["stipend"]):
            result["compensation"] = "stipend"
        elif any(kw in t for kw in ["funded", "grant funding"]):
            result["compensation"] = "grant"

        return result

    # ------------------------------------------------------------------
    # Location
    # ------------------------------------------------------------------
    def _infer_location_type(self, text: str) -> Optional[str]:
        t = text.lower()
        remote = any(s in t for s in [
            "fully remote", "100% remote", "virtual program",
            "remote participation", "online program",
        ])
        in_person = any(s in t for s in [
            "in-person", "in person", "on-site", "on site",
            "must attend", "physical location",
        ])
        hybrid = any(s in t for s in ["hybrid", "mix of in-person and remote"])

        if hybrid:
            return "hybrid"
        if remote and in_person:
            return "hybrid"
        if remote:
            return "remote"
        if in_person:
            return "in_person"
        return None

    def _extract_location(self, text: str) -> Optional[str]:
        patterns = [
            r'(?:located?\s+in|based\s+in|held\s+(?:in|at))\s+([A-Z][a-zA-Z\s,]+?)(?:\.|,\s+(?:the|our|we|and)|\s+\()',
        ]
        for pat in patterns:
            m = re.search(pat, text)
            if m:
                loc = m.group(1).strip().rstrip(",. ")
                if 2 < len(loc) < 80:
                    return loc
        return None

    # ------------------------------------------------------------------
    # Duration / season
    # ------------------------------------------------------------------
    def _extract_duration(self, text: str) -> Optional[str]:
        patterns = [
            (r'(\d+(?:\s*[-–]\s*\d+)?)\s*weeks?\b', "weeks"),
            (r'(\d+(?:\s*[-–]\s*\d+)?)\s*months?\b', "months"),
            (r'(\d+(?:\s*[-–]\s*\d+)?)\s*years?\b', "years"),
            (r'(\d+(?:\s*[-–]\s*\d+)?)\s*days?\b', "days"),
        ]
        for pat, unit in patterns:
            m = re.search(pat, text, re.IGNORECASE)
            if m:
                return f"{m.group(1)} {unit}"
        if "ongoing" in text.lower():
            return "ongoing"
        return None

    _SEASON_KEYWORDS = {
        "summer": ["summer program", "summer fellowship", "summer cohort",
                    "june through august", "summer 20"],
        "fall": ["fall program", "fall cohort", "fall semester",
                 "september through december"],
        "spring": ["spring program", "spring cohort", "spring semester"],
        "winter": ["winter program", "winter cohort", "winter session"],
        "year_round": ["year-round", "year round", "ongoing program",
                       "continuous", "12-month", "full year"],
    }

    def _infer_cohort_season(self, text: str) -> Optional[str]:
        t = text.lower()
        for season, kws in self._SEASON_KEYWORDS.items():
            if any(kw in t for kw in kws):
                return season
        return None

    # ------------------------------------------------------------------
    # Tags
    # ------------------------------------------------------------------
    _TAG_KEYWORDS = {
        "ai": ["artificial intelligence", " ai ", "machine learning", "deep learning"],
        "ml": ["machine learning"],
        "research": ["research"],
        "startup": ["startup", "start-up"],
        "vc": ["venture capital", " vc "],
        "diversity": ["diversity", "underrepresented", "minority", "women in"],
        "climate": ["climate", "sustainability", "clean energy"],
        "health": ["health", "biotech", "biomedical"],
        "hardware": ["hardware"],
        "web3": ["web3", "blockchain"],
        "open_source": ["open source", "open-source"],
        "social_impact": ["social impact", "social good"],
        "canada": ["canada", "canadian"],
        "sf": ["san francisco", "bay area"],
        "nyc": ["new york"],
    }

    def _generate_tags(self, text: str, extracted: Dict) -> Optional[str]:
        t = " " + text.lower() + " "
        tags: set = set()
        for tag, kws in self._TAG_KEYWORDS.items():
            if any(kw in t for kw in kws):
                tags.add(tag)
        cat = extracted.get("category")
        if cat:
            tags.add(cat)
        return "|".join(sorted(tags)) if tags else None


# ======================================================================
# Helpers (module-level, shared)
# ======================================================================

def _get_clean_text(soup: BeautifulSoup) -> str:
    """Text with scripts / styles / nav removed."""
    clone = BeautifulSoup(str(soup), "lxml")
    for tag in clone.find_all(["script", "style", "nav", "noscript", "iframe"]):
        tag.decompose()
    return clone.get_text(separator=" ", strip=True)


def _get_main_content_text(soup: BeautifulSoup) -> str:
    """Try to isolate the main content area."""
    for sel in ["main", "article", '[role="main"]', ".content", "#content"]:
        el = soup.select_one(sel)
        if el:
            return el.get_text(separator=" ", strip=True)
    return _get_clean_text(soup)


def _find_section_text(
    soup: BeautifulSoup,
    heading_keywords: List[str],
    max_chars: int = 500,
) -> Optional[str]:
    """Find text content under a heading whose text matches any keyword."""
    for heading in soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"]):
        ht = heading.get_text(strip=True).lower()
        if not any(kw in ht for kw in heading_keywords):
            continue
        parts: List[str] = []
        level = int(heading.name[1])
        sib = heading.find_next_sibling()
        while sib:
            if sib.name and sib.name in ("h1", "h2", "h3", "h4", "h5", "h6"):
                if int(sib.name[1]) <= level:
                    break
            t = sib.get_text(strip=True)
            if t:
                parts.append(t)
            if sum(len(p) for p in parts) > max_chars:
                break
            sib = sib.find_next_sibling()
        if parts:
            return " ".join(parts)

    # Fallback: look for divs / sections with matching id or class
    for el in soup.find_all(["div", "section"]):
        el_id = (el.get("id") or "").lower()
        el_class = " ".join(el.get("class", [])).lower()
        combined = el_id + " " + el_class
        if any(kw.replace(" ", "") in combined or kw.replace(" ", "-") in combined
               for kw in heading_keywords):
            t = el.get_text(separator=" ", strip=True)
            if t and 10 < len(t) < max_chars:
                return t
    return None


def _org_from_url(url: str) -> Optional[str]:
    try:
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        for prefix in ["www.", "apply.", "jobs.", "careers.", "events."]:
            if domain.startswith(prefix):
                domain = domain[len(prefix):]
        parts = domain.split(".")
        if len(parts) >= 2:
            return parts[0].replace("-", " ").replace("_", " ").title()
    except Exception:
        pass
    return None
