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
# (see sources/kleinanzeigen.py docstring) — an <article class="aditem"
# data-href="..."> per listing, no Product/Offer JSON-LD on search-results
# pages. Re-verified 2026-07-21: the site replaced the earlier
# <li class="j-adlistitem"> structure with this one without notice.
FAKE_KLEINANZEIGEN_HTML = """
<html><body>
<li class="ad-listitem fully-clickable-card">
  <article class="aditem" data-adid="123" data-href="/s-anzeige/rennrad/123">
    <div class="aditem-main">
      <div class="aditem-main--middle">
        <h2 class="text-module-begin">
          <a class="ellipsis" href="/s-anzeige/rennrad/123">Rennrad Trek Domane</a>
        </h2>
        <p class="aditem-main--middle--description">guter Zustand</p>
        <div class="aditem-main--middle--price-shipping">
          <p class="aditem-main--middle--price-shipping--price">780 € VB</p>
        </div>
      </div>
    </div>
    <img src="https://example.com/rad.jpg" />
  </article>
</li>
<li class="ad-listitem badge-topad is-topad">
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
    html = '<li class="ad-listitem badge-topad is-topad"><div>ad banner</div></li>'
    assert kleinanzeigen._scrape_html(html, "Berlin") == []


def test_subito_prefers_json_ld_when_present():
    listings = subito._from_json_ld(FAKE_JSON_LD_PAGE, "Milano")
    assert len(listings) == 1
    assert listings[0].price == 450.0
    assert listings[0].source == "subito"
