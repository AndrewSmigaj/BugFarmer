---
name: thorough-research
description: Invoke for ANY non-trivial research, "look up how X is done / research best practices / how do good games do Y / find the right approach" task BEFORE proposing a design or writing code. This is the anti-bare-minimum gate — the default failure is "do half a search, find a couple things, call it good," and that is a FAILURE here. Forces breadth by agent fan-out, deep-reading (not snippets), ≥4 scored candidates per hard choice, an adversarial cold-critic loop until it finds nothing, and self-verification of load-bearing claims against the real code/docs. Pairs with certainty-assessment (the scoring gate) and deep-investigate (root-causing ONE bug). Read this the moment a task says "research" or "how should we do X".
---

# Thorough research — breadth by construction, not willpower

The enemy this skill kills: **the half-search.** On any "research how to do X" task the lazy path is a couple
of web searches, a few snippets, and a confident writeup — which repeatedly ships **affirmatively-wrong**
claims and **feature-breaking design flaws** that a single skeptical pass would have caught. The countermeasure
is to make thoroughness **structural and countable**, so shallowness is a visible failure, not a judgment call.

## The rule that matters most
**If a cold critic can point at a real improvement — a missing technique a great example uses, an unverified
claim, a cheaper approach, a wrong candidate ranking — you under-researched. Keep going until it can't.** The
critic loop below operationalizes this; it is the highest-value part of the skill (it has caught wrong claims
AND a critical design flaw in one session). Do not skip it to save time — it IS the work.

## The gates (all COUNTABLE — missing a count = not done)

### 1. Breadth by AGENT FAN-OUT (not your willpower)
Each research stage runs **≥3 parallel Explore/research agents**, each assigned a distinct cluster and required
to **DEEP-READ ≥5 sources in full** (WebFetch the actual article/repo/talk — NOT search snippets) and **study
the actual code of ≥1 real open-source implementation**. So a stage covers **≥15 deep-read sources + ≥3 studied
codebases by construction.** Each agent returns a **source table**: `source → concrete technique → cost/perf →
does it fit OUR constraints`. Under the count = the agent isn't done; re-dispatch.

### 2. Search is a SWEEP, not a query
**≥4 angles per topic:** by-technique, by-game/example, by-engine/library-feature, by-problem-symptom. No topic
rests on one search. Name the angles.

### 3. ≥4 SCORED candidates per hard choice
Every load-bearing decision enumerates **≥4 candidates scored on explicit axes** (e.g. fidelity-vs-reference ·
perf · platform/version fit · dev cost), each with a **keep/reject reason**. Stopping at the first that works is
failure. Mark the PICK and say why the rejects lose.

### 4. The ADVERSARIAL COLD-CRITIC loop (loop-until-dry)
After each doc, dispatch a **FRESH** agent told: *no cheerleading — hunt the lazy shortcuts, the missing
modality/source, the technique a great example uses that this omits, the unverified claim, the wrong candidate
ranking. Do your own web research to find what's missing. End with a verdict + evidence.* **Incorporate every
valid finding; re-run until the critic returns nothing material.** After a *big* revision, **re-critic** — a
fix can introduce a new error (this session: round-2 caught a version-specific error introduced while fixing
round 1; a design re-verify caught scope contradictions introduced while fixing the critical flaw).

### 5. VERIFY load-bearing claims yourself (don't trust sub-agents)
Sub-agents are great for breadth and **wrong at the load-bearing altitude often enough to matter.** Before a
claim carries weight, **read the real code / the real doc / the real version yourself** (file:line, the actual
manual page, `ProjectVersion.txt`). This session: self-verification caught an imprecise "post is all-zero"
claim, and **pinning the exact engine version flipped a render recommendation** (a capability existed only in a
newer version than the project runs). **Pin versions/environment explicitly** so the design can't inherit
capabilities you don't have.

### 6. Certainty gate + concrete acceptance bar
Run **certainty-assessment** on the resulting design (MIN-aggregate; no load-bearing row left below Strong
without being named as a spike/user-decision residual). The acceptance bar is **concrete**, never "looks
better": "reproduces reference X's look, per element" / "passes gate Y." Where only an in-engine/in-situ
prototype can resolve a render/behavior question, say so and make the **spike** the gate — a critic can't prove
it, only the tool can.

### 7. Surface owner-taste as QUESTIONS, never guesses
Genuine taste/scope decisions (how-dark, which mood, which trade-off) are **surfaced as questions**, quoting the
owner verbatim where attributing intent. Never launder your inference into their decision. (See the
`dont-launder-guesses` memory.)

## Definition of DONE (countable — no "looks good enough")
- Each research doc: **≥15 deep-read sources + ≥3 studied codebases**, distilled (a source TABLE + checkable
  techniques, not a link dump), with a counterexample/"skip" call where relevant.
- **The cold-critic returned nothing material on its final pass** (loop-until-dry), and big revisions were
  re-critiqued.
- Each design: **≥4 scored candidates per hard choice**; every load-bearing claim cites a real `file:line` /
  doc / version you verified; certainty table has no un-addressed sub-Strong load-bearing row.
- Owner-taste questions surfaced, not guessed.

## Where outputs go (don't invent folders)
- **Working / throwaway research** → `docs/product/investigations/` (the deep-investigate home).
- **Keeper conclusions** graduate into the canonical `docs/product/architecture/architecture_<topic>.md`
  (marked DESIGN/PROPOSED until built + verified). Research records the *evidence*; the architecture doc records
  the *decision*.

## Honest note on enforcement
This skill can't be hook-gated (research isn't a single file edit), so it relies on (a) an unmistakable
`description` that triggers invocation, (b) countable quotas that make a half-search a visible failure, and
(c) the critic loop as the real backstop — a fresh skeptic is the thing that actually catches the shortcut.
When a task says "research" / "look up how X is done" / "how do good games do Y," invoke this FIRST. Scale the
counts to the stakes (a quick check needs less than a shippable-system design), but **never drop the critic
loop** — it is the cheapest way to find the thing you missed.
