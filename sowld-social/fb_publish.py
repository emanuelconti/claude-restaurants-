#!/usr/bin/env python3
"""Publish a rendered carousel on Good Message Studio's Facebook Page, as one post with all its slides.

    python3 fb_publish.py --check-token
    python3 fb_publish.py --date 2026-11-02 --slot 1            # the same slides and caption as the Instagram post

The owner (1 November 2026): no ad budget, so the shop's carousels go out
organically on Facebook too. It reads, from the environment:
- FB_PAGE_TOKEN_GMS: a Page access token for the "Good Message Studio" Page,
  with pages_manage_posts and pages_read_engagement (a long-lived one), or the
  owner's user token with those permissions plus pages_show_list: the script
  then asks Facebook for the Page token itself;
- FB_PAGE_ID_GMS: the Page's id.

Same safety rules as ig_publish.py: at most 3 posts a day (Europe/Madrid),
at least 60 minutes between posts, never the same caption twice, and it stops
for good on any answer from Meta that says blocked, limit, spam, restricted or
temporarily. The token never goes in a URL or in the output.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from zoneinfo import ZoneInfo

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import carousels as C  # noqa: E402
import ig_publish as IG  # noqa: E402  (temporary image hosts, shared with Instagram)

API = "https://graph.facebook.com/v21.0"
MAX_PER_DAY = 6  # the owner, 1 November 2026: 6 a day for Good Message Studio
MIN_GAP = 60  # minutes
STOP_WORDS = ("blocked", "limit", "spam", "restricted", "temporarily")
MADRID = ZoneInfo("Europe/Madrid")


class Stop(RuntimeError):
    pass


def call(method: str, path: str, token: str, params: dict | None = None) -> dict:
    params = dict(params or {})
    url = f"{API}/{path}"
    data = None
    if method == "GET":
        if params:
            url += "?" + urllib.parse.urlencode(params)
    else:
        data = urllib.parse.urlencode(params).encode()
    req = urllib.request.Request(url, data=data, method=method, headers={"Authorization": f"Bearer {token}"})
    try:
        with urllib.request.urlopen(req, timeout=90) as r:
            return json.loads(r.read().decode() or "{}")
    except urllib.error.HTTPError as error:
        try:
            message = json.loads(error.read().decode()).get("error", {}).get("message", "")
        except Exception:
            message = str(error)
        if any(w in message.lower() for w in STOP_WORDS):
            raise Stop(f"Meta says: {message}. Stopped, nothing retried.") from None
        raise RuntimeError(f"{method} {path}: {message}") from None


SHOP = "https://goodmessagestudio.com"


def to_square(src: str, dst: str) -> None:
    """A 4:5 slide on a 1:1 card, whole and centred on its own background colour, so nothing is cropped."""
    from PIL import Image
    im = Image.open(src).convert("RGB")
    bg = im.getpixel((4, 4))
    side = max(im.width, im.height)
    canvas = Image.new("RGB", (side, side), bg)
    canvas.paste(im, ((side - im.width) // 2, (side - im.height) // 2))
    canvas.resize((1080, 1080), Image.LANCZOS).save(dst, "JPEG", quality=90)


def hosted_by_facebook(page: str, token: str, url: str) -> str:
    """Cards showed up blank (2 November 2026): Facebook fetched the picture later from the temporary host,
    which had expired or refused it. So each card image is first uploaded to the Page as an unpublished
    photo, and the card uses Facebook's own copy of it, which does not disappear."""
    photo = call("POST", f"{page}/photos", token, {"url": url, "published": "false"})
    images = call("GET", photo["id"], token, {"fields": "images"}).get("images", [])
    if not images:
        raise RuntimeError("Facebook stored the photo but returned no image address")
    return max(images, key=lambda i: i.get("width", 0))["source"]


def page_token(page: str, token: str) -> str:
    """Return a Page token: FB_PAGE_TOKEN_GMS may hold the owner's user token
    instead (1 November 2026), and a user token with pages_show_list can ask for
    the Page's own token. A Page token asking for itself gets no access_token
    back, so it is used as it is."""
    try:
        return call("GET", page, token, {"fields": "access_token"}).get("access_token") or token
    except RuntimeError:
        return token


def recent(page: str, token: str) -> list:
    return call("GET", f"{page}/posts", token, {"fields": "message,created_time,permalink_url", "limit": 25}).get("data", [])


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--date")
    ap.add_argument("--slot", type=int, default=1)
    ap.add_argument("--out", default=os.path.join(HERE, "out"))
    ap.add_argument("--check-token", action="store_true")
    args = ap.parse_args()
    token = os.environ.get("FB_PAGE_TOKEN_GMS", "").strip()
    page = os.environ.get("FB_PAGE_ID_GMS", "").strip()
    if not token or not page:
        sys.exit("FB_PAGE_TOKEN_GMS or FB_PAGE_ID_GMS is not set: nothing published")
    try:
        token = page_token(page, token)
        if args.check_token:
            name = call("GET", page, token, {"fields": "name"}).get("name", "?")
            print(f"token ok: Page {name!r}, {len(recent(page, token))} recent posts read, publishing not tried")
            return
        if not args.date:
            ap.error("--date is needed to publish")
        folder = os.path.join(args.out, args.date, f"carousel-{args.slot}")
        meta = json.load(open(os.path.join(folder, "carousel.json"), encoding="utf-8"))
        first = meta["caption"].split("\n", 1)[0].strip()
        posts = recent(page, token)
        done = next((p for p in posts if (p.get("message") or "").strip().startswith(first)), None)
        if done:
            print(f"already published: {done.get('permalink_url')}")
            return
        now = dt.datetime.now(dt.timezone.utc)
        stamps = [dt.datetime.strptime(p["created_time"], "%Y-%m-%dT%H:%M:%S%z") for p in posts if p.get("created_time")]
        today = sum(1 for s in stamps if s.astimezone(MADRID).date() == now.astimezone(MADRID).date())
        if today >= MAX_PER_DAY:
            print(f"daily cap: the Page already has {today} posts today, nothing published")
            return
        if stamps and (now - max(stamps)).total_seconds() < MIN_GAP * 60:
            sys.exit(f"too soon: the last post went out {int((now - max(stamps)).total_seconds() // 60)} min ago (minimum {MIN_GAP}), nothing published")
        # The owner (1 November 2026): on Facebook the post must be one image you swipe, like a Meta ads
        # carousel, not a grid of small photos. So it is a link carousel: each slide is a card (square, as
        # Facebook shows them) that opens the shop when tapped.
        def public(path):
            for _, host in IG.HOSTS:
                try:
                    return IG.upload_temporary(path, host)
                except Exception as error:
                    print(f"upload did not work ({error}); trying the next host", file=sys.stderr)
            sys.exit(f"could not make {os.path.basename(path)} public: nothing published")

        cards = []
        for i, name in enumerate(meta["slides"][:10]):
            square = os.path.join(folder, name.replace(".jpg", "-square.jpg"))
            to_square(os.path.join(folder, name), square)
            cards.append({"link": SHOP, "picture": hosted_by_facebook(page, token, public(square)),
                          "name": meta["title"] if i == 0 else "Shop now at goodmessagestudio.com",
                          "description": "Good Message Studio"})
        message = meta["caption"].replace(C.CAPTION_SHARE, C.CAPTION_SHARE_LINK).replace(C.CAPTION_SAVE, C.CAPTION_SAVE + "\n\n" + C.CAPTION_SHARE_LINK)
        params = {"message": message, "link": SHOP, "multi_share_end_card": "false",
                  "multi_share_optimized": "false", "child_attachments": json.dumps(cards)}
        try:
            post = call("POST", f"{page}/feed", token, params)
        except RuntimeError as error:
            # Some Pages take at most 5 cards: keep the cover, the first points and the shop slide.
            if "child" not in str(error).lower() and "attachment" not in str(error).lower():
                raise
            keep = cards[:4] + [cards[-2] if len(cards) > 5 else cards[-1]]
            params["child_attachments"] = json.dumps(keep[:5])
            post = call("POST", f"{page}/feed", token, params)
        link = call("GET", post["id"], token, {"fields": "permalink_url"}).get("permalink_url")
    except Stop as stop:
        sys.exit(str(stop))
    except RuntimeError as error:
        sys.exit(f"Facebook: {error}")
    with open(os.path.join(folder, "published-facebook.json"), "w", encoding="utf-8") as fh:
        json.dump({"post_id": post["id"], "permalink": link}, fh, indent=1)
    print(f"published: {link}")


if __name__ == "__main__":
    main()
