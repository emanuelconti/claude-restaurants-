#!/usr/bin/env python3
"""TikTok for Good Message Studio: the day's reel posted through the Content Posting API. OFF by default.

    python3 tiktok_publish.py --date 2026-11-02              # dry run (the default): checks, posts nothing
    python3 tiktok_publish.py --date 2026-11-02 --publish    # only when GMS_TIKTOK_ENABLED=1

Needs, in the environment (names only; values never printed):
- TIKTOK_CLIENT_KEY_GMS, TIKTOK_CLIENT_SECRET_GMS: the TikTok developer app's keys
  (Content Posting API product added, Direct Post enabled);
- TIKTOK_REFRESH_TOKEN_GMS: a refresh token for the Good Message Studio TikTok account
  with the scopes user.info.basic, video.list and video.publish (one consent by the owner);
- GMS_TIKTOK_ENABLED=1: set by the owner once the account, the app audit and the rights
  are confirmed;
- GMS_TIKTOK_PRIVACY (optional): SELF_ONLY by default. TikTok only lets an unaudited
  app post privately; PUBLIC_TO_EVERYONE needs the app to pass TikTok's audit, and the
  value must be one the account offers (creator_info).

Rules from channel_guard.py: 6 posts a day at most, 60 minutes since the last post,
20 minutes since the last Instagram/Facebook post, stop on any pushback word. Without
video.list the limits cannot be checked, so nothing is posted.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import carousels as C  # noqa: E402
import channel_guard as G  # noqa: E402


def open_text(path: str) -> str:
    with open(path, encoding="utf-8") as fh:
        return fh.read()

API = "https://open.tiktokapis.com/v2"
NEEDED = ("TIKTOK_CLIENT_KEY_GMS", "TIKTOK_CLIENT_SECRET_GMS", "TIKTOK_REFRESH_TOKEN_GMS")


def access_token() -> str:
    form = {"client_key": os.environ["TIKTOK_CLIENT_KEY_GMS"].strip(), "client_secret": os.environ["TIKTOK_CLIENT_SECRET_GMS"].strip(),
            "grant_type": "refresh_token", "refresh_token": os.environ["TIKTOK_REFRESH_TOKEN_GMS"].strip()}
    out = G.http("POST", "https://open.tiktokapis.com/v2/oauth/token/", form=form)
    if not out.get("access_token"):
        raise RuntimeError(f"TikTok did not return an access token: {out.get('error_description') or out.get('error') or 'unknown'}")
    return out["access_token"]


def check_ok(out: dict, what: str) -> dict:
    err = (out.get("error") or {})
    if err.get("code") not in (None, "ok"):
        G.stop_if_pushback(f"{err.get('code')} {err.get('message', '')}")
        raise RuntimeError(f"{what}: {err.get('code')} {err.get('message', '')}")
    return out.get("data") or {}


def recent_stamps(token: str) -> list:
    data = check_ok(G.http("POST", f"{API}/video/list/?fields=id,create_time", token, body={"max_count": 20}), "video list")
    return [dt.datetime.fromtimestamp(v["create_time"], dt.timezone.utc) for v in data.get("videos", []) if v.get("create_time")]


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--date", required=True)
    ap.add_argument("--out", default=os.path.join(HERE, "out"))
    ap.add_argument("--publish", action="store_true", help="really post (needs GMS_TIKTOK_ENABLED=1)")
    args = ap.parse_args()

    folder = os.path.join(args.out, args.date, "reel")
    meta = json.loads(open_text(os.path.join(folder, "reel.json")))
    video = os.path.join(folder, meta["video"])
    if not os.path.exists(video):
        sys.exit("reel.mp4 missing: nothing posted")
    tags = [p for p in meta["caption"].split("\n\n") if p.strip().startswith("#")]
    title = (meta["title"] + " " + (tags[0] if tags else "#goodmessagestudio"))[:2200]
    privacy = os.environ.get("GMS_TIKTOK_PRIVACY", "SELF_ONLY").strip() or "SELF_ONLY"
    print(f"plan: 1 video, {os.path.getsize(video) // 1024} KB, title {meta['title']!r}, privacy {privacy}")

    gaps = G.missing(*NEEDED)
    if gaps:
        print("TikTok not connected: missing " + ", ".join(gaps) + ". Dry run only, nothing posted.")
        return
    try:
        token = access_token()
        creator = check_ok(G.http("POST", f"{API}/post/publish/creator_info/query/", token, body={}), "creator info")
        options = creator.get("privacy_level_options", [])
        stamps = recent_stamps(token)
        print(f"account ok: {creator.get('creator_username', '?')}, privacy options {options}, {len(stamps)} recent videos read")
        if privacy not in options:
            sys.exit(f"privacy {privacy} is not offered to this account ({options}): nothing posted")
        if not args.publish:
            print("dry run: nothing posted (pass --publish, with GMS_TIKTOK_ENABLED=1)")
            return
        if not G.enabled("tiktok"):
            print("TikTok is OFF (GMS_TIKTOK_ENABLED is not 1): nothing posted")
            return
        G.check_limits(stamps, "TikTok")
        G.check_cross_channel()
        size = os.path.getsize(video)
        init = check_ok(G.http("POST", f"{API}/post/publish/video/init/", token, body={
            "post_info": {"title": title, "privacy_level": privacy, "disable_comment": False, "disable_duet": False, "disable_stitch": False},
            "source_info": {"source": "FILE_UPLOAD", "video_size": size, "chunk_size": size, "total_chunk_count": 1}}), "init")
        with open(video, "rb") as fh:
            G.http("PUT", init["upload_url"], data=fh.read(), headers={"Content-Type": "video/mp4", "Content-Range": f"bytes 0-{size - 1}/{size}"}, timeout=600)
        for _ in range(40):
            status = check_ok(G.http("POST", f"{API}/post/publish/status/fetch/", token, body={"publish_id": init["publish_id"]}), "status")
            if status.get("status") in ("PUBLISH_COMPLETE", "SEND_TO_USER_INBOX"):
                print(f"published ({privacy}): status {status.get('status')}, publish id {init['publish_id']}")
                return
            if status.get("status") == "FAILED":
                G.stop_if_pushback(str(status.get("fail_reason", "")))
                raise RuntimeError(f"TikTok failed: {status.get('fail_reason')}")
            time.sleep(6)
        raise RuntimeError("TikTok is still processing after 4 minutes; check the account before trying again")
    except G.Stop as stop:
        sys.exit(str(stop))
    except RuntimeError as error:
        sys.exit(f"TikTok: {error}")


if __name__ == "__main__":
    main()
