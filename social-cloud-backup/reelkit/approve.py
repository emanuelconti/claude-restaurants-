#!/usr/bin/env python3
"""Bind visually reviewed reels into queue.json (editor tool).

    python reelkit/approve.py --ids sp-2026-11-07-3,... --qa "Contact sheet ... inspected 5 November"

Only run after every scene of every listed reel was inspected in its contact
sheet. Records kind=reel, reel_dir and exact SHA256 of reel.mp4, reel.json and
cover.jpg, plus measured duration and decoded loudness. The topic, title, slot
and carousel files stay unchanged, so receipts and dedupe keep working.
"""
import argparse, hashlib, json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
import media_checks as M  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--ids', required=True)
    ap.add_argument('--qa', required=True)
    args = ap.parse_args()
    path = ROOT / 'queue.json'
    queue = json.loads(path.read_text())
    for wanted in args.ids.split(','):
        item = next(x for x in queue if x['id'] == wanted)
        folder = ROOT / 'queue' / item['brand'] / item['date'] / f"reel-{item['slot']}"
        info = M.check_video(folder / 'reel.mp4', new_reel=True)
        M.check_reel_folder(folder, item['title'])
        meta = json.loads((folder / 'reel.json').read_text())
        item['kind'] = 'reel'
        item['reel_dir'] = folder.name
        item['reel_sha256'] = {n: hashlib.sha256((folder / n).read_bytes()).hexdigest() for n in ('reel.mp4', 'reel.json', 'cover.jpg')}
        swaps = sum(1 for p in meta['photos'] if p.get('replaces'))
        item['reel_qa'] = (f"{args.qa} {info['seconds']:.1f} s 1080x1920 30 fps; original music ({meta['music'].split(',')[0]}), decoded AAC "
                           f"mean {info['mean_db']} dB peak {info['peak_db']} dB; {len(meta['photos'])} scene photos"
                           + (f", {swaps} swapped for variety within the same reviewed photo set" if swaps else ", all identical to the reviewed slides"))
        print(item['id'], item['reel_dir'], info)
    path.write_text(json.dumps(queue, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
