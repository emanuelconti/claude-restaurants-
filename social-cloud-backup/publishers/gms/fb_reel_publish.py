#!/usr/bin/env python3
"""Publish a reviewed Good Message Studio Reel on its Facebook Page via Meta's native Page Reels API.

    python3 fb_reel_publish.py --date 2026-11-07 --reel-dir reel-7 --out <queue/gms>

Supported path (developers.facebook.com/docs/video-api/guides/reels-publishing,
read 5 November 2026): POST /{page-id}/video_reels upload_phase=start, upload
the local reviewed bytes to rupload.facebook.com, then upload_phase=finish with
video_state=PUBLISHED. Meta allows 30 API-published Reels per Page per rolling
24 hours; the owner's cap is far lower (eight Facebook posts a Singapore day in
total, 60 minutes apart, enforced by the controller and again here).

Safety: identity check, exact-caption dedupe against both feed posts and
Reels, Singapore daily cap, 60-minute gap, local ffprobe/audio checks before
upload, and a post-publication read-back of status, length and permalink.
Any Meta answer that says blocked, limit, spam, restricted or temporarily stops.
A started upload is never retried blindly.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import fb_publish as F  # noqa: E402

RUPLOAD = "https://rupload.facebook.com/video-upload/v21.0/"


def reels(page: str, token: str) -> list:
    rows = F.call("GET", f"{page}/video_reels", token, {"fields": "description,created_time,permalink_url", "limit": 25}).get("data", [])
    return [dict(message=r.get("description") or "", created_time=r.get("created_time"), permalink_url=r.get("permalink_url")) for r in rows]


def probe(path: str) -> dict:
    out = json.loads(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "stream=codec_type,width,height,r_frame_rate",
                                              "-show_entries", "format=duration", "-of", "json", path], text=True))
    video = next(s for s in out["streams"] if s["codec_type"] == "video")
    audio = [s for s in out["streams"] if s["codec_type"] == "audio"]
    seconds = float(out["format"]["duration"])
    if (video["width"], video["height"]) != (1080, 1920) or not audio or not 3 <= seconds <= 90:
        raise RuntimeError("reel is not a 1080x1920 video with audio between 3 and 90 seconds")
    return dict(seconds=seconds)


def upload(video_id: str, token: str, path: str) -> None:
    data = open(path, "rb").read()
    req = urllib.request.Request(RUPLOAD + video_id, data=data, method="POST",
                                 headers={"Authorization": f"OAuth {token}", "offset": "0", "file_size": str(len(data))})
    try:
        with urllib.request.urlopen(req, timeout=600) as r:
            body = json.loads(r.read().decode() or "{}")
    except urllib.error.HTTPError as error:
        message = error.read().decode()[:300]
        if any(w in message.lower() for w in F.STOP_WORDS):
            raise F.Stop(f"Meta says: {message}. Stopped, nothing retried.") from None
        raise RuntimeError(f"Reel upload failed: {message}") from None
    if not body.get("success"):
        raise RuntimeError("Reel upload not acknowledged")


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--date", required=True)
    ap.add_argument("--reel-dir", default="reel")
    ap.add_argument("--out", default=os.path.join(HERE, "out"))
    args = ap.parse_args()
    if os.path.basename(args.reel_dir) != args.reel_dir:
        sys.exit("invalid reel folder: nothing published")
    token = os.environ.get("FB_PAGE_TOKEN_GMS", "").strip()
    page = os.environ.get("FB_PAGE_ID_GMS", "").strip()
    if not token or not page:
        sys.exit("FB_PAGE_TOKEN_GMS or FB_PAGE_ID_GMS is not set: nothing published")
    folder = os.path.join(args.out, args.date, args.reel_dir)
    meta = json.load(open(os.path.join(folder, "reel.json"), encoding="utf-8"))
    path = os.path.join(folder, meta["video"])
    try:
        token = F.page_token(page, token)
        if F.call("GET", page, token, {"fields": "name"}).get("name") != "Good Message Studio":
            sys.exit("wrong Facebook Page identity: nothing published")
        local = probe(path)
        first = meta["caption"].split("\n", 1)[0].strip()
        posts = F.recent(page, token) + reels(page, token)
        done = next((p for p in posts if (p.get("message") or "").strip().startswith(first)), None)
        if done:
            print(f"already published: {done.get('permalink_url')}")
            return
        now = dt.datetime.now(dt.timezone.utc)
        stamps = [dt.datetime.strptime(p["created_time"], "%Y-%m-%dT%H:%M:%S%z") for p in posts if p.get("created_time")]
        today = sum(1 for s in stamps if s.astimezone(F.SINGAPORE).date() == now.astimezone(F.SINGAPORE).date())
        if today >= F.MAX_PER_DAY:
            print(f"daily cap: the Page already has {today} posts today, nothing published")
            return
        if stamps and (now - max(stamps)).total_seconds() < F.MIN_GAP * 60:
            sys.exit(f"too soon: the last post went out {int((now - max(stamps)).total_seconds() // 60)} min ago (minimum {F.MIN_GAP}), nothing published")
        message = meta["caption"].replace("(link in bio)", "").replace("  ", " ")
        if "https://goodmessagestudio.com" not in message:
            message += "\n\nShop now: https://goodmessagestudio.com"
        start = F.call("POST", f"{page}/video_reels", token, {"upload_phase": "start"})
        video_id = start.get("video_id")
        if not video_id:
            raise RuntimeError("Reel upload session not opened; nothing published")
        upload(video_id, token, path)
        F.call("POST", f"{page}/video_reels", token, {"upload_phase": "finish", "video_id": video_id,
                                                      "video_state": "PUBLISHED", "description": message})
        status = {}
        for _ in range(60):
            status = F.call("GET", video_id, token, {"fields": "status,permalink_url,length"})
            st = status.get("status", {})
            if st.get("video_status") in ("error", "expired", "upload_failed"):
                raise RuntimeError(f"Facebook Reel processing failed: {st.get('video_status')}")
            phase = st.get("publishing_phase") or {}
            if st.get("video_status") == "ready" and (phase.get("status") == "complete" or phase.get("publish_status") == "published"):
                break
            time.sleep(10)
        st = status.get("status", {})
        phase = st.get("publishing_phase") or {}
        if st.get("video_status") != "ready" or not (phase.get("status") == "complete" or phase.get("publish_status") == "published"):
            raise RuntimeError(f"Facebook Reel still {st.get('video_status')} after 10 minutes; held for reconciliation")
        length = float(status.get("length") or 0)
        if abs(length - local["seconds"]) > 1.0:
            raise RuntimeError(f"Facebook Reel length {length} does not match the reviewed file")
        link = status.get("permalink_url") or ""
        if link.startswith("/"):
            link = "https://www.facebook.com" + link
    except F.Stop as stop:
        sys.exit(str(stop))
    except RuntimeError as error:
        sys.exit(f"Facebook: {error}")
    with open(os.path.join(folder, "published-facebook.json"), "w", encoding="utf-8") as fh:
        json.dump({"video_id": video_id, "permalink": link, "format": "native_page_reel", "length": length}, fh, indent=1)
    print(f"published: {link}")


if __name__ == "__main__":
    main()
