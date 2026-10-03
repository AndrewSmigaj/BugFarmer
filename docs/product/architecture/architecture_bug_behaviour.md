# Bug behaviour — how every bug gets built (PROPOSED, 2026-10-03)

**Status: a plan for the owner's review. Nothing here is built unless a line says so.** No bug is finished yet: the
fifteen in the prototype each get their behaviour polished or redone, and the other forty-three decided bugs aren't in
the game yet (the owner's rule, §03 "Every bug is unfinished", 2026-09-27).

What each bug should do is in GDD §03 (one proposal per bug); how each zone's bugs live together is in GDD §04
(one proposal per zone). This document is the engineering side: what the engine does today, the shared pieces
every bug is built from, the order of work, and how each bug is tested and signed off.

## In short (for the owner)
1. **One set of building blocks, then bugs.** About a dozen mechanics are shared by many bugs: following a trail,
   leaving a group, living in a nest, breeding in water, hunting from ambush, spinning a web, glowing, spraying a
   defence, a day-and-night routine. Each block is built once, tested once, and reused; a bug is then mostly data
   (its numbers, its foods, its homes) plus one signature mechanic of its own.
2. **Zone by zone, in the roadmap's order.** First the five zones around home (Village, Bee Meadow, Ant Tunnels,
   Mining Camp, Ant Colony), redoing their bugs and adding their newcomers; then each later ring as its zone is
   built. A zone's bugs are tuned together, because they eat each other.
3. **Every bug is signed off by you.** For each bug: its sheet (§03) agreed first; then built in a pen in the Bug
   Lab test zone, where you can watch it feed, breed, hunt and react to you; a short recording and the test
   results come with it. A zone is signed off when its bugs live together in it the way §04 describes.
4. **Behaviour before numbers.** A bug's behaviour is finished before its numbers are tuned (accepted, overview
   P10); then the zone's food web is balanced with the existing tuning tools.

## 1. The engine today (as built, checked 2026-10-03)
- **Bugs live in groups ("swarms") of 1–60 with a per-bug simulation.** Every player's computer runs each bug's
  movement the same way, in fixed-point maths with a shared random seed (`BugAgent.cs`, `FixedPoint.cs`); the
  server sends a small ledger of events (a group's new target, a bug removed, a group spawned or split) that every
  computer applies at the same tick, and a per-tick check catches and repairs any drift
  (`architecture_swarm_sync.md` §0). This is why bug behaviour lives on the players' computers, not the server:
  rich behaviour for hundreds of bugs would cost too much network traffic otherwise (the owner's rule).
- **Five ways of moving** (`MovementFactory.cs`): jittering (flies, bees), gliding (butterflies, fireflies),
  darting (wasps, the hornet, the dragonfly), crawling (millipede, carrion beetle, ants) and the centipede's
  segmented run.
- **Three reactions to a player** (`species.json` `player_reaction`): flee (fly), curious (butterfly), attack
  (wasps, hornet, centipedes); the rest ignore you. Bees and ants sting only to defend.
- **Combat** is built and shared: a per-bug telegraphed sting or bite you can dodge, chase ranges, the centipede's
  lunge, night-only attackers, smoke that calms (`architecture_combat.md`, the `combat-enemy` skill).
- **Food and breeding** come in four shapes (`ecology_parameters.md`): bugs that breed where they feed (the fly on
  rot, the carrion beetle on carcasses, the millipede in leaf litter); eggs on a host plant (the butterfly on
  milkweed); nests that hatch new bugs and found daughter nests (wasps, hornet, bees, ants); and a "well fed"
  timer (centipedes). Hunters strike one prey bug at a time (a wasp kills and eats one fly).
- **Ant trails** (`colony.go`): scouts remember their walk to food, register the site, and recruit workers, who
  march the remembered route; sites fade unless traffic renews them. It works per group, not per ant, so a single
  ant can't be led away from the others today.
- **Ecology control**: per-zone population bands, reseeding of a species that dies out, rain and drought as levers,
  hard caps against crashes, and a tuning rig that runs the Bug Lab at six times speed (`ecology-tuning` skill).
- **Gaps already known** (BACKLOG, 2026-10-03): the centipedes eat only flies and have no breeding place; the
  dragonfly never breeds and eats only the paper wasp; the firefly has no food; the hornet's nest has no picture
  or zone; the yellowjacket shares the paper wasp's nest.

## 2. Rules every new behaviour follows
- **On the players' computers, identical everywhere.** Anything a bug's movement depends on reaches every
  computer through the ledger or the join snapshot, never through a message only some players get; fixed-point
  maths only; random choices from the shared seed; lists sorted before they're walked. The `frontier-sync` skill
  is the recipe, and every new block passes the `test-changes` gates (Go tests, the replay check, and the
  two-player late-join check, run so the new behaviour actually fires).
- **Cheap enough for hundreds of bugs.** Per-bug decisions run a few times a second, not every frame; anything
  that looks across the map (a trail field, a light) is a small grid of cells, not a search over every bug.
- **Groups where it doesn't matter, individuals where it does.** Flies and gnats can stay in groups; a bug the
  player handles, follows or fights acts on its own (an ant you tap, a wasp guarding its nest, a spider at its
  web). This builds on the individual ecology design (`investigations/individual_ecology_redesign.md`), one block
  at a time rather than all at once.
- **Real biology first.** A behaviour is in because the real animal does it (the facts and their sources:
  `investigations/research-2026-10-03/bug-ecology-facts-A.md`, `-B.md`); where 2126 lacks what it needs (no
  mammals, birds, reptiles or snails), the stand-in is named in the bug's sheet.
- **Telegraphed danger.** Anything that hurts the player warns first and can be dodged (the combat foundation).

## 3. The building blocks
Each block lists the bugs that need it, what exists, and what to build. The state class (who owns it, how it
syncs) follows the `frontier-sync` classification.

| # | Block | Bugs that use it | Exists today | To build |
|---|---|---|---|---|
| B1 | **Leave the group, act alone** (split off on a stimulus, follow, rejoin) | ants, any bug you tap, herd or lure | groups split and merge for population; one wasp can hunt one fly | per-bug goals that can pull a bug out of its group and back (a split event naming the bug ids), the individual "brain" from the redesign |
| B2 | **Trails** (scent paths that strengthen with use and fade) | black ants, fire ants (and marching locust bands) | per-group remembered routes, scout recruitment, fading sites | per-ant trail following on a cell grid, so taps, leading and new trails work ant by ant (§4) |
| B3 | **The bug stick** (tap, steer, lead; non-lethal) | ants first; later any walker (beetles, crickets, millipedes) | none | an item, a tap that sends a ledger event naming the tapped bugs, and the follow behaviour (B1) |
| B4 | **Day, night and weather routines** | every bug (fireflies, moths and the hornet at night; mosquitoes at dusk; dragon millipedes after rain; bumblebees in cool weather) | a night-only switch for attacks | an activity schedule per species: when it's out, where it rests (under logs, in cracks, in the nest), and what rain or drought does |
| B5 | **Nests and colonies** (castes, brood, a queen, defence, new colonies) | ants, wasps, hornets, bees, bumblebees | nests that hatch bugs, found daughter nests, recall defenders; swarms claim empty hive boxes | one nest per species (each its own nest picture, so species don't steal each other's nests), visible castes, a queen, raids on other nests (the giant hornet), requeening (the killer bee), the bumblebee box |
| B6 | **Life stages in the world** (eggs, larvae, pupae you can see and take) | butterflies and moths, the silk moth, beetle grubs, mantis egg cases, spider egg sacs, fireflies, the glowworm | the butterfly's eggs, caterpillars and chrysalis on milkweed | the same model on other hosts: the mulberry (silkworms), dead wood (stag and Hercules grubs), stems (mantis egg cases), cave roofs (cave spider egg sacs) |
| B7 | **Water life** (eggs and young in water, adults over it) | dragonflies, mosquitoes, the water strider, the crayfish, the horse fly, the river crab | water is only a tile today: it stops people, and every bug crosses it (`BugCollision.cs`; whether it should stop crawling bugs is §01 Q1, open) | water cells as a habitat: young that live in still or running water, adults that hunt over it, sand laid on the marsh that stops mosquito breeding |
| B8 | **Ambush and lures** (wait still, strike; draw prey in) | mantises, the orchid mantis, the giant centipede (from the ceiling), the glowworm (sticky lines), wolf spiders and tarantulas (from burrows), scorpions (from cracks) | the centipede lunge | a "wait at a spot" state, a lure the prey bugs read (a glow, a flower shape), and a strike from rest |
| B9 | **Webs and silk lines** (fixed traps) | the black widow, the cave spider, the glowworm | none | a web as a world object: it catches small bugs, slows a player who walks into it, can be cut for silk |
| B10 | **Defences** (spray, cloud, curl, drop a leg, hiss, hairs) | the bombardier beetle, the millipedes, the black ants (formic acid), the daddy longlegs, the Goliath tarantula, the monarch (poison) | flee, sting to defend | a small hazard area (spray, cloud) with a telegraph, a curl-up state that ignores taps, a dropped-leg decoy, warning marks the hunters read |
| B11 | **Lights and sounds** (flashes, glows, songs) | fireflies (flash codes), the glowworm, the field cricket's song, the death's-head's squeak, the Goliath's hiss; the hornet and moths drawn to lamps | lights exist for the player and objects | a bug light the lighting system draws; lamps that draw night flyers (a cell-grid attraction); sounds tied to behaviour |
| B12 | **Parasites and burial** (lay in or on another bug) | the tarantula hawk (on a tarantula), the ant-decapitating fly (in a fire ant), the burying beetle (buries a carcass) | carcasses as food | a "host" link between two bugs: a paralysed tarantula dragged to a burrow, a fire ant that stops and dies, a carcass that sinks into the ground and becomes a brood |
| B13 | **Swarm change** (crowding turns solitary into swarming) | the locust | none | a crowding count per cell area that flips a group's form and behaviour, marching bands then flying swarms |
| B14 | **Player tools on bugs** | all | net, smoker, bait dishes (designed, P4), fences, hive boxes | the bug stick (B3), lamps as lures (B11), the fish trap for crayfish and crabs, sand for marshes, host plants as nurseries |

Building a block means: the design in this document; the deterministic implementation (`frontier-sync`); a Bug Lab
pen that shows it; the gates; then the bugs that use it.

## 4. Worked example: ant trails you can lead ants off
The owner's example (2026-10-03): ants follow a trail; tapping some with the bug stick makes them veer off it, so a
player can take, say, five ants somewhere else while the rest keep going down the old route.

**Proposed design** (to be scored against the alternatives in `research-2026-10-03/bug-mechanics-in-games.md`):
- **Trails are scent on cells.** Each colony keeps a small grid of trail strength (one value per cell near its
  nest). An ant walking home with food marks the cells it crosses; marks fade over time; an ant leaving the nest
  follows the strongest marked cells toward food. This is how real ants work (trail pheromone laid by successful
  foragers, evaporating unless renewed), it makes trails emerge and straighten on their own, and it is cheap: one
  number per cell, updated at a fixed rate in fixed-point.
- **A tap takes those ants off the trail.** The bug stick taps the ants under it (one tap catches one to a few
  ants, the number set per tool tier). The tap is a ledger event naming those ant ids, so every computer agrees.
  Tapped ants stop following scent and follow the stick instead, for a while (the bug follows the player's
  position, which every computer already shares).
- **The rest keep going.** Untapped ants still follow the scent, so the column carries on down the old route.
- **Bring them to food and they start a new trail.** If the led ants reach food, they eat, pick up a load and walk
  home marking the cells; other ants find the new scent and follow it; if the new food is better or nearer, the
  new trail grows and the old one fades. If they find nothing, they drift back to the old trail.
- **Why this is fun:** you can feed a colony by leading a few ants to your carcass pile, pull ants away from your
  crops, or set up a trail that runs past your bug catcher. It's the real biology, and every outcome comes from
  the player's choices.
- **Build steps:** (1) the trail grid as zone state (snapshot carrier + hash, `frontier-sync` per-zone dict
  pattern); (2) per-ant scent following inside the existing group movement; (3) the tap event and the follow
  state (B1, B3); (4) a Bug Lab pen with a nest, two food sites and a player; (5) gates, then the owner's sign-off.

## 5. Order of work
The roadmap's phases set the order (ROADMAP.md): the five zones around home are rebuilt to final quality in
Phase 2, the other rings as each zone is built in Phase 3.

1. **Foundation** (before any zone): B1 leave the group, B4 routines, the per-bug brain; then the blocks the home
   zones need first: B2 trails and B3 the bug stick (ants), B5 nests (wasps, bees, ants), B6 life stages
   (butterfly, silk moth), B7 water life (the village pond's dragonfly, water strider, crayfish), B10 defences
   (millipede), B11 lights (firefly, glowworm).
2. **Ring A — the five home zones**, one zone at a time: redo every bug already there to its §03 sheet, add the
   newcomers, then tune the zone's food web (§04). Village → Bee Meadow → Ant Tunnels → Mining Camp → Ant Colony.
3. **Ring B, C and D** with their zones (Phase 3): each zone's newcomers built with the zone (the `zone-craft`
   skill), using the blocks; new blocks (B8 ambush, B9 webs, B12 parasites, B13 swarm change) arrive with the
   first zone that needs them.

**Each bug, in order:** its sheet agreed (§03) → data (`species.json`: numbers, foods, homes, attacks) → behaviour
(blocks plus its signature mechanic) → its picture (paid image calls are asked for first, per batch) → a Bug Lab
pen → the gates → your sign-off → placed in its zone → tuned with the zone.

**When a bug counts as done:** it does what its sheet says; it passes the determinism gates with its behaviour
actually firing; it has its final art, its carcass item and its examine facts (P8); it holds its population band
in its zone without the safety net doing the work; and you have signed it off.

## 6. Testing and sign-off
- **Per block:** Go unit tests for the server side; the `sim-determinism` replay; the two-player late-join check,
  co-located and spawn-apart, with the block firing during the join (`test-changes` skill).
- **Per bug:** a pen in the Bug Lab (`nakama/data/zones/bug_lab/`, built by `tools/ecology/make_bug_lab.py`) with
  its food, its breeding place, its predator and its prey; a headless run that logs what it did (fed, bred,
  hunted, fled, died of what); a short recording or screenshots from the Unity command line for you.
- **Per zone:** the six-times-speed ecology runs (`ecology-tuning` skill) over several game days, showing every
  species inside its band, births coming from its own breeding rather than reseeding, and the food chains §04
  describes actually feeding each other.

## 7. Risks
- **The individual brain is the big piece.** Moving more of each bug's decisions onto the players' computers,
  identically, is a large job (the redesign doc is honest about it). Mitigation: one block at a time, each with
  its gates, starting with the ants.
- **Performance.** Hundreds of individually-acting bugs; mitigation: decisions a few times a second, cell grids
  instead of searches, groups kept wherever individuals don't matter.
- **Art.** Forty-three new bugs need pictures and animations; each batch is a paid request asked for first.
- **Tuning knock-on.** Every behaviour change moves a zone's numbers; the zone is retuned after its bugs change,
  never before (P10).

## 8. Sources
- `architecture_swarm_sync.md` §0 and §14; `architecture_combat.md`; `ecology_parameters.md`;
  `investigations/individual_ecology_redesign.md`; `nakama/modules/world/colony.go`; `nakama/data/species.json`.
- Facts per bug: `investigations/research-2026-10-03/bug-ecology-facts-A.md` and `-B.md`.
- How games do it: `investigations/research-2026-10-03/bug-mechanics-in-games.md`.
