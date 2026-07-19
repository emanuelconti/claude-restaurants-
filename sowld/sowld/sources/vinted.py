"""Vinted fetch layer — pan-European, the biggest of the sources here.

Vinted has no official public API, but its web client calls a JSON search
endpoint (`/api/v2/catalog/items`) that's well documented by community
tools (e.g. the pyVinted project) and works unauthenticated for basic
search. Vinted runs one marketplace per country domain rather than a
single global site with radius search, so this maps the searched location
to a country via reverse geocoding and picks that country's domain.

Same rules as the other sources (SOW Part B, §B3): low volume, realistic
user-agent, no seller personal data kept.
"""

from __future__ import annotations

import time

import requests

from .common import REQUEST_TIMEOUT, USER_AGENT, Listing, geocode_location_detailed

# Country code -> Vinted domain. Not exhaustive — falls back to vinted.com
# for countries Vinted doesn't have a dedicated site for.
COUNTRY_DOMAINS = {
    "es": "vinted.es",
    "fr": "vinted.fr",
    "de": "vinted.de",
    "it": "vinted.it",
    "nl": "vinted.nl",
    "pl": "vinted.pl",
    "be": "vinted.be",
    "at": "vinted.at",
    "cz": "vinted.cz",
    "pt": "vinted.pt",
    "lt": "vinted.lt",
    "lv": "vinted.lv",
    "lu": "vinted.lu",
    "sk": "vinted.sk",
    "gb": "vinted.co.uk",
    "ie": "vinted.ie",
    "se": "vinted.se",
    "dk": "vinted.dk",
    "fi": "vinted.fi",
    "ro": "vinted.ro",
    "hu": "vinted.hu",
    "hr": "vinted.hr",
    "gr": "vinted.gr",
}
DEFAULT_DOMAIN = "vinted.com"


def _price(item: dict) -> float:
    price = item.get("price") or {}
    try:
        return float(price.get("amount", 0) or 0)
    except (TypeError, ValueError):
        return 0.0


def _item_to_listing(item: dict, domain: str, fallback_location: str) -> Listing:
    photo = item.get("photo") or {}
    # Vinted search results don't include a full description, but they do
    # include brand/size/condition directly — feed those to the parsing
    # step as a synthetic description so it still has something to read.
    description = ", ".join(
        bit for bit in (item.get("brand_title"), item.get("size_title"), item.get("status")) if bit
    )
    return Listing(
        title=(item.get("title") or "").strip(),
        price=_price(item),
        description=description,
        url=item.get("url") or f"https://www.{domain}/items/{item.get('id', '')}",
        location=fallback_location,
        photo_urls=[photo["url"]] if photo.get("url") else [],
        source="vinted",
    )


def fetch_listings(
    query: str,
    location: str,
    max_results: int = 40,
    delay: float = 1.0,
) -> list[Listing]:
    """Fetch current Vinted listings for `query`, on the domain for `location`'s country.

    Note: the endpoint occasionally 401s on the very first request until a
    session cookie is set, which is why this visits the homepage once
    before searching.
    """
    geo = geocode_location_detailed(location)
    domain = COUNTRY_DOMAINS.get(geo["country_code"], DEFAULT_DOMAIN)
    time.sleep(delay)

    session = requests.Session()
    headers = {"User-Agent": USER_AGENT, "Accept": "application/json"}
    session.get(f"https://www.{domain}/", headers=headers, timeout=REQUEST_TIMEOUT)

    params = {
        "search_text": query,
        "per_page": max_results,
        "order": "newest_first",
    }
    resp = session.get(
        f"https://www.{domain}/api/v2/catalog/items",
        params=params,
        headers=headers,
        timeout=REQUEST_TIMEOUT,
    )
    resp.raise_for_status()
    payload = resp.json()

    raw_items = payload.get("items", [])
    listings = [_item_to_listing(item, domain, location) for item in raw_items[:max_results]]
    return [l for l in listings if l.title and l.price > 0]
