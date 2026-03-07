"""Pydantic models for opportunity data."""

from datetime import date
from typing import Optional, List, Literal
from pydantic import BaseModel, HttpUrl, field_validator, ConfigDict
import re

from .config import (
    CATEGORIES, SUBCATEGORIES, REGIONS, AUDIENCE_OPTIONS,
    DEADLINE_TYPES, STATUS_OPTIONS, COMPENSATION_OPTIONS,
    LOCATION_TYPES, COHORT_SEASONS, SOURCE_TYPES
)

# Type aliases for clarity
CategoryType = Literal[
    "research", "fellowship", "accelerator", "grant",
    "scholarship", "ecosystem", "innovation", "leadership"
]

StatusType = Literal["open", "closed", "upcoming", "unknown"]

SourceType = Literal["official", "linkedin", "newsletter", "community", "manual", "scraped"]


class Opportunity(BaseModel):
    """Represents a single opportunity entry."""

    model_config = ConfigDict(str_strip_whitespace=True)

    # Required fields
    id: str
    name: str
    organization: str
    category: CategoryType
    url: HttpUrl

    # Optional classification
    subcategory: Optional[str] = None
    region: Optional[str] = None
    country: Optional[List[str]] = None
    audience: Optional[List[str]] = None
    eligibility: Optional[str] = None

    # Application details
    apply_url: Optional[HttpUrl] = None
    deadline: Optional[str] = None
    deadline_type: Optional[str] = None
    status: StatusType = "unknown"

    # Compensation
    compensation: Optional[str] = None
    compensation_details: Optional[str] = None

    # Location/timing
    location_type: Optional[str] = None
    location: Optional[str] = None
    duration: Optional[str] = None
    cohort_season: Optional[str] = None

    # Metadata
    tags: Optional[List[str]] = None
    description: Optional[str] = None
    source: Optional[str] = None
    source_type: SourceType = "manual"
    date_added: date
    last_verified: date
    notes: Optional[str] = None

    @field_validator('id')
    @classmethod
    def validate_id(cls, v: str) -> str:
        """Ensure ID is kebab-case."""
        if not re.match(r'^[a-z0-9]+(-[a-z0-9]+)*$', v):
            raise ValueError(f"ID must be kebab-case: {v}")
        return v

    @field_validator('subcategory')
    @classmethod
    def validate_subcategory(cls, v: Optional[str]) -> Optional[str]:
        """Validate subcategory against allowed values."""
        if v is not None and v not in SUBCATEGORIES:
            raise ValueError(f"Invalid subcategory: {v}")
        return v

    @field_validator('region')
    @classmethod
    def validate_region(cls, v: Optional[str]) -> Optional[str]:
        """Validate region against allowed values."""
        if v is not None and v not in REGIONS:
            raise ValueError(f"Invalid region: {v}")
        return v

    @field_validator('audience', mode='before')
    @classmethod
    def parse_audience(cls, v):
        """Parse pipe-separated audience string into list."""
        if isinstance(v, str):
            return [x.strip() for x in v.split('|') if x.strip()]
        return v

    @field_validator('country', mode='before')
    @classmethod
    def parse_country(cls, v):
        """Parse pipe-separated country string into list."""
        if isinstance(v, str):
            return [x.strip() for x in v.split('|') if x.strip()]
        return v

    @field_validator('tags', mode='before')
    @classmethod
    def parse_tags(cls, v):
        """Parse pipe-separated tags string into list."""
        if isinstance(v, str):
            return [x.strip() for x in v.split('|') if x.strip()]
        return v

    @field_validator('deadline_type')
    @classmethod
    def validate_deadline_type(cls, v: Optional[str]) -> Optional[str]:
        """Validate deadline_type against allowed values."""
        if v is not None and v not in DEADLINE_TYPES:
            raise ValueError(f"Invalid deadline_type: {v}")
        return v

    @field_validator('compensation')
    @classmethod
    def validate_compensation(cls, v: Optional[str]) -> Optional[str]:
        """Validate compensation against allowed values."""
        if v is not None and v not in COMPENSATION_OPTIONS:
            raise ValueError(f"Invalid compensation: {v}")
        return v

    @field_validator('location_type')
    @classmethod
    def validate_location_type(cls, v: Optional[str]) -> Optional[str]:
        """Validate location_type against allowed values."""
        if v is not None and v not in LOCATION_TYPES:
            raise ValueError(f"Invalid location_type: {v}")
        return v

    @field_validator('cohort_season')
    @classmethod
    def validate_cohort_season(cls, v: Optional[str]) -> Optional[str]:
        """Validate cohort_season against allowed values."""
        if v is not None and v not in COHORT_SEASONS:
            raise ValueError(f"Invalid cohort_season: {v}")
        return v

    @field_validator('date_added', 'last_verified', mode='before')
    @classmethod
    def parse_date(cls, v):
        """Parse date string to date object."""
        if isinstance(v, str):
            return date.fromisoformat(v)
        return v

    def to_csv_row(self) -> dict:
        """Convert to CSV row format."""
        return {
            'id': self.id,
            'name': self.name,
            'organization': self.organization,
            'category': self.category,
            'subcategory': self.subcategory or '',
            'region': self.region or '',
            'country': '|'.join(self.country) if self.country else '',
            'audience': '|'.join(self.audience) if self.audience else '',
            'eligibility': self.eligibility or '',
            'url': str(self.url),
            'apply_url': str(self.apply_url) if self.apply_url else '',
            'deadline': self.deadline or '',
            'deadline_type': self.deadline_type or '',
            'status': self.status,
            'compensation': self.compensation or '',
            'compensation_details': self.compensation_details or '',
            'location_type': self.location_type or '',
            'location': self.location or '',
            'duration': self.duration or '',
            'cohort_season': self.cohort_season or '',
            'tags': '|'.join(self.tags) if self.tags else '',
            'description': self.description or '',
            'source': self.source or '',
            'source_type': self.source_type,
            'date_added': self.date_added.isoformat(),
            'last_verified': self.last_verified.isoformat(),
            'notes': self.notes or '',
        }


class RawOpportunity(BaseModel):
    """Raw scraped opportunity data before normalization."""

    name: Optional[str] = None
    organization: Optional[str] = None
    url: Optional[str] = None
    apply_url: Optional[str] = None
    deadline_text: Optional[str] = None
    description: Optional[str] = None
    source_url: Optional[str] = None
    raw_html: Optional[str] = None

    def is_valid(self) -> bool:
        """Check if we have minimum required data."""
        return bool(self.name and self.url)
