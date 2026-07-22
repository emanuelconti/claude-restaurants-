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

# Matches the real markup verified against a live kleinanzeigen.de response
# (see sources/kleinanzeigen.py docstring) — a plain <li data-href="..."> per
# listing, no Product/Offer JSON-LD on search-results pages.
FAKE_KLEINANZEIGEN_HTML = """
<html><body>
<li class="j-adlistitem adlist--item" data-href="/s-anzeige/rennrad/123" data-adid="123">
  <div class="adlist--item--descarea">
    <strong class="adlist--item--boldtitle">
      <a href="/s-anzeige/rennrad/123">Rennrad Trek Domane</a>
    </strong>
    <div class="adlist--item--description">
      <div class="long-description">guter Zustand</div>
    </div>
    <div class="adlist--item--price">780 € VB</div>
  </div>
  <img src="https://example.com/rad.jpg" />
</li>
<li class="adlist--item-banner j-liberty-wrapper">
  <div>this is a promoted banner, not a real ad, and must be skipped</div>
</li>
</body></html>
"""


def test_kleinanzeigen_scrapes_real_markup_structure():
    listings = kleinanzeigen._scrape_html(FAKE_KLEINANZEIGEN_HTML, "Berlin")
    assert len(listings) == 1
    assert listings[0].title == "Rennrad Trek Domane"
    assert listings[0].price == 780.0
    assert listings[0].description == "guter Zustand"
    assert listings[0].url == "https://www.kleinanzeigen.de/s-anzeige/rennrad/123"
    assert listings[0].source == "kleinanzeigen"


def test_kleinanzeigen_skips_banner_items_without_data_href():
    html = '<li class="adlist--item-banner j-liberty-wrapper"><div>ad banner</div></li>'
    assert kleinanzeigen._scrape_html(html, "Berlin") == []


def test_subito_prefers_json_ld_when_present():
    listings = subito._from_json_ld(FAKE_JSON_LD_PAGE, "Milano")
    assert len(listings) == 1
    assert listings[0].price == 450.0
    assert listings[0].source == "subito"
