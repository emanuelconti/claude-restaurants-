import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sowld.sources import kleinanzeigen, subito

FAKE_JSON_LD_PAGE = """
<html><head>
<script type="application/ld+json">
{"@type": "Product", "name": "Bici da corsa", "description": "Ottimo stato",
 "offers": {"@type": "Offer", "price": "450", "url": "https://example.com/annuncio/1"},
 "image": "https://example.com/img1.jpg"}
</script>
</head></html>
"""

FAKE_KLEINANZEIGEN_HTML = """
<html><body>
<article class="aditem">
  <a class="ellipsis" href="/s-anzeige/rennrad/123">Rennrad Trek Domane</a>
  <div class="aditem-main--middle--price-shipping--price">780 €</div>
  <div class="aditem-main--middle--description">guter Zustand</div>
  <img src="https://example.com/rad.jpg" />
</article>
</body></html>
"""


def test_kleinanzeigen_prefers_json_ld_when_present():
    listings = kleinanzeigen._from_json_ld(FAKE_JSON_LD_PAGE, "Berlin")
    assert len(listings) == 1
    assert listings[0].title == "Bici da corsa"
    assert listings[0].price == 450.0
    assert listings[0].source == "kleinanzeigen"


def test_kleinanzeigen_falls_back_to_html_scrape():
    listings = kleinanzeigen._scrape_html(FAKE_KLEINANZEIGEN_HTML, "Berlin")
    assert len(listings) == 1
    assert listings[0].title == "Rennrad Trek Domane"
    assert listings[0].price == 780.0
    assert listings[0].url == "https://www.kleinanzeigen.de/s-anzeige/rennrad/123"


def test_subito_prefers_json_ld_when_present():
    listings = subito._from_json_ld(FAKE_JSON_LD_PAGE, "Milano")
    assert len(listings) == 1
    assert listings[0].price == 450.0
    assert listings[0].source == "subito"


def test_kleinanzeigen_json_ld_skips_products_without_price():
    html = """
    <script type="application/ld+json">
    {"@type": "Product", "name": "No price item", "offers": {"@type": "Offer"}}
    </script>
    """
    assert kleinanzeigen._from_json_ld(html, "Berlin") == []
