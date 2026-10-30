"""Sowld's look: colours, fonts, the mark, and the photo helpers the slides use.

Split out of SocialPerks' daily.py, which carried the whole video pipeline
with it. The carousel needs none of that: only a palette, a few drawing
helpers and a way to fetch a photo. Keeping it here means Sowld's carousels
have no dependency on the other product's code.

The colours are getsowld.com's own tokens (webapp/templates/landing.html in
emanuelconti/sowld): the near-black ink, the pink that is the brand's single
accent, and the warm paper behind everything.
"""

from __future__ import annotations

import math
import os
import sys
import urllib.request

import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
DISPLAY = os.path.join(HERE, "fonts", "InterTight-latin.ttf")
BODY = os.path.join(HERE, "fonts", "Inter-latin.ttf")
MARK = os.path.join(HERE, "assets", "mark.png")

# getsowld.com's tokens.
INK = (20, 24, 26)  # --ink   #14181a
SIGNAL = (200, 26, 92)  # --lime  #c81a5c, the brand's one accent
DEEP = (156, 17, 73)  # --lime2 #9c1149
PAPER = (251, 250, 249)  # --paper #fbfaf9
MUTED = (110, 104, 98)  # --muted #6e6862
SOFT = (242, 239, 233)  # --soft  #f2efe9
WHITE = (255, 255, 255)

_fonts: dict = {}


def font(size: int, weight: int = 800, path: str = DISPLAY) -> ImageFont.FreeTypeFont:
    key = (path, size, weight)
    if key not in _fonts:
        f = ImageFont.truetype(path, size)
        f.set_variation_by_axes([weight])
        _fonts[key] = f
    return _fonts[key]


def clamp(x: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return lo if x < lo else hi if x > hi else x


def rounded(size, radius, fill, outline=None, width=0) -> Image.Image:
    im = Image.new("RGBA", size, (0, 0, 0, 0))
    ImageDraw.Draw(im).rounded_rectangle((0, 0, size[0] - 1, size[1] - 1), radius, fill=fill, outline=outline, width=width)
    return im


def photo(pid: str, cache: str) -> Image.Image | None:
    """An Unsplash photo by id, cached. A photo that cannot be fetched returns
    None and the caller falls back to a gradient, so a slide always renders."""
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
    """Fill w x h with the photo, cropping the overflow around a focus point."""
    r = max(w / img.width, h / img.height)
    im = img.resize((math.ceil(img.width * r), math.ceil(img.height * r)), Image.LANCZOS)
    x = int(clamp(focus[0] * im.width - w / 2, 0, im.width - w))
    y = int(clamp(focus[1] * im.height - h / 2, 0, im.height - h))
    return im.crop((x, y, x + w, y + h))


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


def pill(text, size, fg, bg, weight=700, pad_x=None, pad_y=None) -> Image.Image:
    f = font(size, weight, BODY)
    pad_x = pad_x or int(size * 0.8)
    pad_y = pad_y or int(size * 0.5)
    w = int(f.getlength(text) + pad_x * 2)
    h = int(size * 1.25 + pad_y * 2)
    im = rounded((w, h), h // 2, bg)
    ImageDraw.Draw(im).text((pad_x, (h - size * 1.2) / 2), text, font=f, fill=fg)
    return im


def mark(size: int) -> Image.Image:
    """Sowld's mark. Falls back to drawing it, so a missing file never stops a run."""
    try:
        return Image.open(MARK).convert("RGBA").resize((size, size), Image.LANCZOS)
    except Exception:
        im = rounded((size, size), size // 4, INK + (255,))
        inner = size // 2
        im.alpha_composite(rounded((inner, inner), inner // 3, SIGNAL + (255,)), ((size - inner) // 2,) * 2)
        return im


def gradient(w: int, h: int, top=SIGNAL, bottom=INK) -> Image.Image:
    """Stands in for a photo that could not be fetched."""
    g = np.linspace(0, 1, h)[:, None, None]
    arr = (np.array(top)[None, None, :] * (1 - g) + np.array(bottom)[None, None, :] * g).repeat(w, axis=1)
    return Image.fromarray(arr.astype(np.uint8), "RGB")
