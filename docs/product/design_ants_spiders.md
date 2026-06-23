# Design — Ants & Spiders (two new creature systems)

**Status: DESIGNED, NOT BUILT (set aside 2026-06-23).** This is the durable record of an approved design
to add two new bug-species families to the living-ecosystem engine, plus a small rotten-fruit decay fix.
Produced via codebase research (execution-model / reusable-systems / determinism-wiring), game research
(Empires of the Undergrowth, SimAnt, Grounded, ACO/stigmergy), a per-element certainty assessment, two lens
passes, and a "what did I miss" reflection. All load-bearing reuse claims were verified against real code.
Bar: **fun and legible first**, deterministic-system-correct, and reuse-dominant.

---

## The determinism foundation (the lever for the whole design)
The sim is **hybrid** (resolved against code; `architecture_swarm_sync §1.1` was stale on this):
- **SERVER (Nakama Go, `match.go` swarm loop + handlers)** runs the swarm-**center** AI each tick — Think,
  `FindNearbyFood`, movement legs, population (merge/split/spawn/reproduce), lifecycle, nests, broods — and
  **emits the influence ledger** (`SWARM_SET_TARGET`, `SWARM_SPAWNED`, `BUG_REMOVED`, `SWARM_REPRODUCED`,
  `OCCUPANT_BLOCKS_BUGS`, `ITEM_ROTTED`/`FOOD_CONSUMED`). It has **no per-bug positions — only centers**.
- **CLIENTS (C#)** deterministically compute **per-bug positions** (scatter around the center, which marches
  along server legs) from `(worldSeed, swarmId, bugId, tick)`; `ComputeStateHash` = per-bug pos/vel.
- **AUTHORITY CLIENT** only detects per-bug **predation strikes** (needs individual positions) → reports →
  server relays `BUG_REMOVED`.

**The lever:** anything that only changes *which leg the server emits* can be **server-only soft state** —
**no new ledger event, no hashing, no client code** — because its only observable output is the existing
`SWARM_SET_TARGET` leg every client already replays (same class as `FindNearbyFood`). Its only obligation is
server determinism: `state.Rng` + `sortedStringKeys` iteration. **Ant trails/colony-memory live here.** New
*client-read* state is needed only for things the per-bug client sim must see — and webs reuse the
already-ledgered-and-hashed `OCCUPANT_BLOCKS_BUGS`.

---

## Step 0 — Rotten-fruit decay fix (bound the pile; quick, gated)
`processGroundItemDecay` is O(all items)/tick and item count climbs because rotten fruit
(`rottenFruitDecaySeconds = 5040s = 6 game-days`, `handlers_farming.go:29`) is produced by trees faster than
flies eat it → a 6-day-deep pile. **Fix:** lower `rottenFruitDecaySeconds` (data-driven from the decay-curve,
target a ~1–2 game-day plateau) AND add a cheap **per-zone standing-count cap** (a new drop past the cap
expires the oldest → bounded regardless of consumption). Keep it a tuning constant in `ecology_tuning.json`
where possible. **Verify:** re-profile (`run_config 00_baseline`) → `decay` µs/day flattens; bug_lab chart →
flies don't starve. Synergy: **ants eating carrion** (below) is a living second answer to "too many dead
things on the ground."

---

## ANTS — a foraging colony (suggestions, not orders)
Design philosophy (Empires of the Undergrowth): you don't order individual ants; the colony emits suggestions
and a living trail emerges. We get the FEEL with cheap heuristics — **no per-cell ACO grid**.

### Entities (data: `species.json` + `occupants.json`)
- **`ant_hill`** (occupant) — colony base. Reuses **`NestState`** (`nests.go`): houses the queen, banks
  provisioned food as `Brood`, founds daughter hills when rich (existing nest-split, `nests.go:311-322`).
- **`ant_queen`** — stationary at the hill; provisioned brood → eggs via **`BroodState`** (`brood.go`) →
  hatches workers/scouts (`SWARM_REPRODUCED`). Pure reuse of the egg→hatch nursery.
- **`ant_scout`** — small fast swarm/individual; wanders widely; passing carrion, **registers the site** in
  colony memory weighted by local carrion density (a cheap `FindNearbyFood` carrion count — O(local) on the
  new index).
- **`ant_worker` / forager** — heads to the colony's best-known site, eats carrion there (`consumeFood` →
  `FOOD_CONSUMED`), fills up, **carries it home** and deposits to grow the colony — reusing the wasp
  **provisioning loop verbatim** (`predation.go:169-191`: full → `Phase="homing"` + `CarryingBrood` → home →
  `depositBrood` → reset; `NestHomingTimeout` drops the load if orphaned).
- **`ant_leafcutter`** (data-driven type) — a forager attracted to a *plant* occupant instead of carrion;
  proves the type system. Ship after the carrion forager works.
- **`ant_soldier`** (optional) — reuses the wasp **nest-defend** state for colony defense.

### Colony memory = the "trail" core (server-only soft state)
A small per-colony list of known food sites `{cell, strength}` (strength = recent carrion density), strength
**decays each colony tick**, sites drop off at zero (the broods "source-gone sweep" precedent). Scouts
add/refresh; foragers pick best = nearest×strongest and stream nest↔site. Foragers repeatedly walking the
same route → **a line of ants reads as a trail** — emergent, no grid. Server-only soft state → biases the
forager's leg target only → no ledger/hash/client work. Deterministic via `sortedStringKeys` + `state.Rng`.

**Deferred enhancement (NOT v1):** a sparse, bounded pheromone scalar on actual worker-path cells (evaporate
over the sparse set, "sense-3-ahead" bias) for true shortest-path reinforcement + a visible decal. Only
needed for obstacle-dense optimization or a literal pheromone aesthetic — in our open zones, direct pathing +
`RaycastClamp` is already end-user-equivalent to ACO trails.

**Genuinely new code:** colony-memory struct + scout "register site" + generalize the provisioning
homing-trigger to fire for non-predator foragers. Everything else is reuse.

---

## SPIDERS — two archetypes (Grounded-style)
### A. Web-builder (orb-weaver-like) — ambush trapper
Patrols a small home range near its web patch; periodically spins a web tile; waits; prey slowed in the web
gets struck.
- **Web tile = occupant**, server-placed at runtime exactly like a nest split (`nests.go:319`:
  `chunk.SetOccupant` + `broadcastWorldUpdate` for the sprite) + emit `OCCUPANT_BLOCKS_BUGS` if it blocks.
- **Decision: web SLOWS, not hard-blocks** (a trap, not a wall): a new occupant field `web_slow` read
  **server-side** — a prey swarm center on a web cell gets `SpeedMult < 1` on its next leg (rides the
  existing leg-speed field; no per-bug client state, no new hash). The spider then pounces.
- **Webs decay** (lifetime / breakable HP) so they don't accumulate, and are **transient soft occupants — NOT
  written into saved zone data** (else a restart inherits a web-choked zone; treat like nests). Never place
  webs on zone-edge / spawn / transition cells (placement guard).

### B. Jumping / wolf spider — stalk-and-pounce hunter
Approaches slowly (stalk, low `SpeedMult`) then **pounces** (high-`SpeedMult` short leg) and strikes. **Pure
reuse of the centipede `ActionState` machine** (`centipede.go:65`: windup→surge→recover, sampling target
velocity at windup — a telegraphed lunge). Pounce = `surge` leg; kill = predation strike (`BUG_REMOVED`);
windup = the readable telegraph.

**Sharp determinism subtlety:** the centipede lunges at the *player* (server-known via `PLAYER_CELL_ENTER`).
The server has no per-bug positions — only prey **swarm centers**. So the spider's pounce targets the prey
**swarm center** (server-side), and the per-bug victim is resolved by the **authority client's strike pass**.
Pounce-to-center + strike-nearest-bug is fully consistent with the hybrid model — no new client state.

---

## Test world, art, verification
- **`ant_spider_lab`** (via `make_test_zone.py` / a small `make_*_lab`): carrion-pile arenas + a prey pen +
  open lanes so trails are visible. Run via `run_config.py --zone ant_spider_lab`; chart with the existing
  population/interaction/perf dashboard. **Balance is found here before any production zone.**
- **Art (Pipeline A — gpt-image-1):** `ant_hill`, `ant_worker`, `ant_scout` (+ `ant_queen`,
  `ant_leafcutter`, `ant_soldier`), `spider_web` tile, web-builder + jumping spiders; reuse `dead_*` carcasses.
- **Verification:** Go unit tests per mechanic (mirror `predation_test.go`/`brood_test.go`); `sim-determinism`
  + new scenarios (should stay byte-identical — they emit only existing ledger events); fresh-match
  `run_sync_latejoin` when sync is touched + real two-client Unity when available; `ant_spider_lab` chart
  loop for balance + FEEL. Reconcile `architecture_swarm_sync`, `BACKLOG.md`, `lenses.md`, and `frontier-sync`
  at completion.

---

## Build phasing (each its own verified unit; lowest-risk first)
0. Rotten-fruit decay fix → re-profile + bug_lab.
1. `ant_spider_lab` test zone + art stubs.
2. **Jumping spider** (predation + ActionState reuse; retarget to prey) — the safest/fastest win.
3. **Spider web** (occupant + `web_slow` + decay + ambush).
4. **Ant colony core** (hill/queen/eggs via Nest+Brood; worker forage→carry→deposit via generalized
   provisioning; carrion eating).
5. **Colony memory + scouts** (the trail feel) — watch a trail form in the lab.
6. Leafcutter / soldier + balance pass; only then a production zone.
- Deferred: the sparse pheromone trail layer + decal (only if the emergent trail isn't enough).

---

## Certainty (after the lens sweep)
- Determinism fit **~95%** (ant trails server-only; webs reuse hashed `OCCUPANT_BLOCKS_BUGS`; pounce/kills
  reuse legs+ActionState+strike; web-slow is swarm-center-level, NOT per-bug).
- Reuse correctness **~92%** (`nests.go:319`, `centipede.go:65`, `predation.go:169-191`, `brood.go`,
  `FindNearbyFood` all read + confirmed fit).
- Ant colony loop **~88%**; trail feel **~85%**; spider web **~85%**; spider pounce **~90%**; perf **~90%**
  (O(local) on the new indexes; the 256² pheromone grid is explicitly avoided); art/authoring **~88%**.
- **Ecology balance ~70% (inherently playtest)** — ants vs detritivores for carrion; spiders vs
  wasps/centipedes for flies. A bug_lab tuning problem, not an architecture risk; ship behind the lab.

## Design review & complexity
**Good design, two honest caveats.** Strengths: reuse-dominant (~80% maps onto determinism-verified systems),
determinism-aligned (the headline ant-trail feature adds zero sync surface), perf-aware (refuses the O(zone)
grid), fun-first/legible, honest about heuristic-equivalence. Caveats: (1) **ecology balance** — two species
perturbing a hard-won food web is real open-ended tuning; (2) **trail "feel" is unproven** — colony-memory
may read as "bugs walking to food" without the deferred pheromone layer.
**Complexity:** decay = Low; jumping spider = Low–Med; spider web = Med; ant colony core = Med–High (bulk of
new code); colony memory+trails = Med; balance = Med–High (open-ended). **Overall Med–High, concentrated in
ants.** Spiders are the faster, higher-confidence payoff — build them first (as phased).

## Sources
Empires of the Undergrowth ([basic mechanics](https://wiki.hoodedhorse.com/Empires_of_the_Undergrowth/Basic_Mechanics)) ·
SimAnt ([scent trails](https://strategywiki.org/wiki/SimAnt)) ·
ACO/stigmergy ([example](https://github.com/Melell/Ant-Colony-Simulation)) ·
Grounded ([Orb Weaver](https://grounded.fandom.com/wiki/Orb_Weaver), [Wolf Spider](https://grounded.fandom.com/wiki/Wolf_Spider)).
