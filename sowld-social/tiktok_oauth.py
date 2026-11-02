#!/usr/bin/env python3
"""Connect the Good Message Studio TikTok account once (Login Kit OAuth), for tiktok_publish.py.

    python3 tiktok_oauth.py --url                      # the page the owner opens and approves
    python3 tiktok_oauth.py --code '<address bar URL>' # exchanges the code, shows the refresh token ONCE

Reads TIKTOK_CLIENT_KEY_GMS and TIKTOK_CLIENT_SECRET_GMS from the environment (sandbox keys while the
app is in review). The redirect https://goodmessagestudio.com/ must be listed in Login Kit.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

REDIRECT = "https://goodmessagestudio.com/"
SCOPES = os.environ.get("TIKTOK_SCOPES_GMS", "").strip() or "user.info.basic,video.publish"  # add video.list once the Display API product is on the app


def env(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        sys.exit(f"{name} is not set")
    return value


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--url", action="store_true")
    ap.add_argument("--code")
    args = ap.parse_args()
    if args.url:
        q = urllib.parse.urlencode({"client_key": env("TIKTOK_CLIENT_KEY_GMS"), "scope": SCOPES, "response_type": "code",
                                    "redirect_uri": REDIRECT, "state": "goodmessagestudio"})
        print("https://www.tiktok.com/v2/auth/authorize/?" + q)
        return
    if not args.code:
        ap.error("--url or --code")
    code = args.code.strip()
    if code.startswith("http"):
        params = urllib.parse.parse_qs(urllib.parse.urlsplit(code).query)
        if "code" not in params:
            sys.exit("no code in that address: approve again and copy the address bar right after")
        code = params["code"][0]
    form = {"client_key": env("TIKTOK_CLIENT_KEY_GMS"), "client_secret": env("TIKTOK_CLIENT_SECRET_GMS"),
            "code": code, "grant_type": "authorization_code", "redirect_uri": REDIRECT}
    req = urllib.request.Request("https://open.tiktokapis.com/v2/oauth/token/", data=urllib.parse.urlencode(form).encode(),
                                 method="POST", headers={"Content-Type": "application/x-www-form-urlencoded"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            out = json.loads(r.read().decode())
    except urllib.error.HTTPError as error:
        sys.exit(f"TikTok refused the exchange: HTTP {error.code} {error.read().decode()[:300]}")
    if "refresh_token" not in out:
        sys.exit(f"TikTok refused the exchange: {out.get('error')} {out.get('error_description')}")
    print(f"scopes: {out.get('scope')}; refresh token valid {int(out.get('refresh_expires_in', 0) / 86400)} days")
    print("Save this in the Default environment as TIKTOK_REFRESH_TOKEN_GMS (shown once, do not share it):")
    print(out["refresh_token"])


if __name__ == "__main__":
    main()
