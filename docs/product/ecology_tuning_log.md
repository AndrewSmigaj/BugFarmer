# Ecology Tuning Log

Append-only record of every population-balancing strategy we try on the real zone **village_21_B**, so we
never retread a dead end or lose what worked. The goal: all 6 species (fly, butterfly, wasp, centipede,
millipede, beetle) sitting in good, *alive* (oscillating) bands, bounded by emergent food competition /
predation / aging — NOT by artificial knobs. Hard `max_population` is only a rare backstop.

## How to read this
Each entry: **date · category · the exact change · seed · measured result**. Categories:
`food` (source counts / regen / decay), `breed` (breeding params), `behavior` (vision / forage / movement),
`spawn` (seeding / Director bands / events), `mechanic` (a code fix to how a mechanic works), `infra`
(tooling that makes the above measurable). Measured result = per-species min/max/trajectory + which
telemetry pointed the way (ECOSTATS births/deaths, RESSTATS food stocks, PREDLOG kills).

**Runs are only comparable once seeded** — see the determinism entry below. Pre-determinism numbers are
directional, not reproducible.

---

## Reference levers (where each knob lives)
- **Bugs** — `nakama/data/species.json`: `reproduce_cooldown`, `breed_amount`, `egg_count_*`,
  `satiation_decay_rate`, `feed_amount`, `vision_range`, `lifespan_secs`, `forage_chance`, `attractions_by_phase`.
- **Shared dials** — `nakama/data/ecology_tuning.json`: nectar/host regen, `host_breed_cost`,
  `max_host_capacity`, predator breed satiation, nest-found distances.
- **Plants/world** — `tools/zonegen/scenes/zone_village_21_B.py`: counts of fruit trees, milkweed,
  flowers, leaf-litter; orchard layout. Fruit→rot pipeline timing in `handlers_farming.go`.
- **Spawn/Director** — zone.json `bug_spawning.species_caps` (initial/max/`max_population`/`min_population`/
  `event_low`/`event_high`/`cull_at`/`spawn_interval`) + `ecology_director.go`.
- **Run a config**: `python3 tools/run_config.py <cfg> --zone village_21_B --duration 300`
  (charts → `tools/_generated/ecology_charts/`; food stocks via RESSTATS + `plot_phase.py`).

---

## Log

### 2026-06-18 · mechanic · Flies can now breed on rotten fruit (the core fly fix)
**Problem:** flies stuck at ~30 (`b_brood` 3–9/day) despite 19k+ rotten fruit on the ground — they were
*supposed* to breed on it. **Root cause (verified in code):** a maggot brood was tied to the ONE apple a
single fly stood on, keyed by that exact cell, and swept (dropping un-matured eggs) the instant that apple
was eaten (seconds later, before the 10s egg maturation). No shared pile. **Fix** (`brood.go`): ground-pile
broods are now ONE SHARED pile per ~4×4 area (≈ per tree's windfall), decoupled from any single apple's
lifetime (food is paid at lay time), retired only once fully hatched out; ground-pile keys namespaced `g:`
so they can't collide with milkweed/station broods. **Result:** flies breed correctly — `b_brood`
48→445→1170/day, pop climbs toward ~1500 (overshoots; food still over-supplied — see below). Butterflies
appeared to crash the same run, but that comparison was pre-determinism (not reliable) — under investigation.

### 2026-06-18 · infra · Made the server sim reproducible (determinism pass) — PREREQUISITE for tuning
**Problem:** `WorldSeed` was never wired into `math/rand`, and the sim iterated Go maps in random order, so
every run was a different random draw — population comparisons were partly noise (couldn't attribute a
change to a parameter). **Fix:** per-match seeded RNG (`state.Rng` from `zone.seed`) replacing ~45 global
`rand.*` calls; sorted iteration (`sortedStringKeys`) on every loop that draws rand / mints IDs (main swarm
loop, splitting, predator breeding, nests, broods, spawn, Director). Harness pins `seed=1337`; production
stays random. Safe for netcode (clients replay server-broadcast legs). **Result:** _pending the
reproducibility gate (same config twice → identical ECOSTATS)._

### 2026-06-18 · mechanic · Rotted fruit now decomposes (was an immortal-food hack)
**Sanity check (is it sane / does it make sense / will it help):** rot window ≈ 2× fly lifespan (6
game-days) — sane (same order as the creatures eating it), makes sense (bounds the standing pile to "what
dropped in the last ~6 days"), should help (turns infinite fly food into a finite, competed-for resource).
**Change** (`handlers_farming.go`): rotted fruit `Lifetime` 999999 (≈1190 game-days = never) →
`rottenFruitDecaySeconds = 5040` (6 game-days). The 999999 was a hack *I* added earlier to feed flies — it
made fly food effectively infinite and let the rotten count balloon past 30k. **Result:** see next entry —
the fix alone did NOT drop the pile, which exposed a deeper bug.

### 2026-06-18 · infra · Test zones were inheriting prior runs' ground items (the real confound)
**Symptom:** rotten pile was ~40k *on day 1* — impossible from this run's drops (fruit needs 2 game-days to
rot), and it had grown across runs (30k→32k→41k). **Root cause:** `zone_persist.go` saved AND restored
ground items unconditionally; `EphemeralSwarms` only resets *swarms*, not ground items. So every harness
run reloaded the immortal rotten fruit my earlier runs had saved to postgres — each run started dirtier
than the last, which ALSO secretly broke the reproducibility gate. **Fix:** skip ground-item
save+restore for `EphemeralSwarms` (fresh-start) zones, so a tuning run neither inherits nor accumulates a
pile and the DB self-cleans on next save. This is the prerequisite for ANY trustworthy tuning number.

### 2026-06-18 · infra · Determinism: ~20× less noise, not bit-perfect (good enough to tune)
After the seeded-RNG + sorted-iteration + deterministic-ID + posHash + clean-start fixes, run-to-run
variance dropped from ~30× (butterfly 353 vs 12) to ~1.5× on day 1 (fly 12 vs 13, millipede 27 vs 43).
But it is NOT yet byte-identical: the divergence reaches species far from the harness player (millipede
b_reproduce 25 vs 41), which is the signature of a SINGLE shared sequential RNG stream desyncing from one
non-deterministic consumption point — most likely the harness player's wall-clock-timed join/move messages
perturbing nearby bugs, which then shifts every later draw in the shared stream. A full fix would need
per-subsystem counter-RNG (keyed by tick/entity, like the client's CounterRng) — a big refactor, deferred.
**Decision:** tune on LONGER runs where the population magnitude/trend dominates the residual per-day
noise, and treat a lever as "real" only if it moves a population well beyond ~1.5×. Revisit counter-RNG
only if a tuning signal ever gets lost in the noise.

### 2026-06-18 · baseline · Clean 8-game-day baseline (seed 1337, post-determinism)
Per-species pop by game-day, and the food stocks:
- fly: 16,17,15,61,371,1344,1322,1184 — booms to ~1300, sits near its 1500 cap (CAP-limited, not
  food-limited — the plan wants food/predation to bound it instead).
- butterfly: 10,13,13,26,25,16,13,34 — oscillates low.
- wasp: 4,4,4,4,4,4,4,4 — STUCK; avg_sat ~20, d_starve 4–8 → wasps STARVE despite 1300 fly prey.
- centipede: 4×6 then 11,41 — starts climbing day 7–8. millipede: ~130 stable. beetle: 3 then 8 (day 8).
- rotten: 0,0,345,2348,3480,4575,5079,5835 — bounded (not 40k) but still climbing toward a ~6–8k plateau;
  nectar ~28.4k flat, milkweed ~2.6k flat (butterfly food still never bites).
Read: the standing rotten (~6k) feeds flies to the cap. Rather than cut the fruit again (owner set the
10× trees + 6-day rot deliberately), the aligned lever is PREDATION — if wasps actually ate the abundant
flies they'd crop the boom into an oscillation. Next: why do wasps starve amid 1300 prey?

### 2026-06-18 · behavior · Wasp home_range 40→80 (v21b_wasp_range) — PARTIAL win
Hypothesis: wasps starve because their 40-cell nest range can't reach the dispersed flies (centipedes,
free-roaming, thrive on the same prey). Result: wasp KILLS jumped (day5–8: 12,18,11 flies vs baseline ~0)
and flies were cropped (peak 1344→1023, day8 1184→810) — so reach WAS a limiter. BUT wasp pop still stuck
~5 (4,4,6,4,5,5,5,5). So reach is fixed; the population won't grow. (Butterfly 222 vs baseline 10–34 is
the determinism noise, not this lever — butterflies are the noise-sensitive species; ignore for now.)
Keep home_range 80 (net positive: more predation, no downside). Next bottleneck: survival/founding.

### 2026-06-18 · behavior · Wasp satiation_decay 0.11→0.06 (v21b_wasp_survive, on top of range 80) — testing
Why: the founding trigger (nests.go:273) needs the resident patrol to reach MaxSwarmSize, but it starves in
troughs (sat 10↔74) and culls back to ~5, so it never founds daughter nests to grow the colony. Slower
decay should keep the swarm fed between hunt bursts → grow → found → spread. [result pending]

### 2026-06-18 · behavior · Wasp decay 0.06 result + ROOT CAUSE (nest economy, structural)
Decay 0.06 fixed starvation (d_starve→0, sat 40–99) but wasp pop STILL stuck ~4, 0 nest foundings, and
`b_nest` = 8 on day 1 then **0 every day after** — the nest hatches its initial brood once, then goes
DORMANT. Root cause (predation.go:131–156): a nest wasp only carries brood home + deposits when its
`Satiation >= 100` (full), and the homing trip ABORTS if it can't reach the nest within NestHomingTimeout.
So there's a structural tension — **small home_range → can't reach prey (starve); large home_range → hunts
too far to return-and-deposit within the timeout → nest never refills its brood → never hatches → resident
never reaches MaxSwarmSize (10) → never founds daughters → colony stuck at the spawn floor.** This is why
home_range alone traded reach for deposit. NOT a param tweak — the nest deposit/homing loop needs a
redesign (e.g. deposit at deposit_satiation instead of full-100; or a return-timeout that scales with
home_range; or decouple brood accrual from the home trip). Deferred to the owner: redesign the wasp nest
economy, or accept the free-roaming CENTIPEDE as the primary fly predator (it works: 4→41). The wasp
configs (v21b_wasp_range / _survive) are diagnostic only — NOT applied to species.json.

### 2026-06-18 · mechanic · Nest-predator behavior redesign → 2-state forager loop (predation.go)
The wasp control scheme was four interacting thresholds (hunt-start 45, home 100, deposit-reset 80, hunt
timeout) that produced a 45–100 "dead zone" (too fed to start a hunt, not full enough to home) AND made a
hungry wasp give up and idle-wander — so it almost never completed a home trip, the nest brood never
refilled (b_nest 8→0), and the colony froze at the spawn floor. Redesigned the nest-predator branch to a
clean 2-state loop keyed off ONE threshold `predatorFullSatiation`:
  FORAGE while satiation < full → always re-acquire the nearest in-range prey (lost/elusive prey = pick the
    next; never idle while hungry);  PROVISION at full → carry home, deposit brood, drop to deposit level,
    forage again.
The point it stops hunting IS the point it heads home, so there's no gap. Navigation was never the issue
(Move beelines, no collision; homing reaches the nest fine) — the *decision to go home* was. Free-roaming
individuals (centipede) are untouched (keep their own threshold + rest-wander). Expect: wasps deposit
reliably → colony grows → founds daughters → crops the fly boom (the predator-prey oscillation). [testing]

### 2026-06-18 · observation · Food is massively over-supplied (the next lever)
**RESSTATS (per game-day):** `rotten` ~19–29k items, `nectar` ~28.5k, `milkweed` ~2.6k — none of it ever
depletes. So the food-competition bound never engages and populations run away. The dominant tuning lever
going forward is to tighten the plant/food side (windfall accumulation / rot decay / flower + milkweed
counts & regen) until food becomes a real, depleting constraint and boom-bust emerges. _(Not yet tuned.)_
