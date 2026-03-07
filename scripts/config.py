"""Configuration and constants for the automation scripts."""

from pathlib import Path

# Paths
ROOT_DIR = Path(__file__).parent.parent
DATA_DIR = ROOT_DIR / "data"
DOCS_DIR = ROOT_DIR / "docs"

CSV_PATH = DATA_DIR / "opportunities.csv"
SCHEMA_PATH = DATA_DIR / "schema.json"
README_PATH = ROOT_DIR / "README.md"

# CSV columns in order
CSV_COLUMNS = [
    "id", "name", "organization", "category", "subcategory",
    "region", "country", "audience", "eligibility", "url", "apply_url",
    "deadline", "deadline_type", "status", "compensation", "compensation_details",
    "location_type", "location", "duration", "cohort_season", "tags",
    "description", "source", "source_type", "date_added", "last_verified", "notes"
]

# Valid enum values (must match schema.json)
CATEGORIES = [
    "research", "fellowship", "accelerator", "grant",
    "scholarship", "ecosystem", "innovation", "leadership"
]

SUBCATEGORIES = [
    "reu", "industry_research", "academic_research",
    "cohort_fellowship", "technical_fellowship", "founder_fellowship",
    "startup_accelerator", "student_incubator",
    "project_grant", "research_grant", "travel_grant",
    "merit_scholarship", "need_based_scholarship", "field_specific_scholarship",
    "vc_fellowship", "talent_network", "founder_network",
    "hackathon", "competition", "challenge",
    "community_program", "technical_leadership", "other"
]

REGIONS = ["us", "canada", "us_canada", "north_america", "global", "specific"]

AUDIENCE_OPTIONS = [
    "undergrad", "masters", "phd", "recent_grad",
    "early_career", "founder", "high_school"
]

DEADLINE_TYPES = ["fixed", "rolling", "multiple_rounds", "tba", "varies_by_track"]

STATUS_OPTIONS = ["open", "closed", "upcoming", "unknown"]

COMPENSATION_OPTIONS = [
    "paid", "stipend", "grant", "scholarship",
    "equity", "unpaid", "varies", "unknown"
]

LOCATION_TYPES = ["in_person", "remote", "hybrid", "varies"]

COHORT_SEASONS = ["spring", "summer", "fall", "winter", "year_round", "varies"]

SOURCE_TYPES = ["official", "linkedin", "newsletter", "community", "manual", "scraped"]

# Rate limiting
DEFAULT_RATE_LIMIT = 2.0  # seconds between requests
GOOGLE_RATE_LIMIT = 3.0
LINKEDIN_RATE_LIMIT = 5.0

# Verification
STALE_THRESHOLD_DAYS = 30  # Flag entries not verified in this many days
REQUEST_TIMEOUT = 30  # seconds
MAX_RETRIES = 3
