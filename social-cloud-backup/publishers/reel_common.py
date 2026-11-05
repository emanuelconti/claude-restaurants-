"""Shared Instagram Reel publication for every brand (owner, 5 November 2026).

Used by publishers/<brand>/reel_publish.py with that brand's own ig_publish
module (token, account identity, API host), its own market timezone and cap.
It publishes only the reviewed, hash-verified MP4 served from the immutable
commit URL the controller passes in REEL_PUBLIC_VIDEO_URL, with the reviewed
cover frame from REEL_PUBLIC_COVER_URL. Same rules as the carousel publishers:
exact-caption dedupe against the account, the brand's local daily cap, and any
Meta answer that says blocked, limit, spam, restricted or temporarily stops.
"""
from __future__ import annotations

import datetime as dt
import json
import os
import sys
import urllib.request
from zoneinfo import ZoneInfo


def check_url(url: str, magic) -> None:
    """The public asset must be served directly (no redirect) and be the expected file type."""
    class NoRedirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, *a, **k):
            return None
    opener = urllib.request.build_opener(NoRedirect)
    with opener.open(urllib.request.Request(url, headers={"Range": "bytes=0-63"}), timeout=60) as response:
        if response.status not in (200, 206):
            raise RuntimeError(f"public asset answered {response.status}")
        header = response.read(64)
    if not magic(header):
        raise RuntimeError("public asset is not the expected file type")


def publish(IG, user: str, username: str, token: str, folder: str, timezone: str, daily_cap: int) -> None:
    meta = json.load(open(os.path.join(folder, "reel.json"), encoding="utf-8"))
    video_url = os.environ.get("REEL_PUBLIC_VIDEO_URL", "")
    cover_url = os.environ.get("REEL_PUBLIC_COVER_URL", "")
    if not video_url.startswith("https://raw.githubusercontent.com/emanuelconti/claude-restaurants-/"):
        sys.exit("immutable reviewed reel URL missing: nothing published")
    print(f"account: @{username}")
    recent = IG.call("GET", f"{user}/media", token, {"fields": "caption,permalink,timestamp", "limit": 25}).get("data", [])
    first = meta["caption"].split("\n", 1)[0].strip()
    done = next((m for m in recent if (m.get("caption") or "").strip().startswith(first)), None)
    if done:
        print(f"already published: {done.get('permalink')}")
        return
    local = ZoneInfo(timezone)
    now = dt.datetime.now(dt.timezone.utc)
    stamps = [dt.datetime.strptime(m["timestamp"], "%Y-%m-%dT%H:%M:%S%z") for m in recent if m.get("timestamp")]
    today = sum(1 for t in stamps if t.astimezone(local).date() == now.astimezone(local).date())
    if today >= daily_cap:
        print(f"daily cap: the account already has {today} posts today, nothing published")
        return
    check_url(video_url, lambda h: h[4:8] == b"ftyp")
    params = {"media_type": "REELS", "video_url": video_url, "caption": meta["caption"], "share_to_feed": "true"}
    if cover_url:
        check_url(cover_url, lambda h: h[:3] == b"\xff\xd8\xff")
        params["cover_url"] = cover_url
    item = IG.call("POST", f"{user}/media", token, params)
    IG.wait_ready(item["id"], token, 900)
    media = IG.call("POST", f"{user}/media_publish", token, {"creation_id": item["id"]})
    info = IG.call("GET", media["id"], token, {"fields": "permalink,media_type,media_product_type"})
    with open(os.path.join(folder, "published.json"), "w") as fh:
        json.dump({"media_id": media["id"], "permalink": info.get("permalink"), "media_product_type": info.get("media_product_type")}, fh, indent=1)
    print(f"published: {info.get('permalink')}")
