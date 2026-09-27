#!/usr/bin/env python3
"""Pre-commit backstop — called by .githooks/pre-commit. Blocks a commit whose STAGED source changed
but its doc (per manifest doc_coverage) did not. This is our real backstop absent CI: it catches drift
even if the Stop hook was bypassed. Override a legitimate case with `git commit --no-verify`.

A staged .go/.py file whose change touched only comments (or Python docstrings) is not counted — see
_comments.py.

FAIL-OPEN on its own errors: a bug in this checker must NEVER block commits, so any exception -> exit 0
(allow). Only genuine detected drift returns exit 1 (block). Staged files come from git, or from
$CLAUDE_STAGED_FILES (space/newline-separated) for tests; $CLAUDE_DIFF_CONTENT stands in for their
versions (see _comments.py).
"""
import sys
import os
import subprocess

import _comments
import _manifest


def _staged():
    override = os.environ.get("CLAUDE_STAGED_FILES")
    if override is not None:
        return [x for x in override.replace("\n", " ").split() if x]
    out = subprocess.run(["git", "diff", "--cached", "--name-only", "--diff-filter=ACMR"],
                         capture_output=True, text=True, timeout=15)
    return [x for x in out.stdout.splitlines() if x.strip()]


def main():
    staged = _staged()
    if not staged:
        return 0
    counted = []
    for path in staged:
        if path.endswith(_comments.CODE_SUFFIXES) and _comments.comments_only(path, *_comments.staged_versions(path)):
            sys.stderr.write(f"doc-drift: comments only, not counted — {path}\n")
            continue
        counted.append(path)
    drift = _manifest.doc_drift(counted, _manifest.load())
    seen, items = set(), []
    for doc, trig in drift:
        if doc in seen:
            continue
        seen.add(doc)
        items.append((doc, trig))
    if not items:
        return 0
    sys.stderr.write("\n⛔ Doc-drift (pre-commit) — staged source changed but its doc did not:\n")
    for doc, trig in items:
        sys.stderr.write(f"    - {doc}   (staged source: {trig})\n")
    sys.stderr.write("\nUpdate the doc(s) and re-stage, or override:  git commit --no-verify\n\n")
    return 1


if __name__ == "__main__":
    try:
        code = main()
    except Exception:
        code = 0  # fail-open: a checker bug must never block commits
    sys.exit(code)
