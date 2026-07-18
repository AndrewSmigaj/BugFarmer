# village_21_B — Bug Lifecycle Audit (A)

Assessment only, no code changed. Every load-bearing claim is traced to `file:line` in the
real Go server / data / sprite files. Line numbers are from the tree at audit time.

## Roster verification (confirmed against `nakama/data/zones/village_21_B/zone.json` → `bug_spawning.species_caps`)

Six roster species, matching the stated ground truth:

| species | initial | max swarms | max_pop | director bands | notes |
|---|---|---|---|---|---|
| fly_common | 78 | 200 | 1500 | min 12 / low 40 / high 400 | 16 spawn_areas |
| butterfly_meadow | 30 | 140 | 800 | min 10 / low 30 / high 250 | 6 spawn_areas |
| wasp_common | 0 | 12 | 120 | min 3, **max_nests 7** | nest-only; 7 spawn_areas (dead — see gaps) |
| centipede_garden | 16 | 40 | 140 | min 3 | 6 spawn_areas |
| millipede | 16 | 250 | 200 | min 3 | 2 spawn_areas |
| beetle_carrion | 12 | 40 | 140 | min 2 | 2 spawn_areas |

Also present in zone chunks (counted by scanning `chunk_*.json` occupant ids): **7 `wasp_nest`**,
**4 `beehive_basic`** (bee_honey is NOT in the roster — a dormant hook), **7 `compost_bin`**,
**29 `milkweed`**, **10 `leaf_litter`**, **0 `manure_pile`**, **0 `rotten_fruit`** occupants
(rotten fruit is a windfall ground item from 67 apple / 25 cherry / 12 orange / 25 plum trees, not
a placed occupant). `initial_carrion`: 3 `dead_millipede` seeds near (188-198, 236-241) — the
day-1 carrion bootstrap for beetles + carrion-breeding flies (`match.go:1799 seedInitialCarrion`).

## How the lifecycle engine actually decides things (the load-bearing mechanics)

- **Reproduction is driven by `attractions_by_phase["reproducing"]`, NOT `breeding_plants`.** The swarm's
  food target comes from `GetCurrentAttractions` which reads only `AttractionsByPhase[phase]`
  (`modules/entities/swarm.go:439-447`). `breeding_plants` is declared (`species.go:66`) but read
  **nowhere** in logic — the only other mention calls it "Dropped" (`entities.go:206-207`). **DEAD CONFIG.**
- **Reproduction requires a DEPLETABLE source.** Meter fills only when `swarm.TargetFoodDepletable`
  is true (`match.go:1430`, "v1: breeding requires a depletable source"), and reproducing-phase food
  hits are filtered to depletable-only (`match.go:1332-1340`). Depletable = ground items/carrion
  (`resource_query.go:78`), filled stations (`:96`), milkweed host-plants + flower/litter forage
  pools with stock (`:108-118`). Plain flora is non-depletable.
- **`reproduceSwarm` splits three ways** (`match.go:73-160`):
  - `Category != "individual"` AND not a nest species → **visible brood** via `layIntoBrood` (`:90-97`).
  - `Category == "individual"` (centipede) → mints a **new solo swarm beside the parent** (`:119-151`); NO brood.
  - Nest species (wasp) → excluded here; breeds through the nest deposit path instead (`:86-90` comment).
- **`layIntoBrood`** (`brood.go:71-102`) resolves the source: station / milkweed host-plant / rotten-fruit
  or carrion ground-pile — and has a **catch-all fallback** (`:90-98`) that lays a visible clutch at the
  swarm's own cell for anything with no recognized food-source spot. So any non-individual, non-nest
  swarm that reproduces DOES get a visible brood.
- **`processBroods`** (`brood.go:104-164`) climbs one stage per `BroodEggMatureTicks/transitions`;
  `broodPupates` = "species has a `pupa_sprite_id`" (`brood.go:250-253`). So egg→larva→**pupa**→adult
  for species with a pupa sprite; egg→larva→adult otherwise. Final transition hatches via
  `growSwarm`/`spawnSwarmAt` (`brood.go:302-367`).
- **Nest lifecycle** (`nests.go`): occupant scanned at chunk-load → `registerNestAt`/`nestSpawnResident`
  staffs a resident patrol (`:92-139`); resident hunts, homes when sated and `depositBrood` lays 1 egg
  into the nest's visible BroodState (`predation.go:206-211`, `nests.go:223-245`); `processBroods`
  matures + hatches into the resident; thriving colonies split daughter nests up to `max_nests`
  (`processNestFounding :291-404`); dead colonies recover only if live prey is in range
  (`processNests :170-210`). All slow-clock processors are wired at `match.go:1237-1241,1515,1523-1524`.
- **Spawn paths:** initial (`spawnInitialSwarms match.go:1743`, nest species skipped `:1764`), continuous
  immigration (`checkContinuousSpawning :1997`, nest species skipped `:2019`), director anti-extinction
  reseed (`ecology_director.go:52`, nest species skipped), nest founding/recovery (wasp only).
- **Death:** `DeathTick = born + lifespan_secs ± spread` (`handlers_bugs.go:51-64`); `processNaturalDeath`
  culls at that tick and drops the species carcass (`match.go:2099-2129` → `killBugsNaturally`
  `handlers_combat.go:281-362`); `processStarvation` culls starving swarms + drops carcasses
  (`match.go:2151`). All six carcass items exist in `items.json` (`dead_fly/butterfly/wasp/centipede/
  millipede/beetle`, food_value 10, tag `carrion`). All 6 adult + all 16 egg/larva/pupa sprites exist
  under `Assets/Resources/Bugs|Objects/`.

## Per-species lifecycle table

| species | SPAWN | BREED source (works here?) | STAGES (pupates? sprites used?) | FOOD (present?) | DEATH | VERDICT |
|---|---|---|---|---|---|---|
| **fly_common** | initial 78 + continuous + director reseed (`match.go:1774,2046`; `ecology_director.go:53`) | `attractions_by_phase.reproducing = [rotten_fruit, compost_bin, dead_millipede]`, all depletable → visible brood (station / ground-pile). Sources present: windfall from fruit trees + carrion (compost bins start empty, filled by beetles) | egg→larva→**pupa**→adult; pupates (`fly_pupa`); `fly_eggs/fly_larvae/fly_pupa` all rendered by the brood engine | feeding = rotten_fruit / compost_bin / dead_millipede — present (windfall + carrion; compost after fill) | lifespan 5500±1260s → `dead_fly` | **COMPLETE** |
| **butterfly_meadow** | initial 30 + continuous + reseed | `reproducing = [milkweed]` (host-plant, depletable). **29 milkweed present** → host_plant brood | egg→caterpillar→**chrysalis**→adult; pupates (`butterfly_chrysalis`); all 3 sprites used | feeding = flowers; abundant (130 wild + others) | 3360±1120s → `dead_butterfly` | **COMPLETE** |
| **wasp_common** | initial 0; **7 placed `wasp_nest` staffed at chunk-load** (`registerNestAt`); NO free spawn (nest-only) | Nest deposit path: sated resident homes → `depositBrood` (1 egg into nest BroodState) → matures → hatches into resident. Prey present (flies/butterflies) | egg→grub→**pupa**→adult **in the nest**; pupates (`wasp_pupa`); `wasp_eggs/wasp_grubs/wasp_pupa` used | predation prey = fly/butterfly/bee; flies+butterflies present (bee prey inert — no bees) | 9450±2520s → `dead_wasp` | **COMPLETE** |
| **centipede_garden** | initial 16 + continuous + reseed | Well-fed carnivore path: `processPredatorBreeding` (`predation.go:885-909`) → `reproduceSwarm` individual branch → **new solo swarm beside parent** (`match.go:119-151`). Reproduces YES, but NO brood | **NO visible stages.** `egg_sprite centipede_eggs` + `larva_sprite centipede_larvae` + `larva_name/brood_label` **UNUSED** — individuals are excluded from the brood engine (`match.go:87-90`, "get the clutch when Phase 3"). No pupa | predation prey = fly_common; present | 6300±1680s → `dead_centipede` | **HALF-WORKING** |
| **millipede** | initial 16 + continuous + reseed | `reproducing = [leaf_litter]`; leaf_litter registers a depletable forage pool (`handlers_farming.go:1741-1756`). **10 present** → visible ground-pile brood at own cell (fallback) | egg→larva→adult; **no pupa by design** (no `pupa_sprite_id` → `broodPupates` false); `millipede_eggs/millipede_larvae` used | feeding = leaf_litter; present (10 pools) | 5040±1260s → `dead_millipede` | **COMPLETE** (data desc wrong — see gaps) |
| **beetle_carrion** | initial 12 + continuous + reseed + `initial_carrion` bootstrap (3 dead_millipede) | `reproducing = [dead_fly…dead_beetle]` (carrion ground items, depletable) → visible ground-pile brood at the carcass | egg→grub→**pupa**→adult; pupates (`beetle_pupa`); all 3 sprites used | feeding = all `dead_*` carcasses; seeded carrion + ongoing bug deaths. `produces_compost` → fills compost bins → fly food | 5040±1260s → `dead_beetle` | **COMPLETE** |

## Dormant bees (`beehive_basic` ×4) — INERT but registered

`beehive_basic` is one of `bee_honey.predation.nest_occupants_extra`. At chunk-load `initNestsInChunk`
→ `speciesForNestOccupant` resolves it to `bee_honey` with `isBox=true`, so `registerNestAt(dormant=true)`
creates 4 **empty** NestStates (`nests.go:75-104`). But `bee_honey` is **not** in the zone's
`species_caps`, so: no initial spawn, no continuous immigration, no director reseed, no wild
`bee_hive_wild` placed (0), and no existing bee colony that could daughter-found into a box
(`findClaimableBox` needs a live parent colony `nests.go:353-358`). Result: **the 4 hives register
dormant and are never staffed** — bees never populate village_21_B. It is a wired-but-inert future hook,
exactly as suspected. (Harmless: `processNests` leaves a never-founded box dormant — `nests.go:180-183`.)

## GAPS / HALF-WORKING / DEAD-CONFIG / INCONSISTENCIES (each with file:line)

**Severity ordered.**

1. **centipede visible lifecycle is unwired (HALF-WORKING).** Centipede reproduces (well-fed →
   new solo swarm, `predation.go:885-909` + `match.go:119-151`), but its authored brood assets
   `egg_sprite_id=centipede_eggs`, `larva_sprite_id=centipede_larvae`, `larva_name="young"`,
   `brood_label="Young"` (`species.json` centipede_garden) are **never used** — `reproduceSwarm`
   excludes `Category=="individual"` from `layIntoBrood` (`match.go:87-90`), so no centipede brood is
   ever created. The PNGs `Objects/centipede_eggs.png` + `Objects/centipede_larvae.png` exist but are
   orphaned. The code comment marks this a deferred "Phase 3" feature. So: reproduction works, the
   egg→larva stages are decorative/unimplemented.

2. **`breeding_plants` is global DEAD CONFIG.** Declared at `species.go:66`, read by no logic (only the
   "Dropped" note at `entities.go:206-207`). Reproduction is entirely driven by
   `attractions_by_phase["reproducing"]` (`swarm.go:439-447`). So `fly_common.breeding_plants =
   [rotten_fruit, manure_pile, dead_millipede]` and `butterfly_meadow.breeding_plants=[milkweed]` are
   inert. Note the fly value even lists `manure_pile`, which is (a) not in its actual reproducing
   attractions and (b) has 0 placements in this zone — a double phantom. Misleading to anyone reading
   the data to reason about breeding.

3. **`wasp_soldier.nest_occupant="wasp_nest"` is unreachable DEAD CONFIG.** `speciesForNestOccupant`
   iterates species in **sorted** key order and returns the first match (`nests.go:37-55`).
   `wasp_common` sorts before `wasp_soldier` and both claim `wasp_nest`, so `wasp_common` always wins;
   `wasp_soldier` can never own a nest. (wasp_soldier is absent from village_21_B entirely, and since
   its only spawn route would be a nest, it is globally unreachable except via a director `cull_with`
   pulse or a direct spawn.) Confirms the stated suspicion.

4. **wasp_common's 7 `spawn_areas` in zone.json are DEAD CONFIG.** Nest species are skipped in BOTH
   `spawnInitialSwarms` (`match.go:1764`) and `checkContinuousSpawning` (`match.go:2019`), and nests are
   located by scanning occupant cells, not spawn areas. So the 7 authored wasp circles are never
   consulted. (Likely intended as visual hints for where the 7 `wasp_nest` occupants sit.)

5. **millipede description is a copy-paste of the beetle's and is inaccurate (data INCONSISTENCY).**
   `millipede.description` = "A slow, gentle detritivore. Trundles between corpses, eating the fallen
   and packing the rot into compost. Harmless." — but millipede's attractions are `leaf_litter` (not
   corpses) and it has **no** `produces_compost` (only `beetle_carrion` does, `species.json`). The
   description belongs to the beetle; millipede actually eats forest-floor litter and makes no compost.

6. **beehive_basic ×4 are inert** (detailed above) — registered dormant, never staffed; bees never
   appear. Expected "future-bees hook", but currently 4 no-op NestStates.

7. **Minor bootstrap dependency (not a bug):** compost bins start `Fill=0` and only count as fly food
   once filled (`resource_query.go:90` skips `Fill<=0`). Bins fill from beetle `produces_compost`
   deposits (`match.go:1459-1465`) or player deposits. Until then, flies breed/feed on windfall +
   carrion. The recycle loop (bug deaths → carrion → beetles → compost → fly food) closes on its own,
   but a fresh zone's compost bins are not immediately fly food.

## What USES its stage sprites/labels vs decorative-only

- **Fully used (brood engine renders every stage):** fly (egg/larva/pupa), butterfly
  (egg/caterpillar/chrysalis), beetle (egg/grub/pupa), wasp (egg/grub/pupa, in-nest), millipede
  (egg/larva; no pupa by design).
- **Decorative-only (files exist, engine never creates the brood):** centipede `centipede_eggs` +
  `centipede_larvae` + its `larva_name`/`brood_label` (item #1 above).
- **Non-pupating by design (no orphan):** millipede + centipede have no `pupa_sprite_id`, so the
  ladder correctly runs egg→larva→adult / (centipede: none).

## Net verdict

Roster of 6 confirmed. **4 species COMPLETE** (fly, butterfly, wasp, beetle) with full, wired,
sprite-backed lifecycles including the correct pupa step. **1 HALF-WORKING** (centipede: reproduces
but its egg/larva stages are unimplemented decorative assets). **1 COMPLETE-with-a-data-defect**
(millipede: lifecycle works; its description is the beetle's and is wrong). **Bees inert.** Plus four
pieces of dead config (`breeding_plants` everywhere, `wasp_soldier` nest, wasp `spawn_areas`) that
mislead anyone reading the data but don't break the running sim.
