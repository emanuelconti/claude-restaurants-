#!/usr/bin/env python3
"""Sincronia's look, shared by every carousel: colours, type, the mark, photos.

The palette is the site's own (sincronia/landing/index.html): paper, ink,
muted and brass. The mark is the site's favicon drawn at any size, so the
feed and the site read as one brand.
"""

from __future__ import annotations

import math
import os
import sys
import urllib.request

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
DISPLAY = os.path.join(HERE, "fonts", "InterTight-latin.ttf")
BODY = os.path.join(HERE, "fonts", "Inter-latin.ttf")

# sincronia/landing/index.html :root
PAPER = (251, 250, 249)
SUB = (242, 239, 233)
INK = (20, 24, 26)
MUTED = (110, 104, 98)
BRASS = (176, 122, 69)
BRASS_INK = (138, 92, 43)
WHITE = (255, 255, 255)

_fonts: dict = {}


def font(size: int, weight: int = 800, path: str = DISPLAY) -> ImageFont.FreeTypeFont:
    key = (path, size, weight)
    if key not in _fonts:
        f = ImageFont.truetype(path, size)
        try:
            f.set_variation_by_axes([weight])
        except Exception:
            pass
        _fonts[key] = f
    return _fonts[key]


def clamp(x: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return lo if x < lo else hi if x > hi else x


def rounded(size, radius, fill, outline=None, width=0) -> Image.Image:
    img = Image.new("RGBA", size, (0, 0, 0, 0))
    ImageDraw.Draw(img).rounded_rectangle((0, 0, size[0] - 1, size[1] - 1), radius, fill=fill,
                                          outline=outline, width=width)
    return img


def mark(size: int) -> Image.Image:
    """The site's favicon: an ink tile with a brass S."""
    img = rounded((size, size), max(2, int(size * 0.22)), INK + (255,))
    d = ImageDraw.Draw(img)
    f = font(int(size * 0.62), 800, DISPLAY)
    d.text((size / 2, size * 0.53), "S", font=f, fill=BRASS, anchor="mm")
    return img


def wrap_lines(text: str, f, max_w: float) -> list:
    lines, line = [], ""
    for w in text.split(" "):
        trial = (line + " " + w).strip()
        if line and f.getlength(trial) > max_w:
            lines.append(line)
            line = w
        else:
            line = trial
    return lines + [line]


def photo(pid: str, cache: str) -> Image.Image | None:
    """An Unsplash photo by id, cached; a missing one never stops a carousel."""
    os.makedirs(cache, exist_ok=True)
    path = os.path.join(cache, f"{pid}.jpg")
    if not os.path.exists(path) or os.path.getsize(path) < 5000:
        url = f"https://images.unsplash.com/photo-{pid}?w=1400&q=85&fm=jpg"
        try:
            with urllib.request.urlopen(url, timeout=60) as r, open(path, "wb") as out:
                out.write(r.read())
        except Exception as error:
            print(f"photo {pid} unavailable: {error}", file=sys.stderr)
            return None
    try:
        return Image.open(path).convert("RGB")
    except Exception:
        return None


def cover(img: Image.Image, w: int, h: int, focus=(0.5, 0.45)) -> Image.Image:
    r = max(w / img.width, h / img.height)
    im = img.resize((math.ceil(img.width * r), math.ceil(img.height * r)), Image.LANCZOS)
    x = int(clamp(focus[0] * im.width - w / 2, 0, im.width - w))
    y = int(clamp(focus[1] * im.height - h / 2, 0, im.height - h))
    return im.crop((x, y, x + w, y + h))


def pill(text: str, size: int, fg, bg, weight: int = 800) -> Image.Image:
    f = font(size, weight, DISPLAY)
    pad_x, pad_y = int(size * 0.95), int(size * 0.55)
    w = int(f.getlength(text)) + pad_x * 2
    h = int(size * 1.5) + pad_y
    img = rounded((w, h), h // 2, bg)
    ImageDraw.Draw(img).text((w / 2, h / 2), text, font=f, fill=fg, anchor="mm")
    return img
