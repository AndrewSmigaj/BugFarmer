# The village's bug life before any changes — 48-game-day baseline, 2026-10-04

Part of S2 in [`docs/plans/finish-bugs-zones-items.md`](../../../plans/finish-bugs-zones-items.md): the "before" picture
for the first slice (the village's bug life). No players, no changes: the village as shipped, on its bench copy.

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

1. **Flies and wasps make a real predator-and-prey cycle.** Fly numbers surge (peaks of about 300–400 around days 7,
   22 and 37) and crash. Wasps rise after them and fall when the flies are gone. Flies breed from their own brood
   (only 7% of births are top-ups), and their main cause of death is wasps. Wasps keep themselves going entirely from
   brood and nests. This is the living, swinging kind of ecosystem decided on 2026-10-03.
2. **Centipedes churn.** They breed fast and starve fast: about 9,850 born and 9,850 starved, averaging 38 alive. That
   is the known break where predators can breed the moment they appear (born at 50 satiety against a breeding
   threshold of 32), already on the plan's fix list.
3. **Millipedes and carrion beetles only survive on top-ups.** 210 of 254 millipede births and 72 of 112 beetle births
   are the director topping them up, and every one starves. They are not part of a working cycle yet.
4. **Butterflies sink slowly** from 184 to a low, fairly steady 20–40, dying mostly of hunger and old age.
5. **Nothing hunts the wasps, centipedes, millipedes or beetles.** Their only cause of death is starvation.

## Costs over the same run
- Server: 0.2 ms per tick on average; worst tick 76 ms (start-up); none over 100 ms.
- The snapshot the computer in charge uploads (most of what a late joiner downloads): about 206 KB on average,
  574 KB at most, with only about 200 bugs. It gets bigger with more bugs; worth measuring at 2× and 4×.
- **The client's cost per tick grows over time:** from 0.7 ms to about 5.7 ms with roughly the same number of bugs.
  Over the same days the pile of rotten fruit grows from 3 pieces to about 700 (`RESSTATS`). This fits the
  scaling study's suspect (every bug scans every piece of food each tick). The client's memory also climbs, from 38 to
  113 MB; not yet explained.

## Lessons for the village slice (my reading, for the design work)
- The flies-and-wasps loop already behaves the way you asked for; the slice should keep it.
- The centipede needs the breeding fix before its population means anything.
- Millipedes and carrion beetles need a real food source and a reason to die other than hunger, or they stay
  propped-up decorations.
- Butterflies need their low steady level checked against their nectar and milkweed (the food-loop charts).
- The rotten-fruit pile grows without limit over the run; it is already on the BACKLOG
  ("bound the ground-item pile"), and it now matters for the players' computers too.
