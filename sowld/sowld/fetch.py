"""Fetch layer: turn a (query, location, source) triple into a list of listings.

Dispatches to the right marketplace module under sources/. Each source
module implements the same fetch_listings(query, location, max_results,
delay) signature and returns a list of the shared Listing type, so
everything downstream (parsing, valuation, scoring) is source-agnostic.

To add a new marketplace: write sources/<name>.py with a fetch_listings()
function returning list[Listing], then register it in SOURCES below.
"""

from __future__ import annotations

from .sources import ebay, kleinanzeigen, leboncoin, subito, vinted, wallapop
from .sources.common import Listing

SOURCES = {
    "wallapop": wallapop.fetch_listings,
    "leboncoin": leboncoin.fetch_listings,
    "vinted": vinted.fetch_listings,
    "kleinanzeigen": kleinanzeigen.fetch_listings,
    "subito": subito.fetch_listings,
    "ebay": ebay.fetch_listings,
}

# Verified live (2026-07-19): wallapop/leboncoin/subito are blocked by
# anti-bot protection (see README "Multiple marketplaces"), kleinanzeigen
# is unreliable. vinted is the only source confirmed working consistently.
DEFAULT_SOURCE = "vinted"

# Sources whose access is still being worked on — surfaced in the UI so
# users aren't left guessing why a search on one of these comes up empty.
BETA_SOURCES = {"wallapop", "leboncoin", "subito", "kleinanzeigen"}


def fetch_listings(
    query: str,
    location: str,
    source: str = DEFAULT_SOURCE,
    max_results: int = 40,
    delay: float = 1.0,
) -> list[Listing]:
    if source not in SOURCES:
        available = ", ".join(sorted(SOURCES))
        raise ValueError(f"Unknown source {source!r}. Available: {available}")
    return SOURCES[source](query, location, max_results=max_results, delay=delay)


__all__ = ["Listing", "SOURCES", "DEFAULT_SOURCE", "fetch_listings"]
