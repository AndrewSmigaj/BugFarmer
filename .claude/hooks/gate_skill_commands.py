#!/usr/bin/env python3
"""PreToolUse (matcher: Bash) hook — block test/gate commands until their skill was read this session.

Why this exists: prose reminders (CLAUDE.md, a memory, the skill description) failed TWICE to make me
open `.claude/skills/test-changes/SKILL.md` before running a test gate — I'd *feel* I knew the procedure,
skip the file, and improvise the wrong runner. This hook makes the read non-optional: a gate command is
DENIED until the skill's SKILL.md has actually been Read this session (marker set by mark_skill_read.py).

FAIL-OPEN by construction. A workflow gate must never be able to wall off the workflow it disciplines, so
the whole body is wrapped in try/except and always exits 0. Only an explicit matched-gate-without-marker
prints a deny decision. Per the documented hook contract, exit 0 + empty stdout = allow; only exit 2 blocks
(which we never emit), so any bug here degrades to "allow", never "block everything".

Extending to another skill later = add one row to GATES.

stdin JSON (official contract): { "session_id": "...", "tool_input": { "command": "..." }, ... }
Deny output (official contract): {"hookSpecificOutput":{"hookEventName":"PreToolUse",
                                   "permissionDecision":"deny","permissionDecisionReason":"..."}}
"""
import sys
import os
import re
import json

# ---------------------------------------------------------------------------
# GATES: (skill slug, [regexes that identify a run of that skill's gate commands])
# The slug maps to .claude/skills/<slug>/SKILL.md and to the marker
# /tmp/claude-skill-read-<slug>-<session_id>. Regexes are matched against each
# command *segment* after quoted strings are stripped (see is_gate).
#
# test-changes gate tokens are verified to cover every command the skill documents:
#   run_go_tests.sh · run_sync*.sh (run_sync_latejoin.sh) · run_config.py · run_sweep.sh ·
#   harness_persist_test.sh · tools/test.sh · sim-determinism · sync-harness · `dotnet run`
#   (the bare form used after `cd tools/sync-harness`) · Unity -executeMethod ·
#   `docker compose build|up|run|restart`.
# Intentionally NOT gated (authoring/analysis/log-view, not test runs): make_bug_lab.py,
# plot_*.py, `docker compose logs`.
# ---------------------------------------------------------------------------
GATES = [
    ("test-changes", [
        r"\brun_go_tests\.sh\b",
        r"\brun_sync[a-z_]*\.sh\b",
        r"\brun_config\.py\b",
        r"\brun_sweep\.sh\b",
        r"\bharness_persist_test\.sh\b",
        r"\btools/test\.sh\b",
        r"\bsim-determinism\b",
        r"\bsync-harness\b",
        r"\bdotnet\s+run\b",
        r"-executeMethod\b",
        r"\bdocker[- ]compose\s+(build|up|run|restart)\b",
    ]),
]

# First-token commands that only READ/inspect/navigate — never a test execution. If a command
# segment starts with one of these, it's skipped (so `grep run_go_tests.sh`, `cat tools/test.sh`,
# `git commit -m '…run_go_tests.sh…'`, `cd tools/sync-harness` are not gated).
VIEWERS = {
    "grep", "rg", "egrep", "fgrep", "cat", "bat", "less", "more", "head", "tail",
    "ls", "tree", "find", "fd", "wc", "echo", "printf", "stat", "file", "vim",
    "nvim", "nano", "emacs", "code", "sed", "awk", "cut", "column", "diff", "git",
    "cd", "pushd",
}

_GATES = [(slug, [re.compile(p) for p in pats]) for slug, pats in GATES]
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


def matched_gate(command):
    """Return the slug of the first gate whose command is actually being executed, else None."""
    for segment in _SEGSEP.split(command):
        if _first_exec(segment) in VIEWERS:
            continue  # inspection / navigation, not a test run
        stripped = _QUOTED.sub(" ", segment)  # a real invocation token is never inside quotes
        for slug, regexes in _GATES:
            if any(r.search(stripped) for r in regexes):
                return slug
    return None


def _safe(s):
    return re.sub(r"[^A-Za-z0-9_.-]", "_", s or "")


def main():
    data = json.load(sys.stdin)
    command = (data.get("tool_input") or {}).get("command", "") or ""
    slug = matched_gate(command)
    if not slug:
        return  # not a gate command — allow (silent)

    session_id = _safe(data.get("session_id", "nosession"))
    marker = os.path.join(
        os.environ.get("TMPDIR", "/tmp"),
        f"claude-skill-read-{_safe(slug)}-{session_id}",
    )
    if os.path.exists(marker):
        return  # skill already read this session — allow (silent)

    reason = (
        f"⛔ Gate command blocked — the {slug} skill has not been opened this session. "
        f"The loaded skill *description* is only a pointer, not the procedure. Read the full file first:\n"
        f"    .claude/skills/{slug}/SKILL.md\n"
        f"then re-run this command. (Clears for the rest of the session once you Read it.)"
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
