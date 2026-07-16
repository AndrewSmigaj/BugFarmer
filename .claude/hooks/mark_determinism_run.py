#!/usr/bin/env python3
"""PostToolUse (Bash) hook — set a per-session marker when a determinism GATE command runs, so the Stop
determinism nudge (check_determinism.py) clears automatically once the gate was actually run this session.

FAIL-OPEN: any error -> exit 0 (worst case a missed marker, so the nudge asks again).
stdin: { "session_id": "...", "tool_input": { "command": "..." }, ... }
"""
import sys
import os
import re
import json

GATE_RE = re.compile(r"run_go_tests\.sh|sim-determinism|run_sync[a-z_]*\.sh|harness_persist_test\.sh")


def _safe(s):
    return re.sub(r"[^A-Za-z0-9_.-]", "_", s or "")


def main():
    data = json.load(sys.stdin)
    cmd = (data.get("tool_input") or {}).get("command", "") or ""
    if not GATE_RE.search(cmd):
        return
    sid = _safe(data.get("session_id", "nosession"))
    marker = os.path.join(os.environ.get("TMPDIR", "/tmp"), f"claude-determinism-run-{sid}")
    with open(marker, "w"):
        pass  # touch


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass  # fail-open
    sys.exit(0)
