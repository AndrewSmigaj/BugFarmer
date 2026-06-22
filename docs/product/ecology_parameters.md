# Ecology tuning parameters — the control panel

Every dial that shapes a bug population's size + oscillation, grouped by **what it does** to the curve.
Tune populations by **adjusting these parameters** — NOT by bolting on new food sources/items. The model
already has enough levers; the art is finding the right values on the 6× `bug_lab` chart (see the
`test-changes` skill §2.5).

**The tuning rig (Phase 4c).** The Go balance consts below are overridable as DATA via
`nakama/data/ecology_tuning.json` (`Tuning` struct, loaded at MatchInit; absent file → compiled
defaults = byte-identical). A run is a CONFIG — `tools/bug_lab_configs/<name>.json` deep-merged over the
baseline (sections: `tuning`→ecology_tuning.json, `species`→species.json, `fruit`→occupants.json tree
rates, `lab`→Director bands/caps) — applied + run + restored by `tools/run_config.py <name>`. The
**interaction log** (`ECOSTATS`/`PREDLOG` → `tools/plot_interactions.py`) is the "why": per-day
births-by-source / deaths-by-cause + the predation matrix. `tools/compare_configs.py` scores each config
on the objective (mean vs target center, amplitude, **%re-seed births → 0 = self-maintained**). Change
ONE dial per config; diagnose with the interaction log; never guess.

**Mental model — a population sits where BIRTHS = DEATHS, capped by FOOD.** To move a species:
raise/lower its **birth rate**, its **death rate**, or its **food supply** (carrying capacity). The
Director **bands** are the last-resort guardrails, not the primary bound — if a species only sits where
it does because the cull holds it there, you've tuned the wrong dial (bound it by food instead).

Legend: **↑pop** = raising this grows the population; **↓pop** = raising this shrinks it.

---

## 1. BIRTH RATE — how fast a population regrows
| Param | Where | Effect |
|---|---|---|
| `reproduce_cooldown` | `species.json` per species | sec between breeds. ↓pop (longer = fewer births) |
| `breed_amount` | `species.json` | how fast the ReproductionMeter fills at a breeding food. ↑pop |
| `hatch_time` | `species.json` (brood layers: fly/butterfly) | egg→bug maturation delay. ↓pop |
| `max_swarm_size` / `min_swarm_size` | `species.json` | swarm grows in-place to max, then splits a child. ↑pop |
| `reproduceFoodCost` | `match.go` const | food consumed per breed event. ↓pop |
| **Breeding-food bottleneck (butterflies):** `hostBreedCost` ↓pop, `hostRegenPerTick` ↑pop, `maxHostCapacity` ↑pop (`handlers_farming.go`), **# of milkweed** in the zone ↑pop | — | the host capacity gates BIRTHS; the tightest butterfly dial |
| **Nest predators (wasp):** `NestHatchCount` ↑pop, `NestHatchCost` ↓pop, `NestBroodCap` ↑pop, `NestFoundingSize`, `NestRehatchDelay` ↓pop, `MaxNests` ↑pop | `entities/nest.go` + zone `species_caps.max_nests` | wasps grow ONLY via the nest (hatch) + founding daughter hives |
| **Nestless carnivores (centipede):** `predatorBreedSatiation` | `predation.go` const | satiation needed to breed on the well-fed timer. ↓pop (higher = breeds less) |

## 2. DEATH RATE — how fast they die
| Param | Where | Effect |
|---|---|---|
| `lifespan_secs` / `lifespan_spread_secs` | `species.json` | old-age death. ↓pop (shorter life). Spread destaggers cohort die-offs |
| `satiation_decay_rate` | `species.json` | how fast hunger sets in → how soon it starves with no food. ↓pop |
| `spawnSatiation` | `match.go` const | newborn's starting satiation (survival runway). ↑pop |
| `starvationDeathSecs` | `match.go` const | sec at 0 satiation before the starvation cull begins. ↑pop |
| `starvationCullFrac` / `starvationCullPause` | `match.go` const | how hard/often a starving swarm dies back. ↓pop |
| **Predation pressure on PREY (↓prey pop):** `feed_per_kill` (predator sustains longer per kill), `kills_per_strike`, `strike_radius`, `strike_cooldown_ticks` (lower = strikes more), `hunt_speed_mult`, `vision_range`, `hunt_satiation_threshold` (higher = hunts even when fairly full = MORE kills) | `species.json` predator `predation` block | these make a predator a better hunter → fewer prey, but more predators |

## 3. FOOD SUPPLY — the carrying capacity (where births = deaths caps out)
| Param | Where | Effect |
|---|---|---|
| **Fruit (fly food):** `max_fruit`, `fruit_grow_ticks` (↓=faster), `fruit_drop_ticks`, `fruit_rot_ticks` (↑=fruit lasts longer on the ground = more fly-food window), # of trees, tree-rate MIX | `occupants.json` tree `world` block + zone placement | fly carrying capacity. Trees are rain-gated (need a full `treeTankCap` tank) |
| `treeTankCap` + `rainDailyChance`/`rainMin`/`rainMaxTicks` | `handlers_farming.go` / `handlers_env.go` | how often trees actually fruit (rain waters the tank). ↑fly food |
| **Nectar (butterfly feeding):** `maxNectar`, `nectarRegenPerTick`, **# of flowers** | `handlers_farming.go` + zone placement | butterfly feeding carrying capacity. Fewer flowers / slower regen ↓pop |
| **Detritus (millipede):** `leaf_litter` occupants (nectar pool) — # of piles ↑pop | zone placement | millipede's own food (separate from the flies' fruit) |
| **Carrion (beetle):** there is NO knob — it's the OLD-AGE/STARVATION death rate of the OTHER species. More deaths → more `dead_<bug>` → more beetles. Predation CONSUMES prey (no corpse) | — | beetle pop tracks the corpse supply (see the `corpses` chart line) |
| `feed_amount` | `species.json` | satiation gained per tick at food (faster sate = breeds sooner). ↑pop |
| `consume_rate` | `species.json` | how fast a big swarm drains a food source (faster = food-limited sooner). ↓pop |
| `food_value` | `items.json` (rotten fruit, `dead_*`) | satiation per food item. ↑pop |
| `droughtFoodRegenMult` | `handlers_farming.go` const | during a drought ALL plant food (nectar+host) regrows ×this. ↓pop of nectar/host feeders in drought |
| **Compost stations:** `food_per_unit`, `capacity`, `process_ticks` | `placeables.json` station block | compost→fly-food throughput (a farming mechanic: crops/scraps → compost) |

## 4. DIRECTOR BANDS — the last-resort guardrails (NOT the primary bound)
Per-species in the zone's `species_caps` (`zone.json` / authored in `make_bug_lab.py`'s `DIRECTOR`):
| Band | Effect when crossed |
|---|---|
| `min_population` | below → RE-SEED (anti-extinction floor). Set just above 0 |
| `event_low` | below → request EXTRA-RAIN (more fruit). Relief BEATS drought (see note) |
| `event_high` | above → request DROUGHT (suppress rain + cut nectar/host regen) |
| `cull_at` | above → HARD CULL. Keep this FAR above the natural band — it's the safety, not the dial |
| `cull_with` | predator species released on a prey boom (else a direct cull) |
| `max_population` | the HARD crash-guard (server mints nothing past it). 0 = uncapped |
| `max` / `initial` / `swarm_size` | swarm-COUNT cap / initial seed / bugs per swarm |

**⚠ Relief-over-suppression gotcha:** if ANY species is below its `event_low`, rain fires and CANCELS
every drought request that pass. So a chronically-low prey species (flies) blocks the butterfly drought
from ever firing. Corollary: **a population that needs the drought to be braked can't rely on it while a
prey species is starving** — bound it by FOOD instead (§3), and keep the drought as a bonus.

Director clock: `directorIntervalTicks` (how often it acts), `directorPredatorCount`, `droughtDays`
(`ecology_director.go`).

## 5. MOVEMENT / SPATIAL / CLUSTERING (indirect — affects who eats whom, and where)
**Hunt effectiveness** (`species.json`): `base_speed`, `vision_range`, `wander_radius`, `home_range`,
`hunt_speed_mult`. A faster / longer-sighted predator catches more prey (↓prey, ↑predator); a faster prey
flees better.

**Swarm grain** (`species.json`): `max_swarm_size` (a swarm past this SPLITS — `category:individual`
splits a daughter beside it, swarms shed a child), `min_swarm_size`, `merge_radius` (two same-species
swarms within this distance FUSE), `swarm_radius` (visual/strike spread). Bigger swarms = fewer, denser
hunt decisions (one swarm = one target choice); smaller = more, more-distributed coverage.

**Predator clustering — the nest-found distance dial** (`Tuning.nest_found_dist_min/max`, default 2..6).
Daughter wasp nests are founded this many Chebyshev rings from the parent (`findEmptyCellNear`,
`nests.go`). Too small → every hive's patrol overlaps the SAME prey disc (co-located swarms over-serve the
nearest prey cloud and ignore the rest = "all clustered, bad hunting"); wider → territories spread and the
predators cover more prey. This — NOT `home_range` — is the real lever for the "predators bunched up"
symptom. Raise the max (and/or min) to spread hives across the arena.

## 6. GLOBAL SIM (do not retune for balance)
- `SimRate` (`match.go`) = the canonical balance anchor (sim ticks/sec of GAME time). **Never change** —
  all secs↔ticks conversions key off it.
- `call_rate` (zone.json, test zones only) = Nakama call rate, **clamped 1..60** → wall-clock speed
  (60 = 6×). Balance-neutral. 60 is the ceiling; faster headless runs need sim-step batching per call.

---

## How to use this when a population is wrong
1. **Too high / pinning a cap?** It's food-unlimited or the cull is doing the work. Cut its FOOD (§3) so
   births=deaths lands lower; raise `cull_at` so the cull stops masking it.
2. **Too low / crashing?** Raise its food (§3) or birth rate (§1), or lower predation/decay on it (§2).
   Check it's not a downstream victim (predators starve when PREY is thin — fix the prey first).
3. **Cohort crash (flatlines then drops to 0 together)?** It isn't breeding — check the birth path (§1)
   and `lifespan_spread_secs`.
4. **One species starves another?** Shared food. Give the loser more, or separate their foods.
Always change ONE dial at a time and read the 6× chart; the whole web keys off the **fly prey base**.
