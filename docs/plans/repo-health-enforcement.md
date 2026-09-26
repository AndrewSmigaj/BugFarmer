# Plan — Adopt Fable's Claude-Code repo guide: enforcement-based repo health (execution-ready)

> **This plan is the bridge across a compaction.** After planning we compact; a fresh session executes from
> THIS FILE + `docs/guides/claudecode/claudecoderepoguide_claude.md` (the design authority — read it first).
> Do the phases in order; each is independently committable. Owner-gated at each phase boundary.

## PROGRESS (execution log — newest last; the resume pointer)
- **P0 DONE (in-session).** Events doc-confirmed supported (v2.1.211); `smoke_log.py` logic-verified; wired on
  `UserPromptSubmit`/`Stop`/`PreToolUse:ExitPlanMode`. **Reload finding: hooks snapshot at SESSION START** →
  nothing wired this session fires until a restart; `selftest.py` is the in-session logic gate. LIVE-FIRE +
  logger-removal queued for the next restart (see P0).
- **P1 DONE.** `.claude/manifest.json` created (5 authoring_gates + 3 command_gates + command_viewers, exact
  behavior-preserving copies of the old hardcoded tables; 37 doc_coverage entries covering all 16
  architecture docs + every art/authoring guide). Shared `_manifest.py` loader; both gate hooks refactored to
  load it; `validate_manifest.py` (exit 0); `selftest.py` 35/35 (added 2 manifest-fail-open cases). All hooks
  stay pure-stdlib + fail-open (missing/broken manifest → ALLOW, proven by selftest).
- **Doc-hygiene findings surfaced during P1 → feed P6:** (a) `docs/guides/art/bugs_new.md` is a bug-system
  architecture doc MISFILED in art/ and duplicating `architecture_bugs.md` — resolve/merge; (b)
  `architecture_entity_sync.md` is stale (superseded by `architecture_swarm_sync.md` for the bug half);
  (c) `block_prompts.md` references `tools/lab_server.py` which no longer exists (stale reference).
- **P2 DONE.** route_skills.py (UserPromptSubmit nudge for UNREAD relevant skills) + gate_plan_exit.py
  (ExitPlanMode: scans active plan for covered paths/keywords, denies if a touched-domain skill is unread) +
  manifest `routing` table. Wired (live next restart). selftest 44/44. Committed 11f9bdc.
- **P3 DONE.** log_touched.py (PostToolUse) + check_doc_drift.py (Stop: exit-2 if covered source changed but
  its doc did not, per-doc session waiver) + check_staged_drift.py via committed .githooks/pre-commit
  (core.hooksPath=.githooks ACTIVE NOW — git hook live this session; Stop hook live next restart). Shared
  doc_drift() in _manifest.py. selftest 55/55. Committed 5b9eaf2.
- **P4 DONE.** child nakama/modules/world/CLAUDE.md (determinism checklist, grounded in swarm_sync §0) +
  manifest `determinism` scope + check_determinism.py (Stop) + mark_determinism_run.py (PostToolUse Bash).
  selftest 62/62. Committed 829bf90. **Hooks README** written + committed 8502f7d.
- **P5 DONE.** docs/plans/ (README + TEMPLATE + this plan copied as repo-health-enforcement.md) + premortem
  subsection added to certainty-assessment. Committed c54beff.
- **P6 (audit only) DONE.** Skill-frontmatter audit: all 15 skills single-line desc + closed frontmatter →
  NO silent-unlist hazard; `effort:` pinned on 0/15 (a real gap). Merge/cut NOT done (OUT OF SCOPE: scar-born stay).
- **STOPPED HERE — owner-review queue.** Enforcement system P0-P5 COMPLETE, tested (selftest 62/62, validate
  exit 0), 10 commits. DEFERRED for owner (taste/destructive/big): trim CLAUDE.md to a router; effort-pinning +
  manual-invocation frontmatter (do WITH review — silent-unlist hazard); doc-hygiene fixes (bugs_new.md dup,
  entity_sync stale, block_prompts->lab_server.py); (P7) visual verification + loop engineering + skill evals
  (need Unity/owner setup; loops have burned overnight sessions). Then the PARKED game work resumes.
- **⚠ NEXT-SESSION FIRST ACTION:** confirm `.claude/hooks/_smoke.log` shows UserPromptSubmit + Stop +
  ExitPlanMode fired (proves the new hooks are live) → then REMOVE the 3 smoke loggers from settings.json +
  delete smoke_log.py (see P0). The real gates (route_skills, gate_plan_exit, doc-drift, determinism) are now live.

## Context / why
All of today's lost time traces to two things the guide names: **reminders don't fire** (CLAUDE.md + memory
told me to read `test-changes`/design docs; I didn't — the `gate_skill_commands` HOOK is what worked) and
**docs drift** (stale docs → I re-derived designs wrong for hours). Goal: convert the repeatedly-violated rules
into ENFORCEMENT (hooks + a machine-readable manifest), so repo health is structural, not willpower.

## PARKED — return after this pass (do NOT lose)
- **Centipede** → SWARM model + client-side per-individual decisions (staggered attacks, better combat); fixes
  "no synced knots." Committed swarm-of-1 (`03a8e4a`) is the OLD state; the swarm move was discussed, not committed.
- **village_21_B per-bug audit + D23 nursery layer** (open/harvest=random-portion-rest-perish/destroy=occupant-break+pickup).
- **Insect-accurate life stages (own plan):** beetle egg→larva→pupa→adult (individual-to-individual, pupa→silk);
  butterfly eggs+caterpillar on milkweed → chrysalis wanders off to tree/bush/fence → adult; fly = nursery.

## EXISTING INFRA (verified — the new hooks EXTEND this; don't reinvent)
`.claude/hooks/` (wired in `.claude/settings.json`), all **fail-open** (any error → exit 0 = allow), session-keyed:
- `gate_skill_commands.py` — PreToolUse/Bash. `GATES = [([skill slugs],[cmd regexes],note)]`; blocks a gated
  command until a governing skill's `SKILL.md` was read/invoked this session. Extend = add a GATES row.
- `gate_authoring_edits.py` — PreToolUse/Edit|Write|MultiEdit. `PATHS = [(skill,[path regexes],note)]`; blocks
  authoring a file until its skill was read. **This is Fable's "Edit-path gate" already half-built.**
- `mark_skill_read.py` — PostToolUse. Marks `<TMPDIR>/claude-skill-read-<slug>-<session_id>` on Read of a
  `SKILL.md` OR a `Skill` invocation.
- `selftest.py` — drives the scripts end-to-end via subprocess; extend it for every new hook.
- Hook contract: exit 2 + stderr = BLOCK (fed back to me); exit 0 = allow; PreToolUse can deny via JSON
  `{"hookSpecificOutput":{"permissionDecision":"deny","permissionDecisionReason":"..."}}`.
- **Repo facts (verified):** NO CI · NO screenshot/visual test in the headless client · 15 skills (all
  scar-born) · CLAUDE.md 138 lines · 257 docs (most are brainstorms/idea docs, NOT code-coverage docs) · plans
  live uncommitted in `~/.claude/plans`.

---
## P0 — Smoke-test the NEW hook events (ADAPTED by the reload finding — read this)
**Why:** our `settings.json` only used `PreToolUse`/`PostToolUse`. P2/P3/P4 rely on `UserPromptSubmit`, `Stop`,
and a `PreToolUse` matcher on **`ExitPlanMode`** — previously unproven here.
**FINDING (2026-07-15 · guide-agent + official Claude Code docs, v2.1.211):** (1) all three events ARE
supported; (2) a `PreToolUse` `matcher:"ExitPlanMode"` DOES match the built-in tool — same exact-match
mechanism as our `Bash` / `Edit|Write` matchers; (3) both `UserPromptSubmit` and `Stop` stdin carry
`hook_event_name` + `session_id`. **BUT hooks are snapshotted at SESSION START** — a mid-session `settings.json`
edit does NOT take effect until a restart (`claude --resume`). So NOTHING wired this session (smoke loggers OR
the real P1–P6 hooks) fires until the next session.
**Consequence (the approach the finding forces):** a "live-fire this turn" test is impossible without a
disruptive restart. Therefore — (a) the EVENT-SUPPORT risk is retired by the docs above; (b) **`selftest.py` is
the in-session LOGIC gate** (drives the scripts by subprocess, independent of Claude Code loading them) — keep
it GREEN after every phase; (c) LIVE-FIRE confirmation is deferred to the next natural session start, where the
wired smoke loggers (`smoke_log.py` → `.claude/hooks/_smoke.log`) give a clean per-event signal AND the real
hooks self-demonstrate.
**Done this turn:** `smoke_log.py` written + logic-verified by subprocess (all 3 events log correctly); wired on
`UserPromptSubmit`, `Stop`, and `PreToolUse:ExitPlanMode`; new `settings.json` re-validated; `_smoke.log` reset.
**NEXT-SESSION VERIFICATION (do at the next restart, before removing the loggers):** confirm `_smoke.log` shows
all 3 events fired; **if the `ExitPlanMode` matcher did NOT fire** → fall back to `UserPromptSubmit` + the
Edit-path gate for P2 (layered by design). Then REMOVE the temporary smoke loggers from `settings.json` + delete
`smoke_log.py`.

## P1 — The manifest (KEYSTONE; every hook below reads it)
**Requirement:** one machine-readable **`.claude/manifest.json`** (JSON, NOT YAML — the hooks are pure-stdlib +
fail-open; `pyyaml` is available but adding `import yaml` risks the fail-open guarantee, so stay stdlib `json`)
mapping docs↔source-paths↔owning-skill, so the gate/staleness/placement hooks all read ONE source (today the
mappings are duplicated in each hook's table).
**Schema** (per entry): `doc:` · `covers: [source path globs it documents]` · `owner_skill:` · optional
`kind: code_doc|reference` (reference = brainstorm/idea doc, EXCLUDED from staleness).
**Scope decision:** only **code-documenting docs** need `covers:` (the ~16 `architecture_*.md`, the pipeline
guides in `guides/art` + `guides/authoring`, `test-changes`/`frontier-sync` domains). The ~200 brainstorms are
`kind: reference` (no `covers`). Seed `owner_skill` from the existing `gate_*` tables (they already encode it).
**Acceptance:** (1) every `architecture_*.md` + pipeline guide has a `covers:` + `owner_skill`; (2)
`gate_skill_commands.py` + `gate_authoring_edits.py` are refactored to LOAD the manifest (their hardcoded
tables become manifest rows) with `selftest.py` still green; (3) a `validate_manifest.py` asserts every
`covers:` glob matches ≥1 real path and every `owner_skill` exists.
**Verify:** `python3 .claude/hooks/selftest.py` green after refactor; `python3 .claude/hooks/validate_manifest.py` exits 0.

## P2 — Skill-read enforcement (fixes today's #1 failure)
**Requirement:** I must have read the relevant skill/docs BEFORE planning/implementing in a domain. Three
LAYERED triggers (Fable Appendix — they fail independently):
- **(a) `UserPromptSubmit`** → `route_skills.py`: reads the manifest, matches the prompt/domain, injects a
  TINY routing line ("domain X → read skill Y / doc Z") — salience BEFORE planning, cheap (keep payload small).
- **(b) `PreToolUse` on `ExitPlanMode`** → `gate_plan_exit.py`: blocks leaving plan mode until the required
  skills for the touched domain were read this session ("state which you've read; read the missing ones").
  Exiting is always a tool call I make → reliably fires regardless of who entered plan mode.
- **(c) Edit-path gate** = the EXISTING `gate_authoring_edits.py`, now manifest-driven (P1).
**Acceptance:** in a fresh session, an attempt to `ExitPlanMode` on a plan touching a covered domain without
having read the owner skill is DENIED with the skill named; reading it clears it. `route_skills.py` payload
≤ ~5 lines. `selftest.py` extended to cover (a)(b) and green.
**Verify:** selftest cases for gate_plan_exit (deny-without-marker, allow-after-marker) + route_skills (injects
for a known domain, silent for none).

## P3 — Doc-drift enforcement (fixes today's stale-docs disaster)
**Requirement:** a turn can't end (and ideally a commit can't land) with covered source changed but its doc not.
- `PostToolUse` Edit/Write → `log_touched.py`: append each edited path to `<session>/touched.log`.
- `Stop` → `check_doc_drift.py`: diff `touched.log` vs manifest `covers:`; if a covered path changed and its
  `doc` did NOT, **exit 2** naming the exact stale doc(s). Allow a one-line waiver ("no doc change needed: <why>",
  logged). Note the 8-block cap → strong nudge, not a wall.
- **+ git pre-commit backstop** — a COMMITTED `.githooks/pre-commit` + `git config core.hooksPath .githooks`
  (version-controlled, unlike `.git/hooks`; no git hooks exist today — verified): same staleness check on staged
  files; blocks the commit. This is our real backstop absent CI.
**Acceptance:** editing a covered source file without its doc → the Stop hook names the doc; a waiver line clears
it; the pre-commit hook blocks a `git commit` with the same drift. selftest extended + green.
**Verify:** selftest drift cases (covered-change-no-doc → block; +doc → pass; +waiver → pass).

## P4 — Determinism defense-in-depth (highest-consequence code)
**Requirement:** the frontier-gated sim (`nakama/modules/world/`) can't be edited casually.
- Child `nakama/modules/world/CLAUDE.md` — determinism rules ONLY (the concrete-violation checklist: nondeterministic
  iteration order, wall-clock, RNG outside the seeded stream, float divergence, unordered-collection serialization).
- Manifest scope those paths → `owner_skill: frontier-sync` (+ `test-changes`); gate_authoring_edits blocks edits
  until read.
- `Stop` → run the headless determinism replay (`tools/sim-determinism` / the sync gate) when sim paths changed,
  before the turn ends.
**Acceptance:** an edit under `nakama/modules/world/` without frontier-sync read → denied; a sim-path change with
the determinism check unrun → Stop-blocked. **Verify:** selftest + a real `bash tools/run_go_tests.sh` / sim-determinism run.

## P5 — Plan/spec discipline
**Requirement:** committed, structured plans that survive compaction + prevent drift.
- Committed `plans/` in-repo (template header: requirements verbatim · acceptance criteria (testable) ·
  evidence-cited design · **deferred-decisions** · **out-of-scope** · test plan). Integrate with the harness
  plan-mode file (copy the approved plan into `plans/<slug>.md` at commit).
- `Stop` → conformance-table check: a task can't report "done" without a table (criterion · evidence · test name).
- Add **premortem** questions to `certainty-assessment` (already has the evidence caps: no file:line → ≤50).
**Acceptance:** a completion without a conformance table is Stop-blocked; the certainty skill emits a premortem line.

## P6 — Hygiene
- Trim `CLAUDE.md` to a **router** (identity + invariants + manifest pointer); move procedures into skills. Keep
  the scar-born gotchas (determinism orientation, save-not-builder) — they earned it.
- **Skill audit** through the owner's **scar-born-vs-guess-born** lens (backlog) — merge/cut only guess-born,
  one-sentence-gap failures; single-line-frontmatter check (multi-line desc = silently unlisted skill).
- Pin `effort:` in frontmatter (xhigh certainty · high impl · medium mechanical).
- Convert pipelines to **manual-invocation** skills (`disable-model-invocation`): `/add-object`, `/sprite-batch`,
  `/tune-ecology`, etc. → procedure-skipping structurally impossible.

## P7 — Autonomy-ceiling infra (last; raises what loops can safely do)
- **Visual verification FIRST** (our biggest gap): headless client screenshot capture + baseline compare, wired
  into `test-changes` — so art/UI regressions are caught (functional tests pass while sprites read wrong).
- **Loop engineering — the probe method:** pick ONE best-verified task class (sprite batch / ecology sweep),
  write the spec with out-of-scope, arm circuit breakers (max iters, per-iter timeout, cost cap, stuck-detect),
  run ONE overnight loop in a worktree, measure: did reviewing the output cost less than doing it interactively?
  Loops **only implement**; planning stays the gated `certainty-assessment` phase.
- **Skill evals** for the load-bearing skills (certainty-assessment, frontier-sync/determinism).

## Throughout
Write a **hooks README** (`.claude/hooks/README.md`: each hook, its event, what it reads, how to extend).
**Weekly harness-maintenance ritual:** every new failure → a checklist line / GATES-or-PATHS row / eval case /
manifest fix (this compounding IS the win).

## OUT OF SCOPE (do NOT do)
- No new top-level dirs without a manifest rationale. · No rewriting the sim for determinism (only GATE it). ·
  No aggressive skill deletion (scar-born stay). · No full 257-doc manifest — only code-docs get `covers`. ·
  The parked bug/nursery/insect work is NOT part of this pass.

## DEFERRED DECISIONS (resolved this pass)
- **RESOLVED — Manifest = `.claude/manifest.json`** (JSON/stdlib to preserve hooks' fail-open; not YAML).
- **RESOLVED — Doc-drift backstop = committed `.githooks/pre-commit` + `core.hooksPath`** (no CI stand-up now).
- OPEN — Committed-`plans/` integration mechanism with the harness plan file (decide at P5).
- **RESOLVED — Order = P0 → P1 → P2 → P3** first, then P4, P5, P6, P7. (P0 added by the certainty pass.)

## TEST PLAN (overall)
`python3 .claude/hooks/selftest.py` green after EVERY phase · `validate_manifest.py` exits 0 · a fresh-session
manual pass: (plan touching a covered domain without reading its skill → ExitPlanMode denied) + (edit covered
source w/o doc → Stop names it) + (sim edit w/o frontier-sync → denied) · `bash tools/run_go_tests.sh` still green.
