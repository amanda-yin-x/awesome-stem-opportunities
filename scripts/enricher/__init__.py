"""Opportunity enrichment pipeline.

Given a URL, fetches the page and related pages on the same domain,
extracts structured opportunity fields, and optionally falls back
to web search for missing information.
"""

from .pipeline import enrich_url, enrich_urls, validate_and_add

__all__ = ["enrich_url", "enrich_urls", "validate_and_add"]
