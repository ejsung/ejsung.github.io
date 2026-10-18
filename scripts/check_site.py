#!/usr/bin/env python3
"""Check references to local pages/assets in a generated Jekyll site.

No network access or third-party packages are required. Run *after* jekyll build.
External websites are intentionally not fetched: their reachability is a
separate, network-dependent task.
"""

import argparse
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import sys
from urllib.parse import unquote, urlsplit
from xml.etree import ElementTree

SITE_HOSTS = {'ejsung.github.io', 'www.ejsung.github.io'}
ASSET_ATTRS = {'href', 'src', 'poster', 'data-src', 'data-href'}
CSS_URL = re.compile(r'url\(\s*[\'"]?([^\'"\)]+)', re.I)


class References(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.urls = []

    def handle_starttag(self, tag, attrs):
        d = dict(attrs)
        for key in ASSET_ATTRS:
            if d.get(key):
                self.urls.append(d[key])
        if d.get('srcset'):
            # A srcset candidate is URL followed by optional density/width.
            self.urls.extend(x.strip().split()[0] for x in d['srcset'].split(',') if x.strip())
        if d.get('style'):
            self.urls.extend(CSS_URL.findall(d['style']))


def resolve(root: Path, containing: Path, raw_url: str):
    """Return a local destination or None for external, fragment, and data URLs."""
    raw_url = raw_url.strip()
    if not raw_url or raw_url.startswith(('#', '//')):
        return None
    parsed = urlsplit(raw_url)
    if parsed.scheme and parsed.scheme not in {'http', 'https'}:
        return None
    if parsed.netloc and parsed.netloc.lower() not in SITE_HOSTS:
        return None
    path = unquote(parsed.path)
    if not path:
        return None
    if path.startswith('/'):
        candidate = root / path.lstrip('/')
    else:
        candidate = containing.parent / path
    # Normalize and reject unexpected traversal paths.
    candidate = candidate.resolve()
    if not candidate.is_relative_to(root.resolve()):
        return ('invalid path traversal', raw_url)
    if candidate.is_file():
        return None
    if candidate.is_dir() and (candidate / 'index.html').is_file():
        return None
    if not candidate.suffix and (candidate / 'index.html').is_file():
        return None
    if not candidate.suffix and candidate.with_suffix('.html').is_file():
        return None
    return (str(candidate.relative_to(root)), raw_url)


def check(root: Path):
    issues = []
    if not (root / 'index.html').is_file():
        return [('index.html', 'missing site homepage')]
    for filename in sorted(root.rglob('*.html')):
        parser = References()
        parser.feed(filename.read_text(encoding='utf-8', errors='replace'))
        for u in parser.urls:
            issue = resolve(root, filename, u)
            if issue is not None:
                issues.append((str(filename.relative_to(root)), issue[1]))
    for filename in sorted(root.rglob('*.css')):
        for u in CSS_URL.findall(filename.read_text(encoding='utf-8', errors='replace')):
            issue = resolve(root, filename, u)
            if issue is not None:
                issues.append((str(filename.relative_to(root)), issue[1]))
    for filename in sorted(root.rglob('*.webmanifest')):
        try:
            d = json.loads(filename.read_text(encoding='utf-8'))
        except (ValueError, UnicodeError) as exc:
            issues.append((str(filename.relative_to(root)), f'invalid JSON: {exc}'))
            continue
        for icon in d.get('icons', []):
            issue = resolve(root, filename, icon.get('src', ''))
            if issue is not None:
                issues.append((str(filename.relative_to(root)), issue[1]))
    for filename in sorted(root.rglob('browserconfig.xml')):
        try:
            tree = ElementTree.parse(filename)
        except ElementTree.ParseError as exc:
            issues.append((str(filename.relative_to(root)), f'invalid XML: {exc}'))
            continue
        for elem in tree.iter():
            if elem.get('src'):
                issue = resolve(root, filename, elem.get('src'))
                if issue is not None:
                    issues.append((str(filename.relative_to(root)), issue[1]))
    return issues


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root', default='_site', type=Path)
    args = p.parse_args()
    if not args.root.is_dir():
        p.error(f'build directory is missing: {args.root}')
    issues = check(args.root)
    if issues:
        print(f'FAILED: {len(issues)} missing or invalid local references:', file=sys.stderr)
        for owner, link in issues[:80]:
            print(f'  {owner}: {link}', file=sys.stderr)
        if len(issues) > 80:
            print(f'  ... and {len(issues) - 80} more', file=sys.stderr)
        return 1
    print('PASS: all checked local HTML, CSS, and manifest references resolve.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
