#!/usr/bin/env python3
"""PostToolUse (Edit|Write|MultiEdit) hook — append each edited file path to a per-session log, so
the Stop hook (check_doc_drift.py) can tell what source changed this session and whether the docs
that cover it were also updated. Records EVERY edit (docs included — check_doc_drift needs to see the
doc was touched); the drift filtering happens there.

FAIL-OPEN by construction: any error exits 0 with no output; worst case a missed log entry.
stdin: { "session_id": "...", "tool_input": { "file_path": "..." }, ... }
Log: <TMPDIR|/tmp>/claude-touched-<session_id>.log  (one path per line)
"""
import sys
import os
import re
import json


def _safe(s):
    return re.sub(r"[^A-Za-z0-9_.-]", "_", s or "")


def main():
    data = json.load(sys.stdin)
    fp = (data.get("tool_input") or {}).get("file_path", "") or ""
    if not fp:
        return
    sid = _safe(data.get("session_id", "nosession"))
    log = os.path.join(os.environ.get("TMPDIR", "/tmp"), f"claude-touched-{sid}.log")
    with open(log, "a") as f:
        f.write(fp.replace("\\", "/") + "\n")


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass  # fail-open
    sys.exit(0)
