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
import re
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
# Owner, 13 November 2026 (stricter rule, wins over every older one): 9 posts were removed as spam on
# 6-7 November. Nothing before 16 November, then at most ONE post a day, at least 20 hours apart, text only
# (1-3 human sentences, no link, no hashtags, no slides).
THREADS_RESUME = "2026-11-16"
MAX_PER_DAY = 1
MIN_GAP = 20 * 60  # minutes
# Owner, 22 November 2026: "aggiungi le foto, con ottimizzazione". After a clean week of text posts, from
# PHOTO_FROM the daily post can carry ONE photo, the carousel's cover (still 1 post a day, no link, no hashtag).
# Optimisation: the days alternate text / photo until each kind has MIN_EACH posts since PHOTO_FROM, then the
# kind with more views per post (Threads insights) wins; without insights the days keep alternating.
PHOTO_FROM = "2026-11-30"
MIN_EACH = 5
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
    # Owner, 7 and 13 November: Threads removed posts as spam. A Threads post is 1-3 human sentences of the
    # topic itself: no link (it is on the profile), no hashtags, no shop or save/share lines, no slides.
    boiler = (C.CAPTION_SHARE_LINK, getattr(C, "CAPTION_SHARE", None), getattr(C, "CAPTION_SAVE", None))
    parts = [p.strip() for p in caption.split("\n\n") if p.strip() and not p.strip().startswith("#")
             and "http" not in p and "goodmessagestudio.com" not in p.lower() and p.strip() not in boiler]
    text = " ".join(parts[:1]).replace("\n", " ")
    text = re.sub(r"\s*#\w+", "", text).strip()
    sentences = re.split(r"(?<=[.!?])\s+", text)
    text = " ".join(sentences[:3]).strip()
    return text if len(text) <= 280 else text[:277].rsplit(" ", 1)[0] + "..."


def editorial_topic(date: str, title: str) -> dict | None:
    """The written topic of that day's carousel (editorial/gms-<date>.txt holds one JSON object per slot)."""
    try:
        raw = open(os.path.join(HERE, "..", "..", "editorial", f"gms-{date}.txt"), encoding="utf-8").read()
    except OSError:
        return None
    dec, i = json.JSONDecoder(), 0
    while i < len(raw):
        while i < len(raw) and raw[i].isspace():
            i += 1
        if i >= len(raw):
            break
        try:
            obj, i = dec.raw_decode(raw, i)
        except ValueError:
            return None
        if isinstance(obj, dict) and obj.get("title") == title:
            return obj
    return None


def threads_text(meta: dict, date: str = "") -> str:
    """The post itself, not the carousel's title (owner, 22 November: the profile showed only titles).

    The hook, then the carousel's ideas as short sentences, e.g. "A slow Saturday morning sets the tone.
    Wake up without an alarm. Breakfast at a kopitiam. A walk in a park. Plan nothing until noon."
    Still 1 post a day, text only, no link, no hashtags, no shop line, at most 280 characters.
    """
    topic = {"points": meta["points"]} if meta.get("points") else (editorial_topic(date, meta.get("title", "")) or {})
    parts = [p.strip() for p in meta.get("caption", "").split("\n\n") if p.strip()]
    hook = (topic.get("hook") or "").strip()
    if not hook and len(parts) > 1 and parts[0] == (meta.get("title") or "").strip():
        hook = parts[1]
    heads = [p[0].strip().rstrip(".!") for p in (topic.get("points") or [])
             if isinstance(p, (list, tuple)) and p and isinstance(p[0], str) and p[0].strip()]
    if not hook or "http" in hook or hook.startswith("#"):
        return short_caption(meta.get("caption", ""))
    picks = heads[:3] + ([heads[-1]] if len(heads) > 3 else [])
    text = hook if hook.endswith((".", "!", "?")) else hook + "."
    for head in picks:
        line = f"{head}."
        if "http" in line or "goodmessagestudio" in line.lower() or len(text) + 1 + len(line) > 280:
            break
        text += " " + line
    return re.sub(r"\s*#\w+", "", text).strip()


def pick_mode(date: str, history: list | None = None) -> str:
    """'TEXT' or 'IMAGE' for the post of this date. history: [(media_type, views)] of posts since PHOTO_FROM."""
    if not date or date < PHOTO_FROM:
        return "TEXT"
    history = history or []
    views = {kind: [v for k, v in history if k == kind and v is not None] for kind in ("TEXT", "IMAGE")}
    if all(len(v) >= MIN_EACH for v in views.values()):
        text_avg = sum(views["TEXT"]) / len(views["TEXT"])
        image_avg = sum(views["IMAGE"]) / len(views["IMAGE"])
        return "IMAGE" if image_avg > text_avg else "TEXT"
    day = dt.date.fromisoformat(date).toordinal() - dt.date.fromisoformat(PHOTO_FROM).toordinal()
    return "IMAGE" if day % 2 == 0 else "TEXT"


def history_since(user: str, token: str) -> list:
    """(media_type, views) of the profile's posts since PHOTO_FROM; views None when insights are not readable."""
    out = []
    try:
        posts = call("GET", f"{user}/threads", token, {"fields": "id,media_type,timestamp", "limit": 50}).get("data", [])
    except RuntimeError:
        return out
    for p in posts:
        if (p.get("timestamp") or "")[:10] < PHOTO_FROM or p.get("media_type") not in ("TEXT_POST", "IMAGE"):
            continue
        try:
            data = call("GET", f"{p['id']}/insights", token, {"metric": "views"}).get("data", [])
            v = data[0]["values"][0]["value"] if data and data[0].get("values") else data[0].get("total_value", {}).get("value")
        except (RuntimeError, KeyError, IndexError, TypeError):
            v = None
        out.append(("IMAGE" if p["media_type"] == "IMAGE" else "TEXT", v))
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--date")
    ap.add_argument("--slot", type=int, default=1)
    ap.add_argument("--out", default=os.path.join(HERE, "out"))
    ap.add_argument("--base-url", default=None, help="public folder URL of the carousel (photo days use its cover)")
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
        text = threads_text(meta, args.date)
        first = text.split("\n", 1)[0].strip()
        done = next((p for p in posts if (p.get("text") or "").strip().startswith(first)), None)
        if done:
            print(f"already published: {done.get('permalink')}")
            return
        now = dt.datetime.now(dt.timezone.utc)
        if now.astimezone(SINGAPORE).date().isoformat() < THREADS_RESUME:
            print(f"Threads is paused until {THREADS_RESUME} (owner, 13 November): nothing published")
            return
        if not text:
            sys.exit("no human text left after removing links and hashtags: nothing published")
        stamps = [dt.datetime.strptime(p["timestamp"], "%Y-%m-%dT%H:%M:%S%z") for p in posts if p.get("timestamp")]
        today = sum(1 for s in stamps if s.astimezone(SINGAPORE).date() == now.astimezone(SINGAPORE).date())
        if today >= MAX_PER_DAY:
            print(f"daily cap: the profile already has {today} posts today, nothing published")
            return
        if stamps and (now - max(stamps)).total_seconds() < MIN_GAP * 60:
            sys.exit(f"too soon: the last post went out {int((now - max(stamps)).total_seconds() // 60)} min ago (minimum {MIN_GAP}), nothing published")
        if args.dry_run:
            print(f"dry run: a text-only post of {len(text)} characters would be posted; nothing published")
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
        # Text only until PHOTO_FROM (owner, 13 November); then text or ONE photo, the cover (owner, 22 November).
        # Never slides, never a link.
        mode = pick_mode(args.date, history_since(user, token))
        params = {"media_type": "TEXT", "text": text}
        if mode == "IMAGE":
            cover = os.path.join(folder, (meta.get("slides") or ["slide-01.jpg"])[0])
            try:
                url = (args.base_url.rstrip("/") + "/" + os.path.basename(cover)) if args.base_url else IG.upload_temporary(cover)
                IG.check_public(url)
                params = {"media_type": "IMAGE", "image_url": url, "text": text}
            except Exception as error:  # the host failing never stops the post: it goes out as text
                print(f"photo host failed ({type(error).__name__}), posting text only")
                mode = "TEXT"
        post = call("POST", f"{user}/threads", token, params)
        wait_ready(post["id"], token)
        media = call("POST", f"{user}/threads_publish", token, {"creation_id": post["id"]})
        link = call("GET", media["id"], token, {"fields": "permalink"}).get("permalink")
    except Stop as stop:
        sys.exit(str(stop))
    except RuntimeError as error:
        sys.exit(f"Threads: {error}")
    json.dump({"media_id": media["id"], "permalink": link, "mode": mode}, open(os.path.join(folder, "published-threads.json"), "w"), indent=1)
    print(f"published: {link}")


if __name__ == "__main__":
    main()
