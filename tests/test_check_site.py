import sys
from pathlib import Path
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from check_site import check


class SiteLinkTests(unittest.TestCase):
    def test_valid_local_references(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'assets').mkdir()
            (root / 'about').mkdir()
            (root / 'assets' / 'photo.webp').write_bytes(b'webp')
            (root / 'about' / 'index.html').write_text('<h1>About</h1>')
            (root / 'index.html').write_text('''<a href="/about/">About</a>
                <img src="/assets/photo.webp" alt="Photo">
                <a href="https://example.com">External</a>''')
            self.assertEqual(check(root), [])

    def test_quoted_css_url_with_parentheses(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'assets').mkdir()
            (root / 'assets' / 'photo (2).jpg').write_bytes(b'photo')
            (root / 'index.html').write_text(
                '<div style="background-image: url(\'/assets/photo%20(2).jpg\')"></div>'
            )
            (root / 'assets' / 'site.css').write_text(
                'body { background-image: url("photo%20(2).jpg"); }'
            )
            self.assertEqual(check(root), [])

    def test_missing_image_with_parentheses_is_reported(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'index.html').write_text(
                '<div style="background-image: url(\'/assets/missing%20(2).jpg\')"></div>'
            )
            self.assertEqual(check(root), [('index.html', '/assets/missing%20(2).jpg')])

    def test_missing_local_asset_is_reported(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'index.html').write_text('<img src="/missing.jpg">')
            self.assertEqual(check(root), [('index.html', '/missing.jpg')])

    def test_broken_manifest_icon_is_reported(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'index.html').write_text('OK')
            (root / 'site.webmanifest').write_text('{"icons":[{"src":"/old-path.png"}]}')
            self.assertEqual(check(root), [('site.webmanifest', '/old-path.png')])


if __name__ == '__main__':
    unittest.main()
