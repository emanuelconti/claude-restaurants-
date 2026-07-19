import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sowld.fetch import DEFAULT_SOURCE, SOURCES, fetch_listings
from sowld.sources.common import extract_json_ld_products


def test_all_expected_sources_registered():
    assert set(SOURCES) == {"wallapop", "leboncoin", "vinted", "kleinanzeigen", "subito"}


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
