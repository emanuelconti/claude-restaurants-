import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sowld.fetch import Listing
from sowld.parse import ParsedListing
from sowld.valuation import compute_fair_values, condition_multiplier


def make_parsed(price, brand="trek", model="domane", condition=3):
    listing = Listing(
        title=f"{brand} {model}",
        price=price,
        description="",
        url="https://example.com",
        location="Barcelona",
    )
    return ParsedListing(
        listing=listing,
        brand=brand,
        model=model,
        variant=None,
        year=None,
        size=None,
        condition_score=condition,
    )


def test_condition_multiplier_baseline_is_neutral():
    assert condition_multiplier(3) == 1.0


def test_condition_multiplier_scales_with_score():
    assert condition_multiplier(5) > condition_multiplier(3) > condition_multiplier(1)


def test_condition_multiplier_defaults_missing_to_baseline():
    assert condition_multiplier(None) == condition_multiplier(3)


def test_fair_value_is_median_of_comparables():
    group = [make_parsed(p) for p in (900, 1000, 1100)]
    valued = compute_fair_values(group)
    fair_values = {v.fair_value for v in valued}
    assert fair_values == {1000.0}


def test_underpriced_listing_gets_positive_deal_score():
    group = [make_parsed(1000), make_parsed(1000), make_parsed(600)]
    valued = compute_fair_values(group)
    cheap = next(v for v in valued if v.parsed.listing.price == 600)
    assert cheap.deal_score >= 0.25


def test_condition_shifts_fair_value():
    # Two mint-condition (5) items anchor the baseline; a beat-up (1) item
    # of the same model should get a lower fair value, not the raw median.
    group = [make_parsed(1000, condition=5), make_parsed(1000, condition=5), make_parsed(700, condition=1)]
    valued = compute_fair_values(group)
    poor_condition = next(v for v in valued if v.parsed.condition_score == 1)
    mint_condition = next(v for v in valued if v.parsed.condition_score == 5)
    assert poor_condition.fair_value < mint_condition.fair_value


def test_groups_smaller_than_minimum_are_skipped():
    group = [make_parsed(900, brand="rare", model="onlyone")]
    assert compute_fair_values(group) == []


def test_listings_missing_brand_or_model_are_skipped():
    listing = Listing(
        title="mystery bike",
        price=500,
        description="",
        url="https://example.com",
        location="Barcelona",
    )
    parsed = ParsedListing(
        listing=listing,
        brand=None,
        model=None,
        variant=None,
        year=None,
        size=None,
        condition_score=3,
    )
    assert compute_fair_values([parsed, parsed]) == []


def test_different_models_are_not_compared_to_each_other():
    group = [
        make_parsed(1000, brand="trek", model="domane"),
        make_parsed(1000, brand="trek", model="domane"),
        make_parsed(200, brand="specialized", model="allez"),
    ]
    valued = compute_fair_values(group)
    # only the trek domane group has >= 2 members, allez has just 1
    assert all(v.parsed.brand == "trek" for v in valued)
