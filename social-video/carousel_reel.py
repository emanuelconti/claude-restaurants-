#!/usr/bin/env python3
"""Turn a rendered carousel into an Instagram Reel (vertical video, gentle motion, original music) and post it.

    python3 carousel_reel.py --date 2026-11-06 --slot 3                        # builds reel.mp4 only (look at it)
    python3 carousel_reel.py --date 2026-11-06 --slot 3 --publish --token-env INSTAGRAM_TOKEN_SOWLD

The owner (4 November 2026): 3-4 Reels a day on every Instagram profile, besides the carousels, premium,
targeted, with good music. Each Reel is built from a carousel rendered for it (new topic, its own slot):
every slide is shown full width on a 1080x1920 canvas in the account's colours, with a slow zoom, soft
cross-fades and an original synthesized track (no copyrighted music). Same file on all three accounts:
it uses the folder's own ig_publish.py for the account, the token and the temporary public hosts.
Limits: at most MAX_REELS Reels a day per account; stop without retry on blocked/limit/spam/restricted/
temporarily/too soon. Tokens are never printed.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import subprocess
import sys
import wave
from zoneinfo import ZoneInfo

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ig_publish as IG  # noqa: E402

MAX_REELS = 4
SLIDE_SECONDS = 2.6
MADRID = ZoneInfo("Europe/Madrid")


def music(seconds: float, path: str, sr: int = 44100) -> None:
    """An original warm track: a slow major-seventh pad, soft kick on every beat at 100 BPM, light hi-hat."""
    t = np.arange(int(seconds * sr)) / sr
    beat = 60 / 100
    chords = [(261.6, 329.6, 392.0, 493.9), (220.0, 261.6, 329.6, 392.0), (174.6, 220.0, 261.6, 329.6), (196.0, 246.9, 293.7, 349.2)]
    pad = np.zeros_like(t)
    bar = beat * 4
    for i, f in enumerate(chords * int(seconds // (bar * 4) + 1)):
        s, e = int(i * bar * sr), int(min((i + 1) * bar, seconds) * sr)
        if s >= len(t):
            break
        seg = t[s:e] - t[s]
        env = np.minimum(1, seg / 0.4) * np.minimum(1, (bar - seg) / 0.4)
        pad[s:e] += sum(np.sin(2 * np.pi * x * seg) for x in f) * env * 0.05
    kick = np.zeros_like(t)
    for k in np.arange(0, seconds, beat):
        s = int(k * sr)
        seg = np.arange(min(int(0.25 * sr), len(t) - s)) / sr
        kick[s:s + len(seg)] += np.sin(2 * np.pi * (60 + 80 * np.exp(-seg * 30)) * seg) * np.exp(-seg * 12) * 0.35
    hat = np.zeros_like(t)
    rng = np.random.default_rng(7)
    for k in np.arange(beat / 2, seconds, beat):
        s = int(k * sr)
        n = min(int(0.05 * sr), len(t) - s)
        hat[s:s + n] += rng.standard_normal(n) * np.exp(-np.arange(n) / sr * 80) * 0.04
    mix = pad + kick + hat
    fade = np.minimum(1, t / 1.0) * np.minimum(1, (seconds - t) / 1.5)
    mix = np.clip(mix * fade, -1, 1)
    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes((mix * 32000).astype(np.int16).tobytes())


def build(folder: str, slides: list) -> str:
    seconds = SLIDE_SECONDS * len(slides)
    audio = os.path.join(folder, "music.wav")
    music(seconds, audio)
    cmd = ["ffmpeg", "-y", "-loglevel", "error"]
    for s in slides:
        cmd += ["-i", os.path.join(folder, s)]
    cmd += ["-i", audio]
    frames = int(SLIDE_SECONDS * 30)
    parts = []
    for i in range(len(slides)):
        # slow zoom-in on the full slide, centred on a dark canvas (4:5 slide on 9:16)
        parts.append(f"[{i}:v]scale=2160:2700:flags=lanczos,zoompan=z='min(zoom+0.0007,1.06)':d={frames}:"
                     f"x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1080x1350:fps=30,"
                     f"pad=1080:1920:0:285:color=0x121214,setsar=1,format=yuv420p,"
                     f"fade=t=in:st=0:d=0.3,fade=t=out:st={SLIDE_SECONDS - 0.3}:d=0.3[v{i}]")
    graph = ";".join(parts) + ";" + "".join(f"[v{i}]" for i in range(len(slides))) + f"concat=n={len(slides)}:v=1:a=0[out]"
    dst = os.path.join(folder, "reel.mp4")
    cmd += ["-filter_complex", graph, "-map", "[out]", "-map", f"{len(slides)}:a", "-c:v", "libx264", "-preset", "slow",
            "-crf", "17", "-maxrate", "12M", "-bufsize", "24M", "-r", "30", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", dst]
    subprocess.run(cmd, check=True)
    return dst


def stop_on(message: str) -> None:
    if any(w in message.lower() for w in ("blocked", "limit", "spam", "restricted", "temporarily", "too soon")):
        sys.exit(f"stopped, nothing retried: {message}")


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--date", required=True)
    ap.add_argument("--slot", type=int, required=True)
    ap.add_argument("--out", default=os.path.join(HERE, "out"))
    ap.add_argument("--token-env", default="INSTAGRAM_ACCESS_TOKEN")
    ap.add_argument("--publish", action="store_true")
    args = ap.parse_args()
    folder = os.path.join(args.out, args.date, f"carousel-{args.slot}")
    meta = json.load(open(os.path.join(folder, "carousel.json"), encoding="utf-8"))
    video = build(folder, meta["slides"])
    print(f"reel ready: {video} ({len(meta['slides'])} slides, {SLIDE_SECONDS * len(meta['slides']):.0f} s)")
    if not args.publish:
        print("dry run: nothing published")
        return
    token = os.environ.get(args.token_env, "").strip()
    if not token:
        sys.exit(f"{args.token_env} is not set: nothing published")
    if token.startswith("EAA"):
        IG.API = "https://graph.facebook.com/v21.0"
    id_env = "INSTAGRAM_USER_ID" if args.token_env == "INSTAGRAM_ACCESS_TOKEN" else "INSTAGRAM_USER_ID_" + args.token_env.replace("INSTAGRAM_TOKEN_", "")
    known = os.environ.get(id_env, "").strip() or getattr(IG, "KNOWN_IG_IDS", {}).get(args.token_env, "")
    if known:
        os.environ["INSTAGRAM_USER_ID"] = known
    if args.token_env != "INSTAGRAM_ACCESS_TOKEN":
        os.environ["IG_STRICT_ACCOUNT"] = "1"
    try:
        user, _ = IG.resolve(token, None) if hasattr(IG, "resolve") else IG.account(token)
        recent = IG.call("GET", f"{user}/media", token, {"fields": "caption,media_type,media_product_type,timestamp", "limit": 40}).get("data", [])
        today = dt.datetime.now(MADRID).date()
        reels = [m for m in recent if m.get("media_product_type") == "REELS"
                 and dt.datetime.strptime(m["timestamp"], "%Y-%m-%dT%H:%M:%S%z").astimezone(MADRID).date() == today]
        if len(reels) >= MAX_REELS:
            print(f"daily cap: {len(reels)} Reels already today, nothing published")
            return
        first = meta["caption"].split("\n", 1)[0].strip()
        if any((m.get("caption") or "").startswith(first) and m.get("media_product_type") == "REELS" for m in recent):
            print("already published as a Reel: nothing published")
            return
        url = None
        for _, host in IG.HOSTS:
            try:
                url = IG.upload_temporary(video, host)
                break
            except Exception as error:
                print(f"upload did not work ({error}); trying the next host", file=sys.stderr)
        if not url:
            sys.exit("could not make the video public: nothing published")
        item = IG.call("POST", f"{user}/media", token, {"media_type": "REELS", "video_url": url, "caption": meta["caption"], "share_to_feed": "true"})
        IG.wait_ready(item["id"], token, timeout=300)
        media = IG.call("POST", f"{user}/media_publish", token, {"creation_id": item["id"]})
        link = IG.call("GET", media["id"], token, {"fields": "permalink"}).get("permalink")
    except IG.ApiError as error:
        stop_on(str(error))
        sys.exit(f"Instagram: {error}")
    json.dump({"media_id": media["id"], "permalink": link}, open(os.path.join(folder, "published-reel.json"), "w"))
    print(f"published Reel: {link}")


if __name__ == "__main__":
    main()
