import sys
import time
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sowld.parse import parse_listings
from sowld.sources.common import Listing


class _FakeMessages:
    def create(self, model, max_tokens, system, messages):
        title = messages[0]["content"].split("\n", 1)[0].removeprefix("Title: ")
        time.sleep(0.05)  # simulate network latency, like a real API call
        text = f'{{"brand": "{title}", "model": null, "variant": null, "year": null, "size": null, "condition_score": null}}'
        return SimpleNamespace(content=[SimpleNamespace(type="text", text=text)])


class _FakeClient:
    def __init__(self):
        self.messages = _FakeMessages()


def _listing(title: str) -> Listing:
    return Listing(title=title, price=100.0, description="", url="u", location="Roma")


def test_parse_listings_preserves_input_order_under_concurrency():
    listings = [_listing(f"item-{i}") for i in range(20)]
    parsed = parse_listings(listings, client=_FakeClient())
    assert [p.brand for p in parsed] == [f"item-{i}" for i in range(20)]


def test_parse_listings_runs_faster_than_serial_would(monkeypatch):
    listings = [_listing(f"item-{i}") for i in range(8)]
    start = time.monotonic()
    parse_listings(listings, client=_FakeClient())
    elapsed = time.monotonic() - start
    # Serial would take ~8 * 0.05s = 0.4s; concurrent (8 workers) should be
    # close to a single call's latency.
    assert elapsed < 0.3


def test_parse_listings_handles_empty_input():
    assert parse_listings([], client=_FakeClient()) == []
