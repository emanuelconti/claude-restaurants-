#!/usr/bin/env python3
"""3D Reel for a reviewed queue item with videokit3d (owner, 26 November 2026). Editor tool, never run by the publisher.

    bash social-cloud-backup/videokit3d/setup.sh /tmp/vk3
    python social-cloud-backup/videokit3d/reel3d.py <item-id> [<item-id> ...]      # VK3=/tmp/vk3 by default

A golden or moonlit sea, the topic's reviewed photos as floating framed panels, a camera that flies from one
to the next on the beat, one short line on screen at a time, bloom, and a brand end card. Palette, layout,
camera orbit and music change with every item. The topic (with its photo_ids or photo_urls) comes from the
day's editorial file. Writes queue/<brand>/<date>/reel-<slot>/{reel.mp4, reel.json, cover.jpg} and a contact
sheet in $VK3/sheets to inspect before reelkit/approve.py. About 3 minutes per Reel on 4 cores."""
import hashlib, json, os, shutil, subprocess, sys, urllib.request
from pathlib import Path
from PIL import Image

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
VK = Path(os.environ.get('VK3', '/tmp/vk3'))
PUB = ROOT / 'publishers'
FPS, BEAT = 30, 0.65
STARTS = [round(BEAT * 4 * k, 2) for k in range(7)]   # hook + 5 points, end card at STARTS[6]
SECONDS = STARTS[6] + 3.0
CA = '/root/.ccr/ca-bundle.crt'

PALETTES = {
    'dusk':   dict(top='#120d33', horizon='#a8506a', ground='#0c0819', glow='#ff9f62', frame='#fff6ec', particles=['#ffd29a', '#ff9fb0', '#b9a8ff']),
    'night':  dict(top='#05070f', horizon='#24305e', ground='#04060c', glow='#7fb4ff', frame='#f1f4ff', particles=['#9fc3ff', '#ffe3a3', '#c7b2ff']),
    'golden': dict(top='#211638', horizon='#b8613a', ground='#140c18', glow='#ffb870', frame='#fffaf0', particles=['#ffe2a8', '#ffc38a', '#fff1d6']),
    'dawn':   dict(top='#33366e', horizon='#b06f86', ground='#211a2e', glow='#ffd0dc', frame='#ffffff', particles=['#ffffff', '#ffd6e4', '#e8dcff']),
    'teal':   dict(top='#071c26', horizon='#2f8f9a', ground='#06141b', glow='#9ff3e8', frame='#effffd', particles=['#b9fff4', '#ffe7b0', '#a8d8ff']),
}
BRANDS = {
    'sp':  dict(palettes=['dusk', 'golden', 'night', 'teal'], accent='#ffd24a', accentInk='#15161b', serif=False, logo='sp-mark.png',
                name='SocialPerks', cta='socialperkses.com', small='Llévate a un amigo a tu sitio favorito.'),
    'sin': dict(palettes=['night', 'teal', 'dusk', 'golden'], accent='#c8955a', accentInk='#ffffff', serif=False, logo='sin-mark.png',
                name='Sincronia', cta='Follow @sincronia.live', small='Funding readiness for European founders.'),
    'gms': dict(palettes=['dawn', 'dusk', 'golden', 'dawn'], accent='#c81a5c', accentInk='#ffffff', serif=True, logo='gms-logo.png',
                name='Good Message Studio', cta='goodmessagestudio.com', small='Link in bio'),
}
LAYOUTS = ['zigzag', 'left', 'zigzag', 'right']
# Owner, 27 November 2026: GMS gets story films (story3d.html: night city, a message of light, the real hoodie, a heart of lights), not photo panels.
STORY_BRANDS = {'gms'}


def fetch(url, path):
    if not path.exists():
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        import ssl
        data = urllib.request.urlopen(req, context=ssl.create_default_context(cafile=CA), timeout=60).read()
        path.write_bytes(data)
    im = Image.open(path).convert('RGB')
    if max(im.size) > 1400:
        im.thumbnail((1400, 1400)); im.save(path, quality=90)
    return path


def topic_for(item):
    import re
    name = f"gms-{item['date']}.txt" if item['brand'] == 'gms' else f"europe-{item['date']}.txt"
    text, dec, i = (ROOT / 'editorial' / name).read_text(), json.JSONDecoder(), 0
    while True:
        m = re.compile(r'(sp |sin |)\{').search(text, i)
        if not m:
            raise SystemExit(f"{item['id']}: topic not found")
        obj, i = dec.raw_decode(text, m.start() + len(m.group(1)))
        if (m.group(1).strip() or 'gms') == item['brand'] and obj['title'] == item['title']:
            return obj


def learned(b, h):
    """Owner, 27 November 2026: every Reel learns from the last ones. Views of published Reels (YouTube Shorts and
    Instagram, from performance/<brand>.json) are matched by title to their reel.json; palette and layout with the
    best mean views (at least 2 samples each, 6 in all, posts older than 48 h) are reused two times in three, the
    third explores the hash choice. Returns (palette_name or None, layout or None, note)."""
    import datetime as dt, glob
    try:
        perf = json.loads((ROOT / 'performance' / f'{b}.json').read_text())
    except Exception:
        return None, None, 'explore: no performance file'
    cutoff = dt.datetime.now(dt.timezone.utc) - dt.timedelta(hours=48)
    views = {}
    for ch in ('youtube', 'instagram', 'ig'):
        for p in (perf.get('channels', {}).get(ch) or {}).get('posts', []):
            v = p.get('views') if p.get('views') is not None else p.get('plays')
            try:
                v = float(v); t = dt.datetime.fromisoformat(p['stamp'].replace('Z', '+00:00').replace('+0000', '+00:00'))
            except Exception:
                continue
            if t <= cutoff:
                key = p.get('title', '').split(' | ')[0].strip().lower()
                views.setdefault(key, []).append(v)
    by_pal, by_lay = {}, {}
    for f in glob.glob(str(ROOT / 'queue' / b / '*' / 'reel*' / 'reel.json')):
        try:
            r = json.loads(Path(f).read_text())
        except Exception:
            continue
        v = views.get(r.get('title', '').strip().lower())
        if not v:
            continue
        pal = r.get('palette_name') or next((n for n, d in PALETTES.items() if d['horizon'] in r.get('engine', '')), None)
        lay = r.get('layout') or next((l for l in set(LAYOUTS) if f"layout {l}" in r.get('engine', '')), None)
        m = sum(v) / len(v)
        if pal in B_PALS(b): by_pal.setdefault(pal, []).append(m)
        if lay in LAYOUTS: by_lay.setdefault(lay, []).append(m)
    def best(d):
        ok = {k: sum(x) / len(x) for k, x in d.items() if len(x) >= 2}
        if sum(len(x) for x in d.values()) < 6 or not ok:
            return None
        k = max(ok, key=ok.get)
        allm = [y for x in d.values() for y in x]
        return k if ok[k] > sum(allm) / len(allm) else None
    if h % 3 == 0:
        return None, None, 'explore: one in three Reels tries something new'
    bp, bl = best(by_pal), best(by_lay)
    note = f'learned from {sum(len(x) for x in by_pal.values())} measured Reels: palette {bp or "no winner"}, layout {bl or "no winner"}'
    return bp, bl, note


def B_PALS(b):
    return BRANDS[b]['palettes']


def prepare():
    """Copy the scene, the music and the brand fonts and marks into the videokit3d cache."""
    (VK / 'fonts').mkdir(parents=True, exist_ok=True); (VK / 'assets').mkdir(exist_ok=True)
    for f in ('reel3d.html', 'story3d.html', 'story3d-2.html', 'music3d.py'):
        shutil.copy(HERE / f, VK / f)
    for f in (PUB / 'gms' / 'fonts').glob('*.ttf'):
        shutil.copy(f, VK / 'fonts' / f.name)
    # Brand marks live with the brand publishers; a cache already holding them (copied by the editor) is fine.
    for src, dst in ((PUB / 'sp' / 'assets' / 'mark.png', 'sp-mark.png'), (PUB / 'gms' / 'assets' / 'gms-logo-1024.png', 'gms-logo.png')):
        if src.exists():
            shutil.copy(src, VK / 'assets' / dst)
    try:
        sys.path.insert(0, str(PUB / 'sin'))
        import brand as SB
        SB.mark(512).save(VK / 'assets' / 'sin-mark.png')
    except Exception as e:
        print('sin mark skipped:', e)
    subprocess.Popen([sys.executable, '-m', 'http.server', '8765'], cwd=VK, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def make(item_id):
    queue = json.loads((ROOT / 'queue.json').read_text())
    item = next(x for x in queue if x['id'] == item_id)
    b, slot = item['brand'], item['slot']
    B = BRANDS[b]
    topic = topic_for(item)
    h = int(hashlib.sha256(item_id.encode()).hexdigest()[:8], 16)
    assets = VK / 'assets' / item_id
    assets.mkdir(parents=True, exist_ok=True)
    photos, sources = [], []
    if b == 'gms':
        urls = [u for u in topic['photo_urls']]
        hero = 'https://cdn.shopify.com/s/files/1/1038/5401/4799/files/gm-boat-back.jpg'
        urls = [urls[(h + k) % len(urls)] for k in range(len(urls))]
        urls = [hero if urls[0] != hero else urls[1]] + urls
        for k, u in enumerate(urls[:6]):
            photos.append(fetch(u, assets / f'p{k}.jpg')); sources.append(dict(url=u, product_photo=True))
    else:
        for k, pid in enumerate(topic['photo_ids'][:6]):
            photos.append(fetch(f'https://images.unsplash.com/photo-{pid}?w=1400&q=85&auto=format&fit=crop', assets / f'p{k}.jpg'))
            sources.append(dict(unsplash=pid, slide=f'slide-0{k + 1}.jpg'))
    lp, ll, learn_note = learned(b, h)
    pal_name = lp or B['palettes'][(slot // 2 + h) % len(B['palettes'])]
    pal = dict(PALETTES[pal_name], accent=B['accent'], accentInk=B['accentInk'])
    lines = [dict(text=topic['title'])] + [dict(text=p[0], num=f'0{k + 1}') for k, p in enumerate(topic['points'])]
    long_hook = len(topic['title']) > 34
    cfg = dict(seed=h, palette=pal, sunX=((h >> 4) % 100 - 50) / 160, layout=ll or LAYOUTS[(h >> 8) % 4], gap=13 + (h >> 12) % 5,
               orbit=0.35 + ((h >> 16) % 30) / 100, bloom=0.35 if b == 'gms' else 0.5,
               photos=[f'assets/{item_id}/{p.name}' for p in photos], lines=lines, serif=B['serif'],
               hookTop=250, hookSize=96 if long_hook else 116, lineTop=280, lineSize=104 if not B['serif'] else 110,
               starts=STARTS, seconds=SECONDS,
               end=dict(logo=f'assets/{B["logo"]}', name=B['name'], cta=B['cta'], small=B['small']),
               particles=pal['particles'], beat=BEAT)
    scene = os.environ.get('VK_SCENE') or ('story3d.html' if b in STORY_BRANDS else 'reel3d.html')
    (VK / 'cfg').mkdir(exist_ok=True)
    (VK / 'cfg' / f'{item_id}.json').write_text(json.dumps(cfg, ensure_ascii=False))
    frames = VK / 'frames' / item_id
    shutil.rmtree(frames, ignore_errors=True)
    total = round(SECONDS * FPS)
    procs = int(os.environ.get('VK_PROCS', '4'))
    step = (total + procs - 1) // procs
    ps = [subprocess.Popen(['node', 'render.js', f'{scene}?cfg=cfg/{item_id}.json', str(SECONDS), '1080', '1920', str(a), str(min(a + step, total)), str(frames)], cwd=VK)
          for a in range(0, total, step)]
    if any(p.wait() for p in ps):
        raise SystemExit(f'{item_id}: frame render failed')
    folder = ROOT / 'queue' / b / item['date'] / f'reel-{slot}'
    folder.mkdir(parents=True, exist_ok=True)
    wav = VK / 'frames' / f'{item_id}.wav'
    subprocess.run([sys.executable, str(VK / 'music3d.py'), b, str(h % 997), str(SECONDS), str(BEAT), str(STARTS[6]), str(wav)], check=True)
    mp4 = folder / 'reel.mp4'
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-framerate', str(FPS), '-i', str(frames / 'f%05d.jpg'), '-i', str(wav),
                    '-map', '0:v', '-map', '1:a', '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-pix_fmt', 'yuv420p', '-profile:v', 'high',
                    '-g', '60', '-r', str(FPS), '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', '-ac', '2', '-t', f'{SECONDS:.3f}',
                    '-movflags', '+faststart', str(mp4)], check=True)
    Image.open(frames / 'f00015.jpg').convert('RGB').save(folder / 'cover.jpg', quality=92)
    meta = json.loads((ROOT / item['folder'] / 'carousel.json').read_text())
    reel = dict(date=item['date'], title=item['title'], video='reel.mp4', cover='cover.jpg', seconds=round(SECONDS, 2), caption=meta['caption'],
                music=f'videokit3d music3d.py {b} style, seed {h % 997} (original, tones written in code, rights-cleared)',
                engine=f'videokit3d {scene} (Three.js, bloom, frame-by-frame), palette {pal}, layout {cfg["layout"]}',
                palette_name=pal_name, layout=cfg['layout'], learning=learn_note,
                photos=sources, scenes=['hook'] + [p[0] for p in topic['points']] + ['end card'])
    (folder / 'reel.json').write_text(json.dumps(reel, ensure_ascii=False, indent=1))
    picks = [0, 15, 45] + [round((STARTS[k] + 0.9) * FPS) for k in range(1, 6)] + [round((STARTS[k] + 2.2) * FPS) for k in (1, 3)] + [round((STARTS[6] + 0.4) * FPS), total - 5]
    ims = [Image.open(frames / f'f{p:05d}.jpg').resize((270, 480)) for p in picks]
    sheet = Image.new('RGB', (270 * 6, 480 * 2), 'white')
    for k, im in enumerate(ims):
        sheet.paste(im, ((k % 6) * 270, (k // 6) * 480))
    (VK / 'sheets').mkdir(exist_ok=True)
    sheet.save(VK / 'sheets' / f'{item_id}.jpg', quality=85)
    shutil.rmtree(frames)
    wav.unlink()
    print(item_id, 'ok', SECONDS, flush=True)

# ---------- story3d-2: "a message across the bay", the week's new GMS film (27 November 2026) ----------
# A night city on the bay, one lonely lit window (hook, frame one), a message of light crossing the water, the real
# message hoodie rising from the sea as a glowing card, the city switching on, the lights flying into a heart, brand end.
STORY_TIMES = dict(depart=2.6, arrive=5.6, rise=7.8, wave2=10.4, heart=12.6, end=15.6)   # on bars of 4 x 0.65 s
STORY_SECONDS = 19.6
STORY_PALETTES = {
    'harbour': dict(top='#03050f', horizon='#1d2350', fog='#080b22', wall='#0d1226', warm='#ffc874', cool='#bcd6ff', pink='#ff8fb8', water='#03060f', moon='#dfe8ff', orb='#ffe0a8'),
    'violet':  dict(top='#06030f', horizon='#3a1d55', fog='#120a26', wall='#140d26', warm='#ffd09a', cool='#d9c8ff', pink='#ff7fb0', water='#05030c', moon='#f1e6ff', orb='#ffd6e6'),
    'teal':    dict(top='#020a10', horizon='#163f4f', fog='#071a22', wall='#0a1a22', warm='#ffd38a', cool='#aef3ea', pink='#ff9cc4', water='#020a0e', moon='#e3fbff', orb='#fff0c2'),
}
STORY_PICKS = [0, 0.5, 1.5, 3.5, 4.6, 6.3, 8.5, 9.8, 11.5, 13.8, 15.2, 17.5]


def story_card(spec, item_id):
    """--card <reviewed slide path, relative to social-cloud-backup>:x0,y0,x1,y1 -> cropped real product photo in the cache."""
    path, _, box = spec.partition(':')
    im = Image.open(ROOT / path).convert('RGB')
    crop = [int(v) for v in box.split(',')] if box else [0, 0, im.width, im.height]
    out = VK / 'assets' / item_id; out.mkdir(parents=True, exist_ok=True)
    im.crop(crop).save(out / 'card.jpg', quality=95)
    return out / 'card.jpg', dict(slide=path, crop=crop, product_photo=True)


def story_lines(topic, message):
    hook = topic['hook'] if len(topic.get('hook', '')) <= 40 else topic['title']
    pts = [p[0] for p in topic['points']]
    pick = [pts[i] for i in (0, 2, 3) if i < len(pts)]
    T = STORY_TIMES
    slots = [(0.0, T['depart'] - 0.1), (T['depart'] + 0.1, T['arrive'] - 0.5), (T['arrive'] - 0.3, T['rise'] - 0.1), (T['rise'] + 0.2, T['wave2'] - 0.1)]
    lines = [dict(text=hook, a=0.0, b=slots[0][1], top=230, size=100 if len(hook) > 26 else 112)]
    for (a, b), text in zip(slots[1:], pick):
        lines.append(dict(text=text, a=a, b=b, top=240, size=94 if len(text) > 20 else 104 if len(text) > 16 else 112))
    lines.append(dict(text=message, a=T['heart'] + 0.4, b=T['end'] - 0.1, top=1440, size=108, msg=True))
    return lines


def make_story(item_id, card, message, cta='Gift the message'):
    queue = json.loads((ROOT / 'queue.json').read_text())
    item = next(x for x in queue if x['id'] == item_id)
    b, slot = item['brand'], item['slot']
    if b != 'gms':
        raise SystemExit('story3d-2 is a Good Message Studio film')
    B = BRANDS[b]
    topic = topic_for(item)
    h = int(hashlib.sha256(item_id.encode()).hexdigest()[:8], 16)
    card_path, card_src = story_card(card, item_id)
    pal_name = list(STORY_PALETTES)[h % len(STORY_PALETTES)]
    pal = dict(STORY_PALETTES[pal_name], accent=B['accent'])
    lines = story_lines(topic, message)
    cfg = dict(seed=h, palette=pal, moonX=(1 if (h >> 4) & 1 else -1) * (0.45 + ((h >> 5) % 15) / 100),   # the moon stays to one side, never over the heart
                farX=4 + (h >> 10) % 9, waveSpeed=14, bloom=0.55,
               cardW=4.6, cardDist=11.5, heartScale=1.0, times=STORY_TIMES, card=f'assets/{item_id}/card.jpg', lines=lines,
               end=dict(logo=f'assets/{B["logo"]}', name=B['name'], cta=cta, small=B['cta']))
    (VK / 'cfg').mkdir(exist_ok=True)
    (VK / 'cfg' / f'{item_id}.json').write_text(json.dumps(cfg, ensure_ascii=False))
    frames = VK / 'frames' / item_id
    shutil.rmtree(frames, ignore_errors=True)
    total = round(STORY_SECONDS * FPS)
    procs = int(os.environ.get('VK_PROCS', '4'))
    step = (total + procs - 1) // procs
    ps = [subprocess.Popen(['node', 'render.js', f'story3d-2.html?cfg=cfg/{item_id}.json', str(STORY_SECONDS), '1080', '1920', str(a), str(min(a + step, total)), str(frames)], cwd=VK)
          for a in range(0, total, step)]
    if any(p.wait() for p in ps):
        raise SystemExit(f'{item_id}: frame render failed')
    folder = ROOT / 'queue' / b / item['date'] / f'reel-{slot}'
    folder.mkdir(parents=True, exist_ok=True)
    wav = VK / 'frames' / f'{item_id}.wav'
    subprocess.run([sys.executable, str(VK / 'music3d.py'), b, str(h % 997), str(STORY_SECONDS), str(BEAT), str(STORY_TIMES['end']), str(wav)], check=True)
    mp4 = folder / 'reel.mp4'
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-framerate', str(FPS), '-i', str(frames / 'f%05d.jpg'), '-i', str(wav),
                    '-map', '0:v', '-map', '1:a', '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-pix_fmt', 'yuv420p', '-profile:v', 'high',
                    '-g', '60', '-r', str(FPS), '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', '-ac', '2', '-t', f'{STORY_SECONDS:.3f}',
                    '-movflags', '+faststart', str(mp4)], check=True)
    Image.open(frames / 'f00015.jpg').convert('RGB').save(folder / 'cover.jpg', quality=92)
    meta = json.loads((ROOT / item['folder'] / 'carousel.json').read_text())
    reel = dict(date=item['date'], title=item['title'], video='reel.mp4', cover='cover.jpg', seconds=STORY_SECONDS, caption=meta['caption'],
                music=f'videokit3d music3d.py {b} style, seed {h % 997} (original, tones written in code, rights-cleared)',
                engine=f'videokit3d story3d-2.html (Three.js film-story: night bay city, lonely window, light message, hoodie card, city lights, heart; bloom, frame-by-frame), palette story2-{pal_name}',
                scene='story3d-2', palette_name=f'story2-{pal_name}', layout='story3d-2', learning='story3d-2 scene, first run: compared against story3d and reel3d by views per Reel',
                photos=[card_src], lines=[l['text'] for l in lines] + [B['name'], cta, B['cta']],
                scenes=['hook: lonely lit window', 'message of light crosses the bay', 'far window lights up', 'real hoodie rises as a card', 'city lights up', 'lights become a heart', 'end card'])
    (folder / 'reel.json').write_text(json.dumps(reel, ensure_ascii=False, indent=1))
    picks = [min(round(x * FPS), total - 1) for x in STORY_PICKS]
    sheet = Image.new('RGB', (270 * 6, 480 * 2), 'white')
    for k, p in enumerate(picks):
        sheet.paste(Image.open(frames / f'f{p:05d}.jpg').resize((270, 480)), ((k % 6) * 270, (k // 6) * 480))
    (VK / 'sheets').mkdir(exist_ok=True)
    sheet.save(VK / 'sheets' / f'{item_id}.jpg', quality=85)
    shutil.rmtree(frames)
    wav.unlink()
    print(item_id, 'ok story3d-2', STORY_SECONDS, flush=True)



if __name__ == '__main__':
    import argparse, time
    ap = argparse.ArgumentParser()
    ap.add_argument('ids', nargs='+')
    ap.add_argument('--scene', default='auto', choices=['auto', 'story3d-2'], help='auto: story3d for GMS, reel3d for the others (VK_SCENE overrides)')
    ap.add_argument('--card', help='story3d-2: reviewed slide with the real hoodie, e.g. queue/gms/<date>/carousel-7/slide-05.jpg:0,490,1080,1350')
    ap.add_argument('--message', help="story3d-2: the hoodie's message as the last line, e.g. 'Enjoy the little things.'")
    ap.add_argument('--cta', default='Gift the message')
    a = ap.parse_args()
    prepare()
    time.sleep(1)
    for i in a.ids:
        if a.scene == 'story3d-2':
            make_story(i, a.card, a.message, a.cta)
        else:
            make(i)
