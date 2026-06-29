---
name: deep-investigate
description: Use to deeply investigate ONE reported problem (a playtest bug, a wrong behavior, a console error, a "why does X happen") and produce a written findings + recommendation document — WITHOUT fixing it. Traces the issue to a fully-understood root cause across the whole stack, proposes the right (good-design, no-debt) solution, self-reviews it with evidence-gated certainty levels + a lens pass, then closes every certainty gap and writes a morning-readable debrief. Investigate-and-recommend ONLY: it makes NO code/data/art changes — the fix is a separate, human-approved step. Invoke once per issue (a plan loops it over a list).
---

# Deep-investigate one issue → findings + recommendation (NO fix)

The deliverable is a **document**, not a code change. You root-cause ONE issue to the point where the
fix is obvious and de-risked, write it up, then critically review your own write-up until certainty is
maxed — so a human can approve the fix in the morning from the doc alone.

## Hard rules (these define the skill — do not violate)
- **Investigate-and-recommend ONLY. Make NO changes to code, data, art, zones, or config.** The only
  files you write are the findings doc (and read-only probes under `tools/_generated/`). The fix is a
  separate approved step. (Allowed: spin up the backend, run tests/harnesses, render previews, write the doc.)
- **Never guess — read the REAL code at the load-bearing altitude.** The real function, the real call
  site, the real data shape, ALL call sites. A claim without a `file:line` is a hypothesis, not a finding.
- **Always re-verify sub-agent findings against the actual source.** Explore agents give breadth fast but
  are wrong often enough that one already injected a false claim into this codebase. Every load-bearing
  claim an agent makes gets re-read by you in the real file before it enters the doc.
- **Symptom ≠ cause, and there may be MORE THAN ONE cause.** Do not stop at the first plausible
  explanation. Trace to the actual root, and keep looking for additional contributors until the picture
  is complete and self-consistent.
- **Anti-anchoring — DERIVE the cause, don't CONFIRM a guess.** Start from the symptom and enumerate
  SEVERAL competing hypotheses before reading deeply. A navigation pointer (which file/subsystem to look at)
  is "where to look," NEVER "what's wrong" — the cause may live in a different file, in data, in persistence,
  or on the other side of the wire. Treat ANY handed-down lead (a plan note, a recon result, a sub-agent's
  claim, your own first hunch) as a hypothesis to actively try to **DISPROVE**, not confirm. Do not close on
  the first plausible fit; only converge when the evidence rules out the alternatives.
- **Certainty is evidence-gated.** A `%` is a *ranking of how well-evidenced a claim is*, never a vibe.
  90%+ means "I read the thing that proves it." Front-load EVERY surprise/uncertainty into the open before
  you call it done — do not leave a knowable unknown for the morning.
- **Don't launder guesses as the user's decisions; quote the user verbatim** when attributing intent. The
  user's game-model beats real-world priors. Docs *I* authored are NOT authority — built artifacts + the
  user's words are.
- **No cowardice.** If the real cause is hard, ugly, or implicates earlier work, say so plainly. Never
  soften, drop, or redefine the problem to make it tractable.

## Output contract — one doc per issue
Write `docs/product/investigations/<issue-slug>.md` (the existing home — see `determinism_audit_2026-06-20.md`,
`crash_investigation.md`; do NOT invent a new folder). The doc is a LIVING artifact: it starts as findings +
proposed solution (Phase 2), then accumulates the critical review, lens pass, and gap-closing log, and ends
with the **Debrief at the very top** (written last, read first). Use the template at the bottom of this skill.

## The phases

### 0 · Frame & reproduce
- Restate the issue in precise terms; **quote the user's report verbatim** so intent isn't drifted.
- Pin: the observable **symptom**, the **expected** behavior, **repro conditions** (which zone, single- vs
  multi-client, fresh vs persisted save, which build, what triggers it), and all **evidence** (console
  lines, screenshots, numbers).
- Write the **acceptance test**: the concrete observable that proves "resolved."
- **Classify** the issue → routes the subsystems, docs, and gotchas to check:
  render/display · bug-sim/determinism · data/content · server logic · persistence/save · networking/wire
  · UX/UI · performance · economy/balance. (An issue can span several.)

### 1 · Investigate to root cause (understand the SYSTEM, not just the symptom)
- **Hypotheses FIRST (before deep reading).** Write down 3–5 plausible causes spanning the stack (client
  render, wire, server logic, data, persistence, determinism). The job is to DISPROVE them with evidence, not
  to pick a favourite and confirm it. Any pointer you were handed (plan note / recon / sub-agent) is just one
  hypothesis — and the prime suspect to try to FALSIFY first.
- **Trace the full path** symptom → cause across the stack: client render → wire/opcode → server logic →
  canonical data → persistence → determinism boundary. Read the real code at every step.
- Build a **correct mental model** of the affected subsystem (this is `complex-change-review.md` STAGE 1
  UNDERSTAND — fire its cells). You should be able to explain how it's *supposed* to work, with citations,
  before you explain what's wrong.
- **Run the BugFarmer triage checklist** (below) to quickly rule the known traps in or out.
- **Gather evidence with real probes**, not assertions: greps/audits (Python), `git log`/`git blame` for
  regressions, the headless gates (Go tests in Docker, the sim-determinism harness, render previews), and
  — when the issue needs a live server — **spin up the backend** (`run-backend` skill) and reproduce it.
- **Enumerate hypotheses, then kill them with evidence.** Record what you ruled OUT and why (this is half
  the value — it stops the morning re-litigation).
- Sub-agents (Explore/general) for breadth — then **re-read every load-bearing claim in the source yourself.**

### 2 · Write the findings + proposed-solution doc
Create the doc (template below). Fill: Issue & repro & evidence → Root cause (the full `file:line` chain) →
How the system actually works → Ruled-out hypotheses → **Proposed solution** (the recommended one) →
Alternatives considered + why rejected → Files that would change → Determinism/risk/blast-radius →
Verification plan (how the eventual fix gets proven). Recommend the **good-design** option, not the quickest
patch; if the clean fix is bigger, say so rather than quietly proposing a band-aid.

### 3 · Critically review the doc + assign certainty
Re-read your own doc adversarially and score **evidence-gated certainty %** for each:
- **Root cause correct AND complete** (no second cause hiding) — %
- **Proposed solution actually fixes it** — %
- **System fully understood / no remaining guesses** — %
- **Good design — not a hack, fixes cause not symptom, adds no code debt, done at the right altitude** — %
- **No determinism/sync regression** (if it touches the sim) — %
Run the `complex-change-review.md` MATRIX cells live for the change's stage + the **BugFarmer invariant
checklist**. Every load-bearing answer needs evidence; an UNKNOWN is a gap for Phase 5, not a pass.

### 4 · Lens analysis
Fire the relevant lenses from [`.claude/lenses.md`](../../lenses.md) (the ★ high-value ones always; plus the
domain lenses for the issue's class — Determinism, Data/Contract, Verification, Content-Reachability,
Hidden-Asset-Cost, Simpler-Alternative, etc.). For each lens that surfaces something, record it and
**re-score the affected certainty**.

### 5 · Close every certainty gap (raise the numbers)
For EACH sub-threshold certainty (treat <90% as a gap), do the specific investigation that would resolve it
— read the remaining call sites, run the probe/harness, blame the regressing commit, spin up the backend and
observe, write a minimal reproducible experiment. Loop until certainty plateaus or you hit a genuine
*user-decision* (not a knowable fact). **Log what you did and how each number moved.** Front-load surprises.

### 6 · Recommendation report & morning debrief
Write the **Debrief** at the TOP of the doc: 1–2 sentence TL;DR · the root cause in one line · the recommended
fix + why · the certainty table · risks/determinism · rough effort · and **exactly what needs YOUR decision**
(if anything). End with a clear status: `READY TO IMPLEMENT` or `BLOCKED ON: <decision>`.

## BugFarmer triage checklist (rule each in/out fast — these are the recurring traps)
- **Stale persisted save** overriding authored zone state → the "it disappeared / wrong count" class.
  Persisted `ChunkSave`/`SwarmSave` overlay beats the authored zone; a fresh server or `FRESH=1` reset
  changes the answer. (`zone_persist.go`; the `bug-spawning` skill.)
- **Lazily-loaded chunks** — `state.Chunks` only holds SUBSCRIBED chunks; zone-wide scans must load the full
  grid from disk (force-recreate builder+nakama to deploy a rebuilt plugin).
- **Sprite `.meta` / import** — `spriteMode 2` vs `1`, PPU 16 vs the default 100 ("micro sprite"),
  filterMode. (object_pipeline.md "PPU 16 gotcha".) **But verify the symptom** — `Resources.Load<Sprite>`
  returns the first sub-sprite for Multiple-mode, so spriteMode 2 does NOT always break rendering.
- **"Data shipped, art never made"** — an occupant/item is placed/referenced but its sprite file was never
  created/committed (cherry/plum trees, dead-bug carcasses, beetle_carrion, leaf_litter all hit this).
  Audit: does every placed occupant + droppable item resolve to a real sprite file?
- **Determinism / sim-hash boundary** — float vs fixed-point, map/set iteration order, RNG draw order. A
  sim-INPUT must arrive via a frontier-gated ledger event or a snapshot; a DISPLAY-only value must NOT enter
  `ComputeStateHash`. (`architecture_swarm_sync.md` §0; the `frontier-sync` skill.) `movement_style`,
  `flies_over_fences` etc. are hash-bearing — changing them is a determinism change.
- **Published-vs-canonical drift** — `nakama/data/entities/*` is canonical; `Resources/Data/entities/*` is
  published output. `publish_entities.py --check` catches drift. Top-level vs `world`-nested fields
  (wasp_nest's `sprite_w` bug).
- **Footprint-X shift** for even-width occupants; **tests run in Docker only** (`tools/run_go_tests.sh`,
  never local `go`); **sync runs need a FRESH match** (strays/persisted match = false divergence).

## Certainty rubric
- **95–100%** — I read the exact code/data that proves it; I can cite the line; I checked all relevant call
  sites; (if testable) a headless gate confirms it.
- **75–90%** — strong evidence, one or two unread call sites or an unrun experiment remain → a Phase-5 gap.
- **<75%** — a real hypothesis with partial evidence, OR a genuine user-decision. Never present as settled.
Always state WHAT would move a number up, and in Phase 5 go do it.

## Tools available (investigate-only)
Code reads/greps · Python audits · `git log`/`blame` (regression hunting) · Go tests via Docker
(`bash tools/run_go_tests.sh`) · the `tools/sim-determinism` headless hash gate · the sync-harness ·
render previews (`make_scene.py`, ad-hoc PIL comparisons) · **the live backend** via the `run-backend` skill
when an issue needs a running Nakama/Postgres/client to reproduce. None of these change the game's source.

## Findings-doc template
```markdown
# Investigation: <issue title>
_status: <DRAFT | READY TO IMPLEMENT | BLOCKED ON …> · investigated <date> · investigate-only (no fix applied)_

## Debrief (read me first)   ← written LAST
- **TL;DR:** <1–2 sentences: what's broken and why>
- **Root cause:** <one line, with the file:line>
- **Recommended fix:** <one line> — because <one line>
- **Certainty:** cause <%> · fix <%> · design <%> · determinism <%>
- **Risk / determinism:** <…>   **Effort:** <S/M/L>   **Needs your decision:** <none | …>

## 1. Issue, repro & evidence
> <verbatim user report>
- Symptom · Expected · Repro conditions (zone/clients/save/build) · Evidence (logs/numbers) · Acceptance test.

## 2. Root cause (the chain)
<symptom → … → cause, each step a file:line. Name the single defect (and any second contributor).>

## 3. How the system actually works
<the correct mental model of the subsystem, with citations — so the fix is obviously safe.>

## 4. Ruled out (not the cause)
<hypothesis → the evidence that killed it.>

## 5. Proposed solution
<the recommended fix.> · **Alternatives considered:** <option → why rejected.> · **Files that change:** …
· **Determinism / risk / blast-radius:** … · **Verification plan:** <how the fix gets proven>.

## 6. Critical review + certainty
<the Phase-3 table + complex-change-review/invariant answers, each with evidence.>

## 7. Lens analysis
<each fired lens → finding → certainty delta.>

## 8. Gap-closing log
<each Phase-5 check → what I found → how certainty moved.>

## 9. Open decisions for you
<only genuine user-decisions, each with a recommendation.>
```

## Anti-patterns (the ways this goes wrong)
- **Anchoring on a handed-down candidate cause** and confirming it instead of deriving the cause from
  evidence (the recon/plan lead may be a plausible-but-wrong guess; falsify it first). · Stopping at the
  first plausible cause (there may be two). · Trusting a sub-agent's `file:line` without
  re-reading it. · A certainty number with no evidence behind it. · Proposing a band-aid because the clean
  fix is bigger (flag the clean fix instead). · Quietly making a code change "while I'm here" (this skill
  NEVER edits source). · Calling a sim-touching change safe without naming the hash boundary. · Leaving a
  knowable unknown for the morning instead of front-loading it now.
