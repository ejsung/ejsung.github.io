#!/usr/bin/env bash
# Update all Gemfile-compatible Ruby gems on the development Mac.
# Do not commit until the site builds and CI passes with the new Gemfile.lock.
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."

if ! command -v bundle >/dev/null 2>&1; then
  echo "Bundler is not in PATH; use the Ruby environment used to build Jekyll." >&2
  exit 1
fi
if [[ -n "$(git status --porcelain)" ]]; then
  echo "Commit the source modernization changes first; dependency upgrades require a clean working tree." >&2
  exit 1
fi

# Resolve all gems within Gemfile constraints, then validate on this branch.
bundle update
bundle check
JEKYLL_ENV=production bundle exec jekyll build
python3 -m unittest discover -s tests -v
python3 scripts/check_site.py --root _site
node --check assets/js/site-custom.js

echo "Dependency upgrade validated locally. Review Gemfile.lock and run the GitHub Actions branch build before committing."
echo "Optional vulnerability review: gem install bundler-audit && bundle audit check --update"
git diff -- Gemfile.lock
