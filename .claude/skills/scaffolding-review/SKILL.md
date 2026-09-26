---
name: scaffolding-review
description: Use when CHANGING the behavioral scaffolding — a skill (.claude/skills/*/SKILL.md), a guide, a hook (.claude/hooks/*.py), or .claude/manifest.json — to check the change actually fires when it should, fails safe, and really changes behavior (not theater). This is the sibling of certainty-assessment: that scores game/determinism CODE; this scores changes to the rules that steer Claude. Read before adding/editing a gate, a routing rule, a skill's coverage, or a hook.
---

# Reviewing a change to the scaffolding

The scaffolding (skills + `manifest.json` + hooks) exists to make me READ the governing procedure before I
work, because prose reminders repeatedly failed. Changing it is high-leverage and easy to get subtly wrong —
a gate that never fires, one that fires on everything, a skill that documents an invention, a manifest typo
that silently disables enforcement. Reviewing it needs a different lens than game code: correctness here is
"does this fire exactly when it should AND change what I do," not "is the algorithm right."

## How the machinery actually works (know the levers before you pull them)
Wiring lives in `.claude/settings.json`; the data lives in `.claude/manifest.json`; the shared loader is
`.claude/hooks/_manifest.py`. All hooks are **fail-open** (every one try/excepts to `exit 0` = allow; a bug or
a broken manifest degrades to "no enforcement," never "blocked").

- **`manifest.json` sections:** `authoring_gates` (path-glob → skill that must be read before editing that
  file; drives `gate_authoring_edits.py` on Edit/Write/MultiEdit), `command_gates` (regex → skill, drives
  `gate_skill_commands.py` on Bash), `command_viewers` (read-only commands that never gate), `routing`
  (keyword → skill nudge), `doc_coverage` (per-doc source globs → drives `check_doc_drift.py`), `determinism`.
- **Two ways a skill gets REQUIRED, both are SUBSTRING scans:**
  1. **Authoring-gate path prefix** — `gate_plan_exit.py` takes each `covers` glob, cuts it at the first `*`
     (`tools/player_sprites/*.py` → `tools/player_sprites`), and if that prefix (len ≥ 6) appears anywhere in
     the plan text, the skill is required. `gate_authoring_edits.py` matches the *actual edited file* against
     the full glob.
  2. **Routing keyword** — `route_skills.py` (UserPromptSubmit nudge) and `gate_plan_exit.py` scan the
     prompt/plan for each `routing.keywords` substring.
- **Globs are component-aware** (`PurePosixPath.match`): `*` does NOT cross `/`, and the convention uses NO
  `**`. So `dir/*.py` matches `dir/a.py` but NOT `dir/sub/a.py` — list every level you mean to cover.
- **Markers are per-session files** (`$TMPDIR/claude-skill-read-<slug>-<session_id>`), set by
  `mark_skill_read.py` on a **Read of `…/SKILL.md`** OR a **Skill invocation**. Reading/invoking a skill clears
  its gate for the rest of that session.
- **Activation is at SESSION START.** Hooks read `settings.json` + `manifest.json` when the session begins, so
  a manifest/skill edit you make now is LIVE NEXT SESSION, not this one. You still verify the LOGIC this session
  by running `selftest.py` (it invokes the real hook scripts directly with fixtures).

## The review dimensions (score each Proven / Strong / Plausible / Shaky / Guess vs real evidence; name the weakest)
1. **Trigger correctness** — does it fire EXACTLY when it should? Check BOTH directions: the positive case
   (the file/command/plan you mean to gate is caught) AND the negative case (a sibling file, an incidental
   mention, an unrelated command is NOT caught). Evidence = run the hook with sample inputs, or trace the
   matcher. This is where over-fire (the `zonegen` scar) and under-fire (a subfolder the glob misses) live.
2. **Fail-safety** — worst case must be fail-OPEN (allow), never a lockout or a walled-off workflow. Evidence:
   the hook's try/except + the missing-manifest selftest cases.
3. **Content correctness & completeness** — if I FOLLOW the skill/guide, do I produce the right result? Is the
   procedure accurate against the REAL code (not a doc-you-wrote invention — see `docs-i-wrote-are-not-authority`)?
   Is coverage complete (every path/command that should be governed, is)?
4. **Mechanism integrity** — `validate_manifest.py` exit 0 (every glob hits ≥1 real path; every referenced
   skill has a SKILL.md; every command regex compiles; every doc exists) AND `selftest.py` all-pass. Critically:
   your new keywords/globs must NOT collide with selftest's HARDCODED fixture strings, or you flip an existing
   check — grep selftest before choosing them.
5. **Activation & timing** — be honest that the change is live NEXT session; don't claim "it's enforcing now."
   Markers are per-session.
6. **Composition** — no duplicate/contradictory routing; a doc covered by two owners is a deliberate,
   waiver-resolved overlap, not an accident; layering respected (route nudge → plan-exit → edit/command gate).
7. **Behavioral efficacy** — the hard one, and usually the weakest link. Does it actually change what I DO, or
   is it theater? A gate on a PROXY (e.g. "editing the pipeline script" as a stand-in for "doing this kind of
   work") has a real completeness gap (a pure Bash run, or a hand-write to an output dir, isn't an edit of a
   covered script). Name the gap and how it's mitigated (a `command_gate`, the routing nudge, the MAP,
   discipline). Can't be unit-proven — only reasoned now and observed over sessions.

## The gates that turn Strong → Proven (model-independent, run them)
- `python3 .claude/hooks/validate_manifest.py` → exit 0.
- `python3 .claude/hooks/selftest.py` → all N/N pass.
- **A manual trigger check** for a new gate: with the marker cleared, exercise the gate (edit a covered file /
  run a covered command / draft a plan naming the domain) and confirm it DENIES; read the skill and confirm it
  ALLOWS; confirm an unrelated sibling does NOT fire. A gate you didn't watch fire is unverified.

## Gotchas (each a real miss)
- **Keep routing keywords to human INTENT PHRASES, never tool/folder names.** `'zonegen'` (a folder name)
  matched every incidental path mention; `'make a hat'` only fires when someone means it. (See `manifest.json`
  `_routing_readme`.)
- **A meta-plan over-fires by design.** A plan that DISCUSSES several domains (like a scaffolding-reorg plan)
  trips each one's gate because the match is a substring scan. That's fail-toward-reading, not a bug — clear it
  by reading the named skills; do NOT reword the plan to dodge the gate (that's gaming it).
- **The output-write proxy gap** — the authoring gate catches editing a script, not the script writing output.
  If the failure mode you care about is "makes a mess when the tool RUNS," add a `command_gate` too, or accept
  the gap explicitly.
- **Extending is a DATA row, not hook code** — add a manifest row; only touch a hook to change mechanism.
- **Fail-open is sacred** — never write a hook path that can block on error. If unsure, the missing-manifest
  selftest cases are the contract.

Compose with `certainty-assessment` (the code sibling), `.claude/hooks/README.md` (the design intent), and
`.claude/lenses.md`. When the change is to game/determinism code, use certainty-assessment instead.
