# Plan — Finishing Bug Farmer: the foundation, the zone process and tuning (2026-10-04)

> The order of work from here to a finished game, with a repeatable process for designing, building and tuning
> each zone's ecosystem. It sits on top of [`ROADMAP.md`](../product/ROADMAP.md) (the phases) and
> [`finish-bugs-zones-items.md`](finish-bugs-zones-items.md) (the detail for bugs, behaviour, zones and items). Every
> step is reviewed by the owner; nothing is decided automatically.

## PROGRESS (newest last)
- 2026-10-04: written after the owner asked for a thorough plan with a real process for zones and tuning, and after
  the day's measurements found what is wrong underneath the bugs (below). Nothing in it is built yet.

## Where we are (2026-10-04)
- **The design document** (`docs/gdd/`): 2 sections final, 3 waiting for review, 3 in rework (world, bestiary,
  ecology), 15 drafted.
- **The review app** is built, tested and rehearsed; it is published over the items page when the owner says so.
- **Measured today, with evidence** (details: `docs/product/investigations/scaling-2026-10-04/`,
  `village-baseline-2026-10-04/`):
  1. **The server only brings to life the chunks a player has loaded.** Food sources (fruit trees, nests, milkweed,
     flowers, leaf litter) are set up when a chunk is first loaded for a player (`handlers_world.go:23-43`), and ground
     in an unloaded chunk counts as a wall for moving bugs (`state.go:607`). A player loads a 5×5 block of chunks
     (`TilemapManager.cs:63`), 25 of the village's 64. The June tuning runs used a driver that loaded all 64; every
     run since 2026-07-18 used the real client and saw about 40% of the village. That is why millipedes (all ten
     leaf-litter piles are outside the block) and carrion beetles collapsed.
  2. **The centipede breeds and starves in a loop since 2026-07-18:** a group hatched from centipede eggs starts at
     the spawn satiety (50) with no breeding cooldown, and predators breed at 32 (`brood.go:350-357`,
     `handlers_bugs.go:109`, `predation.go:880`).
  3. **The players' computers waste most of their bug time.** At ~3,300 bugs at normal speed a tick takes 27.4 ms:
     moving the bugs 17.7 (the food lookup alone 15.0, because every bug checks every piece of food in the zone),
     the hunting-strike checks 4.3, the state check 3.3, re-sorting the groups every tick 1.9. Every frame adds 3.2 ms
     to smooth every bug on screen and 3.3 ms of centipede trails, visible or not. About 23 of the 27 ms per tick are
     avoidable.
  4. **The snapshot** a joiner downloads is ~670 KB today and ~2 MB at 4× the bugs, and the computer in charge uploads
     it every 10 seconds whether anyone joins or not, because the server keeps only 20 seconds of events.

## The order of work
Each stage has a check that proves it is done. The owner reviews each stage's results in the app.

### Stage 1 — the foundation under the bugs (engineering; my work, the owner reviews the results)
1. **Whole-zone loading.** When a zone starts, the server loads every chunk and sets up every food source, nest and
   station, and bugs move against the real map everywhere (the roadmap's "zone-complete collision/loading"). The
   ecosystem is zone-wide by design: the bug simulation on the players' computers already is. Empty zones stay frozen
   until someone arrives (owner decision, 2026-09-26).
   *Done when:* a run's food counts match the zone's authored counts (29 milkweed, 185 flowers, 129 fruit trees, 7
   wasp nests, 10 litter piles for the village); Go tests; both late-join gate halves.
2. **The client's bug simulation, without waste** (identical results on every computer, so nothing about play changes):
   - one food lookup per group per tick, and food kept in a grid of cells so a lookup only checks nearby cells;
   - each group's living bugs kept in one sorted list, updated on birth and death, which the movement, the strike
     check, the state check and the snapshot all read (no re-sorting or copying every tick);
   - the state check reads the few numbers it needs straight from each bug;
   - a tick's work spread over the frames between ticks, so no frame carries a whole tick;
   - on screen: smoothing and centipede trails only for the bugs a player can see.
   *Done when:* at the 1×, 2× and 4× test sizes, the per-tick and per-frame costs are measured; the determinism replay,
   the Go tests and both late-join gate halves pass.
3. **The snapshot on demand, and small.** The server asks the computer in charge for a fresh snapshot only when a
   player joins or a computer needs to resync, and hands it over with the few events since; if no answer comes in time,
   the joiner builds the bugs from the shared seed and the drift check pulls it into step (today's first-moments path).
   Bugs are packed as plain numbers and compressed (the server passes them through untouched).
   *Done when:* no snapshot traffic while nobody joins; join size measured at each test size; both late-join gate
   halves; the deliberate-drift self-test resyncs.
4. **The centipede breeding fix:** a new or split-off group can't breed until it has eaten (a breeding cooldown at
   birth). *Done when:* Go test; no breed-starve loop in a run.
5. **The baseline again**, on the whole village: 48 game-days, three seeds. This is the real "before" picture.

### Stage 2 — the bug budget (the owner decides, from Stage 1's numbers)
How many bugs a zone may hold, from measured costs on this PC and an allowance for a slower one, plus the join size and
the server's broadcast. I bring a recommendation (a range per zone, and how it is split across species by role); the
owner sets it. Today's estimate after Stage 1: a few thousand bugs per zone, well past the ~1,000 the owner would be
happy with; Stage 1's measurements replace the estimate.

### Stage 3 — the village, the first zone through the whole process
The steps in "The zone process" below, with the tuning in "How tuning works". The village's bug list and layout follow
the review app's zone review (Part B of `finish-bugs-zones-items.md`). The behaviour work for its bugs (the combat
groundwork C1–C12 and the behaviour model) is built with it. *Done when:* the owner has played it and signed it off.

### Stage 4 — the kit, then the rest of the zones
What the village taught becomes the kit (the bench copy, the run tools, the charts, the checklists). Then the ants as the
second slice, then the zones ring by ring (roadmap Phases 2 and 3), each through the same process.

### Alongside, all the way: the design document
Sections in the order the zones need them: §01 world, §03 bestiary, §04 ecology (with the tuning bands), §05 bug
farming, §07 combat, §18 time and weather, §02 progression, then the rest. Each through the app, one at a time.

## The zone process (every zone, the same steps; each is reviewed in the app)
1. **Purpose and place:** what the zone is for, its ring and danger, its neighbours and the natural barriers between
   rings (rivers with bridges and shallows, ridges). Sign-off: the map.
2. **The bug list, with jobs:** each bug's job for the player (livestock, danger, prey, a material), where it sits in
   the food web, and the moment only it creates. From the registry.
3. **The ecosystem design.** A food-web diagram, and for each species:
   - its food and where that food is placed (its habitat);
   - how it breeds (nest, brood, eggs per trip);
   - what eats it, and what it eats;
   - its target range and character (a boom-and-bust prey, a predator that lags it, a steady decomposer);
   - its share of the zone's bug budget (Stage 2), and what the player sees.
   Sign-off: the bug list and its design.
4. **The layout:** landmarks and habitats placed to serve the food web (the zone-craft process). Habitats are where
   their food is; every species can reach its food.
5. **Build:** the zone files and the data, with the checks (barriers, crossings, every habitat reachable, food counts).
6. **Tune** (below).
7. **Pressure:** test players who over-hunt, over-farm and hoard; how fast collapses come, what warns first, how
   things come back. This shapes the Ecologist's warnings and quests.
8. **The owner plays it and signs it off.**

## How tuning works
**What "tuned" means:** every species stays in the target range set in step 3, with the character set there (cycles
are good; a flat line at a cap is not; a crash is fine if it comes back), over 48 game-days, with top-ups only as a
rare safety net.

**The rig:** the zone's bench copy (never the real save), the whole zone loaded (Stage 1), the real game client in
charge at the zone's speed, 48 game-days per run, a fixed seed, and two more seeds to confirm a result.

**Reading a run** (all on charts in the app):
- population against the target range;
- births by source: is it keeping itself going, or living on top-ups?
- deaths by cause: what limits it (hunger, predators, old age, players)?
- food against population (the food loops): is it food-limited?
- cost: the bug budget still holds.

**The order:** first the structural breaks (anything that can't work: food out of reach, instant breeding, frozen
habitats), then from the bottom of the food web up: food supply → plant-eaters → predators → scavengers.

**The levers, per species:**
- food: amount, regrowth, placement;
- breeding: eggs per trip, brood size, hatch time, cooldowns;
- death: lifespan, starvation time;
- predation: hunting speed, strike cooldown, kills per strike;
- space: habitat size and placement.
Caps and top-ups are the safety net, not the tuning.

**The method:** one change per run, each logged in `docs/product/ecology/ecology_tuning_log.md` with its chart and
what it showed. The owner sees each batch in the app.

**For the village, the starting point:**
- the settings shipped today, which are the June 19 rebalance (`ecology_tuning_log.md`, "Phase-2 rebalance r2-r6 →
  BAKED"): flies about 112, butterflies about 45, millipedes about 19, wasps about 16, centipedes about 4, beetles
  about 3 (short of carcasses, accepted then). Those runs loaded the whole zone and had the server decide predation;
- then adjusted for what changed since: predation is decided on the players' computers, centipedes live in packs, the
  village starts populated, and breeding comes from brood instead of instant growth.

## What the owner is asked, and when
- **Now:** read this plan; say "publish" when the items page is closed on other devices (the app then holds this plan
  and every review).
- **After Stage 1:** the bug budget (Stage 2), with the numbers.
- **Per zone:** the map, the bug list and its design, the tuning results, and the final play — each in the app.

## Risks
| Risk | How it's handled |
|---|---|
| A performance change breaks sync between players | every change is result-identical by design and passes the determinism replay and both late-join gate halves before it is kept |
| Whole-zone loading makes the server slower | the server measured 0.2–0.4 ms per tick; loading 64 chunks of data at zone start is small; measured after the change |
| Tuning drifts or chases noise | three seeds per result, one change per run, every run logged |
| The owner's review load | batches in the app, a stage at a time |
