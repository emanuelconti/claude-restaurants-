"""Read the reviewed editorial topic text for a queue item (editor tool)."""
import json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def _blocks(text):
    """Yield (brand, topic dict) from pipe-format or JSON-format editorial files."""
    text = text.replace('\r', '')
    i = 0
    dec = json.JSONDecoder()
    while i < len(text):
        m = re.compile(r'(sp |sin |)\{').match(text, i)
        if m:
            obj, end = dec.raw_decode(text, i + len(m.group(1)))
            pts = [(p[0], (p[1][0] if p[1] else ''), p[2] if len(p) > 2 else '') for p in obj['points']]
            yield (m.group(1).strip() or 'gms'), dict(title=obj['title'], hook=obj['hook'], points=pts, set=obj.get('photos'), point_sets=obj.get('point_sets'))
            i = end
            continue
        j = text.find('\n\n', i)
        block = text[i: len(text) if j < 0 else j].strip()
        i = len(text) if j < 0 else j + 2
        if not block or block.startswith(('{', 'sp {', 'sin {')):
            continue
        lines = block.split('\n')
        head = lines[0].split('|')
        if head[0] in ('sp', 'sin') and len(head) >= 3:
            brand, title, hook = head[0], head[1], head[2]
        elif len(head) == 2:
            brand, title, hook = 'gms', head[0], head[1]
        else:
            continue
        pts = [tuple((l.split('|') + ['', ''])[:3]) for l in lines[1:] if '|' in l]
        yield brand, dict(title=title, hook=hook, points=pts, set=head[3] if len(head) > 3 else None)


def topic(brand, date, title):
    files = [ROOT / 'editorial' / (f'gms-{date}.txt' if brand == 'gms' else f'europe-{date}.txt')]
    for f in files:
        if f.exists():
            for b, t in _blocks(f.read_text()):
                if b == brand and t['title'].strip() == title.strip():
                    return t
    return None
