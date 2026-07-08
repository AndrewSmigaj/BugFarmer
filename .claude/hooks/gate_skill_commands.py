#!/usr/bin/env python3
"""PreToolUse (matcher: Bash) hook — block a gated command until one of its governing skills was read
this session. The command twin of gate_authoring_edits.py (which gates Edit/Write).

Why this exists: prose reminders (CLAUDE.md, a memory, the skill description) failed TWICE to make me
open the governing SKILL.md before running its command — I'd *feel* I knew the procedure, skip the file,
and improvise the wrong runner. This hook makes the read non-optional: a gate command is DENIED until a
governing skill's SKILL.md has been read/invoked this session (marker set by mark_skill_read.py).

Some commands legitimately span SKILLS (e.g. `docker compose` = run-backend AND test-changes;
`run_config.py` = ecology-tuning / perf-tuning / test-changes). Each GATES row therefore lists the SET of
acceptable skills — reading ANY ONE clears the command, and the deny names them all so the right one is on
the radar. (command→one-skill was the old cross-wire: every command forced reading test-changes, even
`docker compose up`, whose real skill is run-backend.)

FAIL-OPEN by construction. A workflow gate must never be able to wall off the workflow it disciplines, so
the whole body is wrapped in try/except and always exits 0. Only an explicit matched-gate-without-marker
prints a deny. exit 0 + empty stdout = allow; we never emit exit 2, so any bug here degrades to "allow".

Extending to another skill later = add a GATES row.

stdin (official contract): { "session_id": "...", "tool_input": { "command": "..." }, ... }
Deny output (official contract): {"hookSpecificOutput":{"hookEventName":"PreToolUse",
                                   "permissionDecision":"deny","permissionDecisionReason":"..."}}
"""
import sys
import os
import re
import json

# ---------------------------------------------------------------------------
# GATES: ([acceptable skill slugs], [regexes identifying the command], context note).
# Reading ANY of the acceptable skills clears the command. Regexes are matched against each
# command *segment* after quoted strings are stripped (see matched_gate).
# ---------------------------------------------------------------------------
GATES = [
    # determinism / test / verify runners  -> the test-changes discipline
    (["test-changes"], [
        r"\brun_go_tests\.sh\b",
        r"\brun_sync[a-z_]*\.sh\b",
        r"\bharness_persist_test\.sh\b",
        r"\bsim-determinism\b",
        r"\bsync-harness\b",
        r"\bdotnet\s+run\b",
        r"-executeMethod\b",
    ], "test/determinism runner — read test-changes"),
    # server lifecycle  -> run-backend (or test-changes, which also rebuilds the plugin before a test)
    (["run-backend", "test-changes"], [
        r"\bdocker[- ]compose\s+(build|up|run|restart|down)\b",
    ], "docker compose = server lifecycle (run-backend), or rebuilding the plugin before a test (test-changes)"),
    # ecology/perf harness  -> ecology-tuning / perf-tuning (or test-changes for a determinism verify)
    (["ecology-tuning", "perf-tuning", "test-changes"], [
        r"\brun_config\.py\b",
        r"\brun_sweep\.sh\b",
    ], "run_config/sweep = balance (ecology-tuning) / profiling (perf-tuning) / determinism-verify (test-changes)"),
]

# First-token commands that only READ/inspect/navigate — never an execution. If a command segment starts
# with one of these it's skipped (so `grep run_go_tests.sh`, `cat …`, `cd tools/sync-harness` aren't gated).
VIEWERS = {
    "grep", "rg", "egrep", "fgrep", "cat", "bat", "less", "more", "head", "tail",
    "ls", "tree", "find", "fd", "wc", "echo", "printf", "stat", "file", "vim",
    "nvim", "nano", "emacs", "code", "sed", "awk", "cut", "column", "diff", "git",
    "cd", "pushd",
}

_GATES = [(slugs, [re.compile(p) for p in pats], note) for (slugs, pats, note) in GATES]
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
    """Return (acceptable_slugs, note) of the first gate whose command is actually executed, else None."""
    for segment in _SEGSEP.split(command):
        if _first_exec(segment) in VIEWERS:
            continue  # inspection / navigation, not an execution
        stripped = _QUOTED.sub(" ", segment)  # a real invocation token is never inside quotes
        for slugs, regexes, note in _GATES:
            if any(r.search(stripped) for r in regexes):
                return slugs, note
    return None


def _safe(s):
    return re.sub(r"[^A-Za-z0-9_.-]", "_", s or "")


def _marker(slug, session_id):
    return os.path.join(os.environ.get("TMPDIR", "/tmp"), f"claude-skill-read-{_safe(slug)}-{session_id}")


def main():
    data = json.load(sys.stdin)
    command = (data.get("tool_input") or {}).get("command", "") or ""
    hit = matched_gate(command)
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
