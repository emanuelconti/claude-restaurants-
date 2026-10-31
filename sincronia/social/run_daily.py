#!/usr/bin/env python3
"""Render and publish a Sincronia carousel, retrying on its own.

    python3 run_daily.py --slot 1          # today's first carousel
    python3 run_daily.py --catch-up        # every slot of today that is not out yet

A slot counts as done when published.json sits next to its slides. The
catch-up run is the evening safety net: it walks today's slots, renders what
is missing and publishes whatever is still unpublished, so a failed afternoon
never costs the day a post.

Publishing is tried several times with growing gaps, because the temporary
image hosts and Instagram both fail transiently. Exit 2 means the account id
is still missing: the slides stay rendered and a later run publishes them
unchanged, so nothing is lost and nothing is posted twice.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import subprocess
import sys
import time
from zoneinfo import ZoneInfo

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import carousels as C  # noqa: E402

TZ = ZoneInfo("Europe/Madrid")
TOKEN_ENV = "INSTAGRAM_TOKEN_SINCRONIA"
DAILY_CAP = C.SLOTS  # posts a day, counted on the account itself


def posted_today(date: str, ig_id: str | None) -> int:
    """How many posts the account already has for this date, whoever made them.

    The dedupe inside ig_publish.py only catches the same carousel twice. This
    counts the day on the account, so a second scheduler running elsewhere
    cannot quietly double the feed: on 31 October two of them put out six."""
    cmd = [sys.executable, "ig_publish.py", "--recent", "25", "--token-env", TOKEN_ENV]
    if ig_id:
        cmd += ["--ig-id", ig_id]
    code, log = run(cmd, timeout=180)
    if code != 0:
        return 0  # cannot tell: let the normal dedupe decide
    return sum(1 for line in log.splitlines() if line.strip().startswith(date))


def run(cmd: list, timeout: int = 900) -> tuple:
    p = subprocess.run(cmd, cwd=HERE, capture_output=True, text=True, timeout=timeout)
    return p.returncode, (p.stdout or "") + (p.stderr or "")


def folder_for(date: str, slot: int, out: str) -> str:
    return os.path.join(out, date, f"carousel-{slot}")


def is_published(date: str, slot: int, out: str) -> bool:
    return os.path.exists(os.path.join(folder_for(date, slot, out), "published.json"))


def ensure_rendered(date: str, slot: int, out: str) -> bool:
    if os.path.exists(os.path.join(folder_for(date, slot, out), "carousel.json")):
        return True
    code, log = run([sys.executable, "carousel.py", "--date", date, "--slot", str(slot), "--out", out])
    print(log.strip())
    return code == 0


def try_publish(date: str, slot: int, out: str, ig_id: str | None, attempts: int = 3) -> int:
    """0 published or already out, 2 no account id yet, 1 everything else."""
    cmd = [sys.executable, "ig_publish.py", "--date", date, "--slot", str(slot),
           "--out", out, "--upload", "--token-env", TOKEN_ENV]
    if ig_id:
        cmd += ["--ig-id", ig_id]
    for attempt in range(1, attempts + 1):
        code, log = run(cmd)
        print(log.strip())
        if code == 0:
            return 0
        if code == 2:  # no id: a later run will publish these same slides
            return 2
        if attempt < attempts:
            wait = 60 * attempt
            print(f"attempt {attempt} failed; retrying in {wait}s", file=sys.stderr)
            time.sleep(wait)
    return 1


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--date", default=None)
    ap.add_argument("--slot", type=int, default=None, choices=range(1, C.SLOTS + 1))
    ap.add_argument("--catch-up", action="store_true", help="every slot of the day that is not out yet")
    ap.add_argument("--out", default=os.path.join(HERE, "out"))
    ap.add_argument("--ig-id", default=os.environ.get("SINCRONIA_IG_ID", "").strip() or None)
    ap.add_argument("--cap", type=int, default=DAILY_CAP,
                    help="most posts the account should have in a day, counted on the account")
    args = ap.parse_args()

    date = args.date or dt.datetime.now(TZ).date().isoformat()
    slots = list(range(1, C.SLOTS + 1)) if args.catch_up else [args.slot or 1]

    already = posted_today(date, args.ig_id)
    room = max(0, args.cap - already)
    print(f"{date}: {already} already on the account today, room for {room} more")

    pending, failed, posted = [], [], []
    for slot in slots:
        if len(posted) >= room:
            print(f"slot {slot}: the day is full ({args.cap} posts); leaving it")
            continue
        if is_published(date, slot, args.out):
            print(f"slot {slot}: already published")
            continue
        if not ensure_rendered(date, slot, args.out):
            failed.append(slot)
            continue
        code = try_publish(date, slot, args.out, args.ig_id)
        (posted if code == 0 else pending if code == 2 else failed).append(slot)

    print(f"\n{date}: posted {posted or '-'} | waiting for the account id {pending or '-'} | failed {failed or '-'}")
    if failed:
        sys.exit(1)
    if pending:
        sys.exit(2)


if __name__ == "__main__":
    main()
