"""reel3d.learned(): Reels reuse the palette and layout with the best measured views (owner, 27 November 2026)."""
import importlib.util, json, tempfile, unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location('reel3d', Path(__file__).parent / 'videokit3d' / 'reel3d.py')
R = importlib.util.module_from_spec(spec); spec.loader.exec_module(R)


class Learning(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); root = Path(self.tmp.name); self.old = R.ROOT; R.ROOT = root
        posts = []
        for k in range(8):
            pal, lay, views = ('golden', 'left', 900) if k < 4 else ('dawn', 'zigzag', 50)
            d = root / 'queue' / 'gms' / f'2026-11-1{k}' / 'reel-1'; d.mkdir(parents=True)
            (d / 'reel.json').write_text(json.dumps(dict(title=f'T{k}', palette_name=pal, layout=lay)))
            posts.append(dict(title=f'T{k} | goodmessagestudio.com #Shorts', stamp='2026-11-01T10:00:00Z', views=str(views)))
        (root / 'performance').mkdir(); (root / 'performance' / 'gms.json').write_text(json.dumps(dict(channels=dict(youtube=dict(posts=posts)))))

    def tearDown(self):
        R.ROOT = self.old; self.tmp.cleanup()

    def test_reuses_the_winner_two_times_in_three(self):
        self.assertEqual(R.learned('gms', 1)[:2], ('golden', 'left'))
        self.assertEqual(R.learned('gms', 2)[:2], ('golden', 'left'))

    def test_explores_one_time_in_three(self):
        self.assertEqual(R.learned('gms', 3)[:2], (None, None))

    def test_no_data_means_hash_choice(self):
        (R.ROOT / 'performance' / 'gms.json').unlink()
        self.assertEqual(R.learned('gms', 1)[:2], (None, None))


if __name__ == '__main__':
    unittest.main()
