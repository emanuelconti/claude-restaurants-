#!/usr/bin/env python3
"""Keep the long-lived tokens alive, so publishing never stops (owner, 2 November 2026).

    python3 token_keepalive.py          # refresh what can be refreshed in place, report the rest

Instagram (Instagram Login tokens) and Threads long-lived tokens can be refreshed by their own API
before they expire: the refresh pushes the expiry 60 days forward. If the API hands back a different
token string, the old one keeps working until its old expiry, and this script says so in its FIRST
output line so the owner (or any Claude / Codex) saves the new value in the environment in time.
Nothing secret is ever printed: only names, expiry dates and what to do.
"""

from __future__ import annotations

import datetime as dt
import json
import os
import urllib.error
import urllib.parse
import urllib.request

REFRESH = [
    # (env name, refresh endpoint, grant type)
    ("INSTAGRAM_ACCESS_TOKEN", "https://graph.instagram.com/refresh_access_token", "ig_refresh_token"),
    ("INSTAGRAM_TOKEN_SOWLD", "https://graph.instagram.com/refresh_access_token", "ig_refresh_token"),
    ("INSTAGRAM_TOKEN_SINCRONIA", "https://graph.instagram.com/refresh_access_token", "ig_refresh_token"),
    ("THREADS_TOKEN_GMS", "https://graph.threads.net/refresh_access_token", "th_refresh_token"),
]


def get(url: str) -> dict:
    with urllib.request.urlopen(url, timeout=60) as r:
        return json.loads(r.read().decode())


def main():
    alerts, notes = [], []
    for name, endpoint, grant in REFRESH:
        token = os.environ.get(name, "").strip()
        if not token:
            continue
        if token.startswith("EAA"):
            notes.append(f"{name}: Facebook-login token, cannot be refreshed in place (check its expiry with the daily check)")
            continue
        try:
            out = get(endpoint + "?" + urllib.parse.urlencode({"grant_type": grant, "access_token": token}))
        except urllib.error.HTTPError as error:
            alerts.append(f"{name}: refresh refused (HTTP {error.code}); regenerate it and save it in the Default environment")
            continue
        days = int(out.get("expires_in", 0) / 86400)
        until = (dt.date.today() + dt.timedelta(days=days)).isoformat()
        if out.get("access_token") and out["access_token"] != token:
            alerts.append(f"{name}: the API issues a NEW value on refresh (the saved one keeps its old expiry): "
                          "save the new value in the Default environment before the old one expires")
        else:
            notes.append(f"{name}: refreshed, valid until about {until}")
    print(("⚠️ " + " | ".join(alerts)) if alerts else "✅ tokens ok")
    for n in notes:
        print(n)


if __name__ == "__main__":
    main()
