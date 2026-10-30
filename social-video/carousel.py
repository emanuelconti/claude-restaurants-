#!/usr/bin/env python3
"""The day's SocialPerks carousel: a swipeable list post, rendered as JPEGs.

    python3 carousel.py                      # today (Madrid time)
    python3 carousel.py --date 2026-10-31    # any day; the same day always gives the same carousel

Writes, under --out/<date>/carousel/: slide-01.jpg ... (1080x1350, the 4:5
Instagram feed size), and carousel.json with the title, the slide files and
the caption to paste.

The look is the one the owner pointed at (30 October): a cover photo with a
big white title on a dark fade, then one numbered point per slide, the text
on white at the top and a photo fading in under it, the mark on every slide,
no faces. The last slide is SocialPerks. What it says comes from
carousels.py; the photos are the video's (episodes.py), fetched from
Unsplash and cached like the video's.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import sys
from zoneinfo import ZoneInfo

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import carousels as C  # noqa: E402
import daily as D  # noqa: E402
import episodes as E  # noqa: E402

W, H = 1080, 1350
MARGIN = 80
TEXT_W = W - 2 * MARGIN
INK = (21, 22, 27)
MUTED = (70, 70, 82)
WHITE = (255, 255, 255)
SIGNAL = D.SIGNAL
YELLOW = D.YELLOW

# The "venue" set, for the business topics (carousels.PHOTO_SETS has the others):
# photos without faces to camera, the video's, plus the product's reward
# photos of the same places (socialperks: src/assets/rewards/CREDITS.json).
EXTRA_PHOTOS = [
    "1544982560-63ad67a35c23",  # pizza slice and a drink
    "1758467700651-b0cdd3346cc7",  # brow tweezers
    "1732861612244-5704d12e9397",  # hair mask and serum
    "1767953829433-1e405b6889de",  # scalp massager
    "1745327883290-1e9c6447b938",  # massage room
]
# The barbershop's place photo shows the client's face: the carousel keeps to hands, plates and rooms.
WITH_FACES = {E.PLACE_PHOTO["barber"]}
PHOTOS = [p for p in dict.fromkeys(list(E.STORY_PHOTO.values()) + list(E.PLACE_PHOTO.values()) + EXTRA_PHOTOS) if p not in WITH_FACES]


def fade(w: int, h: int, colour, start: float, end: float, top_alpha: int, bottom_alpha: int) -> Image.Image:
    """A vertical band of one colour whose opacity goes from top_alpha to bottom_alpha between start and end (0..1)."""
    y = np.linspace(0, 1, h)[:, None]
    t = np.clip((y - start) / max(end - start, 1e-6), 0, 1)
    t = t * t * (3 - 2 * t)
    alpha = (top_alpha + (bottom_alpha - top_alpha) * t).repeat(w, axis=1).astype(np.uint8)
    out = Image.new("RGBA", (w, h), colour + (0,))
    out.putalpha(Image.fromarray(alpha, "L"))
    return out


def get_photo(pid: str, cache: str, w: int, h: int, focus=(0.5, 0.5)) -> Image.Image:
    img = D.photo(pid, cache)
    if img is None:
        a, b = SIGNAL, D.PINK
        g = np.linspace(0, 1, h)[:, None, None]
        arr = (np.array(a)[None, None, :] * (1 - g) + np.array(b)[None, None, :] * g).repeat(w, axis=1)
        return Image.fromarray(arr.astype(np.uint8), "RGB")
    return D.cover(img, w, h, focus)


def wrap(text: str, f, max_w: float) -> list:
    """Wrapped like text-wrap: balance, so no line ends with one word alone."""
    lines = D.wrap_lines(text, f, max_w)
    if len(lines) < 2:
        return lines
    lo, hi = max_w * 0.5, max_w
    while hi - lo > 4:
        mid = (lo + hi) / 2
        if len(D.wrap_lines(text, f, mid)) <= len(lines):
            hi = mid
        else:
            lo = mid
    return D.wrap_lines(text, f, hi)


def fit(text: str, size_max: int, size_min: int, max_w: int, max_lines: int, weight: int, path: str):
    """The biggest size, down to size_min, at which text wraps into max_lines."""
    size = size_max
    while True:
        f = D.font(size, weight, path)
        lines = wrap(text, f, max_w)
        if len(lines) <= max_lines or size <= size_min:
            return f, lines, size
        size -= 2


def centred(d: ImageDraw.ImageDraw, lines, f, y: float, colour, leading: float) -> float:
    for line in lines:
        d.text((W / 2, y), line, font=f, fill=colour, anchor="ma")
        y += f.size * leading
    return y


def brand_row(img: Image.Image, y: int, colour, label: bool, size: int = 64) -> None:
    """The mark between two rules, like a signature at the top of each slide."""
    d = ImageDraw.Draw(img)
    m = D.mark(size)
    if label:
        f = D.font(30, 800, D.DISPLAY)
        text = "SOCIALPERKS"
        tw = f.getlength(text)
        gap = 16
        total = size + gap + tw
        x = int((W - total) / 2)
        img.alpha_composite(m, (x, y))
        d.text((x + size + gap, y + size / 2), text, font=f, fill=colour, anchor="lm")
        left, right = x - 36, x + total + 36
    else:
        x = (W - size) // 2
        img.alpha_composite(m, (x, y))
        left, right = x - 36, x + size + 36
    rule = 190
    d.line((left - rule, y + size / 2, left, y + size / 2), fill=colour, width=4)
    d.line((right, y + size / 2, right + rule, y + size / 2), fill=colour, width=4)


def slide_cover(title: str, pid: str, cache: str) -> Image.Image:
    img = get_photo(pid, cache, W, H, (0.5, 0.42)).convert("RGBA")
    img.alpha_composite(fade(W, H, (0, 0, 0), 0.38, 0.78, 0, 238))
    f, lines, size = fit(title, 88, 58, TEXT_W, 4, 800, D.DISPLAY)
    leading = 1.08
    block = size * leading * len(lines)
    y_text = H - 92 - block
    brand_row(img, int(y_text - 40 - 46), (255, 255, 255), True, 46)
    centred(ImageDraw.Draw(img), lines, f, y_text, WHITE, leading)
    return img.convert("RGB")


def slide_point(n: int, heading: str, lines: list, punch: str, pid: str, cache: str) -> Image.Image:
    img = Image.new("RGBA", (W, H), WHITE + (255,))
    d = ImageDraw.Draw(img)
    brand_row(img, 70, INK, False, 72)

    # The text block, at a size that leaves at least 470px of photo.
    for scale in (1.0, 0.94, 0.88, 0.82, 0.76):
        hf, hlines, hs = fit(f"{n}. {heading.upper()}", int(72 * scale), int(50 * scale), TEXT_W, 2, 800, D.DISPLAY)
        bf = D.font(int(42 * scale), 400, D.BODY)
        pf = D.font(int(42 * scale), 700, D.BODY)
        body = [w for line in lines for w in wrap(line, bf, TEXT_W)]
        plines = wrap(punch, pf, TEXT_W)
        end = 200 + hs * 1.08 * len(hlines) + 30 + bf.size * 1.38 * len(body) + 22 + pf.size * 1.32 * len(plines)
        if end <= H - 470:
            break
    y = 200
    y = centred(d, hlines, hf, y, INK, 1.08) + 30
    y = centred(d, body, bf, y, MUTED, 1.38) + 22
    y = centred(d, plines, pf, y, SIGNAL, 1.32)

    top = int(y + 40)
    ph = get_photo(pid, cache, W, H - top, (0.5, 0.5)).convert("RGBA")
    img.alpha_composite(ph, (0, top))
    band = min(240, (H - top) // 2)
    img.alpha_composite(fade(W, band, WHITE, 0.0, 1.0, 255, 0), (0, top))
    return img.convert("RGB")


def slide_cta() -> Image.Image:
    img = Image.new("RGBA", (W, H), SIGNAL + (255,))
    d = ImageDraw.Draw(img)
    # The mark on a white tile: its own colours vanish on the brand blue.
    tile = D.rounded((190, 190), 48, WHITE + (255,))
    tile.alpha_composite(D.mark(140), (25, 25))
    img.alpha_composite(tile, ((W - 190) // 2, 230))
    f, lines, size = fit(C.CTA["title"], 84, 60, TEXT_W, 3, 800, D.DISPLAY)
    y = centred(d, lines, f, 470, WHITE, 1.06) + 36
    bf = D.font(40, 500, D.BODY)
    body = [w for line in C.CTA["lines"] for w in wrap(line, bf, TEXT_W)]
    y = centred(d, body, bf, y, (226, 223, 255), 1.4) + 56
    pill = D.pill(C.CTA["url"], 44, INK, YELLOW + (255,), weight=800)
    img.alpha_composite(pill, ((W - pill.width) // 2, int(y)))
    sf = D.font(30, 500, D.BODY)
    small = D.wrap_lines(C.CTA["small"], sf, TEXT_W)
    centred(d, small, sf, H - 110 - sf.size * 1.4 * (len(small) - 1), (206, 202, 250), 1.4)
    return img.convert("RGB")


def render(date: dt.date, out: str, cache: str, slot: int = 1, topic: dict | None = None) -> dict:
    car = C.carousel(date, PHOTOS, slot, topic)
    folder = os.path.join(out, car["date"], f"carousel-{slot}")
    os.makedirs(folder, exist_ok=True)
    slides = [slide_cover(car["title"], car["photos"][0], cache)]
    for i, (heading, lines, punch) in enumerate(car["points"], 1):
        slides.append(slide_point(car["numbers"][i - 1], heading, lines, punch, car["photos"][i], cache))
    if car["cta"]:
        slides.append(slide_cta())
    names = []
    for i, im in enumerate(slides, 1):
        name = f"slide-{i:02d}.jpg"
        im.save(os.path.join(folder, name), "JPEG", quality=90, optimize=True, progressive=True)
        names.append(name)
    meta = dict(date=car["date"], slot=slot, title=car["title"], slides=names, caption=car["caption"])
    with open(os.path.join(folder, "carousel.json"), "w", encoding="utf-8") as fh:
        json.dump(meta, fh, ensure_ascii=False, indent=1)
    return dict(meta, folder=folder)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--date", default=None, help="YYYY-MM-DD; default today in Madrid")
    ap.add_argument("--out", default=os.path.join(HERE, "out"))
    ap.add_argument("--cache", default=os.path.join(HERE, ".cache"))
    ap.add_argument("--slot", type=int, default=1, choices=range(1, C.SLOTS + 1), help="which of the day's carousels")
    ap.add_argument("--topic", default=None, help="a topic written for this run (JSON, as in carousels.py); else the written bank")
    args = ap.parse_args()
    date = dt.date.fromisoformat(args.date) if args.date else dt.datetime.now(ZoneInfo("Europe/Madrid")).date()
    topic = None
    if args.topic:
        topic = json.load(open(args.topic, encoding="utf-8"))
        errors = C.check_topic(topic)
        if errors:
            sys.exit("the topic needs fixing:\n- " + "\n- ".join(errors))
    meta = render(date, args.out, args.cache, args.slot, topic)
    print(f"{meta['date']}: {meta['title']}")
    for name in meta["slides"]:
        print(f"  {os.path.join(meta['folder'], name)}")
    print(f"  {os.path.join(meta['folder'], 'carousel.json')}")


if __name__ == "__main__":
    main()
