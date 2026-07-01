#!/usr/bin/env python3
"""PostToolUse (matcher: Read) hook — record that a skill's SKILL.md was opened this session.

Companion to gate_skill_commands.py. When Claude uses the Read tool on a file matching
`.claude/skills/<slug>/SKILL.md`, drop a per-session marker so the gate hook knows that
skill was actually read (the loaded skill *description* is only a pointer, not the content).

Generic across skills — it marks whichever skill's SKILL.md was read.

Fail-open by construction: any error whatsoever exits 0 with no output. This hook must never
be able to disrupt a Read; the worst a bug here can do is "forget" to set a marker, which only
means the gate asks Claude to read the skill again.

stdin JSON (official hook contract): { "session_id": "...", "tool_input": { "file_path": "..." }, ... }
Marker written: /tmp/claude-skill-read-<slug>-<session_id>
"""
import sys
import os
import re
import json

SKILL_RE = re.compile(r"\.claude/skills/([^/]+)/SKILL\.md$")


def _safe(s: str) -> str:
    """Keep marker filenames tame regardless of odd slug/session ids."""
    return re.sub(r"[^A-Za-z0-9_.-]", "_", s or "")


def main() -> None:
    data = json.load(sys.stdin)
    file_path = (data.get("tool_input") or {}).get("file_path", "") or ""
    m = SKILL_RE.search(file_path.replace("\\", "/"))
    if not m:
        return  # not a skill SKILL.md — no-op
    slug = _safe(m.group(1))
    session_id = _safe(data.get("session_id", "nosession"))
    marker = os.path.join(
        os.environ.get("TMPDIR", "/tmp"),
        f"claude-skill-read-{slug}-{session_id}",
    )
    with open(marker, "w"):
        pass  # touch


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass  # fail-open: never disrupt a Read
    sys.exit(0)
