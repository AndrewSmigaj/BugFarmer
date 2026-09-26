#!/usr/bin/env python3
"""Stop hook — nudge (exit 2) if determinism-critical sim code changed this session but the determinism
GATE was NOT run (no marker from mark_determinism_run.py) and not waived. Stops a turn from ending with an
unverified determinism change — the highest-consequence code in the repo. Waivable per session.

FAIL-OPEN: no edit log / any error -> allow the stop. Cleared automatically the moment the gate runs.
stdin: { "session_id": "...", "stop_hook_active": bool, ... }
"""
import sys
import os
import re
import json

import _manifest


def _safe(s):
    return re.sub(r"[^A-Za-z0-9_.-]", "_", s or "")


def _touchlog(sid):
    return os.path.join(os.environ.get("TMPDIR", "/tmp"), f"claude-touched-{sid}.log")


def _runmarker(sid):
    return os.path.join(os.environ.get("TMPDIR", "/tmp"), f"claude-determinism-run-{sid}")


def _waiver(sid):
    return os.path.join(os.environ.get("TMPDIR", "/tmp"), f"claude-determinism-waiver-{sid}")


def main():
    data = json.load(sys.stdin)
    sid = _safe(data.get("session_id", "nosession"))
    if os.path.exists(_runmarker(sid)) or os.path.exists(_waiver(sid)):
        return  # the gate ran, or the change was waived — allow stop

    log = _touchlog(sid)
    if not os.path.isfile(log):
        return
    with open(log) as f:
        changed = [ln.strip() for ln in f if ln.strip()]

    det = _manifest.load().get("determinism") or {}
    covers = det.get("covers", [])
    hit = next((c for c in changed if _manifest.path_matches(c, covers)), None)
    if not hit:
        return  # no determinism-critical edit this session — allow stop

    hint = det.get("gate_hint", "run the determinism gates (test-changes skill)")
    msg = (
        f"\n⛔ Determinism gate — you changed sim code this session ({hit}) but have NOT run the "
        f"determinism gate. Before ending the turn:\n    {hint}\n"
        f"Or, if this change genuinely cannot affect the sim (comment/log only), waive for the session:\n"
        f'      echo "no determinism impact: <why>" > {_waiver(sid)}\n'
        f"(Running the gate clears this automatically; Claude Code caps repeated Stop-blocks.)\n"
    )
    sys.stderr.write(msg)
    sys.exit(2)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        sys.exit(0)  # fail-open: never wall off Stop on a bug
    sys.exit(0)
