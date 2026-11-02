#!/usr/bin/env python3
"""Last-resort Instagram publisher: no AI, no credits, runs on GitHub Actions.

    python3 backup-publisher/publish.py            # check every account, publish only where needed
    python3 backup-publisher/publish.py --dry-run  # say what it would do

The Claude sessions publish every day. This only steps in when an account has
had no post for HOURS_SILENT hours, which means every Claude is out of credits
or down. It then posts ONE ready-made carousel from reserve/<account>/<NN>/,
the first one whose title is not already on the account, served straight from
this public repository (raw.githubusercontent.com), so nothing is uploaded.

Each account needs one repository secret (Settings, Secrets and variables,
Actions): its token, under the name in ACCOUNTS. An account without it is
skipped. Meta answers that mean "slow down" stop the run at once.
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

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.environ.get("GITHUB_REPOSITORY", "emanuelconti/claude-restaurants-")
RAW = f"https://raw.githubusercontent.com/{REPO}/main/backup-publisher/reserve"
HOURS_SILENT = 20
STOP_WORDS = ("blocked", "limit", "spam", "restricted", "temporarily")

# account folder: (token secret, Instagram account id; ids are public, tokens are not)
ACCOUNTS = {
    "socialperks": ("INSTAGRAM_ACCESS_TOKEN", "17841450639747283"),
    "gms": ("INSTAGRAM_TOKEN_SOWLD", "17841470732004019"),
    "sincronia": ("INSTAGRAM_TOKEN_SINCRONIA", "17841404632479565"),
}


class Stop(RuntimeError):
    pass


def call(method: str, path: str, token: str, params: dict | None = None) -> dict:
    api = "https://graph.facebook.com/v21.0" if token.startswith("EAA") else "https://graph.instagram.com/v21.0"
    url, data = f"{api}/{path}", None
    if method == "GET":
        url += "?" + urllib.parse.urlencode(params or {})
    else:
        data = urllib.parse.urlencode(params or {}).encode()
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
            raise Stop(f"Meta says: {message}") from None
        raise RuntimeError(f"{method} {path}: {message}") from None


def wait_ready(container: str, token: str) -> None:
    for _ in range(40):
        status = call("GET", container, token, {"fields": "status_code"}).get("status_code")
        if status in (None, "FINISHED", "PUBLISHED"):
            return
        if status in ("ERROR", "EXPIRED"):
            raise RuntimeError(f"container {container}: {status}")
        time.sleep(3)
    raise RuntimeError(f"container {container}: not ready")


def run(name: str, dry: bool) -> None:
    token_env, user = ACCOUNTS[name]
    token = os.environ.get(token_env, "").strip()
    if not token:
        print(f"{name}: secret {token_env} not set, skipped")
        return
    posts = call("GET", f"{user}/media", token, {"fields": "caption,timestamp", "limit": 50}).get("data", [])
    if posts:
        last = dt.datetime.strptime(posts[0]["timestamp"], "%Y-%m-%dT%H:%M:%S%z")
        hours = (dt.datetime.now(dt.timezone.utc) - last).total_seconds() / 3600
        if hours < HOURS_SILENT:
            print(f"{name}: last post {hours:.1f} h ago, the main publisher is alive")
            return
    titles = {(p.get("caption") or "").split("\n", 1)[0].strip() for p in posts}
    folder = os.path.join(HERE, "reserve", name)
    for item in sorted(os.listdir(folder)):
        meta = json.load(open(os.path.join(folder, item, "carousel.json"), encoding="utf-8"))
        title = meta["caption"].split("\n", 1)[0].strip()
        if title in titles:
            continue
        slides = sorted(f for f in os.listdir(os.path.join(folder, item)) if f.endswith(".jpg"))[:10]
        urls = [f"{RAW}/{name}/{item}/{s}" for s in slides]
        if dry:
            print(f"{name}: would publish «{title}» ({len(urls)} slides)")
            return
        children = [call("POST", f"{user}/media", token, {"image_url": u, "is_carousel_item": "true"})["id"] for u in urls]
        for c in children:
            wait_ready(c, token)
        box = call("POST", f"{user}/media", token, {"media_type": "CAROUSEL", "children": ",".join(children), "caption": meta["caption"]})["id"]
        wait_ready(box, token)
        media = call("POST", f"{user}/media_publish", token, {"creation_id": box})["id"]
        link = call("GET", media, token, {"fields": "permalink"}).get("permalink")
        print(f"{name}: published «{title}» {link}")
        return
    print(f"{name}: reserve used up, nothing left to publish")


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    for name in ACCOUNTS:
        try:
            run(name, args.dry_run)
        except Stop as error:
            sys.exit(f"{name}: {error}. Stopped, nothing retried.")
        except Exception as error:  # one account failing never stops the others
            print(f"{name}: failed: {error}")


if __name__ == "__main__":
    main()
