#!/usr/bin/env python3
"""Modern Facebook photo-post slides for Good Message Studio (owner, 6 November 2026: the pastel serif
cards look dated). Editor tool, never run by the publisher.

    python reelkit/fb_modern.py --ids gms-2026-11-06-4,... --cache /tmp/rk --sheets /tmp/rk/fb

Writes fb-01.jpg ... fb-07.jpg (1080x1350) next to the reviewed carousel and lists them in
carousel.json as facebook_slides (Instagram keeps its own slides). Real message-hoodie photos only,
the whole print visible; bold sans type; one idea per slide; a clear shop end card.
"""
import argparse, json, math, os, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
import topics as T  # noqa: E402
import render as R  # noqa: E402

W, H = 1080, 1350
PINK = (200, 26, 92)
INK = (16, 18, 22)
WHITE = (255, 255, 255)
SOFT = (196, 200, 208)


def font(size, weight=800, body=False):
    from PIL import ImageFont
    f = ImageFont.truetype(str(ROOT / 'publishers/gms/fonts' / ('Inter-latin.ttf' if body else 'InterTight-latin.ttf')), size)
    try:
        f.set_variation_by_axes([weight])
    except Exception:
        pass
    return f


def wrap(text, f, width):
    return R.wrap(text, f, width)


def fit(text, big, small, width, lines_max, weight=800, body=False):
    s = big
    while True:
        f = font(s, weight, body)
        lines = wrap(text, f, width)
        if (len(lines) <= lines_max and all(f.getlength(l) <= width for l in lines)) or s <= small:
            return f, lines
        s -= 4


def backdrop(photo):
    r = max(W / photo.width, H / photo.height)
    b = photo.resize((math.ceil(photo.width * r), math.ceil(photo.height * r)), Image.BILINEAR)
    x, y = (b.width - W) // 2, (b.height - H) // 2
    b = b.crop((x, y, x + W, y + H)).filter(ImageFilter.GaussianBlur(50))
    return Image.blend(b, Image.new('RGB', (W, H), INK), 0.62)


def product(photo, size, radius=36):
    p = photo.resize((size, int(photo.height * size / photo.width)), Image.LANCZOS)
    m = Image.new('L', p.size, 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, p.width - 1, p.height - 1), radius, fill=255)
    out = Image.new('RGBA', p.size)
    out.paste(p, (0, 0), m)
    return out


def label(img, y, text='GOOD MESSAGE STUDIO'):
    d = ImageDraw.Draw(img)
    d.rectangle((72, y, 72 + 44, y + 8), fill=PINK)
    d.text((72 + 60, y + 4), text, font=font(26, 700, True), fill=WHITE, anchor='lm')


def cover(photo, title):
    img = backdrop(photo).convert('RGBA')
    p = product(photo, 760)
    img.alpha_composite(p, ((W - p.width) // 2, 70))
    g = Image.new('L', (1, H))
    for y in range(H):
        g.putpixel((0, y), int(max(0, min(1, (y - 640) / 380)) ** 1.2 * 245))
    shade = Image.new('RGBA', (W, H), INK + (0,))
    shade.putalpha(g.resize((W, H)))
    img.alpha_composite(shade)
    f, lines = fit(title, 92, 60, W - 144, 3)
    lh = int(f.size * 1.05)
    y = H - 90 - lh * len(lines)
    label(img, y - 70)
    d = ImageDraw.Draw(img)
    for k, l in enumerate(lines):
        d.text((72, y + k * lh), l, font=f, fill=WHITE)
    return img.convert('RGB')


def point(photo, n, heading, body):
    img = backdrop(photo).convert('RGBA')
    d = ImageDraw.Draw(img)
    d.text((72, 70), f'{n:02d}', font=font(120, 800), fill=PINK)
    hf, hl = fit(heading, 104, 64, W - 144, 2)
    y = 220
    for l in hl:
        d.text((72, y), l, font=hf, fill=WHITE)
        y += int(hf.size * 1.08)
    bf, bl = fit(body, 46, 36, W - 144, 2, 450, True)
    y += 14
    for l in bl:
        d.text((72, y), l, font=bf, fill=SOFT)
        y += int(bf.size * 1.35)
    top = max(y + 36, 520)
    size = min(W - 144, H - 60 - top)
    p = product(photo, size)
    if p.height > H - 60 - top:
        p = p.crop((0, 0, p.width, H - 60 - top))
    img.alpha_composite(p, ((W - p.width) // 2, top))
    return img.convert('RGB')


def end(photo):
    img = Image.new('RGBA', (W, H), INK + (255,))
    p = product(photo, 520)
    img.alpha_composite(p, ((W - p.width) // 2, 120))
    d = ImageDraw.Draw(img)
    f = font(84, 800)
    d.text((W / 2, 760), 'Wear the message.', font=f, fill=WHITE, anchor='ma')
    d.text((W / 2, 870), 'Message hoodies with one kind line.', font=font(38, 450, True), fill=SOFT, anchor='ma')
    pf = font(44, 800)
    t = 'Shop now · goodmessagestudio.com'
    w = int(pf.getlength(t)) + 80
    d.rounded_rectangle(((W - w) / 2, 970, (W + w) / 2, 1062), 46, fill=PINK)
    d.text((W / 2, 1016), t, font=pf, fill=WHITE, anchor='mm')
    d.text((W / 2, 1150), '@goodmessage_studio', font=font(34, 700, True), fill=SOFT, anchor='ma')
    return img.convert('RGB')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--ids', required=True)
    ap.add_argument('--cache', required=True)
    ap.add_argument('--sheets', required=True)
    a = ap.parse_args()
    queue = json.loads((ROOT / 'queue.json').read_text())
    photos = [R.fetch(u, Path(a.cache) / 'gms') for u, _ in R.GMS_PHOTOS]
    Path(a.sheets).mkdir(parents=True, exist_ok=True)
    for wanted in a.ids.split(','):
        item = next(x for x in queue if x['id'] == wanted)
        topic = T.topic('gms', item['date'], item['title'])
        if not topic or len(topic['points']) != 5:
            raise SystemExit(f'{wanted}: reviewed topic text not found')
        folder = ROOT / item['folder']
        k0 = int(item['date'][-2:]) + item.get('publish_order', item['slot'])
        pick = lambda k: photos[(k0 + k) % len(photos)]
        slides = [cover(pick(0), topic['title'])] + [point(pick(i), i, h, b) for i, (h, b, _p) in enumerate(topic['points'], 1)] + [end(pick(6))]
        names = []
        for i, s in enumerate(slides, 1):
            name = f'fb-{i:02d}.jpg'
            s.save(folder / name, quality=90)
            names.append(name)
        meta = json.loads((folder / 'carousel.json').read_text())
        meta['facebook_slides'] = names
        (folder / 'carousel.json').write_text(json.dumps(meta, ensure_ascii=False, indent=2))
        sheet = Image.new('RGB', (270 * 7, 338), 'white')
        for i, s in enumerate(slides):
            sheet.paste(s.resize((270, 338)), (270 * i, 0))
        sheet.save(Path(a.sheets) / f'{wanted}.jpg', quality=85)
        print(wanted, item['title'])


if __name__ == '__main__':
    main()
