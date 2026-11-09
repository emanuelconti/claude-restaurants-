#!/usr/bin/env python3
"""Answer comments on our own Instagram posts (allowed by the Instagram API: instagram_manage_comments).

    python3 comments.py --token-env INSTAGRAM_TOKEN_SOWLD --list            # comments from the last 10 posts with no reply from us
    python3 comments.py --token-env INSTAGRAM_TOKEN_SOWLD --reply <comment_id> "text"

The owner (9 November 2026): he cannot spend time on the accounts, so every run answers new comments on
our posts, warm and human, in the post's language, so people come back. Only our own posts; never like,
follow, comment or DM on other accounts (forbidden automation). At most 20 replies per run. Tokens are never printed.
"""

from __future__ import annotations

import argparse
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ig_publish as IG  # noqa: E402


def setup(token_env: str) -> tuple:
    token = os.environ.get(token_env, "").strip()
    if not token:
        sys.exit(f"{token_env} is not set")
    if token.startswith("EAA"):
        IG.API = "https://graph.facebook.com/v21.0"
    id_env = "INSTAGRAM_USER_ID" if token_env == "INSTAGRAM_ACCESS_TOKEN" else "INSTAGRAM_USER_ID_" + token_env.replace("INSTAGRAM_TOKEN_", "")
    known = os.environ.get(id_env, "").strip() or getattr(IG, "KNOWN_IG_IDS", {}).get(token_env, "")
    if known:
        os.environ["INSTAGRAM_USER_ID"] = known
    if token_env != "INSTAGRAM_ACCESS_TOKEN":
        os.environ["IG_STRICT_ACCOUNT"] = "1"
    user, name = IG.resolve(token, None) if hasattr(IG, "resolve") else IG.account(token)
    return token, user, name


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--token-env", default="INSTAGRAM_ACCESS_TOKEN")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--reply", nargs=2, metavar=("COMMENT_ID", "TEXT"))
    args = ap.parse_args()
    token, user, name = setup(args.token_env)
    if args.reply:
        cid, text = args.reply
        out = IG.call("POST", f"{cid}/replies", token, {"message": text[:300]})
        print(f"replied: {out.get('id')}")
        return
    media = IG.call("GET", f"{user}/media", token, {"fields": "id,caption", "limit": 10}).get("data", [])
    found = 0
    for m in media:
        comments = IG.call("GET", f"{m['id']}/comments", token, {"fields": "id,text,username,replies{username}", "limit": 50}).get("data", [])
        for c in comments:
            if c.get("username") == name:
                continue
            replies = (c.get("replies") or {}).get("data", [])
            if any(r.get("username") == name for r in replies):
                continue
            found += 1
            post = (m.get("caption") or "").split("\n", 1)[0][:60]
            print(f"{c['id']} | post: {post} | @{c.get('username')}: {c.get('text', '')[:200]}")
    print(f"{found} comments waiting for a reply")


if __name__ == "__main__":
    main()
