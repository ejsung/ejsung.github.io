# Personal website code and dependency modernization — state and validation

Branch: `maintenance/modernize-website`. Do not merge to `master` before
source cleanup, dependency lockfile updates, branch CI and browser tests pass.

## Scope

Repository code, theme overrides, dependencies, configuration, and tests only.
Photographs and other authored image assets are intentionally untouched.

## What has been implemented

- Migrated theme layouts/includes to pinned Minimal Mistakes 4.28.1 and
  synchronized customized Sass to that release.
- Replaced the old locally built JavaScript bundle with the remote theme bundle;
  retained only site-specific behavior in `assets/js/site-custom.js`.
- Switched to MathJax 4, Academicons 1.9.6 and version-pinned frontend CDNs.
- Removed obsolete local templates, unused Lunr language copies, unused local
  translation table, retired Microsoft/IE metadata, inactive social-link stubs,
  and old JavaScript/npm build infrastructure.
- Corrected broken browser-manifest icon paths without editing any image files.
- Reduced Jekyll configuration to active options, limited workflow job token
  permissions, pinned Ubuntu 24.04, and added local page/asset validation tests.
- Added `scripts/inventory_repo.py` to classify tracked files and record the
  reasons for retaining local theme overrides.

## Verification commands

```bash
python3 -m unittest discover -s tests -v
python3 scripts/inventory_repo.py
node --check assets/js/site-custom.js
JEKYLL_ENV=production bundle exec jekyll build
python3 scripts/check_site.py --root _site
```

The generated-site checker validates internal HTML/CSS links and manifest URLs.
It cannot validate CDN availability, external social/DOI links, scripts at runtime,
layout geometry, mathematical rendering, or performance. Those need browser checks.

## Outstanding release gates — not complete without these

- [ ] Run `scripts/update_dependencies.sh` on the Mac and review the newly
      resolved `Gemfile.lock`; check security advisories with bundler-audit.
- [ ] Run the updated branch GitHub Actions build. It must pass while deployment
      remains skipped.
- [ ] Check desktop/mobile navigation, active search, profile links, MathJax,
      pagination (if used), bibliography, Research timestamps, responsive media,
      fixed masthead, sidebar, footer and academic icons in Firefox.
- [ ] Check browser console, keyboard navigation, and search interaction for regressions.
- [ ] Compare appearance with the pre-modernization site before merging.

The **complete `_sass` tree** is a deliberate, version-matched vendor copy,
not a file classification oversight. Its removal requires a separate, tested
architectural migration; the existing remote theme is not fully Sass-module
modernized upstream. See `docs/ARCHITECTURE.md`.
