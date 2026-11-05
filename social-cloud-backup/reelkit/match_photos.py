"""Find which source photo each reviewed slide actually shows (editor tool, never run by the publisher).

Reels must reuse the exact photographs that were already visually approved for the
same scene. The carousel renderers place the photo at the top of slide 1 (full-bleed
cover, focus 0.5/0.42) and at the bottom of slides 2-6 (cover, focus 0.5/0.5, a white
fade on its first <=240 rows). We compare unfaded regions against every candidate.
"""
import math, sys
from pathlib import Path
import numpy as np
from PIL import Image

W, H = 1080, 1350


def cover(img, w, h, focus):
    r = max(w / img.width, h / img.height)
    im = img.resize((math.ceil(img.width * r), math.ceil(img.height * r)), Image.BILINEAR)
    x = int(min(max(focus[0] * im.width - w / 2, 0), im.width - w))
    y = int(min(max(focus[1] * im.height - h / 2, 0), im.height - h))
    return im.crop((x, y, x + w, y + h))


def small(img, box, size=(108, 20)):
    return np.asarray(img.crop(box).resize(size, Image.BILINEAR), dtype=np.float32)


class Matcher:
    def __init__(self, cache: Path):
        self.photos = {p.stem: Image.open(p).convert('RGB') for p in sorted(cache.glob('*.jpg'))}
        self.covers = {pid: small(cover(im, W, H, (0.5, 0.42)), (0, 0, W, 420), (108, 42)) for pid, im in self.photos.items()}
        self.points = {}
        for pid, im in self.photos.items():
            for h in range(470, 1000, 6):
                self.points[(pid, h)] = small(cover(im, W, h, (0.5, 0.5)), (0, h - 200, W, h))

    def cover_id(self, slide):
        s = small(slide, (0, 0, W, 420), (108, 42))
        scores = sorted((float(np.abs(v - s).mean()), pid) for pid, v in self.covers.items())
        return scores[0][1], scores[0][0], scores[1][0]

    def point_id(self, slide):
        s = small(slide, (0, H - 200, W, H))
        best = {}
        for (pid, h), v in self.points.items():
            e = float(np.abs(v - s).mean())
            if e < best.get(pid, 1e9):
                best[pid] = e
        scores = sorted((e, pid) for pid, e in best.items())
        return scores[0][1], scores[0][0], scores[1][0]


if __name__ == '__main__':
    m = Matcher(Path(sys.argv[1]))
    for folder in sys.argv[2:]:
        f = Path(folder)
        c = m.cover_id(Image.open(f / 'slide-01.jpg').convert('RGB'))
        pts = [m.point_id(Image.open(f / f'slide-0{i}.jpg').convert('RGB')) for i in range(2, 7)]
        print(folder, c, pts)
