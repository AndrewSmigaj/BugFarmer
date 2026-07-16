#!/usr/bin/env python3
"""PreToolUse (matcher: Bash) hook — block a gated command until one of its governing skills was read
this session. The command twin of gate_authoring_edits.py (which gates Edit/Write).

Why this exists: prose reminders (CLAUDE.md, a memory, the skill description) failed TWICE to make me
open the governing SKILL.md before running its command — I'd *feel* I knew the procedure, skip the file,
and improvise the wrong runner. This hook makes the read non-optional: a gate command is DENIED until a
governing skill's SKILL.md has been read/invoked this session (marker set by mark_skill_read.py).

Some commands legitimately span SKILLS (e.g. `docker compose` = run-backend AND test-changes;
`run_config.py` = ecology-tuning / perf-tuning / test-changes). Each command_gates row therefore lists the
SET of acceptable skills — reading ANY ONE clears the command, and the deny names them all.

The gate ROWS (command_gates) + the inspect-only first-tokens (command_viewers) live in
.claude/manifest.json — the ONE source shared with the other hooks — NOT hardcoded here. Extend = add a
command_gates row to the manifest.

FAIL-OPEN by construction. A workflow gate must never wall off the workflow it disciplines, so the whole
body is wrapped in try/except and always exits 0. Only an explicit matched-gate-without-marker prints a
deny; we never emit exit 2, so any bug here (including a missing/malformed manifest) degrades to "allow".

stdin (official contract): { "session_id": "...", "tool_input": { "command": "..." }, ... }
Deny output (official contract): {"hookSpecificOutput":{"hookEventName":"PreToolUse",
                                   "permissionDecision":"deny","permissionDecisionReason":"..."}}
"""
import sys
import os
import re
import json

import _manifest

_ASSIGN = re.compile(r"^\w+=")               # leading VAR=value env assignments
_QUOTED = re.compile(r"'[^']*'|\"[^\"]*\"")  # '...' / "..." — mentions, not invocations
_SEGSEP = re.compile(r"&&|\|\||[|;&\n]")      # shell command separators


def _first_exec(segment):
    """Basename of the first real command token in a segment (skipping VAR= assignments)."""
    for tok in segment.strip().split():
        if _ASSIGN.match(tok):
            continue
        return tok.split("/")[-1]
    return ""


def matched_gate(command, gates, viewers):
    """Return (acceptable_slugs, note) of the first gate whose command is actually executed, else None.
    `gates` rows must already carry a compiled-regex list under '_compiled' (set in main)."""
    for segment in _SEGSEP.split(command):
        if _first_exec(segment) in viewers:
            continue  # inspection / navigation, not an execution
        stripped = _QUOTED.sub(" ", segment)  # a real invocation token is never inside quotes
        for row in gates:
            if any(r.search(stripped) for r in row.get("_compiled", [])):
                return row.get("skills", []), row.get("note", "")
    return None


def _safe(s):
    return re.sub(r"[^A-Za-z0-9_.-]", "_", s or "")


def _marker(slug, session_id):
    return os.path.join(os.environ.get("TMPDIR", "/tmp"), f"claude-skill-read-{_safe(slug)}-{session_id}")


def main():
    data = json.load(sys.stdin)
    command = (data.get("tool_input") or {}).get("command", "") or ""

    m = _manifest.load()
    gates = m.get("command_gates", [])
    for row in gates:
        row["_compiled"] = [re.compile(p) for p in row.get("patterns", [])]
    viewers = set(m.get("command_viewers", []))

    hit = matched_gate(command, gates, viewers)
    if not hit:
        return  # not a gate command — allow (silent)
    slugs, note = hit

    session_id = _safe(data.get("session_id", "nosession"))
    if any(os.path.exists(_marker(s, session_id)) for s in slugs):
        return  # a governing skill was read this session — allow (silent)

    read_list = " OR ".join(f".claude/skills/{s}/SKILL.md" for s in slugs)
    reason = (
        f"⛔ Gate command blocked — none of its governing skills ({', '.join(slugs)}) has been read this "
        f"session. The loaded skill *description* is only a pointer, not the procedure. Read the relevant "
        f"skill first:\n    {read_list}\n({note})\nthen re-run. (Clears for the session once you read it.)"
    )
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": reason,
        }
    }))


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass  # fail-open: any error → no output → tool proceeds
    sys.exit(0)
