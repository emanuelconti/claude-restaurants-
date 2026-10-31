#!/usr/bin/env python3
"""The day's Sincronia carousel: a swipeable list post, rendered as JPEGs.

    python3 carousel.py                      # today (Madrid time)
    python3 carousel.py --slot 2             # the day's second carousel
    python3 carousel.py --topic topic.json   # a topic written for this run

Writes, under --out/<date>/carousel-<slot>/: slide-01.jpg ... (1080x1350, the
4:5 Instagram feed size) and carousel.json with the title, the slide files and
the caption.

The look: a cover photo with a big white title on a dark fade, then one
numbered point per slide, text on paper at the top and a photo fading in under
it, the mark on every slide, no faces. The last slide asks for the follow.
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
import brand as B  # noqa: E402
import carousels as C  # noqa: E402

W, H = 1080, 1350
MARGIN = 80
TEXT_W = W - 2 * MARGIN


def fade(w: int, h: int, colour, start: float, end: float, top_alpha: int, bottom_alpha: int) -> Image.Image:
    y = np.linspace(0, 1, h)[:, None]
    t = np.clip((y - start) / max(end - start, 1e-6), 0, 1)
    t = t * t * (3 - 2 * t)
    alpha = (top_alpha + (bottom_alpha - top_alpha) * t).repeat(w, axis=1).astype(np.uint8)
    out = Image.new("RGBA", (w, h), colour + (0,))
    out.putalpha(Image.fromarray(alpha, "L"))
    return out


def get_photo(pid: str, cache: str, w: int, h: int, focus=(0.5, 0.5)) -> Image.Image:
    img = B.photo(pid, cache)
    if img is None:  # a missing photo falls back to the brand's own gradient
        g = np.linspace(0, 1, h)[:, None, None]
        arr = (np.array(B.INK)[None, None, :] * (1 - g) + np.array(B.BRASS)[None, None, :] * g).repeat(w, axis=1)
        return Image.fromarray(arr.astype(np.uint8), "RGB")
    return B.cover(img, w, h, focus)


def wrap(text: str, f, max_w: float) -> list:
    """Wrapped so no line is left with a single word."""
    lines = B.wrap_lines(text, f, max_w)
    if len(lines) < 2:
        return lines
    lo, hi = max_w * 0.5, max_w
    while hi - lo > 4:
        mid = (lo + hi) / 2
        if len(B.wrap_lines(text, f, mid)) <= len(lines):
            hi = mid
        else:
            lo = mid
    return B.wrap_lines(text, f, hi)


def fit(text: str, size_max: int, size_min: int, max_w: int, max_lines: int, weight: int, path: str):
    size = size_max
    while True:
        f = B.font(size, weight, path)
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
    m = B.mark(size)
    if label:
        f = B.font(30, 800, B.DISPLAY)
        text = "SINCRONIA"
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
    f, lines, size = fit(title, 88, 56, TEXT_W, 4, 800, B.DISPLAY)
    leading = 1.08
    block = size * leading * len(lines)
    y_text = H - 92 - block
    brand_row(img, int(y_text - 40 - 46), B.WHITE, True, 46)
    centred(ImageDraw.Draw(img), lines, f, y_text, B.WHITE, leading)
    return img.convert("RGB")


def slide_point(n: int, heading: str, lines: list, punch: str, pid: str, cache: str) -> Image.Image:
    img = Image.new("RGBA", (W, H), B.PAPER + (255,))
    d = ImageDraw.Draw(img)
    brand_row(img, 70, B.INK, False, 72)

    for scale in (1.0, 0.94, 0.88, 0.82, 0.76):
        hf, hlines, hs = fit(f"{n}. {heading.upper()}", int(72 * scale), int(48 * scale), TEXT_W, 2, 800, B.DISPLAY)
        bf = B.font(int(42 * scale), 400, B.BODY)
        pf = B.font(int(42 * scale), 700, B.BODY)
        body = [w for line in lines for w in wrap(line, bf, TEXT_W)]
        plines = wrap(punch, pf, TEXT_W)
        end = 200 + hs * 1.08 * len(hlines) + 30 + bf.size * 1.38 * len(body) + 22 + pf.size * 1.32 * len(plines)
        if end <= H - 470:
            break
    y = 200
    y = centred(d, hlines, hf, y, B.INK, 1.08) + 30
    y = centred(d, body, bf, y, B.MUTED, 1.38) + 22
    y = centred(d, plines, pf, y, B.BRASS_INK, 1.32)

    top = int(y + 40)
    ph = get_photo(pid, cache, W, H - top, (0.5, 0.5)).convert("RGBA")
    img.alpha_composite(ph, (0, top))
    band = min(240, (H - top) // 2)
    img.alpha_composite(fade(W, band, B.PAPER, 0.0, 1.0, 255, 0), (0, top))
    return img.convert("RGB")


def slide_follow() -> Image.Image:
    """The last slide of every carousel: what the page gives, and to follow it."""
    img = Image.new("RGBA", (W, H), B.INK + (255,))
    d = ImageDraw.Draw(img)
    tile = B.rounded((150, 150), 38, B.WHITE + (255,))
    tile.alpha_composite(B.mark(110), (20, 20))
    img.alpha_composite(tile, ((W - 150) // 2, 250))
    f, lines, size = fit(C.FOLLOW["title"], 92, 60, TEXT_W, 3, 800, B.DISPLAY)
    y = centred(d, lines, f, 450, B.WHITE, 1.06) + 36
    bf = B.font(40, 500, B.BODY)
    body = [w for line in C.FOLLOW["lines"] for w in wrap(line, bf, TEXT_W)]
    y = centred(d, body, bf, y, (196, 190, 182), 1.4) + 60
    pill = B.pill(C.FOLLOW["pill"], 42, B.INK, B.BRASS + (255,), weight=800)
    img.alpha_composite(pill, ((W - pill.width) // 2, int(y)))
    sf = B.font(30, 500, B.BODY)
    small = B.wrap_lines(C.FOLLOW["small"], sf, TEXT_W)
    centred(d, small, sf, H - 110 - sf.size * 1.4 * (len(small) - 1), (150, 144, 136), 1.4)
    return img.convert("RGB")


def render(date: dt.date, out: str, cache: str, slot: int = 1, topic: dict | None = None) -> dict:
    car = C.carousel(date, slot, topic)
    folder = os.path.join(out, car["date"], f"carousel-{slot}")
    os.makedirs(folder, exist_ok=True)
    slides = [slide_cover(car["title"], car["photos"][0], cache)]
    for i, (heading, lines, punch) in enumerate(car["points"], 1):
        slides.append(slide_point(car["numbers"][i - 1], heading, lines, punch, car["photos"][i], cache))
    slides.append(slide_follow())
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
    ap.add_argument("--slot", type=int, default=1, choices=range(1, C.SLOTS + 1))
    ap.add_argument("--topic", default=None, help="a topic written for this run (JSON, as in carousels.py)")
    args = ap.parse_args()
    date = dt.date.fromisoformat(args.date) if args.date else dt.datetime.now(ZoneInfo("Europe/Madrid")).date()
    topic = None
    if args.topic:
        topic = json.load(open(args.topic, encoding="utf-8"))
        errors = C.check_topic(topic)
        if errors:
            sys.exit("the topic needs fixing:\n- " + "\n- ".join(errors))
    meta = render(date, args.out, args.cache, args.slot, topic)
    print(f"{meta['date']} slot {meta['slot']}: {meta['title']}")
    for name in meta["slides"]:
        print(f"  {os.path.join(meta['folder'], name)}")


if __name__ == "__main__":
    main()
