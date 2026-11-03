#!/usr/bin/env python3
"""Publish a rendered reel (out/<date>/reel/reel.mp4) on Good Message Studio's Instagram, and share it to the feed.

    python3 reel_publish.py --token-env INSTAGRAM_TOKEN_SOWLD --date 2026-11-02

Same rules as ig_publish.py, read from it so they can never drift apart: the
daily cap and the minimum gap are counted on the account itself (a reel counts
as a post), the same caption is never published twice, and any answer from Meta
that says blocked, limit, spam, restricted or temporarily stops the run.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import sys
from zoneinfo import ZoneInfo

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ig_publish as IG  # noqa: E402


def wait_video(container: str, token: str, timeout: float = 600) -> None:
    IG.wait_ready(container, token, timeout)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--date", required=True)
    ap.add_argument("--out", default=os.path.join(HERE, "out"))
    ap.add_argument("--token-env", default="INSTAGRAM_TOKEN_SOWLD")
    ap.add_argument("--ig-id", default=None)
    args = ap.parse_args()
    token = os.environ.get(args.token_env, "").strip()
    if not token:
        sys.exit(f"{args.token_env} is not set: nothing published")
    # The account id exactly as ig_publish.py finds it: the flag, the env var next to the token, the known ids.
    id_env = "INSTAGRAM_USER_ID_" + args.token_env[len("INSTAGRAM_TOKEN_"):] if args.token_env.startswith("INSTAGRAM_TOKEN_") else "INSTAGRAM_USER_ID"
    resolved = args.ig_id or os.environ.get(id_env, "").strip() or getattr(IG, "KNOWN_IG_IDS", {}).get(args.token_env, "")
    if resolved:
        os.environ["INSTAGRAM_USER_ID"] = resolved
    os.environ["IG_STRICT_ACCOUNT"] = "1"
    if token.startswith("EAA"):
        IG.API = "https://graph.facebook.com/v21.0"
    folder = os.path.join(args.out, args.date, "reel")
    meta = json.load(open(os.path.join(folder, "reel.json"), encoding="utf-8"))
    try:
        user, username = IG.resolve(token, None)
        print(f"account: @{username}")
        recent = IG.call("GET", f"{user}/media", token, {"fields": "caption,permalink,timestamp", "limit": 10}).get("data", [])
        first = meta["caption"].split("\n", 1)[0].strip()
        done = next((m for m in recent if (m.get("caption") or "").strip().startswith(first)), None)
        if done:
            print(f"already published: {done.get('permalink')}")
            return
        local = ZoneInfo("Asia/Singapore")
        now = dt.datetime.now(dt.timezone.utc)
        stamps = [dt.datetime.strptime(m["timestamp"], "%Y-%m-%dT%H:%M:%S%z") for m in recent if m.get("timestamp")]
        today = sum(1 for t in stamps if t.astimezone(local).date() == now.astimezone(local).date())
        if today >= IG.DAILY_CAP:
            print(f"daily cap: the account already has {today} posts today, nothing published")
            return
        if stamps and (now - max(stamps)).total_seconds() < IG.MIN_GAP * 60:
            sys.exit(f"too soon: the last post went out {int((now - max(stamps)).total_seconds() // 60)} min ago (minimum {IG.MIN_GAP}), nothing published")
        url, problems = os.environ.get("GMS_PUBLIC_VIDEO_URL") or None, []
        if url:
            import urllib.request
            with urllib.request.urlopen(urllib.request.Request(url, headers={"Range": "bytes=0-63"}), timeout=60) as response:
                header = response.read(64)
            if header[4:8] != b"ftyp":
                raise IG.ApiError("Approved public video URL did not serve an MP4 file")
        for name, host in ([] if url else IG.HOSTS):
            try:
                url = IG.upload_temporary(os.path.join(folder, meta["video"]), host)
                print(f"video is public ({name})")
                break
            except IG.ApiError as error:
                problems.append(f"{name}: {error}")
        if not url:
            sys.exit("could not make the video public: " + "; ".join(problems))
        item = IG.call("POST", f"{user}/media", token, {"media_type": "REELS", "video_url": url, "caption": meta["caption"], "share_to_feed": "true"})
        wait_video(item["id"], token)
        media = IG.call("POST", f"{user}/media_publish", token, {"creation_id": item["id"]})
        link = IG.call("GET", media["id"], token, {"fields": "permalink"}).get("permalink")
    except IG.ApiError as error:
        sys.exit(f"Instagram: {error}")
    json.dump({"media_id": media["id"], "permalink": link}, open(os.path.join(folder, "published.json"), "w"), indent=1)
    print(f"published: {link}")


if __name__ == "__main__":
    main()
