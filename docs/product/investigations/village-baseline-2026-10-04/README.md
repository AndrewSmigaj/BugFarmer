# The village's bug life before any changes — 48-game-day baseline, 2026-10-04

Part of S2 in [`docs/plans/finish-bugs-zones-items.md`](../../../plans/finish-bugs-zones-items.md). No players, no
changes: the village as shipped, on its bench copy.

> **Correction (2026-10-04, later the same day): this run simulated only about 40% of the village.** The server sets
> up food (fruit trees, nests, milkweed, flowers, leaf litter) only in chunks a player has loaded
> (`handlers_world.go:23-43`), and ground in an unloaded chunk counts as a wall for moving bugs (`state.go:607`). The
> headless client loads a 5×5 block of chunks around itself (`TilemapManager.cs:63`), so 25 of the village's 64 chunks
> were alive. The log matches exactly: 11 of 29 milkweed sites, 165 of 185 flowers, 48 of 129 fruit trees, 3 of 7
> wasp nests, and none of the 10 leaf-litter piles. The old tuning runs (June) used a driver that loaded all 64
> chunks (`tools/sync-harness/Program.cs:56`), so they and this run measured different worlds. The millipede and
> carrion-beetle results below come from that: their homes are outside the loaded block, where they were frozen
> beside food that never existed. This run is NOT the "before" picture of the village; the fix (load and set up the
> whole zone) comes first, then the baseline is run again. Two statements below were also wrong and are corrected in
> place: centipedes, not wasps, killed the most flies, and the rotten-fruit pile levels off (about 450–710 from
> day 19) instead of growing without limit.

## How it was run
- `python3 tools/ecology/scaling_study.py --configs bench_baseline --duration 6720` on `bench_village` (a copy of
  `village_21_B`'s authored files): 6,720 real seconds at 6× speed = 47 game-days, seed 1337.
- The real game client, headless, in charge of the zone, its clock running at the zone's speed (`-timescale 6`, new
  tonight). It reached 60.6 ticks a second throughout, so the bugs' own hunting and eating kept pace with the server.
  Earlier real-client runs didn't (see `docs/product/investigations/scaling-2026-10-04/`).
- Charts: `tools/_generated/ecology_charts/bench_village/current/` (population, births and deaths by cause, food loops,
  cost). Raw data (git-ignored): `tools/_generated/scaling/2026-10-04-baseline48d/`.

## What it shows
**Totals over 47 game-days:**

| Species | Born (from brood / nest / top-ups) | Died (starved / eaten / old age) | Average alive |
|---|---|---|---|
| Common fly | 5,372 (4,236 / – / 360) | 5,337 (2,157 / 3,180 / 0) | 81 |
| Village wasp | 811 (535 / 276 / 0) | 784 (784 / 0 / 0) | 38 |
| Garden centipede | 9,876 (9,818 / – / 14) | 9,851 (9,851 / 0 / 0) | 38 |
| Meadow butterfly | 722 (368 / – / 96) | 711 (446 / 57 / 208) | 30 |
| Millipede | 254 (0 / – / 210) | 251 (251 / 0 / 0) | 4 |
| Carrion beetle | 112 (4 / – / 72) | 109 (109 / 0 / 0) | 3 |

(The rest of the births are the start-up spawn.)

1. **Flies and wasps make a real predator-and-prey cycle** inside the loaded block. Fly numbers surge (peaks of about
   300–400 around days 7, 22 and 37) and crash. Wasps rise after them and fall when the flies are gone. Flies breed from
   their own brood (only 7% of births are top-ups); they die to predators (centipedes 1,743 kills, wasps 1,437) and
   hunger. Wasps keep themselves going entirely from brood and nests (3 of the 7 nests were loaded).
2. **Centipedes churn.** They breed fast and starve fast: about 9,850 born and 9,850 starved, averaging 38 alive. A
   group hatched from centipede eggs with no pack nearby starts a new group at the spawn satiety (50) with no breeding
   cooldown, and predators breed at 32 or more (`brood.go:350-357`, `handlers_bugs.go:109`, `predation.go:880`), so it
   breeds at once and starves. This came in with the centipede rework of 2026-07-18 (`05cca298`).
3. **Millipedes and carrion beetles only survive on top-ups** in this run, because their homes were outside the loaded
   block (see the correction). Millipedes eat only leaf litter, and all ten litter piles were unloaded; in June, with the
   whole zone loaded, they kept themselves going.
4. **Butterflies sink slowly** from 184 to a low, fairly steady 20–40, dying mostly of hunger and old age.
5. **Nothing hunts the wasps, centipedes, millipedes or beetles.** Their only cause of death is starvation.

## Costs over the same run
- Server: 0.2 ms per tick on average; worst tick 76 ms (start-up); none over 100 ms.
- The snapshot the computer in charge uploads (most of what a late joiner downloads): about 206 KB on average,
  574 KB at most, with only about 200 bugs. It gets bigger with more bugs; worth measuring at 2× and 4×.
- **The client's cost per tick grows over time:** from 0.7 ms to about 5.7 ms with roughly the same number of bugs.
  Over the same days the pile of rotten fruit grows from 3 pieces to between about 450 and 710 (`RESSTATS`), where it
  levels off. This fits the scaling study's finding (every bug scans every piece of food each tick). The client's memory also climbs, from 38 to
  113 MB; not yet explained.

## Lessons for the village slice (my reading, for the design work)
- The flies-and-wasps loop already behaves the way you asked for; the slice should keep it.
- The centipede needs the breeding fix before its population means anything.
- Millipedes and carrion beetles need a real food source and a reason to die other than hunger, or they stay
  propped-up decorations.
- Butterflies need their low steady level checked against their nectar and milkweed (the food-loop charts).
- The rotten-fruit pile settles at several hundred pieces; its cost on the players' computers goes away with the
  food-lookup fix.
- **First of all:** load and set up the whole zone, then run this baseline again.
