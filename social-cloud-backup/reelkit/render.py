#!/usr/bin/env python3
"""Render reviewed Instagram/Facebook Reels for any brand (editor tool, never run by the publisher).

    python reelkit/render.py --brand sp --ids sp-2026-11-07-3,sp-2026-11-07-7 --cache /tmp/rk

Owner brief (5 November 2026): a hook readable in the first frame, one idea per
scene, full-bleed photos that match each scene with slow motion, bold kinetic
text, quick cuts, a clean end card, 1080x1920 at 30 fps, 15-30 seconds and an
original audible music track from the brand's existing beat generator (never
third-party music, never silent).

Photos: SocialPerks and Sincronia reels reuse exactly the Unsplash photographs
already visually approved on the same topic's slides (identified by pixel
matching in match_photos.py, ambiguous matches stop the render). Good Message
Studio reels use only real message-hoodie photos from goodmessagestudio.com.

Each brand runs in its own process because the brand folders share module
names (brand.py, carousels.py).
"""
from __future__ import annotations

import argparse, ast, hashlib, json, math, os, subprocess, sys, urllib.request, wave
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
import topics as T  # noqa: E402

W, H, FPS = 1080, 1920, 30
HOOK_S, POINT_S, END_S = 2.2, 2.6, 2.8
SAFE_TOP, SAFE_BOTTOM, SIDE = 230, 430, 84
PUNCH = 4  # frames of zoom punch at every hard cut

# Real message-hoodie photos with the printed message visible (GMS brief), checked 5 November 2026.
GMS_PHOTOS = [
    ("https://cdn.shopify.com/s/files/1/1038/5401/4799/files/gm-boat-back.jpg", "Enjoy The Little Things Hoodie"),
    ("https://cdn.shopify.com/s/files/1/1038/5401/4799/files/0326d32f-3a56-4329-bc0e-de51267574a9.jpg", "Be Kind Rainbow Hoodie"),
    ("https://cdn.shopify.com/s/files/1/1038/5401/4799/files/fab40257-cce2-49d3-89a5-dabddcf67fdb.jpg", "Do What Makes You Happy Hoodie"),
    ("https://cdn.shopify.com/s/files/1/1038/5401/4799/files/gm-back.jpg", "Enjoy The Little Things Hoodie"),
    ("https://cdn.shopify.com/s/files/1/1038/5401/4799/files/cca0712a-b748-49ee-abf9-976097c16398.jpg", "Be Kind Rainbow Hoodie"),
]


# ---------------------------------------------------------------- brand setup
class Brand:
    def __init__(self, name):
        self.name = name
        folder = ROOT / 'publishers' / name
        sys.path.insert(0, str(folder))
        os.chdir(folder)
        if name == 'sp':
            import daily as D
            import carousel as K
            self.font = lambda s, w=800: D.font(s, w, D.DISPLAY if w >= 600 else D.BODY)
            self.mark, self.accent, self.ink, self.label = D.mark, D.YELLOW, D.INK, 'SOCIALPERKS'
            self.accent_ink = D.INK
            self.end_slide = K.slide_follow
            self.music = lambda seed, dur, path, cuts: D.music(seed, dur, path, cuts=cuts)
            self.music_name = 'publishers/sp/daily.py music() original dembow/latin beat'
        elif name == 'sin':
            import brand as B
            import carousel as K
            self.font = lambda s, w=800: B.font(s, w, B.DISPLAY if w >= 600 else B.BODY)
            self.mark, self.accent, self.ink, self.label = B.mark, B.BRASS, B.INK, 'SINCRONIA'
            self.accent_ink = B.WHITE
            self.end_slide = K.slide_follow
            self.music = lambda seed, dur, path, cuts: soft_beat()(dur, path)
            self.music_name = 'publishers/gms/reel.py soft_beat() original warm beat'
        else:
            import brand as B
            import reel as R
            self.font = lambda s, w=800: B.font(s, 400, B.SERIF) if w >= 600 else B.font(s, w, B.BODY)
            self.mark, self.accent, self.ink, self.label = B.mark, B.SIGNAL, B.INK, 'GOOD MESSAGE STUDIO'
            self.accent_ink = B.WHITE
            self.end_slide = lambda: R.end_frames(1 / FPS)[0]
            self.music = lambda seed, dur, path, cuts: R.soft_beat(dur, path)
            self.music_name = 'publishers/gms/reel.py soft_beat() original warm beat'


def soft_beat():
    src = (ROOT / 'publishers/gms/reel.py').read_text()
    node = next(n for n in ast.parse(src).body if isinstance(n, ast.FunctionDef) and n.name == 'soft_beat')
    scope = {'np': np, 'wave': wave}
    exec(compile(ast.Module(body=[node], type_ignores=[]), 'soft_beat', 'exec'), scope)
    return scope['soft_beat']


# ---------------------------------------------------------------- photos
def fetch(url, cache: Path):
    cache.mkdir(parents=True, exist_ok=True)
    path = cache / (hashlib.sha1(url.encode()).hexdigest() + '.jpg')
    if not path.exists() or path.stat().st_size < 5000:
        with urllib.request.urlopen(url, timeout=90) as r:
            path.write_bytes(r.read())
    return Image.open(path).convert('RGB')


def unsplash(pid, cache):
    return fetch(f'https://images.unsplash.com/photo-{pid}?h=2400&q=85&fm=jpg', cache / 'hires')


def prepare_product(img, zoom=1.14):
    """GMS: the whole real garment print stays visible in the lower part of the frame, over a
    full-bleed blurred backdrop of the same product photo; the text owns the top."""
    bw, bh = int(W * zoom), int(H * zoom)
    r = max(bw / img.width, bh / img.height)
    back = img.resize((math.ceil(img.width * r), math.ceil(img.height * r)), Image.BILINEAR)
    x, y = (back.width - bw) // 2, (back.height - bh) // 2
    back = back.crop((x, y, x + bw, y + bh)).filter(ImageFilter.GaussianBlur(44))
    back = Image.blend(back, Image.new('RGB', back.size, (0, 0, 0)), 0.30)
    fw = int(880 * zoom)
    fg = img.resize((fw, int(img.height * fw / img.width)), Image.LANCZOS)
    mask = Image.new('L', fg.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, fg.width - 1, fg.height - 1), 40, fill=255)
    back.paste(fg, ((bw - fw) // 2, int(850 * zoom)), mask)
    return back


def prepare(img, zoom=1.14):
    """A frame-filling version with room for slow motion. Low-resolution squares get a
    blurred full-bleed backdrop of the same photo instead of being blown up."""
    bw, bh = int(W * zoom), int(H * zoom)
    r = max(bw / img.width, bh / img.height)
    if r <= 1.6:
        im = img.resize((math.ceil(img.width * r), math.ceil(img.height * r)), Image.LANCZOS)
        x, y = (im.width - bw) // 2, (im.height - bh) // 2
        return im.crop((x, y, x + bw, y + bh))
    back = img.resize((math.ceil(img.width * r), math.ceil(img.height * r)), Image.BILINEAR)
    x, y = (back.width - bw) // 2, (back.height - bh) // 2
    back = back.crop((x, y, x + bw, y + bh)).filter(ImageFilter.GaussianBlur(40))
    back = Image.blend(back, Image.new('RGB', back.size, (0, 0, 0)), 0.35)
    fg = img.resize((bw, int(img.height * bw / img.width)), Image.LANCZOS)
    back.paste(fg, (0, (bh - fg.height) // 2 + int(bh * 0.06)))
    return back


def motion(photo, t, direction, punch=0.0):
    """Slow zoom with a gentle drift; punch adds a short zoom-in at a hard cut."""
    k = t * t * (3 - 2 * t)
    scale = 1.0 + 0.11 * k + punch
    cw, ch = int(photo.width / scale), int(photo.height / scale)
    span = photo.width - cw
    x = int(span / 2 + direction * span * 0.35 * (k - 0.5))
    y = (photo.height - ch) // 2
    return photo.crop((x, y, x + cw, y + ch)).resize((W, H), Image.BILINEAR)


# ---------------------------------------------------------------- text
def wrap(text, f, width):
    words, lines, line = text.split(), [], ''
    for w in words:
        cand = (line + ' ' + w).strip()
        if f.getlength(cand) > width and line:
            lines.append(line)
            line = w
        else:
            line = cand
    lines.append(line)
    if len(lines) >= 2 and len(lines[-1].split()) == 1 and len(lines[-2].split()) > 2:
        prev = lines[-2].split()
        lines[-2], lines[-1] = ' '.join(prev[:-1]), prev[-1] + ' ' + lines[-1]
    return lines


def fit(brand, text, big, small, width, max_lines, weight=800):
    size = big
    while True:
        f = brand.font(size, weight)
        lines = wrap(text, f, width)
        if (len(lines) <= max_lines and all(f.getlength(l) <= width for l in lines)) or size <= small:
            return f, lines
        size -= 4


def text_layer(brand, lines, f, colour=(255, 255, 255), lead=1.1, shadow=True):
    lh = int(f.size * lead)
    w = int(max(f.getlength(l) for l in lines)) + 60
    h = lh * len(lines) + 50
    layers = []
    for k, line in enumerate(lines):
        layer = Image.new('RGBA', (w, lh + 50), (0, 0, 0, 0))
        if shadow:
            sh = Image.new('RGBA', layer.size, (0, 0, 0, 0))
            ImageDraw.Draw(sh).text((w / 2, 25 + 4), line, font=f, fill=(0, 0, 0, 200), anchor='ma')
            layer.alpha_composite(sh.filter(ImageFilter.GaussianBlur(9)))
        ImageDraw.Draw(layer).text((w / 2, 25), line, font=f, fill=colour, anchor='ma')
        layers.append(layer)
    return layers, lh, w, h


def kinetic(frame, layers, lh, x0, y0, i, start, stagger=3, ramp=5, rise=48):
    """Each line slides up and fades in quickly, staggered; fully set after a few frames."""
    for k, layer in enumerate(layers):
        a = max(0.0, min(1.0, (i - start - k * stagger) / ramp))
        if a <= 0:
            continue
        ly = layer if a >= 1 else _alpha(layer, a)
        frame.alpha_composite(ly, (x0 - layer.width // 2, int(y0 + k * lh + (1 - a) ** 2 * rise)))


def _alpha(layer, a):
    out = layer.copy()
    out.putalpha(out.getchannel('A').point(lambda v: int(v * a)))
    return out


def gradient(top_alpha, bottom_alpha, top_end=0.55, bottom_start=0.62):
    g = np.linspace(0, 1, H)[:, None]
    a = (np.clip((top_end - g) / top_end, 0, 1) ** 0.85 * top_alpha
         + np.clip((g - bottom_start) / (1 - bottom_start), 0, 1) ** 1.4 * bottom_alpha).astype(np.uint8)
    ov = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    ov.putalpha(Image.fromarray(np.repeat(a, W, axis=1), 'L'))
    return ov


def brand_row(brand, frame, y, colour=(255, 255, 255)):
    m = brand.mark(54)
    f = brand.font(28, 800) if brand.name != 'gms' else brand.font(28, 600)
    tw = f.getlength(brand.label)
    x = int((W - (54 + 16 + tw)) / 2)
    frame.alpha_composite(m, (x, y))
    ImageDraw.Draw(frame).text((x + 70, y + 27), brand.label, font=f, fill=colour, anchor='lm')


# ---------------------------------------------------------------- scenes
def scene_hook(brand, photo, title, n):
    f, lines = fit(brand, title, 116, 72, W - 2 * SIDE, 4 if brand.name != 'gms' else 3)
    layers, lh, w, h = text_layer(brand, lines, f)
    if brand.name == 'gms':
        shade = gradient(235, 60, 0.45, 0.85)
        y0 = SAFE_TOP + 110
    else:
        shade = gradient(110, 235, 0.35, 0.30)
        y0 = H - SAFE_BOTTOM - len(lines) * lh - 40
    for i in range(n):
        fr = motion(photo, i / max(n - 1, 1), 1).convert('RGBA')
        fr.alpha_composite(shade)
        brand_row(brand, fr, y0 - 110 if brand.name != 'gms' else SAFE_TOP + 10)
        # Readable in the very first frame: lines start fully set, with a slight settle.
        s = 1.0 + 0.05 * max(0.0, 1 - i / 8)
        for k, layer in enumerate(layers):
            ly = layer if s == 1.0 else layer.resize((int(layer.width * s), int(layer.height * s)), Image.BILINEAR)
            fr.alpha_composite(ly, (W // 2 - ly.width // 2, int(y0 + k * lh - (ly.height - layer.height) / 2)))
        yield fr.convert('RGB')


def scene_point(brand, photo, number, total, heading, body, n, direction):
    hf, hlines = fit(brand, heading, 104, 60, W - 2 * SIDE, 3 if brand.name != 'gms' else 2)
    bf, blines = fit(brand, body, 56, 42, W - 2 * SIDE - 20, 3, 500)
    hl, hlh, _, hh = text_layer(brand, hlines, hf)
    bl, blh, _, bh = text_layer(brand, blines, bf, (240, 240, 240), 1.25)
    pf = brand.font(40, 800) if brand.name != 'gms' else brand.font(40, 500)
    label = f'{number}/{total}'
    pw = int(pf.getlength(label)) + 56
    pill = Image.new('RGBA', (pw, 74), (0, 0, 0, 0))
    ImageDraw.Draw(pill).rounded_rectangle((0, 0, pw - 1, 73), 37, fill=brand.accent + (255,))
    ImageDraw.Draw(pill).text((pw / 2, 37), label, font=pf, fill=brand.accent_ink, anchor='mm')
    shade = gradient(240, 110, 0.66, 0.72)
    y_pill = SAFE_TOP + 40
    y_head = y_pill + 110
    y_body = y_head + len(hlines) * hlh + 10
    for i in range(n):
        punch = 0.06 * max(0.0, 1 - i / PUNCH)
        fr = motion(photo, i / max(n - 1, 1), direction, punch).convert('RGBA')
        fr.alpha_composite(shade)
        a = min(1.0, (i + 1) / 4)
        fr.alpha_composite(pill if a >= 1 else _alpha(pill, a), ((W - pw) // 2, y_pill))
        kinetic(fr, hl, hlh, W // 2, y_head, i, 2)
        kinetic(fr, bl, blh, W // 2, y_body, i, 9 + 3 * len(hlines), stagger=2, ramp=6, rise=30)
        yield fr.convert('RGB')


def scene_end(brand, n):
    slide = brand.end_slide().convert('RGB')
    if slide.size == (W, H):
        base = slide
    else:
        base = Image.new('RGB', (W, H), slide.getpixel((5, 5)))
        base.paste(slide, (0, (H - slide.height) // 2 - 60))
    for i in range(n):
        s = 1.0 + 0.03 * (i / max(n - 1, 1)) + 0.04 * max(0.0, 1 - i / PUNCH)
        fr = base.resize((int(W * s), int(H * s)), Image.BILINEAR)
        x, y = (fr.width - W) // 2, (fr.height - H) // 2
        yield fr.crop((x, y, x + W, y + H))


# ---------------------------------------------------------------- render
RECENT = []

def render(brand, item, cache: Path, matcher=None):
    car = ROOT / item['folder']
    meta = json.loads((car / 'carousel.json').read_text())
    topic = T.topic(item['brand'], item['date'], item['title'])
    if not topic or len(topic['points']) != 5:
        raise SystemExit(f"{item['id']}: reviewed topic text not found")
    sources = []
    if brand.name == 'gms':
        day = int(item['date'][-2:])
        # Owner, 6 November: four Reels a day. The extra Reels (publish_order 1 and 6) start
        # further along the same reviewed hoodie photos so a day's Reels never repeat one order;
        # the existing lunch/evening Reels keep their original order.
        shift = {1: 2, 6: 4}.get(item.get('publish_order', item['slot']), 0)
        picks = [GMS_PHOTOS[(day + shift + k) % len(GMS_PHOTOS)] for k in range(6)]
        photos = [fetch(u, cache / 'gms') for u, _ in picks]
        sources = [dict(url=u, product=p) for u, p in picks]
    else:
        slides = [Image.open(car / f'slide-0{k}.jpg').convert('RGB') for k in range(1, 7)]
        found = [matcher.cover_id(slides[0])] + [matcher.point_id(s) for s in slides[1:]]
        for pid, best, second in found:
            if not (best < 4.0 and second > 3 * best + 4):
                raise SystemExit(f"{item['id']}: ambiguous photo match {pid} {best:.2f}/{second:.2f}; not rendered")
        # Variety: the reviewed carousels reuse photos across days. A photo already used by the
        # brand's previous two reels is swapped for an unused one from the same topic photo set.
        import carousels as CS
        pool = list(CS.PHOTO_SETS.get(topic.get('set') or '', []))
        recent = set(p for reel in RECENT[-2:] for p in reel)
        ids, sources = [], []
        for k, (pid, best, second) in enumerate(found):
            src = dict(unsplash=pid, slide=f'slide-0{k + 1}.jpg', match_error=round(best, 2), runner_up=round(second, 2))
            if pid in recent or pid in ids:
                spare = [p for p in pool if p not in recent and p not in ids and p not in [f[0] for f in found]]
                if spare:
                    src = dict(unsplash=spare[0], replaces=pid, reason=f"variety: same '{topic.get('set')}' photo set as the reviewed slide")
                    pid = spare[0]
            ids.append(pid)
            sources.append(src)
        RECENT.append(ids)
        photos = [unsplash(pid, cache) for pid in ids]
    prepared = [prepare_product(p) if brand.name == 'gms' else prepare(p) for p in photos]
    folder = ROOT / 'queue' / item['brand'] / item['date'] / f"reel-{item['slot']}"
    folder.mkdir(parents=True, exist_ok=True)
    n_hook, n_point, n_end = int(HOOK_S * FPS), int(POINT_S * FPS), int(END_S * FPS)
    total = n_hook + 5 * n_point + n_end
    seconds = total / FPS
    cuts = [HOOK_S + k * POINT_S for k in range(6)]
    wav = folder / 'music.wav'
    seed = int(hashlib.sha256(item['id'].encode()).hexdigest()[:6], 16) % 997
    brand.music(seed, seconds, str(wav), cuts)
    mp4 = folder / 'reel.mp4'
    cmd = ['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
           '-i', str(wav), '-map', '0:v', '-map', '1:a', '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-pix_fmt', 'yuv420p',
           '-profile:v', 'high', '-g', '60', '-keyint_min', '60', '-sc_threshold', '0', '-r', str(FPS),
           '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', '-ac', '2', '-t', f'{seconds:.3f}', '-movflags', '+faststart', str(mp4)]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    samples, idx = {}, 0
    def emit(frames, tag):
        nonlocal idx
        for j, fr in enumerate(frames):
            if j in (2, n_point // 2) or (tag == 'hook' and j == 15):
                samples[f'{tag}-{j}'] = fr.copy()
            proc.stdin.write(fr.tobytes())
            idx += 1
    hook_frames = list(scene_hook(brand, prepared[0], topic['title'], n_hook))
    cover = hook_frames[15]
    first = hook_frames[0]
    emit(hook_frames, 'hook')
    for k, (heading, body, _punch) in enumerate(topic['points']):
        emit(scene_point(brand, prepared[k + 1], k + 1, 5, heading, body, n_point, 1 if k % 2 else -1), f'p{k + 1}')
    emit(scene_end(brand, n_end), 'end')
    proc.stdin.close()
    if proc.wait() != 0:
        raise SystemExit('ffmpeg failed')
    wav.unlink()
    cover.save(folder / 'cover.jpg', quality=92)
    reel = dict(date=item['date'], title=item['title'], video='reel.mp4', cover='cover.jpg', seconds=round(seconds, 2),
                caption=meta['caption'] if brand.name != 'gms' else gms_caption(item, meta),
                music=brand.music_name + ', seed %d (original, rights-cleared, generated in code)' % seed,
                photos=sources, scenes=['hook'] + [p[0] for p in topic['points']] + ['end card'])
    (folder / 'reel.json').write_text(json.dumps(reel, ensure_ascii=False, indent=1))
    # Contact sheet of every scene for visual review.
    keys = ['hook-0', 'hook-15'] + [f'p{k}-{j}' for k in range(1, 6) for j in (2, n_point // 2)] + ['end-2', f'end-{n_point // 2}']
    samples['hook-0'] = first
    ims = [samples[k] for k in keys if k in samples]
    sheet = Image.new('RGB', (270 * 7, 480 * math.ceil(len(ims) / 7)), 'white')
    for k, im in enumerate(ims):
        sheet.paste(im.resize((270, 480)), ((k % 7) * 270, (k // 7) * 480))
    return folder, sheet, reel


def gms_caption(item, meta):
    # Keep the reviewed carousel caption: its first line is the exact title used for dedupe.
    return meta['caption']


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--brand', required=True, choices=['sp', 'sin', 'gms'])
    ap.add_argument('--ids', required=True)
    ap.add_argument('--cache', required=True)
    ap.add_argument('--sheets', required=True)
    args = ap.parse_args()
    queue = json.loads((ROOT / 'queue.json').read_text())
    wanted = args.ids.split(',')
    items = [next(x for x in queue if x['id'] == i) for i in wanted]
    cache = Path(args.cache)
    brand = Brand(args.brand)
    matcher = None
    if args.brand != 'gms':
        import match_photos as M
        matcher = M.Matcher(cache / 'match')
    Path(args.sheets).mkdir(parents=True, exist_ok=True)
    for item in items:
        folder, sheet, reel = render(brand, item, cache, matcher)
        sheet.save(Path(args.sheets) / f"{item['id']}.jpg", quality=85)
        print(item['id'], folder, reel['seconds'], [p.get('unsplash') or p.get('product') for p in reel['photos']], flush=True)


if __name__ == '__main__':
    main()
