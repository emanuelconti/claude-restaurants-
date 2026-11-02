#!/usr/bin/env python3
"""Offline tests for the extra channels: no network, no tokens, nothing can be published.

    python3 tests/test_channels.py

Every HTTP call goes through channel_guard.http, which is replaced by a fake that
records the calls, so each test can prove which endpoints a run would touch.
"""

from __future__ import annotations

import contextlib
import datetime as dt
import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)
import channel_guard as G  # noqa: E402
import pinterest_publish as P  # noqa: E402
import tiktok_publish as T  # noqa: E402
import youtube_publish as Y  # noqa: E402

NOW = dt.datetime.now(dt.timezone.utc)
CLEAN_ENV = {k: v for k, v in os.environ.items() if not k.startswith(("PINTEREST_", "YOUTUBE_", "TIKTOK_", "GMS_"))}


def fixtures(root: str) -> None:
    from PIL import Image
    car = os.path.join(root, "2026-11-02", "carousel-1")
    os.makedirs(car)
    slides = []
    for i in range(1, 9):
        name = f"slide-{i:02d}.jpg"
        Image.new("RGB", (108, 135), (200, 200, 200)).save(os.path.join(car, name))
        slides.append(name)
    json.dump({"title": "5 gifts for her", "slides": slides,
               "caption": "5 gifts for her\n\nHook.\n\nBody text.\n\nWear the message: goodmessagestudio.com (link in bio).\n\n#goodmessagestudio #singapore"},
              open(os.path.join(car, "carousel.json"), "w"))
    reel = os.path.join(root, "2026-11-02", "reel")
    os.makedirs(reel)
    subprocess.run(["ffmpeg", "-loglevel", "error", "-f", "lavfi", "-i", "color=c=white:s=108x192:d=1", "-pix_fmt", "yuv420p",
                    os.path.join(reel, "reel.mp4")], check=True)
    json.dump({"title": "Send this to her", "video": "reel.mp4",
               "caption": "Send this to her\n\nBody.\n\nWear the message: goodmessagestudio.com (link in bio).\n\n#goodmessagestudio"},
              open(os.path.join(reel, "reel.json"), "w"))


class FakeHTTP:
    def __init__(self, stamps_minutes_ago=(300,)):
        self.calls = []
        self.ago = stamps_minutes_ago

    def __call__(self, method, url, token=None, form=None, body=None, data=None, headers=None, timeout=120):
        self.calls.append((method, url))
        iso = [(NOW - dt.timedelta(minutes=m)).isoformat() for m in self.ago]
        if "pinterest" in url:
            if url.endswith("/user_account"):
                return {"username": "goodmessagestudio"}
            if "/boards" in url:
                return {"items": [{"id": "123", "name": "Good Message Studio"}]}
            if "/pins?" in url:
                return {"items": [{"created_at": s} for s in iso]}
            return {"id": "999"}
        if "oauth2.googleapis.com" in url or "oauth/token" in url:
            return {"access_token": "fake"}
        if "youtube/v3/channels" in url:
            return {"items": [{"snippet": {"title": "Good Message Studio"}, "contentDetails": {"relatedPlaylists": {"uploads": "UU1"}}}]}
        if "playlistItems" in url:
            return {"items": [{"contentDetails": {"videoPublishedAt": s}} for s in iso]}
        if "creator_info" in url:
            return {"data": {"creator_username": "goodmessagestudio", "privacy_level_options": ["SELF_ONLY"]}, "error": {"code": "ok"}}
        if "video/list" in url:
            return {"data": {"videos": [{"create_time": int((NOW - dt.timedelta(minutes=m)).timestamp())} for m in self.ago]}, "error": {"code": "ok"}}
        return {"id": "x", "_headers": {"Location": "https://upload.example/x"}, "data": {"publish_id": "p", "upload_url": "https://u", "status": "PUBLISH_COMPLETE"}, "error": {"code": "ok"}}

    def writes(self):
        reads = ("/user_account", "/boards", "/pins?", "oauth", "/channels", "playlistItems", "creator_info", "video/list")
        return [c for c in self.calls if c[0] in ("POST", "PUT") and not any(r in c[1] for r in reads)]


def run(module, args, env, fake):
    out = io.StringIO()
    with mock.patch.dict(os.environ, env, clear=True), mock.patch.object(G, "http", fake), \
         mock.patch.object(G, "check_cross_channel", lambda gap=20: None), \
         mock.patch.object(G, "public_url", lambda p: "https://public.example/" + os.path.basename(p)), \
         mock.patch.object(sys, "argv", ["x"] + args), contextlib.redirect_stdout(out):
        try:
            module.main()
            code = 0
        except SystemExit as e:
            code = e.code
    return out.getvalue(), code


class Channels(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.mkdtemp()
        fixtures(cls.tmp)
        cls.pin_env = dict(CLEAN_ENV, PINTEREST_TOKEN_GMS="t", PINTEREST_BOARD_GMS="Good Message Studio")
        cls.yt_env = dict(CLEAN_ENV, YOUTUBE_CLIENT_ID_GMS="a", YOUTUBE_CLIENT_SECRET_GMS="b", YOUTUBE_REFRESH_TOKEN_GMS="c")
        cls.tt_env = dict(CLEAN_ENV, TIKTOK_CLIENT_KEY_GMS="a", TIKTOK_CLIENT_SECRET_GMS="b", TIKTOK_REFRESH_TOKEN_GMS="c")

    def args(self, *extra, reel=False):
        base = ["--date", "2026-11-02", "--out", self.tmp] + ([] if reel else ["--slot", "1"])
        return base + list(extra)

    def test_missing_variables_touch_nothing(self):
        for module, reel in ((P, False), (Y, True), (T, True)):
            fake = FakeHTTP()
            out, code = run(module, self.args(reel=reel), CLEAN_ENV, fake)
            self.assertIn("missing", out)
            self.assertEqual(fake.calls, [], module.__name__)

    def test_dry_run_only_reads(self):
        for module, env, reel in ((P, self.pin_env, False), (Y, self.yt_env, True), (T, self.tt_env, True)):
            fake = FakeHTTP()
            out, code = run(module, self.args(reel=reel), env, fake)
            self.assertIn("dry run", out, module.__name__)
            self.assertEqual(fake.writes(), [], module.__name__)

    def test_publish_needs_the_enable_flag(self):
        for module, env, reel, word in ((P, self.pin_env, False, "Pinterest is OFF"), (Y, self.yt_env, True, "YouTube is OFF"), (T, self.tt_env, True, "TikTok is OFF")):
            fake = FakeHTTP()
            out, code = run(module, self.args("--publish", reel=reel), env, fake)
            self.assertIn(word, out)
            self.assertEqual(fake.writes(), [], module.__name__)

    def test_too_soon_stops_before_any_write(self):
        for module, env, reel, flag in ((P, self.pin_env, False, "GMS_PINTEREST_ENABLED"), (Y, self.yt_env, True, "GMS_YOUTUBE_ENABLED"), (T, self.tt_env, True, "GMS_TIKTOK_ENABLED")):
            fake = FakeHTTP(stamps_minutes_ago=(30,))
            out, code = run(module, self.args("--publish", reel=reel), dict(env, **{flag: "1"}), fake)
            self.assertIn("too soon", str(code))
            self.assertEqual(fake.writes(), [], module.__name__)

    def test_daily_cap_stops(self):
        fake = FakeHTTP(stamps_minutes_ago=(61, 120, 180, 240, 300, 360))
        stamps = [NOW - dt.timedelta(minutes=61 + m) for m in range(G.DAILY_CAP)]  # exactly the cap, all older than the gap
        with self.assertRaises(G.Stop) as ctx:
            G.check_limits(stamps, "Test")
        self.assertIn("daily cap", str(ctx.exception))

    def test_pushback_words_stop_without_retry(self):
        for word in G.STOP_WORDS:
            with self.assertRaises(G.Stop):
                G.stop_if_pushback(f"Error: account {word} for now")

    def test_enabled_publish_makes_one_post(self):
        fake = FakeHTTP(stamps_minutes_ago=(300,))
        out, code = run(P, self.args("--publish"), dict(self.pin_env, GMS_PINTEREST_ENABLED="1"), fake)
        posts = [c for c in fake.writes() if c[1].endswith("/pins")]
        self.assertEqual(len(posts), 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
