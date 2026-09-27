#!/usr/bin/env python3
"""Durable self-test for the skill-gate hooks
(mark_skill_read.py + gate_skill_commands.py + gate_authoring_edits.py).

Run:  python3 .claude/hooks/selftest.py
Exits 0 iff every check passes. Drives the ACTUAL script files end-to-end via subprocess
(stdin JSON -> stdout/exit), exactly as Claude Code invokes them. Uses a synthetic session id
so it never touches the real per-session markers. Safe to re-run anytime.
"""
import json
import os
import re
import subprocess
import sys

HOOKS = os.path.dirname(os.path.abspath(__file__))
GATE_CMD = os.path.join(HOOKS, "gate_skill_commands.py")
GATE_EDIT = os.path.join(HOOKS, "gate_authoring_edits.py")
MARK = os.path.join(HOOKS, "mark_skill_read.py")
GATE_PLAN = os.path.join(HOOKS, "gate_plan_exit.py")
ROUTE = os.path.join(HOOKS, "route_skills.py")
LOG_TOUCHED = os.path.join(HOOKS, "log_touched.py")
CHECK_DRIFT = os.path.join(HOOKS, "check_doc_drift.py")
STAGED_DRIFT = os.path.join(HOOKS, "check_staged_drift.py")
MARK_DET = os.path.join(HOOKS, "mark_determinism_run.py")
CHECK_DET = os.path.join(HOOKS, "check_determinism.py")
SID = "SELFTEST"
TMP = os.environ.get("TMPDIR", "/tmp")

results = []


def marker(slug):
    return os.path.join(TMP, f"claude-skill-read-{slug}-{SID}")


def clear_markers():
    for slug in ("test-changes", "run-backend", "ecology-tuning", "perf-tuning",
                 "zone-craft", "author-zone", "economy", "frontier-sync", "regenerate-sprite",
                 "combat-enemy", "bug-spawning", "add-object"):
        try:
            os.remove(marker(slug))
        except OSError:
            pass


def run(script, payload):
    p = subprocess.run([sys.executable, script], input=json.dumps(payload),
                       capture_output=True, text=True)
    return p.returncode, p.stdout.strip()


def run_raw(script, raw):
    p = subprocess.run([sys.executable, script], input=raw, capture_output=True, text=True)
    return p.returncode, p.stdout.strip()


def run_env(script, payload, extra_env):
    e = dict(os.environ)
    e.update(extra_env)
    p = subprocess.run([sys.executable, script], input=json.dumps(payload),
                       capture_output=True, text=True, env=e)
    return p.returncode, p.stdout.strip()


def run3(script, payload):
    p = subprocess.run([sys.executable, script], input=json.dumps(payload), capture_output=True, text=True)
    return p.returncode, p.stdout.strip(), p.stderr.strip()


def run3env(script, payload, extra_env):
    e = dict(os.environ)
    e.update(extra_env)
    p = subprocess.run([sys.executable, script], input=json.dumps(payload),
                       capture_output=True, text=True, env=e)
    return p.returncode, p.stdout.strip(), p.stderr.strip()


def _safe(s):
    return re.sub(r"[^A-Za-z0-9_.-]", "_", s or "")


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


def cmd(c):
    return run(GATE_CMD, {"session_id": SID, "tool_input": {"command": c}})


def edit(fp):
    return run(GATE_EDIT, {"session_id": SID, "tool_input": {"file_path": fp}})


def mark_read(fp):
    return run(MARK, {"session_id": SID, "tool_name": "Read", "tool_input": {"file_path": fp}})


def mark_invoke(slug):
    return run(MARK, {"session_id": SID, "tool_name": "Skill", "tool_input": {"skill": slug}})


def main():
    clear_markers()

    # ============ COMMAND GATE (gate_skill_commands.py) ============
    for c in ["bash tools/run_go_tests.sh",
              "dotnet run -- --zone bug_lab --duration 15",
              "FRESH=1 tools/run_sync_latejoin.sh village_21_B 70 12",
              "docker compose up -d --force-recreate nakama",
              "Unity.exe -batchmode -quit -executeMethod SyncTestBuild.Build",
              "python3 tools/ecology/run_config.py 01_no_cull --duration 250"]:
        rc, out = cmd(c)
        check(f"cmd DENIES (unread): {c[:46]}", rc == 0 and is_deny(out))

    for c in ["git status", "git commit -m 'fix run_go_tests.sh flake'",
              "grep -rn run_go_tests.sh docs", "cat tools/run_sync_latejoin.sh",
              "cd tools/sync-harness", "docker compose logs nakama | grep Drift",
              "python3 tools/data/publish_entities.py",
              "curl -d 'run_config.py payload' http://x"]:
        rc, out = cmd(c)
        check(f"cmd ALLOWS: {c[:46]}", rc == 0 and out == "")

    # cross-wire fix: docker compose is run-backend, not test-changes
    mark_invoke("run-backend")
    rc, out = cmd("docker compose up -d")
    check("cmd ALLOWS docker compose after run-backend (cross-wire fixed)", rc == 0 and out == "")
    rc, out = cmd("bash tools/run_go_tests.sh")
    check("cmd still DENIES run_go_tests (needs test-changes, not run-backend)", is_deny(out))
    mark_read("/x/.claude/skills/test-changes/SKILL.md")
    rc, out = cmd("bash tools/run_go_tests.sh")
    check("cmd ALLOWS run_go_tests after test-changes", rc == 0 and out == "")

    clear_markers()

    # ============ AUTHORING GATE (gate_authoring_edits.py) ============
    for fp in ["/x/tools/zonegen/scenes/zone_ant_colony_40.py",
               "/x/nakama/data/entities/items.json",
               "/x/nakama/modules/world/handlers_bugs.go",
               "/x/nakama/data/species.json",
               "/x/tools/art/catalog/decor.json"]:
        rc, out = edit(fp)
        check(f"edit DENIES (unread): {fp[3:44]}", rc == 0 and is_deny(out))

    for fp in ["/x/tools/zonegen/features/cave.py", "/x/tools/zonegen/zonebuilder.py",
               "/x/README.md", "/x/docs/guides/authoring/caves.md"]:
        rc, out = edit(fp)
        check(f"edit ALLOWS (not content-authoring): {fp[3:40]}", rc == 0 and out == "")

    # marker via Skill invocation clears the authoring gate
    mark_invoke("zone-craft")
    rc, out = edit("/x/tools/zonegen/scenes/zone_x.py")
    check("edit ALLOWS scene after INVOKING zone-craft (deadlock fix)", rc == 0 and out == "")
    # marker via Read clears a different gate
    mark_read("/x/.claude/skills/economy/SKILL.md")
    rc, out = edit("/x/nakama/data/entities/placeables.json")
    check("edit ALLOWS entity after READING economy", rc == 0 and out == "")

    clear_markers()

    # ============ MARKER hygiene ============
    mark_read("/x/nakama/data/species.json")
    check("mark IGNORES non-skill read", not os.path.exists(marker("test-changes")))
    mark_invoke("bee-plugin:zone-craft")
    check("mark strips plugin: namespace on invoke", os.path.exists(marker("zone-craft")))

    # ============ FAIL-OPEN ============
    rc, out = run_raw(GATE_CMD, "not json")
    check("cmd gate FAIL-OPEN on bad stdin", rc == 0 and out == "")
    rc, out = run_raw(GATE_EDIT, "not json")
    check("edit gate FAIL-OPEN on bad stdin", rc == 0 and out == "")
    rc, out = run_raw(MARK, "not json")
    check("mark FAIL-OPEN on bad stdin", rc == 0)

    # the manifest dependency must ALSO fail-open: a genuinely-gated command/path with a MISSING
    # manifest must ALLOW (a broken manifest must never wall off the workflow the gates discipline).
    rc, out = run_env(GATE_CMD, {"session_id": SID, "tool_input": {"command": "bash tools/run_go_tests.sh"}},
                      {"CLAUDE_MANIFEST_PATH": "/no/such/manifest.json"})
    check("cmd gate FAIL-OPEN on missing manifest", rc == 0 and out == "")
    rc, out = run_env(GATE_EDIT, {"session_id": SID, "tool_input": {"file_path": "/x/nakama/modules/world/foo.go"}},
                      {"CLAUDE_MANIFEST_PATH": "/no/such/manifest.json"})
    check("edit gate FAIL-OPEN on missing manifest", rc == 0 and out == "")

    clear_markers()

    # ============ PLAN-EXIT GATE (gate_plan_exit.py) ============
    plan = os.path.join(TMP, f"selftest-plan-{SID}.md")
    with open(plan, "w") as f:
        f.write("# Plan\nWe will edit nakama/modules/world/handlers_bugs.go to add a mechanic.\n")
    rc, out = run_env(GATE_PLAN, {"session_id": SID, "tool_name": "ExitPlanMode"}, {"CLAUDE_PLAN_FILE": plan})
    check("plan-exit DENIES: plan names world/*.go, frontier-sync unread", rc == 0 and is_deny(out))
    mark_invoke("frontier-sync")
    rc, out = run_env(GATE_PLAN, {"session_id": SID, "tool_name": "ExitPlanMode"}, {"CLAUDE_PLAN_FILE": plan})
    check("plan-exit ALLOWS after reading frontier-sync", rc == 0 and out == "")
    clear_markers()
    with open(plan, "w") as f:
        f.write("# Plan\nWrite a short poem about a sunset. No code, no zones.\n")
    rc, out = run_env(GATE_PLAN, {"session_id": SID, "tool_name": "ExitPlanMode"}, {"CLAUDE_PLAN_FILE": plan})
    check("plan-exit ALLOWS: no covered domain in plan", rc == 0 and out == "")
    with open(plan, "w") as f:
        f.write("# Plan\nTune the ecology and rebalance the food web.\n")
    rc, out = run_env(GATE_PLAN, {"session_id": SID, "tool_name": "ExitPlanMode"}, {"CLAUDE_PLAN_FILE": plan})
    check("plan-exit DENIES: ecology keyword, ecology-tuning unread", rc == 0 and is_deny(out))
    rc, out = run_env(GATE_PLAN, {"session_id": SID, "tool_name": "ExitPlanMode"}, {"CLAUDE_PLAN_FILE": "/no/such/plan.md"})
    check("plan-exit FAIL-OPEN when no plan file", rc == 0 and out == "")

    # ---- LAYOUT gate: a plan that creates files must say WHERE they go ----
    def plan_says(text):
        with open(plan, "w") as f:
            f.write(text)
        return run_env(GATE_PLAN, {"session_id": SID, "tool_name": "ExitPlanMode"},
                       {"CLAUDE_PLAN_FILE": plan})

    rc, out = plan_says("# Plan\nWe will create a helper script to render the sprites.\n")
    check("layout DENIES: plan creates files, no destination", rc == 0 and is_deny(out))
    rc, out = plan_says("# Plan\nWe will create a helper script at tools/sprites/render_sheet.py.\n")
    check("layout ALLOWS: destination path stated", rc == 0 and out == "")
    rc, out = plan_says("# Plan\nCreate a preview generator.\nLayout:\n```\nfoo/bar/baz.png\n```\n")
    check("layout ALLOWS: a folder tree is given", rc == 0 and out == "")
    rc, out = plan_says("# Plan\nRefactor the existing loop for clarity; no new files.\n")
    check("layout ALLOWS: plan creates nothing", rc == 0 and out == "")
    try:
        os.remove(plan)
    except OSError:
        pass
    clear_markers()

    # ============ ROUTE-SKILLS nudge (route_skills.py) ============
    rc, out = run(ROUTE, {"session_id": SID, "prompt": "let's build a zone with a cave landmark scene"})
    check("route injects zone-craft nudge (unread)", rc == 0 and "zone-craft" in out)
    rc, out = run(ROUTE, {"session_id": SID, "prompt": "hello, how are you today"})
    check("route SILENT when no domain keyword", rc == 0 and out == "")
    mark_invoke("frontier-sync")
    rc, out = run(ROUTE, {"session_id": SID, "prompt": "add a new bug mechanic with determinism"})
    check("route SILENT for a skill already read this session", rc == 0 and out == "")
    rc, out = run_raw(ROUTE, "not json")
    check("route FAIL-OPEN on bad stdin", rc == 0 and out == "")
    clear_markers()

    # ============ DOC-DRIFT (log_touched.py + check_doc_drift.py) ============
    tlog = os.path.join(TMP, f"claude-touched-{SID}.log")
    FARM = "/x/nakama/modules/world/handlers_farming.go"          # covered by exactly one doc
    FARM_DOC = "docs/product/architecture/architecture_farming.md"
    for p in (tlog,):
        try:
            os.remove(p)
        except OSError:
            pass
    run(LOG_TOUCHED, {"session_id": SID, "tool_input": {"file_path": FARM}})
    check("log_touched records the edited path",
          os.path.isfile(tlog) and "handlers_farming.go" in open(tlog).read())
    rc, _o, _e = run3(CHECK_DRIFT, {"session_id": SID})
    check("drift BLOCKS (exit 2): source changed, doc not", rc == 2)
    with open(tlog, "a") as f:
        f.write(FARM_DOC + "\n")
    rc, _o, _e = run3(CHECK_DRIFT, {"session_id": SID})
    check("drift CLEARS when the doc is also changed", rc == 0)
    try:
        os.remove(tlog)
    except OSError:
        pass
    run(LOG_TOUCHED, {"session_id": SID, "tool_input": {"file_path": FARM}})
    waiver = os.path.join(TMP, f"claude-docwaiver-{_safe(FARM_DOC)}-{SID}")
    with open(waiver, "w") as f:
        f.write("no doc change needed: internal refactor\n")
    rc, _o, _e = run3(CHECK_DRIFT, {"session_id": SID})
    check("drift CLEARS with a per-doc waiver", rc == 0)
    for p in (waiver, tlog):
        try:
            os.remove(p)
        except OSError:
            pass
    rc, _o, _e = run3(CHECK_DRIFT, {"session_id": SID})
    check("drift ALLOWS stop when nothing edited", rc == 0)
    rc, out = run_raw(CHECK_DRIFT, "not json")
    check("drift FAIL-OPEN on bad stdin (exit 0)", rc == 0)
    rc, out = run_raw(LOG_TOUCHED, "not json")
    check("log_touched FAIL-OPEN on bad stdin", rc == 0)

    # ============ PRE-COMMIT STAGED DRIFT (check_staged_drift.py) ============
    # An empty content fixture keeps these hermetic: the real git state can't make them comment-only.
    diffs = os.path.join(TMP, f"claude-diff-content-{SID}.json")

    def with_diffs(content):
        with open(diffs, "w", encoding="utf-8") as f:
            json.dump(content, f)
        return {"CLAUDE_DIFF_CONTENT": diffs}

    rc, _o, _e = run3env(STAGED_DRIFT, {}, dict(with_diffs({}), CLAUDE_STAGED_FILES="nakama/modules/world/handlers_farming.go"))
    check("staged-drift BLOCKS (exit 1): source staged, doc not", rc == 1)
    rc, _o, _e = run3env(STAGED_DRIFT, {}, dict(with_diffs({}), CLAUDE_STAGED_FILES="nakama/modules/world/handlers_farming.go " + FARM_DOC))
    check("staged-drift PASSES when doc also staged", rc == 0)
    rc, _o, _e = run3env(STAGED_DRIFT, {}, {"CLAUDE_STAGED_FILES": ".claude/manifest.json README.md"})
    check("staged-drift PASSES for non-covered files", rc == 0)
    rc, _o, _e = run3env(STAGED_DRIFT, {}, {"CLAUDE_STAGED_FILES": ""})
    check("staged-drift PASSES with nothing staged", rc == 0)

    # ============ COMMENT-ONLY CHANGES DON'T COUNT (_comments.py) ============
    GO = "nakama/modules/world/handlers_farming.go"       # doc: architecture_farming.md
    PY = "tools/zonegen/features/yard.py"                  # doc: docs/guides/authoring/yard.md
    go_old = 'package world\n\n// quoted: "x"\nfunc f() int {\n\treturn 1 // one\n}\n'
    go_cmt = 'package world\n\n// restated\n/* a block\n   comment */\nfunc f() int {\n\treturn 1 // uno\n}\n'
    go_code = go_old.replace("return 1", "return 2")
    go_str_old = 'package world\n\nfunc g() string {\n\treturn "a  b" // s\n}\n'
    go_str_new = 'package world\n\nfunc g() string {\n\treturn "a b" // s\n}\n'
    go_semi_old = 'package world\n\nfunc h() {\n\treturn\n\tx()\n}\n'
    go_semi_new = 'package world\n\nfunc h() {\n\treturn x()\n}\n'
    py_old = 'def f():\n    """Old doc quoting "x"."""\n    return 1  # one\n'
    py_cmt = 'def f():\n    """Restated doc."""\n    return 1  # uno\n'
    py_code = 'def f():\n    """Old doc."""\n    return 2\n'

    def staged_rc(path, old, new, extra=""):
        env = dict(with_diffs({path: {"old": old, "new": new}}), CLAUDE_STAGED_FILES=(path + " " + extra).strip())
        return run3env(STAGED_DRIFT, {}, env)

    rc, _o, _e = staged_rc(GO, go_old, go_cmt)
    check("staged-drift PASSES a Go change that touched only comments", rc == 0)
    rc, _o, _e = staged_rc(GO, go_old, go_code)
    check("staged-drift BLOCKS a Go code change", rc == 1)
    rc, _o, _e = staged_rc(GO, go_str_old, go_str_new)
    check("staged-drift BLOCKS a Go change inside a string", rc == 1)
    rc, _o, _e = staged_rc(GO, go_semi_old, go_semi_new)
    check("staged-drift BLOCKS a Go line-break change (semicolons)", rc == 1)
    rc, _o, _e = staged_rc(GO, go_old, go_old)
    check("staged-drift BLOCKS when the versions can't be told apart", rc == 1)
    rc, _o, _e = staged_rc(PY, py_old, py_cmt)
    check("staged-drift PASSES a Python change to comments and docstrings only", rc == 0)
    rc, _o, _e = staged_rc(PY, py_old, py_code)
    check("staged-drift BLOCKS a Python code change", rc == 1)
    rc, _o, _e = staged_rc(PY, py_old, "def f(:\n")
    check("staged-drift BLOCKS when the new Python won't parse", rc == 1)
    env = dict(with_diffs({GO: {"old": go_old, "new": go_cmt}, PY: {"old": py_old, "new": py_code}}),
               CLAUDE_STAGED_FILES=GO + " " + PY)
    rc, _o, err = run3env(STAGED_DRIFT, {}, env)
    check("staged-drift names only the doc of the real code change",
          rc == 1 and "yard.md" in err and "architecture_farming.md" not in err)
    try:
        os.remove(tlog)
    except OSError:
        pass
    run(LOG_TOUCHED, {"session_id": SID, "tool_input": {"file_path": FARM}})
    rc, _o, _e = run3env(CHECK_DRIFT, {"session_id": SID}, with_diffs({FARM: {"old": go_old, "new": go_cmt}}))
    check("drift ALLOWS stop when the edit touched only comments", rc == 0)
    rc, _o, _e = run3env(CHECK_DRIFT, {"session_id": SID}, with_diffs({FARM: {"old": go_old, "new": go_code}}))
    check("drift still BLOCKS a code edit", rc == 2)
    for p in (tlog, diffs):
        try:
            os.remove(p)
        except OSError:
            pass
    clear_markers()

    # ============ DETERMINISM GATE (mark_determinism_run.py + check_determinism.py) ============
    tlog = os.path.join(TMP, f"claude-touched-{SID}.log")
    runmark = os.path.join(TMP, f"claude-determinism-run-{SID}")
    detwaiver = os.path.join(TMP, f"claude-determinism-waiver-{SID}")
    for p in (tlog, runmark, detwaiver):
        try:
            os.remove(p)
        except OSError:
            pass
    run(LOG_TOUCHED, {"session_id": SID, "tool_input": {"file_path": "/x/nakama/modules/world/match.go"}})
    rc, _o, _e = run3(CHECK_DET, {"session_id": SID})
    check("determinism BLOCKS (exit 2): sim changed, gate not run", rc == 2)
    run(MARK_DET, {"session_id": SID, "tool_input": {"command": "ls -la nakama"}})
    check("mark_determinism_run IGNORES a non-gate command", not os.path.exists(runmark))
    run(MARK_DET, {"session_id": SID, "tool_input": {"command": "bash tools/run_go_tests.sh"}})
    check("mark_determinism_run marks a gate command", os.path.exists(runmark))
    rc, _o, _e = run3(CHECK_DET, {"session_id": SID})
    check("determinism CLEARS after the gate ran", rc == 0)
    os.remove(runmark)
    with open(detwaiver, "w") as f:
        f.write("no determinism impact: comment only\n")
    rc, _o, _e = run3(CHECK_DET, {"session_id": SID})
    check("determinism CLEARS with a session waiver", rc == 0)
    os.remove(detwaiver)
    try:
        os.remove(tlog)
    except OSError:
        pass
    run(LOG_TOUCHED, {"session_id": SID, "tool_input": {"file_path": "/x/README.md"}})
    rc, _o, _e = run3(CHECK_DET, {"session_id": SID})
    check("determinism ALLOWS when no sim code changed", rc == 0)
    rc, out = run_raw(CHECK_DET, "not json")
    check("determinism FAIL-OPEN on bad stdin", rc == 0)
    for p in (tlog, runmark, detwaiver):
        try:
            os.remove(p)
        except OSError:
            pass
    clear_markers()

    print()
    passed = sum(results)
    print(f"{passed}/{len(results)} checks passed")
    return 0 if passed == len(results) else 1


if __name__ == "__main__":
    sys.exit(main())
