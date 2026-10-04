# §04 · Ecology, the Ecologist & the Ecology tab
<!-- gdd: id=04 status=rework updated=2026-10-04 -->

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
  Already settled: the black ants forage into the Bee Meadow (2026-07-06/07, §01) and the Mining Camp (D21); the
  Deadly Ants forage up into the Shallow Swamp (D3, D9).
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
corrections. "New" counts the species whose home is that zone; a bug that also visits other zones is listed there
under "Also there". The rings are §01's (home, middle, far, edge). Your guideline is three or four new species per zone
(2025-12-30): eleven zones fall short, and the questions at the end take them one by one (Q1–Q14, with three zones
that meet it but have one strong candidate).

| Ring | Zone | New bugs | New | Also there |
|---|---|---|---|---|
| Home | Village | house fly, queen butterfly, paper wasp, garden centipede, garden millipede, carrion beetle, blue dasher, firefly, honeybee, water strider, crayfish; silk moth and house cricket on the farm | 13 | — |
| Home | Bee Meadow | bumblebee, death's-head hawkmoth, field cricket | 3 | honeybees, paper wasps, blue dashers, butterflies, flies, fireflies, garden millipedes, carrion beetles; black ants from the south |
| Home | Ant Tunnels | black ants (workers, scouts) | 1 | flies, carrion beetles, garden centipedes |
| Home | Mining Camp | tiger centipede, cave beetle, cave glowworm, giant African millipede, daddy longlegs | 5 | black ants crossing in; cave flies |
| Home | Ant Colony + Queen | cave fly (at the granaries, its lineup's home); the black ants' warriors and queen | 1 | tiger centipedes |
| Middle | Wasp Thicket | yellowjacket, European hornet, forest scorpion, stag beetle, purple emperor, Chinese mantis, luna moth | 7 | house flies |
| Middle | Butterfly Fields | monarch, emperor dragonfly, orchid mantis, jumping spider | 4 | luna moths, queen butterflies, fireflies, bees; dragonhunters along the river |
| Middle | Hilltop Meadow | bombardier beetle | 1 | paper wasps kept as pest control, European hornets, bumblebees, field crickets, honeybees |
| Middle | Centipede Cavern | giant centipede, cave spider | 2 | tiger centipedes, glowworms, cave beetles, cave flies, African millipedes, dragon millipedes (proposed), daddy longlegs |
| Middle | Underground River | river crab | 1 | glowworms over the water, cave flies, cave beetles |
| Far | Locust Farmland + town | desert locust, Colorado beetle, killer bee | 3 | Chinese mantises, house crickets |
| Far | Millipede Forest | northern giant hornet, Hercules beetle, dragon millipede, dragonhunter (on its river) (+ Asian honey bee, open) | 4–5 | giant centipedes, African millipedes, emperor dragonflies along the river, luna moths (proposed) |
| Far | Scorpion Rocks | fat-tailed scorpion | 1 | killer bees; field crickets proposed as prey |
| Far | Shallow Swamp | horse fly, house mosquito, ant-decapitating fly (over the fire ants' columns) | 3 | water striders, crayfish, emperor dragonflies, blue dashers; the fire ants' foraging front, with mounds and rafts; caterpillars on swamp milkweed (proposed) |
| Far | Deadly Ants outpost | fire ants (workers, warriors) | 1 | the decapitating flies' "zombie" ants wandering out |
| Far | Underground River, deep | — | 0 | river crabs, glowworms, cave beetles |
| Edge | Spider Vale West | wolf spider, Brazilian wandering spider | 2 | jumping spiders, giant centipedes, daddy longlegs; field crickets proposed as prey |
| Edge | Spider Vale East | black widow, Goliath tarantula, giant huntsman, tarantula hawk | 4 | daddy longlegs; millipedes and garden centipedes as prey (proposed) |
| Edge | Deep Swamp | malaria mosquito | 1 | horse flies, crayfish, water striders, blue dashers, emperor dragonflies and their young; caterpillars on swamp milkweed (proposed) |
| Edge | Deadly Ants core | fire ant queen (a boss) | 0 | fire ants |

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
<!-- key: 04.finishing-ecology-every-bug-has -->
- **Food:** something it really eats, present in its zone, in amounts a zone can be tuned around.
- **A place to breed:** the real one — rot, a host plant, a nest, water, dead wood, a burrow, a web, a carcass —
  so its numbers come from its own breeding, not from the game reseeding it.
- **A check:** a hunter, a parasite, a shortage or the player, so it can't take over its zone unless a player lets
  it (and players may tip a zone, D62). The hard caps and reseeding stay underneath as the safety net (decided).
- **Where the real food or breeding place is gone in 2126**, the sheet names the stand-in: the burying beetle
  buries dead bugs instead of small birds and rodents; mosquitoes and horse flies bite people and big bugs such as
  caterpillars (decided, D66), so the swamps need caterpillars of their own (P18); the cave beetle eats what washes in
  and dead cave bugs, not bat droppings.
- A zone isn't finished until every bug in it passes this check in the six-times-speed ecology runs: its births
  come from its own breeding, and it stays in its band without the safety net doing the work.

**Lenses:** Real biology — every link is the real animal's (facts files). Models agree: a hunter and its prey settle
into cycles instead of crashing only when the prey's own food regrows (NetLogo's predator–prey model). Fit — your ask
that every bug have food and a place to breed (2026-10-03), made a rule. **Cost and risk:** some zones need new plants,
water or objects for breeding (each zone lists them).

### P2. Habitat makes the ecology
<!-- key: 04.habitat-makes-ecology -->
- Each zone's plants, water, wood and rock are chosen for its bugs: milkweed for the milkweed butterflies, reeds
  and still water for dragonflies and mosquitoes, dead wood for beetle grubs, stones and cracks for scorpions and
  centipedes, cave walls and overhangs for glowworms and cave spiders (the view is from above, so caves show no
  ceilings, decided).
- So building a zone (the zone-craft skill) and finishing its ecology are one job: the zone's design lists the
  habitat its bugs need, and the zone isn't done until they breed in it.
- Plants steer bugs as well as feeding them (accepted, overview P8): some draw bugs, some keep them off, some boost
  breeding, so a player can shape a zone without walls.

**Lenses:** Fit — habitat does the everyday work (accepted, overview P10). Picture the moment — reading a zone by
its plants: reeds mean dragonflies, rotten logs mean grubs. **Cost and risk:** zone art and placement, done with
each zone.

### P3. Zones trade bugs where real bugs would
<!-- key: 04.zones-trade-bugs-where-real -->
- Ants forage out of their zones along trails (the black ants into the Bee Meadow and the Mining Camp, decided;
  the fire ants up into the Shallow Swamp, decided), locust swarms carry on out of the farmland (your wish,
  2025-12-30), wasps and hornets spread from their nests, night flyers cross toward powered lights, dragonflies
  follow the river.
- Crossing uses the real bug transfer between zones (decided), and a zone nobody is in catches up when someone
  arrives (decided).

**Lenses:** Real biology — real bugs don't respect borders. Fit — the decided crossings, extended where the real
animal would cross. **Cost and risk:** rides the cross-zone transfer already planned.

### P4. Every zone gives the player levers
<!-- key: 04.every-zone-gives-player-levers -->
- In each zone the player can push the ecology with the tools of the trade: bait (decided, overview P4), plants,
  light, sand on a marsh, smoke, fences and stone, the bug stick, releasing a natural enemy (the mantis against
  locusts, the blue dasher against flies and mosquitoes by the water, the decapitating fly against fire ants), or
  simply harvesting.
- Each zone below names its main levers, so the Ecologist's quests (accepted) have real solutions.

**Lenses:** Fit — several solutions to every problem (the Ecologist's quests, accepted). Picture the moment —
setting mantis egg cases along a field edge before the locusts hatch. **Cost and risk:** most levers are built or
designed; each zone lists what's new.

### P5. Village (home, easy) — the fly farm's food web
<!-- key: 04.village-home-easy-fly-farms -->
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
  wasps, flowers and milkweed, dragonflies against flies by the water, the bug stick, bait; in the powered age,
  light traps at night (ordinary lamps and firefly lanterns draw no bugs, §03 P7).
- **To build for it:** the reedy pond as a dragonfly nursery (today the dragonfly never breeds); stones and logs as
  the centipede's breeding place (today it has none); damp ground with grubs for the fireflies (today they eat
  nothing); the mulberry; a cricket pen; water life in the lake.
- **Plenty of bugs** for a home zone.

**Lenses:** Fit — the legible chain the village was built around (fruit → rot → flies → wasps), finished. Picture the
moment — dusk: flies settling, fireflies rising, a dragonfly on a reed. **Cost and risk:** the water block and the
breeding places; the village's numbers are retuned after (P10).

### P6. Bee Meadow (home, easy) — honey, flowers and a thief at night
<!-- key: 04.bee-meadow-home-easy-honey -->
- **Bugs it brings in (3):** bumblebee, death's-head hawkmoth, field cricket. **Also here:** wild honeybee hives and
  Maren's farm, paper wasps at the forest edges (built), blue dashers on the river, queen butterflies, house flies,
  fireflies, garden millipedes and carrion beetles (all built there today); black ants foraging in from the south once
  bugs cross zones (decided).
- **The food web:** flowers everywhere feed the honeybees, bumblebees and butterflies; paper wasps take caterpillars
  and flies; the death's-head moth raids hives for honey at night; field crickets graze the short, dry turf; the
  windfalls under the south meadow's fruit trees feed flies and, later, the incoming ants.
- **Where they breed:** wild hive trees and boxes (honeybees), hollows and nest boxes (bumblebees), wild nightshade
  (the death's-head's caterpillars), burrows in short dry turf (field crickets), paper combs (wasps), milkweed.
- **The player's levers:** hives and smoke, bumblebee boxes, flowers, the bug stick on the ants; in the powered age,
  light traps kept away from the hives.
- **To build for it:** wild nightshade patches (the death's-head's caterpillars have nothing to eat otherwise); bare,
  short turf for cricket burrows; bumblebee boxes.
- **Meets your guideline** with three newcomers; Q1 offers a fourth.

**Lenses:** Fit — the gentle bee zone (the zone sheet), now with a night side. Real biology — the death's-head in
the hive (facts B). **Cost and risk:** small; most of it is the bees' existing work.

### P7. Ant Tunnels (home, easy, half above ground) — the ants' open country
<!-- key: 04.ant-tunnels-home-easy-half -->
- **Bugs it brings in (1 species, 2 castes):** black ants — workers and scouts. **Also here:** flies and carrion
  beetles at windfalls and carcasses, and garden centipedes (built there today).
- **The food web:** nectar, windfalls and dead bugs feed the black ants, who carry it along their trails down to the
  colony below (P9).
- **Where they breed:** the colony's chambers below; new colonies from mating flights.
- **The player's levers:** the bug stick (lead ants off a trail and start a new one), bait, a stone across a trail, a
  carcass pile to feed the colony.
- **Crossings:** ants out to the Bee Meadow and the Mining Camp (decided).
- **To build for it:** the scent trail followed ant by ant (the first block, architecture doc §4).
- **Thin by species, rich in behaviour:** trails, castes and leading are the zone's content; Q2 asks what else lives
  along the trails.

**Lenses:** Fit — the half-outdoor ant country you laid out (2026-07-06/07). Picture the moment — lines of ants
bending toward the dark mouth in the cliff. **Cost and risk:** the trail block is the largest single piece.

### P8. Mining Camp (home, easy, underground) — the dark food chain
<!-- key: 04.mining-camp-home-easy-underground -->
- **Bugs it brings in (5):** tiger centipede (D21's cave centipede), cave beetle, cave glowworm (D21: with the glowing
  mushrooms, the mine's light), giant African millipede (D21's tougher cave millipede), daddy longlegs. **Also
  here:** black ants coming in through the dirt tunnels (decided, D21); cave flies, whose home is the Ant Colony's
  granaries (their lineup). No spiders yet (D21).
- **The food web:** water seeping down the walls and dead bugs feed the cave beetles; dead bugs and the ants' refuse
  feed the cave flies; flying cave flies end in the glowworms' threads; decaying plants in the dirt top feed the
  African millipedes; tiger centipedes hunt beetles, flies and ants; daddy longlegs scavenge small dead things.
- **Where they breed:** egg clumps on cave walls (glowworms), under stones (centipedes, brooding mothers), damp dirt
  (millipedes), the seeps (beetles), damp crevices (daddy longlegs).
- **The player's levers:** light (glowworms go dark when touched), smoke, stone against dirt, glowworm lanterns.
- **To build for it:** seeping-water spots on walls; glowworm lines on the walls and overhangs (caves show no
  ceilings, decided).

**Lenses:** Fit — D21's roster for this zone, each given its real species; the cave fly counted in the home its
lineup gives it. Picture the moment — blue stars along a wet seam of the mine wall, beside the rail. **Cost and
risk:** small per bug.

### P9. Ant Colony and its Queen (home, medium, deep) — the superorganism
<!-- key: 04.ant-colony-queen-home-medium -->
- **Bugs it brings in (1, with the ants' castes):** the cave fly, at the granaries and refuse heaps (its lineup's
  home); the black ants' warriors and their queen. **Also here:** tiger centipedes at the dirt-and-rock seam with the
  Centipede Cavern, eating ants (an ecosystem, not a raid — D79).
- **The food web:** everything the trails bring in — nectar, fruit, carcasses — feeds the brood and the queen; the
  refuse feeds cave flies; centipedes take ants at the seam.
- **A correction:** the old zone design's fungus gardens are leafcutter-ant farming; black garden ants don't farm
  fungus, so I propose food stores and brood chambers in their place.
- **Where they breed:** the queen's chamber and the nurseries; daughter colonies from mating flights.
- **The player's levers:** the bug stick, bait, blocking stones; killing the queen ends the colony until a new queen
  founds another (accepted, overview P13).
- **To build for it:** the queen, the warriors' formic acid, brood chambers, refuse heaps.
- **Thin:** one newcomer besides the castes; see Q3.

**Lenses:** Real biology — black garden ants' real diet (facts A). Fit — the colony and its Queen (D3). **Cost and
risk:** reuses the ant work.

### P10. Wasp Thicket (middle ring, medium) — the first place that fights back
<!-- key: 04.wasp-thicket-middle-ring-medium -->
- **Bugs it brings in (7):** yellowjacket, European hornet, forest scorpion, stag beetle, purple emperor, Chinese mantis
  (at its edges), luna moth. **Also here:** house flies at the rotten fruit.
- **The food web:** flowers and rotten fruit feed the yellowjackets, which hunt the caterpillars on the willows and
  walnuts and the flies at the rot (house flies, also here); the hornets from the hollow trees hunt yellowjackets, moths
  and mantises, and come to the ranger outpost's powered lights at night (D72); sap and rot bring the purple emperors
  down from the oaks, and willow scrub feeds their caterpillars; walnut and birch feed the luna caterpillars; dead wood
  feeds the stag beetles' grubs; forest scorpions under logs take the beetles and caterpillars of the woods' floor, and
  mantises at the edges hunt what passes.
- **Where they breed:** hidden ground and tree nests (yellowjackets), hollow trees (hornets), dead wood (stag beetles),
  walnut and birch (luna), willow scrub (purple emperor), twigs (mantis egg cases), under logs (scorpions).
- **The player's levers:** smoke, the outpost's powered lights (they draw hornets), mantis egg cases, the bug stick on
  beetles.
- **To build for it:** hollow trees, ground-nest entrances, dead wood with grubs, walnut, birch and willow scrub.

**Lenses:** Fit — the combat-intro zone (the zone sheet), with every threat from the real food web. Picture the moment
— the ranger outpost's powered lamp at midnight, and the hum of hornets. **Cost and risk:** the alarm call and the lights.

### P11. Butterfly Fields (middle ring, medium) — milkweed, beauty and the night glow
<!-- key: 04.butterfly-fields-middle-ring-medium -->
- **Bugs it brings in (4):** monarch, emperor dragonfly, orchid mantis, jumping spider. **Also here:** luna moths, queen
  butterflies, fireflies at night, bees; dragonhunters from the Millipede Forest along the river at its edge (P16).
- **The food web:** milkweed feeds the monarch and queen caterpillars, whose stored poison keeps most hunters off;
  flowers feed the butterflies and bees; orchid mantises among the flowers take pollinators; jumping spiders take
  caterpillars and small bugs; emperor dragonflies hunt butterflies and other dragonflies in the air; fireflies light
  the night, and their young hunt soft grubs in the damp soil by the pond.
- **Where they breed:** milkweed (monarchs, queens), host trees (luna), a pond or spring (emperor dragonflies — the zone
  has little water today), under stones and bark (jumping spiders), egg cases on stems (orchid mantises), damp ground
  (fireflies).
- **The player's levers:** milkweed and flowers, nets, a light trap for moths in the powered age, moving orchid
  mantises off a butterfly patch.
- **To build for it:** a pond for the emperor dragonflies' young; host trees for luna moths; the great milkweed stand.

**Lenses:** Fit — the aesthetic zone (the zone sheet), with a real reason for every beautiful thing. Picture the
moment — monarchs clustered on a milkweed stand, and a pink "flower" that eats one. **Cost and risk:** the water
block for one pond.

### P12. Hilltop Meadow (middle ring, medium) — advanced beekeeping under the hornets
<!-- key: 04.hilltop-meadow-middle-ring-medium -->
- **Bugs it brings in (1):** bombardier beetle. **Also here:** paper wasps a player keeps as pest control (§01), the
  European hornet (its top threat), bumblebees, field crickets, honeybees.
- **The food web:** flowers feed the bees; hornets hunt bees at the hives by day and come to powered lights at
  night; field crickets graze the dry turf; bombardiers hunt small bugs, such as young crickets, under stones at
  night. A gap: the bombardier's young are thought to live on other beetles' pupae, and no other beetle lives here
  yet (Q4).
- **Where they breed:** hives and boxes (bees), hollow trees (hornets), burrows (crickets), under stones (bombardiers).
- **The player's levers:** smoke, the stronger hives, the paper wasps kept against crop pests, light traps that draw
  hornets away from the hives in the powered age.
- **Thin:** one newcomer; see Q4.

**Lenses:** Fit — the step up from the Bee Meadow (the zone sheet). **Cost and risk:** small.

### P13. Centipede Cavern (middle ring, medium, deep) — glowworm light and the giant in the wall
<!-- key: 04.centipede-cavern-middle-ring-medium -->
- **Bugs it brings in (2):** giant centipede, cave spider. **Also here:** tiger centipedes in the upper halls,
  glowworms, cave beetles, cave flies, African millipedes, daddy longlegs; and D21's venomous millipede for these
  depths, which I propose is the shocking pink dragon millipede, the roster's poisonous one (its home is the Millipede
  Forest; here it is the game's placement).
- **The food web:** seeps and dead bugs feed the cave beetles and millipedes; cave spiders take millipedes and
  centipedes; glowworms take the cave flies on the wing; giant centipedes take big bugs from the cracks in the walls.
- **Where they breed:** wall hollows (spider egg sacs), cave walls and overhangs (glowworms), under stones
  (centipedes, brooding mothers), damp floors (millipedes), the seeps (cave beetles), the refuse of dead bugs (cave
  flies), damp crevices (daddy longlegs).
- **The player's levers:** light (spiders flee it, their young are drawn to it, glowworms go dark), smoke, stone.
- **Thin-ish:** two newcomers; see Q5.

**Lenses:** Fit — D21's deeper roster (spiders, the venomous centipede and a venomous millipede here, not in the
first mine); the view from above (no ceilings, decided). Picture the moment — the torch finds a white teardrop in a
hollow of the wall, then two feelers in the crack beside it. **Cost and risk:** the ambush block.

### P14. Underground River (middle ring, medium) — the dark river
<!-- key: 04.underground-river-middle-ring-medium -->
- **Bugs it brings in (1):** river crab. **Also here:** glowworms hanging their lines from the overhangs over the
  water (their lineup; real ones of their kind live in stream caves), cave flies, cave beetles.
- **The food web:** debris washed in feeds the crabs and beetles; glowworms over the water take the flies.
- **Where they breed:** the crabs in the banks, the glowworms on the walls and overhangs, the beetles at the seeps.
- **The player's levers:** the fish trap, light (glowworms go dark when disturbed), glowworm lanterns.
- **Thin:** one newcomer; see Q6.

**Lenses:** Fit — the water rung below the swamps (the zone sheet). **Cost and risk:** small.

### P15. Locust Farmland and the western town (far ring, hard) — holding the line
<!-- key: 04.locust-farmland-western-town-far -->
- **Bugs it brings in (3):** desert locust, Colorado beetle, killer bee. **Also here:** Chinese mantises; house crickets
  at the town's farm store.
- **The food web:** crops and wild green feed the locusts and the Colorado beetles (the tomato family); mantises take
  locusts and other bugs; flowers and crops feed the killer bees.
- **Where they breed:** bare soil (locust egg pods), crop leaves (beetle egg clusters), twigs (mantis egg cases),
  ground cavities and crevices (killer bees).
- **The player's levers:** harvesting locusts before they crowd, mantis egg cases, picking off egg clusters, trap
  crops, requeening killer bees.
- **Crossings:** locust swarms carry on into the next zones, with nothing to stop them (your wish, 2025-12-30; §01 P5
  proposes it).
- **To build for it:** tomato-family crops and wild nightshade for the Colorado beetles (a wheat zone otherwise has
  nothing for them); bare soil for egg pods.
- **Meets your guideline** with three newcomers; Q7 offers a fourth, a real enemy of the locusts' eggs.

**Lenses:** Fit — the embattled farm zone (the zone sheet), with the swarm as a cause and effect. **Cost and risk:** the
swarm-change block.

### P16. Millipede Forest (far ring, hard) — old growth and the hornets' raids
<!-- key: 04.millipede-forest-far-ring-hard -->
- **Bugs it brings in (4, 5 with the proposed bee):** northern giant hornet, Hercules beetle, shocking pink dragon
  millipede, the dragonhunter on the forest's river (moved from the underground, a correction: a dragonfly hunts by
  sight, and its real home is streams), and the Asian honey bee (open). **Also here:** giant centipedes, giant
  African millipedes, emperor dragonflies along the river; luna moths in the old trees (my proposal: real ones live
  in hardwood forests on walnut, hickory and birch).
- **The food web:** leaf litter and dead wood feed the millipedes and the Hercules grubs; fallen fruit and sap feed the
  adult beetles and the hornets; bees feed the giant hornets' young, and without the Asian honey bee they take the
  river's emperor dragonflies, big moths and beetles instead (all real prey); the dragonhunter takes the emperor
  dragonflies on the river; giant centipedes take millipedes and big bugs.
- **Where they breed:** rotten roots (giant hornet nests), fallen trees (Hercules grubs), leaf litter (millipedes, the
  dragon millipede's eggs among them), hives (Asian honey bees), the river's edges (dragonflies' young), host trees
  (luna caterpillars), under logs (giant centipedes, brooding mothers).
- **To build for it:** fallen trees and fruit trees for the Hercules beetles; walnut, hickory and birch for the lunas;
  the river's reedy edges; rotten-root nest sites.
- **The player's levers:** Asian honey bee hives, stopping a hornet scout before it brings a raid, rain (dragon
  millipedes come out after it).

**Lenses:** Fit — the deep woods and chitin armour (the zone sheet); your deadly dragonfly (D79) placed where danger
belongs. Real biology — the dragonhunter lives on streams (facts A). Picture the moment — a hornet scout at your hive.
**Cost and risk:** the raid; the water block for the river's dragonflies.

### P17. Scorpion Rocks (far ring, hard) — heat, cracks and deadly venom
<!-- key: 04.scorpion-rocks-far-ring-hard -->
- **Bugs it brings in (1):** fat-tailed scorpion. **Also here:** killer bees.
- **A gap:** the scorpions need prey, and the zone has almost none. The accepted field cricket really lives in warm,
  dry, sunny, gravelly ground (facts B), so I propose field crickets in the rocks' gravel and scrub as the scorpions'
  prey, and Q8 asks about new bugs.
- **The food web (with the crickets):** dry plants feed the crickets; fat-tailed scorpions take them from the cracks at
  night; flowers feed the killer bees.
- **Where they breed:** cracks and under stones (scorpions; real scorpion mothers carry their young), burrows
  (crickets), crevices (killer bees).
- **The player's levers:** an ultraviolet lantern (scorpions glow under it, real), heat gear, antivenom.
- **Thin:** one newcomer; see Q8.

**Lenses:** Real biology — the cricket's real habitat (facts B). Fit — the venom-and-mining zone (the zone sheet).
**Cost and risk:** small.

### P18. Shallow Swamp (far ring, hard) — water, reeds and biters
<!-- key: 04.shallow-swamp-far-ring-hard -->
- **Bugs it brings in (3):** horse fly, house mosquito, and the ant-decapitating fly, which hunts over the fire ants'
  columns by day. **Also here:** water striders, crayfish, emperor dragonflies, blue dashers (real marsh
  mosquito-eaters); the fire ants' foraging front up from the Deadly Ants (decided), with their mounds, mating flights
  and, after heavy rain, rafts on the water; the milkweed butterflies' caterpillars on swamp milkweed (my proposal: a
  real marsh plant that monarchs lay on).
- **The food web:** rot in still water feeds the mosquitoes' young; water striders and blue dashers eat them; female
  mosquitoes and horse flies bite people and the big caterpillars on the swamp milkweed (D66), so they breed with no
  player near; males of both drink nectar; crayfish eat plants, rot and small bugs; fire ants forage the edges; the
  decapitating flies lay their eggs in the fire ants.
- **Where they breed:** still water (mosquito rafts), wet mud (horse fly young), reeds and stones (horse fly eggs),
  banks (crayfish), underwater stems (striders), water plants (dragonflies), swamp milkweed (butterflies), mounds (fire
  ants), inside the fire ants (decapitating flies).
- **The player's levers:** sand on the marsh (D79), striders and dragonflies, light clothes and shade against horse
  flies, catching decapitating flies and releasing them over the mounds against the fire ants.
- **To build for it:** swamp milkweed; the mounds at the front; the water block.
- **Meets your guideline** with three newcomers; Q9 offers a fourth.

**Lenses:** Fit — the water zone (the zone sheet) and your sand rule (D79). **Cost and risk:** the water block.

### P19. Deadly Ants outpost (far ring, hard, underground) — the fire ants' front
<!-- key: 04.deadly-ants-outpost-far-ring -->
- **Bugs it brings in (1):** fire ants (workers and warriors), in galleries and chambers below the swamp. **Also
  here:** the decapitating flies' "zombie" ants wandering out of the galleries to die (the flies themselves hunt by
  day at the front in the Shallow Swamp, P18).
- **The food web:** fire ants eat nearly everything they meet and forage up into the Shallow Swamp; the decapitating
  flies' young grow inside the workers they struck at the front.
- **Where they breed:** the chambers below (the queens are deep in the core, P24); the mounds and mating flights
  happen at the front.
- **The player's levers:** releasing decapitating flies at the front, fire resistance, bait to draw the columns.
- **Thin:** one newcomer; see Q10.

**Lenses:** Fit — the endgame ant war (the zone sheet), given its real enemy. **Cost and risk:** the parasite block.

### P20. Underground River, deep (far ring, hard) — the sunken lake
<!-- key: 04.underground-river-deep-far-ring -->
- **Bugs it brings in:** none new yet — river crabs, glowworms and cave beetles continue from above. The dragonhunter
  that the bug lineups put on "the deep river" belongs on the Millipede Forest's river (P16): dragonflies hunt by sight
  and need daylight.
- **The food web:** with no daylight and no plants, the sunken lake lives on what the river carries down: leaves, dead
  bugs and fish remains settle on the lake floor and feed the crabs and beetles; crabs also take small fish (real);
  glowworms on the overhangs take the few flies.
- **Where they breed:** the crabs in the banks (their young ride with the mother, real), the glowworms on the walls and
  overhangs, the beetles at the seeps.
- **The player's levers:** the fish trap, light, diving gear; and what the player lets wash down from the river above
  (a carcass dropped upstream feeds the lake).
- **To build for it:** the still lake and its banks (the water block); food that drifts down from the river above.
- **Thin:** no newcomers; see Q11.

**Lenses:** Real biology — dark caves live on food carried in from outside (the cave beetle's and the cave
crayfish's facts); dragonflies hunt by sight (the July research). **Cost and risk:** small, once the water block
exists.

### P21. Spider Vale West (edge ring, extra hard) — hunters in the dark
<!-- key: 04.spider-vale-west-edge-ring -->
- **Bugs it brings in (2):** wolf spider, Brazilian wandering spider. **Also here:** jumping spiders, giant centipedes,
  daddy longlegs.
- **A gap:** like Scorpion Rocks, the hunters need prey. Field crickets really live on heath and dry sunny ground (facts
  B), which suits the vale's gorse; I propose them as the main prey.
- **The food web (with the crickets):** crickets feed the wolf spiders (from burrows), the wandering spiders (on the
  ground at night) and the jumping spiders (by day); giant centipedes take spiders; daddy longlegs scavenge.
- **Where they breed:** burrows (wolf spiders; mothers carry their young), silk sacs (wandering, jumping spiders),
  crickets' burrows, under stones and logs (giant centipedes, brooding mothers), damp crevices (daddy longlegs).
- **The player's levers:** a torch (eyeshine shows where wolf spiders wait), antivenom, keeping to the light.
- **Thin:** two newcomers; see Q12.

**Lenses:** Fit — the spider zone (the zone sheet). **Cost and risk:** small.

### P22. Spider Vale East (edge ring, the hardest surface zone) — webs, burrows and the tarantula's wasp
<!-- key: 04.spider-vale-east-edge-ring -->
- **Bugs it brings in (4):** black widow, Goliath tarantula, giant huntsman, tarantula hawk. **Also here:** daddy
  longlegs; garden millipedes, giant African millipedes and garden centipedes in the damp litter, as the prey base
  (my proposal: the vale is dim and damp, no place for the sun-loving field cricket).
- **The food web:** decaying leaves feed the millipedes; the widows' webs catch insects, millipedes, centipedes and
  harvestmen (real black widow prey); the Goliaths take large bugs, such as the African millipedes, from their
  burrows; huntsmen hunt bugs on the cave walls; tarantula hawks hunt the tarantulas and drink milkweed nectar.
- **Where they breed:** webs (widows' egg sacs), burrows (tarantulas), the caves (huntsmen), the paralysed tarantula in
  a burrow (tarantula hawks), the damp litter (millipedes, centipedes, daddy longlegs).
- **The player's levers:** cutting webs, a torch, antivenom.
- **To build for it:** milkweed in the vale for the tarantula hawks.

**Lenses:** Fit — the endgame surface (the zone sheet). Picture the moment — a rust-winged wasp dragging a tarantula.
**Cost and risk:** the parasite and web blocks.

### P23. Deep Swamp (edge ring, extra hard) — the quiet biters and the black water
<!-- key: 04.deep-swamp-edge-ring-extra -->
- **Bugs it brings in (1):** malaria mosquito. **Also here:** horse flies, crayfish, water striders, blue dashers,
  emperor dragonflies and their young in the weeds; the milkweed butterflies' caterpillars on swamp milkweed (my
  proposal, as in the Shallow Swamp).
- **The food web:** still, sunlit pools with plants feed the malaria mosquitoes' young; striders, blue dashers and the
  emperor dragonflies' young eat them; female mosquitoes bite people and big bugs such as caterpillars (D66), so they
  breed with no player near; horse flies bite at the sunny edges; crayfish eat plants, rot and small bugs.
- **Where they breed:** still, sunlit pools with plants (malaria mosquitoes; their young lie flat under the surface,
  real), wet mud (horse flies), banks (crayfish), underwater stems (striders), water plants (dragonflies), swamp
  milkweed (butterflies).
- **The player's levers:** sand on the marsh (D79), striders and dragonflies, diving gear, light clothes and shade
  against horse flies, remedies against the swamp's disease and poison.
- **To build for it:** still, sunlit pools with water plants; swamp milkweed; the water block, with diving.
- **Thin:** one newcomer, and the zone design wants an apex predator (the giant water bug, cut); see Q13.

**Lenses:** Fit — diving, disease and poison (the zone sheet; §01), and your sand rule (D79). Real biology — the
malaria mosquito's still, sunlit, planted water (facts B). **Cost and risk:** the water block, with diving.

### P24. Deadly Ants core (edge ring, extra hard, deep) — the war queen's fortress
<!-- key: 04.deadly-ants-core-edge-ring -->
- **Bugs it brings in:** the fire ant queen (the war queen, a boss — accepted, overview P13). **Also here:** fire ants,
  workers and warriors guarding the brood; the decapitating flies' "zombie" ants wandering in from above.
- **The food web:** everything the foragers carry down from the swamp front feeds the queen and her brood; the
  colony's dead are carried out to refuse chambers.
- **Where they breed:** the queens' chambers and the brood galleries; new queens leave on mating flights at the front.
- **The player's levers:** weaken the colony first — decapitating flies at the front thin the foragers that feed it,
  bait draws warriors away, fire resistance keeps you standing — then the queen fight (accepted, overview P13).
- **To build for it:** the war queen (the boss); brood chambers; the warriors' defence of the brood.
- **Thin by species:** the queen fight is the zone's headline; see Q14.

**Lenses:** Fit — the hardest underground zone, and the colony's heart. Picture the moment — the galleries going
quiet as the decapitating flies' work above starves the brood. **Cost and risk:** the boss.

## Questions
Your guideline (2025-12-30): each zone brings in three or four new species. Counting each bug in its home zone,
eleven zones fall short; the questions below take them one by one, plus three zones that meet it but have one strong
candidate. Every candidate is a real species checked for this game: it eats and breeds on things that exist in 2126
and in its zone, and none is a bug you cut. Following D79, they are recognisable or variants of known bugs, with now
and then a unique one. Nothing here joins the roster until you choose it. The checks, with sources:
`docs/product/investigations/research-2026-10-03/thin-zone-candidates.md` and `thin-zone-candidates-2.md`.

### Q1. Bee Meadow: a fourth new bug?
<!-- key: 04.bee-meadow-fourth-new-bug -->
Three new bugs today (bumblebee, death's-head hawkmoth, field cricket), which meets your guideline.
- **A.** The European beewolf: a wasp that catches honeybees on the flowers, stings them still and flies them to
  burrows in the dune belt by the coves, where its young eat them; in some places it really cuts honeybee numbers. A
  beekeeper finds the nest field and decides what to do about it. It needs only the honeybees already there.
- **B.** The hummingbird hawk-moth: a harmless day moth that hovers, humming, at flowers and comes back to the same
  beds at about the same time each day, so you learn its round; the death's-head's cousin, out by day. Its
  caterpillars need bedstraw, a plant to add.
- **C.** Both.
- **D.** Neither; three is enough here.

**Recommendation: A.** The meadow is where beekeeping starts, and the beewolf gives a beekeeper a real threat that
works the flowers rather than the hive, with a nest field to find in the dunes. It is plainly a wasp, so nobody is
puzzled. The hawk-moth is lovely, but it adds less to play.

### Q2. Ant Tunnels: what lives along the trails?
<!-- key: 04.ant-tunnels-lives-along-trails -->
One new species today (the black ants); the trails are the zone's heart, but it falls short of your guideline.
- **A.** The antlion: its young dig pits in the dry, loose soil under the cliff's overhangs, where the trails bend
  into the tunnel mouths, and catch the ants that slip in, throwing sand at any that climb (real; ants are its main
  food). You can lead ants round a pit with the bug stick, or past one you keep. The adult is a slow night flier.
- **B.** The silver-studded blue: a small blue butterfly whose caterpillars black garden ants really guard, for the
  sugary drops the caterpillars give them.
- **C.** Both.
- **D.** Neither; the trails are enough.

**Recommendation: A.** The antlion is the trail's everyday danger, and it makes the bug stick matter: steering ants
away from a pit, or feeding one. The butterfly brings back the trade of sugar for protection that went with the
aphids (D79).

### Q3. Ant Colony: who lives in the nest with the ants?
<!-- key: 04.ant-colony-lives-nest-ants -->
One new species besides the ants' own castes: the cave fly at the granaries (its lineup's home).
- **A.** The ant cricket: a tiny wingless cricket that rubs against the ants until it smells like one of them, then
  begs food from them (real for ant crickets with Lasius ants; the black garden ant itself isn't named). A thief an
  ant rancher learns to spot.
- **B.** The ant-nest case beetle: the ants themselves carry its eggs into the nest; its young live there for years in
  little cases they build, eating the colony's rubbish and some of its brood, and pull into the case when an ant
  touches them (real; the black garden ant is a recorded host). The adults are orange-red leaf beetles with black
  spots, out on the willows above, which play dead when bothered.
- **C.** The ant-nest hoverfly: its armoured, slug-shaped young live deep in the colony eating ant eggs and young (its
  link to the black garden ant is only "believed").
- **D.** A and B.

**Recommendation: D.** Both are real lodgers of black ants' nests, and both give an ant rancher something to manage:
a thief at the food and a guest in the brood that the ants themselves let in. With the cave fly the colony has three.
The hoverfly's slug-shaped young would puzzle players, and its tie to our ant is the weakest.

### Q4. Hilltop Meadow: what threatens the advanced beekeeper?
<!-- key: 04.hilltop-meadow-threatens-advanced-beekeeper -->
One new species today (the bombardier beetle), whose young need other beetles' pupae, which the meadow lacks.
- **A.** The large velvet ant: a wingless, armoured wasp that walks into bumblebee nests and lays its eggs on the young;
  it squeaks when caught and has a painful but not dangerous sting (real). Despite its name, it isn't an ant.
- **B.** A bee-killing robber fly with the garden chafer: the robber fly waits on a perch and catches bees in the air,
  looking like a bumblebee (real; in Argentina's honey country it can cut honey crops by up to four fifths). Its young
  need white grubs in the soil, which the garden chafer gives: a small day-flying beetle whose grubs live under the
  clover and grass, a real pest of grass and crops. The chafer's pupae can also feed the bombardier's young in the
  game (real ones use ground beetles' pupae).
- **C.** All three.
- **D.** Neither.

**Recommendation: B.** It adds a beekeeper's enemy in the air and a farmer's pest underground, gives the bombardier's
young their food, and makes three. The velvet ant is a fine threat to bumblebee boxes, but a wasp called an ant would
puzzle players in a game with two ants (D79).

### Q5. Centipede Cavern: a third new bug?
<!-- key: 04.centipede-cavern-third-new-bug -->
Two new today (giant centipede, cave spider).
- **A.** The whip spider: a flat hunter, harmless to you, whose whip-thin front legs, longer than its body many times
  over, sweep the dark for prey, which it spears on spiny arms (real); whip spider mothers carry their young on their
  backs, and rivals duel, the loser sometimes eaten (real for whip spiders). It lives in warm, damp caves, like the
  cavern's giant centipede.
- **B.** Neither; the giant centipede and the cave spider are the cavern.

**Recommendation: A.** It looks frightening and turns out harmless, which teaches a player to read a bug rather
than its looks, and it is the caves' one unique bug (D79 allows one now and then).

### Q6. Underground River: which bugs live in the dark water?
<!-- key: 04.underground-river-bugs-live-dark -->
One new today (the river crab); glowworms, cave flies and cave beetles also live here.
- **A.** The blind cave crayfish (the southern cave crayfish): pale and blind, it lives only in cave streams, first
  breeds at five or six years and lives over twenty (real). The slow, valuable crayfish beside the fast red swamp
  crayfish; like its cave relatives, it needs clean water.
- **B.** The dobsonfly: its young are the top hunters under the stones of fast, clean streams, and anglers really dig
  them up for bait; the adults are big night fliers, the males with long jaws that can't hurt you. Real ones live in
  surface streams; the fast river under the waterfall is the game's placement, and the bait suits the zone's cave
  fishing.
- **C.** Both.
- **D.** Neither.

**Recommendation: C.** The crayfish is a true cave animal with a farming role no other bug has (slow to raise, worth
the wait), and the dobsonfly gives the cave angler a bait to dig, so the river has three.

### Q7. Locust Farmland: a fourth new bug, against the locusts?
<!-- key: 04.locust-farmland-fourth-new-bug -->
Three new today (desert locust, Colorado beetle, killer bee), which meets your guideline.
- **A.** The Chinese blister beetle: its young hunt out buried locust egg pods and eat the eggs (real, on migratory
  locust eggs; desert locust eggs aren't named); its adults eat bean and alfalfa leaves; its body holds a poison that
  blisters skin, so it is never grabbed bare-handed.
- **B.** Neither; three is enough here.

**Recommendation: A.** It is a real enemy of the locusts at the one moment that matters, before they crowd, and a
farmer can encourage it at a price: the adults eat crops and burn the hands that catch them.

### Q8. Scorpion Rocks: what else lives in the hot rocks?
<!-- key: 04.scorpion-rocks-else-lives-hot -->
One new today (the fat-tailed scorpion); field crickets are proposed as its prey (P17).
- **A.** The camel spider: a fast night hunter that eats scorpions, and by day follows your shadow for the shade it
  gives (real) — a scare that turns out to be about shade; a painful bite, but no venom.
- **B.** The six-eyed sand spider: it hides under warm rocks and lies buried in sand, and its venom kills skin (real),
  the zone's deadly venom in a spider.
- **C.** The desert stink beetle: a harmless beetle of the rocks that stands on its head and squirts a foul spray when
  bothered (real); the zone's common, easy catch.
- **D.** A and C.

**Recommendation: D.** A runner that hunts the scorpions and a harmless beetle with a warning you can read give the
zone a fearsome-looking bug that isn't and a gentle one, beside the deadly scorpion. The sand spider is real and good,
but a second deadly venom in one zone blurs the scorpion's role.

### Q9. Shallow Swamp: a fourth new bug?
<!-- key: 04.shallow-swamp-fourth-new-bug -->
Three new: the horse fly, the house mosquito, and the ant-decapitating fly, which hunts over the fire ants' columns
here (P18).
- **A.** The six-spotted fishing spider: it runs on the water, dives and stays under for up to ninety minutes in a coat
  of air, catches fish, and guards nursery webs on the swamp plants (real).
- **B.** The water scorpion: an ambush biter in the shallows, given away by the tip of its breathing tube at the
  surface (real); not a true scorpion, a water bug with a scorpion's look.
- **C.** Neither; three is enough.

**Recommendation: A.** A spider that hunts the water's skin and dives out of reach is a fine sight for the zone of
the water gear, and it sets up its bigger cousin in the Deep Swamp (Q13). The water scorpion's name would puzzle
players (D79).

### Q10. Deadly Ants outpost: who lives off the fire ants?
<!-- key: 04.deadly-ants-outpost-lives-off -->
One new species today (the fire ants); the decapitating flies hunt them at the front in the Shallow Swamp.
- **A.** Orasema wasps: small wasps that lay their eggs in the swamp's plants; their young ride foraging fire ants down
  into the nest and grow on the ants' pupae, fed by the ants as if they were their own brood (real) — a thread from the
  swamp into the galleries.
- **B.** The twisted-wing parasite: fire ants it infects climb to high perches and freeze there (real), a sign that
  something is wrong in the colony; its females live inside crickets.
- **C.** The fire ant scarab: a small beetle that lives in fire ant nests, eating brood and taking on each colony's
  smell (real, but little is written about it).
- **D.** A and C.

**Recommendation: D.** Two recognisable nest thieves, a wasp and a beetle, both working against the colony the player
fights. The twisted-wing parasite is the strangest of the three and would puzzle players, and its frozen ants repeat
the decapitating fly's "zombies".

### Q11. Underground River, deep: anything new in the sunken lake?
<!-- key: 04.underground-river-deep-anything-new -->
No new species today; river crabs, glowworms and cave beetles continue from above.
- **A.** The cave amphipod (Niphargus): a blind, white, shrimp-like hunter of underground water that can go more than
  two hundred days without food; in one cave it lives in a food web run on bacteria, with no sunlight at all (real).
- **B.** The Kentucky cave shrimp: a clear-bodied shrimp of cave pools (real; little is known of its life).
- **C.** Both.
- **D.** Neither; the deep lake is for fishing and diving, and its bugs come from above.

**Recommendation: C.** Two pale crustaceans, kin to the crabs and crayfish players know, give the lake its own life;
even so the zone stays below your guideline, which its fishing and diving can carry.

### Q12. Spider Vale West: more spiders?
<!-- key: 04.spider-vale-west-more-spiders -->
Two new today (wolf spider, Brazilian wandering spider).
- **A.** The ladybird spider: it lives in a silk-lined burrow in dry, sandy, sunny heath with a trap at the mouth; the
  males are red and black like a ladybird; the young end by eating their mother (real); its bite brings pain
  and fever.
- **B.** The net-casting spider: at night it hangs holding a small silk net between its front legs and casts it over
  passing prey, crickets among them (real); it lives on heathland.
- **C.** Both.
- **D.** Neither.

**Recommendation: C.** Both are spiders, so nothing puzzles, and each hunts its own way: a burrow trap and a thrown
net, beside the wolf spider's burrow ambush and the wandering spider's night walks. The vale reaches four.

### Q13. Deep Swamp: which bugs, and its apex hunter?
<!-- key: 04.deep-swamp-bugs-apex-hunter -->
One new today (the malaria mosquito); the zone's design wants an apex predator, and the giant water bug is cut.
- **A.** The diving bell spider: it lives underwater in a bell of silk filled with air carried down on its hairs, and
  darts out at prey that touches its threads (real); the diving zone's own bug. It needs clean water, so it lives in
  the swamp's clearer pools.
- **B.** The Okefenokee fishing spider: the six-spotted fishing spider's bigger, swamp-only cousin (females about 30
  mm), the swamp's top hunter on and under the water; little is known of its own habits, so it would behave like its
  cousin.
- **C.** Both, with the emperor dragonfly's young as the hunter in the weeds: big and very aggressive in real weedy
  ponds, and already on the roster as the emperor's own young.
- **D.** Neither.

**Recommendation: C.** Three new species, the diving theme in a bug, and an apex that needs no invented animal: the
big fishing spider above the water and the emperor's young below it.

### Q14. Deadly Ants core: anything besides the war queen?
<!-- key: 04.deadly-ants-core-anything-besides -->
No new species; the war queen is the zone's boss (accepted, overview P13).
- **A.** As it is: the war queen, her warriors and brood, and the outpost's nest guests at their thickest around her
  brood. No other real species was found that fits: the one parasite of queen larvae found lives with another ant.
- **B.** Look further, for one species of the core's own.

**Recommendation: A.** The queen fight carries the zone, and the colony's own guests show the player how close the
heart is; a species found only to fill the count would be weaker than the ones already there.

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

