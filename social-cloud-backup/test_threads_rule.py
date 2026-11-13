"""Owner, 13 November 2026: Threads paused until 16 November, then one text-only post a day, 20 h apart."""
import os, sys, unittest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'publishers', 'gms'))
os.environ.setdefault('THREADS_TOKEN_GMS', '')
import threads_publish as T
from policy import daily_cap


class ThreadsRule(unittest.TestCase):
    def test_limits(self):
        self.assertEqual(T.THREADS_RESUME, '2026-11-16')
        self.assertEqual(T.MAX_PER_DAY, 1)
        self.assertGreaterEqual(T.MIN_GAP, 20 * 60)

    def test_controller_cap(self):
        self.assertEqual(daily_cap('threads', 8, '2026-11-15'), 0)
        self.assertEqual(daily_cap('threads', 8, '2026-11-16'), 1)
        self.assertEqual(daily_cap('threads', 3, '2026-11-17'), 0)

    def test_text_is_short_and_clean(self):
        text = T.short_caption('One. Two? Three! Four.\n\nSave this.\n\nhttps://goodmessagestudio.com\n\n#sg')
        self.assertEqual(text, 'One. Two? Three!')
        self.assertNotIn('http', text)
        self.assertNotIn('#', text)

    def test_text_only_no_slides(self):
        src = open(T.__file__, encoding='utf-8').read()
        self.assertIn('"media_type": "TEXT"', src)
        self.assertNotIn('"CAROUSEL"', src)
        self.assertNotIn('is_carousel_item', src)


if __name__ == '__main__':
    unittest.main()
