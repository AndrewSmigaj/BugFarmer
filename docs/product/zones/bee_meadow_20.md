# Zone Design: Bee Meadow (2,0 · `bee_meadow_20`)

## Overview
- **Zone ID / Grid:** `bee_meadow_20` · row 2, col 0
- **Biome / Difficulty:** meadow / coast · EASY (the gentlest zone on the map — west of the start)
- **The feel:** a sunlit flower clearing in a WOODED coast (owner 2026-07-06 + forest.md
  §Zone-scale balance: "a huge meadow surrounding the bee farm but everything else should be
  more wooded"). The great meadow rings Maren's farm; woods band the east, south and north;
  the RIVER runs from a flared sea-mouth in the north-west, under the road bridge, through
  the rocky gorge, east into the village. A wild cove beach walls the west, and the fishing
  hamlet drowses over its inlet in the south-west. The hook: this is where the player learns
  beekeeping (smoke → harvest → extract → craft), and the whole zone is visibly built out of
  the thing bees need — flowers.

## Connections (map)
- **E → village_21_B**: the dirt road exits at y≈124 (the village's west lane reaches (2,124) on its
  side); the STREAM exits east at y≈76 (the village declares it entering at (0,76) and feeding its
  lake). Both edges must line up.
- **W**: the sea — a natural boundary (no neighbor).
- **N (future)**: Meadow (1,0) "advanced bee stuff" — the open corridor between the north forest
  stands is the eventual route.
- **S (future) → Ant Colony (3,0, underground)**: NO ant content in THIS zone (owner, 2026-07-06:
  "there is no ant colony in the zone" — the colony is the neighbor zone, mostly underground
  tunnels). The south band is a terrain GRADIENT ONLY: the meadow "start[s] getting dirty and
  rocky on a gradient, not suddenly having the dirt wall" — clean grass → dirt-speckled →
  mostly dirt → rockier at the edge, with mineable dirt masses + rocky cores embedded in the
  dirtiest band. Crossing the zone line lands mid-gradient (C12).

## Key species & ecology
- **Plants:** flowers EVERYWHERE (flower_wild/red/blue/yellow + lavender/chamomile/poppy/clover) — the
  nectar ForagePools ARE the honey economy; milkweed patches for butterflies; leaf litter in the woods.
- **Pollinators:** honeybees (nest-founded from wild hives + claimable placed boxes — never
  free-spawned, never Director-reseeded), butterflies (high).
- **Pests/predators:** wasps (2 nests at the forest edges — the raiders, GDD 9.2); dragonflies over
  the water hunting the wasps (the counterweight); NO centipedes (this is the EASY zone).
- **Ambience:** fireflies drifting along the stream (amber glow at dusk), flies/millipedes/beetles low.
- **Future — ants forage in from the SOUTH** (owner, 2026-07-06: "the ants will be coming from
  the south, they mostly collect dead bugs and food"): the gradient band stays walkable
  (lanes between the masses/woods), and the south-meadow WILD FRUIT pair (≈(100,44)) drops
  windfalls near the band — carrion + food on their path without any ant content in-zone.
- **Wild fruit clumps** (2026-07-06): corridor apple+cherry (≈150,212), road-fork plum pair
  (≈129,129), south-meadow orange+apple (≈102,43) — blossom forage for bees, windfalls for
  flies/ants, snacks for travelers.

## Landmarks & little features
1. **THE RIVER MOUTH (NW coast)** — the river reaches the SEA through a flared, reeded
   mouth in the north beach (owner 2026-07-06: "the river should flow to the sea not a
   little pond next to the sea" — the old spring pondlet is gone). Fireflies still drift
   the lower banks at dusk. The river runs sea → gorge → village, width 4 at the mouth,
   3 along the run (C17).
2. **The coves** — the west beach bitten into arcs, dressed with a WRACK LINE (shells, driftwood,
   starfish, the odd message bottle concentrated along the tideline), a 2-3-cell DUNE BELT with
   wind-blown sand hummocks, sandstone HEADLAND rock on the convex points between coves, and a
   TIDE POOL (y≈199) cupped in the dry sand; one tiny unreachable palm ISLAND offshore (organic
   two-blob shape) with a message bottle you can see but not reach.
3. **The SHIPWRECK (mid-coast cove, y≈141)** — a broken hull at the waterline beside THE ROCK
   SHE STRUCK (a sandstone head), her cargo raked down-tide: crates, barrels, broken timbers.
4. **The picnic spot (north beach, y≈206)** — a beach parasol, a bench, someone's shell pile,
   last night's campfire ring with a log seat; a sandcastle further down the sand.
5. **Dragonfly Lake (south-center)** — sand shore, reeds, lily pads, a stub pier + boat.
6. **The quiet bench (NE pond)** — facing the water, under the evening fireflies.
7. **The wild hive trees** — wild bee hives in flower-adjacent tree clumps (plus one hanging in
   an oak just OUTSIDE Maren's fence — the kept boxes inside, the free colony without).
8. **The three bridges** — wood-decked road crossings over the stream (+ Gullwash's footbridge).
9. **THE HONEY GLADE** — the flower-filled clearing between the two north forest stands, a wild
   hive at its heart; **THE MUSHROOM HOLLOW** — the damp clearing west of it (mushrooms, litter,
   ferns — millipede country).
10. **THE ROCKY GORGE (east river exit)** — the river cuts a rocky THROAT: four mineable
    stone masses flanking BOTH banks the whole stretch (owner 2026-07-06: the gorge must
    surround the river), stone lips + gap-toothed rim boulders over the water, a wide scree
    apron, doctrine ore veins (commons + short deep silver/gold/ruby in the cores), and
    J. Halloway's abandoned CLAIM huddled at the north mass's foot ("Back by spring").
11. **THE SOUTH GRADIENT (the south band)** — REBUILT 2026-07-06 per the owner correction:
    a noise-warped gradient (grass → speckle flecks → dirt tongues → near-solid dirt with
    stone-grit mottling; the frontier meanders ±7 cells, never a level line), five mineable
    dirt-block masses embedded in the dirtiest part (size-varied ~6:1, one overlapping
    cluster; shovel shells → ragged stone cores → doctrine veins at a measured 10-22%;
    iron + the ONE deep silver in the anchor), torn-ground rubble flecks, dry flora
    (tall-grass drifts, dead bushes, tumbleweed, two skeletal trees), and PATCHY WOODS
    with real clearings holding the band's east (village forest recipe + lone-tree fray).
    No ants, no dig narrative (C12).
12. **THE WAYSTONE (road entrance, ≈(243,118))** — the approach landmark: an old standing
    stone on the last rise, a bench, flowers let grow around it.
13. **THE HUMMING OAK (roadside, ≈(206,118))** — two oaks over a wild hive in deep grass
    just north of the road: the mid-route beat you hear before you see.

## Named places (on the signs)
**Gullwash Landing** (the split-shore fishing hamlet on the inlet) · **Dragonfly Lake** ·
**Maren's Bee Farm**. Junction signs carry directions; the entrance sign names the zone.

## Structures / NPCs
- **Maren's bee farm (center-west, south of the river):** 4-room cottage — bedroom
  (honeycomb rug, beeswax candle), kitchen (honey-jar shelf), fireplace living room with the
  straw skep, and the BREWING BACKROOM: extractor + wine rack + honey shelf + mead keg ALL
  INSIDE (owner 2026-07-06 / C19 — off the lawn). Fenced APIARY: the bee-STATION row (3 small
  + 1 large — the only two hive placeables now, owner 2026-07-06) on its dirt strip, three
  planted bed rows (premium lavender/chamomile), the INTERRUPTED INSPECTION vignette, compost
  line, waterer; honey crates staged on the lane. Wild hive in an oak just outside the fence.
  **Maren (Beekeeper NPC, shop):** sells bee_station_small / bee_station_large / smoker /
  bee_suit / calm_spray; buys honey / honeycomb / beeswax. The zone's economy anchor (D10).
- **Gullwash Landing (the SW inlet):** a SPLIT-SHORE hamlet on a true arm of the sea (open water
  from the docks past the fairway buoys; the banks carry independent noise and the mouth flares —
  never a mirrored pipe). One home on each shore, DOORS FACING THE WATER (the south home uses
  the north-door cottage plan); a dock off each shore, a plank footbridge over the east narrows,
  the catch and gear split between the two quays (drying racks, crate line, nets, lobster pots).
  The DOMESTIC layer (2026-07-06): worn shore lanes linking each quay to the footbridge, the
  fisher's log pile + chopping stump inland of his cottage, the south home's berry-row kitchen
  garden below its laundry line, the shared WELL, and log seats pulled up to the fire — the
  hamlet's commons. No NPC yet (fishing stays backlogged — the village fisherman already says
  "Fishing's coming").

## Materials / loot
Flowers (cut), honeycomb (wild hives, breakable), seashells (piles), driftwood → wood, wild berries,
mushrooms in the forest patches. Mining is the ZONE'S TEASE, not its business: shovel-tier dirt-block
masses with small stone/ore cores in ant country, and the rocky gorge's stone with common veins + a
few deep rares — a taste of the underground rows below (the full ore economy lives in the mining
zones; see caves.md per-zone tables).

## Craft brief (zone-craft skill; this pass: the south band + the gorge, 2026-07-06)
> **OWNER CORRECTION after this pass shipped (2026-07-06):** everything ant-flavored below
> (mounds, the ring "colony", the OLD DIG story, the sign gag, the ant owner-questions) was
> builder invention and is VOID — "there is no ant colony in the zone." The south band is a
> pure dirty/rocky GRADIENT with embedded mineable masses (see Connections §S + C12). Kept
> from this pass: the mass/core/vein mechanics, the gorge, Halloway's claim.
- **The promise:** a gentle flower coast that HUMS — the zone where you learn bees, while the
  ground itself starts whispering about what lives below.
- **Region jobs:** sea/beach = wild edge + curiosity rewards · Gullwash inlet = working harbor ·
  Maren's farm = the teaching workplace · east meadows = the nectar engine · north woods +
  glade/hollow = discovery band framing the north route · Dragonfly Lake = quiet recreation ·
  stream + gorge = the mining tease · ANT COUNTRY (south) = the transition + first digging ·
  the road web = the spine.
- **Landmarks:** 12 named (see Landmarks above) — floor is 3.
- **Content brainstorm (this pass, ≥25 across 6 categories):**
  *activity/work:* prospector's dig at the gorge (ore_pile, crate, a leaning signpost claim),
  shovel-test pits in the dirt masses (1-cell gaps), a stake line? (cut — reads as fence);
  *people & wear:* a worn scratch of path toward the richest mass, the claim sign's text,
  scattered spilled blocks (the apron doing its job);
  *nature:* ant mounds crowding the mass feet, mounds in a ring (a young colony), dry tall_grass
  drifts between masses, sparse dandelion on dirt;
  *ground/water:* dirt-block masses (5-6, varied sizes), stone cores, painted-dirt lanes, gravelly
  stone_floor lips at the gorge, the stream cutting the gorge rock;
  *loot/extraction:* commons veins in every mass (coal/copper), iron in the bigger cores, ONE
  short deep rare per the doctrine (silver in ant country's largest core; silver+gold+ruby as
  doctrine rares in the gorge), honey nowhere near — the contrast IS the point;
  *whimsy:* a mound pushed up THROUGH the old picnic spot? (cut — beach is far), an ant_mound
  right beside the warning sign (the sign is losing the argument), one message_bottle worth of
  weird: a buried boot? (no entity — cut; keep the sign gag).
  → CHOSEN: masses+cores+veins, mounds at feet + one ring, the prospector story at the gorge,
  test pits, dirt lanes, the sign-vs-mound gag.
- **Micro-stories (≥2):** (1) someone staked a claim at the gorge and left in a hurry — ore_pile,
  a crate, a claim sign ("CLAIM — J. Halloway. Back by spring."); (2) the warning sign at ant
  country with a fresh mound erupting right beside its post — the ground is winning.
- **Ground-variety plan (≥3):** dirt_block masses / stone_block+ore cores / painted-dirt aprons
  + lanes / stone_floor gorge lips — over the existing grass/sand/forest-floor base.
- **Edges:** unchanged contracts (E road y=124 + stream y≈76 to the village; W sea; N corridor
  toward Meadow (1,0); S = ant country foreshadowing Ant Colony (3,0) below).
- **The deliberate rule-bend (C6):** the prospector's gear is deliberately UNTIDY — rows are for
  working places; this one was ABANDONED in a hurry, and the disorder is the story.
- **Owner questions:** (1) surface ants as a real species (sprites exist) — queue as its own
  gated slice? (2) when Ant Colony (3,0) is built, does the transition get a real entrance
  occupant (a collapsed burrow) here?

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
