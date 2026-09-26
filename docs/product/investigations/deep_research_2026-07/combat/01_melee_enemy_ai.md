# Close-range / melee enemy AI — research findings

*Topic 1 of the 2026-07 combat research. Synthesized from deep-read sources (source table below);
raw agent transcripts in `../_raw_recovered/combat/`. For a 2D top-down, **deterministic,
server-authoritative** sim: a central arbiter is GOOD (that's what our server is); per-frame RNG and
unstable float/iteration order are the enemy.*

## TL;DR — the deterministic-server sweet spot
A **central "stage manager" attack-token layer** (the "Belgian AI" pattern) sitting **above** per-enemy
**FSM/behaviour-tree brains**, whose leaves drive **steering** (seek / arrive / pursue with a hysteresis
stand-off band), with **tick-phase attack timing** (anticipation → active → recovery in integer frames)
and **all randomness seeded from `(tick, entityId)`**. Use Utility AI only for attack/target *selection*
(argmax + a momentum bonus, stable tie-break). Skip GOAP.

## Source table (deep-read)

| Source | Concrete technique | Cost / perf | Determinism fit |
|---|---|---|---|
| **Craig Reynolds, "Steering Behaviors for Autonomous Characters," GDC99** (red3d.com/cwr/steer/gdc99) | seek, flee, arrive (slowing radius), pursue (predict `T=D·c`), evade, obstacle avoidance (cylinder look-ahead), containment, wander, separation/cohesion/alignment; combine by weighted sum / priority / dithering; truncate to `max_force`, Euler-integrate | Very cheap; O(1) per behaviour, O(neighbours) for group | GOOD **except** `wander` (per-frame random displacement) and "prioritized dithering" (random selection) break determinism unless seeded from tick+id. Separation must iterate neighbours in a **stable order** |
| **Reynolds, Boids** (red3d.com/cwr/boids) | 3 rules: separation, alignment, cohesion; local neighbourhood = distance + view-angle cone | O(neighbours) | Deterministic given stable neighbour iteration; no inherent RNG |
| **gdx-ai `Pursue.java`** (real code, Apache-2) | `predictionTime = min(sqrt(sqDist/sqSpeed), maxPredictionTime)`; `future = targetPos + targetVel·predictionTime`; steer toward `future` | O(1) | Deterministic — pure arithmetic |
| **gdx-ai `Arrive.java`** (real code) | `arrivalTolerance`, `decelerationRadius`; inside radius `targetSpeed *= dist/decelRadius`; `timeToTarget` default **0.1 s** | O(1) | Deterministic |
| **BehaviorTree.CPP `reactive_sequence.cpp`** (real code) | Reactive sequence re-ticks from the first child each tick; child SUCCESS→next, FAILURE→fail, RUNNING→return running AND halt other children; asserts if >1 RUNNING | Reactive = re-evaluates prefix each tick (more CPU than a "memory" sequence) | GOOD — deterministic given fixed child order; RUNNING-halts-siblings gives clean reproducible interruption |
| **Michael Dawe, "Beyond the Kung-Fu Circle" (Game AI Pro ch.28)** | **Attack-token / stage-manager ("Belgian AI").** A central manager owns an 8-slot ring around the player + two budgets: **grid capacity** (who may approach) and **attack capacity** (who may strike). Per-creature **grid weight**, per-attack **attack weight**; approve if weight ≤ remaining capacity, deduct on grant, refund on release. Attackers **lock** their slot mid-attack; slots reassigned greedily (closest) each frame; can be **stolen** when the player repositions. Non-slotted creatures stand in front of an unoccupied slot → **emergent flanking with zero peer awareness**. Difficulty = raise the two capacities | Cheap; one central pass over requesters/frame | **EXCELLENT** — pure integer capacity arithmetic, single central arbiter, **no RNG**. Essentially built for a deterministic server. The headline pick |
| **Jeff Orkin, "The AI of F.E.A.R." (GOAP)** | GOAP = A\* over actions (preconditions/effects/costs); a 3-state FSM (GoTo/Animate/UseSmartObject) executes plans; squad coordination is *emergent* (agents don't know each other exists, just share aligned goals); replan on precondition invalidation | Highest — A\* search per replan; F.E.A.R. shipped a bug where rats replanned **every frame** | Deterministic **only if** A\* tie-breaking is stable and costs are integer/fixed-point. Largest nondeterminism surface + most CPU — use sparingly |
| **apoch/curvature, "Utility Theory Crash Course"** (wiki) | Utility AI: score each action = **product of its considerations** (any 0 → action 0); pick top. **Momentum bonus: last-chosen action gets +25% next think** → hysteresis, kills oscillation | O(actions×considerations)/think; throttle think rate | GOOD with **argmax + stable tie-break** (lowest id). "Weighted-random among top-N" is an RNG hazard — avoid or seed. The 25 % momentum is determinism-*friendly* |
| **Dave Mark / IAUS considerations** | consideration = normalized input [0,1] → **response curve** (linear/quadratic/logistic) → score; scores multiplied; a **compensation factor** counters "product shrinks toward 0 as considerations pile up" | Cheap per consideration | Deterministic; watch cross-platform `pow`/`exp` float drift — prefer fixed-point LUTs |
| **GDKeys, "Anatomy of an Attack"** | Every attack = **Anticipation (wind-up) → Active (strike) → Recovery (window of opportunity)**. `anticipation = playerReaction + abilityTrigger + difficultyBuffer` (worked example ≈ **18 frames**). Recovery 1f→10+s = the counter window. Each attack needs a **drastically different** wind-up | Trivial (timers) | **PERFECT** — pure tick counters, fully deterministic |
| **signalsandlight, "Enemy ranged & melee combat"** | Melee approach archetypes: **In-Place / Lunging / Charging**; **motion warping** = procedurally warp translation+rotation during the attack anim to track the target | Cheap | Deterministic (motion warping is a fixed procedural transform) |

## Distilled techniques (with params)

### Movement / pursuit
- **Seek:** `desired = normalize(target−pos)·maxSpeed; steer = desired − vel`.
- **Arrive** (stand-off without overshoot): `decelerationRadius` ≈ 1–2 body radii, `arrivalTolerance`, `timeToTarget ≈ 0.1 s`; inside radius `speed *= dist/decelRadius`.
- **Pursue** (lead the moving player): `T = min(sqrt(dist²/speed²), maxPredictionTime)`; seek `targetPos + targetVel·T`. `maxPredictionTime` ~0.3–1.0 s so distant enemies don't over-lead.
- **Separation** (anti-clump): repulse by `1/dist²`, summed over neighbours **in stable id order**, within a radius + view cone.
- Combine as **weighted sum truncated to `max_force`** (deterministic) — NOT priority-dithering (RNG).

### Group / spacing / encirclement
- **Attack-token stage manager (adopt this):** 8 surround slots, `gridCapacity` + `attackCapacity` budgets, per-creature `gridWeight`, per-attack `attackWeight`; grant if weight ≤ remaining; **lock slot during an attack**, refund on release; reassign nearest-free slot each tick; allow slot-stealing when the player repositions. Scale difficulty by raising the two capacities.
- **Emergent flanking:** park non-attacking enemies in front of their assigned (unoccupied) slot — no peer awareness needed.
- **Kiting / stand-off with a hysteresis band:** approach if `dist > outerBand`, retreat if `dist < innerBand`, else strafe/hold. The band (desiredRange ± 0.5–1 cell) stops boundary jitter.
- **Melee approach archetypes:** In-Place / Lunge / Charge chosen by distance bucket; **motion-warp** the strike to track the target.

### Readability / attack selection
- **Three-phase attack:** Anticipation (**≥ ~15–18 frames / ~0.25–0.6 s**, up to ~3 s for a heavy/unblockable) → Active (few frames, constant direction, clean silhouette) → Recovery (counter window). Anticipation must be **per-attack distinct** in silhouette + SFX.
- **Feints / mix-ups:** play the anticipation, then cancel into a different move — select via a **`(tick, entityId)`-seeded hash**, never `rand()`.
- **Threat / aggro + leashing:** per-enemy integer threat table (damage/heal → threat), target = max threat; `leashRadius` from an anchor → on exceed, drop aggro + return. Integer accumulation = deterministic. (Depth in `03_challenge_and_effectiveness.md`.)

### Architecture axis (cost / best-for / determinism)
- **Pure steering** — cheapest; movement only; deterministic minus wander RNG. The low-level "how to move" layer under everything.
- **FSM / HFSM** — cheap, O(1) transitions; best for a small enemy with few modes (Idle / Chase / Telegraph / Attack / Recover / Flee). Deterministic. **Default for most bugs.**
- **Behaviour Tree** — moderate; reactive nodes re-tick each frame but give clean interruption; deterministic given fixed child order. Best past ~6 states.
- **Utility AI** — moderate; best for "which of many attacks/targets" scoring; deterministic with argmax + stable tie-break + the 25 % momentum bonus; avoid weighted-random.
- **GOAP** — most expensive + largest nondeterminism surface; overkill for melee bugs. Skip.
- **They compose:** FSM/Utility selects a BT subtree; BT leaves run steering; the **attack-token stage manager sits ABOVE all of them** as a central permission layer.

## ≥4 scored candidate approaches for "raise challenge + effectiveness"

Axes: **challenge impact · readability/fairness · dev cost · fits our deterministic influence-event model** (1–5, higher better).

| Candidate | Challenge | Readable/fair | Dev cost | Determinism fit | Verdict |
|---|:--:|:--:|:--:|:--:|---|
| **A. Attack-token stage manager + FSM brains + steering** | 5 | 5 | 3 | 5 | **PICK.** Central arbiter = our server. Caps simultaneous attackers (fair), density stays scary. Integer-only. |
| B. Pure boids swarm, everyone can bite | 3 | 1 | 2 | 3 | REJECT — mobbing is unreadable/unfair; float-sum order is a desync risk. |
| C. Per-enemy Utility AI (no central layer) | 4 | 3 | 4 | 3 | Keep for *selection* only. Alone it lets everyone commit at once and adds RNG/tie-break hazards. |
| D. GOAP squads (F.E.A.R.-style) | 5 | 3 | 5 | 2 | REJECT — huge cost + nondeterminism surface for little gain on small bugs. |
| E. Scripted set-piece attacks (fixed patterns) | 2 | 5 | 2 | 5 | Keep as a *complement* for bosses/nests; too static for the general roster. |

**Why A wins for us:** the server already IS the central authority the stage-manager pattern needs; it turns "N bugs all bite" into a bounded, tunable, fair pressure system with emergent flanking for free, using only integer budgets — trivially deterministic and sync-safe. Layer per-bug FSMs beneath it and Utility scoring for attack choice.

## Anti-patterns (what does NOT work)
- **Everyone attacks at once (mobbing)** — no token/arbiter → unreadable, unfair. Fix: stage-manager attack tokens.
- **Per-frame RNG** in wander, dithering, feint choice, or utility "weighted-random top-N" — breaks cross-client determinism. Fix: seed all randomness from `(tick, entityId)`.
- **No hysteresis** on approach/retreat (or utility with no momentum) → enemies jitter/oscillate at the stand-off boundary. Fix: dead-band + the 25 % momentum bonus.
- **Telegraph too short / instant** (< ~15 frames) → unreadable, feels cheap.
- **Utility multiply without a compensation factor** → decision scores collapse toward 0 as considerations pile up.
- **Argmax / A\* / obstacle-selection without a stable tie-break** → different client picks a different equal-scoring winner → desync.
- **Summing separation/boids over an unstable neighbour order** → float result differs machine-to-machine → desync. Fix: iterate neighbours by id.
- **GOAP replanning every tick regardless of need** (the shipped F.E.A.R. "rats" bug).

## How it maps to our swarm sim (as influence events)
Our bugs move via `SWARM_SET_TARGET` legs; the authority relays outcomes via `BUG_REMOVED`; sim reads must be zone-wide frontier-gated events; per-bug HP is display-only. Fit:
- The **stage manager runs on the authority** (server-side) — it already decides swarm legs. It grants a small integer pool of **bite tokens** per player; only token-holders emit a damaging lunge. This is a server-only decision whose *observable output* (a hit / a telegraphed lunge leg) rides the ledger — same shape as the existing predation strike (authority-detect → relay).
- **Attack phases** become authored integer tick counts on the leg (`windupTicks / activeTicks / recoveryTicks`), so every client renders the same telegraph at the same tick.
- **Steering (seek/arrive/pursue)** computes the *target* of the next `SWARM_SET_TARGET` leg on the authority in fixed-point; clients just replay the leg. Determinism landmine: any separation/boids sum must be fixed-point and iterate bug ids in sorted order.
- **Threat/aggro** is an integer accumulator per (swarm, target) on the server; it picks which leg target (player vs. lure vs. crop) — see `03`.

## Open questions (owner taste — not guessed)
1. **How much bite at once?** The token-pool size is the core difficulty dial (1 = one attacker at a time, cozy; 2–3 = tense). What should the default feel like, and should it scale with a difficulty setting?
2. **Telegraph length vs. cozy pace** — a ~0.5 s wind-up is fair-but-slow; do you want combat reads that leisurely, or snappier (harder)?
3. **Do bugs get real per-bug HP** (so the player "fights" them) or stay one-hit swarm units? (Affects whether the whole three-phase/recovery-punish loop is even visible.)
