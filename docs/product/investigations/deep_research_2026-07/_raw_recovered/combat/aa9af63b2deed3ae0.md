I'll research this by fanning out across the four required angles, with each sub-agent doing deep web-fetches and returning cited notes with a determinism lens. Then I'll synthesize the final source table and technique list myself.

---

I've launched all four research agents. They're running in the background. I'll wait for them to complete and then synthesize.

---

API Error: Server is temporarily limiting requests (not your usage limit) · Rate limited

---

All four sub-agents were killed by transient rate-limiting before doing real work (token counts 36-88 — essentially empty). I'll do the research directly myself. Let me load the web tools.

---

Now I'll do the research directly, fetching sources in controlled batches. Starting with the foundational steering and architecture sources.

---

The peer message appears to be a confused/stale sub-agent — I am the main agent and haven't produced the synthesis yet, so there is nothing lost. I'll disregard it and continue my own research.

The GOAP URL 404'd. Let me find working URLs for the remaining priority sources and the open-source code.

---

Excellent finds — "Beyond the Kung-Fu Circle" is exactly the attack-token chapter. Let me fetch that, the F.E.A.R./GOAP article, and real source code from gdx-ai.

---

The Kung-Fu Circle PDF saved locally — I'll read it directly (Read handles PDFs). The other two fetches hit a transient classifier outage; I'll retry them.

---

Got the full Kung-Fu Circle / Belgian AI chapter — the exact attack-token pattern, centralized and RNG-free. Now the remaining sources: GOAP article (retry), Pursue.java code (retry), a Behavior Tree library's real source, and utility AI.

---

Strong material. Now the utility-AI internals (tie-breaking matters for determinism), and combat readability/telegraph numbers.

---

Good telegraph numbers. Let me deep-read the GDKeys attack-anatomy piece for concrete phase params, and the ranged/melee enemy combat breakdown for kiting/spacing.

---

I have deep-read 10+ sources across all four angles plus three real open-source source files. Here is the synthesis.

---

# Close-Range / Melee Enemy AI — Research Findings

For a 2D top-down, deterministic, server-authoritative sim. Determinism lens throughout: a **central arbiter is GOOD** for us (it's what a server is); **per-frame RNG and unstable float/iteration order are the enemy**.

## SOURCE TABLE

| Source (title + URL) | Concrete technique | Cost / perf | Determinism-friendliness |
|---|---|---|---|
| **Craig Reynolds, "Steering Behaviors for Autonomous Characters," GDC99** — http://www.red3d.com/cwr/steer/gdc99/ | seek, flee, arrive (slowing radius), pursue (predict T=D·c), evade, obstacle avoidance (cylinder look-ahead), containment, wander, separation/cohesion/alignment; combine by weighted sum / priority / dithering; forces truncated to max_force, Euler-integrated | Very cheap; O(1) per behavior, O(neighbors) for group behaviors (needs spatial hash) | GOOD except two hazards: **wander uses per-frame random displacement** and **"prioritized dithering" uses random selection** — both break determinism unless seeded from tick+id. Pure seek/arrive/pursue = deterministic if float summation order is fixed. Separation must iterate neighbors in a **stable order** or the summed float differs across machines |
| **Reynolds, Boids** — http://www.red3d.com/cwr/boids/ | 3 rules: separation, alignment, cohesion; local neighborhood = distance + view-angle cone; "9 numeric params" (weight+distance+angle ×3) | O(neighbors) | Deterministic given stable neighbor iteration; no inherent RNG |
| **gdx-ai `Pursue.java`** (real code) — https://github.com/libgdx/gdx-ai `.../steer/behaviors/Pursue.java` | `predictionTime = min(sqrt(sqDist/sqSpeed), maxPredictionTime)`; `future = targetPos + targetVel·predictionTime`; steer = normalize(future − pos)·maxAccel | O(1) | Deterministic — pure arithmetic, no RNG |
| **gdx-ai `Arrive.java`** (real code) — https://github.com/libgdx/gdx-ai `.../steer/behaviors/Arrive.java` | `arrivalTolerance`, `decelerationRadius`; inside radius `targetSpeed *= dist/decelRadius`; accel = `(targetVel − vel)/timeToTarget` clamped to maxAccel; `timeToTarget` default **0.1s** | O(1) | Deterministic |
| **BehaviorTree.CPP `reactive_sequence.cpp`** (real code) — https://github.com/BehaviorTree/BehaviorTree.CPP | Reactive sequence re-ticks children **from the first every tick**; child SUCCESS→next, FAILURE→return fail, RUNNING→return running AND `haltChild(i)` all non-running siblings; asserts if >1 child RUNNING | Reactive = re-evaluates whole prefix each tick (more CPU than a "memory" sequence that resumes) | GOOD — deterministic given fixed child order; no RNG unless you add a random node. RUNNING-halts-siblings gives clean, reproducible interruption |
| **Michael Dawe, "Beyond the Kung-Fu Circle" (Game AI Pro, ch.28)** — http://www.gameaipro.com/GameAIPro/GameAIPro_Chapter28_Beyond_the_Kung-Fu_Circle_A_Flexible_System_for_Managing_NPC_Attacks.pdf | **Attack-token pattern ("Belgian AI").** Central *stage manager* owns an 8-slot world-space grid around the player + two budgets: **grid capacity** (who may approach) and **attack capacity** (who may strike). Each creature has a **grid weight**; each attack an **attack weight**. Approve if weight ≤ remaining capacity; deduct on grant, refund on release. Inner "attack" circle vs outer "approach" circle. Non-slotted creatures stand in front of an unoccupied slot → **emergent flanking with zero peer awareness**. Attackers **lock** their slot mid-attack; slots reassigned greedily (closest) every frame; can **steal** a slot when player rolls toward a different enemy. Per-attack cooldowns: individual / creature-wide / global. Difficulty = just raise the two capacities | Cheap; one central pass over requesters per frame; greedy closest-slot assignment | **EXCELLENT.** Pure integer capacity arithmetic, a single central arbiter, **no RNG** — this is essentially built for a deterministic server. The headline recommendation |
| **Jeff Orkin GOAP / "Three States and a Plan: The AI of F.E.A.R."** — https://www.gamedeveloper.com/design/building-the-ai-of-f-e-a-r-with-goal-oriented-action-planning | GOAP = **A\*** over ~120 actions (preconditions/effects/costs) to reach a goal state; only a **3-state FSM** (GoTo / Animate / UseSmartObject) executes plans; plans typically 1–4 actions; replan on precondition invalidation. Squad "coordination" is emergent — **agents don't know each other exists**, they just get aligned goals | Highest of the architectures — A* search per replan; F.E.A.R. shipped a bug where rats **replanned every frame** regardless of need | Deterministic **only if** A* open-set tie-breaking is stable and costs are integer/fixed-point. No inherent RNG. But per-agent search is the most nondeterminism *surface* and the most CPU — use sparingly |
| **apoch/curvature, "Utility Theory Crash Course"** — https://github.com/apoch/curvature/wiki/Utility-Theory-Crash-Course | Utility AI: each action scored = **product of its considerations** (any 0 → whole action 0); pick top score (or weighted-random among top-N). **Momentum bonus: last-chosen action gets +25% next think** → hysteresis, kills oscillation | O(actions × considerations) per think; throttle think rate | GOOD if you pick **argmax with a stable tie-break** (e.g. lowest id). **"Weighted-random among top-5" is an RNG hazard** — avoid or seed from tick. The 25% momentum bonus is a determinism-*friendly* anti-oscillation trick |
| **IAUS considerations (Dave Mark), via Wikipedia/IAUS docs** — https://en.wikipedia.org/wiki/Utility_system + search synthesis | Consideration = normalized input [0,1] → **response curve** (linear, quadratic/polynomial, logistic/sigmoid, logit) with params slope/exponent/x-shift/y-shift → score; scores multiplied; a **compensation factor** counters the "product shrinks toward 0 as you add considerations" problem | Cheap per consideration | Deterministic; curves are pure functions. Watch float determinism on `pow`/`exp` across platforms — prefer fixed-point LUTs if cross-platform float drift is a risk |
| **GDKeys, "Keys to Combat Design: Anatomy of an Attack"** — https://gdkeys.com/keys-to-combat-design-1-anatomy-of-an-attack/ | Every attack = **Anticipation (windup) → Active (strike) → Recovery (window of opportunity)**. `anticipation = playerReaction + abilityTriggerTime + difficultyBuffer`; worked example ≈ **18 frames minimum** (8fr reaction + 10fr block). Active = few frames, constant speed/direction, clean geometry + motion blur/trail. Recovery 1 frame → 10+s = the counter window | Trivial (timers) | **PERFECT** — pure tick counters, fully deterministic and syncs trivially |
| **Enemy telegraphing (Game Developer + note.com + chaoticstupid), search synthesis** — https://www.gamedeveloper.com/design/enemy-attacks-and-telegraphing | Avg player needs **>0.3s** to perceive+decide+press; unblockable/big moves may need up to **3s** telegraphs; telegraph = animation + SFX + VO + VFX combined; each attack's anticipation must be **visually distinct** (silhouette) | Trivial | Deterministic (timing/animation state) |
| **signalsandlight, "How does enemy ranged and melee combat work?"** — https://signalsandlight.substack.com/p/how-does-enemy-ranged-and-melee-combat | Melee approach archetypes: **In-Place / Lunging / Charging**; **motion warping** = procedurally warp translation+rotation during the attack anim to track the target; ranged enemies take fixed "ledges" for predictable attack origins | Cheap | Deterministic (motion warping is a fixed procedural transform) |

## DISTILLED CHECKABLE TECHNIQUES (with params)

**Movement / pursuit**
- **Seek**: `desired = normalize(target−pos)·maxSpeed; steer = desired − vel`.
- **Arrive** (standoff/approach without overshoot): `decelerationRadius` (≈ 1–2 body radii), `arrivalTolerance`, `timeToTarget ≈ 0.1s`; inside radius `speed *= dist/decelRadius`.
- **Pursue** (lead the moving player): `T = min(sqrt(dist²/speed²), maxPredictionTime)`; seek `targetPos + targetVel·T`. Set `maxPredictionTime` ~0.3–1.0s so distant enemies don't over-lead.
- **Separation** (anti-clump): repulse by `1/dist²`, summed over neighbors **in stable id order**, within a neighborhood radius + view cone.
- **Obstacle avoidance**: cylinder look-ahead scaled by speed; steer = negate lateral projection of the nearest-intersection obstacle; **stable tie-break on "most threatening."**
- Combine as **weighted sum truncated to `max_force`** (deterministic) — NOT priority-dithering (RNG).

**Group / spacing / encirclement**
- **Attack-token stage manager** (adopt this): N surround slots (8), `gridCapacity` + `attackCapacity` budgets, per-creature `gridWeight`, per-attack `attackWeight`; grant if weight ≤ remaining; **lock slot during an attack**, refund on release; reassign nearest-free slot each tick; allow slot-stealing when the player repositions. Scale difficulty by raising the two capacities.
- **Emergent flanking**: park non-attacking enemies in front of their assigned (unoccupied) slot — no peer awareness needed.
- **Kiting / standoff with a hysteresis band**: approach if `dist > outerBand`, retreat if `dist < innerBand`, else strafe/hold. The band (e.g. desiredRange ± 0.5–1 cell) is what stops boundary jitter/oscillation.
- **Melee approach archetypes**: In-Place / Lunge / Charge, chosen by distance bucket; **motion-warp** the strike anim to track the target.

**Readability / attack selection**
- **Three-phase attack**: Anticipation (**≥18 frames / ~0.6s**, up to **3s** for heavy/unblockable) → Active (few frames, constant direction, clean silhouette) → Recovery (counter window). Anticipation must be per-attack-distinct in silhouette + SFX.
- **Feints/mix-ups**: play the anticipation, then cancel into a different move — implement selection via **tick+entityId-seeded hash**, never `rand()`, so all clients agree.
- **Threat/aggro + leashing**: per-enemy integer threat table (damage/heal → threat), target = max threat; `leashRadius` from anchor → on exceed, drop aggro + regen + return. Integer accumulation = deterministic.

**Architecture axis (cost / best-for / determinism)**
- **Pure steering** — cheapest; movement only; deterministic minus wander RNG. Use for the low-level "how to move" layer under everything.
- **FSM/HFSM** — cheap, O(1) transitions; best for a small enemy with few modes (Idle/Chase/Telegraph/Attack/Recover/Flee). Deterministic. **Default for most 2D enemies.**
- **Behavior Tree** — moderate; reactive nodes re-tick each frame (more CPU) but give clean interruption; deterministic given fixed child order. Best when behavior grows past ~6 states.
- **Utility AI** — moderate (actions×considerations); best for "which of many attacks/targets" scoring; deterministic with argmax + stable tie-break + the **25% momentum bonus** for hysteresis; avoid weighted-random selection.
- **GOAP** — most expensive (A* per replan) and largest nondeterminism surface; overkill for melee bugs. Skip unless enemies need genuine multi-step improvisation.
- **They compose**: FSM- or Utility-selects-BT-subtree; BT leaves run steering; the **attack-token stage manager sits ABOVE all of them** as a central permission layer (orthogonal to whatever each enemy's brain is).

## ANTI-PATTERNS (what does NOT work)

- **Everyone attacks at once (mobbing)** — no token/arbiter → unreadable, unfair. Fix: stage-manager attack tokens.
- **Per-frame RNG** in wander, prioritized-dithering, feint choice, or utility "weighted-random top-N" — breaks cross-client determinism. Fix: seed all randomness from `(tick, entityId)`.
- **No hysteresis** on approach/retreat (or utility with no momentum) → enemies **jitter/oscillate** at the standoff boundary. Fix: dead-band + the 25% momentum bonus.
- **Telegraph too short / instant** (< ~18 frames) → unreadable, feels cheap/unfair.
- **Utility multiply without a compensation factor** → decision scores collapse toward 0 as considerations pile up.
- **Utility argmax / A\* / obstacle-selection without a stable tie-break** → different client picks a different equal-scoring winner → desync.
- **Summing separation/boids over an unstable neighbor order** → float result differs machine-to-machine → desync. Fix: iterate neighbors by id.
- **GOAP replanning every tick regardless of need** (the shipped F.E.A.R. "rats" bug) → wasted CPU + more nondeterminism surface.
- **Cohesion vs separation weights unbalanced** → clumping (collapse) or explosion.
- **Static ranged enemies / no motion-warp on melee** → dull ranged, whiffing melee.

## OPEN-SOURCE CODE STUDIED
- **gdx-ai** (Apache-2, Java): `Pursue.java` (prediction-time formula) and `Arrive.java` (deceleration-radius arrive) — cited above with the exact formulas.
- **BehaviorTree.CPP** (C++): `reactive_sequence.cpp` — confirmed the RUNNING-halts-siblings, re-tick-from-first reactive semantics and the single-RUNNING-child invariant.

**Bottom line for the design doc:** the deterministic-server sweet spot is a **central "stage manager" attack-token layer (Belgian AI)** on top of **per-enemy FSM/BT brains** whose leaves drive **steering (seek/arrive/pursue with a hysteresis standoff band)**, with **tick-phase attack timing (anticipation/active/recovery)** and **all randomness seeded from tick+id**. Save Utility AI for attack/target selection (argmax + momentum, stable tie-break) and skip GOAP.