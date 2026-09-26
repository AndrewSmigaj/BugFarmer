#!/usr/bin/env python3
"""UserPromptSubmit hook — inject a TINY routing nudge when the prompt is about a domain whose
governing skill has NOT been read this session. Early salience BEFORE planning, so the right skill
is on the radar (the Edit-path / command / plan-exit GATES are the hard backstops). NUDGE ONLY —
never blocks; UserPromptSubmit stdout (exit 0) is added to context.

Reads .claude/manifest.json "routing" (skill / keywords / hint). Skills already read this session
(marker set by mark_skill_read.py) are skipped, so the nudge fades as the session progresses.

FAIL-OPEN: any error -> no output (the prompt proceeds untouched).
stdin: { "prompt": "...", "session_id": "...", ... }
"""
import sys
import os
import re
import json

import _manifest

MAX_HINTS = 3


def _safe(s):
    return re.sub(r"[^A-Za-z0-9_.-]", "_", s or "")


def _marker(slug, sid):
    return os.path.join(os.environ.get("TMPDIR", "/tmp"), f"claude-skill-read-{_safe(slug)}-{sid}")


def main():
    data = json.load(sys.stdin)
    prompt = (data.get("prompt", "") or "").lower()
    if not prompt.strip():
        return
    sid = _safe(data.get("session_id", "nosession"))
    routing = _manifest.load().get("routing", [])

    hints = []
    for row in routing:
        slug = row.get("skill", "")
        if not slug or os.path.exists(_marker(slug, sid)):
            continue  # already read this session — no nudge
        if any(kw.lower() in prompt for kw in row.get("keywords", [])):
            hints.append(row.get("hint") or f"read the {slug} skill")
            if len(hints) >= MAX_HINTS:
                break

    if hints:
        print("[skill-routing] Before you plan/implement, read the governing skill(s) for this domain "
              "(the loaded description is only a pointer, not the procedure):")
        for h in hints:
            print(f"  - {h}")
        print("(reading/invoking a skill clears its authoring/command/plan-exit gate for the session)")


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass  # fail-open: never disrupt a prompt
    sys.exit(0)
