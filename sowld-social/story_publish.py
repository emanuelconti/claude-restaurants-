#!/usr/bin/env python3
"""Post a Good Message Studio carousel as a Story on Instagram and on the Facebook Page.

    python3 story_publish.py --date 2026-11-02 --slot 3             # dry run: builds the story image only
    python3 story_publish.py --date 2026-11-02 --slot 3 --publish   # Instagram story, then Facebook Page story

The owner (2 November 2026): "like Meta ads usually do, add stories too". The story is the carousel
cover on a full 9:16 canvas with a "Shop now · link in bio" line. Same safety rules as the feed scripts:
at most 10 stories a day per channel, at least 60 minutes between two stories on the same channel, and
any blocked/limit/spam/restricted/temporarily/too soon answer stops the run with no retry.
Tokens are read from the environment only and never printed.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import sys

from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import brand as B  # noqa: E402
import ig_publish as IG  # noqa: E402

CAP, GAP = 10, 60


def build(folder: str, meta: dict) -> str:
    cover = Image.open(os.path.join(folder, meta["slides"][0])).convert("RGB")
    canvas = cover.resize((1080, 1920)).filter(ImageFilter.GaussianBlur(40))
    canvas = Image.blend(canvas, Image.new("RGB", canvas.size, (18, 18, 20)), 0.45)
    card = cover.copy()
    card.thumbnail((960, 1200))
    canvas.paste(card, ((1080 - card.width) // 2, 260))
    d = ImageDraw.Draw(canvas)
    font = B.font(64, path=B.SERIF)
    text = "Shop now · link in bio"
    w = d.textlength(text, font=font)
    d.text(((1080 - w) / 2, 260 + card.height + 90), text, font=font, fill=(255, 255, 255))
    out = os.path.join(folder, "story.jpg")
    canvas.save(out, quality=92)
    return out


def check(stamps: list, channel: str) -> None:
    now = dt.datetime.now(dt.timezone.utc)
    today = [s for s in stamps if now - s < dt.timedelta(hours=24)]
    if len(today) >= CAP:
        sys.exit(f"daily cap: {channel} already has {len(today)} stories in 24 hours, nothing published")
    if today and (now - max(today)).total_seconds() < GAP * 60:
        sys.exit(f"too soon: last {channel} story {int((now - max(today)).total_seconds() // 60)} min ago (minimum {GAP})")


def stop_on(message: str) -> None:
    if any(w in message.lower() for w in ("blocked", "limit", "spam", "restricted", "temporarily", "too soon")):
        sys.exit(f"stopped, nothing retried: {message}")


def instagram(path: str) -> str:
    token = os.environ.get("INSTAGRAM_TOKEN_SOWLD", "").strip()
    if not token:
        return "Instagram: INSTAGRAM_TOKEN_SOWLD missing, skipped"
    if token.startswith("EAA"):
        IG.API = "https://graph.facebook.com/v21.0"
    known = os.environ.get("INSTAGRAM_USER_ID_SOWLD", "").strip() or IG.KNOWN_IG_IDS.get("INSTAGRAM_TOKEN_SOWLD", "")
    if known:
        os.environ["INSTAGRAM_USER_ID"] = known
    os.environ["IG_STRICT_ACCOUNT"] = "1"
    try:
        user, _ = IG.resolve(token, None)
        live = IG.call("GET", f"{user}/stories", token, {"fields": "timestamp"}).get("data", [])
        check([dt.datetime.strptime(s["timestamp"], "%Y-%m-%dT%H:%M:%S%z") for s in live if s.get("timestamp")], "Instagram")
        url = None
        for _, host in IG.HOSTS:
            try:
                url = IG.upload_temporary(path, host)
                break
            except Exception as error:
                print(f"upload did not work ({error}); trying the next host", file=sys.stderr)
        if not url:
            return "Instagram: could not make the story image public, nothing published"
        box = IG.call("POST", f"{user}/media", token, {"image_url": url, "media_type": "STORIES"})
        IG.wait_ready(box["id"], token)
        media = IG.call("POST", f"{user}/media_publish", token, {"creation_id": box["id"]})
        return f"Instagram story published: {media.get('id')}"
    except IG.ApiError as error:
        stop_on(str(error))
        return f"Instagram: {error}"


def facebook(path: str) -> str:
    import fb_publish as FB
    token, page = os.environ.get("FB_PAGE_TOKEN_GMS", "").strip(), os.environ.get("FB_PAGE_ID_GMS", "").strip()
    if not (token and page):
        return "Facebook: FB_PAGE_TOKEN_GMS / FB_PAGE_ID_GMS missing, skipped"
    try:
        token = FB.page_token(page, token)
        live = FB.call("GET", f"{page}/stories", token, {"fields": "creation_time"}).get("data", [])
        stamps = []
        for s in live:
            t = s.get("creation_time")
            if t:
                stamps.append(dt.datetime.fromtimestamp(int(t), dt.timezone.utc) if str(t).isdigit()
                              else dt.datetime.strptime(t, "%Y-%m-%dT%H:%M:%S%z"))
        check(stamps, "Facebook")
        with open(path, "rb") as fh:
            data = fh.read()
        import urllib.request
        boundary = "gmsstory"
        body = (f"--{boundary}\r\nContent-Disposition: form-data; name=\"published\"\r\n\r\nfalse\r\n"
                f"--{boundary}\r\nContent-Disposition: form-data; name=\"source\"; filename=\"story.jpg\"\r\n"
                f"Content-Type: image/jpeg\r\n\r\n").encode() + data + f"\r\n--{boundary}--\r\n".encode()
        req = urllib.request.Request(f"{FB.API}/{page}/photos", data=body, method="POST",
                                     headers={"Authorization": f"Bearer {token}",
                                              "Content-Type": f"multipart/form-data; boundary={boundary}"})
        with urllib.request.urlopen(req, timeout=120) as r:
            photo = json.loads(r.read().decode())
        story = FB.call("POST", f"{page}/photo_stories", token, {"photo_id": photo["id"]})
        return f"Facebook story published: {story.get('post_id') or story.get('id')}"
    except RuntimeError as error:
        stop_on(str(error))
        return f"Facebook: {error}"
    except Exception as error:
        stop_on(str(error))
        return f"Facebook: {type(error).__name__}: {error}"


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--date", required=True)
    ap.add_argument("--slot", type=int, required=True)
    ap.add_argument("--out", default=os.path.join(HERE, "out"))
    ap.add_argument("--publish", action="store_true")
    args = ap.parse_args()
    folder = os.path.join(args.out, args.date, f"carousel-{args.slot}")
    meta = json.load(open(os.path.join(folder, "carousel.json"), encoding="utf-8"))
    path = build(folder, meta)
    if not args.publish:
        print(f"dry run: story image ready at {path}; nothing published")
        return
    print(instagram(path))
    print(facebook(path))


if __name__ == "__main__":
    main()
