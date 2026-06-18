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

### 2026-06-18 · observation · Food is massively over-supplied (the next lever)
**RESSTATS (per game-day):** `rotten` ~19–29k items, `nectar` ~28.5k, `milkweed` ~2.6k — none of it ever
depletes. So the food-competition bound never engages and populations run away. The dominant tuning lever
going forward is to tighten the plant/food side (windfall accumulation / rot decay / flower + milkweed
counts & regen) until food becomes a real, depleting constraint and boom-bust emerges. _(Not yet tuned.)_
