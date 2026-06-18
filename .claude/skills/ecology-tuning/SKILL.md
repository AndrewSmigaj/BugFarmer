---
name: ecology-tuning
description: Use when balancing the bug ecology — tuning the 6-species food web (fly, butterfly, wasp, centipede, millipede, beetle) so populations sit in good, alive (oscillating) bands instead of crashing, running away, or pinning the hard cap. Covers the run_config harness, the per-zone chart layout, how to read population/interaction/phase charts, the levers (species params, plant/food, spawn/Director), the determinism caveats, and the discipline (one sane lever at a time, measure, log). Read this before proposing ANY ecology balance change.
---

# Ecology tuning

Balance the living 6-species ecology so every species sits in a good, **oscillating** band — bounded by
EMERGENT mechanics (food competition, predation, aging, breeding-when-fed), NOT by artificial knobs or the
hard `max_population` cap (which is only a rare backstop). The job is tuning the REAL parameters of the bugs
and plants until the emergent populations land well.

## 0. Discipline (the rule that matters most)
Before EVERY change, say out loud: **is this sane? does it make sense? will it actually help?** Then change
ONE lever, predict the effect, run, measure, and write it in the log. Do NOT lurch to 10×/100×/∞ values, and
do NOT stack changes you can't separate. The owner has repeatedly caught kneejerk extremes — don't.

- **Strategy log (append-only):** `docs/product/ecology_tuning_log.md`. EVERY move + its measured result
  goes here (category, exact change, seed, per-species outcome). Read it first so you don't retread.
- Tune in ISOLATION then couple: get a consumer↔food pair into a good band before adding predators on top.

## 1. Zones — tune the REAL one
- **`village_21_B`** — the real shipped 256×256 open zone with the full food web. **TUNE HERE.**
- **`bug_lab`** — a small FENCED arena for OBSERVING individual behavior only. Its pens are fake/unnatural;
  balance tuned there does NOT transfer. Archived. Don't balance on it.

## 2. Run a config
```bash
python3 tools/run_config.py <config> --zone village_21_B --duration 600   # ~8 game-days
```
- Configs live in `tools/bug_lab_configs/*.json` — a DELTA deep-merged over canonical data:
  `species` (species.json fields, incl. nested `predation`), `tuning` (ecology_tuning.json dials),
  `bug_spawning` (zone.json species_caps / spawn weights / Director bands), `fruit` (tree rates),
  `flags`. Supports `"extends": "<parent>"` to build on a prior config.
- `run_config.py` SNAPSHOTS + RESTORES canonical data around the run (it mutates species.json etc. then
  reverts) — so a sweep never leaves the repo dirty. It restarts nakama, runs the headless sync-harness,
  charts, and restores. `v21b_baseline` = no deltas (the reference). Duration×0.0133 ≈ game-days.
- The harness pins **seed 1337** for reproducibility (production zones keep seed 0 = random per match).

## 3. Where the charts go (per-zone layout)
`tools/_generated/ecology_charts/` (see its README.md). Per ZONE:
- **`<zone>/current/`** — the CURRENT setup: `population.png`, `interactions.png`, `phase_portraits.png`
  from the latest baseline run = where the zone sits now. Refreshed automatically on any `baseline` run.
- **`<zone>/archive/<timestamp>_<tag>/`** — every run, with a `note.md` (what it changed + result), for
  comparing which settings were better.
- **`<zone>/comparisons/`** — overlay charts (one line per run): `python3 tools/plot_compare.py out.png
  "label=_data/nakama_<tag>.log" ...`. The fastest before/after read.
- **`_data/`** — raw `nakama_*.log` + telemetry CSVs (regenerate plots from these).
- **ALWAYS surface the chart path to the owner** after a run — don't just grep the log silently.

### Reading the charts
- **population.png** — in-band & oscillating? or flat / runaway / crashed / pinned at the cap?
- **interactions.png** — WHY it moved. `b_*` births by source, `d_*` deaths by cause (from ECOSTATS).
  High `b_reseed` = propped up by the Director (not self-sustaining — drive it toward 0). High `d_starve`
  = food/access-limited. PREDLOG = predator→prey kills.
- **phase_portraits.png** — population vs its food, coloured by time: closed loop = alive boom-bust cycle;
  inward spiral = damping to flat; outward = crash/runaway. (RESSTATS logs the food STOCKS.)

## 4. The levers
- **Bugs** (`nakama/data/species.json`): `reproduce_cooldown`, `breed_amount`, `egg_count_*`,
  `satiation_decay_rate`, `feed_amount`, `vision_range`, `lifespan_secs`, `forage_chance`,
  `attractions_by_phase`, and the `predation` block (`home_range`, `feed_per_kill`, `strike_*`,
  `deposit_satiation`, `hunt_satiation_threshold`, prey list).
- **Shared dials** (`nakama/data/ecology_tuning.json`): nectar/host regen, `host_breed_cost`, caps,
  predator breed satiation, nest-found distances.
- **Plants/world** (`tools/zonegen/scenes/zone_village_21_B.py` + regen): counts of fruit trees, milkweed,
  flowers, leaf-litter. Fruit→rot pipeline timing lives in `handlers_farming.go`.
- **Spawn/Director** (zone.json `bug_spawning.species_caps`: initial/max/`max_population`/`min_population`/
  `event_low`/`event_high`/`cull_at`/`spawn_interval`) + `ecology_director.go`.
- Most species/tuning/spawn levers are config-able (no rebuild). Plant COUNTS need a zonegen edit + regen.
  Go MECHANIC changes (e.g. predator behavior) need `docker compose up builder --build` then a fresh run.

## 5. Caveats that bite (learned the hard way)
- **Reproducible-ish, not byte-identical.** Seeded RNG + sorted iteration cut run-to-run variance ~20×, but
  a residual shared-RNG-stream desync (the harness player) leaves ~1.5× day-to-day noise. Trust a lever
  only if it moves a population WELL beyond ~1.5×. Butterfly is the most noise-sensitive — don't over-read
  single-run butterfly numbers. (A full fix = per-subsystem counter-RNG; deferred.)
- **Test zones (`EphemeralSwarms`) must start clean.** Ground items used to persist + accumulate across runs
  (an immortal-rotten-fruit bug grew the pile to 40k and silently broke comparisons). That's fixed; if
  numbers look impossibly large on day 1, suspect persisted state again.
- **Rotted fruit decomposes** (`rottenFruitDecaySeconds`, ~2× fly lifespan) — it is NOT infinite food.
- **Determinism is netcode-safe**: clients replay server-broadcast swarm legs, so changing server RNG/order
  only changes which legs broadcast (identically to all clients). Run the `test-changes` 2-client hash
  parity after any sim change to confirm no desync.

## 6. Current status (read the tuning log for detail)
Determinism + fruit-rot + clean-start fixed. Flies breed (booms ~1300, still cap-limited). Centipede is the
working fly predator; millipede stable ~130. **Wasp nest economy is still broken** (resident starves at the
nest → nestless Director reseeds; provision/deposit rhythm fragile) — open problem. Butterfly noisy.
