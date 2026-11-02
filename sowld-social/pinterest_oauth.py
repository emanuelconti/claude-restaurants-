#!/usr/bin/env python3
"""Connect Good Message Studio's Pinterest account once (OAuth), so the publisher can renew its own access token.

    python3 pinterest_oauth.py --url                      # the page the owner opens and approves ("Give access")
    python3 pinterest_oauth.py --code '<address bar URL>' # exchanges the code, shows the refresh token ONCE

Reads from the environment (never from a file, never printed):
- PINTEREST_APP_ID_GMS (default 1632981, the app "Good Message Studio Publisher");
- PINTEREST_APP_SECRET_GMS: the app secret.

After the exchange the owner saves, in the Default environment, PINTEREST_REFRESH_TOKEN_GMS
(valid about a year) next to PINTEREST_APP_ID_GMS and PINTEREST_APP_SECRET_GMS, plus
PINTEREST_BOARD_GMS. pinterest_publish.py then gets a fresh access token by itself on every run.
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

REDIRECT = "https://goodmessagestudio.com/"
SCOPES = "boards:read,boards:write,pins:read,pins:write,user_accounts:read"


def app_id() -> str:
    return os.environ.get("PINTEREST_APP_ID_GMS", "").strip() or "1632981"


def token_call(form: dict) -> dict:
    secret = os.environ.get("PINTEREST_APP_SECRET_GMS", "").strip()
    if not secret:
        sys.exit("PINTEREST_APP_SECRET_GMS is not set")
    basic = base64.b64encode(f"{app_id()}:{secret}".encode()).decode()
    req = urllib.request.Request("https://api.pinterest.com/v5/oauth/token", data=urllib.parse.urlencode(form).encode(),
                                 method="POST", headers={"Authorization": f"Basic {basic}",
                                                         "Content-Type": "application/x-www-form-urlencoded"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as error:
        sys.exit(f"Pinterest refused the exchange: HTTP {error.code} {error.read().decode()[:300]}")


def refresh(refresh_token: str) -> str:
    """A fresh access token from the long-lived refresh token (used by pinterest_publish.py)."""
    out = token_call({"grant_type": "refresh_token", "refresh_token": refresh_token})
    if not out.get("access_token"):
        raise RuntimeError("Pinterest returned no access token for the refresh token")
    return out["access_token"]


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--url", action="store_true")
    ap.add_argument("--code", help="the code, or the whole address-bar URL after 'Give access'")
    args = ap.parse_args()
    if args.url:
        q = urllib.parse.urlencode({"client_id": app_id(), "redirect_uri": REDIRECT, "response_type": "code",
                                    "scope": SCOPES, "state": "goodmessagestudio"})
        print("https://www.pinterest.com/oauth/?" + q)
        return
    if not args.code:
        ap.error("--url or --code")
    code = args.code.strip()
    if code.startswith("http"):
        params = urllib.parse.parse_qs(urllib.parse.urlsplit(code).query)
        if "code" not in params:
            sys.exit("no code in that address: approve the app again and copy the address bar right after")
        code = params["code"][0]
    out = token_call({"grant_type": "authorization_code", "code": code, "redirect_uri": REDIRECT})
    days = int(out.get("refresh_token_expires_in", 0) / 86400)
    print(f"scopes: {out.get('scope')}")
    print(f"access token valid for {int(out.get('expires_in', 0) / 86400)} days; refresh token for {days} days")
    print("Save this in the Default environment as PINTEREST_REFRESH_TOKEN_GMS (shown once, do not share it):")
    print(out.get("refresh_token", "(none returned)"))


if __name__ == "__main__":
    main()
