#!/usr/bin/env python3
"""PreToolUse (Edit|Write|MultiEdit) hook — block AUTHORING a file until its governing skill was read
this session. The file-edit twin of gate_skill_commands.py (which only gates Bash commands).

Why this exists: prose reminders + the loaded skill *description* failed repeatedly to make me READ the
governing skill/guide before authoring — I'd build from priors and REINVENT things we already designed
(a human farm instead of an ant nest; an entity that already exists). The Bash gate can't catch this:
authoring is a Write/Edit, which has no command signature. This gate makes the read non-optional for the
file being edited.

The gate ROWS live in .claude/manifest.json ("authoring_gates") — the ONE source shared with the other
hooks — NOT hardcoded here (they used to be). Extend = add an authoring_gates row to the manifest.

FAIL-OPEN by construction: the whole body is wrapped in try/except and always exits 0. Per the hook
contract, exit 0 + empty stdout = allow; only an explicit matched-gate-without-marker prints a deny. So
any bug here (including a missing/malformed manifest) degrades to "allow", never "block everything". Once
the governing skill is read/invoked this session (marker set by mark_skill_read.py), that path authors
freely for the rest of the session.

stdin (official contract):  { "session_id": "...", "tool_input": { "file_path": "..." }, ... }
Deny output (official contract): {"hookSpecificOutput":{"hookEventName":"PreToolUse",
                                   "permissionDecision":"deny","permissionDecisionReason":"..."}}
"""
import sys
import os
import re
import json

import _manifest


def _safe(s):
    return re.sub(r"[^A-Za-z0-9_.-]", "_", s or "")


def matched_gate(file_path, gates):
    """Return the first authoring_gates row whose covers-glob matches the edited file, else None."""
    for row in gates:
        if _manifest.path_matches(file_path, row.get("covers", [])):
            return row
    return None


def main():
    data = json.load(sys.stdin)
    file_path = (data.get("tool_input") or {}).get("file_path", "") or ""
    gates = _manifest.load().get("authoring_gates", [])
    hit = matched_gate(file_path, gates)
    if not hit:
        return  # not a gated authoring surface — allow (silent)
    slug = hit.get("skill", "")
    note = hit.get("note", "")

    session_id = _safe(data.get("session_id", "nosession"))
    marker = os.path.join(
        os.environ.get("TMPDIR", "/tmp"),
        f"claude-skill-read-{_safe(slug)}-{session_id}",
    )
    if os.path.exists(marker):
        return  # governing skill already read/invoked this session — allow (silent)

    reason = (
        f"⛔ Authoring gate — the {slug} skill has not been read this session, and its loaded "
        f"*description* is only a pointer, not the procedure. Before editing this file, read the full "
        f"skill (this clears the gate for the session):\n"
        f"    .claude/skills/{slug}/SKILL.md\n"
        f"{note}\n"
        f"Then re-run this edit. (Reading/invoking the skill clears the gate.)"
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
