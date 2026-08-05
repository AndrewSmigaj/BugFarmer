#!/usr/bin/env python3
"""Pre-commit backstop — called by .githooks/pre-commit. Blocks a commit where an outfit's
`current/CURRENT.md` and its `current/` folder disagree.

WHY THIS EXISTS
---------------
`promote.py` makes recording a decision inseparable from acting on it. This catches the one way round
that: copying a file into `current/` by hand. One checkable question, no intent guessing —

    Does CURRENT.md describe exactly what is in current/ ?

A file in `current/` with no ledger row, or a row pointing at a file that isn't there, fails the commit.
`anim/` IS ledgered. It used to be excluded as derived output, but the MOTION is the thing being chosen
and the gif is the record of that choice — an agreed animation that is not ledgered is exactly what went
missing on 2026-08-04.

Deliberately a GIT hook rather than a Claude Code hook: git hooks are live the moment they are wired,
where Claude Code hooks are snapshotted at session start and would not take effect until a restart.

FAIL-OPEN on its own errors: a bug in this checker must NEVER block commits, so any exception -> exit 0
(allow). Only a genuine detected mismatch returns exit 1 (block). Override with `git commit --no-verify`.

Outfit roots come from git, or from $CLAUDE_SPRITE_ROOT for tests.
"""
import os
import sys

# `anim/` USED to be excluded as derived output, regenerated from the frames. That is no longer true:
# the MOTION is the thing being chosen, and the gif is the record of that choice. An agreed animation
# that is not ledgered is exactly what went missing on 2026-08-04.
DERIVED = ()
IMG = (".png", ".gif")
LEDGER = "CURRENT.md"


def _root():
    override = os.environ.get("CLAUDE_SPRITE_ROOT")
    if override:
        return override
    here = os.path.dirname(os.path.abspath(__file__))
    repo = os.path.dirname(os.path.dirname(here))
    return os.path.join(repo, "tools", "_generated", "player", "outfits")


def _current_files(cur):
    """Ledgerable files under current/, relative to it. Mirrors promote.current_files."""
    out = []
    for root, dirs, files in os.walk(cur):
        dirs[:] = [d for d in dirs if d not in DERIVED]
        for f in files:
            if f == LEDGER:
                continue
            if os.path.splitext(f)[1].lower() in IMG:
                out.append(os.path.relpath(os.path.join(root, f), cur).replace(os.sep, "/"))
    return set(out)


def _ledger_files(path):
    listed = set()
    with open(path, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            if not line.startswith("| ") or line.startswith("| file "):
                continue
            if set(line.strip()) <= set("|- "):
                continue
            cell = line.strip().strip("|").split("|")[0].strip().strip("`")
            if cell:
                listed.add(cell)
    return listed


def problems(root):
    found = []
    if not os.path.isdir(root):
        return found
    for outfit in sorted(os.listdir(root)):
        cur = os.path.join(root, outfit, "current")
        if not os.path.isdir(cur):
            continue                      # not migrated yet — nothing to check
        ledger = os.path.join(cur, LEDGER)
        on_disk = _current_files(cur)
        if not os.path.exists(ledger):
            if on_disk:
                found.append((outfit, f"current/ has {len(on_disk)} file(s) but no {LEDGER}"))
            continue
        listed = _ledger_files(ledger)
        for f in sorted(on_disk - listed):
            found.append((outfit, f"in current/ but not in {LEDGER}: {f}"))
        for f in sorted(listed - on_disk):
            found.append((outfit, f"in {LEDGER} but missing from current/: {f}"))
    return found


def main():
    found = problems(_root())
    if not found:
        return 0
    sys.stderr.write("\n⛔ Sprite ledger (pre-commit) — CURRENT.md does not match current/:\n")
    for outfit, msg in found[:20]:
        sys.stderr.write(f"    - {outfit}: {msg}\n")
    if len(found) > 20:
        sys.stderr.write(f"    … and {len(found) - 20} more\n")
    sys.stderr.write("\nPromote properly so the decision is recorded:\n"
                     "    python3 tools/player_sprites/promote.py <outfit> <path> \"<their words>\"\n"
                     "Or override:  git commit --no-verify\n\n")
    return 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:                                    # noqa: BLE001 - fail-open by design
        sys.stderr.write(f"[check_sprite_ledger] non-fatal: {exc}\n")
        sys.exit(0)
