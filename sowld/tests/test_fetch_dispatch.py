import sys
import time
from pathlib import Path

import pytest
import requests

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sowld.fetch import DEFAULT_SOURCE, SOURCES, fetch_listings
from sowld.sources.common import (
    extract_json_ld_products,
    request_with_backoff,
    retry_until_non_empty,
)


def test_all_expected_sources_registered():
    assert set(SOURCES) == {"wallapop", "leboncoin", "vinted", "kleinanzeigen", "subito", "ebay"}


def test_default_source_is_registered():
    assert DEFAULT_SOURCE in SOURCES


def test_unknown_source_raises():
    with pytest.raises(ValueError, match="Unknown source"):
        fetch_listings("bike", "Barcelona", source="not-a-real-marketplace")


def test_extract_json_ld_products_finds_offer():
    html = """
    <html><head>
    <script type="application/ld+json">
    {"@type": "Product", "name": "Trek Domane", "offers": {"@type": "Offer", "price": "780", "url": "https://example.com/1"}}
    </script>
    </head></html>
    """
    products = extract_json_ld_products(html)
    assert len(products) == 1
    assert products[0]["name"] == "Trek Domane"


def test_extract_json_ld_products_handles_list_and_nesting():
    html = """
    <script type="application/ld+json">
    [{"@type": "ItemList", "itemListElement": [
        {"@type": "Product", "name": "Bike A"},
        {"@type": "Product", "name": "Bike B"}
    ]}]
    </script>
    """
    products = extract_json_ld_products(html)
    names = {p["name"] for p in products}
    assert names == {"Bike A", "Bike B"}


def test_extract_json_ld_products_ignores_invalid_json():
    html = '<script type="application/ld+json">{not valid json}</script>'
    assert extract_json_ld_products(html) == []


def test_extract_json_ld_products_empty_when_absent():
    assert extract_json_ld_products("<html><body>no structured data here</body></html>") == []


def test_request_with_backoff_succeeds_after_transient_failures():
    calls = {"n": 0}

    def flaky():
        calls["n"] += 1
        if calls["n"] < 3:
            raise requests.ConnectionError("boom")
        return "ok"

    result = request_with_backoff(flaky, attempts=3, base_delay=0.01)
    assert result == "ok"
    assert calls["n"] == 3


def test_request_with_backoff_raises_after_exhausting_attempts():
    def always_fails():
        raise requests.ConnectionError("boom")

    with pytest.raises(requests.ConnectionError):
        request_with_backoff(always_fails, attempts=2, base_delay=0.01)


def test_retry_until_non_empty_stops_at_first_non_empty_result():
    calls = {"n": 0}

    def sometimes_empty():
        calls["n"] += 1
        return [] if calls["n"] < 2 else ["deal"]

    result = retry_until_non_empty(sometimes_empty, attempts=3, base_delay=0.01)
    assert result == ["deal"]
    assert calls["n"] == 2


def test_retry_until_non_empty_gives_up_and_returns_empty():
    result = retry_until_non_empty(lambda: [], attempts=2, base_delay=0.01)
    assert result == []
