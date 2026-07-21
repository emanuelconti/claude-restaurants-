"""eBay fetch layer — the one official, legal source in this list.

Uses eBay's Browse API (buy/browse/v1/item_summary/search) with an
OAuth2 client-credentials token — no scraping, no reverse-engineering, no
risk of an anti-bot wall. Needs EBAY_CLIENT_ID and EBAY_CLIENT_SECRET from
a developer.ebay.com application (see README "Multiple marketplaces").

Unlike the other sources, this doesn't filter to used-only listings via
the API (eBay's condition-filter values are easy to get subtly wrong and
silently drop results) — it searches normally and lets the existing
Claude-based parsing step (parse.py) read condition from the title same
as everywhere else.
"""

from __future__ import annotations

import base64
import os
import time

import requests

from .common import REQUEST_TIMEOUT, USER_AGENT, Listing, geocode_location_detailed, request_with_backoff

TOKEN_URL = "https://api.ebay.com/identity/v1/oauth2/token"
SEARCH_URL = "https://api.ebay.com/buy/browse/v1/item_summary/search"
OAUTH_SCOPE = "https://api.ebay.com/oauth/api_scope"

# Country code -> eBay marketplace ID. Falls back to the German site
# (the largest general eBay marketplace in continental Europe) for
# countries without their own.
MARKETPLACE_IDS = {
    "us": "EBAY_US",
    "gb": "EBAY_GB",
    "de": "EBAY_DE",
    "fr": "EBAY_FR",
    "it": "EBAY_IT",
    "es": "EBAY_ES",
    "at": "EBAY_AT",
    "ch": "EBAY_CH",
    "nl": "EBAY_NL",
    "be": "EBAY_BE",
    "pl": "EBAY_PL",
    "ie": "EBAY_IE",
}
DEFAULT_MARKETPLACE = "EBAY_DE"

# Module-level token cache: one OAuth token covers many searches, no need
# to re-authenticate every call. Client-credentials tokens are app-level,
# not tied to a single request, so caching in the process is safe.
_token_cache: dict[str, float | str] = {"token": "", "expires_at": 0.0}


def _get_access_token() -> str:
    now = time.time()
    if _token_cache["token"] and now < float(_token_cache["expires_at"]) - 60:
        return str(_token_cache["token"])

    client_id = os.environ.get("EBAY_CLIENT_ID", "")
    client_secret = os.environ.get("EBAY_CLIENT_SECRET", "")
    if not client_id or not client_secret:
        raise RuntimeError("EBAY_CLIENT_ID and EBAY_CLIENT_SECRET must be set")

    basic_auth = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
    resp = requests.post(
        TOKEN_URL,
        headers={
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": f"Basic {basic_auth}",
        },
        data={"grant_type": "client_credentials", "scope": OAUTH_SCOPE},
        timeout=REQUEST_TIMEOUT,
    )
    resp.raise_for_status()
    payload = resp.json()

    _token_cache["token"] = payload["access_token"]
    _token_cache["expires_at"] = now + float(payload.get("expires_in", 7200))
    return str(_token_cache["token"])


def _price(item: dict) -> float:
    price = item.get("price") or {}
    try:
        return float(price.get("value", 0) or 0)
    except (TypeError, ValueError):
        return 0.0


def _item_to_listing(item: dict, fallback_location: str) -> Listing:
    image = item.get("image") or {}
    # eBay's search results often include a plain-text condition (e.g.
    # "Used", "For parts or not working") — folded into the description
    # so the Claude parsing step has it to read, same as everywhere else.
    description = item.get("condition") or ""
    return Listing(
        title=(item.get("title") or "").strip(),
        price=_price(item),
        description=description,
        url=item.get("itemWebUrl", ""),
        location=fallback_location,
        photo_urls=[image["imageUrl"]] if image.get("imageUrl") else [],
        source="ebay",
    )


def _do_search(query: str, marketplace_id: str, max_results: int, location: str) -> list[Listing]:
    token = _get_access_token()
    headers = {
        "User-Agent": USER_AGENT,
        "Authorization": f"Bearer {token}",
        "X-EBAY-C-MARKETPLACE-ID": marketplace_id,
    }
    params = {"q": query, "limit": min(max_results, 50), "sort": "newlyListed"}
    resp = requests.get(SEARCH_URL, params=params, headers=headers, timeout=REQUEST_TIMEOUT)
    resp.raise_for_status()
    payload = resp.json()

    raw_items = payload.get("itemSummaries", [])
    return [_item_to_listing(item, location) for item in raw_items]


def fetch_listings(
    query: str,
    location: str,
    max_results: int = 40,
    delay: float = 1.0,
) -> list[Listing]:
    """Fetch current eBay listings for `query`, on the marketplace for `location`'s country."""
    geo = geocode_location_detailed(location)
    marketplace_id = MARKETPLACE_IDS.get(geo["country_code"], DEFAULT_MARKETPLACE)
    time.sleep(delay)

    listings = request_with_backoff(
        lambda: _do_search(query, marketplace_id, max_results, location)
    )
    return [l for l in listings if l.title and l.price > 0][:max_results]
