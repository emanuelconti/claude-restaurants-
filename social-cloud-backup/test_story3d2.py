"""videokit3d story3d-2: the GMS film 'a message across the bay' keeps the owner's video rules (27 November 2026)."""
import importlib.util, unittest
from pathlib import Path

HERE = Path(__file__).parent
spec = importlib.util.spec_from_file_location('reel3d', HERE / 'videokit3d' / 'reel3d.py')
R = importlib.util.module_from_spec(spec); spec.loader.exec_module(R)
TOPIC = dict(title='Making friends in your twenties and thirties', hook='New friends can come at any age.',
             points=[['Join a class'], ['Say yes to invites'], ['Be the one who asks'], ['Show up again'], ['Be patient']])


class Story(unittest.TestCase):
    def test_reel_length_and_beats(self):
        self.assertTrue(15 <= R.STORY_SECONDS <= 30)
        t = R.STORY_TIMES
        self.assertLess(t['depart'], t['arrive']); self.assertLess(t['arrive'], t['rise'])
        self.assertLess(t['rise'], t['wave2']); self.assertLess(t['wave2'], t['heart']); self.assertLess(t['heart'], t['end'])
        self.assertGreaterEqual(R.STORY_SECONDS - t['end'], 3.0)   # the brand end card stays readable
        for k in ('depart', 'rise', 'wave2', 'end'):                 # cuts land on bars of the music
            self.assertAlmostEqual(t[k] / (R.BEAT * 4) % 1, 0, places=6)

    def test_hook_from_frame_one_and_one_line_at_a_time(self):
        lines = R.story_lines(TOPIC, 'Enjoy the little things.')
        self.assertEqual(lines[0]['a'], 0.0)
        self.assertEqual(lines[0]['text'], TOPIC['hook'])
        self.assertTrue(3 <= len(lines) <= 6)
        for a, b in zip(lines, lines[1:]):
            self.assertLessEqual(a['b'], b['a'])                     # never two lines on screen together
        self.assertTrue(lines[-1]['msg']); self.assertLess(lines[-1]['b'], R.STORY_TIMES['end'])

    def test_long_hook_falls_back_to_title(self):
        t = dict(TOPIC, hook='x' * 60)
        self.assertEqual(R.story_lines(t, 'm')[0]['text'], TOPIC['title'])

    def test_scene_file_and_contact_sheet(self):
        html = (HERE / 'videokit3d' / 'story3d-2.html').read_text()
        self.assertIn('window.render', html); self.assertIn('window.ready = true', html)
        self.assertEqual(len(R.STORY_PICKS), 12)
        self.assertTrue(all(0 <= x < R.STORY_SECONDS for x in R.STORY_PICKS))

    def test_story_layout_is_not_learned_as_a_reel3d_layout(self):
        self.assertNotIn('story3d-2', R.LAYOUTS)


if __name__ == '__main__':
    unittest.main()
