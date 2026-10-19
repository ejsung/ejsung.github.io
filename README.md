# Personal academic website

Source for [ejsung.github.io](https://ejsung.github.io/), built with [Jekyll](https://jekyllrb.com/) and the [Minimal Mistakes](https://mmistakes.github.io/minimal-mistakes/) remote theme.

## Develop locally

The GitHub Actions build uses Ruby 3.3.12, Jekyll 4, and the dependencies locked in `Gemfile.lock`. No Node package installation or JavaScript bundling is needed; upstream Minimal Mistakes supplies the theme JavaScript.

```bash
bundle install
bundle exec jekyll serve
```

Visit <http://127.0.0.1:4000/>. After changing `_config.yml`, restart Jekyll.

To verify a production-style build locally:

```bash
JEKYLL_ENV=production bundle exec jekyll build
node --check assets/js/site-custom.js
```

## Repository organization

- `_pages/`, `_data/`, `_bibliography/`: site-specific content and data.
- `_includes/`, `_layouts/`: intentionally retained local overrides; corresponding local files take precedence over remote theme files.
- `_sass/`: the theme Sass import entry point and six site-customized partials; unchanged Sass and vendor files come from the pinned remote theme.
- `assets/css/main.scss`: site stylesheet entry point and site-specific styles.
- `assets/js/site-custom.js`: custom website behavior; `assets/js/main.min.js` is supplied by the remote theme at build time.
- `scripts/`, `docs/`: maintenance tools and documentation, excluded from the generated website.

## Publishing

`.github/workflows/jekyll.yml` builds on pushes to `master` and supports manual runs for branch verification. Only `master` deploys to GitHub Pages. Do not merge a maintenance branch until its local build and browser checks pass.

See [docs/MODERNIZATION.md](docs/MODERNIZATION.md), [docs/FRONTEND-MIGRATION.md](docs/FRONTEND-MIGRATION.md), and [docs/INFRASTRUCTURE.md](docs/INFRASTRUCTURE.md) for migration history and validation instructions.

## Validate and update dependencies

```bash
python3 -m unittest discover -s tests -v
python3 scripts/inventory_repo.py
JEKYLL_ENV=production bundle exec jekyll build
python3 scripts/check_site.py --root _site
```

After committing source changes, run `bash scripts/update_dependencies.sh` on
macOS to resolve and test compatible updated Ruby gems. Review and commit the
new `Gemfile.lock` separately. Do not manually edit the lockfile to invent
versions. Check GitHub Actions on the modernization branch before deployment.

See [architecture and override ownership](docs/ARCHITECTURE.md) and the
[remaining release gates](docs/MODERNIZATION.md).
