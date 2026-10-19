# Repository architecture and ownership

The public site is [ejsung.github.io](https://ejsung.github.io), using Jekyll 4
and the Minimal Mistakes **4.28.1 remote theme**. This repository is not a
fork of the theme, and its local copies should not be replaced indiscriminately.

## What is owned here

| Area | Purpose | Upgrade policy |
| --- | --- | --- |
| `_pages/`, `index.md`, `_data/` | Authored pages, CV metadata, conferences and navigation | Preserve user content; do not rewrite during theme upgrades |
| `_bibliography/`, `assets/bibliography/`, `_layouts/bibliography.html` | Publication data, APS CSL, author highlighting | Keep custom layout and format intentionally |
| `_layouts/single.html`, `_includes/page__date.html`, `_includes/page__meta.html` | Custom academic page layout and timestamp behavior | Compare with corresponding upstream files at each new theme version |
| `_includes/author-profile.html`, `_includes/breadcrumbs.html`, `_includes/video` | Customized profile, navigation and video embeds | Retain until behavior can be replaced with documented theme APIs |
| `_includes/head.html`, `_includes/head/custom.html`, `_includes/scripts.html` | Site metadata, favicons, pinned CDN resources, MathJax 4 and custom scripts | Merge upstream template changes carefully |
| `_sass/` | One local Sass import entry point (`minimal-mistakes.scss`) and six customized partials (`_base`, `_masthead`, `_navigation`, `_page`, `_sidebar`, `_utilities`) | The local entry point ensures custom partials are used while unmodified Sass, skins and vendors inherit from the remote theme |
| `assets/js/site-custom.js` | Sticky sidebar and heading permalink behavior | Keep independent of upstream JavaScript bundle |
| `assets/js/lunr/lunr-store.js` | Custom Lunr page search index | Preserve; other Lunr files load from the remote theme |
| `assets/images/`, `favicons/`, `files/` | Authored images and CV PDF | Retain authored media unchanged during code/dependency maintenance |
| `scripts/`, `tests/`, `docs/` | Tooling, tests and documentation | Excluded from published `_site` output |

To classify every tracked path, run `python3 scripts/inventory_repo.py`.
It writes `../website-file-inventory.csv` and exits nonzero for unclassified paths.

## Sass ownership and remaining upstream limitations

The repository keeps one local `_sass/minimal-mistakes.scss` import entry point
and six customized partials. Keeping the local entry point is necessary so
relative Sass imports find those customized partials rather than bypassing them
via the remote theme entry point. Minimal Mistakes 4.28.1 supplies all unchanged
partials, skins and vendored Breakpoint/Susy/Magnific Popup code. Future theme
upgrades may require updating the six overridden partials and entry point.

This reduces duplicated upstream code but does **not** modernize Minimal
Mistakes' Sass syntax: upstream still uses deprecated `@import` and its own
vendor libraries. Rewriting those is a separate upstream/theme migration,
not a safe local cleanup. A CSS equivalence check is required when removing
same-version partial copies, and manual layout tests are still required.

## External and Ruby dependencies

- Remote Minimal Mistakes: `4.28.1` (pinned)
- Font Awesome: `7.3.1` (pinned CDN)
- MathJax: `4.1.3` (pinned CDN)
- Academicons: `1.9.6` (pinned CDN)
- Jekyll and plugins: pinned by `Gemfile.lock`; use `scripts/update_dependencies.sh`
  on the development Mac, then commit and test the resulting lockfile.
- Theme-provided jQuery, plugins, Lunr source and JS bundle: do not duplicate
  them locally without a documented modification.

Local link checking deliberately does **not** make network requests. External
URL availability, accessibility audits and screenshot diffs require additional
checks in a real browser or network-capable environment.
