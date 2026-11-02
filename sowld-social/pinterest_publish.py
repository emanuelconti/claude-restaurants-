#!/usr/bin/env python3
"""Pinterest for Good Message Studio: the day's carousel as one carousel Pin linking to the shop. OFF by default.

    python3 pinterest_publish.py --date 2026-11-02 --slot 1              # dry run (the default): checks, publishes nothing
    python3 pinterest_publish.py --date 2026-11-02 --slot 1 --publish    # only when GMS_PINTEREST_ENABLED=1

Needs, in the environment (names only; values never printed):
- PINTEREST_APP_SECRET_GMS + PINTEREST_REFRESH_TOKEN_GMS (from pinterest_oauth.py; best: the access
  token is renewed on every run), or PINTEREST_TOKEN_GMS, a ready access token for the Good Message Studio
  business account with boards:read, pins:read and pins:write. Trial access is not
  enough for public Pins: Standard access must be approved first.
- PINTEREST_BOARD_GMS: the board's id (or its exact name; the id is looked up).
- GMS_PINTEREST_ENABLED=1: set by the owner once the app is approved and the
  account and rights are confirmed. Without it nothing is ever published.

Rules from channel_guard.py: 6 Pins a day at most, 60 minutes since the last Pin,
20 minutes since the last Instagram/Facebook post, stop on any pushback word.
A carousel Pin takes 2 to 5 images: the cover, three points and the shop slide.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import carousels as C  # noqa: E402
import channel_guard as G  # noqa: E402


def open_text(path: str) -> str:
    with open(path, encoding="utf-8") as fh:
        return fh.read()

API = "https://api.pinterest.com/v5"
SHOP = "https://goodmessagestudio.com"
NEEDED = ("PINTEREST_BOARD_GMS",)
# Either a ready access token (PINTEREST_TOKEN_GMS) or, better, the app's id and secret plus the long-lived
# refresh token from pinterest_oauth.py: then a fresh access token is made on every run and never expires.
REFRESH = ("PINTEREST_APP_SECRET_GMS", "PINTEREST_REFRESH_TOKEN_GMS")


def get_token() -> str | None:
    if os.environ.get("PINTEREST_REFRESH_TOKEN_GMS", "").strip() and os.environ.get("PINTEREST_APP_SECRET_GMS", "").strip():
        import pinterest_oauth
        return pinterest_oauth.refresh(os.environ["PINTEREST_REFRESH_TOKEN_GMS"].strip())
    return os.environ.get("PINTEREST_TOKEN_GMS", "").strip() or None


def pick_slides(slides: list) -> list:
    """Cover, up to three points, and the shop slide (the one before the follow slide)."""
    if len(slides) <= 5:
        return slides
    return [slides[0]] + slides[1:4] + [slides[-2]]


def pin_text(meta: dict) -> tuple:
    parts = [p.strip() for p in meta["caption"].split("\n\n") if p.strip()]
    tags = [p for p in parts if p.startswith("#")]
    body = [p for p in parts[1:] if not p.startswith("#") and C.CAPTION_SHARE not in p]
    title = meta["title"][:100]
    description = " ".join(body + [C.CAPTION_SHARE_LINK] + tags[:1])[:500]
    return title, description


def board_id(token: str, wanted: str) -> str:
    if wanted.isdigit():
        return wanted
    for b in G.http("GET", f"{API}/boards?page_size=100", token).get("items", []):
        if b.get("name", "").strip().lower() == wanted.strip().lower():
            return b["id"]
    raise RuntimeError(f"no board named {wanted!r} on this account")


def recent_stamps(token: str) -> list:
    pins = G.http("GET", f"{API}/pins?page_size=25", token).get("items", [])
    out = []
    for p in pins:
        if p.get("created_at"):
            stamp = dt.datetime.fromisoformat(p["created_at"].replace("Z", "+00:00"))
            out.append(stamp if stamp.tzinfo else stamp.replace(tzinfo=dt.timezone.utc))  # Pinterest omits the zone: UTC
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--date", required=True)
    ap.add_argument("--slot", type=int, default=1)
    ap.add_argument("--out", default=os.path.join(HERE, "out"))
    ap.add_argument("--publish", action="store_true", help="really publish (needs GMS_PINTEREST_ENABLED=1)")
    args = ap.parse_args()

    folder = os.path.join(args.out, args.date, f"carousel-{args.slot}")
    meta = json.loads(open_text(os.path.join(folder, "carousel.json")))
    slides = pick_slides(meta["slides"])
    for s in slides:
        if not os.path.exists(os.path.join(folder, s)):
            sys.exit(f"slide missing: {s}: nothing published")
    title, description = pin_text(meta)
    print(f"plan: 1 carousel Pin, {len(slides)} images, title {title!r}, link {SHOP}")

    gaps = G.missing(*NEEDED)
    if not os.environ.get("PINTEREST_TOKEN_GMS", "").strip():
        gaps += G.missing(*REFRESH)
    if gaps:
        print("Pinterest not connected: missing " + ", ".join(gaps) + ". Dry run only, nothing published.")
        return
    try:
        token = get_token()
        user = G.http("GET", f"{API}/user_account", token)
        board = board_id(token, os.environ["PINTEREST_BOARD_GMS"].strip())
        stamps = recent_stamps(token)
        print(f"account ok: {user.get('username', '?')}, board found, {len(stamps)} recent Pins read")
        if not args.publish:
            print("dry run: nothing published (pass --publish, with GMS_PINTEREST_ENABLED=1)")
            return
        if not G.enabled("pinterest"):
            print("Pinterest is OFF (GMS_PINTEREST_ENABLED is not 1): nothing published")
            return
        G.check_limits(stamps, "Pinterest")
        G.check_cross_channel()
        urls = [G.public_url(os.path.join(folder, s)) for s in slides]
        source = ({"source_type": "image_url", "url": urls[0]} if len(urls) == 1 else
                  {"source_type": "multiple_image_urls", "items": [{"url": u, "title": title[:100], "link": SHOP} for u in urls]})
        pin = G.http("POST", f"{API}/pins", token, body={"board_id": board, "title": title, "description": description,
                                                         "link": SHOP, "alt_text": title, "media_source": source})
        print(f"published: https://www.pinterest.com/pin/{pin.get('id')}/")
    except G.Stop as stop:
        sys.exit(str(stop))
    except RuntimeError as error:
        sys.exit(f"Pinterest: {error}")


if __name__ == "__main__":
    main()
