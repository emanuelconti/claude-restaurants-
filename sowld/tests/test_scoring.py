import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sowld.fetch import Listing
from sowld.parse import ParsedListing
from sowld.scoring import filter_and_rank
from sowld.valuation import ValuedListing


def make_valued(deal_score):
    listing = Listing(
        title="item", price=100, description="", url="u", location="Barcelona"
    )
    parsed = ParsedListing(
        listing=listing,
        brand="b",
        model="m",
        variant=None,
        year=None,
        size=None,
        condition_score=3,
    )
    fair_value = 100 / (1 - deal_score) if deal_score < 1 else 999
    return ValuedListing(parsed=parsed, fair_value=fair_value, deal_score=deal_score)


def test_filters_below_threshold():
    deals = [make_valued(0.1), make_valued(0.3), make_valued(0.5)]
    result = filter_and_rank(deals, threshold=0.25)
    assert {d.deal_score for d in result} == {0.3, 0.5}


def test_ranks_descending_by_deal_score():
    deals = [make_valued(0.3), make_valued(0.8), make_valued(0.4)]
    result = filter_and_rank(deals, threshold=0.25)
    scores = [d.deal_score for d in result]
    assert scores == sorted(scores, reverse=True)


def test_empty_input_returns_empty_list():
    assert filter_and_rank([], threshold=0.25) == []
