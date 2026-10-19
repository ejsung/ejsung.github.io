#!/usr/bin/env python3
"""Produce an explicit inventory of the tracked repository files.

Unlike `git ls-files`, this report also documents why an override or media
file is retained. Review unusual files before deletion; usage isn't proof of
ownership or the lack of future intent.
"""
import csv
from pathlib import Path
import subprocess
import sys

REASONS = {
    '_layouts/bibliography.html': 'Customized Jekyll Scholar bibliography and author emphasis',
    '_layouts/single.html': 'Custom date placement and academic page layout',
    '_includes/page__date.html': 'Custom created/updated dates and Research update logic',
    '_includes/page__meta.html': 'Custom publication/update metadata',
    '_includes/author-profile.html': 'Customized researcher profile and social link markup',
    '_includes/breadcrumbs.html': 'Customized breadcrumb navigation',
    '_includes/head.html': 'Font Awesome loading and upstream-compatible head',
    '_includes/scripts.html': 'MathJax 4 and custom JavaScript loading',
    '_includes/head/custom.html': 'Favicon, Academicons and external profile link behavior',
    '_includes/video': 'Custom privacy-aware video providers',
    'assets/css/main.scss': 'Site stylesheet entry point and site-specific CSS',
    '_sass/minimal-mistakes.scss': 'Required local theme Sass import entry point; resolves six local custom partials before upstream fallback',
    'assets/js/lunr/lunr-store.js': 'Site-specific search indexing data',
    'assets/js/site-custom.js': 'Site-specific sidebar and heading behavior',
}


def category(name):
    if name in REASONS:
        return 'custom override / site behavior', REASONS[name]
    if name.startswith('_sass/'):
        custom_sass = {
            '_sass/minimal-mistakes/_base.scss',
            '_sass/minimal-mistakes/_masthead.scss',
            '_sass/minimal-mistakes/_navigation.scss',
            '_sass/minimal-mistakes/_page.scss',
            '_sass/minimal-mistakes/_sidebar.scss',
            '_sass/minimal-mistakes/_utilities.scss',
        }
        if name in custom_sass:
            return 'custom Sass override', 'Site-specific style changes; unmodified Sass inherits from pinned remote theme'
        return 'review', 'Unexpected local Sass file; compare against remote theme before retaining'
    if name.startswith('_includes/') or name.startswith('_layouts/'):
        return 'theme override', 'Local template: review rendered output against upstream before removal'
    if name.startswith(('_pages/', '_bibliography/', 'files/')) or name == 'index.md':
        return 'academic content', 'Site-authored academic content, bibliography or CV file'
    if name.startswith('assets/bibliography/'):
        return 'bibliography style', 'APS CSL formatting used by Jekyll Scholar'
    if name.startswith(('assets/images/', 'favicons/')):
        return 'media', 'Retained media or favicon; may include photographs reserved for future pages'
    if name.startswith('assets/js/lunr/'):
        return 'search asset', 'Search-specific code; remaining overrides should be browser-tested'
    if name.startswith(('scripts/', 'tests/')):
        return 'development tooling', 'Audit, migration or regression test; excluded from deployed Jekyll output'
    if name.startswith(('.github/', 'docs/')) or name in ('Gemfile','Gemfile.lock','_config.yml','.gitignore','README.md','LICENSE'):
        return 'project infrastructure', 'Build configuration, documentation, or repository metadata'
    if name.startswith('_data/'):
        return 'site data', 'Navigation, CV or research metadata'
    return 'review', 'Classify this file manually'


def main():
    root = Path(__file__).resolve().parent.parent
    names = subprocess.check_output(['git', '-C', str(root), 'ls-files', '--cached', '--others', '--exclude-standard'], text=True).splitlines()
    rows = [(name, *category(name)) for name in names if (root/name).is_file()]
    out = root.parent/'website-file-inventory.csv'
    with out.open('w',newline='', encoding='utf8') as f:
        writer = csv.writer(f)
        writer.writerow(('path','category','reason'))
        writer.writerows(rows)
    remaining = [name for name,c,_ in rows if c == 'review']
    print(f'{len(rows)} files inventoried: {out}')
    if remaining:
        print('Unclassified paths:', *remaining, sep='\n  ', file=sys.stderr)
        return 1
    print('No uncategorized files.')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
