#!/usr/bin/env python3
"""PostToolUse hook — record that a skill's content was loaded this session, so the gate hooks
(gate_skill_commands.py = Bash, gate_authoring_edits.py = Edit/Write) know it was actually read.

Two ways a skill's content enters context, BOTH marked here:
  1. The **Read** tool on `.claude/skills/<slug>/SKILL.md`  (explicit read — what a deny reason asks for).
  2. The **Skill** tool invoking `<slug>`                    (the natural way; loads the full SKILL.md).
Marking on invocation too is essential: without it, satisfying a gate by invoking the skill (the
idiomatic path) would NOT set the marker, and the gate could livelock ("read the file" forever).

Generic across skills — it marks whichever skill was read/invoked. Fail-open by construction: any error
exits 0 with no output; the worst a bug here does is "forget" a marker, which only makes a gate ask again.

stdin (official contract): { "session_id": "...", "tool_name": "...", "tool_input": { ... }, ... }
Marker written: <TMPDIR|/tmp>/claude-skill-read-<slug>-<session_id>
"""
import sys
import os
import re
import json

SKILL_RE = re.compile(r"\.claude/skills/([^/]+)/SKILL\.md$")


def _safe(s: str) -> str:
    """Keep marker filenames tame regardless of odd slug/session ids."""
    return re.sub(r"[^A-Za-z0-9_.-]", "_", s or "")


def _slug_from(data: dict):
    ti = data.get("tool_input") or {}
    # Case 1: Read tool on a SKILL.md file
    fp = (ti.get("file_path", "") or "").replace("\\", "/")
    m = SKILL_RE.search(fp)
    if m:
        return m.group(1)
    # Case 2: Skill tool invocation — tool_input.skill = "<slug>" (or "plugin:slug")
    skill = ti.get("skill") or ti.get("name") or ""
    if skill:
        return skill.split(":")[-1].strip()   # strip any plugin: namespace
    return None


def main() -> None:
    data = json.load(sys.stdin)
    slug = _slug_from(data)
    if not slug:
        return  # not a skill read/invocation — no-op
    slug = _safe(slug)
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
        pass  # fail-open: never disrupt a tool call
    sys.exit(0)
