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
- **N (future)**: Meadow (1,0) "advanced bee stuff" — the open corridor between the north forest
  stands is the eventual route.
- **S (future) → Ant Colony (3,0, underground)**: the whole south band FORESHADOWS it — ANT COUNTRY:
  torn dirt ground spreading up from the edge, ant mounds, and mineable earth outcrops with rocky
  cores (dirt aprons + stone fill + common ore veins). The actual connection lands when the ant
  colony zone is built.

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
2. **The coves** — the west beach bitten into arcs, dressed with a WRACK LINE (shells, driftwood,
   starfish, the odd message bottle concentrated along the tideline) and dune grass at the seam;
   one tiny unreachable ISLAND offshore with a message bottle you can see but not reach.
3. **The SHIPWRECK (mid-coast cove, y≈141)** — a broken hull half-buried at the waterline,
   driftwood strewn around it; striped buoys float off the cove mouths.
4. **The picnic spot (north beach, y≈206)** — a beach parasol, a bench, someone's shell pile;
   a sandcastle further down the sand.
5. **Dragonfly Lake (south-center)** — sand shore, reeds, lily pads, a stub pier + boat.
6. **The quiet bench (NE pond)** — facing the water, under the evening fireflies.
7. **The wild hive trees** — wild bee hives in flower-adjacent tree clumps (plus one hanging in
   an oak just OUTSIDE Maren's fence — the kept boxes inside, the free colony without).
8. **The three bridges** — wood-decked road crossings over the stream (+ Gullwash's footbridge).
9. **THE HONEY GLADE** — the flower-filled clearing between the two north forest stands, a wild
   hive at its heart; **THE MUSHROOM HOLLOW** — the damp clearing west of it (mushrooms, litter,
   ferns — millipede country).
10. **THE ROCKY GORGE (east stream exit)** — the stream cuts between two mineable stone masses
    pressed against its banks: common ore veins + hand-set silver, gold and a ruby; loose bank
    stones trace the waterline toward the village edge.
11. **ANT COUNTRY (the south band)** — torn dirt, mounds, two earth outcrops with rocky cores;
    a warning sign ("the ground hums here") for the colony below.

## Named places (on the signs)
**Gullwash Landing** (the split-shore fishing hamlet on the inlet) · **Dragonfly Lake** ·
**Maren's Bee Farm**. Junction signs carry directions; the entrance sign names the zone.

## Structures / NPCs
- **Maren's bee farm (center-west, south of the stream):** 3-room cottage, fenced APIARY (the four
  hive tiers in a row + honey extractor + wine rack + clutter), flower-garden ring, signpost.
  **Maren (Beekeeper NPC, shop):** sells beehive_basic / smoker / bee_suit / calm_spray; buys
  honey / honeycomb / beeswax. The zone's economy anchor (D10).
- **Gullwash Landing (the SW inlet):** a SPLIT-SHORE hamlet on a true arm of the sea (open water
  from the docks past the fairway buoys — the old landlocked bay was a bug). One home on each
  shore, DOORS FACING THE WATER (the south home uses the north-door cottage plan); a dock off
  each shore, a plank footbridge over the east narrows, the catch and gear split between the two
  quays (drying racks, crate line, nets, lobster pots), laundry + a shared fire behind. No NPC
  yet (fishing stays backlogged — the village fisherman already says "Fishing's coming").

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
