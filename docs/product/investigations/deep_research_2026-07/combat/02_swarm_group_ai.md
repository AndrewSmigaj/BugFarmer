# Swarm / group AI — coordinated, threatening, deterministic movement

*Topic 1 of the 2026-07 combat research. How groups of small creatures move as a coordinated,
alive, threatening whole — applied to BugFarmer's swarms. Synthesized from a fully-read authoritative
dev source (SupCom2 flow-field tiles) + three community technical writeups. Raw transcript:
`../_raw_recovered/combat/a497beed450fe1d50.md` (near-complete; this doc adds the sim mapping + scoring).*

## The core lesson
**Per-unit A\* does not scale and produces chaos** (units collide, stall, and need babysitting). Real
RTS moved to **field-based movement + a flocking layer + push-not-repath**. For BugFarmer this maps
cleanly: our swarms already move as **legs** (`SWARM_SET_TARGET`), not per-bug pathfinding — so we get
the "shared field" benefit for free; what we're missing is the **flocking/spacing + coordination + sticky
targeting** layer that makes a group read as intelligent rather than a single dot or a random cloud.

## Source table (tiers: [DEV]=shipped-dev/published chapter; [COMMUNITY]=wiki/hobby reconstruction)

| Source | Technique | Fit for a deterministic fixed-point server sim |
|---|---|---|
| **[DEV] Elijah Emerson, "Crowd Pathfinding & Steering Using Flow Field Tiles," Game AI Pro Ch.23 (SupCom2)** — *fully read* | Replace per-unit paths with **shared flow fields**: world = 10×10 sectors + portal graph; per-sector **cost / integration / flow** fields; hierarchical portal-A\* + **"merging" A\*** so units selected together share fields and arrive together; **Eikonal** wave-front integration + a **line-of-sight pass** (near-goal agents steer straight, skip the field); reference-counted **flow-field cache** keyed by portal window; cap tiles integrated/tick | Flow fields are deterministic if built in integer/fixed-point with a fixed cell-visit order. **BUT** full flow-field infra is likely overkill for us — our legs already are the "field". Borrow the *ideas* (shared target, LOS-straight-line, capped work/tick), not the whole system |
| **[COMMUNITY] howtorts "Continuum Crowds" + "Basic Flow Fields"** — *fully read* | Integration field = Dijkstra/BFS distance-to-goal; per cell pick lowest neighbour → direction; **shared field** removes per-unit pathfinding; **bilinear-interpolate** the 4 nearest cells to smooth; Continuum adds a **density grid** + **counterflow cost** so congestion/avoidance is **emergent** ("units avoid high-density + counterflow without explicit steering") | Density-field counterflow is a lovely emergent-spacing idea but "full recompute every timestep" is heavy; a cheap per-cell integer bug-count that biases leg targets could approximate it |
| **[COMMUNITY] "Group Movement" boids reimpl.** — *fully read* | Reynolds **separation / cohesion / alignment**: final vel = path-follow + separation + cohesion (+alignment); **three radii** (vision/body/collision); pre-emptive obstacle avoidance (zero the into-wall velocity component); ~**0.04 ms/entity**, 100+ @60fps; needs spatial partitioning to scale | **Separation** is the key anti-clump force. Determinism: **must sum neighbour contributions in sorted bug-id order** and in fixed-point, or the float result differs across clients → desync |
| **[COMMUNITY] SC2 targeting (Liquipedia et al.)** — *search summary* | **Acquisition range** (default max(5, weaponRange)); **target stickiness** — keep a target until it dies / leaves range / a higher-priority one appears → prevents per-frame flicker; **acquisition delay on switch** naturally **spreads fire**; **overkill prevention** | Stickiness isn't just feel — **target flicker is a determinism hazard** (tiny float differences flip the target). A sticky, integer-priority target with hysteresis is both nicer AND more sync-stable |
| **[COMMUNITY] SC1 "magic box" formation** — *search summary* | A selected group holds **formation while all members are within radius R** ("the magic box"); a member outside → the group **collapses/stacks** to a point. Distance-thresholded, dead cheap | A clean, cheap, deterministic cohesion rule (integer radius check) for "tight formation vs. collapse-to-point" swarm shapes |
| **[DEV] SupCom2 push layer** | On collision, units **push each other + slide along walls via physics**; heavier/priority units displace lighter; **collision resolved by displacement, NOT repathing** (repath-on-collision is a compounding failure) | Push is a client-cosmetic nicety over a server-authoritative position; keep the authority's positions the truth, let clients render soft separation |

## What makes a group read as coordinated (the checklist)
1. **Shared target/field**, not independent paths → units funnel together and arrive together. *(We have this: one leg per swarm.)*
2. **Instant response** to a new target — field/leg movement reacts immediately, no per-unit A\* stall.
3. **Move by the most-restrictive member** so fast units don't race ahead of a mixed group.
4. **Push, not repath**, on collision, with priority displacement.
5. **Boids separation/alignment/cohesion** for organic spacing + shared heading.
6. **Settle-down**: lower avoidance priority + "stop if the destination is crowded" so an arrived group doesn't jitter forever.
7. **Sticky, priority-weighted targeting with an acquisition delay** so the group focuses sensibly and fire spreads instead of dog-piling one thing.

## ≥4 scored candidates for "coordinated, threatening, deterministic swarm movement/attack"
Axes: **threat/aliveness · determinism fit · perf at N bugs · dev cost** (1–5).

| Candidate | Threat/alive | Determinism | Perf | Dev cost | Verdict |
|---|:--:|:--:|:--:|:--:|---|
| **A. Keep leg-based movement; ADD a fixed-point boids-separation + cohesion pass (sorted-id, capped neighbours) on top** | 4 | 4 | 4 | 3 | **PICK #1.** Directly fixes "swarm clumps into one dot / feels random" with the least new machinery; rides our existing legs. |
| **B. Sticky integer-priority targeting + acquisition delay for which target a swarm's leg seeks** | 4 | 5 | 5 | 2 | **PICK #2.** Cheap, removes target-flicker (feel AND sync), enables fire-spread across multiple crops/players/lures. |
| **C. "Magic-box" cohesion states (tight formation ↔ collapse-to-point) for encirclement/pulse attacks** | 4 | 5 | 5 | 2 | **PICK #3 (encirclement).** A cheap integer rule that gives readable "massing then striking" shapes. |
| D. Full SupCom2 flow-field-tile system (portal graph, Eikonal, cache) | 5 | 3 | 3 | 5 | REJECT for now — overkill; our legs already provide shared-field movement. Revisit only if we need thousands of independently-pathing bugs around complex obstacles. |
| E. Continuum-Crowds density/counterflow fields | 4 | 3 | 2 | 5 | REJECT — heavy per-tick recompute; approximate its *good idea* (avoid high-density cells) with a cheap integer bug-count bias in B/C instead. |

## How it maps to our swarm sim (as influence events / server logic)
- Movement stays **`SWARM_SET_TARGET` legs** computed on the authority. The **boids-separation/cohesion pass (A)** runs server-side in **fixed-point**, iterating bug ids in **sorted order**, to nudge per-bug offsets within the swarm's leg — output is deterministic and clients just replay the leg. *(Landmine: `FixedPoint operator* = a*b/1000`; any `1/dist²` must be fixed-point; never raw map iteration.)*
- **Targeting (B)** is an integer-priority pick on the authority for the swarm's next leg target (player vs. crop vs. lure), with **stickiness + an acquisition-delay counter** so it can't flicker. This is the same class as the existing threat/target logic; it changes *which* leg is emitted, nothing the client reads directly.
- **Formation/encirclement (C)** is an integer radius-state on the swarm that shapes the leg targets of its members (spread around the player, then collapse for a pulse "attack"). Pulses can carry the attack-token/telegraph phases from `01`/`03`.
- **Push** is **cosmetic-only on the client** (soft separation for rendering); the authority's positions remain the single truth — do NOT let client push feed back into the sim (that's the classic view-scoped-read desync).

## Determinism landmines (must-hold)
- **Fixed-point, not float**, for every steering sum. Cross-platform `float`/`pow` drift = desync.
- **Stable iteration order** (sorted bug ids / `sortedStringKeys`) for any neighbour sum — the #1 boids desync.
- **No per-frame RNG** in wander/target-tiebreak — seed from `(tick, swarmId, bugId)`.
- **Target stickiness with hysteresis** — argmax target flicker on near-equal scores is both bad feel and a desync surface; require a margin to switch (the WoW 10 %/30 % idea).
- Zone-wide reads only (the one invariant): a swarm's coordination must read zone-complete data, never view-scoped chunks.

## Open questions (owner taste — not guessed)
1. **How tight should swarms read** — a loose organic cloud, or crisp formations that visibly "mass and strike"? (Sets how much of B/C we build.)
2. **Do swarms actively encircle/pressure the player and farms**, or mostly mill about ambiently and only react when provoked? (The ecology-tuning notes say bugs *should* spread and eventually pressure farms — how aggressive?)
3. **Is any of the heavier flow-field infra ever wanted** (e.g. for a big cave "hunt the player through corridors" set-piece), or do we commit to leg-based forever?
