#!/usr/bin/env python3
"""Durable self-test for the skill-gate hooks (mark_skill_read.py + gate_skill_commands.py).

Run:  python3 .claude/hooks/selftest.py
Exits 0 iff every check passes. Drives the ACTUAL script files end-to-end via subprocess
(stdin JSON -> stdout/exit), exactly as Claude Code invokes them. Uses a synthetic session id
so it never touches the real per-session marker. Safe to re-run anytime.
"""
import json
import os
import subprocess
import sys

HOOKS = os.path.dirname(os.path.abspath(__file__))
GATE = os.path.join(HOOKS, "gate_skill_commands.py")
MARK = os.path.join(HOOKS, "mark_skill_read.py")
SID = "SELFTEST"
MARKER = os.path.join(os.environ.get("TMPDIR", "/tmp"), f"claude-skill-read-test-changes-{SID}")

results = []


def run(script, payload):
    p = subprocess.run([sys.executable, script], input=json.dumps(payload),
                       capture_output=True, text=True)
    return p.returncode, p.stdout.strip()


def run_raw(script, raw):
    p = subprocess.run([sys.executable, script], input=raw, capture_output=True, text=True)
    return p.returncode, p.stdout.strip()


def check(name, ok):
    results.append(ok)
    print(f"{'PASS' if ok else 'FAIL':4} {name}")


def is_deny(out):
    if not out:
        return False
    try:
        return json.loads(out)["hookSpecificOutput"]["permissionDecision"] == "deny"
    except Exception:
        return False


def main():
    if os.path.exists(MARKER):
        os.remove(MARKER)

    # --- gate DENIES real gate commands while the skill is unread ---
    for cmd in [
        "bash tools/run_go_tests.sh",
        "dotnet run -- --zone bug_lab --duration 15",            # bare form after `cd tools/sync-harness`
        "FRESH=1 SPAWN_A=126,2 tools/run_sync_latejoin.sh village_21_B 70 12",
        "docker compose up -d --force-recreate nakama",
        'Unity.exe -batchmode -quit -executeMethod SyncTestBuild.Build',
        "python3 tools/ecology/run_config.py 01_no_cull --duration 250",
    ]:
        rc, out = run(GATE, {"session_id": SID, "tool_input": {"command": cmd}})
        check(f"gate DENIES (unread): {cmd[:50]}", rc == 0 and is_deny(out))

    # --- gate ALLOWS inspection / mentions / navigation / unrelated ---
    for cmd in [
        "git status",
        "git commit -m 'fix run_go_tests.sh flake'",
        "grep -rn run_go_tests.sh docs",
        "cat tools/run_sync_latejoin.sh",
        "cd tools/sync-harness",
        "docker compose logs nakama | grep Drift",
        "python3 tools/data/publish_entities.py",
        "curl -d 'run_config.py payload' http://x",              # token only inside quotes
    ]:
        rc, out = run(GATE, {"session_id": SID, "tool_input": {"command": cmd}})
        check(f"gate ALLOWS: {cmd[:50]}", rc == 0 and out == "")

    # --- marker lifecycle ---
    rc, out = run(MARK, {"session_id": SID,
                         "tool_input": {"file_path": "/x/.claude/skills/test-changes/SKILL.md"}})
    check("mark CREATES marker on test-changes SKILL.md read", os.path.exists(MARKER))

    rc, out = run(GATE, {"session_id": SID, "tool_input": {"command": "bash tools/run_go_tests.sh"}})
    check("gate ALLOWS after marker set", rc == 0 and out == "")

    os.remove(MARKER)
    rc, out = run(MARK, {"session_id": SID,
                         "tool_input": {"file_path": "/x/nakama/data/species.json"}})
    check("mark IGNORES non-skill read", not os.path.exists(MARKER))

    # --- fail-open: malformed stdin must exit 0 and emit nothing (never block) ---
    rc, out = run_raw(GATE, "not json at all")
    check("gate FAIL-OPEN on bad stdin (exit 0, empty)", rc == 0 and out == "")
    rc, out = run_raw(MARK, "not json at all")
    check("mark FAIL-OPEN on bad stdin (exit 0)", rc == 0)

    if os.path.exists(MARKER):
        os.remove(MARKER)

    print()
    passed = sum(results)
    print(f"{passed}/{len(results)} checks passed")
    return 0 if passed == len(results) else 1


if __name__ == "__main__":
    sys.exit(main())
