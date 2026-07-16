#!/usr/bin/env python3
"""PreToolUse (matcher: ExitPlanMode) hook — block leaving plan mode if the plan touches a covered
domain whose governing skill has NOT been read this session. Early hard gate; the Edit-path gate
(gate_authoring_edits.py) is the post-plan backstop, so this is the layered pair that catches
"planned an implementation in a domain without reading its skill".

Signal = the active plan file (newest *.md in ~/.claude/plans, or $CLAUDE_PLAN_FILE for tests),
scanned for (a) covered source-path prefixes from manifest authoring_gates.covers and (b) routing
keywords. A plan naming a covered path or a domain keyword is a STRONG signal.

FAIL-OPEN: no plan file / unreadable / any error -> allow. False positives err toward "read a skill
you maybe didn't need" (the safe direction) and clear the moment you read the named skill.
stdin: { "session_id": "...", "tool_name": "ExitPlanMode", ... }
"""
import sys
import os
import re
import json
import glob

import _manifest


def _safe(s):
    return re.sub(r"[^A-Za-z0-9_.-]", "_", s or "")


def _marker(slug, sid):
    return os.path.join(os.environ.get("TMPDIR", "/tmp"), f"claude-skill-read-{_safe(slug)}-{sid}")


def _plan_text():
    override = os.environ.get("CLAUDE_PLAN_FILE")
    paths = [override] if override else glob.glob(os.path.expanduser("~/.claude/plans/*.md"))
    paths = [p for p in paths if p and os.path.isfile(p)]
    if not paths:
        return ""
    newest = max(paths, key=os.path.getmtime)
    with open(newest) as f:
        return f.read().lower()


def _prefix(glob_pat):
    """Literal path prefix of a covers glob, up to the first wildcard."""
    return glob_pat.split("*")[0].rstrip("/")


def main():
    data = json.load(sys.stdin)
    sid = _safe(data.get("session_id", "nosession"))
    plan = _plan_text()
    if not plan:
        return  # nothing to inspect — allow
    m = _manifest.load()

    touched = {}  # slug -> (also_skills, trigger string)
    for row in m.get("authoring_gates", []):        # (a) covered source-path prefixes
        slug = row.get("skill", "")
        for g in row.get("covers", []):
            pfx = _prefix(g)
            if len(pfx) >= 6 and pfx in plan:
                touched.setdefault(slug, (row.get("also_skills", []), pfx))
                break
    for row in m.get("routing", []):                # (b) routing keywords
        slug = row.get("skill", "")
        if slug in touched:
            continue
        for kw in row.get("keywords", []):
            if kw.lower() in plan:
                touched.setdefault(slug, ([], kw))
                break

    unread = [(slug, info) for slug, info in touched.items() if not os.path.exists(_marker(slug, sid))]
    if not unread:
        return  # every touched domain's skill was read (or none touched) — allow

    lines = []
    for slug, (also, trig) in unread:
        extra = f" (also: {', '.join(also)})" if also else ""
        lines.append(f"    - {slug}{extra}   [plan mentions '{trig}']")
    reason = (
        "⛔ Plan-exit gate — this plan touches domain(s) whose governing skill you have NOT read this "
        "session. The skill is the real procedure (the loaded description is only a pointer). Read the "
        "skill(s) below, then ExitPlanMode again (reading/invoking clears the gate):\n"
        + "\n".join(lines) +
        "\n(If a match is spurious, reading the named skill still clears it — err toward reading it.)"
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
