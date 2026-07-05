# Zone Design: Bee Meadow (2,0 · `bee_meadow_20`)

## Overview
- **Zone ID / Grid:** `bee_meadow_20` · row 2, col 0
- **Biome / Difficulty:** meadow / coast · EASY (the gentlest zone on the map — west of the start)
- **The feel:** a sunlit flower coast. Meadows humming with bees roll west from the village road down
  to the SEA — a wild beach full of coves, driftwood and shell piles. A stream slips in from a spring
  in the north-west and wanders east into the village, splitting a quieter north band off the main
  meadow. At the heart sits Maren's bee farm — cottage, fenced apiary, a ring of flower gardens — and
  around the southern cove a tiny fishing hamlet drowses over its docks. The hook: this is where the
  player learns beekeeping (smoke → harvest → extract → craft), and the whole zone is visibly built
  out of the thing bees need — flowers.

## Connections (map)
- **E → village_21_B**: the dirt road exits at y≈124 (the village's west lane reaches (2,124) on its
  side); the STREAM exits east at y≈76 (the village declares it entering at (0,76) and feeding its
  lake). Both edges must line up.
- **W**: the sea — a natural boundary (no neighbor).
- **N (future)**: Meadow (1,0) "advanced bee stuff"; **S (future)**: cliff wall / underground row.

## Key species & ecology
- **Plants:** flowers EVERYWHERE (flower_wild/red/blue/yellow + lavender/chamomile/poppy/clover) — the
  nectar ForagePools ARE the honey economy; milkweed patches for butterflies; leaf litter in the woods.
- **Pollinators:** honeybees (nest-founded from wild hives + claimable placed boxes — never
  free-spawned, never Director-reseeded), butterflies (high).
- **Pests/predators:** wasps (2 nests at the forest edges — the raiders, GDD 9.2); dragonflies over
  the water hunting the wasps (the counterweight); NO centipedes (this is the EASY zone).
- **Ambience:** fireflies drifting along the stream (amber glow at dusk), flies/millipedes/beetles low.

## Landmarks & little features
1. **The spring pondlet (NW)** — where the stream rises; reeds, fireflies.
2. **The coves** — the west beach bitten into arcs; one tiny unreachable ISLAND offshore (a tease);
   driftwood, seashell piles, a sandcastle someone left.
3. **The big fishing lake (south-center)** — sand shore, reeds, a small dock with a moored boat.
4. **The wild hive trees** — 3 wild bee hives hanging in flower-adjacent tree clumps.
5. **The three bridges** — wood-decked road crossings over the stream.

## Structures / NPCs
- **Maren's bee farm (center-west, south of the stream):** 3-room cottage, fenced APIARY (the four
  hive tiers in a row + honey extractor + wine rack + clutter), flower-garden ring, signpost.
  **Maren (Beekeeper NPC, shop):** sells beehive_basic / smoker / bee_suit / calm_spray; buys
  honey / honeycomb / beeswax. The zone's economy anchor (D10).
- **The fishing hamlet (SW cove):** two small cottages, bridge_wood dock over the cove water with
  mooring posts, lanterns and boats; net-and-barrel clutter. No NPC yet (fishing stays backlogged —
  the village fisherman already says "Fishing's coming").

## Materials / loot
Flowers (cut), honeycomb (wild hives, breakable), seashells (piles), driftwood → wood, wild berries,
mushrooms in the forest patches. No ore (EASY zone).

## Biome composition (for the generator)
Base grass; west edge = water_deep sea strip (width varying by noise) + SAND beach band with cove
bites; stream (NW spring → east exit y=76, width 2) + big south lake + north pondlet; dirt road from
the east edge (y=124) forking to the farm + the hamlet, `smooth_paths` once; compose-in-place with
`terrain.{stream,lake,pond,shore_dress,forest,bridge}`, `garden.flower_patch`, `yard.fence_rect`,
`house` composer, `scatter`.

## Scenes (showcase)
- `scenes/scene_beach_cove.py` — a cove + the beach set + the island.
- `scenes/scene_fishing_docks.py` — the hamlet: cottages + dock + boats.
- `scenes/scene_beekeeper_cottage.py` — cottage + apiary + garden + shop (adapts scene_beefarm_woods).
- `scenes/zone_bee_meadow_20.py` — the composed zone.

## Not present
Centipedes, ore, fishing MECHANIC (docks are set-dressing until the fishing slice), crab (cut),
mead/keg (backlogged D26).
