"""Shared types and helpers for all marketplace source modules."""

from __future__ import annotations

import json
import re
import time
from dataclasses import dataclass, field
from typing import Callable, TypeVar

import requests

GEOCODE_URL = "https://nominatim.openstreetmap.org/search"

# Identifies this as a small personal script, not a browser pretending
# to be something it isn't.
USER_AGENT = "SowldDealFinder/0.1 (personal, low-volume; https://github.com/)"

REQUEST_TIMEOUT = 10  # seconds

T = TypeVar("T")


def request_with_backoff(
    make_request: Callable[[], T],
    attempts: int = 3,
    base_delay: float = 2.0,
) -> T:
    """Retry a flaky request with exponential backoff (2s, 4s, 8s, ...).

    For the sites that intermittently serve an empty/blocked response under
    load rather than a hard, permanent failure (Vinted, Kleinanzeigen) — a
    second or third attempt a few seconds later often just works. This does
    not, and should not, retry against sites that return a hard 403 on
    every attempt (Wallapop, Leboncoin, Subito) — that's a wall, not a
    flake, and hammering it faster only makes things worse.
    """
    last_error: Exception | None = None
    for attempt in range(attempts):
        try:
            return make_request()
        except requests.RequestException as exc:
            last_error = exc
            if attempt < attempts - 1:
                time.sleep(base_delay * (2**attempt))
    assert last_error is not None
    raise last_error


def retry_until_non_empty(
    make_request: Callable[[], list[T]],
    attempts: int = 3,
    base_delay: float = 2.0,
) -> list[T]:
    """Like request_with_backoff, but for sites that fail *quietly*.

    Kleinanzeigen sometimes returns 200 OK with an empty JS shell instead
    of the rendered listings — no exception to catch, just zero results.
    Retries a few times with backoff before accepting "genuinely nothing
    found" as the answer.
    """
    result: list[T] = []
    for attempt in range(attempts):
        try:
            result = make_request()
        except requests.RequestException:
            result = []
        if result:
            return result
        if attempt < attempts - 1:
            time.sleep(base_delay * (2**attempt))
    return result


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


def geocode_location_detailed(location: str) -> dict:
    """Resolve a free-text location to lat/lon plus ISO country code via OSM Nominatim."""
    resp = requests.get(
        GEOCODE_URL,
        params={"q": location, "format": "json", "limit": 1, "addressdetails": 1},
        headers={"User-Agent": USER_AGENT},
        timeout=REQUEST_TIMEOUT,
    )
    resp.raise_for_status()
    results = resp.json()
    if not results:
        raise ValueError(f"Could not geocode location: {location!r}")
    result = results[0]
    return {
        "lat": float(result["lat"]),
        "lon": float(result["lon"]),
        "country_code": (result.get("address", {}).get("country_code") or "").lower(),
    }


def geocode_location(location: str) -> tuple[float, float]:
    """Resolve a free-text city name to (latitude, longitude) via OSM Nominatim."""
    geo = geocode_location_detailed(location)
    return geo["lat"], geo["lon"]


_JSON_LD_PATTERN = re.compile(
    r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
    re.DOTALL | re.IGNORECASE,
)


def extract_json_ld_products(html: str) -> list[dict]:
    """Pull Product/Offer nodes out of a page's JSON-LD structured data.

    Several marketplaces without a public search API still embed this for
    SEO. It's a more stable scraping target than hand-picked CSS classes,
    but not guaranteed to be present on every search-results page — sites
    that only add it to individual listing pages will yield nothing here.
    """
    products: list[dict] = []

    def _walk(node: object) -> None:
        if isinstance(node, dict):
            node_type = node.get("@type")
            types = node_type if isinstance(node_type, list) else [node_type]
            if any(t in ("Product", "Offer") for t in types):
                # Matched — its own values (e.g. a Product's nested "offers")
                # describe this node, not separate sibling listings, so
                # don't recurse into them or they'd be double-counted.
                products.append(node)
                return
            for value in node.values():
                _walk(value)
        elif isinstance(node, list):
            for item in node:
                _walk(item)

    for raw_block in _JSON_LD_PATTERN.findall(html):
        try:
            data = json.loads(raw_block)
        except json.JSONDecodeError:
            continue
        _walk(data)

    return products
