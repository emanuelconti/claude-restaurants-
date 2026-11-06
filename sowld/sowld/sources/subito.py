"""Subito.it (Italy) fetch layer — EXPERIMENTAL, unverified.

Subito.it has no public search API, so this scrapes its search-results
HTML page directly. Same defensive approach as kleinanzeigen.py: try the
page's JSON-LD structured data first (more stable across redesigns), fall
back to a CSS selector scrape.

This has NOT been exercised against a live response — this environment
has no network access to subito.it. The first real run is the real test:
if `fetch_listings` returns nothing, open the search URL in a browser,
inspect a listing card's HTML, and update `_scrape_html` below.

Same rules as the other sources (SOW Part B, §B3): low volume, realistic
user-agent, no seller personal data kept.
"""

from __future__ import annotations

import time

import requests
from bs4 import BeautifulSoup

from .common import REQUEST_TIMEOUT, USER_AGENT, Listing, extract_json_ld_products

SEARCH_URL = "https://www.subito.it/annunci-italia/vendita/usato/"


def _parse_price(text: str) -> float:
    digits = "".join(ch for ch in text if ch.isdigit())
    return float(digits) if digits else 0.0


def _from_json_ld(html: str, fallback_location: str) -> list[Listing]:
    listings = []
    for product in extract_json_ld_products(html):
        offers = product.get("offers") or {}
        price = offers.get("price") if isinstance(offers, dict) else None
        try:
            price = float(price) if price is not None else 0.0
        except (TypeError, ValueError):
            price = 0.0
        title = (product.get("name") or "").strip()
        if not title or price <= 0:
            continue
        image = product.get("image")
        photo_urls = [image] if isinstance(image, str) else (image or [])
        listings.append(
            Listing(
                title=title,
                price=price,
                description=(product.get("description") or "").strip(),
                url=product.get("url") or (offers.get("url") if isinstance(offers, dict) else ""),
                location=fallback_location,
                photo_urls=photo_urls,
                source="subito",
            )
        )
    return listings


def _scrape_html(html: str, fallback_location: str) -> list[Listing]:
    """CSS-selector fallback. Selectors are best-effort guesses — verify
    against a live page and adjust."""
    soup = BeautifulSoup(html, "html.parser")
    listings = []
    for card in soup.select("[data-testid='item-card'], article"):
        title_el = card.select_one("h2, [data-testid='item-title']")
        title = title_el.get_text(strip=True) if title_el else ""

        price_el = card.select_one("[data-testid='item-price'], .price")
        price = _parse_price(price_el.get_text()) if price_el else 0.0

        desc_el = card.select_one("p")
        description = desc_el.get_text(strip=True) if desc_el else ""

        link_el = card.select_one("a[href]")
        href = link_el["href"] if link_el else ""
        url = href if href.startswith("http") else f"https://www.subito.it{href}"

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
                    source="subito",
                )
            )
    return listings


def fetch_listings(
    query: str,
    location: str,
    max_results: int = 40,
    delay: float = 1.0,
) -> list[Listing]:
    """Fetch current Subito.it listings for `query` near `location`."""
    headers = {"User-Agent": USER_AGENT, "Accept": "text/html"}
    params = {"q": query, "cq": location}
    resp = requests.get(SEARCH_URL, params=params, headers=headers, timeout=REQUEST_TIMEOUT)
    resp.raise_for_status()
    time.sleep(delay)

    listings = _from_json_ld(resp.text, location)
    if not listings:
        listings = _scrape_html(resp.text, location)

    return listings[:max_results]
