"""Kleinanzeigen (Germany) fetch layer.

Kleinanzeigen (formerly eBay Kleinanzeigen) has no public search API, so
this scrapes its search-results HTML page directly, the same page a
browser loads. Verified against a live response: search-results pages
don't carry Product/Offer JSON-LD (only WebSite/ImageObject), so this
goes straight to CSS selectors against the real markup — each listing is
an `<article class="aditem" data-href="...">` (wrapped in an
`<li class="ad-listitem">`), which conveniently gives the URL as a plain
attribute instead of needing to dig through an <a> tag. (Re-verified live
2026-07-21 — this replaced an earlier `<li class="j-adlistitem">`
structure that was live the day before; the site changes this markup
without notice.)

If this stops matching, Kleinanzeigen changed their markup again — open
the search URL in a browser, inspect a listing card, and update the
selectors below.

Same rules as the other sources (SOW Part B, §B3): low volume, realistic
user-agent, no seller personal data kept.
"""

from __future__ import annotations

import time

import requests
from bs4 import BeautifulSoup

from .common import REQUEST_TIMEOUT, USER_AGENT, Listing, retry_until_non_empty

SEARCH_URL = "https://www.kleinanzeigen.de/s-suchanfrage.html"
BASE_URL = "https://www.kleinanzeigen.de"


def _parse_price(text: str) -> float:
    digits = "".join(ch for ch in text if ch.isdigit())
    return float(digits) if digits else 0.0


def _scrape_html(html: str, fallback_location: str) -> list[Listing]:
    soup = BeautifulSoup(html, "html.parser")
    listings = []
    for card in soup.select("article.aditem[data-href]"):
        title_el = card.select_one("h2.text-module-begin a") or card.select_one(".aditem-main--middle a")
        title = title_el.get_text(strip=True) if title_el else ""

        price_el = card.select_one(".aditem-main--middle--price-shipping--price")
        price = _parse_price(price_el.get_text()) if price_el else 0.0

        desc_el = card.select_one(".aditem-main--middle--description")
        description = desc_el.get_text(strip=True) if desc_el else ""

        href = card.get("data-href", "")
        url = f"{BASE_URL}{href}" if href.startswith("/") else href

        img_el = card.select_one("img[src]")
        photo_urls = [img_el["src"]] if img_el else []

        if title and price > 0:
            listings.append(
                Listing(
                    title=title,
                    price=price,
                    description=description,
                    url=url,
                    location=fallback_location,
                    photo_urls=photo_urls,
                    source="kleinanzeigen",
                )
            )
    return listings


def _do_search(query: str, location: str) -> list[Listing]:
    headers = {"User-Agent": USER_AGENT, "Accept": "text/html"}
    params = {
        "keywords": query,
        "locationStr": location,
        "radius": 25,
        "sortingField": "SORTING_DATE",
        "action": "find",
    }
    resp = requests.get(SEARCH_URL, params=params, headers=headers, timeout=REQUEST_TIMEOUT)
    resp.raise_for_status()
    return _scrape_html(resp.text, location)


def fetch_listings(
    query: str,
    location: str,
    max_results: int = 40,
    delay: float = 1.5,
) -> list[Listing]:
    """Fetch current Kleinanzeigen listings for `query` near `location`.

    Retries on empty results — the known failure mode here is a 200 OK
    with an unrendered JS shell rather than an HTTP error (see module
    docstring), so a plain retry-on-exception wouldn't catch it.
    """
    time.sleep(delay)
    listings = retry_until_non_empty(lambda: _do_search(query, location))
    return listings[:max_results]
