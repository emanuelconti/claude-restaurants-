"""Reels for every brand, Facebook Page Reels and clickable product cards (owner, 5 November 2026)."""
import ast, io, json, os, shutil, subprocess, sys, tempfile, types, unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'publishers/gms'))
import fb_publish as f  # noqa: E402


def jpeg(size, colour='violet'):
    from PIL import Image, ImageDraw
    raw = io.BytesIO()
    im = Image.new('RGB', size, colour)
    ImageDraw.Draw(im).rectangle((0, 0, size[0] // 2, size[1] // 2), fill='white')
    im.save(raw, 'JPEG')
    return raw.getvalue()


def controller_fn(name):
    tree = ast.parse((ROOT / 'controller.py').read_text())
    return next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == name)


class FormatPlan(unittest.TestCase):
    def setUp(self):
        scope = {}
        exec(compile(ast.Module(body=[controller_fn('facebook_format')], type_ignores=[]), 'c', 'exec'), scope)
        self.fmt = scope['facebook_format']

    def test_one_in_three_facebook_posts_are_product_cards(self):
        plan = [self.fmt(dict(publish_order=o, slot=o), {}) for o in range(1, 9)]
        self.assertEqual(plan.count('cards'), 3)
        self.assertEqual([plan[i] for i in (1, 4, 7)], ['cards'] * 3)

    def test_paused_cards_fall_back_to_native_showcase(self):
        self.assertEqual(self.fmt(dict(publish_order=5, slot=5), {'fb_cards_paused': 'cards_withdrawn: x'}), 'products')

    def test_reel_folder_rejects_paths(self):
        import re
        from pathlib import Path as P
        scope = {'re': re, 'Path': P, 'R': P('/r')}
        exec(compile(ast.Module(body=[controller_fn('reel_folder')], type_ignores=[]), 'c', 'exec'), scope)
        self.assertEqual(scope['reel_folder'](dict(brand='sp', date='2099-01-01', reel_dir='reel-3')), P('/r/queue/sp/2099-01-01/reel-3'))
        for bad in ('../x', 'reel-9', 'carousel-1'):
            with self.assertRaises(AssertionError):
                scope['reel_folder'](dict(brand='sp', date='2099-01-01', reel_dir=bad))


class Cards(unittest.TestCase):
    def run_cards(self, stored=(1080, 1080), owned=True, deleted=True):
        catalog = {'products': [dict(title=t + ' Hoodie', handle=h, images=[{'src': f'https://cdn.shopify.com/{h}.jpg', 'width': 800, 'height': 800}],
                                     variants=[{'price': '59'}]) for t, h in (('Be Kind', 'be-kind'), ('Enjoy The Little Things', 'etlt'),
                                                                               ('Do What Makes You Happy', 'dwmyh'))]}
        catalog['products'].append(dict(title='Peace Starts With Us Hoodie', handle='peace', images=[{'src': 'https://cdn.shopify.com/p.jpg', 'width': 500, 'height': 500}], variants=[{'price': '69'}]))
        calls, posts = [], {}
        def api(method, path, token, params=None):
            params = params or {}
            calls.append((method, path, params))
            if path == '' and params.get('fields', '').startswith('ownership'):
                return {'ownership_permissions': {'can_customize_link_posts': owned}}
            if path == '':
                return {}
            if path == 'page/feed':
                pid = f'post{sum(1 for c in calls if c[1] == "page/feed") - 1}'
                posts[pid] = params
                return {'id': pid}
            if path.endswith('/photos'):
                return {'id': f'photo{len(calls)}'}
            if method == 'GET' and path.startswith('photo'):
                return {'images': [{'width': 1080, 'height': 1350}]}
            if method == 'DELETE':
                posts.pop(path, None)
                return {'success': True}
            if method == 'GET' and path in posts and params.get('fields', '').startswith('attachments'):
                children = json.loads(posts[path].get('child_attachments', '[]'))
                return {'attachments': {'data': [{'type': 'multi_share', 'subattachments': {'data': [
                    {'target': {'url': 'https://l.facebook.com/l.php?u=' + c['link'] + '&h=x'}, 'media': {'image': {'src': 'https://scontent.example/' + c['link'][-5:], 'width': stored[0], 'height': stored[1]}}}
                    for c in children]}}]}}
            if method == 'GET' and path.startswith('post') and path not in posts:
                if deleted:
                    raise RuntimeError('GET post: Unsupported get request')
                return {'id': path, 'is_published': True}
            return {'permalink_url': 'https://facebook.com/' + path, 'id': path}
        def direct(url, limit=0):
            if 'cdn.shopify.com' in url:
                return 200, 'image/jpeg', jpeg((800, 800))
            return 200, 'text/html', b'<meta property="og:image" content="x"><meta property="og:url" content="' + url.encode() + b'">'
        def urlopen(url, *a, **kw):
            u = url if isinstance(url, str) else url.full_url
            if u.endswith('products.json?limit=250'):
                return io.BytesIO(json.dumps(catalog).encode())
            if u.startswith('https://scontent'):
                return io.BytesIO(jpeg(stored))
            return io.BytesIO(jpeg((800, 800)))
        from PIL import Image
        with tempfile.TemporaryDirectory() as root:
            folder = Path(root) / '2099-01-01' / 'carousel-2'
            folder.mkdir(parents=True)
            (folder / 'carousel.json').write_text(json.dumps(dict(caption='A unique card topic\nBody', slides=[])))
            out = io.StringIO()
            with patch.dict(os.environ, FB_PAGE_TOKEN_GMS='placeholder', FB_PAGE_ID_GMS='page'), \
                 patch.object(f, 'page_token', return_value='placeholder'), patch.object(f, 'recent', return_value=[]), \
                 patch.object(f, 'call', side_effect=api), patch.object(f, 'fetch_direct', side_effect=direct), \
                 patch.object(f.urllib.request, 'urlopen', side_effect=urlopen), patch('time.sleep'), \
                 patch.object(sys, 'argv', ['fb', '--date', '2099-01-01', '--slot', '2', '--format', 'cards', '--out', root]), \
                 patch('sys.stdout', out):
                f.main()
            receipt = json.loads((folder / 'published-facebook.json').read_text())
        return receipt, calls, posts, out.getvalue()

    def test_verified_cards_publish_clickable_children(self):
        receipt, calls, posts, out = self.run_cards()
        self.assertEqual(receipt['format'], 'clickable_product_cards')
        self.assertEqual(len(receipt['cards']), 3)  # the 500 px Peace photo is excluded by preflight selection
        feed = next(p for m, path, p in calls if path == 'page/feed')
        children = json.loads(feed['child_attachments'])
        self.assertTrue(all(c['link'].startswith('https://goodmessagestudio.com/products/') for c in children))
        self.assertEqual(feed['multi_share_end_card'], 'false')
        self.assertIn('https://goodmessagestudio.com/products/', feed['message'])

    def test_tiny_stored_card_image_withdraws_post_and_falls_back(self):
        receipt, calls, posts, out = self.run_cards(stored=(1, 1))
        self.assertIn('cards_withdrawn: post0', out)
        self.assertTrue(any(m == 'DELETE' and p == 'post0' for m, p, _ in calls))
        self.assertNotIn('post0', posts)
        self.assertEqual(receipt['format'], 'native_products')

    def test_withdrawal_failure_stops_without_fallback(self):
        with self.assertRaisesRegex(SystemExit, 'could not be withdrawn'):
            self.run_cards(stored=(1, 1), deleted=False)

    def test_unowned_links_never_create_card_post(self):
        receipt, calls, posts, out = self.run_cards(owned=False)
        self.assertIn('cards_unavailable', out)
        self.assertFalse(any('child_attachments' in p for _, _, p in calls))
        self.assertEqual(receipt['format'], 'native_products')

    def test_preflight_rejects_redirects_small_and_blank_images(self):
        card = dict(name='x', link='https://goodmessagestudio.com/products/x', picture='https://cdn.shopify.com/x.jpg')
        page = (200, 'text/html', b'property="og:image" ' + card['link'].encode())
        with patch.object(f, 'fetch_direct', side_effect=[(301, 'text/html', b''), page]):
            self.assertTrue(any('301' in p for p in f.preflight_card(card)))
        with patch.object(f, 'fetch_direct', side_effect=[(200, 'image/jpeg', jpeg((500, 500))), page]):
            self.assertTrue(any('below 600' in p for p in f.preflight_card(card)))
        from PIL import Image
        raw = io.BytesIO(); Image.new('RGB', (900, 900), 'white').save(raw, 'JPEG')
        with patch.object(f, 'fetch_direct', side_effect=[(200, 'image/jpeg', raw.getvalue()), page]):
            self.assertTrue(any('blank' in p for p in f.preflight_card(card)))


@unittest.skipUnless(shutil.which('ffmpeg'), 'ffmpeg needed')
class Media(unittest.TestCase):
    def make(self, root, seconds, audio):
        path = Path(root) / 'v.mp4'
        src = 'sine=frequency=440' if audio else 'anullsrc=r=48000:cl=stereo'
        subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-f', 'lavfi', '-i', f'color=c=blue:s=1080x1920:r=30:d={seconds}',
                        '-f', 'lavfi', '-i', f'{src}', '-t', str(seconds), '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-c:a', 'aac', str(path)], check=True)
        return path

    def test_silent_reel_is_rejected_and_audible_reel_passes(self):
        import media_checks as M
        with tempfile.TemporaryDirectory() as root:
            with self.assertRaisesRegex(AssertionError, 'silent'):
                M.check_video(self.make(root, 16, False), new_reel=True)
            self.assertGreater(M.check_video(self.make(root, 16, True), new_reel=True)['mean_db'], -35)
            with self.assertRaisesRegex(AssertionError, 'duration'):
                M.check_video(self.make(root, 10, True), new_reel=True)


class FacebookReel(unittest.TestCase):
    def test_native_page_reel_flow_and_readback(self):
        import fb_reel_publish as FR
        calls = []
        def api(method, path, token, params=None):
            calls.append((method, path, params or {}))
            if path == 'page' :
                return {'name': 'Good Message Studio'}
            if path == 'page/video_reels' and method == 'GET':
                return {'data': []}
            if path == 'page/video_reels' and params.get('upload_phase') == 'start':
                return {'video_id': 'v1'}
            if path == 'page/video_reels':
                return {'success': True}
            if path == 'v1':
                return {'status': {'video_status': 'ready', 'publishing_phase': {'status': 'complete'}}, 'length': 18.0, 'permalink_url': '/reel/v1'}
            return {}
        with tempfile.TemporaryDirectory() as root:
            folder = Path(root) / '2099-01-01' / 'reel-7'
            folder.mkdir(parents=True)
            (folder / 'reel.json').write_text(json.dumps(dict(caption='Evening reel title\n(link in bio)', video='reel.mp4')))
            (folder / 'reel.mp4').write_bytes(b'0' * 100)
            with patch.dict(os.environ, FB_PAGE_TOKEN_GMS='placeholder', FB_PAGE_ID_GMS='page'), \
                 patch.object(FR.F, 'page_token', return_value='placeholder'), patch.object(FR.F, 'recent', return_value=[]), \
                 patch.object(FR.F, 'call', side_effect=api), patch.object(FR, 'probe', return_value={'seconds': 18.0}), \
                 patch.object(FR, 'upload') as upload, patch('time.sleep'), \
                 patch.object(sys, 'argv', ['r', '--date', '2099-01-01', '--reel-dir', 'reel-7', '--out', root]):
                FR.main()
            receipt = json.loads((folder / 'published-facebook.json').read_text())
        upload.assert_called_once()
        finish = next(p for m, path, p in calls if p.get('upload_phase') == 'finish')
        self.assertEqual(finish['video_state'], 'PUBLISHED')
        self.assertIn('https://goodmessagestudio.com', finish['description'])
        self.assertEqual(receipt['permalink'], 'https://www.facebook.com/reel/v1')

    def test_reel_respects_sixty_minute_gap(self):
        import fb_reel_publish as FR, datetime as dt
        recent = [dict(message='Other', created_time=dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%dT%H:%M:%S+0000'))]
        with tempfile.TemporaryDirectory() as root:
            folder = Path(root) / '2099-01-01' / 'reel-7'; folder.mkdir(parents=True)
            (folder / 'reel.json').write_text(json.dumps(dict(caption='Evening reel title', video='reel.mp4')))
            with patch.dict(os.environ, FB_PAGE_TOKEN_GMS='placeholder', FB_PAGE_ID_GMS='page'), \
                 patch.object(FR.F, 'page_token', return_value='placeholder'), patch.object(FR.F, 'recent', return_value=recent), \
                 patch.object(FR, 'reels', return_value=[]), patch.object(FR, 'probe', return_value={'seconds': 18.0}), \
                 patch.object(FR.F, 'call', return_value={'name': 'Good Message Studio'}), \
                 patch.object(sys, 'argv', ['r', '--date', '2099-01-01', '--reel-dir', 'reel-7', '--out', root]):
                with self.assertRaisesRegex(SystemExit, 'too soon'):
                    FR.main()


class InstagramReelAllBrands(unittest.TestCase):
    def test_shared_reel_publisher_dedupes_caps_and_uses_cover(self):
        sys.path.insert(0, str(ROOT / 'publishers'))
        import reel_common as RC
        calls = []
        IG = types.SimpleNamespace(call=lambda m, p, t, params=None: calls.append((m, p, params)) or
                                   ({'data': []} if p.endswith('/media') and m == 'GET' else {'id': 'c1'} if m == 'POST' else {'permalink': 'https://instagram.com/reel/x', 'media_product_type': 'REELS'}),
                                   wait_ready=lambda *a: None)
        with tempfile.TemporaryDirectory() as root:
            (Path(root) / 'reel.json').write_text(json.dumps(dict(caption='Titulo exacto\nCuerpo')))
            base = 'https://raw.githubusercontent.com/emanuelconti/claude-restaurants-/abc/social-cloud-backup/queue/sp/2099-01-01/reel-3/'
            with patch.dict(os.environ, REEL_PUBLIC_VIDEO_URL=base + 'reel.mp4', REEL_PUBLIC_COVER_URL=base + 'cover.jpg'), patch.object(RC, 'check_url'):
                RC.publish(IG, 'u', 'socialperks.es', 't', root, 'Europe/Madrid', 8)
        create = next(p for m, path, p in calls if m == 'POST' and path == 'u/media')
        self.assertEqual(create['media_type'], 'REELS')
        self.assertEqual(create['cover_url'], base + 'cover.jpg')

    def test_sp_and_sin_have_reel_publishers_with_their_own_market(self):
        for brand, zone, token in (('sp', 'Europe/Madrid', 'INSTAGRAM_ACCESS_TOKEN'), ('sin', 'Europe/Paris', 'INSTAGRAM_TOKEN_SINCRONIA')):
            source = (ROOT / 'publishers' / brand / 'reel_publish.py').read_text()
            self.assertIn(zone, source)
            self.assertIn(token, source)

    def test_future_days_carry_the_reels_per_brand(self):
        # Owner, 5 November: two Reels a day (3, 7). Owner, 6 November: at least three or four
        # Reels a day on every Instagram profile, so from 7 November four of the eight topics are
        # Reels: SocialPerks and Sincronia 1, 3, 5, 7; GMS 1, 3, 6, 7 (Facebook keeps its product
        # cards at 2, 5, 8). Earlier days keep 3 and 7 (SocialPerks 6 November also 5).
        items = json.loads((ROOT / 'queue.json').read_text())
        four = {'sp': [1, 3, 5, 7], 'sin': [1, 3, 5, 7], 'gms': [1, 3, 6, 7]}
        for brand in ('sp', 'sin', 'gms'):
            days = sorted({x['date'] for x in items if x['brand'] == brand and x.get('reel_dir', 'reel') != 'reel' and x.get('kind') == 'reel'})
            self.assertTrue(days, brand)
            for day in days:
                reels = [x for x in items if x['brand'] == brand and x['date'] == day and x.get('kind') == 'reel']
                orders = sorted(x.get('publish_order', x['slot']) for x in reels)
                if day >= '2026-11-07':
                    self.assertEqual(orders, four[brand], (brand, day))
                elif (brand, day) == ('sp', '2026-11-06'):
                    self.assertEqual(orders, [3, 5, 7], (brand, day))
                else:
                    self.assertEqual(orders, [3, 7], (brand, day))


if __name__ == '__main__':
    unittest.main()
