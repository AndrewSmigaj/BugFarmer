# BugFarmer: Claude Code Development Guide

How to structure the repo, the Claude Code harness, and the human workflow for high-quality development on a multiplayer game with a deterministic simulation core, LLM-driven content pipelines, and a long-term goal of autonomous work loops.

## Three Principles

**1. Enforcement over reminders.** Instructions in CLAUDE.md, skill descriptions, and memory are advisory: they compete for attention with everything else in the context window and lose more often as it fills. Hooks, manual-invocation entry points, and injected context are deterministic: they happen every time regardless of what the model is attending to. Any rule that has been violated despite a written reminder is a candidate for conversion to enforcement.

**2. Evidence over confidence.** Model self-reported certainty is worst-calibrated exactly when it matters most: when the model has pattern-matched to a familiar-looking problem that differs from this system in one detail. Every process here that asks "how sure are you" is backed by "show the evidence": a file read with line references, a test that passed, a diff that conforms to a spec. This applies to Claude's work and to the harness itself, which should be measured with evals rather than assumed to work.

**3. Context is the scarce resource.** Performance degrades as the context window fills, and auto-compaction is lossy in ways that can quietly summarize specs into vagueness. Most failure modes in long sessions (skipped procedures, stale requirements, forgotten conventions) are partly context-fill symptoms. The recurring fixes: fresh sessions bridged by files, injection of only what is currently needed, and delegation of noisy work to subagents.

---

## Part 1: The Repo Layer

### CLAUDE.md as a router, not a manual

CLAUDE.md holds project identity, the handful of invariants that must never be violated (determinism rules chief among them), and pointers into the document map. Nothing else. Bloated CLAUDE.md files cause the model to ignore the instructions that matter; the test for every line is whether removing it would cause mistakes, and if not, cut it. If a rule keeps being violated despite being present, the file is too long and the rule is drowning: prune, or convert the rule to a hook. Do not add emphasis and hope.

Procedures live in skills and subagent definitions, which load when relevant instead of taxing every turn. Two useful mechanics: `@path/to/file` imports for pulling in the document map, and child-directory CLAUDE.md files, which load on demand when files in that directory are read. A small CLAUDE.md inside the deterministic-sim directory containing only the determinism rules is zero-infrastructure path-scoped context.

### The document map as a machine-readable manifest

Maintain the document map as structured data (YAML), not prose, so hooks can read it as well as Claude. Each entry: the doc, the source paths it covers, the owning skill.

```yaml
- doc: docs/ecology/tuning.md
  covers: [Server/Ecology/, Shared/Sim/Populations/]
  owner_skill: ecology-tuning
- doc: docs/pipeline/sprites.md
  covers: [Tools/SpritePipeline/]
  owner_skill: sprite-pipeline
```

This single file powers three enforcement mechanisms: which skill must be in context before touching which paths, which docs go stale when which paths change, and which directories are legitimate homes for new files. Claude can write the hook scripts that consume it; prompting for "a hook that blocks writes to X unless Y" works well.

### Documentation stays current by enforcement

Reminders to update docs fail because at task end the model's attention is on the finished implementation. The enforcement version: a PostToolUse hook on Edit/Write appends every touched path to a session log; a Stop hook diffs that log against the manifest and, if covered source paths changed without their doc changing, blocks the turn from ending with a message naming the exact stale doc. The block message is itself the instruction, delivered at the only moment it cannot be ignored.

Design notes. Claude Code force-ends the turn after 8 consecutive Stop-hook blocks, so this gate is a strong nudge rather than an unbreakable wall; run the same staleness check in CI as the true backstop. Allow an explicit waiver (one sentence stating why no doc update is needed, logged by the hook) so trivial changes do not generate busywork edits that degrade doc quality.

### File placement stays sane by enforcement

A PreToolUse hook on Write for paths that do not yet exist: block new top-level directories outright (exit code 2 returns the stderr message to Claude: "New top-level directories require adding a rationale line to the structure manifest first"), and validate that new files land in a legitimate parent per the manifest. The friction of updating the manifest first is the point: one deliberate sentence about where something belongs, instead of a reflexive mkdir.

### The deterministic core gets three layers

The frontier-gated deterministic sim is the highest-consequence code in the repo: a desync is expensive to detect and brutal to debug, so it gets defense in depth, all manifest-driven.

1. A skill gate scoped to those paths: a PreToolUse hook on Edit/Write that blocks changes unless the determinism skill has been read this session (a PostToolUse hook on Read marks a session-keyed flag when a SKILL.md under the skills directory is read).
2. Automatic verification: a hook that runs the headless determinism replay tests whenever those files change, before the turn can end.
3. The skill itself written as a checklist of concrete, previously-encountered violations: nondeterministic iteration order, wall-clock reads, RNG outside the seeded stream, float divergence, unordered collection serialization. Models check concrete lists far more reliably than they honor abstract principles like "maintain determinism."

---

## Part 2: Skills, Entry Points, and Subagents

### Skill hygiene comes before skill content

Three failure modes to rule out before blaming a skill's wording.

**Broken frontmatter is silent.** Skills whose YAML frontmatter fails to parse never appear in the available-skills list at all. The known culprit is multi-line description values, which auto-formatters like Prettier introduce. Keep every description on a single line, and periodically verify skills actually appear when Claude lists what is available.

**Too many skills dilute all of them.** Every skill's name and description sits in context permanently. A large library burns tokens on irrelevant options and dilutes attention on relevant ones. Prune like CLAUDE.md: if the workflow gap a skill closes cannot be named in one sentence, merge or delete it.

**Untested skills are assumptions.** The skill-creator supports evals for skills, including trigger testing and pass-rate tracking across versions. The load-bearing skills here (certainty assessment, determinism checklist) deserve small eval sets, converting "Claude probably uses this" into a measured pass rate that can be re-checked after every skill edit and model upgrade.

### Pipelines start through manual-invocation skills

For every recurring pipeline, the procedure should arrive in context by construction rather than by retrieval. A skill with `disable-model-invocation: true` is invoked explicitly as `/skill-name arguments`, with `$ARGUMENTS` available in the body:

```markdown
---
name: new-zone
description: Author a new game zone end to end
disable-model-invocation: true
---
Author a new zone: $ARGUMENTS
1. Read docs/zones/authoring.md and the zone manifest
2. [full procedure]
3. [acceptance checklist]
4. [verification step: how to prove the zone works]
```

When a task always starts through its command (`/new-zone`, `/add-object`, `/sprite-batch`, `/tune-ecology`, and the certainty workflow itself), procedure-skipping for that task is structurally impossible. Reserve description-triggered skills plus hook gating for knowledge that must apply even when the entry point varies, like the determinism rules.

### Subagents: three distinct jobs

**Pipeline subagents** (sprite/object pipeline, zone authoring) carry the procedure in their system prompt, loaded fresh on every invocation and immune to drift, and they keep noisy work (image generation calls, batch retries) out of the main context.

**Investigation subagents** are the answer to context fill during research: "use a subagent to investigate how X works" runs the exploration in a separate window and returns only a summary.

**Review subagents** provide fresh-context adversarial review, covered in Part 3.

Subagent frontmatter supports `model:` and `effort:` fields, which Part 5 uses.

### Plans and specs are files, not conversation

Every nontrivial task produces a committed plan file in `plans/` with a fixed structure: requirements verbatim, acceptance criteria as testable statements, design decisions with evidence citations, decisions deferred to implementation, an explicit out-of-scope list, and the test plan. The plan is the bridge between an expensive planning session and a cheap fresh execution session, and it is the anchor that prevents requirement drift, because unlike early-conversation context it can be re-read, re-injected, and diffed against.

The most useful specs are self-contained: files and interfaces named, out-of-scope stated explicitly, ending with an end-to-end verification step that proves the feature works. The out-of-scope section deserves particular care; the spec is the pin that prevents invention, and explicit "do not do X" lines carry much of that load. For fuzzy requirements, a useful pattern is having Claude interview you first (using its question tool) and write the resulting spec before any planning begins.

Three drift countermeasures in increasing strength: a UserPromptSubmit hook injecting the active plan's acceptance criteria every turn (a few lines, not the whole plan); a conformance table required before completion; and `/goal` conditions, below.

---

## Part 3: Verification and the Certainty Workflow

### The verification ladder

A check Claude can run is the difference between a session you watch and one you walk away from. Without one, "looks done" is the only completion signal and the human becomes the verification loop. Four rungs, trading setup for attention:

1. **In-prompt:** ask Claude to run the check and iterate in the same message.
2. **`/goal` condition:** a separate evaluator re-checks the condition after every turn and Claude keeps working until it holds. Set acceptance criteria as goal conditions during implementation runs; this is native drift-resistance.
3. **Stop hook:** a script blocks the turn from ending until the check passes (subject to the 8-block cap).
4. **Second opinion:** a verification subagent in fresh context, so the agent doing the work is not the one grading it.

Across all rungs, one behavioral rule: require evidence, not assertion. Test output, the command run and what it returned, a screenshot. Reviewing evidence is faster than re-verifying and is the only thing that works for runs nobody watched.

A gotcha specific to a sprite-based game: functional tests can pass while the result is visually broken. The verification set must include visual checks (screenshot capture and comparison via the headless clients) for anything player-facing, not just sim correctness.

### The certainty assessment skill, evidence-based

The certainty workflow (assess certainty across dimensions, investigate to raise it, human-gated plan, auto implementation with tests, report) has the right shape: explore, plan, human gate, implement, verify. Its weak joint is self-reported certainty scores, for the calibration reason in Principle 2. The fix is not removing the dimensions but attaching evidence requirements to each:

- A dimension without cited proof (files read with line references, closest existing codebase pattern named, test identified) is capped at medium certainty by rule, written into the skill.
- "Deterministic-system fit: 9/10" becomes "verified: read Shared/Sim/TickGate.cs; change uses the seeded RNG stream (line refs); no wall-clock or unordered-collection usage introduced; follows the pattern in X."
- Human review then spot-checks citations rather than auditing numbers, which is faster and catches more.

Add premortem questions to the skill ("assume this shipped and caused a desync; what was the cause?"); they surface failure modes that confidence scoring misses, at low token cost.

Every plan ends with a **decisions-deferred-to-implementation** section. This list is the dial for everything downstream: implementation effort level, how much autonomy the task can tolerate, and whether the plan is actually finished or just long. Resolve deferrable items at review time by writing them into the plan.

Run the exploration phase in plan mode, which is read-only, so investigation cannot accidentally become implementation; the plan can be edited directly (Ctrl+G) before approval. And keep a lightweight lane: if the diff can be described in one sentence, skip the ceremony entirely and just ask for the fix. Protecting trivial tasks from the heavyweight process protects the process from becoming resented.

### Adversarial review, calibrated

Before work counts as done, a reviewer in fresh context evaluates the diff on its own terms, without the reasoning that produced it. For pure correctness, the bundled `/code-review` skill reviews the current diff in a fresh subagent. For plan conformance, write the prompt: name the diff, the plan file, and instruct it to check that every requirement is implemented, listed edge cases have tests, and nothing outside scope changed, reporting gaps rather than style preferences.

Calibration warning: a reviewer prompted to find gaps will report some even in sound work. Chasing every finding produces over-engineering: extra abstraction, defensive code, tests for impossible cases. Scope the reviewer to correctness and stated requirements; treat everything else as optional.

---

## Part 4: Loop Engineering

### Deciding what to loop

Loops are not a maturity level to graduate to; they are a tool for a specific shape of task, and the decision is made per task class, not once for the project. The test: **for this class of work, has the checking currently done by hand been mechanized?** Hand-holding is a human acting as the verification loop; a loop does not eliminate that work, it either runs mechanized (tests, replays, screenshot diffs, conformance checks, adversarial review) or silently does not happen. Prompt and spec quality set the ceiling on a single iteration; verification coverage sets the ceiling on autonomy.

The second axis is failure cost. A bad sprite batch costs a revert; a bad deterministic-core change costs a debugging week when the desync surfaces. The same completion rate is acceptable for one and disqualifying for the other.

Sorting this repo's work by both axes:

**Strong loop candidates:** sprite and object pipeline batches (independent items, mechanically checkable, cheap to discard failures), ecology parameter sweeps (deterministic headless tooling already exists for exactly this), test coverage expansion, mechanical refactors and migrations fanned out across files.

**Poor loop candidates:** anything requiring design decisions mid-flight, novel work in the deterministic core, creative judgment calls such as whether a zone is actually good. These stay interactive with a human gate.

Expectations: well-defined tasks with good verification currently complete around 80% of the time, dropping on ambiguous requirements. Even in the good case, every output gets reviewed. The win is not zero involvement; it is that involvement moves entirely to plan approval and report review while throughput multiplies and runs happen overnight.

**The probe method:** do not decide in the abstract. Pick the single best-verified task class, write the spec with an explicit out-of-scope section, arm the circuit breakers, run one loop overnight in a worktree, and measure the only number that matters: did reviewing the output cost less than doing the work interactively would have? If yes, expand to the next task class; the first class where the answer is no marks the current loop frontier. The frontier moves outward every time a verification capability is added, not every time a prompt improves. That yields the standing investment rule: **an hour making the headless clients able to check one more property of the game buys more loop capability than an hour tuning the loop prompt.**

### Loop architecture: fresh context per iteration

The reliable pattern for long autonomous runs is a driver loop over `claude -p`, where every iteration starts with clean context: the same prompt file, the same spec files, plus a progress file marking what is done. Quality measurably degrades once context grows past roughly 100k tokens, and compaction is lossy, so state lives in files (spec, plan, progress, reports), never in the conversation. Each iteration reads state, does one task, updates state, commits, and dies. Do not build loops on `--continue` or `--resume`; they defeat the fresh-context guarantee. (A ralph-wiggum plugin exists that re-feeds the prompt inside one growing session via a Stop hook; the fresh-context driver loop is the more robust pattern for long runs.)

The iteration prompt shape: study the plan, pick the single most important incomplete task, implement it following existing patterns, run the named test command, on pass mark the task complete and commit, on fail fix and retest, output the completion token only when all tasks are done and tests pass.

### The loop only implements

The single biggest reliability upgrade for autonomous runs: two-phase separation where the loop never plans. A separate one-shot planning pass (the certainty skill, at high effort, human-gated) produces and refreshes the plan via gap analysis against the spec; loop iterations exclusively execute plan items. This deliberately routes autonomous time onto the model's strong capability (implementation) and keeps design, where drift compounds fastest, inside the gated phase.

### Circuit breakers and backpressure

Unattended runs need layered kill conditions: a max iteration count, a per-iteration timeout (15 minutes is a reasonable default), a token or cost cap, and stuck detection (the same test failing three iterations in a row stops the loop and notifies). Backpressure means every iteration passes deterministic gates before its work counts: compile, lint, tests, determinism replays; any non-zero exit rejects the iteration. The headless clients and replay tests are the backpressure foundation, and the leash length available is set almost entirely by how much of the game they can verify.

### Native features to adopt as scale grows

Three built-in capabilities replace homebrew plumbing as loops multiply. Native task management supports task lists with dependencies, blockers, and multi-session coordination via a shared task list ID, replacing a hand-rolled queue file. Agent teams coordinate multiple sessions with shared tasks, messaging, and a team lead, the managed version of a driver script. For permissions on unattended runs, auto mode (`--permission-mode auto`) uses a classifier to block risky actions; in `-p` runs it aborts if the classifier repeatedly blocks, since no human is present to fall back to. Combine with `--allowedTools` scoping for batch work, and prefer sandboxing where it fits. The discipline underneath (spec as pin, fresh context, verification gates, reports to files) transfers unchanged.

### Reports and notifications

Reports write to a fixed `reports/` location in a fixed format ending in the conformance table. A Notification or Stop hook pings on finish or block. The human job becomes processing a report queue and approving plans.

---

## Part 5: Effort and Token Strategy

Effort levels are low, medium, high, xhigh, and max, controlling adaptive reasoning depth. Guidance for coding and agentic work: xhigh for the hardest reasoning, high as the minimum for intelligence-sensitive work, medium only for cost-sensitive mechanical work, max reserved for correctness-critical problems (it is deliberately session-only). A documented behavior worth exploiting: at lower effort the model scopes itself to exactly what was asked rather than going beyond, which is a feature for mechanical plan execution and a hazard for open-ended design.

The assignment rule for this workflow: **xhigh for the planning/certainty session; high as the implementation floor whenever in-flight decisions remain nontrivial; medium only when the plan's deferred-decisions list is empty and no deterministic-core paths are in scope.** The deferred-decisions list is the dial, read directly off the plan at review time.

Eliminate manual dial-switching entirely by pinning effort in frontmatter: `effort: xhigh` on the certainty skill, `effort: high` on implementation subagents, `effort: medium` on truly mechanical pipeline agents. The harness then sets effort per activity and no one touches `/effort` mid-session. Mechanics worth knowing: levels low through xhigh persist across sessions once set interactively; `--effort` sets it at launch for headless runs; if the active model does not support the set level, it silently falls back to the highest supported level at or below it, so re-check after model switches.

Context size dominates effort setting in the cost equation: the entire window reprocesses every turn, so a long session at medium routinely costs more than a fresh short session at xhigh. The high-leverage habits are session hygiene, not dial management: track context with a status line, `/clear` between tasks, `/compact` with instructions when a session must continue (plus CLAUDE.md compaction guidance like "always preserve the modified-file list and test commands"), and `/btw` for side questions so they never enter history. Parallelism comes from worktrees running separate fresh sessions, not from stretching one session across projects.

---

## Part 6: The Standard Procedure

1. **Plan.** Fresh session; invoke the certainty skill (carrying `effort: xhigh`). Explore in plan mode. Output: a committed plan file with requirements verbatim, acceptance criteria, evidence-cited design decisions, deferred-decisions list, out-of-scope list, test plan. Skip to a direct request for one-sentence-diff tasks.
2. **Review the plan.** Spot-check evidence citations; read the deferred-decisions list and resolve what can be decided now by writing it into the plan (Ctrl+G edits it directly). Approve or send back.
3. **Commit the plan.** Revert point and drift anchor.
4. **Implement in a fresh session** (own worktree if parallel). Effort per the assignment rule. Load the plan; set acceptance criteria as `/goal` conditions or rely on the UserPromptSubmit injection.
5. **Auto run, unwatched.** Hooks enforce skill reads, doc updates, determinism replays; the step-3 commit and checkpoints make disasters cheap.
6. **Completion requires the test plan run plus the conformance table** (criterion, evidence, test name). Stop hook blocks without it.
7. **Adversarial review** of the diff against the plan in fresh context, scoped to correctness and stated requirements. Then human review of the diff and conformance table, not the transcript. Merge, or send back citing the failed criterion.
8. **Harvest failures.** Any new failure gets ten minutes of harness work before the next task: a checklist line in a skill, a premortem question, a hook check, a manifest fix, and for load-bearing skills, a case added to that skill's eval set.

For loop mode, steps 4 through 7 become iterations of the fresh-context driver loop with circuit breakers armed and reports accumulating in the review queue.

---

## Part 7: Operator Habits

**Course-correct early, or restart.** Esc stops mid-action with context preserved; Esc Esc or `/rewind` restores conversation and code state to any checkpoint (checkpoints track only Claude's file edits, not bash side effects, so git remains the real safety net). After two failed corrections on the same issue, stop correcting: `/clear` and rewrite the initial prompt incorporating what was learned. A clean session with a better prompt almost always beats a long session with accumulated corrections.

**One task, one context.** The kitchen-sink session (unrelated tasks sharing a window) and unscoped investigation (Claude reading hundreds of files into the main context) are the two most common self-inflicted failures. `/clear` between tasks; delegate exploration to subagents. Name long-running sessions (`/rename`) and treat them like branches.

**Review posture.** Two gates, both diff-shaped: the plan file at the front (requirements fidelity, design, evidence citations), the diff plus conformance table at the back. Between them, resist watching; interrupting a run costs more than reverting a bad one.

**Weekly harness maintenance.** The harness should be an accumulating record of every way this specific project has bitten: each incident becomes a checklist line, an eval case, a hook, or a manifest correction. This compounding, more than any individual technique, is what makes month six dramatically better than month one.

---

## Quick Reference

| Problem | Mechanism | Feature |
|---|---|---|
| Procedures skipped | Manual-invocation skills as entry points; manifest injection + edit gate; frontmatter hygiene; skill evals | disable-model-invocation, UserPromptSubmit, PreToolUse |
| Docs not updated | Touched-files log vs manifest, block turn end; CI backstop | PostToolUse + Stop |
| Bad file placement | Manifest validation on new paths | PreToolUse (Write) |
| Determinism violations | Scoped skill gate + auto replay tests + child CLAUDE.md | PreToolUse + Stop |
| Requirement drift | Spec as pin (incl. out-of-scope), criteria injection, goal conditions, conformance table | UserPromptSubmit, /goal, Stop |
| Design drift in loops | Two-phase: loops only implement; design stays human-gated | plan/build separation |
| False completion | Evidence not assertion; fresh-context adversarial review | Stop hook, subagent, /code-review |
| Runaway loops | Max iterations, timeouts, cost caps, stuck detection | driver script |
| Token burn | Effort pinned in frontmatter; fresh sessions over long ones; /clear, /compact, /btw; statusline | model-config |
| Whether to loop a task | Verification-coverage test + failure-cost test; overnight probe; review-cost metric | worktree + claude -p |

## Deploying This Guide

This document is for the human. Claude should receive it in pieces, each in the surface where it is enforced or loaded on demand: the invariants and pointers go in CLAUDE.md; the manifest schema and hook behaviors become `.claude/settings.json` hooks plus scripts; the pipeline procedures become manual-invocation skills; the certainty and determinism content becomes skills with evals; the standard procedure lives wherever plans are filed, as the template header of `plans/`. Putting this whole guide into CLAUDE.md would recreate the exact problem Part 1 exists to solve.

## Appendix: Hook Catalog

### Where the skill-read trigger fires

Three trigger points, catching three different moments; use all three because they fail independently.

1. **UserPromptSubmit** carries the routing manifest: a few lines mapping task domains to skills, injected every turn. This is the salience layer. It fires on every message including trivial ones, so keep the payload tiny; the hook receives the prompt on stdin, so the script can stay selective about when to inject the full manifest versus a one-liner.
2. **PreToolUse matched on ExitPlanMode** catches the exact "before starting a task" moment. Leaving plan mode is itself a tool call, so it is hookable: block or inject "state which required skills have been read this session; read any missing ones before implementing." This is the natural home for the check, because plan approval is the task boundary, and it fires whenever a plan is accepted regardless of who initiated plan mode.
3. **PreToolUse on Edit|Write, path-scoped via the manifest** is the deterministic backstop: no edit to covered paths until the owning skill has been read this session (session-keyed marker set by a PostToolUse hook on Read).

Advanced variant: a PostToolUse hook on Read that matches the file's path against the manifest and surfaces "relevant skill: X exists for this area" the moment Claude starts reading in a domain. Just-in-time discovery, no gating. A path-prefix match gets most of the value of fancier embedding-based versions.

### Enforcement gates (PreToolUse, exit 2 blocks with stderr fed back)

- Dangerous Bash: block force pushes, recursive deletes, database drops or resets, and anything touching production or live-server config.
- Generated-file protection: block direct edits to pipeline outputs (sprite atlases, generated code, baked zone data) with the message "edit the generator or source asset, not the output."
- Secrets: block Read/Edit on .env and credential files.
- Migration and save-data protection: block writes to schema migrations and world save formats without the corresponding skill in context.
- New-path validation and new-top-level-directory blocks per the manifest (Part 1).

### Feedback and backpressure (PostToolUse)

- Format and lint the touched file after every Edit/Write; surface failures back so they are fixed immediately rather than at review. Use `continueOnBlock: true` so the rejection returns as a tool result Claude can act on instead of aborting the turn.
- Compile check after C# edits; scoped fast tests for the module just touched (full suites stay at the Stop gate).
- Schema validation on domain files: zone JSON validated on write, sprite outputs checked for dimensions, palette, and transparency the moment the pipeline writes them.
- Touched-files logging for the doc-drift and conformance checks (Part 1).

### Context injection (stdout becomes context)

- SessionStart: inject orientation automatically: current branch, git status summary, the active plan file path, and any currently failing tests. Re-runs on resume, so it refreshes stale state.
- UserPromptSubmit: routing manifest plus the active plan's acceptance criteria (Part 2).
- PreCompact: write critical session state (modified files, test commands, active task) to a file before compaction so nothing important is lost to summarization.

### Completion gates (Stop)

- Doc-drift check against the manifest (Part 1).
- Conformance-table-exists check before a task may report done (Part 3).
- Tests-actually-ran check: scan the session log for the test command and block completion if implementation happened without it.
- Determinism replay when sim paths changed (Part 1).
- New-TODO check: block if the diff introduces TODO/FIXME markers without a corresponding plan entry.

### Observability and notification

- PostToolUse logging of all tool use to a session log: which files churn, how often tests fail, how often each gate blocks. Hook block rates are direct measurements of where the harness is working and where it is bureaucracy; review them in the weekly maintenance ritual and prune gates that block constantly without changing outcomes.
- Notification and Stop hooks that push to phone or desktop (e.g. a self-hosted push service) when a run finishes, blocks, or requests permission: the infrastructure of the report-queue workflow.
- SubagentStop: validate that pipeline subagents returned output in the expected report format.

### Mechanics worth knowing

- Two signaling channels: exit codes (2 blocks, stderr goes to Claude) for simple gates, and structured JSON on stdout for finer control. PreToolUse JSON can even rewrite a tool's arguments before it runs (`updatedInput`), which enables corrective hooks (redirecting a write to the right directory) rather than only blocking ones.
- Newer hook configurations support prompt- and agent-type hooks alongside shell commands, letting a model make judgment calls a script cannot ("does this diff actually need a doc update?"); check the hooks reference for current support before relying on it.
- Hooks run synchronously in the loop: keep them fast, and push slow checks (full test suites) to Stop rather than PostToolUse.
- Write injected text as plain project guidance. Text framed as out-of-band system commands can trip prompt-injection defenses and get surfaced to the user instead of treated as context.
- Claude writes good hooks when asked; describe the behavior and let it produce the script and settings entry, then review.

## Documentation

Best practices: https://code.claude.com/docs/en/best-practices
Hooks reference: https://code.claude.com/docs/en/hooks
Model and effort configuration: https://code.claude.com/docs/en/model-config
Full docs index: https://code.claude.com/docs/llms.txt