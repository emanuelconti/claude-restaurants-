#!/usr/bin/env python3
"""A Good Message Studio reel: a short vertical video made from the shop's own product photos.

    python3 reel.py --date 2026-11-02 --topic reel.json            # writes out/<date>/reel/reel.mp4 and reel.json

The owner (1 November 2026): now and then a reel next to the carousels, made
very well: a hook in the first second, one message per scene on the real
product photos, a slow push on every photo, quick cuts, and the shop at the
end. 1080x1920, 30 fps, H.264 with an original soft beat (no third-party
music, so nothing can be claimed); the trending sound can still be added in
the app later.

The topic file:
{
  "title": "Send this to the friend who needs it today",   # first caption line, never repeated
  "hook": "Send this to the friend who needs it today",    # on screen in the first scene, at most 60 characters
  "lines": ["Be kind, even on the MRT at 8am.", "..."],      # 3 to 5 messages, one per scene, at most 60 characters each
  "photo_urls": ["https://cdn.shopify.com/...", "..."],    # the shop's product photos: one for the hook, one per line
  "caption": "...", "hashtags": "#goodmessagestudio #singapore ..."
}
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import math
import os
import subprocess
import sys
import wave

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import brand as B  # noqa: E402
import carousels as C  # noqa: E402

W, H, FPS = 1080, 1920, 30
HOOK_S, LINE_S, END_S, FADE = 2.4, 2.1, 2.8, 6  # seconds per scene, crossfade frames
SAFE_TOP, SAFE_BOTTOM = 250, 420  # Instagram's own buttons cover the bottom and the top bar


def check(topic: dict) -> list:
    errors = []
    for key, most in (("title", 90), ("hook", 60)):
        if not isinstance(topic.get(key), str) or not topic[key].strip() or len(topic[key]) > most:
            errors.append(f"{key} is missing or longer than {most} characters")
    lines = topic.get("lines")
    if not isinstance(lines, list) or not 3 <= len(lines) <= 5 or any(not isinstance(x, str) or len(x) > 60 for x in lines):
        errors.append("lines must be 3 to 5 messages of at most 60 characters")
        lines = []
    urls = topic.get("photo_urls") or []
    if len(urls) < 1 + len(lines) or any(not str(u).startswith("https://") for u in urls):
        errors.append("photo_urls needs one product photo for the hook and one per line")
    for t in [topic.get("hook", "")] + list(lines):
        if "—" in t or "–" in t:
            errors.append(f"no dashes: {t!r}")
    return errors


def fit_text(text: str, size_max: int, size_min: int, max_w: int, max_lines: int):
    size = size_max
    while True:
        f = B.font(size, 800, B.DISPLAY)
        lines = B.wrap_lines(text, f, max_w)
        if len(lines) <= max_lines or size <= size_min:
            return f, lines
        size -= 4


def text_block(text: str, size_max: int, size_min: int, max_lines: int = 4) -> Image.Image:
    """White bold text on a soft dark plate, centred, ready to paste."""
    f, lines = fit_text(text, size_max, size_min, W - 180, max_lines)
    lh = int(f.size * 1.12)
    w = int(max(f.getlength(l) for l in lines)) + 90
    h = lh * len(lines) + 70
    plate = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(plate)
    d.rounded_rectangle((0, 0, w - 1, h - 1), 36, fill=(15, 18, 20, 150))
    y = 35
    for l in lines:
        d.text((w / 2, y), l, font=f, fill=(255, 255, 255), anchor="ma")
        y += lh
    return plate


def big_photo(url: str, cache: str) -> Image.Image:
    img = B.photo(url, cache)
    if img is None:
        sys.exit(f"photo {url} could not be fetched: nothing rendered (never a reel without its photos)")
    # 12% larger than the frame, so the slow push has room.
    return B.cover(img, int(W * 1.12), int(H * 1.12), (0.5, 0.45))


def frame_from(photo: Image.Image, t: float) -> Image.Image:
    """A slow push-in: from 1.12x down to 1.0x crop window, eased."""
    k = 1 - (1 - t) ** 2
    scale = 1.0 + 0.10 * k
    cw, ch = int(photo.width / scale), int(photo.height / scale)
    x, y = (photo.width - cw) // 2, (photo.height - ch) // 2
    return photo.crop((x, y, x + cw, y + ch)).resize((W, H), Image.BILINEAR)


def shade(img: Image.Image) -> Image.Image:
    g = np.linspace(0, 1, H)[:, None]
    a = (np.clip((g - 0.55) / 0.45, 0, 1) ** 1.5 * 150 + np.clip((0.18 - g) / 0.18, 0, 1) * 90).astype(np.uint8)
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    overlay.putalpha(Image.fromarray(np.repeat(a, W, axis=1), "L"))
    out = img.convert("RGBA")
    out.alpha_composite(overlay)
    return out


def scene_frames(photo: Image.Image, text: str, seconds: float, hook: bool) -> list:
    n = int(seconds * FPS)
    block = text_block(text, 92 if hook else 80, 56, 5 if hook else 4)
    frames = []
    for i in range(n):
        t = i / max(n - 1, 1)
        fr = shade(frame_from(photo, t))
        appear = min(1.0, i / 7)  # the text lands fast: inside a quarter of a second
        rise = int((1 - (1 - appear) ** 3) * 40)
        y = SAFE_TOP + 90 - rise + 40  # top third: the printed message on the product stays visible
        layer = block.copy()
        if appear < 1:
            layer.putalpha(layer.getchannel("A").point(lambda v: int(v * appear)))
        fr.alpha_composite(layer, ((W - block.width) // 2, min(y, H - SAFE_BOTTOM - block.height)))
        frames.append(fr.convert("RGB"))
    return frames


def end_frames(seconds: float) -> list:
    n = int(seconds * FPS)
    base = Image.new("RGBA", (W, H), B.INK + (255,))
    d = ImageDraw.Draw(base)
    tile = B.rounded((210, 210), 54, (255, 255, 255, 255))
    tile.alpha_composite(B.mark(160), (25, 25))
    base.alpha_composite(tile, ((W - 210) // 2, 520))
    f = B.font(104, 800, B.DISPLAY)
    d.text((W / 2, 820), "Wear the message.", font=f, fill=(255, 255, 255), anchor="ma")
    sf = B.font(46, 500, B.BODY)
    d.text((W / 2, 975), "Hoodies and tees with one kind line.", font=sf, fill=(205, 205, 214), anchor="ma")
    pill = B.pill(C.STORE_URL, 54, B.WHITE, B.SIGNAL + (255,), weight=800)
    base.alpha_composite(pill, ((W - pill.width) // 2, 1080))
    hf = B.font(44, 700, B.BODY)
    d.text((W / 2, 1240), C.FOLLOW["handle"], font=hf, fill=(255, 255, 255), anchor="ma")
    frames = []
    for i in range(n):
        s = 1.0 + 0.03 * (i / max(n - 1, 1))
        fr = base.resize((int(W * s), int(H * s)), Image.BILINEAR)
        x, y = (fr.width - W) // 2, (fr.height - H) // 2
        frames.append(fr.crop((x, y, x + W, y + H)).convert("RGB"))
    return frames


def crossfade(a: list, b: list) -> list:
    if not a:
        return b
    out = a[:-FADE]
    for i in range(FADE):
        out.append(Image.blend(a[len(a) - FADE + i], b[i], (i + 1) / (FADE + 1)))
    return out + b[FADE:]


def soft_beat(seconds: float, path: str, sr: int = 44100) -> None:
    """An original warm beat: a slow major-seventh pad, a soft kick on every beat at 96 BPM, a light shaker."""
    t = np.arange(int(seconds * sr)) / sr
    bpm = 96
    beat = 60 / bpm
    chords = [[261.63, 329.63, 392.0, 493.88], [220.0, 261.63, 329.63, 392.0], [174.61, 220.0, 261.63, 329.63], [196.0, 246.94, 293.66, 392.0]]
    pad = np.zeros_like(t)
    for k, ch in enumerate(chords * 4):
        start, end = k * 4 * beat, (k + 1) * 4 * beat
        m = (t >= start) & (t < end)
        env = np.clip((t[m] - start) / 0.4, 0, 1) * np.clip((end - t[m]) / 0.4, 0, 1)
        for f in ch:
            pad[m] += env * (np.sin(2 * np.pi * f * t[m]) + 0.3 * np.sin(2 * np.pi * f * 2 * t[m])) / len(ch)
    kick = np.zeros_like(t)
    shaker = np.zeros_like(t)
    rng = np.random.default_rng(7)
    for k in range(int(seconds / beat) + 1):
        s = k * beat
        m = (t >= s) & (t < s + 0.25)
        tt = t[m] - s
        kick[m] += np.sin(2 * np.pi * (55 + 90 * np.exp(-tt * 30)) * tt) * np.exp(-tt * 12)
        s2 = s + beat / 2
        m2 = (t >= s2) & (t < s2 + 0.05)
        shaker[m2] += rng.standard_normal(m2.sum()) * np.exp(-(t[m2] - s2) * 80)
    mix = 0.45 * pad + 0.55 * kick + 0.06 * shaker
    fade = np.clip(t / 0.6, 0, 1) * np.clip((seconds - t) / 1.2, 0, 1)
    mix = mix * fade
    mix = mix / (np.abs(mix).max() + 1e-9) * 0.6
    data = (mix * 32767).astype(np.int16)
    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes(data.tobytes())


def render(date: dt.date, topic: dict, out: str, cache: str) -> dict:
    folder = os.path.join(out, date.isoformat(), "reel")
    os.makedirs(folder, exist_ok=True)
    urls = topic["photo_urls"]
    frames = scene_frames(big_photo(urls[0], cache), topic["hook"], HOOK_S, True)
    for url, line in zip(urls[1:], topic["lines"]):
        frames = crossfade(frames, scene_frames(big_photo(url, cache), line, LINE_S, False))
    frames = crossfade(frames, end_frames(END_S))
    seconds = len(frames) / FPS
    wav = os.path.join(folder, "beat.wav")
    soft_beat(seconds, wav)
    mp4 = os.path.join(folder, "reel.mp4")
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
           "-i", wav, "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", "-profile:v", "high",
           "-c:a", "aac", "-b:a", "160k", "-shortest", "-movflags", "+faststart", mp4]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for fr in frames:
        proc.stdin.write(fr.tobytes())
    proc.stdin.close()
    if proc.wait() != 0:
        sys.exit("ffmpeg failed: nothing written")
    frames[len(frames) // 8].save(os.path.join(folder, "cover.jpg"), quality=90)
    caption = f"{topic['title']}\n\n{(topic.get('caption') or '').strip()}\n\n{C.CAPTION_SHARE}\n\n{topic.get('hashtags') or C.HASHTAGS}".replace("\n\n\n\n", "\n\n")
    meta = dict(date=date.isoformat(), title=topic["title"], video="reel.mp4", seconds=round(seconds, 1), caption=caption)
    json.dump(meta, open(os.path.join(folder, "reel.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    return dict(meta, folder=folder)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--date", required=True)
    ap.add_argument("--topic", required=True)
    ap.add_argument("--out", default=os.path.join(HERE, "out"))
    ap.add_argument("--cache", default=os.path.join(HERE, ".cache"))
    args = ap.parse_args()
    topic = json.load(open(args.topic, encoding="utf-8"))
    errors = check(topic)
    if errors:
        sys.exit("the reel topic needs fixing:\n- " + "\n- ".join(errors))
    meta = render(dt.date.fromisoformat(args.date), topic, args.out, args.cache)
    print(f"{meta['date']}: {meta['title']} ({meta['seconds']} s)\n  {os.path.join(meta['folder'], 'reel.mp4')}")


if __name__ == "__main__":
    main()
