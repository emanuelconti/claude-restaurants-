#!/usr/bin/env python3
"""A Sowld carousel: a swipeable list post for Instagram, rendered as JPEGs.

    python3 carousel.py                                   # today (Rome time), slot 1
    python3 carousel.py --date 2026-10-30 --slot 2        # any day and slot; the same pair always gives the same post
    python3 carousel.py --slot 3 --topic topic.json       # a topic written for this run

Writes, under --out/<date>/carousel-<slot>/: slide-01.jpg and on (1080x1350,
the 4:5 feed size), and carousel.json with the title, the slide files and the
caption.

The look: a cover photo with a big white title on a dark fade, then one
numbered point per slide, the text on white at the top and a photo fading in
under it, the mark on every slide, no faces. The last slide is Sowld, and
only when the topic earns it. What it says comes from carousels.py; the
colours and the mark come from brand.py.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import sys
from zoneinfo import ZoneInfo

from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import brand as B  # noqa: E402
import carousels as C  # noqa: E402

W, H = 1080, 1350
MARGIN = 80
TEXT_W = W - 2 * MARGIN
TZ = ZoneInfo("Europe/Rome")


def fade(w: int, h: int, colour, start: float, end: float, top_alpha: int, bottom_alpha: int) -> Image.Image:
    """A band of one colour whose opacity goes from top_alpha to bottom_alpha between start and end (0..1)."""
    import numpy as np

    y = np.linspace(0, 1, h)[:, None]
    t = np.clip((y - start) / max(end - start, 1e-6), 0, 1)
    t = t * t * (3 - 2 * t)
    alpha = (top_alpha + (bottom_alpha - top_alpha) * t).repeat(w, axis=1).astype(np.uint8)
    out = Image.new("RGBA", (w, h), colour + (0,))
    out.putalpha(Image.fromarray(alpha, "L"))
    return out


def get_photo(pid: str, cache: str, w: int, h: int, focus=(0.5, 0.5), spares=()) -> Image.Image:
    """The photo, or the next one that works.

    Two rules pull against each other here. The owner (31 October): never a
    carousel without its photos, so a flat gradient slide must never be
    published. And: a slot must never silently fail to go out. One dead photo
    id satisfies neither if it takes the whole post down with it, and ids do
    die: one in this repo's own list started returning 404.

    So a photo that cannot be fetched is replaced by another from the same
    set, which looks right because the set was chosen for the topic. Only
    when every single one fails, meaning the network is gone rather than one
    URL, does the run stop without publishing.
    """
    for candidate in (pid, *spares):
        img = B.photo(candidate, cache)
        if img is not None:
            if candidate != pid:
                print(f"photo {pid} unavailable, used {candidate} instead", file=sys.stderr)
            return B.cover(img, w, h, focus)
    sys.exit(f"no photo could be fetched, not {pid} nor any of its {len(spares)} alternatives "
             "(is images.unsplash.com allowed in the environment's network access?): "
             "nothing rendered, nothing published")


def wrap(text: str, f, max_w: float) -> list:
    """Wrapped like text-wrap: balance, so no line ends with one word alone."""
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
    """The biggest size, down to size_min, at which text wraps into max_lines."""
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
        text = C.BRAND_NAME
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


COVER_PALETTES = [((244, 225, 222), (120, 40, 60)), ((222, 231, 240), (30, 52, 86)), ((236, 232, 220), (60, 52, 40)),
                  ((228, 236, 226), (38, 70, 52)), ((240, 228, 240), (82, 44, 92)), ((248, 240, 220), (110, 70, 20)),
                  ((24, 26, 30), (244, 240, 232))]


def eyebrow(d: ImageDraw.ImageDraw, y: int, colour) -> None:
    """GOOD MESSAGE STUDIO, small and widely spaced, like a fashion label."""
    f = B.font(26, 600, B.BODY)
    text = " ".join("GOOD MESSAGE STUDIO")
    d.text((W / 2, y), text, font=f, fill=colour, anchor="ma")


def slide_cover(title: str, pid: str, cache: str, spares=()) -> Image.Image:
    """Premium covers (2 November 2026): a hero photo with a serif title, or a typographic cover on a soft colour."""
    if pid.startswith("TEXT:"):
        bg, ink = COVER_PALETTES[int(pid.split(":")[1]) % len(COVER_PALETTES)]
        img = Image.new("RGBA", (W, H), bg + (255,))
        d = ImageDraw.Draw(img)
        eyebrow(d, 150, ink)
        d.line((W / 2 - 60, 205, W / 2 + 60, 205), fill=ink, width=2)
        f, lines, size = fit(title, 112, 70, TEXT_W - 40, 5, 400, B.SERIF)
        block = size * 1.12 * len(lines)
        centred(d, lines, f, (H - block) / 2 + 10, ink, 1.12)
        sf = B.font(30, 500, B.BODY)
        d.text((W / 2, H - 130), "swipe", font=sf, fill=ink, anchor="ma")
        d.line((W / 2 + 62, H - 112, W / 2 + 110, H - 112), fill=ink, width=2)
        return img.convert("RGB")
    img = get_photo(pid, cache, W, H, (0.5, 0.42), spares).convert("RGBA")
    img.alpha_composite(fade(W, H, (0, 0, 0), 0.42, 0.86, 0, 200))
    f, lines, size = fit(title, 96, 62, TEXT_W, 4, 400, B.SERIF)
    leading = 1.1
    y_text = H - 110 - size * leading * len(lines)
    d = ImageDraw.Draw(img)
    eyebrow(d, int(y_text - 70), (255, 255, 255))
    centred(d, lines, f, y_text, B.WHITE, leading)
    return img.convert("RGB")


def slide_point(n: int, heading: str, lines: list, punch: str, pid: str, cache: str, spares=()) -> Image.Image:
    img = Image.new("RGBA", (W, H), B.WHITE + (255,))
    d = ImageDraw.Draw(img)
    brand_row(img, 70, B.INK, False, 72)

    # The text block, at a size that leaves at least 470px of photo.
    for scale in (1.0, 0.94, 0.88, 0.82, 0.76, 0.70, 0.64, 0.58):
        hf, hlines, hs = fit(f"{n}. {heading}", int(74 * scale), int(52 * scale), TEXT_W, 2, 400, B.SERIF)
        bf = B.font(int(42 * scale), 400, B.BODY)
        pf = B.font(int(42 * scale), 700, B.BODY)
        body = [w for line in lines for w in wrap(line, bf, TEXT_W)]
        plines = wrap(punch, pf, TEXT_W)
        end = 200 + hs * 1.08 * len(hlines) + 30 + bf.size * 1.38 * len(body) + 22 + pf.size * 1.32 * len(plines)
        if end <= H - 430:
            break
    y = 200
    y = centred(d, hlines, hf, y, B.INK, 1.08) + 30
    y = centred(d, body, bf, y, B.MUTED, 1.38) + 22
    y = centred(d, plines, pf, y, B.SIGNAL, 1.32)

    top = int(y + 40)
    ph = get_photo(pid, cache, W, H - top, (0.5, 0.5), spares).convert("RGBA")
    img.alpha_composite(ph, (0, top))
    band = min(240, (H - top) // 2)
    img.alpha_composite(fade(W, band, B.WHITE, 0.0, 1.0, 255, 0), (0, top))
    return img.convert("RGB")


CREAM = (247, 243, 236)
PASTELS = [(244, 220, 222), (219, 231, 244), (222, 234, 222), (248, 238, 206), (236, 226, 244)]


def _point_text(d, n, heading, lines, punch, y, max_bottom, colour_body, scale_start=1.0):
    """The heading, the lines and the closing line, centred from y, shrunk until they end above max_bottom."""
    for scale in (1.0, 0.94, 0.88, 0.82, 0.76, 0.70, 0.64, 0.58):
        scale *= scale_start
        hf, hlines, hs = fit(f"{n}. {heading}" if n else heading, int(74 * scale), int(52 * scale), TEXT_W, 3, 400, B.SERIF)
        bf = B.font(int(42 * scale), 400, B.BODY)
        pf = B.font(int(42 * scale), 700, B.BODY)
        body = [w for line in lines for w in wrap(line, bf, TEXT_W)]
        plines = wrap(punch, pf, TEXT_W)
        end = y + hs * 1.08 * len(hlines) + 26 + bf.size * 1.38 * len(body) + 20 + pf.size * 1.32 * len(plines)
        if end <= max_bottom:
            break
    return hf, hlines, bf, body, pf, plines, end


def slide_point_product(n: int, heading: str, lines: list, punch: str, pid: str, cache: str, spares=()) -> Image.Image:
    """The product framed like a shop card on cream, the message under it."""
    img = Image.new("RGBA", (W, H), CREAM + (255,))
    d = ImageDraw.Draw(img)
    brand_row(img, 52, B.INK, False, 56)
    cw, ch, top = W - 180, 700, 150
    ph = get_photo(pid, cache, cw, ch, (0.5, 0.45), spares).convert("RGBA")
    mask = Image.new("L", (cw, ch), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, cw - 1, ch - 1), 40, fill=255)
    ph.putalpha(mask)
    sh = Image.new("RGBA", (cw + 80, ch + 80), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle((40, 50, cw + 40, ch + 50), 40, fill=(0, 0, 0, 55))
    img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(20)), ((W - cw) // 2 - 40, top - 40))
    img.alpha_composite(ph, ((W - cw) // 2, top))
    y = top + ch + 44
    hf, hlines, bf, body, pf, plines, _ = _point_text(d, n, heading, lines, punch, y, H - 50, B.MUTED, 0.9)
    y = centred(d, hlines, hf, y, B.INK, 1.08) + 26
    y = centred(d, body, bf, y, B.MUTED, 1.38) + 20
    centred(d, plines, pf, y, B.SIGNAL, 1.32)
    return img.convert("RGB")


def slide_point_text(n: int, heading: str, lines: list, punch: str, colour_index: int) -> Image.Image:
    """Only words, big, on a soft pastel from the hoodies' own colours."""
    img = Image.new("RGBA", (W, H), PASTELS[colour_index % len(PASTELS)] + (255,))
    d = ImageDraw.Draw(img)
    brand_row(img, 70, B.INK, False, 64)
    hf, hlines, bf, body, pf, plines, end = _point_text(d, n, heading, lines, punch, 0, H - 300, B.INK, 1.35)
    block = end
    y = max(220, (H - block) / 2)
    y = centred(d, hlines, hf, y, B.INK, 1.08) + 26
    y = centred(d, body, bf, y, (60, 62, 70), 1.38) + 20
    centred(d, plines, pf, y, B.SIGNAL, 1.32)
    return img.convert("RGB")


def slide_cta() -> Image.Image:
    img = Image.new("RGBA", (W, H), B.INK + (255,))
    d = ImageDraw.Draw(img)
    tile = B.rounded((190, 190), 48, B.WHITE + (255,))
    tile.alpha_composite(B.mark(140), (25, 25))
    img.alpha_composite(tile, ((W - 190) // 2, 230))
    f, lines, size = fit(C.CTA["title"], 84, 60, TEXT_W, 3, 800, B.DISPLAY)
    y = centred(d, lines, f, 470, B.WHITE, 1.06) + 36
    bf = B.font(40, 500, B.BODY)
    body = [w for line in C.CTA["lines"] for w in wrap(line, bf, TEXT_W)]
    y = centred(d, body, bf, y, (218, 212, 208), 1.4) + 56
    p = B.pill(C.CTA["url"], 44, B.WHITE, B.SIGNAL + (255,), weight=800)
    img.alpha_composite(p, ((W - p.width) // 2, int(y)))
    sf = B.font(30, 500, B.BODY)
    small = B.wrap_lines(C.CTA["small"], sf, TEXT_W)
    centred(d, small, sf, H - 110 - sf.size * 1.4 * (len(small) - 1), (176, 170, 166), 1.4)
    return img.convert("RGB")


def slide_follow() -> Image.Image:
    """The last slide: the one moment someone is most likely to follow.

    Dark like the cover, so the carousel closes where it opened. No URL and
    no product: the only thing this post is selling is the next one."""
    img = Image.new("RGBA", (W, H), B.INK + (255,))
    d = ImageDraw.Draw(img)
    tile = B.rounded((190, 190), 48, B.WHITE + (255,))
    tile.alpha_composite(B.mark(140), (25, 25))
    img.alpha_composite(tile, ((W - 190) // 2, 250))
    f, lines, size = fit(C.FOLLOW["title"], 84, 60, TEXT_W, 3, 800, B.DISPLAY)
    y = centred(d, lines, f, 500, B.WHITE, 1.06) + 34
    bf = B.font(38, 500, B.BODY)
    body = [w for line in C.FOLLOW["lines"] for w in wrap(line, bf, TEXT_W)]
    y = centred(d, body, bf, y, (214, 208, 204), 1.44) + 58
    p = B.pill(C.FOLLOW["handle"], 44, B.WHITE, B.SIGNAL + (255,), weight=800)
    img.alpha_composite(p, ((W - p.width) // 2, int(y)))
    return img.convert("RGB")


def render(date: dt.date, out: str, cache: str, slot: int = 1, topic: dict | None = None) -> dict:
    car = C.carousel(date, slot, topic)
    folder = os.path.join(out, car["date"], f"carousel-{slot}")
    os.makedirs(folder, exist_ok=True)
    # Every slide can fall back on any other photo the topic was given, so one
    # dead id costs a picture rather than the whole post.
    pool = [p for p in dict.fromkeys(car["photos"]) if not p.startswith("TEXT:")]  # typographic covers are not photos
    spares = lambda pid: tuple(p for p in pool if p != pid)
    slides = [slide_cover(car["title"], car["photos"][0], cache, spares(car["photos"][0]))]
    for i, (heading, lines, punch) in enumerate(car["points"], 1):
        pid = car["photos"][i]
        # The owner (1 November 2026): like a page that really grows, the slides vary: the product as a shop
        # card with the message under it, words alone on a pastel, or text with the photo. By default they take turns.
        layouts = car.get("layouts") or []
        kind = layouts[i - 1] if i - 1 < len(layouts) else ("product", "classic", "text")[(i - 1) % 3]
        if kind == "product":
            slides.append(slide_point_product(car["numbers"][i - 1], heading, lines, punch, pid, cache, spares(pid)))
        elif kind == "text":
            slides.append(slide_point_text(car["numbers"][i - 1], heading, lines, punch, i))
        else:
            slides.append(slide_point(car["numbers"][i - 1], heading, lines, punch, pid, cache, spares(pid)))
    if car["cta"]:
        slides.append(slide_cta())
    if car.get("follow"):  # Good Message Studio: the shop slide, then the follow slide (1 November 2026)
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
    ap.add_argument("--date", default=None, help="YYYY-MM-DD; default today in Rome")
    ap.add_argument("--out", default=os.path.join(HERE, "out"))
    ap.add_argument("--cache", default=os.path.join(HERE, ".cache"))
    ap.add_argument("--slot", type=int, default=1, choices=range(1, C.SLOTS + 1), help="which of the day's carousels")
    ap.add_argument("--topic", default=None, help="a topic written for this run (JSON, as in carousels.py); else the written bank")
    args = ap.parse_args()
    date = dt.date.fromisoformat(args.date) if args.date else dt.datetime.now(TZ).date()
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
    print(f"  {os.path.join(meta['folder'], 'carousel.json')}")


if __name__ == "__main__":
    main()
