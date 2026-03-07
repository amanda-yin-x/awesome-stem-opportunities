"""Processing modules for normalization, deduplication, and merging."""

from .normalize import normalize_opportunity
from .dedupe import find_duplicates, deduplicate
from .merge import merge_opportunities

__all__ = ["normalize_opportunity", "find_duplicates", "deduplicate", "merge_opportunities"]
