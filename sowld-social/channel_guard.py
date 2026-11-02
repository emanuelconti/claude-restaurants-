#!/usr/bin/env python3
"""Safety rules shared by the extra Good Message Studio channels (Pinterest, YouTube Shorts, TikTok).

The owner's rules (31 October and 1 November 2026), the same as ig_publish.py,
fb_publish.py and threads_publish.py:
- at most one post per account per run (each script publishes one item and exits);
- at most DAILY_CAP posts a day per channel, and at least 60 minutes since the
  channel's own last post;
- at least 20 minutes since the last Good Message Studio post on Instagram or
  Facebook, so different channels never go out in a burst;
- any answer containing blocked, limit, spam, restricted, temporarily or
  "too soon" stops the run for good: no retry;
- every new channel stays OFF until its GMS_<CHANNEL>_ENABLED variable is "1",
  set by the owner once the account, OAuth/audit and rights are confirmed;
- tokens are only read from the environment and never printed, logged or put in a URL.
"""

from __future__ import annotations

import datetime as dt
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from zoneinfo import ZoneInfo

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

STOP_WORDS = ("blocked", "limit", "spam", "restricted", "temporarily", "too soon")
DAILY_CAP = 10  # (the owner, 2 November 2026: 10 a day, never in a burst: 60 minutes apart)
MIN_GAP = 60  # minutes since the same channel's last post
CROSS_GAP = 20  # minutes since the last post on any other Good Message Studio channel
MADRID = ZoneInfo("Europe/Madrid")


class Stop(RuntimeError):
    """A rule or the platform said stop: the run ends here and nothing is retried."""


def missing(*names: str) -> list:
    """The names (never the values) of the variables that are not set."""
    return [n for n in names if not os.environ.get(n, "").strip()]


def enabled(channel: str) -> bool:
    return os.environ.get(f"GMS_{channel.upper()}_ENABLED", "").strip() == "1"


def stop_if_pushback(message: str) -> None:
    if any(word in message.lower() for word in STOP_WORDS):
        raise Stop(f"stopped, nothing retried: {message}")


def http(method: str, url: str, token: str | None = None, form: dict | None = None, body: dict | None = None,
         data: bytes | None = None, headers: dict | None = None, timeout: int = 120) -> dict:
    """One HTTP call with the token in a header. Any pushback word in an error stops the run."""
    hdrs = dict(headers or {})
    if token:
        hdrs["Authorization"] = f"Bearer {token}"
    if form is not None:
        data = urllib.parse.urlencode(form).encode()
        hdrs.setdefault("Content-Type", "application/x-www-form-urlencoded")
    elif body is not None:
        data = json.dumps(body).encode()
        hdrs.setdefault("Content-Type", "application/json; charset=UTF-8")
    req = urllib.request.Request(url, data=data, method=method, headers=hdrs)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            raw = r.read().decode() or "{}"
            out = json.loads(raw) if raw.strip().startswith(("{", "[")) else {"raw": raw}
            if isinstance(out, dict):
                out.setdefault("_headers", dict(r.headers))
            return out
    except urllib.error.HTTPError as error:
        try:
            message = error.read().decode()[:400]
        except Exception:
            message = str(error)
        stop_if_pushback(message)
        raise RuntimeError(f"{method} {urllib.parse.urlsplit(url).path}: HTTP {error.code} {message}") from None


def check_limits(stamps: list, channel: str, cap: int = DAILY_CAP, gap: int = MIN_GAP) -> None:
    """stamps: aware datetimes of the channel's recent posts. Raises Stop when a limit says no."""
    now = dt.datetime.now(dt.timezone.utc)
    today = sum(1 for s in stamps if s.astimezone(MADRID).date() == now.astimezone(MADRID).date())
    if today >= cap:
        raise Stop(f"daily cap: {channel} already has {today} posts today (cap {cap}), nothing published")
    if stamps:
        minutes = int((now - max(stamps)).total_seconds() // 60)
        if minutes < gap:
            raise Stop(f"too soon: the last {channel} post went out {minutes} min ago (minimum {gap}), nothing published")


def last_gms_post_elsewhere() -> dt.datetime | None:
    """The newest Good Message Studio post on Instagram and Facebook, read-only, None if unknown."""
    newest = []
    try:
        import ig_publish as IG
        token = os.environ.get("INSTAGRAM_TOKEN_SOWLD", "").strip()
        if token:
            if token.startswith("EAA"):
                IG.API = "https://graph.facebook.com/v21.0"
            known = os.environ.get("INSTAGRAM_USER_ID_SOWLD", "").strip() or getattr(IG, "KNOWN_IG_IDS", {}).get("INSTAGRAM_TOKEN_SOWLD", "")
            if known:
                os.environ["INSTAGRAM_USER_ID"] = known
            user, _ = IG.resolve(token, None)
            for m in IG.call("GET", f"{user}/media", token, {"fields": "timestamp", "limit": 3}).get("data", []):
                newest.append(dt.datetime.strptime(m["timestamp"], "%Y-%m-%dT%H:%M:%S%z"))
    except Exception as error:  # read-only probe: unknown is reported, never guessed
        print(f"note: could not read Instagram's last post ({type(error).__name__})", file=sys.stderr)
    try:
        import fb_publish as FB
        token, page = os.environ.get("FB_PAGE_TOKEN_GMS", "").strip(), os.environ.get("FB_PAGE_ID_GMS", "").strip()
        if token and page:
            for p in FB.recent(page, FB.page_token(page, token))[:3]:
                newest.append(dt.datetime.strptime(p["created_time"], "%Y-%m-%dT%H:%M:%S%z"))
    except Exception as error:
        print(f"note: could not read Facebook's last post ({type(error).__name__})", file=sys.stderr)
    return max(newest) if newest else None


def check_cross_channel(gap: int = CROSS_GAP) -> None:
    last = last_gms_post_elsewhere()
    if last is None:
        return
    minutes = int((dt.datetime.now(dt.timezone.utc) - last).total_seconds() // 60)
    if minutes < gap:
        raise Stop(f"too soon: Good Message Studio posted on another channel {minutes} min ago (minimum {gap}), nothing published")


def public_url(path: str) -> str:
    """Put one file on the temporary public hosts ig_publish.py already uses."""
    import ig_publish as IG
    problems = []
    for name, host in IG.HOSTS:
        try:
            return IG.upload_temporary(path, host)
        except Exception as error:
            problems.append(f"{name}: {error}")
    raise RuntimeError("could not make the file public: " + "; ".join(problems))
