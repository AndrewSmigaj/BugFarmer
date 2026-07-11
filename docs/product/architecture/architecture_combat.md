# Combat AI & challenge — design

**STATUS: DESIGN / PROPOSED (not built).** The decided skeleton + the recommended layers around it. Evidence
and alternatives live in the research: [`../investigations/deep_research_2026-07/combat/`](../investigations/deep_research_2026-07/combat/)
(01 melee AI · 02 swarm AI · 03 challenge/effectiveness · 04 player combat & bosses). Runs inside the
deterministic swarm sim — see [`architecture_swarm_sync.md`](architecture_swarm_sync.md) §0.

## The decided skeleton (owner-adopted 2026-07-11)
Three primitives, layered:

1. **Steering** — the low-level "how a bug moves." Simple vector math per bug: `seek` (toward target), `arrive`
   (slow into range, no overshoot), `pursue` (lead a moving player), `separation` (don't clump). Output = the
   *target* of the swarm's next movement leg. Cheap; deterministic in fixed-point with sorted-id neighbour sums.
2. **FSM brains** — each bug/swarm is in exactly one state: `Idle → Chase → Wind-up → Attack → Recover → Flee`,
   with data-driven transitions (see player → Chase; in range → Wind-up; hit → Flee). O(1), deterministic.
3. **Attack-token stage manager** — a central server-side bouncer per player: a small integer pool of **bite
   tokens** (default 1–2) + a ring of surround **slots**. Only a token-holder may execute a damaging lunge;
   the other bugs still crowd/menace (scary) but can't all bite at once (fair). Slots assign nearest-free →
   emergent flanking with zero peer awareness. Difficulty = raise the token/slot budgets. Pure integer
   bookkeeping on the server; emits **no extra network bytes** — only its *outcomes* (a telegraph leg, a strike)
   travel.

These compose: the **stage manager** sits above per-bug **FSM brains** whose Attack/Chase states drive
**steering**, which sets the next `SWARM_SET_TARGET` leg.

## Recommended alongside them — the layers that make the three actually work
*(My recommendation, not yet owner-confirmed. The first group is effectively inseparable from the skeleton —
without it, "smarter enemies" just means "more unavoidable damage," the anti-pattern every source warns of.)*

### Core bundle — strongly recommend (adopt with the three)
- **Three-phase attack timing** (anticipation → active → recovery, authored **integer ticks**). This is the
  *fairness contract*: a token-holder's bite has a visible **wind-up (≥ ~15 ticks)** you can react to, and a
  **recovery** window that's the player's free-hit. Without it the attack tokens are just unavoidable hits.
  Deterministic (tick counters), trivial to sync. **The tokens and the timing are one feature.**
- **Player dodge + i-frames** — the **load-bearing prerequisite**. Every enemy telegraph is meant to be
  answered by *something*; today the player has weapon swings but **no dodge/roll/block/parry** at all. A
  dodge/roll with front-loaded invulnerability (Gungeon-shape: ~0.5–0.7 s, i-frames on the first half) is the
  cheapest, most cozy-forgiving defensive verb and the one to add **first**. Netcode: client-predicts the move;
  the server owns an integer `invulnStart/EndTick` window it checks damage against. (Details: research doc 04.)
- **Threat table + aggro radius + leash** — target arbitration + the escape valve. Integer threat per
  (swarm, target); lures/torches/scarecrows are threat magnets that **peel** part of the swarm off the player;
  a **leash radius** guarantees retreat always works (a cozy game must let you walk away). Turns a blind
  pile-on into a placement puzzle the player out-plays.

### Pacing layer — recommend
- **Threat director** (L4D-style): a per-player intensity valve — rises with bites/nearby deaths, decays only
  when disengaged; Build-Up → Sustain(3–5 s) → Fade → **Relax(30–45 s)**. Varies **frequency, not damage**, so
  threat never curdles into fatigue — the key to staying *cozy* while adding danger. Reinforcements arrive from
  off-screen edges (directional pressure, not a teleport pile-on).

### Cheap steering polish — recommend
- **Sticky priority targeting + acquisition delay** — a bug keeps its target until it dies/leaves range/a
  higher-priority one appears. Fixes target *flicker* (both feel AND a determinism hazard on near-equal scores).
- **Boids separation** in the steering sum — the anti-clump force so a swarm reads as a spread cloud, not one dot.

### Deferred (phase 2, not now)
- **Utility AI for attack/target *selection*** (score considerations, argmax + momentum) — nice once a bug has
  several attacks to choose between; the FSM is enough for a first pass. Determinism-safe if argmax + stable
  tie-break (no weighted-random).
- **Enemy role/variety expansion** (spitter / broodmother / tank / latcher — function-over-stats) — this is a
  *content roadmap* (new species + new player counters), an owner scope call, not an AI-architecture primitive.

### Rejected (for now)
- **GOAP** — huge cost + biggest nondeterminism surface for tiny melee bugs. No.
- **Flow-field-tile pathfinding** (SupCom2-style) — overkill; our `SWARM_SET_TARGET` legs already give shared,
  instant, coordinated movement. Revisit only if we ever need thousands of independently-pathing bugs through
  complex obstacle mazes.

## Determinism & network model (why the "central arbiter" is cheap)
- The stage manager, FSMs, and steering are **server CPU**, run each tick as **integer/fixed-point** math with
  sorted iteration + `(tick, entityId)`-seeded randomness (never `rand()`). No floats in sim sums.
- They put bytes on the wire **only when a decision changes something** — a new **leg** (`SWARM_SET_TARGET`), a
  **telegraph**, a **strike** (`BUG_REMOVED`). Movement is sent as legs the client replays deterministically,
  **never per-bug-per-frame positions.** Verified against `match.go`: the only strictly-every-tick message is a
  tiny **frontier heartbeat** (OpCode 78); the swarm roster (OpCode 20) is one *(x,y,count,radius)* per swarm on
  change; influence events batch per tick. Traffic scales with **decision rate, not bug-count × framerate** —
  low single-digit KB/s even in a busy fight. (`Perf.AddRosterBytes`/`AddInfluenceBytes` already measure the
  real totals — a profiled combat run prints exact figures.)
- New sim-reads (aggro, telegraph windows, dodge i-frames) must ride the frontier-gated ledger per the
  `frontier-sync` recipe — authority decides, relays the observable via events; never a view-scoped read.

## Recommended build order
1. **Player dodge + i-frames** (the prerequisite — nothing else is fair without it).
2. **Three-phase attack timing** on one enemy in `feel_test` + the **attack-token pool** (1–2) → playtest the
   feel. This is the smallest slice that proves the whole loop.
3. **Threat table + aggro radius + leash** (escape + lures).
4. **FSM brains + steering (seek/arrive/pursue + separation + sticky targeting)** generalised across bugs.
5. **Threat director** pacing valve.
6. *(later)* Utility-AI attack selection; enemy-role/species expansion.

## Open questions (owner taste/scope — surfaced, not decided)
1. **How cozy vs. how threatening?** The token-pool size + telegraph length are the master dials. Stardew-mines-
   light, or genuinely dangerous at night / in caves?
2. **Defensive verb:** dodge-roll (recommended) as the one verb, or also **block / parry** later for tell-reading?
3. **Is threat zoned/opt-in?** Safe farm by day, danger in the wilds/caves/night — so players choose their
   challenge (Don't-Starve-style)? Or ambient everywhere?
4. **How far to expand the bestiary for combat** (spitter/broodmother/tank/latcher roles) vs. keep bugs mostly
   ambient? This sets how much of the "roles" content we build.
5. **Difficulty settings:** one global slider over these dials, or split (how-many-bugs vs. how-hard-they-hit)?
