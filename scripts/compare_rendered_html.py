#!/usr/bin/env python3
"""Compare Jekyll HTML output, ignoring only whitespace-only lines.

This is a diagnostic for theme migrations, not a substitute for testing layouts
in a browser. Nonblank text, attributes, URLs, and tag changes remain visible.
"""

import argparse
import difflib
from pathlib import Path


def significant_lines(path: Path) -> list[str]:
    return [line for line in path.read_text(encoding="utf-8").splitlines()
            if line.strip()]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("before", type=Path, help="Previous Jekyll output directory")
    parser.add_argument("after", type=Path, help="Current Jekyll output directory")
    parser.add_argument("--max-diffs", type=int, default=6,
                        help="Number of changed pages for which to print examples")
    args = parser.parse_args()
    if not args.before.is_dir() or not args.after.is_dir():
        parser.error("Both arguments must be built site directories")

    old_files = {f.relative_to(args.before) for f in args.before.rglob("*.html")}
    new_files = {f.relative_to(args.after) for f in args.after.rglob("*.html")}
    missing = sorted(old_files - new_files)
    added = sorted(new_files - old_files)
    changed = []
    blank_lines_only = []
    for relative in sorted(old_files & new_files):
        before = (args.before / relative).read_bytes()
        after = (args.after / relative).read_bytes()
        if before == after:
            continue
        before_lines = significant_lines(args.before / relative)
        after_lines = significant_lines(args.after / relative)
        if before_lines == after_lines:
            blank_lines_only.append(relative)
        else:
            changed.append((relative, before_lines, after_lines))

    print(f"HTML files: {len(old_files)} before, {len(new_files)} after")
    print(f"Changed only by blank lines: {len(blank_lines_only)}")
    print(f"Meaningful HTML text differences: {len(changed)}")
    print(f"Added pages: {len(added)}; missing pages: {len(missing)}")
    for relative in added[:args.max_diffs]:
        print(f"  ADDED {relative}")
    for relative in missing[:args.max_diffs]:
        print(f"  MISSING {relative}")
    for relative, before, after in changed[:args.max_diffs]:
        print(f"\n--- {relative} ---")
        for line in list(difflib.unified_diff(
            before, after, fromfile="previous", tofile="current", lineterm="", n=2
        ))[:35]:
            print(line)
    if len(changed) > args.max_diffs:
        print(f"... and {len(changed) - args.max_diffs} more changed pages")
    return 1 if missing or added or changed else 0


if __name__ == "__main__":
    raise SystemExit(main())
