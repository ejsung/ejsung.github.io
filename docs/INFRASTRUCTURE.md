# Infrastructure maintenance — Minimal Mistakes 4.28.1

The site intentionally uses **remote theme + local overrides**, not the old copied/forked theme build. There is no local Node build step. GitHub Actions deploys only from `master`, while `workflow_dispatch` can verify a feature branch.

## Align local Sass with the remote theme

**Important:** `_sass/` remains in this repository because six partials have intentional customizations. Updating the remote theme ref alone does *not* upgrade those local partials. After applying the 4.28.1 configuration update on a clean branch, use the existing audit utility to synchronize from 4.28.0 to 4.28.1:

```bash
python3 scripts/sync_theme_sass.py \
  --old-tag 4.28.0 --new-tag 4.28.1 \
  --report ../sass-4.28.1-report.txt
```

If it reports zero conflicts, apply and validate:

```bash
python3 scripts/sync_theme_sass.py \
  --old-tag 4.28.0 --new-tag 4.28.1 \
  --apply --report ../sass-4.28.1-report.txt
JEKYLL_ENV=production bundle exec jekyll build
node --check assets/js/site-custom.js
git diff --cached --check
```

If it reports conflicts, stop and resolve *those files only*. Do not replace customized partials with upstream wholesale. Inspect and test the fixed masthead, sidebar, navigation underline, heading links, typography, and mobile layout before committing.

## Deployment checks

The GitHub Pages workflow validates the presence of generated CSS, remote theme JavaScript, custom JavaScript, and the homepage. It retains the committed `Gemfile.lock` for reproducible builds and retains `webrick` for Jekyll's local server. No speculative dependency bump is included in this stage.

The Sass converter's `quiet_deps` and `silence_deprecations: [import]` settings only suppress known upstream deprecation noise; they do not address the deprecated source itself, suppress Sass errors, or guarantee future Dart Sass compatibility.

When all branch tests pass, manually run **Build and deploy Jekyll site to GitHub Pages** with this feature branch selected on GitHub Actions (the deployment job remains gated to `master`) before merging to `master`.
