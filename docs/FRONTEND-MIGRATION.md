# Frontend modernization (Minimal Mistakes 4.28.1)

The site uses the **remote theme's** `assets/js/main.min.js` instead of
maintaining a local copy of the upstream jQuery + plugin bundle. Site-specific
sidebar and heading-permalink styling behavior has been extracted into
`assets/js/site-custom.js` and loaded from `_includes/scripts.html`.

Also updated: MathJax 2 to MathJax 4 (with `$...$`, `\(...\)`, `$$...$$`,
`\[...\]` support); Academicons to the maintained 1.9.6 CDN stylesheet.

Originally migrated on 4.28.0 and subsequently aligned with theme 4.28.1.
After applying the patch and removing the obsolete local JavaScript bundle,
run `bundle exec jekyll build` and check that `_site/assets/js/main.min.js`
exists: this verifies that the remote theme supplies the bundle.

The old Node build setup (`package.json`, `package-lock.json`, `banner.js`,
`assets/js/_main.js`, `assets/js/plugins/`, `assets/js/vendor/`) is no longer
needed. Keep the customized `assets/js/lunr/lunr-store.js`; review the other
Lunr assets separately if the search index works after migration.

## Browser regression checks

1. Header navigation menu at desktop and mobile widths; search toggle.
2. Sticky author sidebar, right-hand table of contents, and sticky footer.
3. Permalink icons on headings, image lightbox and copy-code buttons.
4. MathJax examples: `$E=mc^2$` (inline), `\(E=mc^2\)`, and `$$E=mc^2$$`.
5. ORCID, Google Scholar, ResearchGate, and other academic icons.
6. Local `/assets/js/main.min.js` should respond, with a 4.28.1 theme banner.

Do not merge into `master` if these checks fail. Jekyll building successfully
alone cannot validate dynamic JavaScript or external CDN resources.
