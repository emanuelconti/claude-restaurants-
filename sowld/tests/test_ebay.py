import sys
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sowld.sources import ebay
from sowld.sources.common import Listing


def test_item_to_listing_maps_fields_and_uses_condition_as_description():
    item = {
        "title": "Trek Domane SL6",
        "price": {"value": "780.0", "currency": "EUR"},
        "condition": "Used",
        "itemWebUrl": "https://www.ebay.de/itm/12345",
        "image": {"imageUrl": "https://example.com/img.jpg"},
    }
    listing = ebay._item_to_listing(item, "EBAY_DE")
    assert isinstance(listing, Listing)
    assert listing.title == "Trek Domane SL6"
    assert listing.price == 780.0
    assert listing.description == "Used"
    assert listing.url == "https://www.ebay.de/itm/12345"
    assert listing.photo_urls == ["https://example.com/img.jpg"]
    assert listing.source == "ebay"


def test_item_to_listing_handles_missing_price_and_image():
    listing = ebay._item_to_listing({"title": "Mystery item"}, "EBAY_DE")
    assert listing.price == 0.0
    assert listing.photo_urls == []


def test_get_access_token_requires_credentials(monkeypatch):
    monkeypatch.delenv("EBAY_CLIENT_ID", raising=False)
    monkeypatch.delenv("EBAY_CLIENT_SECRET", raising=False)
    ebay._token_cache["token"] = ""
    ebay._token_cache["expires_at"] = 0.0
    try:
        ebay._get_access_token()
        assert False, "expected RuntimeError"
    except RuntimeError as exc:
        assert "EBAY_CLIENT_ID" in str(exc)


def test_get_access_token_uses_cache_without_a_new_request(monkeypatch):
    ebay._token_cache["token"] = "cached-token"
    ebay._token_cache["expires_at"] = ebay.time.time() + 3600
    with patch("sowld.sources.ebay.requests.post") as mock_post:
        token = ebay._get_access_token()
    assert token == "cached-token"
    mock_post.assert_not_called()


def test_marketplace_ids_cover_expected_countries():
    assert ebay.MARKETPLACE_IDS["it"] == "EBAY_IT"
    assert ebay.MARKETPLACE_IDS["fr"] == "EBAY_FR"
    assert ebay.MARKETPLACE_IDS["es"] == "EBAY_ES"
    assert ebay.MARKETPLACE_IDS["de"] == "EBAY_DE"
    assert ebay.DEFAULT_MARKETPLACE == "EBAY_DE"
