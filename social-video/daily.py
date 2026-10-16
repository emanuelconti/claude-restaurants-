#!/usr/bin/env python3
"""The day's SocialPerks video for the social profile, rendered from scratch.

    python3 daily.py                      # today, Spanish and English
    python3 daily.py --date 2026-10-20    # any day; the same day always renders the same video
    python3 daily.py --lang es --out /tmp/videos

Writes, under --out/<date>/: socialperks-<date>-<lang>.mp4 (1080x1920, 30 fps,
H.264 and AAC, 30 to 34 seconds), a cover JPEG per language and caption.txt
with the text to paste under the post in both languages.

Every video explains the whole idea, whatever the day's format: the hour that
does not fill, the small gift put on it, the customer who shares a Story or
sends a message, the friend who comes in and shows a code at the counter, and
what that brought. The format decides the opening and the order around it.

What it says comes from episodes.py. Everything is drawn here with Pillow,
frame by frame from the time alone, and encoded with ffmpeg; the music bed is
synthesised from the date. Nothing to install beyond Python 3 with Pillow and
numpy, and ffmpeg: the daily run starts in a fresh machine.
"""

from __future__ import annotations

import argparse
import datetime as dt
import math
import os
import subprocess
import sys
import urllib.request
import wave

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import episodes as E  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
W, H, FPS = 1080, 1920, 30
DISPLAY = os.path.join(HERE, "fonts", "InterTight-latin.ttf")
BODY = os.path.join(HERE, "fonts", "Inter-latin.ttf")
MARK = os.path.join(HERE, "assets", "mark.png")
LEFT = 90
TEXT_W = W - 2 * LEFT

# The brand's own colours (socialperks globals.css): ink, signal, the Story
# ring's pink and yellow, paper.
INK = (21, 22, 27)
SIGNAL = (58, 43, 224)
PINK = (223, 73, 150)
YELLOW = (253, 196, 104)
VIOLET = (139, 128, 255)
PAPER = (246, 241, 234)
WHITE = (255, 255, 255)
GREEN = (28, 160, 104)
PALETTES = [
    dict(bg=(13, 13, 18), fg=WHITE, hl=SIGNAL, hl_text=WHITE, acc=YELLOW, sub=(184, 184, 200), blob=(SIGNAL, PINK)),
    dict(bg=SIGNAL, fg=WHITE, hl=YELLOW, hl_text=INK, acc=YELLOW, sub=(222, 218, 255), blob=(PINK, VIOLET)),
    dict(bg=PAPER, fg=INK, hl=YELLOW, hl_text=INK, acc=SIGNAL, sub=(96, 96, 108), blob=(YELLOW, PINK)),
    dict(bg=PINK, fg=WHITE, hl=INK, hl_text=WHITE, acc=YELLOW, sub=(255, 228, 242), blob=(YELLOW, SIGNAL)),
    dict(bg=INK, fg=WHITE, hl=PINK, hl_text=WHITE, acc=VIOLET, sub=(176, 176, 188), blob=(PINK, SIGNAL)),
]

# Where the link sticker sits on each customer photo, clear of the subject
# (the product's story-examples.ts, badgeTop).
STICKER_Y = dict(barber=0.82, salon=0.22, nails=0.70, gym=0.82, wellness=0.84, tattoo_studio=0.30, physio=0.20,
                 hotel=0.30, restaurant=0.64, bar=0.74, cocktail_bar=0.24, pizzeria=0.72, cafe=0.76, brunch=0.66,
                 ice_cream=0.28)

# The 9:16 window the product's own crop of a photo shows (src/assets/stories),
# where it differs from the middle: how far across it is centred, and how much
# of the top it leaves out (the cocktail without the face above it).
STORY_FRAME = dict(barber=(0.30, 0.0), cocktail_bar=(0.543, 0.143))

# ----------------------------------------------------------------- basics

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


def ease_out(x: float) -> float:
    x = clamp(x)
    return 1 - (1 - x) ** 3


def ease_in_out(x: float) -> float:
    x = clamp(x)
    return 4 * x ** 3 if x < 0.5 else 1 - (-2 * x + 2) ** 3 / 2


def ease_back(x: float) -> float:
    x = clamp(x)
    c1 = 1.70158
    c3 = c1 + 1
    return 1 + c3 * (x - 1) ** 3 + c1 * (x - 1) ** 2


def prog(t: float, start: float, dur: float) -> float:
    return clamp((t - start) / dur) if dur > 0 else float(t >= start)


def paste(frame: Image.Image, sprite: Image.Image, x: float, y: float, alpha: float = 1.0) -> None:
    """Alpha-composite `sprite` at (x, y), clipped to the frame, faded by `alpha`."""
    if alpha <= 0.003:
        return
    x, y = int(round(x)), int(round(y))
    sx0, sy0 = max(0, -x), max(0, -y)
    sx1, sy1 = min(sprite.width, W - x), min(sprite.height, H - y)
    if sx1 <= sx0 or sy1 <= sy0:
        return
    part = sprite.crop((sx0, sy0, sx1, sy1)) if (sx0, sy0, sx1, sy1) != (0, 0, sprite.width, sprite.height) else sprite
    if alpha < 0.997:
        part = part.copy()
        a = part.getchannel("A").point(lambda v: int(v * alpha))
        part.putalpha(a)
    frame.alpha_composite(part, (x + sx0, y + sy0))


def scaled(sprite: Image.Image, s: float) -> Image.Image:
    if abs(s - 1) < 0.003:
        return sprite
    w, h = max(1, int(sprite.width * s)), max(1, int(sprite.height * s))
    return sprite.resize((w, h), Image.BILINEAR)


def paste_scaled(frame, sprite, cx, cy, s=1.0, alpha=1.0):
    """Paste `sprite` scaled by `s` around its centre (cx, cy)."""
    sp = scaled(sprite, s)
    paste(frame, sp, cx - sp.width / 2, cy - sp.height / 2, alpha)


def rounded(size, radius, fill, outline=None, width=0) -> Image.Image:
    im = Image.new("RGBA", size, (0, 0, 0, 0))
    ImageDraw.Draw(im).rounded_rectangle((0, 0, size[0] - 1, size[1] - 1), radius, fill=fill, outline=outline, width=width)
    return im


def shadowed(sprite: Image.Image, blur: int = 28, offset: int = 18, opacity: int = 110) -> Image.Image:
    pad = blur * 2
    out = Image.new("RGBA", (sprite.width + pad * 2, sprite.height + pad * 2 + offset), (0, 0, 0, 0))
    shadow = Image.new("RGBA", sprite.size, (8, 8, 20, 0))
    shadow.putalpha(sprite.getchannel("A").point(lambda v: v * opacity // 255))
    out.alpha_composite(shadow, (pad, pad + offset))
    out = out.filter(ImageFilter.GaussianBlur(blur))
    out.alpha_composite(sprite, (pad, pad))
    return out


# ----------------------------------------------------------------- photos

def photo(pid: str, cache: str) -> Image.Image | None:
    os.makedirs(cache, exist_ok=True)
    path = os.path.join(cache, f"{pid}.jpg")
    if not os.path.exists(path) or os.path.getsize(path) < 5000:
        url = f"https://images.unsplash.com/photo-{pid}?w=1400&q=85&fm=jpg"
        try:
            with urllib.request.urlopen(url, timeout=60) as r, open(path, "wb") as out:
                out.write(r.read())
        except Exception as error:  # a missing photo never stops the day's video
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


def story_frame(img: Image.Image, cat: str) -> Image.Image:
    if cat not in STORY_FRAME:
        return img
    fx, top = STORY_FRAME[cat]
    img = img.crop((0, int(img.height * top), img.width, img.height))
    w = min(img.width, round(img.height * 9 / 16))
    h = min(img.height, round(w * 16 / 9))
    x = int(clamp(fx * img.width - w / 2, 0, img.width - w))
    y = (img.height - h) // 2
    return img.crop((x, y, x + w, y + h))


def fallback_photo(pal) -> Image.Image:
    """A gradient in the day's colours, if Unsplash cannot be reached."""
    a, b = pal["blob"]
    g = np.linspace(0, 1, H)[:, None, None]
    arr = (np.array(a)[None, None, :] * (1 - g) + np.array(b)[None, None, :] * g).repeat(W, axis=1)
    return Image.fromarray(arr.astype(np.uint8), "RGB")


class KenBurns:
    """A photo that fills the screen and drifts slowly closer."""

    def __init__(self, img: Image.Image, zoom=(1.0, 1.09), focus=(0.5, 0.45), dark: float = 0.0, blur: int = 0):
        base = cover(img, int(W * 1.12), int(H * 1.12), focus)
        if blur:
            base = base.filter(ImageFilter.GaussianBlur(blur))
        if dark:
            base = Image.blend(base, Image.new("RGB", base.size, (8, 8, 14)), dark)
        self.base = base
        self.zoom = zoom

    def frame(self, p: float) -> Image.Image:
        z = self.zoom[0] + (self.zoom[1] - self.zoom[0]) * ease_in_out(p)
        cw, ch = self.base.width / z, self.base.height / z
        x = (self.base.width - cw) / 2
        y = (self.base.height - ch) / 2
        return self.base.crop((int(x), int(y), int(x + cw), int(y + ch))).resize((W, H), Image.BILINEAR).convert("RGBA")


class Backdrop:
    """The day's colour, with two soft blobs of the Story ring drifting under it."""

    def __init__(self, pal):
        self.color = pal["bg"]
        big = Image.new("RGBA", (W + 400, H + 400), (0, 0, 0, 0))
        d = ImageDraw.Draw(big)
        a, b = pal["blob"]
        d.ellipse((60, 180, 900, 1020), fill=a + (150,))
        d.ellipse((520, 1240, 1400, 2120), fill=b + (130,))
        self.blobs = big.filter(ImageFilter.GaussianBlur(170))

    def frame(self, t: float) -> Image.Image:
        im = Image.new("RGBA", (W, H), self.color + (255,))
        ox = 200 + 90 * math.sin(t * 0.7)
        oy = 200 + 120 * math.cos(t * 0.5)
        im.alpha_composite(self.blobs.crop((int(ox), int(oy), int(ox) + W, int(oy) + H)))
        return im


# ----------------------------------------------------------------- text

def parse(text: str):
    """Words, each marked highlighted or not; `*...*` marks the highlight."""
    words, hl = [], False
    for raw in text.split(" "):
        if not raw:
            continue
        starts = raw.startswith("*")
        ends = raw.endswith("*") or raw.endswith("*.") or raw.endswith("*,") or raw.endswith("*?") or raw.endswith("*!")
        word = raw.replace("*", "")
        on = hl or starts
        words.append((word, on))
        if starts:
            hl = True
        if ends:
            hl = False
    return words


class Words:
    """A paragraph laid out once, drawn word by word."""

    def __init__(self, text, size_max, size_min, max_w, max_h, weight=800, path=DISPLAY, color=WHITE,
                 hl=None, hl_text=None, align="left", leading=1.06, max_lines=6):
        words = parse(text)
        size = size_max
        while True:
            f = font(size, weight, path)
            lines = self._wrap(words, f, max_w)
            lh = int(size * leading)
            # A single long word ("recomendación?") must fit the width too.
            fits = all(f.getlength(w) <= max_w for w, _ in words)
            if (fits and len(lines) * lh <= max_h and len(lines) <= max_lines) or size <= size_min:
                break
            size -= 4
        self.font, self.size, self.lh = f, size, lh
        space = f.getlength(" ")
        self.items = []
        self.bars = []
        y = 0
        widest = 0
        for line in lines:
            lw = sum(f.getlength(w) for w, _ in line) + space * (len(line) - 1)
            widest = max(widest, lw)
            x = (max_w - lw) / 2 if align == "center" else 0
            run = None
            for i, (w, on) in enumerate(line):
                ww = f.getlength(w)
                self.items.append(dict(word=w, x=x, y=y, w=ww, hl=on))
                if on:
                    if run is None:
                        run = [x, x + ww]
                    else:
                        run[1] = x + ww
                if (not on or i == len(line) - 1) and run is not None:
                    self.bars.append(dict(x0=run[0], x1=run[1], y=y, last=len(self.items) - (1 if on else 2)))
                    run = None
                x += ww + space
            y += lh
        self.height = y
        self.width = widest
        pad = int(size * 0.16)
        self.pad = pad
        for item in self.items:
            colour = (hl_text or color) if item["hl"] and hl else color
            im = Image.new("RGBA", (int(item["w"]) + 8, int(size * 1.35)), (0, 0, 0, 0))
            ImageDraw.Draw(im).text((2, 0), item["word"], font=f, fill=colour)
            item["sprite"] = im
        self.hl = hl

    @staticmethod
    def _wrap(words, f, max_w):
        lines, line, width = [], [], 0.0
        space = f.getlength(" ")
        for w, on in words:
            ww = f.getlength(w)
            if line and width + space + ww > max_w:
                lines.append(line)
                line, width = [], 0.0
            width = width + (space if line else 0) + ww
            line.append((w, on))
        if line:
            lines.append(line)
        return lines

    def draw(self, frame, ox, oy, t, start=0.0, stagger=0.07, dur=0.32, style="slam", alpha=1.0):
        """Words land one after another from `start`; highlight bars sweep in under them."""
        n = len(self.items)
        for bar in self.bars:
            # The bar sweeps in once the highlighted words have landed.
            p = ease_out(prog(t, start + bar["last"] * stagger + 0.12, 0.34))
            if p <= 0 or self.hl is None:
                continue
            x0 = ox + bar["x0"] - self.pad
            x1 = x0 + (bar["x1"] - bar["x0"] + 2 * self.pad) * p
            y0 = oy + bar["y"] + self.size * 0.08
            y1 = y0 + self.size * 1.04
            layer = Image.new("RGBA", (int(x1 - x0) + 2, int(y1 - y0) + 2), (0, 0, 0, 0))
            ImageDraw.Draw(layer).rounded_rectangle((0, 0, layer.width - 1, layer.height - 1), int(self.size * 0.18), fill=self.hl + (255,))
            paste(frame, layer, x0, y0, alpha)
        for i, item in enumerate(self.items):
            p = prog(t, start + i * stagger, dur)
            if p <= 0:
                continue
            sp = item["sprite"]
            if style == "slam":
                s = 1.0 + 0.45 * (1 - ease_back(p)) if p < 1 else 1.0
                cx = ox + item["x"] + sp.width / 2
                cy = oy + item["y"] + sp.height / 2
                paste_scaled(frame, sp, cx, cy, s, alpha * ease_out(p * 1.6))
            else:  # rise
                dy = (1 - ease_out(p)) * self.size * 0.6
                paste(frame, sp, ox + item["x"], oy + item["y"] + dy, alpha * ease_out(p))
        return n


def text_sprite(text, size, weight=700, path=BODY, color=WHITE) -> Image.Image:
    f = font(size, weight, path)
    box = f.getbbox(text)
    im = Image.new("RGBA", (int(f.getlength(text)) + 8, box[3] + int(size * 0.3)), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((2, 0), text, font=f, fill=color)
    return im


def on(colour) -> tuple:
    """White or ink, whichever reads on `colour`."""
    r, g, b = colour[:3]
    return INK if (0.299 * r + 0.587 * g + 0.114 * b) > 150 else WHITE


def pill(text, size, fg, bg, weight=700, pad_x=None, pad_y=None, icon=None) -> Image.Image:
    f = font(size, weight, BODY)
    pad_x = pad_x or int(size * 0.8)
    pad_y = pad_y or int(size * 0.5)
    tw = f.getlength(text)
    iw = int(size * 1.1) if icon else 0
    w = int(tw + pad_x * 2 + iw)
    h = int(size * 1.25 + pad_y * 2)
    im = rounded((w, h), h // 2, bg)
    d = ImageDraw.Draw(im)
    x = pad_x
    if icon == "check":
        r = int(size * 0.45)
        cy = h // 2
        d.ellipse((x, cy - r, x + 2 * r, cy + r), fill=GREEN)
        d.line((x + r * 0.55, cy, x + r * 0.9, cy + r * 0.4, x + r * 1.45, cy - r * 0.45), fill=WHITE, width=max(3, size // 9))
        x += iw
    d.text((x, (h - size * 1.2) / 2), text, font=f, fill=fg)
    return im


def mark(size: int) -> Image.Image:
    try:
        return Image.open(MARK).convert("RGBA").resize((size, size), Image.LANCZOS)
    except Exception:
        return rounded((size, size), size // 4, SIGNAL + (255,))


def link_glyph(d: ImageDraw.ImageDraw, x, y, s, color, width):
    d.rounded_rectangle((x, y + s * 0.25, x + s * 0.62, y + s * 0.62), s * 0.18, outline=color, width=width)
    d.rounded_rectangle((x + s * 0.38, y + s * 0.38, x + s, y + s * 0.75), s * 0.18, outline=color, width=width)


def step_chip(n: int, label: str) -> Image.Image:
    """The step a scene shows, numbered: 1 the quiet hour, 2 the share, 3 the visit."""
    size = 40
    f = font(size, 700, BODY)
    d_ = int(size * 1.5)
    pad = int(size * 0.45)
    w = int(pad + d_ + size * 0.55 + f.getlength(label) + size * 0.9)
    h = d_ + 2 * pad
    im = rounded((w, h), h // 2, (255, 255, 255, 236))
    d = ImageDraw.Draw(im)
    d.ellipse((pad, pad, pad + d_, pad + d_), fill=SIGNAL)
    fn = font(int(size * 0.95), 800, DISPLAY)
    num = str(n)
    d.text((pad + d_ / 2 - fn.getlength(num) / 2, pad + d_ * 0.12), num, font=fn, fill=WHITE)
    d.text((pad + d_ + size * 0.55, (h - size * 1.22) / 2), label, font=f, fill=INK)
    return shadowed(im, blur=14, offset=6, opacity=60)


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


def ring_gradient(size: int) -> Image.Image:
    """The Story ring's colours, corner to corner, in a circle."""
    y, x = np.mgrid[0:size, 0:size] / max(1, size - 1)
    g = (x + (1 - y)) / 2
    stops = [(0.0, (253, 196, 104)), (0.4, (223, 73, 150)), (0.7, (138, 58, 185)), (1.0, SIGNAL)]
    arr = np.zeros((size, size, 3))
    for (a, ca), (b, cb) in zip(stops, stops[1:]):
        m = (g >= a) & (g <= b)
        k = ((g - a) / (b - a))[..., None]
        arr = np.where(m[..., None], np.array(ca) * (1 - k) + np.array(cb) * k, arr)
    im = Image.fromarray(arr.astype(np.uint8), "RGB").convert("RGBA")
    mask = Image.new("L", (size, size), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, size - 1, size - 1), fill=255)
    im.putalpha(mask)
    return im


def camera_glyph(d: ImageDraw.ImageDraw, cx, cy, s, color, width):
    d.rounded_rectangle((cx - s / 2, cy - s * 0.38, cx + s / 2, cy + s * 0.38), s * 0.16, outline=color, width=width)
    r = s * 0.17
    d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=color, width=width)
    d.ellipse((cx + s * 0.27, cy - s * 0.27, cx + s * 0.33, cy - s * 0.21), fill=color)


def chat_glyph(d: ImageDraw.ImageDraw, cx, cy, s, color, width):
    d.ellipse((cx - s / 2, cy - s * 0.42, cx + s / 2, cy + s * 0.38), outline=color, width=width)
    d.line((cx - s * 0.3, cy + s * 0.28, cx - s * 0.42, cy + s * 0.48, cx - s * 0.1, cy + s * 0.37), fill=color, width=width, joint="curve")


# ----------------------------------------------------------------- scenes

class Ctx:
    def __init__(self, ep, lang, cache):
        self.ep, self.lang = ep, lang
        self.cat = ep["category"]
        self.place = E.PLACES[self.cat]
        self.c = self.place[lang]
        self.pal = PALETTES[ep["palette"]]
        self.alt = PALETTES[(ep["palette"] + 2) % len(PALETTES)]
        story = photo(E.STORY_PHOTO[self.cat], cache)
        venue = photo(E.PLACE_PHOTO[self.cat], cache)
        self.story_img = story_frame(story, self.cat) if story else fallback_photo(self.pal)
        self.venue_img = venue or self.story_img
        self.name = self.place["name"]
        self.she = self.place["g"] == "f"

    def t(self, es, en):
        return es if self.lang == "es" else en

    def fill(self, text):
        return E.fill(text, self.cat, self.lang)


def scene_hook(ctx: Ctx, text: str, eyebrow: str | None, dur: float, pal=None):
    pal = pal or ctx.pal
    back = Backdrop(pal)
    words = Words(ctx.fill(text), 132, 72, TEXT_W, 820, color=pal["fg"], hl=pal["hl"], hl_text=pal["hl_text"])
    oy = 900 - words.height / 2
    brow = text_sprite(eyebrow, 46, 700, BODY, pal["sub"]) if eyebrow else None

    def draw(t):
        fr = back.frame(t)
        if brow:
            p = ease_out(prog(t, 0.0, 0.4))
            paste(fr, brow, LEFT, oy - 110 + (1 - p) * 30, p)
        words.draw(fr, LEFT, oy, t, start=0.15, stagger=min(0.09, 1.1 / max(1, len(words.items))))
        return fr
    draw.branded = True  # the watermark goes on the drawn scenes only
    return dur, draw


def scene_story(ctx: Ctx, dur: float):
    kb = KenBurns(ctx.story_img, zoom=(1.0, 1.08))
    sticker_y = STICKER_Y.get(ctx.cat, 0.7) * H
    # The sticker the product prints: venue initials, the venue's tag, the ad label, the customer's link.
    sw, sh = 700, 170
    st = Image.new("RGBA", (sw, sh), (0, 0, 0, 0))
    d = ImageDraw.Draw(st)
    d.rounded_rectangle((0, 0, sw - 1, sh - 1), 44, fill=(255, 255, 255, 236))
    d.ellipse((26, 33, 130, 137), fill=INK)
    initials = "".join(w[0] for w in ctx.place["venue"].split()[:2]).upper()
    fi = font(40, 800, DISPLAY)
    d.text((78 - fi.getlength(initials) / 2, 58), initials, font=fi, fill=WHITE)
    d.text((158, 30), ctx.place["tag"], font=font(50, 800, DISPLAY), fill=INK)
    tagw = font(50, 800, DISPLAY).getlength(ctx.place["tag"])
    label = ctx.t("Publi", "Ad")
    lf = font(26, 800, BODY)
    lx = 158 + tagw + 16
    d.rounded_rectangle((lx, 42, lx + lf.getlength(label) + 18, 80), 8, fill=INK)
    d.text((lx + 9, 44), label, font=lf, fill=WHITE)
    link_glyph(d, 160, 100, 34, SIGNAL, 5)
    d.text((206, 96), f"socialperkses.com/s/{ctx.name.lower()}", font=font(32, 600, BODY), fill=SIGNAL)
    sticker = shadowed(st.rotate(4, expand=True, resample=Image.BICUBIC), blur=22, offset=12, opacity=120)
    # The Story's own chrome: progress, who posted it, the reply field.
    chrome = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    cd = ImageDraw.Draw(chrome)
    top = Image.new("RGBA", (W, 420), (0, 0, 0, 0))
    grad = np.linspace(150, 0, 420).astype(np.uint8)
    top.putalpha(Image.fromarray(np.repeat(grad[:, None], W, axis=1), "L"))
    chrome.alpha_composite(top)
    bot = Image.new("RGBA", (W, 420), (0, 0, 0, 0))
    bot.putalpha(Image.fromarray(np.repeat(grad[::-1][:, None], W, axis=1), "L"))
    chrome.alpha_composite(bot, (0, H - 420))
    cd = ImageDraw.Draw(chrome)
    cd.ellipse((60, 150, 160, 250), fill=None, outline=PINK, width=6)
    cd.ellipse((70, 160, 150, 240), fill=INK)
    fa = font(40, 800, DISPLAY)
    cd.text((110 - fa.getlength(ctx.name[0]) / 2, 176), ctx.name[0], font=fa, fill=WHITE)
    cd.text((184, 172), ctx.place["handle"], font=font(42, 700, BODY), fill=WHITE)
    cd.text((184 + font(42, 700, BODY).getlength(ctx.place["handle"]) + 22, 172), ctx.t("2 h", "2h"), font=font(42, 500, BODY), fill=(255, 255, 255, 200))
    cd.rounded_rectangle((60, H - 250, W - 260, H - 150), 50, outline=(255, 255, 255, 200), width=4)
    caption_text = ctx.t(f"2 · {ctx.name} comparte su enlace", f"2 · {ctx.name} shares {'her' if ctx.she else 'his'} link")
    cap = pill(caption_text, 46, WHITE, (12, 12, 20, 200), weight=700)
    cap_y = 330 if sticker_y > H * 0.5 else 1440

    def draw(t):
        p = t / dur
        fr = kb.frame(p)
        fr.alpha_composite(chrome)
        # Drawn on its own layer: ImageDraw replaces pixels, it does not blend.
        bars = Image.new("RGBA", (W - 120, 8), (255, 255, 255, 90))
        ImageDraw.Draw(bars).rounded_rectangle((0, 0, (W - 121) * clamp(p * 1.1), 7), 4, fill=WHITE + (255,))
        fr.alpha_composite(bars, (60, 110))
        ps = prog(t, 0.45, 0.5)
        if ps > 0:
            paste_scaled(fr, sticker, W / 2, sticker_y, 0.4 + 0.6 * ease_back(ps), clamp(ps * 2))
        pc = ease_out(prog(t, 1.0, 0.4))
        paste(fr, cap, (W - cap.width) / 2, cap_y + (1 - pc) * 24, pc)
        return fr
    return dur, draw


def code_card(ctx: Ctx) -> Image.Image:
    cw, ch = 760, 330
    card = rounded((cw, ch), 56, WHITE + (255,))
    d = ImageDraw.Draw(card)
    d.text((56, 44), ctx.t("Código en el mostrador", "Code at the counter"), font=font(36, 600, BODY), fill=(96, 96, 108))
    f = font(116, 800, DISPLAY)
    code = "482 917"
    x = 56
    for ch_ in code:
        d.text((x, 104), ch_, font=f, fill=INK)
        x += f.getlength(ch_) + (10 if ch_ != " " else 18)
    r = 46
    cx, cy = cw - 56 - r, 170
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=GREEN)
    d.line((cx - r * 0.45, cy, cx - r * 0.1, cy + r * 0.38, cx + r * 0.5, cy - r * 0.35), fill=WHITE, width=11)
    d.text((56, 256), ctx.t("Registrada" if ctx.she else "Registrado", "Checked in"), font=font(34, 700, BODY), fill=GREEN)
    return shadowed(card, blur=30, offset=20, opacity=90)


def scene_friend(ctx: Ctx, dur: float):
    pal = ctx.alt
    back = Backdrop(pal)
    wd = ctx.c["wd"]
    text = ctx.t(
        f"{'Una amiga' if ctx.she else 'Un amigo'} de {ctx.name} vino el *{wd}*.",
        f"{ctx.name}'s friend came in on *{wd}*.",
    )
    words = Words(text, 112, 70, TEXT_W, 460, color=pal["fg"], hl=pal["hl"], hl_text=pal["hl_text"])
    card = code_card(ctx)
    gift = pill(ctx.t(f"Regalo: {ctx.c['gift']}", f"Gift: {ctx.c['gift']}"), 44, on(pal["acc"]), pal["acc"] + (255,), weight=800)
    chip = step_chip(3, ctx.t(f"{'Su amiga' if ctx.she else 'Su amigo'} viene", f"{'Her' if ctx.she else 'His'} friend comes in"))

    def draw(t):
        fr = back.frame(t + 3)
        pchip = ease_out(prog(t, 0.0, 0.35))
        paste(fr, chip, LEFT - 28, 250 + (1 - pchip) * 20, pchip)
        words.draw(fr, LEFT, 420, t, start=0.05, stagger=0.06)
        pc = prog(t, 0.75, 0.45)
        if pc > 0:
            paste_scaled(fr, card, W / 2, 1060, 0.85 + 0.15 * ease_back(pc), clamp(pc * 2))
        pg = ease_back(prog(t, 1.35, 0.4))
        if pg > 0:
            paste_scaled(fr, gift, W / 2, 1350, 0.6 + 0.4 * pg, clamp(pg * 2))
        return fr
    draw.branded = True  # the watermark goes on the drawn scenes only
    return dur, draw


def bubble(text, mine: bool, max_w=720, size=44, card=None) -> Image.Image:
    f = font(size, 600, BODY)
    words = text.split(" ")
    lines, line = [], ""
    for w in words:
        trial = (line + " " + w).strip()
        if f.getlength(trial) > max_w - 70 and line:
            lines.append(line)
            line = w
        else:
            line = trial
    lines.append(line)
    lh = int(size * 1.3)
    tw = max(f.getlength(l) for l in lines)
    extra_h = 0
    width = int(tw + 70)
    if card is not None:
        width = max(width, card.width + 36)
        extra_h = card.height + 20
    height = int(len(lines) * lh + 52 + extra_h)
    bg = SIGNAL + (255,) if mine else WHITE + (255,)
    fg = WHITE if mine else INK
    im = rounded((width, height), 42, bg)
    d = ImageDraw.Draw(im)
    y = 26
    if card is not None:
        im.alpha_composite(card, (18, 18))
        y = 18 + card.height + 18
    for l in lines:
        d.text((35, y), l, font=f, fill=fg)
        y += lh
    return shadowed(im, blur=16, offset=8, opacity=70)


def link_card(ctx: Ctx) -> Image.Image:
    cw, ch = 640, 190
    card = rounded((cw, ch), 30, (255, 255, 255, 40))
    thumb = cover(ctx.story_img, 150, 150, (0.5, 0.4))
    mask = rounded((150, 150), 22, (255, 255, 255, 255)).getchannel("A")
    card.paste(thumb, (20, 20), mask)
    d = ImageDraw.Draw(card)
    d.text((196, 34), ctx.place["venue"], font=font(42, 800, DISPLAY), fill=WHITE)
    d.text((196, 98), f"socialperkses.com/s/{ctx.name.lower()}", font=font(30, 600, BODY), fill=(225, 222, 255))
    return card


def scene_chat(ctx: Ctx, dur: float):
    kb = KenBurns(ctx.story_img, zoom=(1.05, 1.12), dark=0.62, blur=26)
    friend = ("Bea" if ctx.she else "Álex") if ctx.lang == "es" else ("Bea" if ctx.she else "Alex")
    msgs = [
        (0.25, False, ctx.c["ask"], None),
        (1.45, True, ctx.t(f"{ctx.place['venue']}. Con mi enlace te regalan {ctx.c['gift']}.", f"{ctx.place['venue']}. With my link you get {ctx.c['gift']}."), link_card(ctx)),
        (2.9, False, ctx.t(f"¿Tienen hueco el {ctx.c['wd']}?", f"Any slot on {ctx.c['wd']}?"), None),
        (3.85, True, ctx.t("Sí. Enseñas el código y listo.", "Yes. Show the code, that's it."), None),
    ]
    sprites = [(at, mine, bubble(text, mine, card=card)) for at, mine, text, card in msgs]
    head = Image.new("RGBA", (W, 210), (0, 0, 0, 0))
    hd = ImageDraw.Draw(head)
    hd.ellipse((LEFT, 70, LEFT + 100, 170), fill=PINK)
    fa = font(44, 800, DISPLAY)
    hd.text((LEFT + 50 - fa.getlength(friend[0]) / 2, 93), friend[0], font=fa, fill=WHITE)
    hd.text((LEFT + 128, 76), friend, font=font(46, 800, DISPLAY), fill=WHITE)
    hd.text((LEFT + 128, 132), ctx.t("en línea", "online"), font=font(32, 500, BODY), fill=(210, 210, 222))

    chip = step_chip(2, ctx.t(f"{ctx.name} manda su enlace", f"{ctx.name} sends {'her' if ctx.she else 'his'} link"))

    def draw(t):
        fr = kb.frame(t / dur)
        fr.alpha_composite(head, (0, 150))
        pchip = ease_out(prog(t, 0.0, 0.35))
        paste(fr, chip, LEFT - 28, 390 + (1 - pchip) * 20, pchip)
        # Bubbles stack upwards from the bottom of the safe area.
        shown = [(at, mine, sp) for at, mine, sp in sprites if t >= at]
        y = 1500
        for at, mine, sp in reversed(shown):
            y -= sp.height - 6
            p = ease_back(prog(t, at, 0.35))
            x = W - LEFT - sp.width + 40 if mine else LEFT - 40
            cx, cy = x + sp.width / 2, y + sp.height / 2
            paste_scaled(fr, sp, cx, cy + (1 - p) * 40, 0.85 + 0.15 * p, clamp(p * 2))
        # Typing dots before each reply.
        for at, mine, sp in sprites:
            if at - 0.6 < t < at and t > 0.4:
                dots = rounded((170, 80), 40, (SIGNAL if mine else WHITE) + (235,))
                dd = ImageDraw.Draw(dots)
                for k in range(3):
                    a = 0.5 + 0.5 * math.sin(t * 10 - k * 0.9)
                    base = (255, 255, 255) if mine else (60, 60, 70)
                    mix = tuple(int(b * (0.45 + 0.55 * a) + (SIGNAL if mine else WHITE)[j] * (0.55 - 0.55 * a)) for j, b in enumerate(base))
                    dd.ellipse((40 + k * 34, 28, 64 + k * 34, 52), fill=mix + (255,))
                paste(fr, dots, W - LEFT - 170 if mine else LEFT, 1530)
        return fr
    return dur, draw


def scene_numbers(ctx: Ctx, dur: float):
    pal = ctx.pal
    back = Backdrop(pal)
    rows = [
        (0.15, "1", ctx.t(f"Story de {ctx.name}", f"Story by {ctx.name}"), None),
        (1.05, "3", ctx.t("amigas nuevas" if ctx.she else "amigos nuevos", "new friends through the door"), (0, 3)),
        (1.95, "0 €", ctx.t("en anuncios", "spent on ads"), (300, 0)),
    ]
    big = font(230, 900, DISPLAY)
    labels = [text_sprite(label, 56, 700, BODY, pal["fg"]) for _, _, label, _ in rows]

    def draw(t):
        fr = back.frame(t)
        d = ImageDraw.Draw(fr)
        for i, (at, value, _, count) in enumerate(rows):
            p = ease_out(prog(t, at, 0.45))
            if p <= 0:
                continue
            y = 330 + i * 400
            x = LEFT - (1 - p) * 120
            shown = value
            if count is not None:
                q = ease_out(prog(t, at, 0.8))
                n = round(count[0] + (count[1] - count[0]) * q)
                shown = f"{n} €" if "€" in value else str(n)
            col = pal["acc"] if i == 2 else pal["fg"]
            layer = Image.new("RGBA", (W, 300), (0, 0, 0, 0))
            ImageDraw.Draw(layer).text((0, 0), shown, font=big, fill=col)
            paste(fr, layer, x, y, p)
            paste(fr, labels[i], x + 6, y + 262, p)
        return fr
    draw.branded = True  # the watermark goes on the drawn scenes only
    return dur, draw


def scene_myth(ctx: Ctx, dur: float):
    pal = ctx.alt
    back = Backdrop(pal)
    title = text_sprite(ctx.t("Lo que te venden:", "What they sell you:"), 50, 700, BODY, pal["sub"])
    items = ctx.t("Más anuncios|Más descuentos|Más seguidores", "More ads|More discounts|More followers").split("|")
    sprites = [text_sprite(i, 96, 800, DISPLAY, pal["fg"]) for i in items]
    truth = Words(ctx.t("Lo que funciona: *los amigos de tus clientes*.", "What works: *your clients' friends*."), 104, 72, TEXT_W, 420,
                  color=pal["fg"], hl=pal["hl"], hl_text=pal["hl_text"])

    def draw(t):
        fr = back.frame(t + 5)
        p0 = ease_out(prog(t, 0.0, 0.35))
        paste(fr, title, LEFT, 300, p0)
        for i, sp in enumerate(sprites):
            at = 0.25 + i * 0.5
            p = ease_out(prog(t, at, 0.35))
            y = 420 + i * 150
            paste(fr, sp, LEFT + (1 - p) * 60, y, p * (0.55 if t > 2.4 else 1))
            s = ease_out(prog(t, at + 0.35, 0.3))
            if s > 0:
                d = ImageDraw.Draw(fr)
                d.rectangle((LEFT - 10, y + 60, LEFT - 10 + (sp.width + 20) * s, y + 72), fill=pal["hl"] if pal["hl"] != pal["fg"] else PINK)
        truth.draw(fr, LEFT, 1020, t, start=2.4, stagger=0.07)
        return fr
    draw.branded = True  # the watermark goes on the drawn scenes only
    return dur, draw


def notification(ctx: Ctx, body: str) -> Image.Image:
    nw, nh = W - 2 * 70, 190
    card = rounded((nw, nh), 44, (250, 250, 252, 236))
    card.alpha_composite(mark(84), (32, 32))
    d = ImageDraw.Draw(card)
    d.text((140, 30), "SocialPerks", font=font(34, 800, BODY), fill=INK)
    now = ctx.t("ahora", "now")
    fn = font(30, 500, BODY)
    d.text((nw - 36 - fn.getlength(now), 32), now, font=fn, fill=(120, 120, 130))
    d.text((140, 80), body, font=font(40, 600, BODY), fill=INK)
    return shadowed(card, blur=20, offset=10, opacity=80)


def scene_pov_setup(ctx: Ctx, dur: float):
    # The place, dark and still: the hour nobody comes.
    kb = KenBurns(ImageOps.grayscale(ctx.venue_img).convert("RGB"), zoom=(1.0, 1.1), dark=0.6)
    text = ctx.t(f"*POV:* tienes {ctx.c['place']} y es {ctx.c['wd']} a las {ctx.c['hour']}.",
                 f"*POV:* you run a {ctx.c['place']} and it's {ctx.c['wd']}, {ctx.c['hour']}.")
    words = Words(text, 118, 70, TEXT_W, 700, color=WHITE, hl=PINK, hl_text=WHITE)
    oy = 860 - words.height / 2

    def draw(t):
        fr = kb.frame(t / dur)
        words.draw(fr, LEFT, oy, t, start=0.1, stagger=0.08)
        return fr
    return dur, draw


def scene_pov_phone(ctx: Ctx, dur: float):
    kb = KenBurns(ctx.venue_img, zoom=(1.1, 1.16), dark=0.72, blur=18)
    clock = text_sprite(ctx.c["hour"].replace("pm", ":00").replace("am", ":00").replace("noon", "12:00") if ctx.lang == "en" else ctx.c["hour"], 210, 300, BODY, WHITE)
    day = text_sprite(ctx.c["wd"].capitalize(), 52, 600, BODY, (230, 230, 240))
    friends = ctx.t(f"2 {'amigas' if ctx.she else 'amigos'} de {ctx.name} han reservado", f"2 of {ctx.name}'s friends just booked")
    arrived = ctx.t(f"{'Amiga' if ctx.she else 'Amigo'} de {ctx.name}: {'registrada' if ctx.she else 'registrado'}", f"{ctx.name}'s friend just checked in")
    notes = [
        (0.35, notification(ctx, ctx.t(f"{ctx.name} ha compartido tu enlace", f"{ctx.name} shared your link"))),
        (1.35, notification(ctx, friends)),
        (2.35, notification(ctx, arrived)),
    ]

    def draw(t):
        fr = kb.frame(t / dur)
        paste(fr, day, (W - day.width) / 2, 250)
        paste(fr, clock, (W - clock.width) / 2, 310)
        shake = 0
        for at, _ in notes:
            if at <= t < at + 0.18:
                shake = 8 * math.sin((t - at) * 90)
        y = 720
        for at, sp in notes:
            p = ease_back(prog(t, at, 0.4))
            if p <= 0:
                continue
            paste(fr, sp, (W - sp.width) / 2 + shake, y + (1 - p) * -60, clamp(p * 2))
            y += sp.height - 30
        return fr
    return dur, draw


WEEKDAYS = dict(
    es=["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"],
    en=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
)
LETTERS = dict(es="LMXJVSD", en="MTWTFSS")


def scene_offer(ctx: Ctx, dur: float):
    """Step 1: the week, the one hour that does not fill, and the small gift put on it."""
    pal = ctx.pal
    back = Backdrop(pal)
    chip = step_chip(1, ctx.t("Tu hora floja", "Your quiet hour"))
    words = Words(ctx.t("Eliges la hora que no se llena. *Le pones un regalo pequeño.*",
                        "Pick the hour that never fills. *Put a small gift on it.*"),
                  104, 64, TEXT_W, 400, color=pal["fg"], hl=pal["hl"], hl_text=pal["hl_text"])
    low = WEEKDAYS[ctx.lang].index(ctx.c["wd"]) if ctx.c["wd"] in WEEKDAYS[ctx.lang] else 1
    rng = np.random.default_rng(500 + ctx.ep["seed"])
    week = [int(v) for v in np.clip(np.array([64, 72, 60, 76, 90, 96, 66]) + rng.integers(-8, 9, 7), 40, 99)]
    week[low] = int(18 + rng.integers(0, 10))
    cw = W - 2 * LEFT
    offer_text = ctx.t(f"Activa: {ctx.c['gift']}", f"Live: {ctx.c['gift']}")
    when = f"{ctx.c['wd'][:1].upper() + ctx.c['wd'][1:]} {ctx.c['hour']}"
    fo = font(42, 800, BODY)
    ow = cw - 112
    lines = wrap_lines(offer_text, fo, ow - 150)
    oh = 60 + len(lines) * 54 + 44
    ch = 540 + oh + 44
    base = rounded((cw, ch), 56, WHITE + (255,))
    bd = ImageDraw.Draw(base)
    bd.text((56, 46), ctx.place["venue"], font=font(46, 800, DISPLAY), fill=INK)
    sub = ctx.t("Esta semana", "This week")
    fs = font(34, 600, BODY)
    bd.text((cw - 56 - fs.getlength(sub), 54), sub, font=fs, fill=(120, 120, 132))
    fl = font(34, 700, BODY)
    gap, top, area = 22, 150, 300
    bw = (cw - 112 - gap * 6) / 7
    for i, letter in enumerate(LETTERS[ctx.lang]):
        x = 56 + i * (bw + gap)
        bd.text((x + bw / 2 - fl.getlength(letter) / 2, top + area + 18), letter, font=fl,
                fill=PINK if i == low else (130, 130, 142))
    offer = Image.new("RGBA", (ow, oh), (0, 0, 0, 0))
    grad = np.linspace(0, 1, ow)[None, :, None]
    arr = (np.array(SIGNAL)[None, None, :] * (1 - grad) + np.array(PINK)[None, None, :] * grad).repeat(oh, axis=0)
    fill_im = Image.fromarray(arr.astype(np.uint8), "RGB").convert("RGBA")
    mask = rounded((ow, oh), 40, (255, 255, 255, 255)).getchannel("A")
    offer.paste(fill_im, (0, 0), mask)
    od = ImageDraw.Draw(offer)
    r = 34
    od.ellipse((34, 34, 34 + 2 * r, 34 + 2 * r), fill=(255, 255, 255, 70))
    od.line((34 + r * 0.55, 34 + r, 34 + r * 0.9, 34 + r * 1.4, 34 + r * 1.5, 34 + r * 0.6), fill=WHITE, width=7)
    y = 30
    for line in lines:
        od.text((130, y), line, font=fo, fill=WHITE)
        y += 54
    od.text((130, y + 4), when, font=font(34, 600, BODY), fill=(236, 232, 255))
    offer = shadowed(offer, blur=18, offset=10, opacity=90)
    card_shadow = shadowed(base, blur=30, offset=20, opacity=90)
    pad = (card_shadow.width - cw) // 2
    card_y = 1230 - ch / 2

    def draw(t):
        fr = back.frame(t + 2)
        pchip = ease_out(prog(t, 0.0, 0.35))
        paste(fr, chip, LEFT - 28, 250 + (1 - pchip) * 20, pchip)
        words.draw(fr, LEFT, 380, t, start=0.1, stagger=0.06)
        pc = ease_out(prog(t, 0.55, 0.5))
        if pc <= 0:
            return fr
        card = card_shadow.copy()
        d = ImageDraw.Draw(card)
        for i, value in enumerate(week):
            g = ease_out(prog(t, 0.8 + i * 0.07, 0.5))
            h = area * value / 100 * g
            x = pad + 56 + i * (bw + gap)
            if h < 2:
                continue
            if i == low:
                pulse = 0.5 + 0.5 * math.sin(max(0.0, t - 1.6) * 5) if t > 1.6 else 0
                glow = int(70 + 80 * pulse)
                d.rounded_rectangle((x - 6, pad + top + area - h - 6, x + bw + 6, pad + top + area + 6), 18, fill=(255, 214, 230, glow))
                d.rounded_rectangle((x, pad + top + area - h, x + bw, pad + top + area), 14, fill=PINK + (255,))
            else:
                d.rounded_rectangle((x, pad + top + area - h, x + bw, pad + top + area), 14, fill=(214, 212, 236, 255))
        paste(fr, card, LEFT - pad, card_y - pad + (1 - pc) * 80, pc)
        po = ease_back(prog(t, 2.0, 0.45))
        if po > 0:
            paste_scaled(fr, offer, W / 2, card_y + ch - 44 - oh / 2 + 5, 0.7 + 0.3 * po, clamp(po * 2))
        return fr
    draw.branded = True  # the watermark goes on the drawn scenes only
    return dur, draw


def way_card(ctx: Ctx, story: bool) -> Image.Image:
    cw, ch = W - 2 * LEFT, 290
    card = rounded((cw, ch), 48, WHITE + (255,))
    d = ImageDraw.Draw(card)
    size = 150
    if story:
        badge = ring_gradient(size)
    else:
        badge = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        ImageDraw.Draw(badge).ellipse((0, 0, size - 1, size - 1), fill=(37, 211, 102, 255))
    bdraw = ImageDraw.Draw(badge)
    (camera_glyph if story else chat_glyph)(bdraw, size / 2, size / 2, size * 0.5, WHITE, 8)
    card.alpha_composite(badge, (44, (ch - size) // 2))
    title = "Story" if story else "WhatsApp"
    body = (ctx.t("La ven todos sus seguidores, durante 24 horas.", "All their followers see it, for 24 hours.") if story
            else ctx.t("Solo los amigos que elige, en su chat.", "Only the friends they choose, in a chat."))
    ft = font(58, 800, DISPLAY)
    fb = font(38, 500, BODY)
    lines = wrap_lines(body, fb, cw - 260)
    block = 70 + len(lines) * 50
    y = (ch - block) / 2
    d.text((236, y - 4), title, font=ft, fill=INK)
    y += 76
    for line in lines:
        d.text((236, y), line, font=fb, fill=(88, 88, 100))
        y += 50
    return shadowed(card, blur=26, offset=16, opacity=85)


def scene_two_ways(ctx: Ctx, dur: float):
    """A Story and a message are different things, with the same link: who sees each, and what the friend does."""
    pal = ctx.alt
    back = Backdrop(pal)
    title = Words(ctx.t("Story o mensaje: *el mismo enlace.*", "Story or message: *the same link.*"),
                  110, 72, TEXT_W, 360, color=pal["fg"], hl=pal["hl"], hl_text=pal["hl_text"])
    story, message = way_card(ctx, True), way_card(ctx, False)
    foot = Words(ctx.t("Quien lo abre reserva *tu hora floja* en un toque.", "Whoever opens it books *your quiet hour* in one tap."),
                 62, 44, TEXT_W, 260, weight=700, path=BODY, color=pal["fg"], hl=pal["hl"], hl_text=pal["hl_text"])

    def draw(t):
        fr = back.frame(t + 7)
        title.draw(fr, LEFT, 330, t, start=0.05, stagger=0.06)
        for k, (card, at, side) in enumerate(((story, 0.7, -1), (message, 1.25, 1))):
            p = ease_out(prog(t, at, 0.5))
            if p > 0:
                x = (W - card.width) / 2 + side * (1 - p) * 220
                paste(fr, card, x, 760 + k * 340 - 40, p)
        foot.draw(fr, LEFT, 1500, t, start=2.1, stagger=0.05, style="rise")
        return fr
    draw.branded = False  # the foot line sits where the watermark would
    return dur, draw


def scene_punch(ctx: Ctx, text: str, dur: float, pal=None):
    pal = pal or ctx.alt
    back = Backdrop(pal)
    words = Words(ctx.fill(text), 120, 72, TEXT_W, 760, color=pal["fg"], hl=pal["hl"], hl_text=pal["hl_text"], align="center")
    oy = 880 - words.height / 2

    def draw(t):
        fr = back.frame(t + 9)
        words.draw(fr, LEFT, oy, t, start=0.05, stagger=0.06, style="rise")
        return fr
    draw.branded = True  # the watermark goes on the drawn scenes only
    return dur, draw


def scene_cta(ctx: Ctx, dur: float):
    pal = ctx.pal
    back = Backdrop(pal)
    m = shadowed(mark(240), blur=26, offset=14, opacity=110)
    cta = E.CTA[ctx.lang]
    site = text_sprite(cta["site"], 92, 800, DISPLAY, pal["fg"])
    free = pill(cta["free"], 48, pal["hl_text"], pal["hl"] + (255,), weight=800)
    g = None
    if ctx.ep["guarantee"]:
        g = Words(cta["guarantee"], 48, 38, TEXT_W - 80, 220, weight=600, path=BODY, color=pal["sub"], align="center")

    def draw(t):
        fr = back.frame(t + 13)
        pm = prog(t, 0.0, 0.5)
        paste_scaled(fr, m, W / 2, 640, 0.5 + 0.5 * ease_back(pm), clamp(pm * 2))
        ps = ease_out(prog(t, 0.3, 0.4))
        paste(fr, site, (W - site.width) / 2, 860 + (1 - ps) * 30, ps)
        pf = ease_back(prog(t, 0.6, 0.4))
        if pf > 0:
            paste_scaled(fr, free, W / 2, 1060, 0.6 + 0.4 * pf, clamp(pf * 2))
        if g is not None:
            g.draw(fr, LEFT + 40, 1170, t, start=0.95, stagger=0.03, style="rise")
        return fr
    return dur, draw


def timeline(ctx: Ctx):
    """30 to 34 seconds. The day's format opens it; the middle always explains the
    whole idea in order (the quiet hour, the gift on it, the share, the visit,
    Story or message), so a viewer who knows nothing about SocialPerks gets it."""
    ep = ctx.ep
    hook = ep["hook"][ctx.lang]
    punch = ep["punch"][ctx.lang]
    eyebrow = ctx.t(f"Si tienes {ctx.c['place']}:", f"If you run a {ctx.c['place']}:")
    f = ep["format"]
    problem = scene_pov_setup(ctx, 3.2)
    offer = scene_offer(ctx, 4.6)
    share = scene_chat(ctx, 5.8) if f == "chat" else scene_story(ctx, 3.6)
    visit = scene_friend(ctx, 3.6)
    ways = scene_two_ways(ctx, 4.6)
    spine = [offer, share, visit, ways]
    cta = scene_cta(ctx, 3.4)
    if f == "story":
        return [scene_hook(ctx, hook, eyebrow, 3.0), problem, *spine, scene_numbers(ctx, 4.0), scene_punch(ctx, punch, 2.8), cta]
    if f == "chat":
        return [scene_hook(ctx, hook, eyebrow, 3.0), problem, *spine, scene_punch(ctx, punch, 2.8), cta]
    if f == "numbers":
        return [scene_hook(ctx, hook, eyebrow, 3.0), scene_numbers(ctx, 4.0), problem, *spine, scene_punch(ctx, punch, 2.8), cta]
    if f == "myth":
        return [scene_hook(ctx, hook, eyebrow, 3.0), scene_myth(ctx, 5.0), problem, *spine, cta]
    # pov: the day's hook closes it, before the address.
    return [problem, scene_pov_phone(ctx, 4.6), *spine, scene_punch(ctx, hook, 3.0, pal=ctx.pal), cta]


def watermark(ctx: Ctx) -> Image.Image:
    f = font(34, 800, DISPLAY)
    w = int(80 + f.getlength("SocialPerks") + 28)
    im = rounded((w, 72), 36, (12, 12, 20, 150))
    im.alpha_composite(mark(48), (14, 12))
    ImageDraw.Draw(im).text((74, 14), "SocialPerks", font=f, fill=WHITE)
    return im


def render(ep, lang, out_path, cover_path, cache):
    ctx = Ctx(ep, lang, cache)
    scenes = timeline(ctx)
    total = sum(d for d, _ in scenes)
    frames = int(round(total * FPS))
    wav = out_path[:-4] + ".wav"
    music(ep["seed"], total, wav)
    mk = watermark(ctx)
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
           "-i", wav, "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p", "-profile:v", "high",
           "-c:a", "aac", "-b:a", "160k", "-shortest", "-movflags", "+faststart", out_path]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    starts = []
    acc = 0.0
    for d, _ in scenes:
        starts.append(acc)
        acc += d
    best = None
    for i in range(frames):
        t = i / FPS
        k = max(j for j, s in enumerate(starts) if s <= t + 1e-9)
        local = t - starts[k]
        fr = scenes[k][1](local)
        # A cut lands with a small punch-in, the way edits on these apps do.
        if k > 0 and local < 0.2:
            z = 1 + 0.05 * (1 - ease_out(local / 0.2))
            cw, ch = W / z, H / z
            fr = fr.crop((int((W - cw) / 2), int((H - ch) / 2), int((W + cw) / 2), int((H + ch) / 2))).resize((W, H), Image.BILINEAR)
            flash = int(90 * (1 - local / 0.2))
            if flash > 0:
                fr.alpha_composite(Image.new("RGBA", (W, H), (255, 255, 255, flash)))
        if getattr(scenes[k][1], "branded", False):
            paste(fr, mk, LEFT, H - 250, 0.9)
        rgb = fr.convert("RGB")
        if best is None and k == 0 and local >= min(2.2, scenes[0][0] - 0.3):
            best = rgb.copy()
        proc.stdin.write(rgb.tobytes())
    proc.stdin.close()
    if proc.wait() != 0:
        raise SystemExit(f"ffmpeg failed for {out_path}")
    os.remove(wav)
    (best or rgb).save(cover_path, quality=90)
    return total


# ----------------------------------------------------------------- music

def music(seed: int, dur: float, path: str, sr: int = 44100):
    """A short, bright bed: four chords, kick, offbeat hats, a plucked arpeggio. Different every day."""
    rng = np.random.default_rng(1000 + seed)
    bpm = [104, 110, 116, 122, 98][seed % 5]
    root = 110.0 * 2 ** ([0, 2, 3, 5, 7, 8, 10][seed % 7] / 12)
    progs = [[0, 8, 3, 10], [0, 5, 8, 7], [0, 10, 8, 7], [0, 3, 10, 5]]
    prog_ = progs[seed % len(progs)]
    minor = [0, 3, 7]
    major = [0, 4, 7]
    n = int((dur + 0.4) * sr)
    t = np.arange(n) / sr
    beat = 60 / bpm
    out = np.zeros((n, 2))

    def note(freq, start, length, amp, kind="saw", pan=0.0, decay=6.0):
        i0 = int(start * sr)
        i1 = min(n, i0 + int(length * sr))
        if i0 >= n:
            return
        tt = np.arange(i1 - i0) / sr
        if kind == "sine":
            w = np.sin(2 * np.pi * freq * tt)
        elif kind == "tri":
            w = 2 / np.pi * np.arcsin(np.sin(2 * np.pi * freq * tt))
        else:
            w = sum(np.sin(2 * np.pi * freq * k * tt) / k for k in range(1, 7))
        env = np.exp(-decay * tt) * np.minimum(1, tt / 0.005)
        sig = w * env * amp
        out[i0:i1, 0] += sig * (1 - pan) / 2 * 2
        out[i0:i1, 1] += sig * (1 + pan) / 2 * 2

    bars = int(dur / (4 * beat)) + 2
    for b in range(bars):
        start = b * 4 * beat
        deg = prog_[b % 4]
        quality = minor if deg in (0, 5) else major
        base = root * 2 ** (deg / 12)
        for k in quality:  # pad
            note(base * 2 * 2 ** (k / 12), start, 4 * beat, 0.035, "sine", 0, 0.4)
        for e in range(8):  # bass, eighths
            note(base / 2, start + e * beat / 2, beat / 2, 0.11, "saw", 0, 9)
        arp = [quality[i % 3] + 12 * (i // 3) for i in range(6)]
        rng.shuffle(arp)
        for s16 in range(16):  # pluck
            if rng.random() < 0.7:
                k = arp[s16 % len(arp)]
                note(base * 4 * 2 ** (k / 12), start + s16 * beat / 4, beat / 2, 0.045, "tri", 0.35 if s16 % 2 else -0.35, 14)
    kick_env = np.zeros(n)
    for k in range(int(dur / beat) + 2):
        i0 = int(k * beat * sr)
        if i0 >= n:
            break
        length = int(0.3 * sr)
        tt = np.arange(min(length, n - i0)) / sr
        freq = 45 + 85 * np.exp(-tt * 30)
        phase = 2 * np.pi * np.cumsum(freq) / sr
        kick = np.sin(phase) * np.exp(-tt * 9) * 0.55
        out[i0:i0 + len(tt)] += kick[:, None]
        kick_env[i0:i0 + len(tt)] = np.maximum(kick_env[i0:i0 + len(tt)], np.exp(-tt * 7))
        # offbeat hat
        h0 = i0 + int(beat / 2 * sr)
        if h0 < n:
            hl = min(int(0.05 * sr), n - h0)
            noise = rng.standard_normal(hl)
            noise = np.diff(noise, prepend=0)
            out[h0:h0 + hl] += (noise * np.exp(-np.arange(hl) / sr * 70) * 0.05)[:, None]
    duck = 1 - 0.45 * kick_env
    out *= duck[:, None]
    fade_in = np.minimum(1, t / 0.25)
    fade_out = np.clip((dur - t) / 1.2, 0, 1)
    out *= (fade_in * fade_out)[:, None]
    peak = np.max(np.abs(out)) or 1
    out = out / peak * 0.8
    data = (out * 32767).astype(np.int16)
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes(data.tobytes())


# ----------------------------------------------------------------- caption

def caption(ep) -> str:
    cat = ep["category"]
    out = []
    for lang in ("es", "en"):
        c = E.PLACES[cat][lang]
        hook = E.fill(ep["hook"][lang], cat, lang).replace("*", "")
        punch = E.fill(ep["punch"][lang], cat, lang).replace("*", "")
        cta = E.CTA[lang]
        line = ("Prueba gratis una semana: socialperkses.com" if lang == "es" else "Try it free for a week: socialperkses.com")
        tags = c["tags"] + (" #bocaaboca #marketinglocal #emprendedores" if lang == "es" else " #wordofmouth #localmarketing #entrepreneur")
        parts = [hook, punch, line]
        if ep["guarantee"]:
            parts.insert(2, cta["guarantee"])
        out.append(("ESPAÑOL" if lang == "es" else "ENGLISH") + "\n\n" + "\n\n".join(parts) + "\n\n" + tags)
    return "\n\n-----\n\n".join(out) + "\n"


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--date", default=None, help="YYYY-MM-DD, Europe/Madrid today by default")
    ap.add_argument("--lang", default="es,en")
    ap.add_argument("--out", default=os.path.join(HERE, "out"))
    ap.add_argument("--cache", default=os.path.join(HERE, ".cache"))
    args = ap.parse_args()
    if args.date:
        day = dt.date.fromisoformat(args.date)
    else:
        try:
            from zoneinfo import ZoneInfo
            day = dt.datetime.now(ZoneInfo("Europe/Madrid")).date()
        except Exception:
            day = dt.date.today()
    ep = E.episode(day)
    folder = os.path.join(args.out, ep["date"])
    os.makedirs(folder, exist_ok=True)
    print(f"{ep['date']}: {ep['category']}, {ep['format']}")
    for lang in [x.strip() for x in args.lang.split(",") if x.strip()]:
        video = os.path.join(folder, f"socialperks-{ep['date']}-{lang}.mp4")
        cover_path = os.path.join(folder, f"socialperks-{ep['date']}-{lang}-cover.jpg")
        total = render(ep, lang, video, cover_path, args.cache)
        print(f"  {lang}: {video} ({total:.1f} s, {os.path.getsize(video) / 1e6:.1f} MB)")
    with open(os.path.join(folder, "caption.txt"), "w") as f:
        f.write(caption(ep))
    print(f"  caption: {os.path.join(folder, 'caption.txt')}")


if __name__ == "__main__":
    main()
