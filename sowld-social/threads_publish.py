#!/usr/bin/env python3
"""Publish a rendered Good Message Studio carousel on Threads, as one carousel post.

    python3 threads_publish.py --check-token
    python3 threads_publish.py --date 2026-11-02 --slot 1 --dry-run   # every check, nothing published
    python3 threads_publish.py --date 2026-11-02 --slot 1      # the same slides as the Instagram post (needs GMS_THREADS_ENABLED=1)

It reads THREADS_TOKEN_GMS from the environment: a Threads access token for the
Good Message Studio profile with threads_basic and threads_content_publish
(made in the same Meta app, "Threads API" use case). The token goes in an
Authorization header, never in a URL or in the output.

Same safety rules as ig_publish.py: at most 6 posts a day (Asia/Singapore date),
at least 60 minutes between posts, never the same first line twice, and a full
stop on any answer that says blocked, limit, spam, restricted or temporarily.
Threads takes at most 500 characters of text, so the caption is shortened to the
title, the hook and the shop line.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from zoneinfo import ZoneInfo

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import carousels as C  # noqa: E402
import ig_publish as IG  # noqa: E402  (temporary image hosts)

API = "https://graph.threads.net/v1.0"
MAX_PER_DAY = 10  # (the owner, 2 November 2026: 10 a day, never in a burst: 60 minutes apart)
MIN_GAP = 0  # owner, 2 Nov 2026: no wait on Threads (Facebook keeps 60)
STOP_WORDS = ("blocked", "limit", "spam", "restricted", "temporarily", "too soon")
SINGAPORE = ZoneInfo("Asia/Singapore")


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
            raise Stop(f"Threads says: {message}. Stopped, nothing retried.") from None
        raise RuntimeError(f"{method} {path}: {message}") from None


def wait_ready(container: str, token: str, timeout: float = 180) -> None:
    end = time.time() + timeout
    while True:
        status = call("GET", container, token, {"fields": "status"}).get("status")
        if status in (None, "FINISHED", "PUBLISHED"):
            return
        if status in ("ERROR", "EXPIRED"):
            raise RuntimeError(f"container {container}: {status}")
        if time.time() > end:
            raise RuntimeError(f"container {container}: still {status}")
        time.sleep(4)


def short_caption(caption: str) -> str:
    parts = [p.strip() for p in caption.split("\n\n") if p.strip() and not p.strip().startswith("#")]
    text = "\n\n".join(parts[:2] + [C.CAPTION_SHARE_LINK])  # a real, clickable link on Threads
    return text if len(text) <= 500 else text[:497].rsplit(" ", 1)[0] + "..."


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--date")
    ap.add_argument("--slot", type=int, default=1)
    ap.add_argument("--out", default=os.path.join(HERE, "out"))
    ap.add_argument("--check-token", action="store_true")
    ap.add_argument("--dry-run", action="store_true", help="every check, nothing published")
    args = ap.parse_args()
    token = os.environ.get("THREADS_TOKEN_GMS", "").strip()
    if not token:
        sys.exit("THREADS_TOKEN_GMS is not set: nothing published")
    try:
        me = call("GET", "me", token, {"fields": "id,username"})
        user = me["id"]
        posts = call("GET", f"{user}/threads", token, {"fields": "text,timestamp,permalink", "limit": 25}).get("data", [])
        if args.check_token:
            print(f"token ok: @{me.get('username', '?')}, {len(posts)} recent posts read, publishing not tried")
            return
        if not args.date:
            ap.error("--date is needed to publish")
        folder = os.path.join(args.out, args.date, f"carousel-{args.slot}")
        meta = json.load(open(os.path.join(folder, "carousel.json"), encoding="utf-8"))
        text = short_caption(meta["caption"])
        first = text.split("\n", 1)[0].strip()
        done = next((p for p in posts if (p.get("text") or "").strip().startswith(first)), None)
        if done:
            print(f"already published: {done.get('permalink')}")
            return
        now = dt.datetime.now(dt.timezone.utc)
        stamps = [dt.datetime.strptime(p["timestamp"], "%Y-%m-%dT%H:%M:%S%z") for p in posts if p.get("timestamp")]
        today = sum(1 for s in stamps if s.astimezone(SINGAPORE).date() == now.astimezone(SINGAPORE).date())
        if today >= MAX_PER_DAY:
            print(f"daily cap: the profile already has {today} posts today, nothing published")
            return
        if stamps and (now - max(stamps)).total_seconds() < MIN_GAP * 60:
            sys.exit(f"too soon: the last post went out {int((now - max(stamps)).total_seconds() // 60)} min ago (minimum {MIN_GAP}), nothing published")
        if args.dry_run:
            print(f"dry run: {len(meta['slides'])} slides and {len(text)} characters of text would be posted; nothing published")
            return
        # OFF until the owner confirms the account and rights (1 November 2026).
        if os.environ.get("GMS_THREADS_ENABLED", "").strip() != "1":
            print("Threads is OFF (GMS_THREADS_ENABLED is not 1): nothing published")
            return
        import channel_guard as G
        try:
            G.check_cross_channel()
        except G.Stop as stop:
            sys.exit(str(stop))
        children = []
        for name in meta["slides"][:20]:
            url = None
            for _, host in IG.HOSTS:
                try:
                    url = IG.upload_temporary(os.path.join(folder, name), host)
                    break
                except Exception as error:
                    print(f"upload did not work ({error}); trying the next host", file=sys.stderr)
            if not url:
                sys.exit(f"could not make {name} public: nothing published")
            item = call("POST", f"{user}/threads", token, {"media_type": "IMAGE", "image_url": url, "is_carousel_item": "true"})
            children.append(item["id"])
        for child in children:
            wait_ready(child, token)
        post = call("POST", f"{user}/threads", token, {"media_type": "CAROUSEL", "children": ",".join(children), "text": text})
        wait_ready(post["id"], token)
        media = call("POST", f"{user}/threads_publish", token, {"creation_id": post["id"]})
        link = call("GET", media["id"], token, {"fields": "permalink"}).get("permalink")
    except Stop as stop:
        sys.exit(str(stop))
    except RuntimeError as error:
        sys.exit(f"Threads: {error}")
    json.dump({"media_id": media["id"], "permalink": link}, open(os.path.join(folder, "published-threads.json"), "w"), indent=1)
    print(f"published: {link}")


if __name__ == "__main__":
    main()
