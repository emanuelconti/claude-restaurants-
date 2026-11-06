"""Valuation step: estimate a fair value for each listing with NO external dataset.

Method (SOW Part B, section B1):
1. Group comparables by brand+model.
2. Normalize each listing's price to a "condition 3 / average" equivalent.
3. Fair value baseline = the median of those normalized prices.
4. Re-adjust the baseline back to each listing's own condition -> fair_value.

This only uses the listings themselves as the reference — it finds items
priced below their own market of comparables, nothing more.
"""

from __future__ import annotations

import statistics
from collections import defaultdict
from dataclasses import dataclass
from typing import Optional

from .parse import ParsedListing

BASELINE_CONDITION = 3
CONDITION_STEP = 0.1  # +/-10% fair value per condition point away from baseline
MIN_GROUP_SIZE = 2  # need at least this many comparables to trust a median


@dataclass
class ValuedListing:
    parsed: ParsedListing
    fair_value: float
    deal_score: float


def condition_multiplier(condition_score: Optional[int]) -> float:
    """Map a 1-5 condition score to a price multiplier, 3 (average) = 1.0x."""
    score = BASELINE_CONDITION if condition_score is None else condition_score
    score = max(1, min(5, score))
    return 1.0 + CONDITION_STEP * (score - BASELINE_CONDITION)


def _group_key(parsed: ParsedListing) -> Optional[tuple[str, str]]:
    if not parsed.brand or not parsed.model:
        return None
    return (parsed.brand.strip().lower(), parsed.model.strip().lower())


def compute_fair_values(
    parsed_listings: list[ParsedListing],
    min_group_size: int = MIN_GROUP_SIZE,
) -> list[ValuedListing]:
    """Group by brand+model and compute a condition-adjusted fair value for each.

    Listings with no brand/model, or whose group is too small to have a
    trustworthy median, are skipped — there's nothing to compare them against.
    """
    groups: dict[tuple[str, str], list[ParsedListing]] = defaultdict(list)
    for parsed in parsed_listings:
        key = _group_key(parsed)
        if key is not None:
            groups[key].append(parsed)

    valued: list[ValuedListing] = []
    for group in groups.values():
        if len(group) < min_group_size:
            continue

        normalized_prices = [
            item.listing.price / condition_multiplier(item.condition_score)
            for item in group
        ]
        baseline = statistics.median(normalized_prices)

        for item in group:
            fair_value = baseline * condition_multiplier(item.condition_score)
            if fair_value <= 0:
                continue
            deal_score = (fair_value - item.listing.price) / fair_value
            valued.append(
                ValuedListing(parsed=item, fair_value=fair_value, deal_score=deal_score)
            )

    return valued
