#!/usr/bin/env python3
"""Publish the day's carousel on SocialPerks' Instagram, as one post with all its slides.

    python3 ig_publish.py --date 2026-10-31 --slot 1 --upload       # slides to a temporary public host, then one post
    python3 ig_publish.py --date 2026-10-31 --base-url ... --dry-run   # checks the token and the images, posts nothing
    python3 ig_publish.py --check-token                                # only checks the token reaches the account

The owner asked for it on 30 October: from the Claude app a page can hand the
phone one file at a time, so a carousel arrived as nine separate shares.
Instagram's own API takes the slides together and publishes one post.

It reads, from the environment:
- INSTAGRAM_ACCESS_TOKEN: a token for the SocialPerks professional account, as
  the Meta app's dashboard generates it (it lasts 60 days). Either kind works:
  an Instagram Login token (it starts with IG, permissions
  instagram_business_basic and instagram_business_content_publish) goes to
  graph.instagram.com; a Facebook Login token (it starts with EAA, permissions
  instagram_basic, instagram_content_publish, pages_show_list) goes to
  graph.facebook.com, and the account is the one linked to the token's Page;
- INSTAGRAM_USER_ID (optional): the account's id; @socialperks.es by default with a
  Facebook Login or system-user token, asked from the API with an Instagram one.

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
API = "https://graph.instagram.com/v21.0"  # graph.facebook.com for a Facebook Login token (main)
MAX_SLIDES = 10  # Instagram's limit for one carousel
# The accounts this script publishes to, as the Meta app's dashboard shows
# them. An Instagram account id is not a secret (it is what the public
# business-discovery lookup returns); the token is, and that stays in the
# environment. Keeping the ids here means a scheduled run needs no setup
# beyond the token, and a system-user token, which cannot list its own
# Pages and so cannot name its account, still resolves.
KNOWN_IG_IDS = {
    "INSTAGRAM_ACCESS_TOKEN": "17841450639747283",  # @socialperks.es
    "INSTAGRAM_TOKEN_SOWLD": "17841470732004019",   # @sowld.ai
    "INSTAGRAM_TOKEN_SINCRONIA": "17841404632479565",  # @sincronia.live
}
SOCIALPERKS_IG_ID = KNOWN_IG_IDS["INSTAGRAM_ACCESS_TOKEN"]


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


def account(token: str) -> tuple:
    """The Instagram account's id and username, for either kind of token.

    Never guesses. The SocialPerks id is only ever a default for SocialPerks'
    own token: any other token has to name its account or have exactly one
    reachable, or this raises rather than posting somewhere unintended.
    """
    given = os.environ.get("INSTAGRAM_USER_ID", "").strip()
    if API.startswith("https://graph.instagram.com"):
        me = call("GET", "me", token, {"fields": "user_id,username"})
        return given or str(me.get("user_id") or me.get("id")), me.get("username", "?")

    if given:
        return given, call("GET", given, token, {"fields": "username"}).get("username", "?")

    tried = []
    # A regular Facebook Login token reaches Instagram through the Pages it
    # manages. This is the normal case and has to be tried before giving up.
    try:
        pages = call("GET", "me/accounts", token,
                     {"fields": "name,instagram_business_account{id,username}", "limit": "100"}).get("data", [])
        linked = [p["instagram_business_account"] for p in pages if p.get("instagram_business_account")]
        if len(linked) == 1:
            return linked[0]["id"], linked[0].get("username", "?")
        if len(linked) > 1:
            names = ", ".join(f"@{a.get('username', '?')} ({a['id']})" for a in linked)
            raise ApiError(f"the token reaches several Instagram accounts, so --ig-id is needed: {names}")
        tried.append(f"me/accounts: {len(pages)} Pages, none with an Instagram account linked")
    except ApiError as error:
        if "several Instagram accounts" in str(error):
            raise
        tried.append(f"me/accounts: {error}")

    # A system-user token has no Pages of its own and reaches the account
    # directly. Only SocialPerks' own token may assume that account.
    if not os.environ.get("IG_STRICT_ACCOUNT"):
        try:
            return SOCIALPERKS_IG_ID, call("GET", SOCIALPERKS_IG_ID, token, {"fields": "username"}).get("username", "?")
        except ApiError as error:
            tried.append(f"direct lookup: {error}")

    raise ApiError(
        "could not work out which Instagram account this token reaches. "
        "Set the account id in the environment next to the token (for "
        "INSTAGRAM_TOKEN_SOWLD that is INSTAGRAM_USER_ID_SOWLD), pass --ig-id, "
        "or give the token the pages_show_list permission. Tried: " + "; ".join(tried))


def _post_file(url: str, field: str, path: str, extra: dict) -> str:
    boundary = "----socialperks" + os.urandom(8).hex()
    body = b""
    for name, value in extra.items():
        body += f"--{boundary}\r\nContent-Disposition: form-data; name=\"{name}\"\r\n\r\n{value}\r\n".encode()
    body += (f"--{boundary}\r\nContent-Disposition: form-data; name=\"{field}\"; filename=\"{os.path.basename(path)}\"\r\n"
             "Content-Type: image/jpeg\r\n\r\n").encode() + open(path, "rb").read() + f"\r\n--{boundary}--\r\n".encode()
    req = urllib.request.Request(url, data=body, method="POST",
                                 headers={"Content-Type": f"multipart/form-data; boundary={boundary}", "User-Agent": "socialperks-daily/1.0"})
    with urllib.request.urlopen(req, timeout=90) as r:
        return r.read().decode().strip()


def _litterbox(path: str) -> str:
    """litterbox.catbox.moe keeps a file for an hour."""
    return _post_file("https://litterbox.catbox.moe/resources/internals/api.php", "fileToUpload", path, {"reqtype": "fileupload", "time": "1h"})


def _uguu(path: str) -> str:
    """uguu.se keeps a file for a few hours."""
    return json.loads(_post_file("https://uguu.se/upload", "files[]", path, {}))["files"][0]["url"]


# Instagram takes images only from a public URL. A git push from a scheduled
# run was refused (30 October), so the slides go to a temporary host instead:
# they are about to be public on Instagram anyway, and vanish within hours.
# Two hosts, so one being down never stops a post (the owner: it must always go out).
HOSTS = [("litterbox", _litterbox), ("uguu", _uguu)]


def upload_temporary(path: str, host=_litterbox) -> str:
    """Put one slide at a public URL on a temporary host, trying three times."""
    last = ""
    for attempt in range(3):
        try:
            url = host(path)
            if url.startswith("https://"):
                return url
            last = url[:200]
        except Exception as error:
            last = str(error)
        time.sleep(5)
    raise ApiError(f"could not upload {os.path.basename(path)}: {last}")


def check_public(url: str) -> None:
    """A quick look that the slide is served as a JPEG; a flaky network here only warns, Instagram fetches it itself."""
    kind, error = "", None
    for attempt in range(3):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, method="HEAD"), timeout=30) as r:
                kind = r.headers.get("Content-Type", "")
            break
        except Exception as e:
            error = e
            time.sleep(3)
    else:
        print(f"warning: could not check {url} ({error}); Instagram will fetch it itself", file=sys.stderr)
        return
    if "image/jpeg" not in kind:
        raise ApiError(f"{url} is served as {kind or 'unknown'}, Instagram needs image/jpeg")


def publish(user: str, token: str, urls: list, caption: str) -> dict:
    """One carousel post from public image URLs, in order."""
    children = []
    for url in urls:
        item = call("POST", f"{user}/media", token, {"image_url": url, "is_carousel_item": "true"})
        children.append(item["id"])
    for child in children:
        wait_ready(child, token)
    post = call("POST", f"{user}/media", token, {"media_type": "CAROUSEL", "children": ",".join(children), "caption": caption})
    wait_ready(post["id"], token)
    return call("POST", f"{user}/media_publish", token, {"creation_id": post["id"]})


def resolve(token: str, expect: str | None) -> tuple:
    """The account this token reaches, refusing anything but the expected one.

    Two products publish from this same script. A token that quietly resolved
    to the wrong profile would put one brand's carousel on the other's feed,
    publicly, with no undo. So when a run names the account it means to post
    to, a mismatch stops everything rather than being reported afterwards.
    """
    user, username = account(token)
    if expect and username.lower().lstrip("@") != expect.lower().lstrip("@"):
        raise ApiError(
            f"this token reaches @{username} ({user}), not @{expect.lstrip('@')}. "
            "Nothing was published. Check which account the token was generated for.")
    return user, username


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--date", default=None)
    ap.add_argument("--out", default=os.path.join(HERE, "out"))
    ap.add_argument("--base-url", default=None, help="public folder URL that holds slide-01.jpg ...")
    ap.add_argument("--upload", action="store_true", help="put the slides on a temporary public host for an hour instead of --base-url")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--check-token", action="store_true", help="say which account the token reaches, and stop")
    ap.add_argument("--slot", type=int, default=1, help="which of the day's carousels (out/<date>/carousel-<slot>)")
    ap.add_argument("--recent", type=int, default=0, metavar="N", help="print the first line of the last N posts' captions, and stop")
    ap.add_argument("--token-env", default="INSTAGRAM_ACCESS_TOKEN", help="the environment variable holding the token (one per account, e.g. INSTAGRAM_TOKEN_SOWLD)")
    ap.add_argument("--ig-id", default=None, help="the Instagram account id, as the Meta app's dashboard shows it; needed only when the token reaches several accounts")
    ap.add_argument("--expect-username", default=None, metavar="NAME", help="refuse to do anything unless the token resolves to this account (no @)")
    args = ap.parse_args()
    if not (args.check_token or args.recent) and not (args.date and (args.base_url or args.upload)):
        ap.error("--date and --upload (or --base-url) are needed to publish")

    token = os.environ.get(args.token_env, "").strip()
    if not token:
        sys.exit(f"{args.token_env} is not set: nothing published")
    # The account id, in order: the flag, then the env var that belongs to this
    # token. A system-user token can publish without being able to say which
    # account it reaches (it has no Pages to list), so the id has to come from
    # somewhere; keeping it in an env var next to the token means a run needs
    # no arguments and starts working the moment the id is set.
    #   INSTAGRAM_TOKEN_SOWLD -> INSTAGRAM_USER_ID_SOWLD
    id_env = "INSTAGRAM_USER_ID"
    if args.token_env.startswith("INSTAGRAM_TOKEN_"):
        id_env = "INSTAGRAM_USER_ID_" + args.token_env[len("INSTAGRAM_TOKEN_"):]
    resolved_id = (args.ig_id or os.environ.get(id_env, "").strip()
                   or KNOWN_IG_IDS.get(args.token_env, ""))
    if resolved_id:
        os.environ["INSTAGRAM_USER_ID"] = resolved_id
    if args.token_env != "INSTAGRAM_ACCESS_TOKEN":
        # Another account's token must never silently resolve to SocialPerks.
        os.environ["IG_STRICT_ACCOUNT"] = "1"
    global API
    if token.startswith("EAA"):
        API = "https://graph.facebook.com/v21.0"
    if args.recent:
        try:
            user, _ = resolve(token, args.expect_username)
            posts = call("GET", f"{user}/media", token, {"fields": "caption,timestamp", "limit": min(args.recent, 100)}).get("data", [])
        except ApiError as error:
            sys.exit(f"Instagram: {error}")
        for post in posts:
            print(f"{post.get('timestamp', '')}  {(post.get('caption') or '').split(chr(10), 1)[0].strip()}")
        return
    if args.check_token:
        try:
            user, username = resolve(token, args.expect_username)
            can = call("GET", f"{user}/media", token, {"fields": "id", "limit": 1})
        except ApiError as error:
            sys.exit(f"Instagram: {error}")
        print(f"token ok: @{username} ({user}), {len(can.get('data', []))} recent post read, publishing not tried")
        return
    folder = os.path.join(args.out, args.date, f"carousel-{args.slot}")
    meta = json.load(open(os.path.join(folder, "carousel.json"), encoding="utf-8"))
    slides = meta["slides"][:MAX_SLIDES]
    if args.base_url:
        base = args.base_url if args.base_url.endswith("/") else args.base_url + "/"
        urls = [base + name for name in slides]

    try:
        user, username = resolve(token, args.expect_username)
        print(f"account: @{username}")

        # Never twice: today's caption already on one of the last posts means it is done.
        first_line = meta["caption"].split("\n", 1)[0].strip()
        recent = call("GET", f"{user}/media", token, {"fields": "caption,permalink,timestamp", "limit": 10}).get("data", [])
        done = next((m for m in recent if (m.get("caption") or "").strip().startswith(first_line)), None)
        if done:
            print(f"already published: {done.get('permalink')}")
            return

        # Each way of making the slides public in turn, until one gets the post out.
        ways = [("base-url", None)] if args.base_url else HOSTS
        media, problems = None, []
        for name, host in ways:
            try:
                if host:
                    urls = [upload_temporary(os.path.join(folder, slide), host) for slide in slides]
                for url in urls:
                    check_public(url)
                print(f"{len(urls)} slides are public ({name})")
                if args.dry_run:
                    print("dry run: token and images are fine, nothing published")
                    return
                media = publish(user, token, urls, meta["caption"])
                break
            except ApiError as error:
                problems.append(f"{name}: {error}")
                print(f"{name} did not work ({error}); trying the next way", file=sys.stderr)
        if media is None:
            raise ApiError("; ".join(problems))
        link = call("GET", media["id"], token, {"fields": "permalink"}).get("permalink")
    except ApiError as error:
        sys.exit(f"Instagram: {error}")

    with open(os.path.join(folder, "published.json"), "w", encoding="utf-8") as fh:
        json.dump({"media_id": media["id"], "permalink": link}, fh, indent=1)
    print(f"published: {link}")


if __name__ == "__main__":
    main()
