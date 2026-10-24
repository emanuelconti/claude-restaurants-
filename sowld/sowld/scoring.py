"""Scoring step: filter for deals meaningfully below fair value, ranked best first."""

from __future__ import annotations

from .valuation import ValuedListing

DEFAULT_THRESHOLD = 0.25  # flag anything >= 25% under fair value


def filter_and_rank(
    valued_listings: list[ValuedListing],
    threshold: float = DEFAULT_THRESHOLD,
) -> list[ValuedListing]:
    deals = [v for v in valued_listings if v.deal_score >= threshold]
    deals.sort(key=lambda v: v.deal_score, reverse=True)
    return deals
