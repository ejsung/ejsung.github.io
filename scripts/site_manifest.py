#!/usr/bin/env python3
"""Capture/compare built Jekyll site files using SHA-256 and file size.

Usage:
  python3 scripts/site_manifest.py capture _site ../site-before.json
  python3 scripts/site_manifest.py compare ../site-before.json ../site-after.json
"""

import argparse
import hashlib
import json
from pathlib import Path


def capture(root):
    if not root.is_dir() or not (root / "index.html").exists():
        raise SystemExit("Build the Jekyll site first: expected _site/index.html")
    return {
        file.relative_to(root).as_posix(): {
            "sha256": hashlib.sha256(file.read_bytes()).hexdigest(),
            "bytes": file.stat().st_size,
        }
        for file in sorted(root.rglob("*")) if file.is_file()
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    cap = sub.add_parser("capture", help="Capture built _site file hashes")
    cap.add_argument("site", type=Path)
    cap.add_argument("output", type=Path)
    cmp = sub.add_parser("compare", help="Compare two saved manifests")
    cmp.add_argument("before", type=Path)
    cmp.add_argument("after", type=Path)
    args = parser.parse_args()
    if args.command == "capture":
        manifest = capture(args.site)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
        print(f"Saved {len(manifest)} built files to {args.output}")
        return
    before = json.loads(args.before.read_text())
    after = json.loads(args.after.read_text())
    for label, paths in (
        ("Added", set(after) - set(before)),
        ("Removed", set(before) - set(after)),
        ("Modified", {p for p in set(before) & set(after) if before[p] != after[p]}),
    ):
        paths = sorted(paths)
        print(f"{label}: {len(paths)}")
        for path in paths[:40]:
            print(f"  {path}")
        if len(paths) > 40:
            print(f"  ... {len(paths)-40} more")
    print("Note: different builds may change dates, feeds, or generated metadata.")


if __name__ == "__main__":
    main()
