#!/usr/bin/env python3
"""Stop hook — before a turn ends, block (exit 2) if covered SOURCE changed this session but its DOC
did not (per manifest doc_coverage). This is the fix for the stale-docs disaster: docs get reconciled
at turn-end instead of drifting for hours. Reads the session edit log (log_touched.py).

WAIVER (per doc, per session): if a doc-update genuinely isn't needed, write a reason to the doc's
waiver marker — the deny message prints the exact command — and it clears for the rest of the session.
This is a STRONG NUDGE, not a wall: Claude Code caps repeated Stop re-blocks, so it can never hard-loop.

FAIL-OPEN: no edit log / any error -> allow the stop (exit 0). Only real, unwaived drift emits exit 2.
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


def _waiver(sid, doc):
    return os.path.join(os.environ.get("TMPDIR", "/tmp"), f"claude-docwaiver-{_safe(doc)}-{sid}")


def main():
    data = json.load(sys.stdin)
    sid = _safe(data.get("session_id", "nosession"))
    log = _touchlog(sid)
    if not os.path.isfile(log):
        return  # nothing edited — allow stop
    with open(log) as f:
        changed = [ln.strip() for ln in f if ln.strip()]
    if not changed:
        return

    drift = _manifest.doc_drift(changed, _manifest.load())
    # drop waived docs; dedupe by doc
    seen, items = set(), []
    for doc, trig in drift:
        if doc in seen or os.path.exists(_waiver(sid, doc)):
            continue
        seen.add(doc)
        items.append((doc, trig))
    if not items:
        return  # no unwaived drift — allow stop

    lines = [f"    - {doc}   (source changed: {trig})" for doc, trig in items]
    waivers = "".join(
        f'      echo "no doc change needed: <why>" > {_waiver(sid, doc)}\n' for doc, _ in items
    )
    msg = (
        "\n⛔ Doc-drift — you changed covered source this session but did NOT update its doc(s):\n"
        + "\n".join(lines)
        + "\n\nBefore ending the turn, EITHER update the doc(s) above, OR waive each with a reason:\n"
        + waivers
        + "(Strong nudge; Claude Code caps repeated Stop-blocks so this can't hard-loop.)\n"
    )
    sys.stderr.write(msg)
    sys.exit(2)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        sys.exit(0)  # fail-open: never wall off Stop on a bug
    sys.exit(0)
