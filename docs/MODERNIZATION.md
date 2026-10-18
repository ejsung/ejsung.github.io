# Website modernization — working plan

This migration is being developed on `maintenance/modernize-website`, based on
`master`. Keep `hobbies-drop-down` separate until this migration is complete.

## Principles

1. Preserve the site's current appearance, navigation, page URLs, academic
   content, publications, and user-written customization.
2. Use Minimal Mistakes as a **version-pinned remote theme**. Prefer upstream
   theme files rather than checking copies into the site repository.
3. Never delete a local theme file merely because it has the same pathname as
   an upstream file. Compare the actual contents against the old and new tags.
4. Keep changes small and make a working local build before each commit.
5. Keep GitHub deployment restricted to `master` until the branch is reviewed.

## Baseline (first commit)

From the website root:

```bash
bundle exec jekyll build
python3 scripts/site_manifest.py capture _site ../site-before.json
```

For a content-aware comparison to upstream, clone Minimal Mistakes **beside**
the website repository (not inside it):

```bash
git clone https://github.com/mmistakes/minimal-mistakes.git ../minimal-mistakes-upstream
python3 scripts/audit_theme_overrides.py \
  --upstream ../minimal-mistakes-upstream \
  --old-tag 4.24.0 \
  --new-tag 4.28.1 \
  --output ../theme-override-audit.csv
```

The CSV classifies local theme-related files but **does not authorize automatic
removal**. Before removing an old copy, inspect its diff, the theme's new version,
and the pages/styles that depend on it.

Note: for reproducible CI comparison, the existing workflow generates
`_data/research_updated.yml` from Git history; a plain local build may instead
use the page's own update-date fallback. This is an expected build difference.

## Migration stages

- [ ] Capture baseline build, page screenshots and override audit.
- [ ] Update `remote_theme` from 4.28.0 to pinned 4.28.1 and build.
- [ ] Retire redundant `_includes`, `_layouts`, and Sass vendor files carefully.
      Migrate custom masthead/body spacing into an intentional custom stylesheet.
- [ ] Retain research/page update-date logic and customized bibliography output.
- [ ] Inspect JavaScript, search, local CSS, academic icons, and MathJax; update
      only with functional checks for affected pages.
- [ ] Review Gemfile/lockfile, Node tooling and ignored/generated files.
- [ ] Run local build and navigate major pages at desktop and mobile widths.
- [ ] Run the branch's Actions build manually; verify artifacts and deployment
      restrictions before merging to `master`.

## Regression checklist

- Homepage and mobile navigation, fixed/sticky masthead, footer position.
- About, Research, CV, Teaching, Contact and all course pages.
- Publication list: author emphasis, numbering, DOI and arXiv links.
- Research page: correct creation/last-update display.
- Search, sidebar social links and external link behavior.
- Mathematical formulas and bibliography presentation.
- Favicons, photos, CV PDF, search assets and page permalinks.

After each change:

```bash
bundle exec jekyll build
python3 scripts/site_manifest.py capture _site ../site-after.json
python3 scripts/site_manifest.py compare ../site-before.json ../site-after.json
```

A changed checksum is not a failure; investigate unexpected changes before
committing. `sass-embedded` may still produce warnings for `@import` and other
legacy upstream Sass features in version 4.28.1. Do not conceal them until the
actual compatibility state is understood.

## Stage 2: Conservatively retire redundant includes/layouts

The first override audit found 161 theme-related files, including 75 byte-identical
copies of upstream 4.28.1, 55 unmodified copies from 4.24.0, 26 locally
modified files, 3 files absent from the new upstream, and 2 local-only files.

Do **not** delete all 130 upstream copies in one operation. Start with only
local `_includes/` and `_layouts/` copies classified as identical to 4.28.1
**and** independently verified to match the actually pinned remote theme
(4.28.0). This intentionally leaves `_sass/`, `assets/js/`, and every
modified or old-only file untouched.

```bash
# Run from the website repo root after committing this script.
python3 scripts/cleanup_verified_theme_files.py \
  --audit ../theme-override-audit.csv \
  --upstream ../minimal-mistakes-upstream \
  --ref 4.28.0

# Examine the dry-run list. Then stage ONLY the verified removals.
python3 scripts/cleanup_verified_theme_files.py \
  --audit ../theme-override-audit.csv \
  --upstream ../minimal-mistakes-upstream \
  --ref 4.28.0 --apply

bundle exec jekyll build > ../website-stage2-build.log 2>&1
python3 scripts/site_manifest.py capture _site ../site-stage2.json
python3 scripts/site_manifest.py compare ../site-before.json ../site-stage2.json

git diff --cached --stat
```

Review unexpected generated-site changes before committing. If a regression
occurs, restore staged deletions with `git restore --source=HEAD --staged --worktree --
_includes _layouts` while still on the modernization branch. The script
refuses to operate in apply mode with an unclean Git tree. Do not change the
pinned remote theme version until this cleanup is validated.
