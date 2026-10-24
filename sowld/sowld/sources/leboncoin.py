"""Leboncoin fetch layer.

Like Wallapop, Leboncoin has no public API for this kind of search. This
uses its internal search endpoint (the same one leboncoin.fr's own web
client calls), which is undocumented and can change or break without
notice — including the "api_key" header value below, which Leboncoin
rotates from time to time. If this stops working, open leboncoin.fr in a
browser, search for something, and check the Network tab for a POST to
/finder/search to find the current key and confirm the request/response
shape hasn't changed.

Same rules as Wallapop (SOW Part B, section B3): keep request volume low,
use a realistic user-agent, respect rate limits, store only the fields on
Listing — never seller personal data.
"""

from __future__ import annotations

import time

import requests

from .common import USER_AGENT, REQUEST_TIMEOUT, Listing, geocode_location

SEARCH_URL = "https://api.leboncoin.fr/finder/search"

# Public key used by leboncoin.fr's own web client as of writing. Rotates
# periodically — see the module docstring if requests start failing.
API_KEY = "ba0c2dad52b3ec"


def _extract_photo_urls(ad: dict) -> list[str]:
    images = ad.get("images") or {}
    urls = images.get("urls_large") or images.get("urls") or []
    return list(urls)


def _price(ad: dict) -> float:
    price = ad.get("price")
    if isinstance(price, list) and price:
        return float(price[0] or 0)
    if isinstance(price, (int, float)):
        return float(price)
    return 0.0


def _ad_to_listing(ad: dict, fallback_location: str) -> Listing:
    location_block = ad.get("location") or {}
    return Listing(
        title=(ad.get("subject") or "").strip(),
        price=_price(ad),
        description=(ad.get("body") or "").strip(),
        url=ad.get("url", ""),
        location=location_block.get("city") or fallback_location,
        photo_urls=_extract_photo_urls(ad),
        source="leboncoin",
    )


def fetch_listings(
    query: str,
    location: str,
    max_results: int = 40,
    delay: float = 1.0,
    radius_m: int = 20000,
) -> list[Listing]:
    """Fetch current Leboncoin listings for `query` near `location`.

    Note: the response shape is not officially documented and may drift
    over time — see the module docstring before relying on this.
    """
    lat, lon = geocode_location(location)
    time.sleep(delay)  # be polite between the geocode call and the search call

    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/json",
        "Content-Type": "application/json",
        "api_key": API_KEY,
    }
    body = {
        "filters": {
            "enums": {"ad_type": ["offer"]},
            "keywords": {"text": query},
            "location": {
                "locations": [
                    {
                        "locationType": "city",
                        "lat": lat,
                        "lng": lon,
                        "radius": radius_m,
                        "label": location,
                    }
                ]
            },
        },
        "limit": max_results,
        "limit_alu": 0,
        "offset": 0,
        "sort_by": "time",
        "sort_order": "desc",
    }
    resp = requests.post(SEARCH_URL, json=body, headers=headers, timeout=REQUEST_TIMEOUT)
    resp.raise_for_status()
    payload = resp.json()

    raw_ads = payload.get("ads", [])
    listings = [_ad_to_listing(ad, location) for ad in raw_ads[:max_results]]
    return [l for l in listings if l.title and l.price > 0]
