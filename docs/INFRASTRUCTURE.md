# Infrastructure maintenance — Minimal Mistakes 4.28.1

The site intentionally uses **remote theme + local overrides**, not the old copied/forked theme build. There is no local Node build step. GitHub Actions deploys only from `master`, while `workflow_dispatch` can verify a feature branch.

## Sass overrides and upstream updates

The local `_sass/minimal-mistakes.scss` entry point must remain: Sass resolves
relative imports before theme load paths, and a theme-provided entry point can
bypass local partial overrides. Six site-specific partials remain in
`_sass/minimal-mistakes/`: `_base.scss`, `_masthead.scss`, `_navigation.scss`,
`_page.scss`, `_sidebar.scss`, and `_utilities.scss`. Variables, skins,
third-party Sass and unchanged partials come from the pinned remote theme.

On a future theme upgrade, compare the entry point and each of these six files
with the corresponding old and new upstream files; merge only the site's customizations. Build the
site with the new theme and manually verify navigation, masthead, sidebar,
footer, mobile layout, and academic icon colors. Do not restore a full local
Sass tree. A theme upgrade will legitimately change the compiled CSS, so use a
browser comparison rather than expecting byte-identical CSS across releases.

The removal of redundant copies of **the same pinned theme release** must
be validated with a byte-for-byte comparison of compiled `assets/css/main.css`
before and after the cleanup. Do not commit the cleanup if this comparison fails.

## Deployment checks

The GitHub Pages workflow validates the presence of generated CSS, remote theme JavaScript, custom JavaScript, and the homepage. It retains the committed `Gemfile.lock` for reproducible builds and retains `webrick` for Jekyll's local server. Ruby dependencies are resolved and pinned in `Gemfile.lock`; update them with `scripts/update_dependencies.sh` and validate in CI.

The Sass converter's `quiet_deps` and `silence_deprecations: [import]` settings only suppress known upstream deprecation noise; they do not address the deprecated source itself, suppress Sass errors, or guarantee future Dart Sass compatibility.

When all branch tests pass, manually run **Build and deploy Jekyll site to GitHub Pages** with this feature branch selected on GitHub Actions (the deployment job remains gated to `master`) before merging to `master`.
