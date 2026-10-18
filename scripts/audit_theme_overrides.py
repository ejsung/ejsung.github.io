#!/usr/bin/env python3
"""Compare locally retained Minimal Mistakes files against two upstream tags.

This is a READ-ONLY audit: it makes no changes to either repository.
Requires Python 3.9+ and Git, with the requested tags available locally.
"""

import argparse
import csv
import io
import subprocess
from collections import Counter
from pathlib import Path


THEME_PREFIXES = (
    "_includes/", "_layouts/", "_sass/", "assets/js/",
)
THEME_EXTRAS = {
    "_data/ui-text.yml", "assets/css/main.scss",
    "package.json", "package-lock.json", "banner.js",
}


def git(upstream, *args):
    proc = subprocess.run(
        ["git", "-C", str(upstream), *args],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False,
    )
    if proc.returncode:
        raise RuntimeError(proc.stderr.decode(errors="replace").strip())
    return proc.stdout


def tree(upstream, ref):
    return set(git(upstream, "ls-tree", "-r", "--name-only", ref).decode().splitlines())


def theme_file(path):
    return path.startswith(THEME_PREFIXES) or path in THEME_EXTRAS


def classify(local, old, new):
    if new is None and old is None:
        return "local-only (no upstream counterpart)"
    if new is None:
        return "missing upstream now (inspect)"
    if local == new:
        return "identical to current upstream"
    if old is not None and local == old:
        return "unchanged old copy (review for replacement)"
    return "locally different (manual review)"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--site", type=Path, default=Path("."))
    parser.add_argument("--upstream", type=Path, required=True)
    parser.add_argument("--old-tag", default="4.24.0")
    parser.add_argument("--new-tag", default="4.28.1")
    parser.add_argument("--output", type=Path, default=Path("../theme-override-audit.csv"))
    args = parser.parse_args()
    site = args.site.resolve()
    upstream = args.upstream.resolve()
    if not (site / "_config.yml").is_file():
        parser.error("--site does not look like the website root")
    if not (upstream / ".git").exists():
        parser.error("--upstream must point to a local Git checkout of Minimal Mistakes")
    try:
        old_paths = tree(upstream, args.old_tag)
        new_paths = tree(upstream, args.new_tag)
    except RuntimeError as exc:
        parser.error(f"Cannot read tags: {exc}. Fetch upstream tags first.")
    local_paths = sorted(
        f.relative_to(site).as_posix()
        for f in site.rglob("*")
        if f.is_file() and theme_file(f.relative_to(site).as_posix())
        and not any(p.startswith(".") for p in f.relative_to(site).parts)
    )
    entries = []
    for path in local_paths:
        local = (site / path).read_bytes()
        old = git(upstream, "show", f"{args.old_tag}:{path}") if path in old_paths else None
        new = git(upstream, "show", f"{args.new_tag}:{path}") if path in new_paths else None
        entries.append({
            "path": path,
            "status": classify(local, old, new),
            "exists_in_old": old is not None,
            "exists_in_new": new is not None,
            "upstream_changed": old is not None and new is not None and old != new,
        })
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="", encoding="utf-8") as fp:
        writer = csv.DictWriter(fp, fieldnames=list(entries[0]) if entries else ["path", "status"])
        writer.writeheader()
        writer.writerows(entries)
    print(f"Audited {len(entries)} local theme-related files")
    for status, count in sorted(Counter(e["status"] for e in entries).items()):
        print(f"  {count:3}  {status}")
    print(f"Saved read-only audit: {args.output}")
    print("No files were removed or changed. Review every candidate before deletion.")


if __name__ == "__main__":
    main()
