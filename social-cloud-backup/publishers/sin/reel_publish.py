#!/usr/bin/env python3
"""Publish a reviewed Sincronia Reel (queue/sin/<date>/<reel-dir>/reel.mp4) on @sincronia.live.

    python3 reel_publish.py --token-env INSTAGRAM_TOKEN_SINCRONIA --date 2026-11-07 --reel-dir reel-3 --out <queue/sin>

Europe/Paris day and the same eight-post cap as ig_publish.py.
"""
import argparse, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))
import ig_publish as IG  # noqa: E402
import reel_common as RC  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", required=True)
    ap.add_argument("--reel-dir", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--token-env", default="INSTAGRAM_TOKEN_SINCRONIA")
    args = ap.parse_args()
    if os.path.basename(args.reel_dir) != args.reel_dir:
        sys.exit("invalid reel folder: nothing published")
    token = os.environ.get(args.token_env, "").strip()
    if not token:
        sys.exit(f"{args.token_env} is not set: nothing published")
    if not token.startswith("EAA"):
        IG.API = "https://graph.instagram.com/v21.0"
    try:
        user, username = IG.account(token, None)
        if username != "sincronia.live":
            sys.exit("wrong Instagram account: nothing published")
        RC.publish(IG, user, username, token, os.path.join(args.out, args.date, args.reel_dir), "Europe/Paris", IG.DAILY_CAP)
    except IG.ApiError as error:
        sys.exit(f"Instagram: {error}")


if __name__ == "__main__":
    main()
