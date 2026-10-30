#!/usr/bin/env python3
"""Publish the day's carousel on SocialPerks' Instagram, as one post with all its slides.

    python3 ig_publish.py --date 2026-10-31 --base-url https://raw.githubusercontent.com/<owner>/<repo>/daily-posts/2026-10-31/
    python3 ig_publish.py --date 2026-10-31 --base-url ... --dry-run   # checks the token and the images, posts nothing

The owner asked for it on 30 October: from the Claude app a page can hand the
phone one file at a time, so a carousel arrived as nine separate shares.
Instagram's own API takes the slides together and publishes one post.

It uses the Instagram API with Instagram Login (graph.instagram.com) and reads,
from the environment:
- INSTAGRAM_ACCESS_TOKEN: a token for the SocialPerks professional account with
  instagram_business_basic and instagram_business_content_publish (the Meta
  app's dashboard generates it; it lasts 60 days);
- INSTAGRAM_USER_ID (optional): the account's id; asked from the API if absent.

Instagram fetches every image from a public URL, so --base-url must be where
the slides are public, as slide-01.jpg, slide-02.jpg, ... The token never goes
in a URL: it is sent in the request body or an Authorization header.

The caption is the one in carousel.json. Before posting, it looks at the
account's last posts and stops if one already has today's caption, so running
it twice never posts twice. It prints the post's link, and writes
published.json next to the slides.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
API = "https://graph.instagram.com/v21.0"
MAX_SLIDES = 10  # Instagram's limit for one carousel


class ApiError(RuntimeError):
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
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.loads(r.read().decode() or "{}")
    except urllib.error.HTTPError as error:
        try:
            body = json.loads(error.read().decode())
            message = body.get("error", {}).get("message") or str(body)
        except Exception:
            message = str(error)
        raise ApiError(f"{method} {path}: {message}") from None


def wait_ready(container: str, token: str, timeout: float = 120) -> None:
    """Instagram prepares each image before it can be published; wait for FINISHED."""
    end = time.time() + timeout
    while True:
        status = call("GET", container, token, {"fields": "status_code"}).get("status_code")
        if status in (None, "FINISHED", "PUBLISHED"):
            return
        if status in ("ERROR", "EXPIRED"):
            raise ApiError(f"container {container}: {status}")
        if time.time() > end:
            raise ApiError(f"container {container}: still {status} after {int(timeout)} s")
        time.sleep(3)


def check_public(url: str) -> None:
    req = urllib.request.Request(url, method="HEAD")
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            kind = r.headers.get("Content-Type", "")
    except Exception as error:
        raise ApiError(f"{url} is not reachable: {error}") from None
    if "image/jpeg" not in kind:
        raise ApiError(f"{url} is served as {kind or 'unknown'}, Instagram needs image/jpeg")


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--date", required=True)
    ap.add_argument("--out", default=os.path.join(HERE, "out"))
    ap.add_argument("--base-url", required=True, help="public folder URL that holds slide-01.jpg ...")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    token = os.environ.get("INSTAGRAM_ACCESS_TOKEN", "").strip()
    if not token:
        sys.exit("INSTAGRAM_ACCESS_TOKEN is not set: nothing published")
    folder = os.path.join(args.out, args.date, "carousel")
    meta = json.load(open(os.path.join(folder, "carousel.json"), encoding="utf-8"))
    slides = meta["slides"][:MAX_SLIDES]
    base = args.base_url if args.base_url.endswith("/") else args.base_url + "/"
    urls = [base + name for name in slides]

    try:
        me = call("GET", "me", token, {"fields": "user_id,username"})
        user = os.environ.get("INSTAGRAM_USER_ID", "").strip() or str(me.get("user_id") or me.get("id"))
        print(f"account: @{me.get('username', '?')}")
        for url in urls:
            check_public(url)
        print(f"{len(urls)} slides are public")

        # Never twice: today's caption already on one of the last posts means it is done.
        first_line = meta["caption"].split("\n", 1)[0].strip()
        recent = call("GET", f"{user}/media", token, {"fields": "caption,permalink,timestamp", "limit": 10}).get("data", [])
        done = next((m for m in recent if (m.get("caption") or "").strip().startswith(first_line)), None)
        if done:
            print(f"already published: {done.get('permalink')}")
            return
        if args.dry_run:
            print("dry run: token and images are fine, nothing published")
            return

        children = []
        for url in urls:
            item = call("POST", f"{user}/media", token, {"image_url": url, "is_carousel_item": "true"})
            children.append(item["id"])
        for child in children:
            wait_ready(child, token)
        post = call("POST", f"{user}/media", token, {"media_type": "CAROUSEL", "children": ",".join(children), "caption": meta["caption"]})
        wait_ready(post["id"], token)
        media = call("POST", f"{user}/media_publish", token, {"creation_id": post["id"]})
        link = call("GET", media["id"], token, {"fields": "permalink"}).get("permalink")
    except ApiError as error:
        sys.exit(f"Instagram: {error}")

    with open(os.path.join(folder, "published.json"), "w", encoding="utf-8") as fh:
        json.dump({"media_id": media["id"], "permalink": link}, fh, indent=1)
    print(f"published: {link}")


if __name__ == "__main__":
    main()
