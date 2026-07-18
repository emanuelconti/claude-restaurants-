"""Shared types and helpers for all marketplace source modules."""

from __future__ import annotations

from dataclasses import dataclass, field

import requests

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
    source: str = ""


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
