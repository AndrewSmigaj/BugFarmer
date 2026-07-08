---
name: ecology-tuning
description: Use when balancing the bug ecology — tuning the living food web (flies, wasps, centipedes, ants and the rest of the species defined in nakama/data/species.json) so populations sit in good, alive (oscillating) bands instead of crashing, running away, or pinning the hard cap. Covers the run_config harness, the per-zone chart layout, how to read population/interaction/phase charts, the levers (species params, plant/food, spawn/Director), the determinism caveats, and the discipline (one sane lever at a time, measure, log). Read this before proposing ANY ecology balance change.
---

# Ecology tuning

Balance the living ecology (every species in `species.json`) so every species sits in a good, **oscillating** band — bounded by
EMERGENT mechanics (food competition, predation, aging, breeding-when-fed), NOT by artificial knobs or the
hard `max_population` cap (which is only a rare backstop). The job is tuning the REAL parameters of the bugs
and plants until the emergent populations land well.

## 0. Discipline (the rule that matters most)
Before EVERY change, say out loud: **is this sane? does it make sense? will it actually help?** Then change
ONE lever, predict the effect, run, measure, and write it in the log. Do NOT lurch to 10×/100×/∞ values, and
do NOT stack changes you can't separate. The owner has repeatedly caught kneejerk extremes — don't.

### HARD RULES (each one was learned by screwing it up — do not repeat)
1. **ONE run at a time.** There is a single nakama server + one harness, and `run_config` RESTARTS nakama as
   its first step — so launching a second run while one is in flight CORRUPTS BOTH (and the data
   snapshot/restore). Before launching: `pgrep -f run_config` must be empty. Never start a second. Set a
   watcher on the running one's completion (`pgrep -f "run_config.py <tag>"` gone), don't poll-and-launch.
2. **Widen the window before tuning a slow system.** If a metric is still drifting at the END of the run
   (not flat), it has NOT settled — DO NOT tune to force it faster. Re-run LONGER (e.g. duration 1200 @
   sim_batch 6 ≈ 48 game-days) and read the true equilibrium. Tuning against a transient = chasing a number
   that was never real. (Millipede looked like it'd crash at day 16; at 47 days it was a stable equilibrium.)
3. **No hard caps to manage populations — caps are a LAST-RESORT backstop.** Populations must be bounded
   EMERGENTLY (food / predation / space). If a species pins at exactly its `cap.Max` band, that's the cap
   binding, not ecology — RAISE the cap to a backstop and find the real emergent bound. NB: `individual`-
   category species (millipede, centipede) hit the **swarm-count cap (`cap.Max`) before food can bind**
   (match.go ~113) — so check the cap FIRST when a species ignores every food/lifespan lever.
4. **Never aim predator spawns at the "densest" area.** The densest bug cluster will be the PLAYER'S PEN, and
   persistently spawning predators there is untrackable + unwanted (accidental drift is fine). Place spawns
   the WASP way: deliberate, hand-picked, SPREAD points near (not on) prey, partitioned across species. Bugs
   SHOULD spread over the map via many small tree/flower patches and eventually pressure player farms — that's
   the intended world experience; provide the patches, don't point spawns at density.
5. **Enumerate ALL levers before tuning; don't tunnel.** List every knob first (§4) — species fields, the 18
   tuning dials, spawn/zone caps, fruit ticks, AND placement — then pick. PLACEMENT is a first-class lever
   (count=level, placement=spread/stability, co-location=coupling); we tuned through it for the wasps. Don't
   fire single params run-after-run; find the BINDING CONSTRAINT (read code/data) before choosing a lever.
6. **Distinct tag per run.** Reusing a config name overwrites its `_data/nakama_<tag>.log` and makes the
   archive folders ambiguous. One experiment = one name. Report run counts/durations/coverage HONESTLY.

- **Strategy log (append-only):** `docs/product/ecology/ecology_tuning_log.md`. EVERY move + its measured result
  goes here (category, exact change, seed, per-species outcome). Read it first so you don't retread.
- **Controllability map:** `docs/product/ecology/ecology_control_campaign.md` — which lever moves which band (and
  whether it moves CENTRE vs AMPLITUDE), the 6 analysis lenses, and the two hardest species (millipede =
  cap-bound until you raise the cap + scarce litter; centipede = reaches its cap only when SPAWNED NEAR PREY
  + the kills→breeding conversion). Read before re-investigating a "stuck" species.
- Tune in ISOLATION then couple: get a consumer↔food pair into a good band before adding predators on top.

## 1. Zones — tune the REAL one
- **`village_21_B`** — the real shipped 256×256 open zone with the full food web. **TUNE HERE.**
- **`bug_lab`** — a small FENCED arena for OBSERVING individual behavior only. Its pens are fake/unnatural;
  balance tuned there does NOT transfer. Archived. Don't balance on it.

## 2. Run a config
```bash
python3 tools/ecology/run_config.py <config> --zone village_21_B --duration 600   # ~8 game-days
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
- **`<zone>/current/`** — WHERE THE ZONE SITS NOW: `population.png`, `interactions.png`,
  `phase_portraits.png`, `bugmap_contact_sheet.png` + `SOURCE.txt` (which run they're from). **Refreshed on
  EVERY run** — the latest tuning run IS the current picture. This is THE folder to keep up to date and to
  look in: as you tune a zone, `current/` must always reflect the most recent run (the tooling does this
  automatically now; if you ever see `current/` older than your last run, that's a bug — fix it, don't
  leave stale charts there). `archive/<ts>_<tag>/` keeps the dated history; `current/` is "latest".
- **`<zone>/archive/<timestamp>_<tag>/`** — every run, with a `note.md` (what it changed + result), for
  comparing which settings were better.
- **`<zone>/comparisons/`** — overlay charts (one line per run): `python3 tools/ecology/plot_compare.py out.png
  "label=_data/nakama_<tag>.log" ...`. The fastest before/after read.
- **`_data/`** — raw `nakama_*.log` + telemetry CSVs (regenerate plots from these).
- **After every run: refresh `current/` (the tooling does this) AND show the owner those charts** —
  `Read` `current/{population,interactions,bugmap_contact_sheet}.png` so they render. Reading the raw
  ECOSTATS log is for YOUR analysis; the owner looks in `current/` and wants the charts to be the latest.

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
- **Shared dials** — every dial's DEFAULT lives in `nakama/modules/world/ecology_tuning.go` (read it for the
  full knob set); override any by ADDING that key to `nakama/data/ecology_tuning.json` (which only *sets* a
  subset — the rest use their .go defaults). Knobs include nectar/host regen (`nectar_regen_per_tick`,
  `max_nectar`, `host_regen_per_tick`, `host_breed_cost`, `max_host_capacity`), `predator_breed_satiation`
  (the kills→population conversion knob — centipede & other nestless predators breed when this well-fed),
  `spawn_satiation`, the nest economy (`nest_brood_cap`/`nest_hatch_*`/`nest_founding_size`/`nest_found_dist_*`),
  and `max_litter`/`litter_regen_per_tick` — leaf_litter, a DEPLETABLE forage pool (millipede's detritus food,
  the forest-floor analogue of nectar); millipede ≈ food-limited by litter THROUGHPUT once its cap isn't
  binding. RESSTATS reports `litter=` next to `nectar=`.
- **Fruit timing** (`nakama/data/entities/occupants.json`, `fruit` config delta): `fruit_grow_ticks`,
  `fruit_drop_ticks`, `fruit_rot_ticks`. The rot LAG (~2 game-days fallen→rotten) is the fly boom-bust
  AMPLITUDE knob; fly lifespan ~3 days, so the lag is most of a fly's life = sharp busts.
- **Placement (first-class — `tools/zonegen/scenes/zone_*.py` + regen):** spawn-circle positions/count/radius,
  nest positions, refugia (a prey source with NO predator in range = stops crash-to-zero), co-location of
  predator-with-prey. Count→band LEVEL, placement→spread/STABILITY, home_range→coupling strength.
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
