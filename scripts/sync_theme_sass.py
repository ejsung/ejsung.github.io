#!/usr/bin/env python3
"""Safely refresh the site's Sass tree from a pinned Minimal Mistakes release.

The theme recommends retaining a complete _sass tree when Sass partials are
customized. For locally changed partials, use a three-way merge between the
old upstream release, the local file, and the target upstream release.

Dry-run by default; does not touch the repository unless --apply is supplied.
"""

import argparse
import re
import subprocess
import sys
import tempfile
from pathlib import Path


def git(repo: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(
        ["git", "-C", str(repo), *args],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=check,
    )


def tree_paths(repo: Path, ref: str) -> set[str]:
    proc = git(repo, "ls-tree", "-r", "-z", "--name-only", ref, "--", "_sass")
    return {p.decode() for p in proc.stdout.split(b"\0") if p}


def content(repo: Path, ref: str, path: str) -> bytes:
    return git(repo, "show", f"{ref}:{path}").stdout


def three_way_merge(local: bytes, base: bytes, updated: bytes) -> tuple[int, bytes]:
    with tempfile.TemporaryDirectory(prefix="sass-merge-") as tmp:
        files = [Path(tmp) / name for name in ("local.scss", "base.scss", "updated.scss")]
        for p, data in zip(files, (local, base, updated)):
            p.write_bytes(data)
        proc = subprocess.run(
            ["git", "merge-file", "-p", "--diff3", *map(str, files)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        if proc.returncode > 1:
            raise RuntimeError(proc.stderr.decode(errors="replace"))
        return proc.returncode, proc.stdout


# Recognize *only* the three conflicts already audited for this website.
# Unexpected conflicts still stop the migration instead of choosing a side.
CONFLICT_HUNK = re.compile(
    r"(?ms)^<<<<<<< [^\n]*\n(.*?)^\|\|\|\|\|\|\| [^\n]*\n"
    r"(.*?)^=======$\n(.*?)^>>>>>>> [^\n]*\n"
)


CUSTOM_ACADEMIC_ICON_COLORS = """  // Site-specific academic/social icon colors (retained from 4.24.0).
  .fa-bluesky,
  .fa-square-bluesky {
    color: #1185fe;
  }

  .fa-orcid {
    color: #A6CE39;
  }

  .fa-google-scholar {
    color: #4285F4;
  }

  .fa-researchgate {
    color: #00CCBB;
  }
"""


def resolve_reviewed_conflict(path: str, candidate: bytes) -> bytes | None:
    """Resolve precisely audited 4.24.0 -> 4.28.0 Sass conflicts.

    The candidate is the diff3 output. Each accepted resolution requires one
    conflict hunk with the exact expected local/base/upstream text. Any change
    to the conflict's structure returns None and stops the whole migration.
    """
    text = candidate.decode("utf-8")
    hunks = list(CONFLICT_HUNK.finditer(text))
    if len(hunks) != 1:
        return None

    hunk = hunks[0]
    local, base, upstream = hunk.groups()

    if path == "_sass/minimal-mistakes/_navigation.scss":
        if (local, base, upstream) != (
            "        visibility: hidden;\n        left: 0;\n",
            "        left: 0;\n",
            "        inset-inline-start: 0;\n",
        ):
            return None
        resolved = "        visibility: hidden;\n        inset-inline-start: 0;\n"

    elif path == "_sass/minimal-mistakes/_sidebar.scss":
        if (base != "      float: right;\n" or
                local.replace("      float: right;", "      float: inline-end;", 1) != upstream):
            return None
        resolved = upstream

    elif path == "_sass/minimal-mistakes/_utilities.scss":
        # The only local change to this hunk was inserting four icon-color
        # rules immediately ahead of .fa-vimeo in the old selector list.
        expected_insert = CUSTOM_ACADEMIC_ICON_COLORS.split("  // Site-specific academic/social icon colors (retained from 4.24.0).\n", 1)[1]
        expected_local = base.replace(
            "  .fa-vimeo,\n", expected_insert + "\n  .fa-vimeo,\n", 1
        )
        if (local != expected_local or
                "  @each $color, $icons in (\n" not in upstream or
                "    #{$icons} {\n      color: $color;\n    }" not in upstream):
            return None
        resolved = upstream.rstrip("\n") + "\n\n" + CUSTOM_ACADEMIC_ICON_COLORS.rstrip("\n") + "\n"

    else:
        return None

    merged = text[:hunk.start()] + resolved + text[hunk.end():]
    if any(marker in merged for marker in ("<<<<<<<", "|||||||", ">>>>>>>")):
        return None
    return merged.encode("utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--upstream", type=Path, default=Path("../minimal-mistakes-upstream"))
    parser.add_argument("--old-tag", default="4.24.0")
    parser.add_argument("--new-tag", default="4.28.0")
    parser.add_argument("--apply", action="store_true", help="Write and stage changes; default is read-only")
    parser.add_argument("--report", type=Path, help="Optional report location, preferably outside the repository")
    args = parser.parse_args()

    root = Path.cwd().resolve()
    upstream = args.upstream.resolve()
    if not (root / ".git").exists():
        print("STOP: Run from the website Git repository root.", file=sys.stderr)
        return 2
    if not (upstream / ".git").exists():
        print(f"STOP: Upstream repository not found at {upstream}", file=sys.stderr)
        return 2

    if git(root, "status", "--porcelain").stdout.strip():
        print("STOP: Commit/stash outstanding changes before running.", file=sys.stderr)
        return 2

    config = (root / "_config.yml").read_text()
    if not re.search(r"(?m)^\s*remote_theme\s*:\s*['\"]?mmistakes/minimal-mistakes@" + re.escape(args.new_tag) + r"(?:['\"]|\s|$)", config):
        print(f"STOP: _config.yml is not pinned to {args.new_tag}; don't mix theme releases.", file=sys.stderr)
        return 2

    for ref in (args.old_tag, args.new_tag):
        if git(upstream, "rev-parse", "--verify", f"{ref}^{{commit}}", check=False).returncode:
            print(f"STOP: Missing upstream Git tag {ref}", file=sys.stderr)
            return 2

    old_paths = tree_paths(upstream, args.old_tag)
    new_paths = tree_paths(upstream, args.new_tag)
    local_paths = {
        p.relative_to(root).as_posix()
        for p in (root / "_sass").rglob("*") if p.is_file()
    }

    writes: dict[str, bytes] = {}
    deletes: list[str] = []
    preserved: list[str] = []
    merged: list[str] = []
    conflicts: list[tuple[str, bytes]] = []
    unchanged = 0

    for path in sorted(local_paths | new_paths):
        local = (root / path).read_bytes() if path in local_paths else None
        previous = content(upstream, args.old_tag, path) if path in old_paths else None
        latest = content(upstream, args.new_tag, path) if path in new_paths else None

        if local is None:
            if latest is not None:
                writes[path] = latest
            continue

        if previous is not None and local == previous:
            desired = latest  # discard old upstream copy (or retire removed partial)
        elif latest is not None and local == latest:
            desired = latest
        elif previous is not None and latest is not None:
            status, candidate = three_way_merge(local, previous, latest)
            if status:
                resolved = resolve_reviewed_conflict(path, candidate)
                if resolved is None:
                    conflicts.append((path, candidate))
                    continue
                candidate = resolved
            desired = candidate
            merged.append(path)
        elif previous is None and latest is None:
            preserved.append(path)  # project-only Sass file
            unchanged += 1
            continue
        else:
            conflicts.append((path, b"Upstream file added/removed; local differs. Requires manual review.\n"))
            continue

        if desired is None:
            deletes.append(path)
        elif desired != local:
            writes[path] = desired
        else:
            unchanged += 1

    lines = [
        f"Sass sync: Minimal Mistakes {args.old_tag} -> {args.new_tag}",
        f"Create/update: {len(writes)} files",
        f"Delete: {len(deletes)} files",
        f"Locally customized partials merged: {len(merged)}",
        f"Unchanged: {unchanged}",
        f"Local-only files preserved: {len(preserved)}",
        f"Merge conflicts / manual decisions: {len(conflicts)}",
        "",
        "Merged customized partials:",
        *(f"  {p}" for p in merged),
        "",
        "Local-only files preserved:",
        *(f"  {p}" for p in preserved),
        "",
        "Conflicts:",
        *(f"  {p}" for p, _ in conflicts),
    ]
    if conflicts:
        lines += ["", "=== MERGE-CONFLICT DETAILS (NOT APPLIED) ==="]
        for path, candidate in conflicts:
            lines += [f"\n=== {path} ===", candidate.decode(errors="replace")]

    report_text = "\n".join(lines) + "\n"
    print(report_text if not conflicts else "\n".join(lines[: 15 + len(merged) + len(preserved) + len(conflicts)]))
    if args.report:
        report = args.report.resolve()
        if report.is_relative_to(root):
            print("STOP: Write report outside the website repository.", file=sys.stderr)
            return 2
        report.write_text(report_text)
        print(f"Report saved: {report}")

    if conflicts:
        print("STOP: No files modified. Review conflicts before applying.", file=sys.stderr)
        return 2
    if not args.apply:
        print("DRY RUN: No files changed. Use --apply to write and stage changes.")
        return 0

    # All changed files were prepared in memory; apply only after verifying
    # the entire tree has no unresolved merges.
    for path in sorted(writes):
        output = root / path
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_bytes(writes[path])
    for path in deletes:
        (root / path).unlink()
    if writes or deletes:
        git(root, "add", "-A", "--", "_sass")
    print("Changes written and staged. Build locally before committing.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
