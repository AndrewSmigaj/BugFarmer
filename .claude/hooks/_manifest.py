#!/usr/bin/env python3
"""Shared loader for .claude/manifest.json — the ONE source the gate/drift hooks read
(authoring_gates, command_gates, command_viewers, doc_coverage). Pure stdlib.

Import-safe: only function defs, no side effects at import. Callers MUST invoke load()
INSIDE their own fail-open try/except — a missing or malformed manifest raises, and the
caller's `except` degrades the gate to "allow" (a gate must never wall off the workflow it
disciplines). path_matches() is the shared glob matcher (authoring gate + doc-drift).
"""
import os
import json
from pathlib import PurePosixPath

# Default path is .claude/manifest.json (one dir up from hooks). CLAUDE_MANIFEST_PATH overrides it —
# used by selftest.py to point at a missing/broken file and prove the gates still fail-open (allow).
_MANIFEST = os.environ.get("CLAUDE_MANIFEST_PATH") or os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "manifest.json")


def load():
    """Return the manifest dict. Raises on missing/malformed file (caller must be fail-open)."""
    with open(_MANIFEST) as f:
        return json.load(f)


def path_matches(file_path, globs):
    """True if file_path matches ANY glob. Right-anchored + component-aware (PurePosixPath.match:
    '*' does NOT cross '/'), so 'nakama/data/entities/*.json' matches an absolute or repo-relative
    path ending in that shape but NOT a sibling dir. Backslashes normalized for Windows paths."""
    p = PurePosixPath((file_path or "").replace("\\", "/"))
    for g in globs or []:
        try:
            if p.match(g):
                return True
        except Exception:
            continue
    return False


def _same_path(changed, target):
    """True if a changed path (absolute or repo-relative) IS the repo-relative target doc."""
    c = (changed or "").replace("\\", "/")
    t = (target or "").replace("\\", "/")
    return c == t or c.endswith("/" + t)


def doc_drift(changed_paths, m):
    """Given the changed repo paths (this session's edits, or git-staged files), return
    [(doc, trigger_source), ...] for each code_doc whose `covers` matched a changed source path
    but whose own doc file was NOT among the changed paths. This is the shared drift check used by
    both the Stop hook (check_doc_drift.py) and the pre-commit backstop (check_staged_drift.py)."""
    changed = [c for c in (changed_paths or []) if c]
    out = []
    for row in m.get("doc_coverage", []):
        if row.get("kind") != "code_doc":
            continue
        covers = row.get("covers", [])
        doc = row.get("doc", "")
        trig = next((c for c in changed if path_matches(c, covers)), None)
        if not trig:
            continue
        if not any(_same_path(c, doc) for c in changed):
            out.append((doc, trig))
    return out
