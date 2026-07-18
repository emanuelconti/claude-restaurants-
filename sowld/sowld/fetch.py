"""Fetch layer: turn a (query, location) pair into a list of current listings.

Wallapop has no public API. This uses its internal search endpoint, which is
undocumented, community-reverse-engineered, and can change or break without
notice. Per the SOW (Part B, section B3): keep request volume low, use a
realistic (not deceptive) user-agent, respect rate limits, and store only
the fields listed below — never seller personal data.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field

import requests

WALLAPOP_SEARCH_URL = "https://api.wallapop.com/api/v3/general/search"
GEOCODE_URL = "https://nominatim.openstreetmap.org/search"

# Identifies this as a small personal script, not a browser pretending
# to be something it isn't.
USER_AGENT = "SowldDealFinder/0.1 (personal, low-volume; https://github.com/)"

REQUEST_TIMEOUT = 10  # seconds


@dataclass
class Listing:
    """Only the fields Sowld is allowed to keep — no seller personal data."""

    title: str
    price: float
    description: str
    url: str
    location: str
    photo_urls: list[str] = field(default_factory=list)


def geocode_location(location: str) -> tuple[float, float]:
    """Resolve a free-text city name to (latitude, longitude) via OSM Nominatim."""
    resp = requests.get(
        GEOCODE_URL,
        params={"q": location, "format": "json", "limit": 1},
        headers={"User-Agent": USER_AGENT},
        timeout=REQUEST_TIMEOUT,
    )
    resp.raise_for_status()
    results = resp.json()
    if not results:
        raise ValueError(f"Could not geocode location: {location!r}")
    return float(results[0]["lat"]), float(results[0]["lon"])


def _extract_photo_urls(item: dict) -> list[str]:
    urls = []
    for img in item.get("images", []) or []:
        url = img.get("original") or img.get("large") or img.get("medium")
        if url:
            urls.append(url)
    return urls


def _item_to_listing(item: dict, fallback_location: str) -> Listing:
    price_block = item.get("price") or {}
    location_block = item.get("location") or {}
    return Listing(
        title=item.get("title", "").strip(),
        price=float(price_block.get("amount", 0) or 0),
        description=(item.get("description") or "").strip(),
        url=f"https://es.wallapop.com/item/{item.get('web_slug', item.get('id', ''))}",
        location=location_block.get("city") or fallback_location,
        photo_urls=_extract_photo_urls(item),
    )


def fetch_listings(
    query: str,
    location: str,
    max_results: int = 40,
    delay: float = 1.0,
) -> list[Listing]:
    """Fetch current listings for `query` near `location`.

    Note: the Wallapop response shape is not officially documented and may
    drift over time. If this starts returning zero results, print the raw
    JSON from a manual request and adjust the parsing below.
    """
    lat, lon = geocode_location(location)
    time.sleep(delay)  # be polite between the geocode call and the search call

    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/json",
    }
    params = {
        "keywords": query,
        "latitude": lat,
        "longitude": lon,
        "order_by": "newest",
    }
    resp = requests.get(
        WALLAPOP_SEARCH_URL, params=params, headers=headers, timeout=REQUEST_TIMEOUT
    )
    resp.raise_for_status()
    payload = resp.json()

    raw_items = (
        payload.get("data", {}).get("section", {}).get("payload", {}).get("items", [])
    )

    listings = [_item_to_listing(item, location) for item in raw_items[:max_results]]
    return [l for l in listings if l.title and l.price > 0]
