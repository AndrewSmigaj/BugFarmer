# `.claude/hooks/` — enforcement-based repo health

Prose reminders (CLAUDE.md, memories, skill *descriptions*) repeatedly failed to make me read the governing
skill or update the docs before acting. These hooks convert the repeatedly-violated rules into **enforcement**:
a skill is *read* before you plan/edit/run in its domain, and docs/determinism are *reconciled* before a turn
or commit lands. One machine-readable **`.claude/manifest.json`** is the single source every hook reads.

## Cardinal rule: everything is FAIL-OPEN
A workflow gate must never be able to wall off the workflow it disciplines. Every hook wraps its body in
`try/except` and, on ANY error (including a missing/malformed manifest), exits 0 = **allow**. A bug here
degrades to "no enforcement", never "block everything". `selftest.py` has explicit fail-open cases for this.

## ⚠ Hooks load at SESSION START
Claude Code snapshots hooks when the session starts. **Editing `settings.json` or a hook mid-session does
NOT take effect until the next `claude` restart.** So changes here go live *next* session; use `selftest.py`
(which drives the scripts directly by subprocess) to verify logic *this* session. (The git `pre-commit` hook,
by contrast, is live the moment `core.hooksPath` is set.)

## The manifest (`.claude/manifest.json`) — the one source
| Section | Shape | Consumed by |
|---|---|---|
| `authoring_gates` | `{skill, covers:[path globs], also_skills, note}` | `gate_authoring_edits.py`, `gate_plan_exit.py` |
| `command_gates` + `command_viewers` | `{skills, patterns:[regex], note}` / `[first-tokens]` | `gate_skill_commands.py` |
| `routing` | `{skill, keywords, hint}` | `route_skills.py`, `gate_plan_exit.py` |
| `determinism` | `{covers:[globs], gate_hint}` | `check_determinism.py` |
| `doc_coverage` | `{doc, kind, owner_skill, covers:[globs]}` | `check_doc_drift.py`, `check_staged_drift.py` |

Path patterns in `*.covers` are **globs** matched right-anchored + component-aware via `_manifest.path_matches`
(`*` does not cross `/`). `command_gates.patterns` are **Python regexes** matched against command segments.
Validate with `python3 .claude/hooks/validate_manifest.py` (every glob must hit ≥1 real path; every skill/doc
must exist). **Extending the system is usually just adding a manifest row — not editing a hook.**

## The hooks (wired in `../settings.json`)
| Hook | Event (matcher) | What it does |
|---|---|---|
| `mark_skill_read.py` | PostToolUse (Read\|Skill) | Marks `<tmp>/claude-skill-read-<slug>-<sid>` when a `SKILL.md` is read or a skill is invoked. The signal every gate below checks. |
| `gate_skill_commands.py` | PreToolUse (Bash) | Denies a gated command (test/determinism runners, docker, ecology harness) until a governing skill was read this session. |
| `gate_authoring_edits.py` | PreToolUse (Edit\|Write\|MultiEdit) | Denies authoring a covered file (sim `.go`, entity JSON, zone scenes, sprite catalog…) until its skill was read. |
| `gate_plan_exit.py` | PreToolUse (ExitPlanMode) | Denies leaving plan mode if the active plan names a covered path / domain keyword whose skill is unread. |
| `route_skills.py` | UserPromptSubmit | Injects a tiny nudge to read the governing skill(s) for the prompt's domain — only for skills NOT yet read. |
| `log_touched.py` | PostToolUse (Edit\|Write\|MultiEdit) | Appends each edited path to `<tmp>/claude-touched-<sid>.log` (the session change set). |
| `mark_determinism_run.py` | PostToolUse (Bash) | Marks `<tmp>/claude-determinism-run-<sid>` when a determinism gate command runs. |
| `check_doc_drift.py` | Stop | Blocks turn-end (exit 2) if covered source changed but its doc did not. Per-doc session waiver. |
| `check_determinism.py` | Stop | Blocks turn-end (exit 2) if sim code changed but the determinism gate was not run. Session waiver; auto-clears when the gate runs. |
| `smoke_log.py` | UserPromptSubmit, Stop, PreToolUse (ExitPlanMode) | **TEMPORARY** (P0) — logs which events fire to `_smoke.log`, to confirm the new events work after the next restart. Remove once confirmed. |

Support (not wired as hooks): `_manifest.py` (shared loader + `path_matches` + `doc_drift`) · `validate_manifest.py`
· `selftest.py` · `check_staged_drift.py` (the pre-commit backstop, below).

## The two gates (keep BOTH green after any change here)
```bash
python3 .claude/hooks/selftest.py          # drives every hook by subprocess (deny/allow/fail-open) — expect NN/NN
python3 .claude/hooks/validate_manifest.py # manifest referential integrity — exit 0
```

## Git pre-commit backstop (live now)
`.githooks/pre-commit` → `check_staged_drift.py` blocks a commit whose **staged** source changed but its doc
did not (the same `doc_drift` check). Activated with `git config core.hooksPath .githooks`. Override a
legitimate case with `git commit --no-verify`. Fail-open: a checker bug never blocks commits.

## How to extend
- **Gate a new command / authoring path / domain** → add a row to the relevant manifest section. No hook edit.
- **Cover a new doc** → add a `doc_coverage` entry (`kind: reference` if it maps to no source).
- **A whole new hook** → add the script (fail-open!), wire it in `../settings.json`, add `selftest.py` cases
  (including a fail-open case), and add it to the table above. Restart to activate.
- **The ritual that compounds:** every new failure-mode → a manifest row / selftest case / doc_coverage entry.
