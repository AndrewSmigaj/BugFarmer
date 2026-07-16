---
name: certainty-assessment
description: Use to score how certain you are about a plan, a design, or a just-built change BEFORE trusting it — and emit a numeric, per-dimension certainty TABLE. Turns a lens/review pass into calibrated, evidence-anchored numbers (each row cites file:line or a gate, names a falsifier, and the gate that would raise it). Reports DESIGN CONFIDENCE (over the design-time axes, so a real weak/unread axis still shows) SEPARATELY from VERIFICATION STATUS (a pending-gate checklist) — so at plan time an always-pending gate does not misleadingly drag the whole score to "not built yet." The number ranks where to dig and exposes residual risk; it is NOT the ship gate (the execution gates are). Invoke after planning a change, after building one, or whenever you're about to claim something is "done / verified / safe."
---

# Certainty assessment → an evidence-anchored numeric table

You are asked for a number. The trap: **a confidence % is overconfident and uncalibrated by default** —
"a high % with thin evidence is a RED flag," and historically the numbers in this project were vibes that
laundered guesses into false "done." This skill makes the number *safe* by binding it to four things, every
time: an **evidence rubric** (the score is READ OFF what evidence exists, not felt), **hard anti-inflation
caps** (each = a real way this codebase has been broken), **MIN aggregation** (a chain is as strong as its
weakest load-bearing link — never average), and a standing rule that the number **ranks where to dig and
flags residual risk — it is not the ship decision.** The execution gates (`test-changes`) are the only
model-independent arbiter; "Proven" requires a gate, not a feeling.

## When to use
- After writing a **plan** (before `ExitPlanMode`) — score design/requirements/sync-fit from reads; the
  verification rows will be "gate identified, not run yet" (capped).
- After **building** a change — re-score; the gate rows flip toward **Proven** as each gate actually runs.
- Whenever you're about to write "**done / verified / complete / safe / ~94% certain**" — produce the table
  instead. A blended one-line % is exactly the failure this replaces.

It composes with the other artifacts (do NOT restate them): **what to look at** → [`lenses.md`](../../lenses.md);
**the stage×failure-mode loop + the BugFarmer invariant checklist + dynamic-prompt recipe** →
[`complex-change-review.md`](../../complex-change-review.md); **the ground-truth gates** → the `test-changes`
skill. This skill owns the **scoring**: the rubric, the caps, the MIN rule, and the output table.

## The dimensions (the core rows)
Score these independently. Mark any that don't apply **N/A** (a pure-docs change has no Sync row). Add
**dynamic rows** per change via `complex-change-review.md`'s recipe (one per invariant held / external input
consumed / cross-boundary contract / state mutation). ★ = the axes that earn their keep here.

1. **Requirements fidelity** — does it *observably* satisfy what the **user actually asked** (quote them
   verbatim), and match what the user **decided** (not what you inferred or invented)? If a requirement got
   hard, score against the **original** ask, not a quietly-relaxed one. [Requirements + Authored-Decision lenses]
2. **Comprehension** — is your mental model of the affected subsystem correct **and complete**: the real data
   flow, **every** reader/writer/emit-site, and is the data valid/populated *at your read point*? [FM1+FM2 · STAGE 1]
3. **Design quality** — extensible, no debt, **mirrors an existing pattern** (cite it), simpler alternative
   weighed, the set isn't a half-ladder, done at the right altitude (cause not symptom). [FM3+FM7 · Consistency/Simpler-Alt/Completeness]
4. ★ **Sync & determinism fit** — *the BugFarmer-critical axis.* Every sim-**READ** arrives frontier-gated /
   zone-wide (NOT view-scoped / on-receipt); **fixed-point not float**; deterministic iteration order;
   **authority-only writes** + replay (detect-don't-remove); **idempotent** under replay/re-join; snapshot
   coherence; nothing wall-clock enters `ComputeStateHash`. **LATE-JOIN COMPLETENESS is a REQUIRED sub-row, not
   optional:** if the change adds/renames ANY client sim-state feeding `ComputeStateHash` (or that moves a bug),
   is it reconstructed on a late-joiner (per-bug → verbatim relay; per-swarm/zone dict → its own snapshot
   section)? "Births/strikes ride the ledger" is NOT sufficient — the S1/S2 predation reviews were FALSELY green
   because they checked the ledger but never the snapshot, and a late-joiner's wasps re-committed to different
   prey (2026-07-14). Enumerate every hash input; a hash input with no snapshot carrier is a **Guess** that BLOCKS
   until closed by a NON-VACUOUS gate. [the invariant checklist · Determinism lens · `architecture_swarm_sync.md` §0]
5. **Correctness** — is the logic actually right at every edit: shapes/units/scale (×1000 fixed-point), the
   load-bearing algorithm, and empty/missing/duplicate/stale/vanished-mid-op inputs? [FM1-at-edit · Failure/Edge]
6. **Blast radius & contract** — are all other consumers / persistence / late-join / replay accounted for, and
   is the server↔client message contract in sync (additive is safe; renames/removals are not)? [FM4 · Data/Contract · Blast-radius]
7. ★ **Verification** — does a **model-independent gate EXERCISE this change** (give the concrete input that
   FAILS if the change is reverted — non-vacuous)? Is the test **tool** itself trusted (parser/compare/sampling)?
   Did the **preconditions** hold this run (fresh match, pinned seed, clients disjoint, entity present)? [FM5 · Verification lens]

## The rubric — read the band off the EVIDENCE, don't feel it
| Band | Score | What earns it |
|------|-------|---------------|
| **Proven** | 95–100 | A model-independent **gate passed on a clean setup AND exercises this property** (non-vacuous); *or* a direct code-read proof with the falsifier checked and **all** call sites read. Cite the line / command output. |
| **Strong** | 80–94 | Verified against **current code at file:line** (real shape, all call sites); falsifier considered; but the executable gate for this axis hasn't run yet. |
| **Plausible** | 60–79 | Reasoned from a pattern + a partial read; load-bearing facts checked but some inference; a **named** residual. |
| **Shaky** | 40–59 | Leans on a doc/memory/sub-agent not re-confirmed, OR one call-site generalized to all, OR a proxy (counts) instead of the id-level detail. |
| **Guess** | <40 | No evidence / an unverified assumption / a guess restated as fact. **A load-bearing Guess BLOCKS** — close it or surface it before proceeding. |

## Hard caps (apply BEFORE the band — the score cannot exceed the cap; each = a scar)
- **No `file:line` or command-output evidence → ≤ 50.** A bare assertion is Shaky at best. [the cardinal rule]
- **Proxy, not the load-bearing altitude → ≤ 60.** Category counts, one call-site, "looks like the siblings,"
  a sub-agent summary are proxies; the **id-level / schema / ALL-call-sites** detail is the real altitude. [verify-at-load-bearing-altitude]
- **Source is a doc / memory / sub-agent, not code you read THIS pass → ≤ 60 until re-confirmed.** Docs *you*
  wrote are NOT authority; they drift and are padded with unbuilt inventions. [FM6 · Docs-Aren't-Authority]
- **A user-intent attribution that is actually your inference → the row is INVALID.** Quote the user verbatim,
  or mark it an explicit **ASSUMPTION** (and ≤ 50). Preserve their hedges; their game-model beats real-world priors. [don't-launder-guesses]
- **A "thorough / complete" claim without the quota met + per-unit enumeration → ≤ 60.** A lean sample is not thorough. [thoroughness-means-quotas]
- **A hard requirement quietly relaxed because it got difficult → score Requirements against the ORIGINAL ask
  (usually Shaky) and flag it.** Never silently drop/redefine. [no-cowardice]
- **A high score on thin evidence is a RED FLAG, not a pass** — when score and evidence disagree, the evidence wins.

## Aggregation — DESIGN CONFIDENCE vs VERIFICATION STATUS (do NOT collapse to one MIN)
*(Updated: the old "Overall = MIN of all rows" was misleading at plan time — the always-pending Verification
row dragged every plan-time score down to "not built yet," which we already know. Report two things instead.)*

1. **Design confidence** — assessed over the DESIGN-TIME axes only (Requirements, Comprehension, Design,
   Sync-fit, Correctness, Blast-radius). **Name the weakest design axis** and pitch the confidence at roughly
   its level. The anti-false-certainty guard stays: a genuinely **Shaky/Guess DESIGN axis** — a real hole
   (unread code, an unproven algorithm, a wrong contract), NOT merely "unbuilt" — still drags it down and
   blocks; don't average a real hole away. But this number does **not** include Verification.
2. **Verification status** — reported **separately** as a checklist: which model-independent gates will
   exercise this change, and their run-state (**pending / passed / failed**). At plan time these are *pending
   by definition* — that is a **status, not a confidence penalty.** `Proven` is earned only when a gate runs.

The distinction that matters: **"unproven because unbuilt"** (expected — track it as a pending gate) is NOT
the same as **"shaky because comprehension/design is genuinely uncertain"** (a real low score — INVESTIGATE to
raise it *now*, before building). Push design confidence as high as the evidence allows before implementation;
let the gates convert it to Proven at build time. If a *design* axis is below Strong, dig there first; if only
*verification* is pending, that's normal — proceed to build and run the gates.

## Output contract — the table is mandatory
Emit exactly this, filled, every time (drop N/A rows or mark them):

| # | Dimension | Score | Band | Evidence (file:line / gate output) | Falsifier | To raise |
|---|-----------|-------|------|-----------------------------------|-----------|----------|
| 1 | Requirements fidelity | … | … | … | what observation drops it | the check that lifts it |
| … | … | … | … | … | … | … |
| — | **Design confidence (weakest design axis)** | **NN** | | **weakest design axis: <row>** | | <the investigation that lifts it> |

Then a separate **Verification: PENDING/PASSED** line listing the gates (row 7 belongs here, not in the
number). Then one line: **what this means for proceeding** — proceed to build / dig into `<design axis>` first /
blocked on `<user-decision>`. (Verification being pending is normal at plan time and is NOT a blocker by itself.)

## The loop
1. **Pick the load-bearing rows** — the 7 core (mark N/A) + the dynamic rows generated from the change.
2. **Evidence each** — read the REAL code at the load-bearing altitude; run the **cheap** gate now if it
   resolves an axis (a `LineBlocked` unit test, a grep of all emit sites). Apply caps → read the band → write
   the falsifier + the raise-it.
3. **Design confidence = the weakest DESIGN axis (rows 1-6); Verification (row 7) reported separately** as a
   pending-gate checklist. Name the weakest design axis.
4. **Close every sub-Strong DESIGN row** — do the specific thing that raises it NOW (read the remaining call
   sites, web-verify the API, grep all emit sites). Re-score. **Log how each number moved.** (Verification rows
   close later, at build time, by running their gate — don't let them hold design confidence down.)
5. **Loop until scores plateau or only a genuine USER-decision remains** (not a knowable fact — front-load it).
   Map each residual to the **execution gate that will close it**. Then — and only then — `Proven` is earned by
   running that gate.

## Premortem — before you finalize the number
Assume it is a week later and this change caused an incident. Answer each briefly; every answer is either a row
you must **re-score down** or a residual you must **name and close now**:
- **What broke — and which dimension's optimism hid it?** (the failure you'd kick yourself for missing)
- **Which load-bearing fact did I take from a doc / memory / sub-agent WITHOUT reading the code this pass?** (→ ≤60 cap; go read it)
- **What input did I assume was populated / valid at my read point** that could be empty, stale, duplicated, or vanished mid-op?
- **If a late-joiner or a replay hit this, what hash-input state has NO snapshot carrier?** (the recurring sync trap — swarm_sync §0)
- **What did the user actually DECIDE (quote them) vs. what did I infer?** An inferred "decision" INVALIDATES that row.
- **Which hard requirement got quietly easier because it was hard?** Score against the ORIGINAL ask.
If the premortem surfaces anything not already a named residual, close it now or lower the score to match — a
premortem that moves no number was not run honestly.

## Worked example — the #20 client-side-LOS plan, scored at PLAN time
| # | Dimension | Score | Band | Evidence | Falsifier | To raise |
|---|-----------|-------|------|----------|-----------|----------|
| 1 | Requirements | 88 | Strong | User chose "Client-side (recommended)" verbatim; fixes the phantom + predators strike around walls | A corner-slip lets a strike pass a thin diagonal blocker | Unity check + a harness LOS scenario |
| 2 | Comprehension | 90 | Strong | Read `RunPredationStrikes` SwarmManager:613-690 (narrow-phase), `BugCollision.cs`, `IsCellBlockedForBugs`→`_blocksBugsZoneWide` | A 2nd strike-report path exists I didn't grep | grep ALL `PredationStrike` emit sites |
| 3 | Design quality | 85 | Strong | Reuses `GetCellCoords`/`IsCellBlockedForBugs`; delegate core mirrors server `RaycastClampWithBlock`; integer Bresenham, no new singleton | A supercover walk is needed for correctness | — |
| 4 | ★ Sync & determinism | 80 | Strong | Integer Bresenham over fixed-point pos + the **zone-wide** map (verified not view-scoped, TilemapManager.cs:1206-1211); authority-only + ledgered → handoff-safe | A float sneaks into the walk → cross-client drift | **2-client sync gate BOTH halves** → would lift to Proven |
| 5 | Correctness | 78 | Plausible | Algorithm reasoned; endpoints-skip handled; but the helper isn't written/tested yet | Off-by-one on the endpoint cells | the `LineBlocked` unit test |
| 6 | Blast radius & contract | 82 | Strong | LOS only narrows victims; +2 telegraph fields are additive (`JsonUtility` ignores unknown) | A follower also runs `RunPredationStrikes` | confirm authority-only at the call site |
| 7 | ★ Verification | 65 | Plausible | Gates **identified** (Go feed test · `LineBlocked` test · sync gate · Unity) but **none have run** | — | run them |
| — | **Design confidence (weakest design axis)** | **78** | | **weakest design axis: Correctness — algorithm reasoned but the helper isn't written** | | the `LineBlocked` unit test |
| — | **Verification: PENDING** | — | | gates identified (Go feed test · `LineBlocked` · sync gate · Unity), none run | | run them at build time |

> Note the split: **design confidence is 78** (honest — the design is well-evidenced, weakest at Correctness
> which a cheap unit test lifts), and **verification is separately PENDING**. The OLD rule would have MIN'd
> these into a misleading **65** dominated by "not built yet." The plan is well-*evidenced* but **unproven** —
> proceed to build and let the gates convert it to Proven. A blended average
> would have rubber-stamped it.

## Anti-patterns (how this goes wrong)
- A number with **no evidence** behind it — the cardinal sin. · **Averaging** the rows so one fatal axis hides. ·
  Scoring "will it work" off "**it compiles**." · Citing a doc/memory/sub-agent as if it were code read this
  pass. · Restating **your inference as the user's decision**. · Calling a **lean sample** "thorough." · Quietly
  relaxing a hard requirement and scoring the easier version. · Treating a **high % as the ship gate** instead of
  running the gate. · A one-line "net certainty %" with no per-dimension table, no weakest-link, no falsifiers.
