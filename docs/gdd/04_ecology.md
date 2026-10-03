# §04 · Ecology, the Ecologist & the Ecology tab
<!-- gdd: id=04 status=review updated=2026-10-03 -->

## The experience
Every zone is a food web you can read. Reeds mean dragonflies and mosquitoes, rotten logs mean grubs and centipedes,
milkweed means butterflies and the wasps that hunt their young. Each bug eats something real, breeds somewhere real,
and is kept in check by something real, so when you change a zone — plant milkweed, sand a marsh, lead ants to a new
carcass pile, flood a field with flies — the change runs through it the way it would in life. Nothing happens at
random: booms, swarms and crashes have causes you can see coming. The Ecologist reads it with you, and pays you to
mend what breaks.

## Decided
- **The ecosystem is the point, and players may tip it** (2026-09-28, D62): changing it, for better or worse, is the
  game; a fly boom from an over-watered orchard is the player's right, up to the caps.
- **Several food chains, some short and some tall, each tuned on its own** (accepted, overview P10, 2026-09-28).
- **Habitat does the everyday work**; **hard caps and reseeding stay** as the safety net; **weather is a lever of last
  resort**; **behaviour is polished before the numbers are tuned** (accepted, overview P10, 2026-09-28).
- **Ecosystems, not events** (2026-10-02, D79): centipedes near the ants live there as part of the ecosystem; there are
  no random raid events.
- **Mosquitoes need something in the marsh to feed on, and are held back by sand laid on the marsh** (2026-10-02, D79).
- **Locusts swarm, and get no boss**; a swarm eats wheat and the other plants locusts eat (2026-09-28).
- **No seasons** (January 2026; confirmed 2026-09-27).
- **Bugs really cross zone borders**, and a zone nobody is in catches up when someone arrives (2026-07-06; 2026-09-26).
  Already settled: the black ants forage into the Bee Meadow and the Mining Camp; the Deadly Ants forage up into the
  Shallow Swamp (D3, D9, D21).
- **Underground, dirt holds the recyclers and ants; rock holds the centipede and spider hunters; spiders only in the
  lower underground, not the first mine** (June 2026, D21).
- **New bugs, not new zones** (2026-09-26): new species are welcome if the balance holds.
- **Research, plants, quests and the tab** work as overview P8 and P9 describe (accepted 2026-09-28): examining a
  species opens its facts; plants feed, steer and boost bugs; the Ecologist's quests come from real conditions; the tab
  shows each zone with a monitoring station.
- **Finishing each bug's ecology** (2026-10-03): every bug needs real food and a real place to breed; P1 makes it a
  rule.

## Current design
The zones and the bugs each brings in, from the accepted bug lineups (D80–D82) and D21, with this section's
corrections. "New" counts the species a player first meets there.

| Ring | Zone | New bugs | New | Also there |
|---|---|---|---|---|
| Home | Village | house fly, queen butterfly, paper wasp, garden centipede, garden millipede, carrion beetle, blue dasher, firefly, honeybee, water strider, crayfish; silk moth and house cricket on the farm | 13 | — |
| Home | Bee Meadow | bumblebee, death's-head hawkmoth, field cricket | 3 | honeybees, paper wasps, blue dashers, butterflies, flies; black ants from the south |
| Home | Ant Tunnels | black ants (workers, scouts) | 1 | flies, carrion beetles |
| Home | Mining Camp | tiger centipede, cave beetle, cave glowworm, giant African millipede, cave fly, daddy longlegs | 6 | black ants crossing in |
| Home | Ant Colony + Queen | black ant warriors and queen (castes) | 0 | tiger centipedes, cave flies |
| Middle | Wasp Thicket | yellowjacket, European hornet, forest scorpion, stag beetle, purple emperor, Chinese mantis, luna moth | 7 | — |
| Middle | Butterfly Fields | monarch, emperor dragonfly, orchid mantis, jumping spider | 4 | luna moths, queen butterflies, fireflies, bees |
| Middle | Hilltop Meadow | bombardier beetle | 1 | European hornets, bumblebees, field crickets, honeybees |
| Middle | Centipede Cavern | giant centipede, cave spider | 2 | tiger centipedes, glowworms, cave beetles, millipedes, daddy longlegs |
| Middle | Underground River | river crab | 1 | glowworms, cave flies, cave beetles |
| Outer | Locust Farmland + town | desert locust, Colorado beetle, killer bee | 3 | Chinese mantises, house crickets |
| Outer | Millipede Forest | northern giant hornet, Hercules beetle, dragon millipede (+ Asian honey bee, open) | 3–4 | giant centipedes, African millipedes |
| Outer | Scorpion Rocks | fat-tailed scorpion | 1 | killer bees; field crickets proposed as prey |
| Outer | Shallow Swamp | horse fly, house mosquito | 2 | water striders, crayfish, emperor dragonflies; fire ants foraging |
| Outer | Deadly Ants outpost | fire ants, ant-decapitating fly | 2 | — |
| Outer | Underground River, deep | — | 0 | river crabs, glowworms |
| Outer | The surface river | dragonhunter (moved here) | 1 | emperor dragonflies, monarchs |
| Far | Spider Vale West | wolf spider, Brazilian wandering spider | 2 | jumping spiders, giant centipedes, daddy longlegs; field crickets proposed as prey |
| Far | Spider Vale East | black widow, Goliath tarantula, giant huntsman, tarantula hawk | 4 | daddy longlegs |
| Far | Deep Swamp | malaria mosquito | 1 | horse flies, crayfish, water striders, emperor dragonflies |
| Far | Deadly Ants core | fire ant queen (a boss) | 0 | fire ants, decapitating flies |

## As built
- **What runs today** (the zones' spawn lists, checked 2026-10-03): the village (village_21_B) — flies, butterflies,
  paper wasps (as "the wasp"), garden centipedes, millipedes and carrion beetles; the Bee Meadow — honeybees,
  butterflies, paper wasps, the dragonfly, fireflies, flies, millipedes and carrion beetles; the Ant Tunnels — workers
  and scouts on scout-remembered trails, and garden centipedes; the Mining Camp — stand-ins (carrion beetles, garden
  centipedes, millipedes) until its own bugs exist; and test zones (the Bug Lab and others). Bug transfer between zones
  isn't built yet.
- **Control:** per-zone population bands, reseeding, rain and drought as levers, hard caps, and a six-times-speed tuning
  rig (`ecology_parameters.md`, the `ecology-tuning` skill).
- **Known gaps** (checked 2026-10-03): the centipedes eat only flies and have no breeding place; the dragonfly never
  breeds and hunts the paper wasp, which real blue dashers don't; the firefly has no food; the hornet's nest has no
  picture or zone; the yellowjacket shares the paper wasp's nest. **No zone's ecology is finished, and no bug is.**
- **No Ecology tab** yet (only a developer graph); the village Ecologist sells six decoration recipes.

## How it will work
Each zone is finished in three passes, in the roadmap's order (home zones first, then each ring as it is built):
1. **Its bugs' behaviour** (§03, each bug signed off by you).
2. **Its habitat**: the plants, water, wood and stone its bugs need to eat and breed (P2), built with the zone.
3. **Its numbers**: the six-times-speed runs until every species holds its band from its own breeding, with the
   safety net idle (P1), and the food chains below actually feeding each other. The Ecologist's quests then come
   from what the tab shows (accepted, overview P9).

## Proposals

### P1. Finishing the ecology: every bug has food, a place to breed, and a check, where it lives
- **Food:** something it really eats, present in its zone, in amounts a zone can be tuned around.
- **A place to breed:** the real one — rot, a host plant, a nest, water, dead wood, a burrow, a web, a carcass —
  so its numbers come from its own breeding, not from the game reseeding it.
- **A check:** a hunter, a parasite, a shortage or the player, so it can't take over its zone unless a player lets
  it (and players may tip a zone, D62). The hard caps and reseeding stay underneath as the safety net (decided).
- **Where the real food or breeding place is gone in 2126**, the sheet names the stand-in: the burying beetle
  buries dead bugs instead of small birds and rodents; mosquitoes and horse flies bite people, the last large
  warm-blooded animals; the cave beetle eats what washes in and dead cave bugs, not bat droppings.
- A zone isn't finished until every bug in it passes this check in the six-times-speed ecology runs: its births
  come from its own breeding, and it stays in its band without the safety net doing the work.

**Lenses:** Real biology — every link is the real animal's (facts files). Fit — your ask that every bug have food and a
place to breed (2026-10-03), made a rule. **Cost and risk:** some zones need new plants, water or objects for breeding
(each zone lists them).

### P2. Habitat makes the ecology
- Each zone's plants, water, wood and rock are chosen for its bugs: milkweed for the milkweed butterflies, reeds
  and still water for dragonflies and mosquitoes, dead wood for beetle grubs, stones and cracks for scorpions and
  centipedes, cave roofs for glowworms and cave spiders.
- So building a zone (the zone-craft skill) and finishing its ecology are one job: the zone's design lists the
  habitat its bugs need, and the zone isn't done until they breed in it.
- Plants steer bugs as well as feeding them (accepted, overview P8): some draw bugs, some keep them off, some boost
  breeding, so a player can shape a zone without walls.

**Lenses:** Fit — habitat does the everyday work (accepted, overview P10). Picture the moment — reading a zone by
its plants: reeds mean dragonflies, rotten logs mean grubs. **Cost and risk:** zone art and placement, done with
each zone.

### P3. Zones trade bugs where real bugs would
- Ants forage out of their zones along trails (the black ants into the Bee Meadow and the Mining Camp, decided;
  the fire ants up into the Shallow Swamp, decided), locust swarms spill out of the farmland (decided), wasps and
  hornets spread from their nests, night flyers cross toward lamps, dragonflies follow the river.
- Crossing uses the real bug transfer between zones (decided), and a zone nobody is in catches up when someone
  arrives (decided).

**Lenses:** Real biology — real bugs don't respect borders. Fit — the decided crossings, extended where the real
animal would cross. **Cost and risk:** rides the cross-zone transfer already planned.

### P4. Every zone gives the player levers
- In each zone the player can push the ecology with the tools of the trade: bait (decided, overview P4), plants,
  light, sand on a marsh, smoke, fences and stone, the bug stick, releasing a natural enemy (the mantis against
  locusts, the dragonfly against wasps), or simply harvesting.
- Each zone below names its main levers, so the Ecologist's quests (accepted) have real solutions.

**Lenses:** Fit — several solutions to every problem (the Ecologist's quests, accepted). Picture the moment —
setting mantis egg cases along a field edge before the locusts hatch. **Cost and risk:** most levers are built or
designed; each zone lists what's new.

### P5. Village (home, easy) — the fly farm's food web
- **Bugs it brings in (13):** house fly, queen butterfly (its real name still open), paper wasp, garden centipede,
  garden millipede, carrion beetle, blue dasher, firefly, honeybee, water strider, crayfish; on the player's farm
  the silk moth and the house cricket (a maybe).
- **The food web:** orchard fruit and compost feed the flies; flies feed the paper wasps, the blue dashers over the
  pond and the garden centipedes at the edge of the north-east woods. Flowers feed the honeybees and butterflies;
  milkweed feeds the butterflies' caterpillars, which the paper wasps hunt. Leaf litter and logs feed the
  millipedes, and the fireflies' young hunt soft grubs in the damp soil. Carcasses go to the carrion beetles, which
  bury them before the flies can breed on them. In the lake, water striders take bugs that fall on the water and
  crayfish eat plants, rot and small bugs.
- **Where they breed:** rot and compost (flies), milkweed (butterflies), paper combs under eaves and branches (paper
  wasps), hive boxes (honeybees), under stones and logs (centipedes, millipedes), buried carcasses (carrion beetles),
  damp ground (fireflies), water plants in the reedy pond (dragonflies), the lake's banks and shallows (striders,
  crayfish), the mulberry (silkworms), a pen (crickets).
- **The player's levers:** the fly farm and its compost, fences, smoke (and taking down nests) against the paper
  wasps, flowers and milkweed, dragonflies against flies by the water, the bug stick, bait, lamps at night.
- **To build for it:** the reedy pond as a dragonfly nursery (today the dragonfly never breeds); stones and logs as
  the centipede's breeding place (today it has none); damp ground with grubs for the fireflies (today they eat
  nothing); the mulberry; a cricket pen; water life in the lake.
- **Plenty of bugs** for a home zone.

**Lenses:** Fit — the legible chain the village was built around (fruit → rot → flies → wasps), finished. Picture the
moment — dusk: flies settling, fireflies rising, a dragonfly on a reed. **Cost and risk:** the water block and the
breeding places; the village's numbers are retuned after (P10).

### P6. Bee Meadow (home, easy) — honey, flowers and a thief at night
- **Bugs it brings in (3):** bumblebee, death's-head hawkmoth, field cricket. **Also here:** wild honeybee hives and
  Maren's farm, paper wasps at the forest edges (built), blue dashers on the river, queen butterflies, house flies;
  black ants foraging in from the south once bugs cross zones (decided).
- **The food web:** flowers everywhere feed the honeybees, bumblebees and butterflies; paper wasps take bees and
  caterpillars; the death's-head moth raids hives for honey at night; field crickets graze the short, dry turf; the
  windfalls under the south meadow's fruit trees feed flies and, later, the incoming ants.
- **Where they breed:** wild hive trees and boxes (honeybees), hollows and nest boxes (bumblebees), wild nightshade
  (the death's-head's caterpillars), burrows in short dry turf (field crickets), paper combs (wasps), milkweed.
- **The player's levers:** hives and smoke, bumblebee boxes, flowers, a lamp kept away from the hives, the bug stick
  on the ants.
- **To build for it:** wild nightshade patches (the death's-head's caterpillars have nothing to eat otherwise); bare,
  short turf for cricket burrows; bumblebee boxes.
- **Thin:** three newcomers; see Q1.

**Lenses:** Fit — the gentle bee zone (the zone sheet), now with a night side. Real biology — the death's-head in
the hive (facts B). **Cost and risk:** small; most of it is the bees' existing work.

### P7. Ant Tunnels (home, easy, half above ground) — the ants' open country
- **Bugs it brings in (1 species, 2 castes):** black ants — workers and scouts. **Also here:** flies and carrion
  beetles at windfalls and carcasses.
- **The food web:** nectar, windfalls and dead bugs feed the black ants, who carry it along their trails down to the
  colony below (P9).
- **Where they breed:** the colony's chambers below; new colonies from mating flights.
- **The player's levers:** the bug stick (lead ants off a trail and start a new one), bait, a stone across a trail, a
  carcass pile to feed the colony.
- **Crossings:** ants out to the Bee Meadow and the Mining Camp (decided).
- **To build for it:** the trail grid with per-ant following (the first block, architecture doc §4).
- **Thin by species, rich in behaviour:** trails, castes and leading are the zone's content; see Q1 for guests of the
  ants' nests.

**Lenses:** Fit — the half-outdoor ant country you laid out (2026-07-06/07). Picture the moment — lines of ants
bending toward the dark mouth in the cliff. **Cost and risk:** the trail block is the largest single piece.

### P8. Mining Camp (home, easy, underground) — the dark food chain
- **Bugs it brings in (6):** tiger centipede (D21's cave centipede), cave beetle, cave glowworm, giant African
  millipede (D21's tougher cave millipede), cave fly, daddy longlegs. **Also here:** black ants coming in through the
  dirt tunnels (decided). No spiders yet (D21).
- **The food web:** water seeping down the walls and dead bugs feed the cave beetles; dead bugs and the ants' refuse
  feed the cave flies; flying cave flies end in the glowworms' threads; decaying plants in the dirt top feed the
  African millipedes; tiger centipedes hunt beetles, flies and ants; daddy longlegs scavenge small dead things.
- **Where they breed:** egg clumps on cave walls (glowworms), under stones (centipedes), damp dirt (millipedes),
  the seeps (beetles), refuse (cave flies).
- **The player's levers:** light (glowworms go dark when touched), smoke, stone against dirt, glowworm lanterns.
- **To build for it:** seeping-water spots on walls; glowworm ceilings; the cave fly's burst-running; the cave fly's
  species recheck.

**Lenses:** Fit — D21's roster for this zone, each given its real species. Picture the moment — a ceiling of
stars over the mine rail. **Cost and risk:** small per bug.

### P9. Ant Colony and its Queen (home, medium, deep) — the superorganism
- **Bugs it brings in:** the black ants' warriors and their queen. **Also here:** tiger centipedes at the dirt-and-rock
  seam with the Centipede Cavern, eating ants (an ecosystem, not a raid — D79); cave flies on the refuse heaps.
- **The food web:** everything the trails bring in — nectar, fruit, carcasses — feeds the brood and the queen; the
  refuse feeds cave flies; centipedes take ants at the seam.
- **A correction:** the old zone design's fungus gardens are leafcutter-ant farming; black garden ants don't farm
  fungus, so I propose food stores and brood chambers in their place.
- **Where they breed:** the queen's chamber and the nurseries; daughter colonies from mating flights.
- **The player's levers:** the bug stick, bait, blocking stones; killing the queen ends the colony until a new queen
  founds another (accepted, overview P13).
- **To build for it:** the queen, the warriors' formic acid, brood chambers, refuse heaps.

**Lenses:** Real biology — black garden ants' real diet (facts A). Fit — the colony and its Queen (D3). **Cost and
risk:** reuses the ant work.

### P10. Wasp Thicket (middle ring, medium) — the first place that fights back
- **Bugs it brings in (7):** yellowjacket, European hornet, forest scorpion, stag beetle, purple emperor, Chinese mantis
  (at its edges), luna moth.
- **The food web:** flowers and rotten fruit feed the yellowjackets, which hunt caterpillars, flies and bees; the
  hornets from the hollow trees hunt yellowjackets, moths, dragonflies and mantises, and come to the ranger station's
  lights at night (D72); sap and rot bring the purple emperors down from the oaks, and willow scrub feeds their
  caterpillars; walnut and birch feed the luna caterpillars; dead wood feeds the stag beetles' grubs; forest scorpions
  under logs and mantises at the edges hunt what passes.
- **Where they breed:** hidden ground and tree nests (yellowjackets), hollow trees (hornets), dead wood (stag beetles),
  walnut and birch (luna), willow scrub (purple emperor), twigs (mantis egg cases), under logs (scorpions).
- **The player's levers:** smoke, lamps (the station's lights draw hornets), mantis egg cases, the bug stick on
  beetles.
- **To build for it:** hollow trees, ground-nest entrances, dead wood with grubs, walnut, birch and willow scrub.

**Lenses:** Fit — the combat-intro zone (the zone sheet), with every threat from the real food web. Picture the moment
— the ranger station's lamp at midnight, and the hum of hornets. **Cost and risk:** the alarm call and the lights.

### P11. Butterfly Fields (middle ring, medium) — milkweed, beauty and the night glow
- **Bugs it brings in (4):** monarch, emperor dragonfly, orchid mantis, jumping spider. **Also here:** luna moths, queen
  butterflies, fireflies at night, bees; the dragonhunter on the river at its edge (P21).
- **The food web:** milkweed feeds the monarch and queen caterpillars, whose stored poison keeps most hunters off;
  flowers feed the butterflies and bees; orchid mantises among the flowers take pollinators; jumping spiders take
  caterpillars and small bugs; emperor dragonflies hunt butterflies and other dragonflies in the air; fireflies light
  the night.
- **Where they breed:** milkweed (monarchs, queens), host trees (luna), a pond or spring (emperor dragonflies — the zone
  has little water today), under stones and bark (jumping spiders).
- **The player's levers:** milkweed and flowers, nets, a lamp for moths, moving orchid mantises off a butterfly patch.
- **To build for it:** a pond for the emperor dragonflies' young; host trees for luna moths; the great milkweed stand.

**Lenses:** Fit — the aesthetic zone (the zone sheet), with a real reason for every beautiful thing. Picture the
moment — monarchs clustered on a milkweed stand, and a pink "flower" that eats one. **Cost and risk:** the water
block for one pond.

### P12. Hilltop Meadow (middle ring, medium) — advanced beekeeping under the hornets
- **Bugs it brings in (1):** bombardier beetle. **Also here:** the European hornet (its top threat), bumblebees, field
  crickets, honeybees.
- **The food web:** flowers feed the bees; hornets hunt bees at the hives by day and come to lamps at night; field
  crickets graze the dry turf; bombardiers hunt small bugs under stones at night.
- **Where they breed:** hives and boxes (bees), hollow trees (hornets), burrows (crickets), under stones (bombardiers).
- **The player's levers:** smoke, the stronger hives, lamps that draw hornets away from the hives.
- **Thin:** one newcomer; see Q1.

**Lenses:** Fit — the step up from the Bee Meadow (the zone sheet). **Cost and risk:** small.

### P13. Centipede Cavern (middle ring, medium, deep) — glowworm light and the giant on the ceiling
- **Bugs it brings in (2):** giant centipede, cave spider. **Also here:** tiger centipedes in the upper halls,
  glowworms, cave beetles, African millipedes, daddy longlegs.
- **The food web:** seeps and dead bugs feed the cave beetles and millipedes; cave spiders take millipedes and
  centipedes; glowworms take the cave flies; giant centipedes take big bugs from the ceiling.
- **Where they breed:** cave roofs (spider egg sacs, glowworms), under stones (centipedes, brooding mothers), damp
  floors (millipedes).
- **The player's levers:** light (spiders flee it, their young are drawn to it, glowworms go dark), smoke, stone.
- **Thin-ish:** two newcomers; see Q1.

**Lenses:** Fit — D21's deeper roster (spiders and the venomous centipede here, not in the first mine). Picture the
moment — the torch finds a white teardrop on the roof, then a shape beside it. **Cost and risk:** the ceiling drop.

### P14. Underground River (middle ring, medium) — the dark river
- **Bugs it brings in (1):** river crab. **Also here:** a glowworm ceiling over the water, cave flies, cave beetles.
- **The food web:** debris washed in feeds the crabs and beetles; glowworms over the water take the flies.
- **Where they breed:** the crabs in the banks, the glowworms on the roof.
- **The player's levers:** the fish trap, light.
- **Thin:** one newcomer; see Q1.

**Lenses:** Fit — the water rung below the swamps (the zone sheet). **Cost and risk:** small.

### P15. Locust Farmland and the western town (outer ring, hard) — holding the line
- **Bugs it brings in (3):** desert locust, Colorado beetle, killer bee. **Also here:** Chinese mantises; house crickets
  at the town's farm store.
- **The food web:** crops and wild green feed the locusts and the Colorado beetles (the tomato family); mantises take
  locusts and other bugs; flowers and crops feed the killer bees.
- **Where they breed:** bare soil (locust egg pods), crop leaves (beetle egg clusters), twigs (mantis egg cases),
  ground cavities and crevices (killer bees).
- **The player's levers:** harvesting locusts before they crowd, mantis egg cases, picking off egg clusters, trap
  crops, requeening killer bees.
- **Crossings:** locust swarms spill into the zones around (decided).

**Lenses:** Fit — the embattled farm zone (the zone sheet), with the swarm as a cause and effect. **Cost and risk:** the
swarm-change block.

### P16. Millipede Forest (outer ring, hard) — old growth and the hornets' raids
- **Bugs it brings in (3, 4 with the proposed bee):** northern giant hornet, Hercules beetle, shocking pink dragon
  millipede, and the Asian honey bee (open). **Also here:** giant centipedes, giant African millipedes.
- **The food web:** leaf litter and dead wood feed the millipedes and the Hercules grubs; fallen fruit and sap feed the
  adult beetles and the hornets; bees feed the giant hornets' young; giant centipedes take millipedes and big bugs.
- **Where they breed:** rotten roots (giant hornet nests), fallen trees (Hercules grubs), leaf litter (millipedes),
  hives (Asian honey bees).
- **The player's levers:** Asian honey bee hives, stopping a hornet scout before it brings a raid, rain (dragon
  millipedes come out after it).

**Lenses:** Fit — the deep woods and chitin armour (the zone sheet). Picture the moment — a hornet scout at your hive.
**Cost and risk:** the raid.

### P17. Scorpion Rocks (outer ring, hard) — heat, cracks and deadly venom
- **Bugs it brings in (1):** fat-tailed scorpion. **Also here:** killer bees.
- **A gap:** the scorpions need prey, and the zone has almost none. The accepted field cricket really lives in warm,
  dry, sunny, gravelly ground (facts B), so I propose field crickets in the rocks' gravel and scrub as the scorpions'
  prey, and more on Q1.
- **The food web (with the crickets):** dry plants feed the crickets; fat-tailed scorpions take them from the cracks at
  night; flowers feed the killer bees.
- **Where they breed:** cracks and under stones (scorpions; real scorpion mothers carry their young), burrows
  (crickets), crevices (killer bees).
- **The player's levers:** an ultraviolet lantern (scorpions glow under it, real), heat gear, antivenom.
- **Thin:** one newcomer; see Q1.

**Lenses:** Real biology — the cricket's real habitat (facts B). Fit — the venom-and-mining zone (the zone sheet).
**Cost and risk:** small.

### P18. Shallow Swamp (outer ring, hard) — water, reeds and biters
- **Bugs it brings in (2):** horse fly, house mosquito. **Also here:** water striders, crayfish, emperor dragonflies;
  fire ants foraging up from the Deadly Ants (decided).
- **The food web:** rot in still water feeds the mosquitoes' young; water striders and dragonflies eat them; mosquitoes
  and horse flies bite people; males of both drink nectar; crayfish eat plants, rot and small bugs; fire ants forage
  the edges.
- **Where they breed:** still water (mosquito rafts), wet mud (horse fly young), reeds and stones (horse fly eggs),
  banks (crayfish), water plants (dragonflies).
- **The player's levers:** sand on the marsh (D79), striders and dragonflies, light clothes and shade against horse
  flies, the decapitating fly against the fire ants.
- **Thin:** two newcomers; see Q1.

**Lenses:** Fit — the water zone (the zone sheet) and your sand rule (D79). **Cost and risk:** the water block.

### P19. Deadly Ants outpost (outer ring, hard, underground) — the fire ants' front
- **Bugs it brings in (2):** fire ants (workers and warriors), ant-decapitating fly.
- **The food web:** fire ants eat nearly everything they meet and forage up into the Shallow Swamp; the decapitating
  flies live off the fire ants.
- **Where they breed:** mounds and their chambers; mating flights; the flies inside the ants.
- **The player's levers:** releasing decapitating flies, fire resistance, bait to draw the columns.

**Lenses:** Fit — the endgame ant war (the zone sheet), given its real enemy. **Cost and risk:** the parasite block.

### P20. Underground River, deep (outer ring, hard) — the sunken lake
- **Bugs it brings in:** none new — river crabs and glowworms continue from above. The dragonhunter that the bug lineups
  put on "the deep river" belongs on the surface river (P21): dragonflies hunt by sight and need daylight.
- **Thin:** no newcomers; see Q1.

**Lenses:** Real biology — dragonflies hunt by sight (the July research). **Cost and risk:** none.

### P21. The surface river — the dragonhunter's beat
- **Bugs:** the dragonhunter, moved here from the underground (a correction to its lineup), along the river where it
  runs past the Butterfly Fields and the Millipede Forest; emperor dragonflies and monarchs from the Fields are its
  prey.
- **The food web:** dragonflies hunt over the water; the dragonhunter hunts the other dragonflies, and monarchs.
- **Where they breed:** the river's edges (dragonflies' young in the water).

**Lenses:** Real biology — the dragonhunter's real home is forest rivers (its lineup). **Cost and risk:** the water
block.

### P22. Spider Vale West (far ring, extra hard) — hunters in the dark
- **Bugs it brings in (2):** wolf spider, Brazilian wandering spider. **Also here:** jumping spiders, giant centipedes,
  daddy longlegs.
- **A gap:** like Scorpion Rocks, the hunters need prey. Field crickets really live on heath and dry sunny ground (facts
  B), which suits the vale's gorse; I propose them as the main prey.
- **The food web (with the crickets):** crickets feed the wolf spiders (from burrows), the wandering spiders (on the
  ground at night) and the jumping spiders (by day); giant centipedes take spiders; daddy longlegs scavenge.
- **Where they breed:** burrows (wolf spiders; mothers carry their young), silk sacs (wandering, jumping spiders),
  crickets' burrows.
- **The player's levers:** a torch (eyeshine shows where wolf spiders wait), antivenom, keeping to the light.

**Lenses:** Fit — the spider zone (the zone sheet). **Cost and risk:** small.

### P23. Spider Vale East (far ring, the hardest surface zone) — webs, burrows and the tarantula's wasp
- **Bugs it brings in (4):** black widow, Goliath tarantula, giant huntsman, tarantula hawk. **Also here:** daddy
  longlegs.
- **The food web:** small bugs caught in the widows' webs; large bugs taken by the tarantulas from their burrows;
  huntsmen in the caves; tarantula hawks hunt the tarantulas and drink milkweed nectar; field crickets as the prey base,
  as in the west vale.
- **Where they breed:** webs (widows' egg sacs), burrows (tarantulas), the caves (huntsmen), the paralysed tarantula in
  a burrow (tarantula hawks).
- **The player's levers:** cutting webs, a torch, antivenom.
- **To build for it:** milkweed in the vale for the tarantula hawks.

**Lenses:** Fit — the endgame surface (the zone sheet). Picture the moment — a rust-winged wasp dragging a tarantula.
**Cost and risk:** the parasite and web blocks.

### P24. Deep Swamp (far ring, extra hard) — the quiet biters and the black water
- **Bugs it brings in (1):** malaria mosquito. **Also here:** horse flies, crayfish, water striders, emperor
  dragonflies.
- **The food web:** still, sunlit water feeds the malaria mosquitoes' young; striders and dragonflies eat them; the
  mosquitoes bite people and drink from the swamp's soft young bugs (§03 P56, a stretch).
- **Thin:** the zone design wants an apex predator (the giant water bug, cut); see Q1.

**Lenses:** Fit — disease and poison (the zone sheet). **Cost and risk:** the water block.

### P25. Deadly Ants core (far ring, extra hard, deep) — the war queen's fortress
- **Bugs it brings in:** the fire ant queen (the war queen, a boss — accepted, overview P13). **Also here:** fire ants,
  decapitating flies.
- **Thin by species:** the queen fight is the zone's headline; see Q1.

**Lenses:** Fit — the hardest underground zone. **Cost and risk:** the boss.

## To settle later (not in this review)
- What area an ecology station covers (the zone, or a radius); rewards for the Ecology tab's tasks; what pollination
  does for crops; how fast a damaged zone recovers; what a boss that grows out of an imbalance drops.
- Each zone's numbers — set by the tuning runs after its bugs' behaviour is signed off (overview P10).
- Whether water should stop crawling bugs (GDD §01, Q1) — it changes what a moat or a river does to the ecology.

## Sources
- The bug lineups (`docs/gdd/bug_lineups.jsonl`), decisions D3, D9, D21, D62, D79–D82, and the overview's accepted
  P8–P10.
- The zones' design sheets (`docs/product/economy/zones/`) and built-zone records (`docs/product/zones/`); each built
  zone's spawn list (`nakama/data/zones/*/zone.json`).
- Facts per bug: `docs/product/investigations/research-2026-10-03/bug-ecology-facts-A.md`, `bug-ecology-facts-B.md`;
  candidate bugs for thin zones: `thin-zone-candidates.md`.
- The ecology engine and its tuning: `docs/product/ecology/ecology_parameters.md`, the `ecology-tuning` skill.

