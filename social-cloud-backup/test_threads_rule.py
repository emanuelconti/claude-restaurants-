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

    def test_post_is_the_ideas_not_the_title(self):
        meta = {'title': 'Saturday morning ideas for a good day',
                'caption': 'Saturday morning ideas for a good day\n\nA slow Saturday morning sets the tone.\n\n'
                           'Discover hoodies at https://goodmessagestudio.com/.\n\nSave it.\n\n#GoodMessageStudio',
                'points': [['Wake up without an alarm', ['x'], 'y'], ['Breakfast at a kopitiam', ['x'], 'y'],
                           ['A walk in a park', ['x'], 'y'], ['Call your family', ['x'], 'y'],
                           ['Plan nothing until noon', ['x'], 'y']]}
        text = T.threads_text(meta)
        self.assertEqual(text, 'A slow Saturday morning sets the tone. Wake up without an alarm. '
                               'Breakfast at a kopitiam. A walk in a park. Plan nothing until noon.')
        self.assertNotIn('Saturday morning ideas', text)
        self.assertLessEqual(len(text), 280)
        no_points = dict(meta, points=None)
        self.assertEqual(T.threads_text(no_points), 'A slow Saturday morning sets the tone.')

    def test_text_only_no_slides(self):
        src = open(T.__file__, encoding='utf-8').read()
        self.assertIn('"media_type": "TEXT"', src)
        self.assertNotIn('"CAROUSEL"', src)
        self.assertNotIn('is_carousel_item', src)


if __name__ == '__main__':
    unittest.main()
