"""Parsing step: turn a messy listing into structured data with Claude.

For each listing, extract {brand, model, variant, year, size, condition_score}
from the title + description. Fields we can't determine are left as None —
the valuation step handles missing data gracefully (see valuation.py).
"""

from __future__ import annotations

import json
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from typing import Optional

from anthropic import Anthropic

from .sources.common import Listing

MODEL = "claude-sonnet-5"

# Listings are parsed one Claude call per listing — each call is I/O bound
# (network round trip), so running them concurrently instead of one after
# another cuts wall-clock time roughly by this factor instead of scaling
# linearly with listing count (e.g. 40 listings serially could take
# 40x a single call's latency; this bounds it to a handful of batches).
MAX_PARSE_WORKERS = 8

SYSTEM_PROMPT = """\
You extract structured product data from second-hand marketplace listings.
Given a listing's title and description, return ONLY a JSON object with these fields:
- brand: string or null
- model: string or null
- variant: string or null (e.g. size, edition, trim, groupset)
- year: integer or null
- size: string or null (e.g. "M", "56cm", "42")
- condition_score: integer from 1 (poor / for parts) to 5 (like new), your best
  estimate from the wording used (e.g. "like new", "some scratches", "for parts")

If a field cannot be determined from the text, use null for it — do not guess
wildly. Respond with the JSON object only, no other text, no markdown fences."""


@dataclass
class ParsedListing:
    listing: Listing
    brand: Optional[str]
    model: Optional[str]
    variant: Optional[str]
    year: Optional[int]
    size: Optional[str]
    condition_score: Optional[int]


def _strip_code_fence(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1] if "\n" in text else text
        if text.endswith("```"):
            text = text[: -3]
        if text.startswith("json"):
            text = text[4:]
    return text.strip()


def parse_listing(client: Anthropic, listing: Listing) -> ParsedListing:
    user_content = f"Title: {listing.title}\nDescription: {listing.description}"
    response = client.messages.create(
        model=MODEL,
        max_tokens=300,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_content}],
    )
    raw_text = "".join(
        block.text for block in response.content if getattr(block, "type", None) == "text"
    )
    try:
        data = json.loads(_strip_code_fence(raw_text))
    except (json.JSONDecodeError, ValueError):
        data = {}

    condition = data.get("condition_score")
    try:
        condition = int(condition) if condition is not None else None
    except (TypeError, ValueError):
        condition = None

    year = data.get("year")
    try:
        year = int(year) if year is not None else None
    except (TypeError, ValueError):
        year = None

    return ParsedListing(
        listing=listing,
        brand=data.get("brand") or None,
        model=data.get("model") or None,
        variant=data.get("variant") or None,
        year=year,
        size=data.get("size") or None,
        condition_score=condition,
    )


def parse_listings(
    listings: list[Listing],
    api_key: Optional[str] = None,
    client: Optional[Anthropic] = None,
) -> list[ParsedListing]:
    """Parse every listing concurrently. Pass a pre-built `client` to reuse a connection/tests."""
    if not listings:
        return []
    client = client or Anthropic(api_key=api_key)
    with ThreadPoolExecutor(max_workers=min(MAX_PARSE_WORKERS, len(listings))) as pool:
        return list(pool.map(lambda listing: parse_listing(client, listing), listings))
