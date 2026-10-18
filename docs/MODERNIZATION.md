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

## Stage 2C — Bulk include/layout migration

The 4.24.0-to-4.28.0 upstream diff has been reviewed. The bulk patch removes
33 **unchanged 4.24.0 copies** of Minimal Mistakes `_includes` and `_layouts`
that were present in the site's initial audit. The pinned remote theme remains
`4.28.0`; Jekyll resolves those paths from the remote theme instead.

**Never remove** the locally customized template overrides just because a theme
file with the same name exists upstream. In particular, this stage retains
`_layouts/single.html`, `_layouts/bibliography.html`, `_includes/page__date.html`,
`_includes/scripts.html`, and the custom author profile, SEO-adjacent includes,
and site-specific navigation templates.

Validation, from the website root:

```bash
bundle exec jekyll build > ../website-bulk-templates-build.log 2>&1
python3 scripts/compare_rendered_html.py \
  ../website-stage2c-reference-output _site
```

`compare_rendered_html.py` deliberately ignores **only** blank lines. A nonzero
exit means content/markup changed and should be reviewed, not necessarily that
the migration failed. A successful build is necessary but is not visual proof:
review homepage, mobile navigation, search, CV and Research content, and the
fixed masthead before committing. The feed can change due to generated dates.

Next stages: isolate and migrate custom Sass partials; audit the local JavaScript
bundle and Node toolchain; update obsolete external assets and MathJax; then
update theme version and production CI, with one final regression check.

## Stage 3 — Synchronize Sass with pinned upstream (4.28.0)

The repository customizes several internal Sass partials. **For extensive
partial customizations, Minimal Mistakes recommends retaining the complete
`_sass` tree**, not deleting most partials and relying on load-path fallbacks.
See https://mmistakes.github.io/minimal-mistakes/docs/stylesheets/ .

`scripts/sync_theme_sass.py` synchronizes the **entire** `_sass` tree to the
version already pinned in `_config.yml` (4.28.0). Files identical to old
upstream are replaced outright. Locally changed files get a three-way merge
(`4.24.0`, local, `4.28.0`) so user changes are not silently discarded.
The script stops without writing anything if any merge has a conflict or a
local change cannot be carried forward automatically. No assets, config,
layouts, or JavaScript files are changed by this tool.

First commit this script, then from a **clean** modernization branch:

```bash
python3 scripts/sync_theme_sass.py --report ../sass-upgrade-report.txt
# Only if the above exits successfully with zero conflicts:
python3 scripts/sync_theme_sass.py --apply --report ../sass-upgrade-report.txt
bundle exec jekyll build > ../website-sass-build.log 2>&1
```

Expected: `assets/css/main.css` and theme-related generated content may change
because this updates Sass from 4.24.0 to 4.28.0. Check the local homepage,
mobile nav, fixed masthead, sidebar, footer, and print view. Do **not** commit
on a failed build or a visual regression. `git restore --source=HEAD --staged
--worktree -- _sass` rolls back all uncommitted Sass migration changes.

After stabilization, an optional follow-up can isolate project-specific CSS
into `assets/css/main.scss` and investigate whether removing local `_sass`
completely works with the remote theme; that is a distinct, testable change.
