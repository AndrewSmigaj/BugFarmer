# Bug behaviour — how every bug gets built (PROPOSED, 2026-10-03)

**Status: a plan for the owner's review. Nothing here is built unless a line says so.** No bug is finished yet: the
fourteen roster bugs in the prototype (fifteen entries, as the black ants' workers and scouts are two) each get their
behaviour polished or redone, and the other forty-four (two of them still open) aren't in the game yet (the owner's
rule, §03 "Every bug is unfinished", 2026-09-27 and 2026-10-03).

What each bug should do is in GDD §03 (one proposal per bug); how each zone's bugs live together is in GDD §04
(one proposal per zone). This document is the engineering side: what the engine does today, the shared pieces
every bug is built from, the order of work, and how each bug is tested and signed off.

## In short (for the owner)
1. **One set of building blocks, then bugs.** About fifteen mechanics are shared by many bugs: following a trail,
   leaving a group, living in a nest, breeding in water, hunting from ambush, spinning a web, glowing, spraying a
   defence, a day-and-night routine. Each block is built once, tested once, and reused; a bug is then mostly data
   (its numbers, its foods, its homes) plus one signature mechanic of its own.
2. **Zone by zone, in the roadmap's order.** First the five zones around home (Village, Bee Meadow, Ant Tunnels,
   Mining Camp, Ant Colony), redoing their bugs and adding their newcomers; then each later ring as its zone is
   built. A zone's bugs are tuned together, because they eat each other.
3. **Every bug is signed off by the owner.** For each bug: its sheet (§03) agreed first; then built in a pen in the
   Bug Lab test zone, where the owner can watch it feed, breed, hunt and react to a player; a short recording and the
   test results come with it. A zone is signed off when its bugs live together in it the way §04 describes.
4. **Behaviour before numbers.** A bug's behaviour is finished before its numbers are tuned (accepted, overview
   P10); then the zone's food web is balanced with the existing tuning tools.
5. **Ants first, the way real ants work.** Trails become scent on the ground that each ant follows on its own, so the
   owner's example works: two taps of the bug stick and five ants follow the player while the column carries on, and if
   the player leads them to food a new trail grows (§4). Before any routine, the day's clock and rain have to reach the
   bug simulation; today they don't (§1).

## 1. The engine today (as built, checked 2026-10-03)
- **Bugs live in groups ("swarms") of 1–60 with a per-bug simulation.** Every player's computer runs each bug's
  movement the same way, in fixed-point maths with a shared random seed (`BugAgent.cs`, `FixedPoint.cs`); the
  server sends a small ledger of events (a group's new target, a bug removed, a group spawned or split) that every
  computer applies at the same tick, and a per-tick check catches and repairs any drift
  (`architecture_swarm_sync.md` §0). Movement lives on the players' computers because rich behaviour for hundreds of
  bugs would cost too much network traffic otherwise; the rule is that per-bug behaviour belongs there, and whatever
  still runs on the server must justify itself (D58).
- **What runs where today.** The players' computers run each bug's movement, its reactions to players, a hunter's
  choice of which prey bug it strikes, and the centipedes' combat logic. The server still runs feeding, breeding, eggs
  and grubs, nests, the ants' memory of food sites, the re-aiming of hunts and the night gate
  (`individual_ecology_redesign.md`; `brood.go`; `colony.go`; `predation.go`). How fast the rest moves over is the
  owner's call (GDD §03 Q1).
- **Five ways of moving** (`MovementFactory.cs`): jittering (flies, bees), gliding (butterflies, fireflies),
  darting (wasps, the hornet, the dragonfly), crawling (millipede, carrion beetle, ants) and the centipede's
  segmented run.
- **Three reactions to a player** (`species.json` `player_reaction`): flee (fly), curious (butterfly), attack
  (wasps, hornet, centipedes); the rest ignore players. Bees and ants sting only to defend.
- **Combat** is built and shared: a per-bug telegraphed sting or bite a player can dodge, chase ranges, the centipede's
  lunge, night-only attackers, smoke that calms (`architecture_combat.md`, the `combat-enemy` skill).
- **Food and breeding** come in four shapes (`ecology_parameters.md`): bugs that breed where they feed (the fly on
  rot, the carrion beetle on carcasses, the millipede in leaf litter); eggs on a host plant (the butterfly on
  milkweed); nests that hatch new bugs and found daughter nests (wasps, hornet, bees, ants); and a "well fed"
  timer (centipedes). Hunters strike one prey bug at a time (a wasp kills and eats one fly).
- **Ant trails** (`colony.go`): scouts remember their walk to food, register the site, and recruit workers, who
  march the remembered route; sites fade unless traffic renews them. It works per group, not per ant, so a single
  ant can't be led away from the others today. The code's own notes record that scouts' routes tangle in open
  ground, so marchers fall back to a straight line.
- **Time and weather don't reach the bug simulation.** The time of day is worked out from the shared tick for
  display only, and rain is a message each computer applies when it arrives (`architecture_weather.md`, "the
  frontier rule"). The night-only attacks are decided on the server (`isNightForHunting`, `handlers_env.go`).
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
  player handles, follows or fights acts on its own (an ant the player taps, a wasp guarding its nest, a spider at its
  web). This builds on the individual ecology design (`investigations/individual_ecology_redesign.md`); whether the
  rest of each bug's life moves over block by block or all at once is the owner's call (GDD §03 Q1).
- **Real biology first.** A behaviour is in because the real animal does it (the facts and their sources:
  `investigations/research-2026-10-03/bug-ecology-facts-A.md`, `-B.md`); where 2126 lacks what it needs (no
  mammals, birds, reptiles or snails), the stand-in is named in the bug's sheet.
- **Telegraphed danger.** Anything that hurts the player warns first and can be dodged (the combat foundation).
- **Who eats whom is data.** Which species eats, fears, ignores or gathers with which is one table that both the
  server and the game read, with each bug's small differences (bolder, shyer) worked out from its id; fifty-eight
  species then need no special code per pair (Rain World's approach, research Part 1 S20).
- **Shared maps, not one path per bug.** Where many bugs head for the same place (ants walking home to their nest),
  one map of the distance to it is built per place and read by every bug in one lookup, and rebuilt only when
  blocking objects change. This is the simplest piece of Supreme Commander 2's flow fields (S23); the July combat
  research turned down that game's full system (sectors, portals, a cache) as too much for moving groups
  (`deep_research_2026-07/combat/02_swarm_group_ai.md`), and nothing here brings it back.
- **Simplify only by shared rules.** If bugs far from every player run a simpler version of themselves, the choice
  comes from data every computer shares (how far the nearest player is), never from one computer's own speed
  (S25, S27).

## 3. The building blocks
Each block lists the bugs that need it, what exists, and what to build; the list after the table says how each one
keeps every computer in step (the `frontier-sync` classes).

| # | Block | Bugs that use it | Exists today | To build |
|---|---|---|---|---|
| B1 | **Leave the group, act alone** (split off on a stimulus, follow, rejoin) | ants, any bug a player taps, herds or lures | groups split and merge for population; one wasp can hunt one fly | per-bug goals that can pull a bug out of its group and back (a split event naming the bug ids), the individual "brain" from the redesign: the most urgent need wins (hunger, home, safety, curiosity), and each species keeps its own distance from a player, so walking behind a group herds it (Game AI Pro ch. 44; the sheepdog study, S5, S24) |
| B2 | **Trails** (scent paths that strengthen with use and fade) | black ants, fire ants (and marching locust bands) | per-group remembered routes, scout recruitment, fading sites | scent on cells, laid only by ants carrying food home and followed ant by ant, with a small stray chance per ant and "no entry" scent at food that ran out (§4) |
| B3 | **The bug stick** (tap, steer, lead; non-lethal) | ants first; later any walker (beetles, crickets, millipedes) | none | an item; two taps sent as ledger events (stop, then follow); following in a loose line behind the player; drop-out rules and a short cool-down (§4; Pikmin, SimAnt) |
| B4 | **Day, night and weather routines** | every bug (fireflies, moths and the hornet at night; mosquitoes at dusk; dragon millipedes after rain; bumblebees in cool weather) | a night-only switch for attacks, decided on the server; time and rain don't reach the bug simulation (§1) | first, time and rain as simulation inputs: the clock from the shared tick, and a clock change and each shower's start and stop as ledger events (the weather doc's deferred design); the shower is scheduled a day ahead, so bugs can settle before it. Then an activity curve per species: when it's out, where it rests (under logs, in cracks, in the nest), and what rain does |
| B5 | **Nests and colonies** (castes, brood, a queen, defence, new colonies) | ants, wasps, hornets, bees, bumblebees | nests that hatch bugs, found daughter nests, recall defenders; swarms claim empty hive boxes | one nest per species (each its own nest picture, so species don't steal each other's nests), visible castes, a queen; jobs by age (young inside, old foraging); nests that answer in steps (a few guards come to look, all come out when the nest is hit, a few more per extra player — Don't Starve); a hurt worker that brings the guards (Grounded); smoke as a patch that cancels alarm; raids on other nests (the giant hornet), requeening (the killer bee), the bumblebee box |
| B6 | **Life stages in the world** (eggs, larvae, pupae a player can see and take) | butterflies and moths, the silk moth, beetle grubs, mantis egg cases, spider egg sacs, fireflies, the glowworm | life stages as counts at their source, shown on it: eggs, larvae and pupae on the milkweed, in rot and in nests (`brood.go`) | D38's caterpillars that leave the nursery, grow out in the world and pupate there (bugs run on the players' computers, so they need the sync work, BACKLOG); the same model on other hosts: the mulberry (silkworms), dead wood (stag and Hercules grubs), stems (mantis egg cases), hollows in cave walls (cave spider egg sacs) |
| B7 | **Water life** (eggs and young in water, adults over it) | dragonflies, mosquitoes, the water strider, the crayfish, the horse fly, the river crab | water is only a tile today: it stops people, and every bug crosses it (`BugCollision.cs`; whether it should stop crawling bugs is §01 Q1, open) | water cells as a habitat: young that live in still or running water, adults that hunt over it, sand laid on the marsh that stops mosquito breeding |
| B8 | **Ambush and lures** (wait still, strike; draw prey in) | mantises, the orchid mantis, the giant centipede (from cracks in the walls), the glowworm (sticky lines), wolf spiders and tarantulas (from burrows), scorpions (from cracks) | the centipede lunge | a "wait at a spot" state, a lure the prey bugs read (a glow, a flower shape), and a strike from rest; trap cells the prey's own movement checks (the cheapest hunters to run); dragonflies aiming where prey is going, not where it is |
| B9 | **Webs and silk lines** (fixed traps) | the black widow, the cave spider, the glowworm | none | a web as a world object: it catches small bugs, slows a player who walks into it, can be cut for silk |
| B10 | **Defences** (spray, cloud, curl, drop a leg, hiss, hairs) | the bombardier beetle, the millipedes, the black ants (formic acid), the daddy longlegs, the Goliath tarantula, the monarch (poison) | flee, sting to defend | a reaction ladder per species (freeze, flee, then defend: curl up, play dead, spray, sting); a spray with a limited number of shots (a real bombardier holds about twenty); a hazard area with a telegraph; a dropped-leg decoy; hunters that learn to avoid a bitter bug |
| B11 | **Lights and sounds** (flashes, glows, songs) | fireflies (flash codes), the glowworm, the field cricket's song, the death's-head's squeak, the Goliath's hiss; the hornet and moths drawn to powered lights | lights exist for the player and objects | a bug light the lighting system draws; powered lights (the light-trap lamp, and places with power such as the ranger outpost) that stamp a light value on nearby cells, which night fliers climb and circle, each turning its own way, with a small chance to break away (the NetLogo moth model); ordinary lamps and firefly lanterns draw no bugs (the accepted catching plan, D63); a player's lantern flash, sent as a ledger event, that male fireflies answer; sounds tied to behaviour |
| B12 | **Parasites and burial** (lay in or on another bug) | the tarantula hawk (on a tarantula), the ant-decapitating fly (in a fire ant), the burying beetle (buries a carcass) | carcasses as food | a "host" link between two bugs: a paralysed tarantula dragged to a burrow, a fire ant that stops and dies, a carcass that sinks into the ground and becomes a brood |
| B13 | **Swarm change** (crowding turns solitary into swarming) | the locust | none | a crowding count per bug that rises fast when its kind is packed close and falls slowly when alone (real locusts change within hours and keep it for days); marching bands where only some walk at any moment (pause-and-go); then flying swarms |
| B14 | **Player tools on bugs** | all | net, smoker, bait dishes (designed, P4), fences, hive boxes | the bug stick (B3), light traps as lures (B11), the fish trap for crayfish and crabs, sand for marshes, host plants as nurseries; pens with an upgrade for each way out (taller walls, a roof net, a feeder — Slime Rancher) |
| B15 | **New ways of moving** | the cave fly (running in bursts), the water strider (skating), the jumping spider and the field cricket (leaps), the dragonflies (aiming ahead of prey) | five movement styles (`MovementFactory.cs`) | each new style with the first bug that needs it, in fixed-point, as the existing five are |


**How each block keeps every computer in step** (the `frontier-sync` classes):
- **Bug state on the players' computers, in the join snapshot:** B1 (goals, leaving and rejoining a group), B3's
  follow and lost states, B8 (waiting and striking), B10 (curled, playing dead, shots left), B13 (the crowding count),
  B15 (the new movement).
- **Zone state on the players' computers, in the state check and the snapshot:** B2's trail grid; B11's light map,
  worked out from the lights placed through the server.
- **Player actions as ledger events:** B3's taps and releases, B11's lantern flash, B14's tools as they reach bugs.
- **Server decisions, relayed:** B2's food pickup (reported by the zone's authority, relayed as `FOOD_CONSUMED`), B12's
  strike on a host, and, until GDD §03 Q1 is settled, B5's nests and B6's egg and grub counts, which run on the server
  today.
- **Time and weather:** B4's clock comes from the shared tick; a clock change and each shower's start and stop become
  ledger events.
- **World objects, placed and removed through the server like any other:** B7's water cells, B8's trap cells, B9's
  webs and threads.

Building a block means: the design in this document; the deterministic implementation (`frontier-sync`); a Bug Lab
pen that shows it; the gates; then the bugs that use it.

## 4. Worked example: ant trails a player can lead ants off
The owner's example (2026-10-03): tapping some ants with the bug stick makes them leave their trail, so a player can
lead a handful of them away while most of the column carries on as before.

**The design: scent on the ground, followed ant by ant.** Five designs were scored in
`research-2026-10-03/bug-mechanics-in-games.md` Part 4. This one scored 17 of 20, and it is the only one that meets
the example *and* lets a new trail form ant by ant. Three ant models with working code and the black garden ant
studies all work this way. A crafted scent lure that lays trail directly (the placed-marker design, as in Empires of
the Undergrowth) is kept as a later tool. The server keeps the colony-level decisions: how many workers go out,
nests and numbers.

**How it plays:**
- **Trails are scent on the ground.** Only an ant carrying food home marks the cells it crosses, most strongly
  near the food, and the marks fade unless they're renewed. Ants leaving the nest follow the strongest marks, so a
  trail always leads to food that was really found, and it straightens itself with use.
- **Most ants follow, not all.** At each choice about one ant in fifteen strays (real black garden ants follow a
  strong trail about 93% of the time), and strays find new food.
- **Two taps take ants off the trail.** First tap: the nearest few stop, rear up and face the player, and go back to
  work if left alone. Second tap while they're stopped: they follow the player in a loose line just behind (Pikmin 3
  Deluxe's two-step call; SimAnt's "recruit five").
- **The rest keep going.** Untapped ants still follow the scent, so the column carries on as before.
- **Letting go.** A follower drops out if the player gets too far ahead for a few seconds, if it reaches food, when the
  player releases it, or after a while, and it can't be retaken for a short time after. A dropped ant looks lost
  (slower, wiggling, turning back) until it finds scent or walks home, as real ants off a trail do.
- **A new trail.** A follower that reaches food picks some up, carries it home marking the way, and remembers the
  spot, so it keeps going back while the new trail is faint (real ants trust a route they remember over the trail).
  Other ants meet the new scent and some switch; if the new food is nearer or richer, traffic shifts on its own.
  The old trail keeps most ants until its food runs out.
- **Endings.** When food runs out, the ant that takes the last piece marks "no entry" there, so the old trail dies
  quickly and its ants spread out to search. Rain washes trails once rain reaches the bug simulation (§1, B4).
- **Other ways to change a trail:** a stone across it (the ants go round), and bait beside it.
- **What the player sees:** a faint sheen on busy trail cells (SimAnt let players switch on a scent view), ants
  rearing up at a tap, a small mark on followers, lost ants zigzagging.
- **Two players:** bugs following one player can't be taken by another's tap; they leave by the usual rules.
- **Across zone borders:** each zone keeps its own trail grid. An ant that walks over a border passes into the next
  zone's simulation with the bug transfer between zones (decided, not built yet), and carriers lay scent on whichever
  side they walk, so a trail into the Bee Meadow or the Mining Camp runs on as two halves that meet at the edge.

**How it's built** (every number is a starting point to tune in the Bug Lab, not a decision):
1. **The trail grid.** Per colony, a sparse map from cell to a small integer, kept only within its foraging range.
   An ant carrying food writes the larger of the old value and a value that falls with the steps it has walked
   since the food (from a lookup table); every N ticks each marked cell loses a fixed step, and cells at zero drop
   out. Writes happen in bug-id order inside the simulation step, and the fade on fixed tick boundaries. A second
   kind of mark is the "no entry" at exhausted food. (The max rule and distance-coded marks are AntSimulator's; the
   fade is NetLogo's.)
2. **Following.** At each decision (a few times a second), an outbound ant on scent reads three cells (ahead,
   ahead-left, ahead-right) and turns to the strongest (NetLogo's three-cell sniff). It ignores the trail on that
   decision with a fixed stray chance drawn from its id, 5–10% to start. The way home comes from a shared
   distance-to-nest map per nest, rebuilt only when blocking objects change (§2).
3. **The taps.** The prodding player's game sends "prod at this cell"; the server stamps it into the ledger. At the
   event tick every computer applies the same rule: that colony's ants within radius r of the cell, sorted by
   distance and then id, first k (k about 5 for the basic stick). The first prod sets them alert for a few seconds.
   A second prod in that window switches them to "follow player P". Prods are budgeted per player, and repeats at
   the same cell are filtered.
4. **Following the player.** Reynolds' leader-following: each follower aims at a spot just behind the player's
   direction of travel (from the player cells the ledger already carries, `PLAYER_CELL_ENTER`), steps aside if
   it's in front, and keeps apart from the others. The line is anchored to the player, never ant to ant, because
   a follow-the-ant-ahead rule is what makes ant mills.
5. **Leaving.** A follower drops out at distance D for T seconds, beside food, on a release event, or at a time
   cap, and then has a short no-retake cool-down. It enters the lost state (slower, more wiggle, U-turns) until it
   smells scent or reaches home on the distance-to-nest map.
6. **Founding.** A follower beside food takes a piece, lays scent all the way home, and keeps that food cell as a
   remembered target for its next trips. Taking the piece changes the food registry, which changes only through the
   server's `FOOD_CONSUMED` event, so it is an authority-only step: the zone's authority client sees the ant at the
   food and reports it, and the server relays `FOOD_CONSUMED` at a tick that every computer applies (detect, report,
   relay — the predation strike's pattern, `architecture_swarm_sync.md` §14). The ant turns home with its load when
   that event arrives, not before.
7. **The sync contract** (`architecture_swarm_sync.md` §0). The grid and each ant's follow, lost and remembered-target
   fields are client simulation state. They go into `ComputeStateHash` (a hash over the marked cells in index order)
   and the join snapshot (the sparse cell list; the per-bug fields ride the per-bug relay). The prod and release are
   new ledger events applied at their tick. The gate is a two-player late-join run with trails and followers
   actually active.
8. **Cost** (to confirm by profiling). About 100 ants deciding three or four times a second make a few hundred to
   about 1,200 cell reads a second, and the fade touches only marked cells. A sparse snapshot is about 4 bytes per
   marked cell, a few KB per colony, against today's village snapshot of about 230 KB.
9. **What changes on the server.** Colony-level decisions stay: how many workers go out, nests and numbers, and the
   food registry. The marching legs (`SWARM_SET_TARGET` along scouts' remembered routes, `colony.go`) stop steering
   the workers that follow scent, or the two would fight; scouts' food sightings still tell the server where food is
   and how many workers to send.

**Build steps:** (1) the distance-to-nest map and the trail grid as client simulation state, with hash and snapshot
(`frontier-sync`); (2) per-ant scent following inside the crawling movement, with carriers laying scent, and the
server's marching legs retired for those workers; (3) picking up food through the authority's report and the
relayed `FOOD_CONSUMED`; (4) the prod and release events and the follow and lost states (B1, B3); (5) a Bug Lab pen
with a nest, two food sites and a player; (6) the gates, including the late-join run with trails and followers
active, then the owner's sign-off.

## 5. Order of work
The roadmap's phases set the order (ROADMAP.md): the five zones around home are rebuilt to final quality in
Phase 2, the other rings as each zone is built in Phase 3.

1. **Foundation** (before any zone): time of day and rain made simulation inputs (B4's first step, §1), B1 leave
   the group, B4 routines, the per-bug brain; then the blocks the home zones need first: B2 trails and B3 the bug
   stick (ants), B5 nests (wasps, bees, ants), B6 life stages (butterfly, silk moth), B7 water life (the village
   pond's blue dasher, water strider, crayfish), B8 ambush (the blue dasher's perch-and-dart, the centipedes),
   B9 sticky threads (the glowworm), B10 defences (millipedes), B11 lights (firefly, glowworm), B12 burial (the
   burying beetle) and B15 new movement (the cave fly).
2. **Ring A — the five home zones**, one zone at a time: redo every bug already there to its §03 sheet, add the
   newcomers, then tune the zone's food web (§04). Village → Bee Meadow → Ant Tunnels → Mining Camp → Ant Colony.
3. **Ring B, C and D** with their zones (Phase 3): each zone's newcomers built with the zone (the `zone-craft`
   skill), using the blocks; the rest of B9 (webs), B12's parasites and B13 swarm change arrive with the first zone
   that needs them.

**Each bug, in order:** its sheet agreed (§03) → data (`species.json`: numbers, foods, homes, attacks) → behaviour
(blocks plus its signature mechanic) → its picture (paid image calls are asked for first, per batch) → a Bug Lab
pen → the gates → the owner's sign-off → placed in its zone → tuned with the zone.

**Real time becomes game time.** A game day is 14 minutes (8,400 ticks, `architecture_weather.md`), so the real
durations in the sheets (a purple emperor caterpillar's year, a stag beetle grub's years) are shrunk for play,
mechanic by mechanic. The sheets give the real figure as the animal's story; the Bug Lab sets the game's.

**When a bug counts as done:** it does what its sheet says; it passes the determinism gates with its behaviour
actually firing; it has its final art, its carcass item and its examine facts (P8); it holds its population band
in its zone without the safety net doing the work; and the owner has signed it off.

## 6. Testing and sign-off
- **Per block:** Go unit tests for the server side; the `sim-determinism` replay; the two-player late-join check,
  co-located and spawn-apart, with the block firing during the join (`test-changes` skill).
- **Per bug:** a pen in the Bug Lab (`nakama/data/zones/bug_lab/`, built by `tools/ecology/make_bug_lab.py`) with
  its food, its breeding place, its predator and its prey; a headless run that logs what it did (fed, bred,
  hunted, fled, died of what); a short recording or screenshots from the Unity command line for the owner.
- **Per zone:** the six-times-speed ecology runs (`ecology-tuning` skill) over several game days, showing every
  species inside its band, births coming from its own breeding rather than reseeding, and the food chains §04
  describes actually feeding each other.

## 7. Risks
- **The individual brain is the big piece.** Moving more of each bug's decisions onto the players' computers,
  identically, is a large job (the redesign doc is honest about it). Mitigation: each step behind its gates,
  starting with the ants; the pace, block by block or all at once after a short trial, is GDD §03 Q1.
- **Performance.** Hundreds of individually-acting bugs; mitigation: decisions a few times a second, cell grids
  instead of searches, groups kept wherever individuals don't matter.
- **Time and rain into the simulation.** Rain is applied on arrival today and time is display-only (§1); making
  them ledger inputs touches the weather code and the replay. Mitigation: the weather doc's deferred design already
  sketches the rain event, and it is built and gated once, before any routine depends on it.
- **Trails are new shared state.** The trail grid and the followers must be in the hash and the join snapshot, or
  a player who joins late sees different ants. Mitigation: the `frontier-sync` recipe, and a late-join gate that
  runs with trails and followers active.
- **Art.** Forty-four new bugs (two still open) need pictures and animations; each batch is a paid request asked
  for first.
- **Tuning knock-on.** Every behaviour change moves a zone's numbers; the zone is retuned after its bugs change,
  never before (P10).

## 8. Sources
- `architecture_swarm_sync.md` §0 and §14; `architecture_combat.md`; `ecology_parameters.md`;
  `investigations/individual_ecology_redesign.md`; `nakama/modules/world/colony.go`; `nakama/data/species.json`.
- Facts per bug: `investigations/research-2026-10-03/bug-ecology-facts-A.md` and `-B.md`.
- How games and real insects do it: `investigations/research-2026-10-03/bug-mechanics-in-games.md` (29 sources and
  five open-source simulations; the trail designs scored in Part 4; the techniques in Part 3, keyed to the blocks).
- `architecture_weather.md` (why time and rain don't reach the bug simulation today, and the deferred rain event).
