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
    'dawn':   dict(top='#4a4f8f', horizon='#d98ea0', ground='#2a2238', glow='#ffd0dc', frame='#ffffff', particles=['#ffffff', '#ffd6e4', '#e8dcff']),
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


def prepare():
    """Copy the scene, the music and the brand fonts and marks into the videokit3d cache."""
    (VK / 'fonts').mkdir(parents=True, exist_ok=True); (VK / 'assets').mkdir(exist_ok=True)
    for f in ('reel3d.html', 'music3d.py'):
        shutil.copy(HERE / f, VK / f)
    for f in (PUB / 'gms' / 'fonts').glob('*.ttf'):
        shutil.copy(f, VK / 'fonts' / f.name)
    shutil.copy(PUB / 'sp' / 'assets' / 'mark.png', VK / 'assets' / 'sp-mark.png')
    shutil.copy(PUB / 'gms' / 'assets' / 'gms-logo-1024.png', VK / 'assets' / 'gms-logo.png')
    sys.path.insert(0, str(PUB / 'sin'))
    import brand as SB
    SB.mark(512).save(VK / 'assets' / 'sin-mark.png')
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
    pal = dict(PALETTES[B['palettes'][(slot // 2 + h) % len(B['palettes'])]], accent=B['accent'], accentInk=B['accentInk'])
    lines = [dict(text=topic['title'])] + [dict(text=p[0], num=f'0{k + 1}') for k, p in enumerate(topic['points'])]
    long_hook = len(topic['title']) > 34
    cfg = dict(seed=h, palette=pal, sunX=((h >> 4) % 100 - 50) / 160, layout=LAYOUTS[(h >> 8) % 4], gap=13 + (h >> 12) % 5,
               orbit=0.35 + ((h >> 16) % 30) / 100, bloom=0.35 if b == 'gms' else 0.5,
               photos=[f'assets/{item_id}/{p.name}' for p in photos], lines=lines, serif=B['serif'],
               hookTop=250, hookSize=96 if long_hook else 116, lineTop=280, lineSize=104 if not B['serif'] else 110,
               starts=STARTS, seconds=SECONDS,
               end=dict(logo=f'assets/{B["logo"]}', name=B['name'], cta=B['cta'], small=B['small']))
    (VK / 'cfg').mkdir(exist_ok=True)
    (VK / 'cfg' / f'{item_id}.json').write_text(json.dumps(cfg, ensure_ascii=False))
    frames = VK / 'frames' / item_id
    shutil.rmtree(frames, ignore_errors=True)
    total = round(SECONDS * FPS)
    procs = int(os.environ.get('VK_PROCS', '4'))
    step = (total + procs - 1) // procs
    ps = [subprocess.Popen(['node', 'render.js', f'reel3d.html?cfg=cfg/{item_id}.json', str(SECONDS), '1080', '1920', str(a), str(min(a + step, total)), str(frames)], cwd=VK)
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
                engine=f'videokit3d reel3d.html (Three.js, bloom, frame-by-frame), palette {pal}, layout {cfg["layout"]}',
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


if __name__ == '__main__':
    prepare()
    import time; time.sleep(1)
    for i in sys.argv[1:]:
        make(i)
