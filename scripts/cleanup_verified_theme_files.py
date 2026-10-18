#!/usr/bin/env python3
"""Safely retire redundant local Minimal Mistakes include/layout overrides.

Reads the file-by-file audit CSV, then independently checks that each proposed
local file is byte-for-byte equal to its counterpart in the theme version
pinned by _config.yml. Without --apply, only prints candidates.

Does not modify custom templates, Sass, JavaScript or theme configuration.
"""

import argparse
import csv
import re
import subprocess
from pathlib import Path


def run(*args, cwd=None, check=False):
    return subprocess.run(
        args, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        check=check,
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--audit", type=Path, default=Path("../theme-override-audit.csv"))
    parser.add_argument("--upstream", type=Path, default=Path("../minimal-mistakes-upstream"))
    parser.add_argument("--ref", default="4.28.0", help="Must match remote_theme in _config.yml")
    parser.add_argument("--apply", action="store_true", help="Stage verified removals with git rm")
    args = parser.parse_args()

    site = Path.cwd()
    config_file = site / "_config.yml"
    if not config_file.is_file():
        parser.error("Run this script from the website repository root")
    config = config_file.read_text(encoding="utf-8")
    pinned = re.search(r'^\s*remote_theme\s*:\s*["\']?mmistakes/minimal-mistakes@([\w.\-]+)', config, re.M)
    if not pinned or pinned.group(1) != args.ref:
        parser.error("The --ref value must match the pinned Minimal Mistakes remote_theme in _config.yml")
    upstream = args.upstream.resolve()
    if not (upstream / ".git").exists():
        parser.error("Upstream checkout is missing; check --upstream")
    if not args.audit.is_file():
        parser.error("Audit CSV is missing; check --audit")
    repo_root = run("git", "rev-parse", "--show-toplevel", cwd=site)
    if repo_root.returncode != 0 or Path(repo_root.stdout.decode().strip()) != site.resolve():
        parser.error("Run this script from the Git repository root")
    if args.apply and run("git", "status", "--porcelain", cwd=site).stdout.strip():
        parser.error("Working tree must be clean before --apply; commit audit tooling first")

    verified = []
    skipped = []
    with args.audit.open(newline="", encoding="utf-8") as fp:
        for row in csv.DictReader(fp):
            path = row["path"]
            if row["status"] != "identical to current upstream":
                continue
            if not path.startswith(("_includes/", "_layouts/")):
                continue
            relative = Path(path)
            if relative.is_absolute() or ".." in relative.parts:
                skipped.append((path, "unsafe path"))
                continue
            local = site / relative
            if not local.is_file():
                skipped.append((path, "missing local file"))
                continue
            tracked = run("git", "ls-files", "--error-unmatch", "--", path, cwd=site)
            if tracked.returncode:
                skipped.append((path, "not tracked by Git"))
                continue
            source = run("git", "-C", str(upstream), "show", f"{args.ref}:{path}")
            if source.returncode != 0:
                skipped.append((path, "missing at pinned tag"))
                continue
            if local.read_bytes() != source.stdout:
                skipped.append((path, "not byte-identical at pinned tag"))
                continue
            verified.append(path)

    print(f"Verified removals against {args.ref}: {len(verified)}")
    for path in verified:
        print(f"  {path}")
    if skipped:
        print(f"Skipped (left untouched): {len(skipped)}")
        for path, reason in skipped:
            print(f"  {path}: {reason}")
    if not args.apply:
        print("DRY RUN — no files changed. Add --apply after reviewing the list.")
        return
    if not verified:
        print("No verified candidates; nothing changed.")
        return
    subprocess.run(["git", "rm", "--", *verified], cwd=site, check=True)
    print(f"Staged {len(verified)} removals; build and compare before committing.")


if __name__ == "__main__":
    main()
