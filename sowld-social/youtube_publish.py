#!/usr/bin/env python3
"""YouTube Shorts for Good Message Studio: the day's reel uploaded as a Short. OFF by default.

    python3 youtube_publish.py --date 2026-11-02              # dry run (the default): checks, uploads nothing
    python3 youtube_publish.py --date 2026-11-02 --publish    # only when GMS_YOUTUBE_ENABLED=1

Needs, in the environment (names only; values never printed):
- YOUTUBE_CLIENT_ID_GMS, YOUTUBE_CLIENT_SECRET_GMS: an OAuth client of a Google Cloud
  project with the YouTube Data API v3 enabled;
- YOUTUBE_REFRESH_TOKEN_GMS: a refresh token for the Good Message Studio channel with
  the scopes youtube.upload and youtube.readonly (one consent by the owner);
- GMS_YOUTUBE_ENABLED=1: set by the owner once the channel and rights are confirmed;
- GMS_YOUTUBE_PRIVACY (optional): "private" by default. Google keeps videos uploaded by
  an unverified project private anyway; set "public" only after the project passes
  Google's API audit.

Rules from channel_guard.py: 6 uploads a day at most, 60 minutes since the last upload,
20 minutes since the last Instagram/Facebook post, stop on any pushback word.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import carousels as C  # noqa: E402
import channel_guard as G  # noqa: E402


def open_text(path: str) -> str:
    with open(path, encoding="utf-8") as fh:
        return fh.read()

API = "https://www.googleapis.com/youtube/v3"
UPLOAD = "https://www.googleapis.com/upload/youtube/v3/videos?uploadType=resumable&part=snippet,status"
NEEDED = ("YOUTUBE_CLIENT_ID_GMS", "YOUTUBE_CLIENT_SECRET_GMS", "YOUTUBE_REFRESH_TOKEN_GMS")


def probe(path: str) -> tuple:
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height",
                          "-show_entries", "format=duration", "-of", "json", path], capture_output=True, text=True, check=True)
    info = json.loads(out.stdout)
    s = info["streams"][0]
    return int(s["width"]), int(s["height"]), float(info["format"]["duration"])


def access_token() -> str:
    form = {"client_id": os.environ["YOUTUBE_CLIENT_ID_GMS"].strip(), "client_secret": os.environ["YOUTUBE_CLIENT_SECRET_GMS"].strip(),
            "refresh_token": os.environ["YOUTUBE_REFRESH_TOKEN_GMS"].strip(), "grant_type": "refresh_token"}
    tok = G.http("POST", "https://oauth2.googleapis.com/token", form=form).get("access_token")
    if not tok:
        raise RuntimeError("Google did not return an access token (refresh token revoked or expired?)")
    return tok


def recent_stamps(token: str) -> tuple:
    ch = G.http("GET", f"{API}/channels?part=snippet,contentDetails&mine=true", token).get("items", [])
    if not ch:
        raise RuntimeError("no YouTube channel on this account")
    uploads = ch[0]["contentDetails"]["relatedPlaylists"]["uploads"]
    items = G.http("GET", f"{API}/playlistItems?part=contentDetails&maxResults=10&playlistId={uploads}", token).get("items", [])
    stamps = [dt.datetime.fromisoformat(i["contentDetails"]["videoPublishedAt"].replace("Z", "+00:00"))
              for i in items if i.get("contentDetails", {}).get("videoPublishedAt")]
    return ch[0]["snippet"].get("title", "?"), stamps


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--date", required=True)
    ap.add_argument("--out", default=os.path.join(HERE, "out"))
    ap.add_argument("--publish", action="store_true", help="really upload (needs GMS_YOUTUBE_ENABLED=1)")
    args = ap.parse_args()

    folder = os.path.join(args.out, args.date, "reel")
    meta = json.loads(open_text(os.path.join(folder, "reel.json")))
    video = os.path.join(folder, meta["video"])
    w, h, seconds = probe(video)
    if h <= w or seconds > 60:
        sys.exit(f"not a Short: {w}x{h}, {seconds:.1f} s (needs vertical and at most 60 s): nothing uploaded")
    title = (meta["title"][:90] + " #Shorts")[:100]
    parts = [p.strip() for p in meta["caption"].split("\n\n") if p.strip()]
    description = "\n\n".join([p for p in parts[1:] if C.CAPTION_SHARE not in p] + [C.CAPTION_SHARE_LINK])[:4900]
    privacy = os.environ.get("GMS_YOUTUBE_PRIVACY", "private").strip() or "private"
    print(f"plan: 1 Short, {w}x{h}, {seconds:.1f} s, title {title!r}, privacy {privacy}")

    gaps = G.missing(*NEEDED)
    if gaps:
        print("YouTube not connected: missing " + ", ".join(gaps) + ". Dry run only, nothing uploaded.")
        return
    try:
        token = access_token()
        channel, stamps = recent_stamps(token)
        print(f"channel ok: {channel}, {len(stamps)} recent uploads read")
        if not args.publish:
            print("dry run: nothing uploaded (pass --publish, with GMS_YOUTUBE_ENABLED=1)")
            return
        if not G.enabled("youtube"):
            print("YouTube is OFF (GMS_YOUTUBE_ENABLED is not 1): nothing uploaded")
            return
        G.check_limits(stamps, "YouTube")
        G.check_cross_channel()
        size = os.path.getsize(video)
        init = G.http("POST", UPLOAD, token, body={
            "snippet": {"title": title, "description": description, "categoryId": "26",
                        "tags": ["goodmessagestudio", "singapore", "kindness", "hoodie", "giftideas"]},
            "status": {"privacyStatus": privacy, "selfDeclaredMadeForKids": False}},
            headers={"X-Upload-Content-Type": "video/mp4", "X-Upload-Content-Length": str(size)})
        location = init.get("_headers", {}).get("Location") or init.get("_headers", {}).get("location")
        if not location:
            raise RuntimeError("YouTube did not return an upload address")
        with open(video, "rb") as fh:
            done = G.http("PUT", location, token, data=fh.read(), headers={"Content-Type": "video/mp4"}, timeout=600)
        print(f"published ({privacy}): https://www.youtube.com/shorts/{done.get('id')}")
    except G.Stop as stop:
        sys.exit(str(stop))
    except RuntimeError as error:
        sys.exit(f"YouTube: {error}")


if __name__ == "__main__":
    main()
