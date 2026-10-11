# Off-screen creature simulation: how games run creatures cheaply where no player is, and hand over to the detailed version

Research, 2026-10-10. Written for the question raised on 2026-10-10: someone who starts a fly farm, goes to another
zone, comes back, and finds nothing has grown. The owner suggested estimating growth from recent population data,
or per swarm from its food access, and asked for alternatives, including the server simulating empty zones itself.

## Purpose

Bug Farmer runs each bug's movement, feeding and hunting on the players' computers, in deterministic lockstep, and
the server (Go) keeps each swarm's life cycle at the group level (births, ageing, hunger, deaths, nests, the
ecology director). A zone nobody is in is frozen today. The decided design (2026-09-26) is one world clock: when
someone enters a frozen zone, the server catches it up on the time it missed before showing it. That catch-up needs a
cheaper, "abstract" stand-in for the hunting and feeding the players' computers normally do. This document collects
how other games and research handle exactly that: a cheap, abstract simulation of creatures where no player is
looking (often called "simulation level of detail", meaning the simulation runs in less detail where it matters
less), and how the abstract and detailed versions hand over to each other without the player noticing a
contradiction.

How to read each entry: the source (link, what was read, whether in full) → the concrete technique → what it costs
to run → how it fits our situation. Anything a source did not actually say is marked "not confirmed".

## Search angles used

For each topic at least four angles were tried: **by game** (the title plus "abstract", "offline", "out of sector"),
**by technique** ("simulation level of detail", "proxy simulation", "alibi generation", "catch-up", "fast forward"),
**by engine feature or code name** (class and setting names such as `AbstractCreature`, `switch_distance`,
`WorldLayerPusher`, `SimulationMode::Simulated`, `mongroup`, `actualize`, `TotalHoursLastUpdate`), and **by player
complaint** ("OOS combat performs better", "frozen in time", "story progression chaos", "spawning out of thin air").
Per topic:
- *Rain World:* game ("abstract creatures realized creatures off-screen"); developer talks ("Joar Jakobsson GDC
  talk … abstract"); code names on the modding wiki (`AbstractCreatureAI`, `Realize`/`Abstractize`); player
  curiosity ("do creatures kill each other offscreen"); and finally the developer's full devlog archive, downloaded
  and searched for every "abstract".
- *S.T.A.L.K.E.R.:* developer interview ("Iassenev … offline online"); config/engine feature (`switch_distance`
  in `alife.ltx`); engine source (OpenXRay `alife_*`); player complaint (S.T.A.L.K.E.R. 2 "A-Life 2.0 isn't working").
- *X3/X4:* technique ("low attention / high attention combat calculated"); game (X3 OOS rounds); patch notes
  ("low attention" changes); player complaint ("OOS combat needs to perform equal to or worse than in-sector").
- *Eco:* devblog ("How the Eco-Sim works"); engine feature (`WorldLayers`, `AnimalLayer`); code (EcoModKit
  reference assemblies); server settings ("SimulationQuality", "AnimalPopulation").
- *The Sims / Dwarf Fortress / Kenshi / RimWorld:* game ("story progression", "world activity", "caravan");
  mod (NRaas StoryProgression); developer statement (EA "Introducing Neighborhood Stories"); player complaint
  ("population explosion", "farms don't grow when I'm away"). The Dwarf Fortress wiki returned 404s and an empty
  search index, and no reliable Kenshi source was found, so those two are **not covered**; The Sims and RimWorld are.
- *Academic:* paper title (Brom, Šerý, Poch 2007); citation-following (Chenney GDC 2001, cited by Brom);
  technique ("alibi generation", "LOD trader", Sunshine-Hill).
- *Open-source code:* repository trees listed through the GitLab/GitHub APIs and searched for the abstraction
  (Veloren `rtsim/`, CDDA `horde_*`/`mongroup`/`map::actualize`, OpenXRay `alife_*`, Vintage Story
  `FastForwardGrowth`/`BehaviorMultiply`).

**How "read" is reported below.** "Read in full" means the raw text or code was downloaded and read line by line.
"Fetched" means a web page was read through a fetching tool that returns a digest of the page; those are used only
for what they plainly report, and are marked.

## Sources

### 1. Rain World (Videocult): abstract rooms, abstract creatures, "quantified" flies

**Source.** Joar Jakobsson's (JLJac) development log on TIGSource, as archived at
https://candlesign.github.io/Rain-World-Devlog/Full%20devlog (the whole archive, about 2 million characters, was
downloaded and searched for every one of its 118 mentions of "abstract"; the passages that describe the abstract
layer were then read in full: Updates 254–280 (June–July 2014), 319 (October 2014), 335, 360–361 (November 2014) and
the post of 20 April 2015). Supporting (fetched, the relevant sections read): the Rain World Modding wiki pages
https://rainworldmodding.miraheze.org/wiki/Rain_World_Code_Structure/Rooms and
.../Rain_World_Code_Structure/AbstractWorldEntity, and the official wiki page
https://rainworld.miraheze.org/wiki/Technical_Glossary/Abstractization. These are the developer's own words while
building the system; whether every detail shipped unchanged in the 2017 release is **not confirmed** unless the wiki
(which describes the shipped code) says so.

**The technique.**
- *Two (later three) levels of detail.* "Realized space is what you see, abstract space is a sort of gross
  simplification of the game, reduced to basically board game rules, where each room is divided into a few 'nodes'
  that simple representations of creatures occupy and interact in." A room is realized (full physics, tile-level
  pathfinding, full AI, 40 updates a second per the modding wiki) when the player is near; every other room in the
  region is abstract.
- *What an abstract creature keeps.* Which room and which node it is in (one node per room exit or den, not per
  area), a timer for how long it has been in that node, a path (just "an array of coordinates in node space"), its
  damage state, what it is carrying, and its unique ID (the wiki: the ID is "used for generating properties of many
  things", so a creature's looks and personality can be re-derived from it instead of stored).
- *How it advances.* Travel times between every pair of exits in every room are worked out ahead of time, per species
  (a "connectivity mapper" paths between the exits "pretending to be each of the creatures"). An abstract creature
  sits in a node until its timer reaches distance × its speed, then jumps to the next node, so it moves "with a
  speed that corresponds to the actual tile-level distances". Abstract rooms update only "once every few frames"
  and are told how many frames have passed; the developer intended far rooms to update at uneven, rarer intervals,
  and "the longer ago it was a creature was updated, the more 'quantum' it gets … when it receives its update it will
  have correspondingly higher chances of doing things".
- *Behaviour off-screen is cut down to what can reach the player.* The developer's reasoning: "what is the only thing
  an offloaded creature can actually do that will be able to affect you in any way? … That's exiting the room."
  So abstract creatures only roam, return to their dens before the rain, and (later) carry prey home. Hunting
  becomes a dice roll: when a predator and prey share a node, "the whole thing is reduced to '4% risk of eating per
  tick while they occupy the same node'". (Whether that exact rule shipped is **not confirmed**; the shipped wiki
  says only that an abstract creature holding food "retreat[s] to a den".)
- *A simple brain and a complex brain.* "In the simple, abstracted world the creatures will make simple, abstracted
  decisions. When the environment is realized at tile level, the AI should get a more powerful component as well."
  When a creature is realized the complex brain decides; the simple brain only stores destinations so they survive
  the next abstraction. They once disagreed (the realized AI sent a lizard home to its den, the abstract AI spat it
  out again); the fix was that the abstract AI "asks if there is a realized AI at play, and in that case outsources
  the decision to it".
- *Hand-over, abstract → realized.* When a room is realized, a creature that was walking between two exits for, say,
  40 ticks is "placed at a corresponding distance along the path", and the path is fed to its pathfinder so it
  keeps walking from the first frame. A creature that was not following a path does a random walk from its
  last-known position "for a corresponding amount of repeats … further away the longer ago you saw it".
- *Hand-over, realized → abstract.* The creature stores its distance to the nearest exit and cannot leave that node
  until that much time has passed ("so that a creature that was half a screen away from an exit won't be able to
  pop through it the very next frame"). Its full AI is kept "in a hibernation mode" if its goal is inside realized
  space, so it remembers what it was doing.
- *Counted creatures ("Quantified Creatures").* For the flies (the game's main food creature) the developers chose
  not to keep individuals at all: "a bat is a fly is a bat … it seemed ridiculous to save the individual positions
  of … 10 000+ flies … So instead I created a system where they are saved as just numbers, per node in each room."
  Moving a flock is "just shuffling numbers (minus one in this room, plus one in this room)", and a world-level
  "Flies World AI" gives each room a migration direction (spread to the emptiest neighbour, or gather in the
  nearest swarm room). The first version leaked: "bats would disappear or appear in the transitions between the
  states … schrödinger's bats"; after a rework, "50 bats is 50 bats, and they only disappear or appear when eaten
  or spawned."
- *A third, coarser level for far regions, plus fast-forward on entry.* Running four regions in abstract space at
  once "worked, but with really bad performance", so other regions were to be unloaded. But "when you enter a
  region, it won't do that all creatures are just popping out of their dens even if you're halfway through a rain
  cycle. So … the region that is loaded will probably go through some sort of sped-up, simplified version of the
  standard abstract space simulation, to place creatures in believable positions". For gaps in time he stores
  "what time it was when the abstract entity was last updated, and on the next update weigh[s] that into the
  simulation". (Whether the sped-up pass shipped is **not confirmed**.)
- *Respawning.* Per the modding wiki's world-file page (https://rainworldmodding.miraheze.org/wiki/World_File_Format,
  its spawn and lineage sections): each creature belongs to a den; "When a creature is killed, it will respawn in a few cycles with a
  different ID", and "lineage" dens can roll to replace a dead creature with the next, tougher species.

**What it costs.** Very little per creature: a node index, a timer and a short path, updated every few frames, with
travel costs baked ahead of time. The developer's aim was that "hundreds of them should be able to run in the
background as you play". The limit he hit was the number of abstract rooms (four regions at once was too slow), not
the creatures. Counted flies cost one integer per node.

**Fit for Bug Farmer.**
- Our swarms on the server are already close to Rain World's abstract creature: a group-level record with a place,
  needs and a life cycle. The pattern of "counted creatures" (a number per place, not individuals) is exactly our
  swarm size, and Rain World shows it can be made lossless across the hand-over ("50 bats is 50 bats") if every
  appear/disappear goes through one door (eaten or spawned).
- The "only simulate what can reach the player" rule maps to: off-screen, the server needs only the outcomes the
  returning player can see (how many bugs, how fed, how many died, whether the farm grew), not the paths.
- The "4% per tick while they share a node" rule is the simplest stand-in for our client-side predation: a rate per
  predator–prey pair sharing an area, scaled by time elapsed.
- The "sped-up, simplified version … to place creatures in believable positions" on region entry is our catch-up on
  arrival, and his "save when it was last updated and weigh the gap" is the same idea as our one world clock.
- Their hand-over placement trick (put a creature part-way along the path it was on, or random-walk it from its
  last-known spot for a number of steps proportional to the time away) is a cheap way for our clients to seed
  bug positions after catch-up without the result looking like everything was reset.
- Difference: Rain World's realized creatures run on one computer, so hand-over can read the abstract state
  directly. Ours must hand over to a deterministic lockstep simulation on several computers, so the catch-up result
  must be fixed by the server before any client starts (it is part of the snapshot the clients load).

### 2. S.T.A.L.K.E.R. (GSC Game World): A-Life, online and offline characters (plus its open engine code)

**Sources.**
- Interview with Dmitriy Iassenev, the lead AI programmer: "Interview: Inside The AI Of S.T.A.L.K.E.R.",
  https://www.gamedeveloper.com/pc/interview-inside-the-ai-of-i-s-t-a-l-k-e-r-i- (downloaded and read in full).
- The X-Ray engine's A-Life source as kept public by the OpenXRay project (https://github.com/OpenXRay/xray-16,
  branch `dev`, folder `src/xrGame/`), read in full: `alife_switch_manager.cpp/.h/_inline.h`,
  `alife_dynamic_object.cpp`, `alife_monster_abstract.cpp`, `alife_online_offline_group.cpp`, `alife_surge_manager.cpp`;
  read in part: `alife_combat_manager.cpp` (the offline fight maths), `alife_update_manager.cpp` (the scheduler).
  The files carry Iassenev's name and dates from 2002–2005.
- On S.T.A.L.K.E.R. 2's "A-Life 2.0" problems: https://gamingbolt.com/s-t-a-l-k-e-r-2-heart-of-chornobyls-a-life-2-0-isnt-working-heres-why
  (fetched; its account of the developer and modder statements read).

**The technique.**
- *Offline as the level of detail of online.* Iassenev: "The offline behavior is very simple: the character does not
  play animations or sounds, does not manage his inventory actively, does not build detailed and smooth paths
  (although he does build paths according to the global navigation graph …). In contrast, online behavior is fully
  detailed. Thus, offline behavior can be considered the LoD (level of detail) of the online." Characters on other
  maps are always offline; on the player's map, only those within "about 150 meters" are online.
- *The switch is a radius with a buffer (hysteresis).* In the code, one `switch_distance` and a `switch_factor` make
  two radii: `online_distance = switch_distance × (1 − factor)` and `offline_distance = switch_distance × (1 + factor)`
  (`alife_switch_manager_inline.h`). An offline object goes online only when the player is inside the smaller radius,
  and an online object goes offline only when the player is outside the larger one (`alife_dynamic_object.cpp`,
  `try_switch_online` / `try_switch_offline`). The gap stops a creature on the boundary flickering between the two
  modes every frame.
- *The hand-over is destroy-and-respawn of the detailed object.* `add_online` destroys the server entity's network
  copy and re-runs the normal spawn with the server-side record as the spawn data; `remove_online` destroys the
  detailed object and keeps only the record (with the children it carries, minus anything that can't be saved), then
  re-registers it with the offline scheduler and the offline map graph. So the abstract record is the truth and the
  detailed object is rebuilt from it each time; the detailed state that is not in the record (the "client data")
  is cleared when it goes offline unless the object asks to keep it.
- *Offline movement is on a coarse graph.* Offline objects live on the "game graph" (a sparse network of points
  across all maps) rather than the fine level navigation mesh; the old monster code advanced a monster along an edge
  by `elapsed game time × speed` and picked a random onward branch at each point.
- *Groups move as one.* A squad (`CSE_ALifeOnlineOfflineGroup`) is updated offline as a single object: its brain
  moves the group, and every member is simply copied to the group's position. The whole squad goes online as soon as
  any member is inside the online radius, and goes offline only when every member is outside the offline radius.
- *Offline fights and births: designed, then mostly cut.* The interview describes offline fights as "the opponents
  took turns making moves, the result calculated based on a formula and the random factor", with results like one
  side fleeing, someone dying or neither noticing the other. The formula survives in `alife_combat_manager.cpp`
  (`choose_combat_action`: chained "victory probability" per pair of fighters against a retreat threshold, and
  random detection rolls). But in the code as kept, the monster's "meet" decision returns "ignore", the call to
  `check_for_interaction` is commented out, and the offline breeding routine (`vfCheckForPopulationChanges`: every
  birth interval, with a birth probability, add `count × random(0.5–1.5) × birth percentage` new members to a
  group) is only called from inside that commented-out block. Iassenev himself says the dealer-and-quest life he
  watched offline was "too bad this did not make it into the original game". So in the shipped game, offline
  creatures mostly move between "smart terrains" (places that hand out tasks such as camping or guarding), and
  population is refilled by a respawn pass (`alife_surge_manager.cpp`: `spawn_new_objects` fills empty spawn slots).
- *Time slicing.* The offline simulation is run by a scheduler with a per-frame time budget and a cap on objects per
  update (`process_time`, `objects_per_update` in `alife_update_manager.cpp`), so it costs a fixed slice of each
  frame regardless of how many characters exist.
- *What happened when it was cut back (S.T.A.L.K.E.R. 2, 2024).* GSC's CEO said "the distance around which the
  system should function had to be limited to optimize performance"; a modder reported the offline layer "no longer
  exists", and players posted clips of characters appearing "out of thin air (and even behind the player)". The
  developers promised fixes.

**What it costs.** Offline characters cost a graph position, a few needs and a task, updated by a time-budgeted
scheduler; they run on the server side even in single player. The switch itself is the expensive moment (a full
spawn of a detailed object), so the hysteresis also saves cost by stopping repeated switches.

**Fit for Bug Farmer.**
- The hysteresis switch is directly useful if we ever let the server simulate parts of an occupied zone abstractly,
  and in a softer form for zone entry/exit: a zone should not flip between frozen and live when a player bounces
  across a zone edge (for example, keep a zone live for a minute after the last player leaves).
- "The record is the truth, the detailed object is rebuilt from it" is our arrangement already: the server's swarm
  record is authoritative, and clients build their deterministic per-bug state from the snapshot. The lesson is to
  make sure everything the player would notice (swarm size, hunger, nest, where the swarm is) is in the record, and
  the rest (each bug's exact position) can be re-derived.
- The squad pattern (one abstract object moved as a whole, members copied to it) is the same as our swarm.
- The warning is the cut features. A-Life's offline fights and births were designed, coded and then switched off,
  and the sequel shrank its bubble for performance and was criticised for creatures popping into existence near the
  player. For us the equivalent failure is a farm that does not grow while away, or bugs that appear from nowhere on
  arrival. The catch-up must produce births and deaths for real, not only movement.

### 3. X3 and X4 (Egosoft): out-of-sector / "low attention" simulation, and the complaints

**Sources.** No first-party technical write-up by Egosoft was found (the official X4 manual page on combat,
https://wiki.egosoft.com/X4%20Foundations%20Wiki/Manual%20and%20Guides/X4:%20Foundations%20Manual/Combat%20And%20Weapons/,
was fetched and does not cover it). What exists is player research and discussion (all three fetched):
- Egosoft forum, "Some M6 OOS Combat Findings" (X3: Terran Conflict), http://forum.egosoft.com/viewtopic.php?t=281614
  — players (Gazz, Wyvern1, Litcube) logging every out-of-sector hit with a modified script.
- Steam, "OOS combat needs to perform equal to or worse than in-sector combat" (X4),
  https://steamcommunity.com/app/392160/discussions/0/840627496100645234/ — the complaint thread.
- Steam, X4 discussion on "high/low attention", https://steamcommunity.com/app/392160/discussions/0/6664812048260991709.
Everything below is therefore player-measured, not developer-stated, unless marked.

**The technique.**
- *Two simulations of the same fight.* X4 calls them "high attention" (near the player: real projectiles, turrets
  that turn, ships that dodge and avoid collisions) and "low attention" (everywhere else, players report from about
  80 km away). Low attention resolves fights as numbers: damage per second against shields and hull, applied in
  pulses, with no line-of-fire check — a player in the X4 thread: in low attention "the game no longer checks if a
  turret has line of fire, just the range, so all station turrets can fire at once where they couldn't in high
  attention."
- *Rounds whose length depends on whether anyone is watching (X3).* A player in the X3 thread: "if you watch battle
  using satellites, each turn/round has 5 seconds, if you dont, 30 seconds." (Player-reported; **not confirmed** by
  Egosoft.) Initiative was a ratio: "The likelihood of getting the first shot is Ship1speed / Ship2speed."
- *The rules changed between versions.* Before X3 version 2.5, a round's damage was the sum of every gun times the
  turrets; a planned change used "the sum of damages of a random turret", which made some heavily armed ships worse
  than lighter ones. A bug made a ship whose one ammunition weapon ran dry deal "zero points of damage with each
  hit literally, even if it has 13 guns".

**The complaints (the useful part for us).**
- *Abstract results beat the real thing.* The X4 thread's starter: "you pretty always have to sit around in some
  other sector to let the out of sector battle simulations play out since they perform better than when you're in
  sector." Another player's breakdown: in the full simulation big ships keep their weapons on target roughly 40% of
  the time; in the abstract one, nearly 100%. Others reported the opposite (abstract fights taking far longer). Both
  are the same fault: the two levels disagree about outcomes.
- *Different builds win in each mode.* Agile fighters do well near the player; shield-heavy ships do well out of
  sight. Players learned to keep separate fleets for "in sector" and "out of sector" (Steam X3 threads), i.e. they
  optimise against the abstraction instead of the game.
- *Watching changes the result.* The player whose ship took more damage the moment he flew away was seeing the
  switch from high to low attention.

**What it costs.** Low attention is a per-pair damage sum per round; cheap enough to run every fight in the galaxy at
once. The cost of making it match the full simulation is the cost of the full simulation, which is why it doesn't.

**Fit for Bug Farmer.**
- This is the clearest warning in the whole cluster: a stand-in that disagrees with the detailed simulation becomes
  something players exploit or resent. If the server's stand-in for hunting gives flies better odds than the clients'
  real predation does, players will learn that leaving a zone is the best way to grow a farm (the exact mirror of the
  owner's worry), and vice versa.
- The remedy is measurement, not more detail: tune the stand-in's rates against what the detailed simulation actually
  produces (see the calibration techniques in the academic and Veloren entries below), and keep both versions'
  results within a band players cannot easily notice.
- The X3 "round length depends on whether it is watched" idea is a version of choosing the time step by need; for us
  it suggests a coarse step for catch-up (e.g. one step per in-game hour) rather than replaying ticks.

### 4. Eco (Strange Loop Games): populations as map layers on the server, individuals spawned and killed to match

**Sources.**
- The official Eco ModKit on GitHub, https://github.com/StrangeLoopGames/EcoModKit — the server's own API
  documentation file `Examples/ReferenceAssemblies/Eco.Simulation.xml` (the developers' code comments for the
  shipped `Eco.Simulation` assembly, 68 KB), downloaded and read in full (all 196 documented members). The same text
  is published as https://docs.play.eco/api/server/eco.simulation/ (that site blocked automated fetching). The
  simulation's source code itself is not public; only these comments are.
- The developers' description of the "Eco-Sim" (the store/Kickstarter text quoted in search results and the ModDB
  post "How the Eco-Sim works: The Players' Lifeline", https://www.moddb.com/news/how-the-eco-sim-works-the-players-lifeline,
  which blocked fetching). Only short quoted lines were seen, so they are used sparingly here.

**The technique.**
- *The truth is a set of grids ("world layers").* Every plant species, animal species, temperature, pollution and
  so on is a 2-D grid over the world, each with its own cell size: the comments give "temperature layer with 5x5
  granularity" and "Oak layer with 20x20 granularity" (in blocks), with conversions `FineToCoarse` (average) and
  `CoarseToFine` (spread the same value) between grids of different sizes. The animal layer's cell size is
  **not confirmed**.
- *Layers tick on a schedule, with "interactions" between them.* "Models an effect that a set of layers have on
  another layer, e.g. animals eating plants for food kills plants." Predation is literally a chemistry formula:
  `SecondOrderReaction` "simulates a differential equation of the form dz/dt = c * x * y … predation happens when
  predator meets prey". Plants grow by a capped logistic step ("growth rate in range [0; 1] … used in formula
  N + N * growthRate"), limited by habitability and by capacity (space and soil), and spread from the 3×3
  neighbouring cells.
- *How the animal population advances.* `AnimalLayer.TickPopulation`: "applies changes to population (like killed
  animals), simulates population growth and spread from neighbor cells. Population will only grow if there [is] at
  least one animal (assuming it was pregnant) and only spread from neighbor cells with at least one organism."
- *Hand-over: "pullers" bring the real world's events into the layers; "pushers" make the real world match the
  layers.* A puller "modifies a world layer based on the state of the world and events since the last tick, e.g.
  adjusts animal population based on player hunting activity"; the `AccumulatingPuller` "accumulates layer
  modifications that occur between worldlayer ticks, typically as a result of WorldObject and player actions". A
  pusher "modifies the world to reflect the state of the world layer simulation, e.g. spawns and kills animals to
  make the population match." For animals the push is: "1. Spawn animals in patches which don't have enough.
  2. Damage animals in patches which have too many." Each spawned animal remembers its home cell
  (`LayerHomePos`), so living animals are grouped by home cell and compared with that cell's number.
- *Never count a fraction of a creature.* "Trim to integer number of plants to avoid consume capacity for
  fractional plants which may prevent plants from grow and spawn." The plant puller "tracks added/removed plants
  between ticks and appl[ies] changes when tick happens. It also sync[s] layer with actual plants count on startup."
- *Individual animals are event-driven.* Each animal has a `NextTick` time and is processed from a time-ordered
  queue; `ForceTick` brings one forward "as reaction on an event". An animal knows its "observer level" (how
  closely players are watching it); what that changes is **not confirmed**.
- *It runs whether or not anyone is there.* The developers' line: when you log out "the world will not be the same in
  the morning, as it lives on with or without you", and "left to its own with no player intervention, the populations
  … will form boom/bust cycles". Eco servers run all the time, so there is no catch-up step; the layer simulation is
  cheap enough to run continuously. (Whether animals are spawned as individuals in areas with no players nearby is
  **not confirmed**.)

**What it costs.** One number per species per grid cell, ticked on a schedule — the cost scales with map area and
species count, not with the number of animals. Individual animals cost more but exist only as the visible face of
the layer numbers.

**Fit for Bug Farmer.**
- This is the closest match to what the owner asked for ("estimate per swarm from its food access"): Eco's growth
  rule is literally "grow by a habitability-limited rate, only if at least one is present, spread from occupied
  neighbours", and its predation rule is "rate × predators × prey". Our ecology director and swarm records already
  hold these numbers at the group level.
- The puller/pusher split is a clean contract for our hand-over. *Pull* (zone emptied): fold the clients' detailed
  outcomes since the last server tick (kills reported by the predation reporter, food eaten) into the server's group
  numbers — we already do this. *Push* (zone entered): the catch-up result is a set of target numbers per swarm; the
  snapshot then spawns individual bugs to match. Because our per-bug state is rebuilt from the snapshot on every
  client, "spawn to match" happens naturally — the risk is only in the number, not the placement.
- "Damage animals in patches which have too many" is a gentle way to reconcile a mismatch (let them die over time)
  instead of deleting them in front of a player.
- "Only grow if at least one is present" and the integer trimming are cheap guards worth copying: no swarm grows
  from nothing, and no fractional bug blocks or creates capacity.
- Difference: Eco runs everything all the time and needs no catch-up; we freeze empty zones, so we need the same
  rules run in large time steps on entry (see the techniques section).

### 5. Veloren `rtsim` (open source, Rust): one brain, two bodies; and a lazy-catch-up note in its own code

**Source (code studied).** Veloren, https://gitlab.com/veloren/veloren, branch `master` (fetched 2026-10-10). Read in
full: `rtsim/src/data/actor.rs` (the actor record, lines 1–470), `rtsim/src/rule/simulate_npcs.rs` (how unloaded
actors advance), `rtsim/src/data/nature.rs` and `rtsim/src/rule/replenish_resources.rs` (per-chunk resources),
`server/src/rtsim/rule/deplete_resources.rs`, the load/unload parts of `server/src/rtsim/tick.rs` (lines 361–726)
and `server/src/rtsim/mod.rs` (lines 41–300); read in part: `rtsim/src/rule/npc_ai/mod.rs` (brain tick rate),
`rtsim/src/rule/architect.rs` and `rtsim/src/data/architect.rs` (respawning), `world/src/lib.rs` lines 570–613 (how
the resource numbers are turned back into blocks).

**What the abstract version keeps.** Every NPC is an `Actor` record held by the server whether or not anyone is
near: a `seed` (re-derives its name, looks and loadout), position `wpos`, facing `dir`, `body`, `role`, `home`
site, `faction`, `presence` (just `health_fraction`), and for NPCs a `personality`, `sentiments` toward other actors,
`job` and known `reports` (gossip). The brain and controller are not saved. A field `mode` says whether the actor is
`Simulated` ("unloaded and is being simulated via rtsim") or `Loaded` ("loaded into the game world as an ECS
entity" — the full game object with physics and combat AI).

The natural world is kept as modifications on top of the generated world, not as a full copy: `Nature` holds, per
chunk (a 32×32-block square), a 0–1 "depletion factor" per resource type — "this value represents only the
variable 'depletion' factor of that resource, which shall change over time as the world evolves and players
interact with it."

**How it advances.**
- *The same brain runs in both modes.* The NPC AI (`npc_ai`) produces an "activity" (go to, gather, hunt, sit…)
  for every actor. When `Loaded`, the game's full agent carries the activity out every tick. When `Simulated`, the
  brain runs only every tenth tick, staggered by seed (`(actor.seed + tick) % SIMULATED_TICK_SKIP == 0`, with
  `SIMULATED_TICK_SKIP = 10`), using the summed time since its last run — "AI code should be broadly
  DT-independent."
- *Simulated actors only move.* `simulate_npcs.rs`: a `Goto` moves the actor in a straight line at
  `max_speed × speed_factor × dt`, clamped to the map and snapped to the approximate ground height; fish and boats
  may not leave rivers. Every other activity — gathering, hunting animals, talking — does nothing while simulated,
  and all queued actions are thrown away: `// TODO: simulate important NPC actions (like attacking)`,
  `retain(|_| matches!(actor.mode, SimulationMode::Loaded))`.
- *Resources regrow by a timer, a slice of the map per tick.* `REPLENISH_TIME = 60.0 * 60.0` (an hour to refill
  fully; the comment: "Makes farming unviable, but probably still poorly balanced"), 8,192 chunks per tick, each
  chunk visited in turn and given the accumulated amount. The developers' own note on doing better is exactly our
  catch-up idea: "It should be possible to optimise this be remembering the last modification time for each chunk,
  then lazily projecting forward using a closed-form solution to the replenishment to calculate resources in a lazy
  manner."
- *Population kept up by an "architect".* "Keeping track of all deaths that happen, and respawn something similar to
  keep the world from dying out", with a minimum respawn delay of one in-game day (`MIN_SPAWN_DELAY`), skipped if
  that kind of NPC is already above its wanted number, and a fallback "if enough time has passed, try spawning
  anyway" after five days. The code notes it cannot yet avoid respawning in chunks a player has loaded ("TODO: If we
  had access to `ChunkStates` here we could make sure these aren't getting respawned in loaded chunks").

**What happens when a player arrives.** Loading is by chunk, not by distance: when the server loads a chunk
(`hook_load_chunk`), any `Simulated` actor standing in it is switched to `Loaded` and a full game entity is built
from the record (`get_actor_entity_info`: config from the body/profession, randomness from `actor.rng(PERM_…)` so
the same NPC always gets the same loadout, health set from `presence.health_fraction`). While loaded, the record is
overwritten from the entity every tick (`actor.wpos = pos.0`, body), so the record never goes stale. When the
entity is unloaded, `hook_rtsim_entity_unload` flips it back to `Simulated`. For the land itself, when a chunk is
generated the stored depletion factor is applied by a dice roll per resource block — and the code admits the flaw:
"TODO: Don't throw a dice, try to generate the *exact* correct number."

**What it costs.** One small record per NPC (thousands world-wide), a straight-line move every tick and a brain run
every tenth tick, spread evenly; resources are one float per resource per chunk, refreshed in slices. No fights,
no pathfinding through terrain, no physics off-screen.

**Fit for Bug Farmer.**
- *Same rules at both levels.* Running one decision-maker that emits intentions, with a cheap executor off-screen
  and a full one on-screen, keeps the two levels from disagreeing about *what* creatures try to do. For us, the
  server's group-level rules (hunger, breeding, ageing, nests) are already the shared layer; the stand-in only has
  to replace the *execution* of feeding and hunting.
- *Warning in the code itself:* Veloren's simulated NPCs don't fight or gather at all ("TODO"). That is the exact
  gap the owner fears for us: if our catch-up only moves time forward for births and ageing but has no stand-in for
  feeding, a farm (which depends on being fed) will look frozen or starve.
- *Lazy closed-form catch-up.* Their note about "remembering the last modification time for each chunk, then
  lazily projecting forward using a closed-form solution" is our catch-up on arrival in one sentence. For anything
  that follows a simple law (food regrowth, ageing, a farm with a full feeder), compute the state at time t
  directly instead of stepping.
- *Exact numbers, not dice, when rebuilding.* Their own TODO shows that turning a stored fraction back into
  individual things by independent dice rolls makes counts drift. Our catch-up should produce whole-number swarm
  sizes on the server and hand those exact numbers to the snapshot.
- *Respawn away from players.* Their missing check ("aren't getting respawned in loaded chunks") is a reminder that
  our ecology director's reseeding should never place new swarms where a player can see them appear.
- *Staggered off-screen ticks* (`(seed + tick) % 10`) are a free way to spread server cost if the server ever
  simulates many empty zones live.

### 6. Cataclysm: Dark Days Ahead (open source, C++): overmap hordes, light/heavy entities, and catch-up on load

**Source (code studied).** https://github.com/CleverRaven/Cataclysm-DDA, branch `master` (fetched 2026-10-10). Read in
full: `src/horde_entity.h` and `.cpp`, `src/horde_map.h`, `src/mongroup.h` (the `mongroup` struct),
`overmap::move_hordes` and `overmap::process_mongroups` and `overmap::spawn_mongroup` in `src/overmap.cpp`
(lines 1299–1310, 1470–1655), `overmapbuffer::despawn_monster` (`src/overmapbuffer.cpp` 2193–2205),
`map::spawn_monsters_submap_group` / `spawn_monsters_submap` (`src/map.cpp` 10147–10368), `map::actualize`,
`grow_plant`, `restock_fruits`, `produce_sap` (`src/map.cpp` 9636–9760, 9953–10017), and `monster::on_load`,
`try_reproduce`, `try_upgrade` (`src/monster.cpp` 465–500, 568–640, 4245–4320). Player-side context: the CDDA forum
thread https://discourse.cataclysmdda.org/t/mainly-domesticated-animal-questions/19189/4 (search snippet only).

**What the abstract version keeps.** The world is a grid of "submaps" (12×12 tiles); only those around the player
(the "reality bubble") are simulated in detail. Everything else is held per overmap (a large region) in two forms:
- `mongroup` — a *count*: "Number of monsters in the group" (`population`), a `type` used only to roll which
  monsters to create, a position, a `target` and an `interest` (0–100, sets movement speed and reaction to noise),
  a `horde` flag and `dying` flag. A group "is likely an attempt to spawn new monsters" when the area is first seen.
- `horde_entity` — one entry per off-screen monster, in one of four buckets (active, idle, dormant, immobile; only
  active ones move). Two weights: "Create a lightweight entity based on a monster id" (just the type, a destination,
  a `tracking_intensity`, `moves` and `last_processed`) or "a heavy entity based on an existing monster", which
  keeps a full copy of the monster "to capture all the random bits of state that a monster can accumulate". The
  comment: "The vast majority of entities in an overmap have never actually been spawned, meaning they don't have
  this member populated."

**How it advances.**
- `move_hordes`: each active entity with a goal gains `moves` from its species speed, steps one square toward its
  destination when it has 100, and loses one point of `tracking_intensity` per turn (interest fades). If its next
  square is inside the loaded map, it is *placed as a real monster* right there and removed from the horde list.
  "TODO: throttle processing of monsters" — every active entity is processed every turn.
- `process_mongroups`: a `dying` group loses a fifth of its population each call: `population = population * 4 / 5`.
- Nothing eats or fights off-screen; there is no off-screen predation at all (not found in any file read).

**What happens when a player arrives (individuals re-created).**
- *Despawn keeps the individual.* When a monster leaves the reality bubble, `despawn_monster` stores it as a heavy
  `horde_entity`, so a wounded or tamed monster comes back as itself.
- *Count groups are rolled into monsters on first sight.* `spawn_monsters_submap_group` turns `population` into
  monsters by rolling the group's type table, places them on free, passable, outdoor tiles — and skips any tile the
  player can see: "monster must spawn outside the viewing range of the player". If there is nowhere unseen to put
  them, a non-horde group is simply discarded ("It's not like we're removing existing monsters").
- *Each individual catches up on its own missed time* (`monster::on_load`, called as it is placed):
  `try_upgrade` loops through every growth stage it would have reached ("so that late into game new monsters can
  'catch up' with all that half-life upgrades they'd get if we were simulating whole world"); `try_reproduce`
  loops through every missed breeding interval (`baby_timer`), checking the season of each, but with "a decreasing
  chance of additional spawns when 'catching up' an existing animal" — the first missed interval breeds for
  certain, the next with chance 1 in 3, then 1 in 5, 1 in 7…, and only if the animal rolled female (one in two) for
  this load; morale and anger drift back toward normal in proportion to the time away; milk-producing animals
  refill.
- *The land catches up too* (`map::actualize`, run when a submap is loaded): `time_since_last_actualize =
  calendar::turn - last_touched`; crops jump straight to the growth stage their seed's age implies (closed form, no
  stepping), fruit bushes restock if a season has changed, sap accumulates by elapsed time, rain funnels fill,
  items rot; then `last_touched = calendar::turn`.

**What it costs.** Off-screen monsters cost a small entry each and a step per turn when active; idle ones cost
nothing. Catch-up is paid once, per monster and per submap, at load time, proportional to the number of missed
intervals (a loop), or constant (closed-form growth stages).

**Fit for Bug Farmer.** This is the closest working precedent for the fly-farm scenario, and it shows both a good
pattern and a trap.
- *Good:* "last touched" time per area, and a catch-up function per thing that knows how to advance itself over a
  gap (crops by age, animals by missed intervals). For us: each swarm record carries the time it was last advanced;
  the catch-up advances it by the zone's missed time in a small number of steps.
- *Good:* light vs heavy records — keep full detail only for creatures players have interacted with. Our farmed
  swarms are the "heavy" case (owned, fed, penned); wild swarms can stay counts.
- *Good:* never create creatures where the player can see them appear.
- *Trap:* CDDA's breeding catch-up ignores food (nothing in `try_reproduce` checks whether the animal ate), and it
  deliberately damps births with the falling 1-in-1, 1-in-3, 1-in-5 chance so that long absences don't explode the
  population. The result is that a long absence gives only a few births — the "my farm didn't grow" feeling. For
  Bug Farmer, damping should come from the food and space limits the bugs really have (a capped growth rule), not
  from a dice rule that quietly throws away growth the player paid for by feeding them.
- *Trap:* nothing hunts off-screen, so wild populations only change through breeding catch-up and spawn rolls;
  predators and prey never balance each other while unloaded.

### 7. Brom, Šerý and Poch, "Simulation Level of Detail for Virtual Humans" (IVA 2007) — the academic framing

**Source.** C. Brom, O. Šerý, T. Poch, *Simulation Level of Detail for Virtual Humans*, IVA 2007, LNAI 4722, pp. 1–14,
https://artemis.ms.mff.cuni.cz/main/papers/IVE_IVA07.pdf — downloaded and read in full (14 pages).

**The technique.**
- *The goal is believability, not accuracy.* "The question behind simulation LOD is how to save resources by
  degrading quality, but keeping the illusion of quality, i.e. believability." They say plainly that this makes it
  "inapplicable when the simulation is aimed to compute a result" — a warning for anything players will measure.
- *Gradual levels instead of all-or-nothing.* The usual game approach — full detail where the player is, nothing
  elsewhere — "causes scenic inconsistencies … e.g. when a user expect[s] a v-human to return to the scene", and
  has "a high overhead of changing the focus of attention, since the simulation at the new centre must start from
  scratch". Their space is a tree (spot → room → building → village → world); a "membrane" cuts through it, and each
  area on the membrane is simulated as a single point. Rules force neighbouring areas to be at similar detail.
- *Behaviour shrinks with space.* Behaviour is a goal/task tree; at lower detail the planner stops descending at a
  higher layer and runs that task "atomically" as one timed event. Their pub example: at full detail miners sip,
  chat and order; one level down each "empt[ies] his glass at once every half an hour or so" and the waiter swaps
  glasses in "one giant step"; two levels down the glasses stop existing and the waiter just lowers the barrel
  "every hour or so"; three levels down the pub is a point and people only come and go.
- *Objects have an "existence level" and a "view level".* Below its existence level a thing stops existing; things
  native to an area ("a glass or a table is area-native in a pub") are destroyed "and only their total number is
  remembered by the area", while foreign objects keep their state. When detail goes up, remembered objects go back
  to their remembered places and the rest are placed by a per-area placing routine ("generating objects randomly
  around fixed places").
- *Event calendar.* Each atomic task's end time is put in a calendar; if detail rises mid-task, the task is
  "partially evaluated" and a sub-task is chosen to start in the middle ("chatting of the miners at a table should
  start in the middle"). Lowering detail is done lazily ("a 'garbage collector' approach … to keep down overhead in
  the case of a user roaming at the border of two areas") — a form of hysteresis.
- *Reconstruct before the player can see it.* When the user left the village, sitting positions were forgotten and
  "must be generated randomly: but sooner than s/he enters the pub again; actually, when s/he enters the village.
  Because of this, it is guaranteed that the simulation will have been running for a while with the new positions
  before s/he enters the pub."
- *Calibration is the open problem.* "A procedure for atomic execution of each task must be written manually. It is
  intriguing to think about whether it would be possible to generate these scripts automatically based on the
  results of many simulations performed in the full detail."

**What it costs.** Their prototype (about 100 characters, four villages) ran at 5–10% of a 3 GHz processor in full
detail with about 5,000 rules, and 0.1–0.5% at one level down with about 2,500 rules and under a third of the
objects. Writing behaviour took "about 50%" longer because each task needs an atomic version.

**Fit for Bug Farmer.**
- Their levels map neatly onto ours: *full* = a zone with players (per-bug lockstep on clients); *full−1* = a swarm
  as one point that eats and breeds in timed events (our server's group level); *full−2* = a zone as one point
  (species totals only — what the ecology director already sees). Catch-up can run at full−1 for a just-left zone
  and full−2 for a long-frozen one.
- "Area-native things are just counted" is exactly our wild swarm sizes; "area-foreign things keep their state" is
  our farmed swarms (owned, penned, fed) — keep their full record.
- "Reconstruct when the player enters the village, not the pub" suggests doing the catch-up as soon as a player
  starts *moving toward* a zone (e.g., at the zone-transition screen or when a neighbouring zone loads), so the
  result is settled — and the clients' deterministic simulation has run for a moment — before the player sees it.
- Their stated open problem (deriving the cheap version's rules from many full-detail runs) is the calibration step
  we should actually do: our headless ecology harness can produce the full-detail statistics.

### 8. Stephen Chenney, "Simulation Level-Of-Detail" (GDC 2001) — proxy simulations and how to prove they match

**Source.** S. Chenney (University of Wisconsin, with O. Arikan and D. Forsyth), *Simulation Level-Of-Detail*, Game
Developers Conference 2001, http://www.cs.wisc.edu/~schenney/research/culling/chenney-gdc2001.pdf — downloaded and
read in full (15 pages). Cited by Brom et al. as their reference [11].

**The technique.**
- *Players only experience events, so only events must be right.* "It doesn't matter how the model is implemented,
  provided a player experiences the right thing. In particular, we are free to substitute a cheaper implementation
  if it produces the same experiences as the full simulation." But doing nothing off-screen fails "for games where
  events beyond the view may have a major impact on the outcome … if nothing is done for out-of-view motion then
  nothing new can ever enter the view by itself."
- *A proxy simulation made of discrete events.* Instead of stepping every object every frame, the proxy predicts
  *when* the next event that matters will happen (in his traffic example: a car reaching the end of a road),
  puts it in a time-ordered queue and does nothing in between. It "only considers at most three cars on each
  event."
- *Choose the one measurable thing to get right.* For traffic it was travel time — the "meta-property that is
  visible to a viewer and sensitive to all of the others". Everything else may be wrong while unseen. But beware
  inference: "a viewer can infer things about the out of view world based on what they see in view, and any
  things a viewer might later see … must be consistent with those inferences."
- *Rebuilding state when something comes back into view.* "Arrival": a car entering view at a known point gets
  known values (position, zero speed), and unknowable details (wheel angles) "randomly". "Exposure": a whole road
  coming into view is rebuilt by re-running just that road from the first car's entry time with the full model —
  accurate but laggy, so for games he recommends "a more aggressive approximation … such as simply placing all
  the cars on the road stationary in a queue".
- *How to verify the proxy (the useful part).* "It is a hopeless task to measure the quality of a proxy simulation by
  comparing its precise behavior to that of the accurate simulation. Small differences at one point will lead to
  wild changes in the details." Instead, compare *statistics*: run many simulations with the full model and with
  the proxy from varied starting conditions and compare the mean and spread of the measured quantity. "If the
  statistical behavior of the proxy simulation is indistinguishable from that of the accurate one, then the viewer
  cannot tell the difference." His proxy's mean travel times were within about 1% with almost the same variance —
  and consistently slightly *too fast*, because "all the assumptions made in predicting event times in the proxy
  ignore potential delays", which "could be remedied by explicitly increasing the predicted event times".

**What it costs.** About two orders of magnitude cheaper: on an 800 MHz machine the full model managed 2,000 cars
in real time, the proxy 12,800 cars at 0.07 s of computing per simulated second. Cost still grows with the number
of off-screen objects ("the only way to avoid this drop is to ignore some objects completely").

**Fit for Bug Farmer.**
- *Pick the measurable quantity.* For a returning player that is: how many bugs each swarm has, whether the farm
  grew, whether a species crashed. That is what our stand-in must get statistically right; individual flight paths
  need not be simulated at all.
- *The verification method is directly usable with our tools.* Our headless ecology harness can run a zone with the
  full per-bug simulation many times from varied seeds over, say, 2 game days, record each swarm's start and end
  sizes and food, then run the server stand-in over the same period, and compare means and spreads per species and
  per farm. Chenney's result also predicts the most likely bias: a stand-in that ignores delays (search time,
  crowding at food) will make things happen *too fast* — for us, too much feeding and growth — unless corrected.
- *Consistency with inferences.* If a player sees few aphids when leaving and many ladybirds, the catch-up must not
  produce an aphid boom with no explanation; predators and prey must be advanced together.
- *"Exposure" rebuild = re-simulate the most recent short stretch in full.* An option for us: do the long catch-up
  at group level, then let the clients' deterministic simulation run the last few seconds before showing the zone
  (the zone-transition screen), so positions look natural.

### 9. The Sims 3 "story progression" and The Sims 4 "neighborhood stories" — abstract lives that players found chaotic

**Sources.**
- The Sims Wiki, "Story progression", page source fetched through the wiki's API
  (https://sims.fandom.com/api.php?action=parse&page=Story_progression&prop=wikitext&format=json) — read in full.
- EA, "Introducing Neighborhood Stories" (The Sims 4 developers' announcement, 2022),
  https://www.ea.com/games/the-sims/the-sims-4/news/introducing-neighborhood-stories — fetched; its design statements read.
- Mod The Sims forum thread on story progression and population, https://modthesims.info/t/498835 — fetched, read.
- Search snippets from Steam's Sims 3 forum about EA's version versus the NRaas "StoryProgression" mod (the NRaas
  documentation site itself blocked fetching), used only for the summary line marked below.

**The technique.** Households the player isn't controlling are not simulated in detail; instead a rule-driven event
system rolls life events for them over time: "Neighbors may move away, new ones will move in, get promotions, get
married, have children, make enemies, and even die." It also steers the town toward targets — "the system goal is to
keep 50% of the town occult" — and enforces a population ceiling: "Babies and toddlers may be killed off if the
town's population gets too high." Unplayed Sims "do not complete wishes". Exact event rates are **not confirmed**
by any source read.

**What players disliked.**
- *Results that contradict what the player knows.* "It may cause Sims who are best friends to become rivals, or an
  adult to become friends with an unrelated baby." Players are told to switch it off or tone it down "as it
  sometimes causes unwanted and chaotic events".
- *Population rules that fight the player.* A Mod The Sims user reports the game "goes ahead and deletes some of my
  homeless sims without my consent" near a cap of about 155 Sims; another describes towns packed until "kids
  bunched up at the school and taking all day to get in", and the Grim Reaper killing "10 or more sims at a time".
- *Interactions between options.* With ageing off, "households may fill up with babies that never age" — the
  abstract birth rule kept running while the matching death rule was disabled.
- *All-or-nothing control.* EA's own reason for replacing it in The Sims 4: story progression "can only be turned on
  or off, leaving many players feeling like they must choose between a chaotic world and a boring one."
- (From search snippets only, **not read in full**:) players preferred the NRaas mod because in EA's version Sims
  "fail to get jobs … get married, but don't move in together", i.e. half-finished abstract outcomes.

**The fix EA chose (The Sims 4).** Fewer, explained, steerable events: a neighbour "autonomously considering a life
change will always call one of your Sims to ask for input before taking any action"; events are filtered by each
Sim's traits ("not all Sims will consider every life change"); paced "at an interesting pace, without being too
spammy"; switchable per household; and a mailbox option "Check Recent Neighbourhood Stories" reports what
happened while you weren't watching.

**What it costs.** Very little: a handful of dice rolls per household per in-game day (rates not confirmed).

**Fit for Bug Farmer.**
- *The owner's fly farm is a "played household".* The Sims lesson is that the player's own things must never be
  handled by the same blunt rules as the background. Farmed swarms should be caught up by a careful,
  explainable rule (fed → grew by X; not fed → starved by Y), never by a population cap or a director cull
  removing them "without my consent".
- *Tell the player what happened.* A short "while you were away" report on return (the farm grew from 40 to 95 flies;
  the wasps in the east meadow crashed and were reseeded; it rained twice) turns abstract outcomes into a story and
  makes surprising results believable. This is cheap for us because the catch-up already produces those numbers.
- *Rules must stay paired.* If our catch-up runs births, it must run the matching deaths and food limits; switching
  one off (like Sims ageing) produces runaway populations.
- *Targets steer, they don't delete.* The Sims' "keep 50% occult" and population ceilings are director-style
  steering, like our ecology director. Their bad reputation came from visible, unexplained removals. Our director
  should act on wild populations only, and preferably away from the player's eyes.

### 10. RimWorld (Ludeon): caravans on the world map — a group with needs and a feeding formula, made real only for events

**Source.** RimWorld Wiki, "Caravan" (Forage redirects to its Foraging section), page source fetched through the
wiki API (https://rimworldwiki.com/api.php?action=parse&page=Caravan&prop=wikitext&format=json) — read in full
(about 47,000 characters). This is a community wiki describing the shipped game; Ludeon's code is not public, so
the formulas below are as the wiki states them (**not confirmed** against code).

**The technique.** When colonists leave their colony map they become a *caravan*: one icon on the world map, a
shared inventory, and each member's needs, simulated without any map, physics or pathing.
- *Feeding by rule, not by behaviour.* "Caravan members will feed as needed while traveling or resting, so long as
  there's food in the caravan inventory"; spoiling food is eaten first; "If there is insufficient food to feed the
  entire caravan, humans will be fed before animals."
- *Grazing and foraging are closed-form yields.* "Grazing animals, when hungry in a place with grazable plants, will
  instantly have their hunger bar refilled without any cost." Foraging gives each forager a daily yield from a stat
  (plants skill +0.09 per level, sight, manipulation), times a biome multiplier, doubled when the caravan isn't
  moving, only in the growing season. Predators get nothing: "carnivorous and omnivorous animals cannot hunt nor
  scavenge while traveling in a caravan. Extra appropriate food must be brought for them or they will starve."
- *A forecast the player can read.* The caravan panel shows "Days of food — number of days before your caravan runs
  out of available food", next to the estimated travel time, with a warning when low.
- *Fixed daily rhythm.* Caravans travel 06:00–22:00 and rest otherwise, whatever the pawns' own schedules.
- *Realise only when something happens.* An ambush, a manhunter pack or an attack on a settlement generates a
  temporary full map ("mini-map") at that spot; the abstract group is turned back into individual pawns, the fight
  is played in full, and afterwards the caravan reforms (with a 24-hour window, after which the storyteller pushes
  the player to leave). Movement speed is a formula: `13.6 × riding multiplier × carried-mass multiplier ÷ terrain
  difficulty`.

**What it costs.** Almost nothing: a few numbers per caravan per tick and a formula per day; the expensive full map
exists only during an event.

**Fit for Bug Farmer.**
- A caravan is a close cousin of our swarm on the server: a group with a shared hunger level, feeding from what is
  available where it is, by formula. RimWorld's split — herbivores graze "instantly … without any cost" where food
  exists, carnivores cannot hunt off-map — is the simplest possible stand-in. For us, plant-eating bugs could feed
  from the zone's food in proportion to what is there (cheap), while predators need a predation rate (see Eco's
  `c × predators × prey` and Rain World's per-tick chance), because "carnivores can't eat off-screen" would
  starve every predator in a frozen zone.
- "Days of food" is a good player-facing idea for farms: show how long a pen's feeder will last, so the player can
  predict what they'll find on return — and the catch-up will then match their prediction.
- Realising only for events matches our split too: the server's group level handles the long gap; individual bugs
  appear only when a player is there.

### 11. Ben Sunshine-Hill, "Alibi Generation" and "the LOD Trader" (Game AI Pro, 2013) — consistency with what the player remembers

**Sources.**
- B. Sunshine-Hill, *Alibi Generation: Fooling All the Players All the Time*, Game AI Pro (2013), chapter 37,
  http://www.gameaipro.com/GameAIPro/GameAIPro_Chapter37_Alibi_Generation_Fooling_All_the_Players_All_the_Time.pdf —
  downloaded and read in full (9 pages).
- B. Sunshine-Hill, *Phenomenal AI Level-of-Detail Control with the LOD Trader*, Game AI Pro (2013), chapter 14,
  http://www.gameaipro.com/GameAIPro/GameAIPro_Chapter14_Phenomenal_AI_Level-of-Detail_Control_with_the_LOD_Trader.pdf —
  downloaded; read: the introduction, problem definition, the "field guide" of noticeable errors, the criticality
  model and the practical-uses section (the optimisation algorithm itself was skimmed). Both rest on his PhD thesis
  *Perceptually Driven Simulation* (University of Pennsylvania, 2011), not read.

**The technique.**
- *Measure the cheap version against an "ideal world".* Imagine "an infinitely fast processor": you would simulate
  everyone all the time. The cheap system's job is to "seamlessly replicate the experience of that ideal game
  world" — the same yardstick as Chenney's.
- *Population that matches the full simulation's averages.* When an unseen area becomes visible, he draws how many
  characters are there from a Poisson distribution (a standard random count given only the average), using the
  average population the full simulation would have there; new arrivals from unseen areas come at the matching
  average rate. "The most important aspect of this is that the two processes match up. If the entry rate is too
  high, the bookstore will start out deserted and quickly fill up; if it's too low, the bookstore will become
  deserted over time." Characters already present (remembered ones) are subtracted from the average before drawing.
- *Generate hidden details lazily, consistent with what was seen ("alibis").* Only the visible state is generated
  at first; the hidden state (where the person came from, where they're going, why) is generated only when it
  matters, and conditioned on what the player saw. Options range from exact (weeks of maths) to "canned alibis":
  "simulate the entire world fully populated, run it for a while, and take snapshots of people in different initial
  conditions … run it on several machines overnight and combine their alibi lists."
- *A field guide to what players notice ("breaks in realism").* *Unrealistic state* — wrong right now ("eating from
  an empty plate"). *Fundamental discontinuity* — "a character's current state is incompatible with the player's
  memory of his past state. A character disappearing while momentarily around a corner, **or having been frozen in
  place for hours while the player was away**". *Unrealistic long-term behaviour* — only visible over long
  observation ("a car that never runs out of gas"). The chance of each depends on attention, memory and how soon
  the player returns.
- *Deleting is also a transition with a cost.* Remove unseen characters only after a distance and time threshold,
  "this way, the player would not be assured of being able to find the same characters even in the full
  simulation"; keep characters the player interacted with for longer.
- *Multiplayer:* add up the "criticality" of a character over all players observing it.

**What it costs.** Alibis cost nothing until needed; canned alibis cost storage and an offline recording run. The
LOD Trader itself ran in "tens of microseconds" a frame for hundreds of characters.

**Fit for Bug Farmer.**
- His own example of a fundamental discontinuity — "frozen in place for hours while the player was away" — is the
  owner's fly-farm worry named precisely. The farm is the thing the player *remembers*, so it carries the highest
  risk; wild bugs in a meadow the player glanced at carry little.
- *Canned outcomes recorded from full runs* is a practical way to build our stand-in: run the headless per-bug
  ecology for many game hours from many starting states, record per-swarm outcomes (growth, deaths, food eaten) as
  tables keyed by a few inputs (species, swarm size, food nearby, predators nearby, hours), and let the server look
  up or interpolate during catch-up. This also fixes the calibration problem raised by Brom and Chenney.
- *Match stocks and flows.* His "the two processes match up" rule maps to our immigration from neighbouring zones:
  the number of bugs that "wander in" during catch-up must be consistent with how many leave, or zones will slowly
  fill or empty.
- *Only what the player could compare needs to be right.* Farms (remembered, counted) need careful catch-up; a
  wild swarm's exact position never does.

### 12. Vintage Story (Anego Studios; game-logic code public on GitHub): calendar catch-up for farms and animals

**Sources.**
- Code studied, read in full: `BlockEntity/BlockEntityFastForwardGrowth.cs` from https://github.com/anegostudios/vssurvivalmod
  (branch `master`), and `Entity/Behavior/BehaviorMultiply.cs` lines 140–300 plus the field list of
  `BehaviorMultiplyBase.cs` from https://github.com/anegostudios/vsessentialsmod (branch `master`). These are the
  game's own survival and essentials modules, published by the developer.
- Player question and answer: "Loaded/unloaded chunks: will my base be frozen in time if I travel far enough?",
  https://www.vintagestory.at/forums/topic/12753-loadedunloaded-chunks-will-my-base-be-frozen-in-time-if-i-travel-far-enough/
  — fetched.

**The technique.**
- *Calendar-driven things catch up; behaviour-driven things freeze.* The forum answer (user Streetwind): things that
  rely on the calendar — "crop and berry bush growth, animal pregnancies and growth, food spoilage, charcoal pits and
  pit kilns and cementation furnaces, torch lifetime" — have the elapsed time applied when you return; processes
  driven by activity ("the firepit, quern processing, and pounder processing") do not advance. And "animals never
  starve. Feeding them only serves to trigger breeding, and keeping their weight up during winter."
- *Crops fast-forward in coarse steps through the real past weather.* `BlockEntityFastForwardGrowth.Update`:
  `hoursSinceLastUpdate = Calendar.TotalHours - totalHoursLastUpdate`; then "Fast forward in 3-4 hour intervalls" —
  a loop that, for each 3–4-hour step, asks the climate system for the temperature and rainfall *at that past date*
  (`GetClimateAt(..., ForSuppliedDate_TemperatureRainfallOnly, totalHoursLastUpdate / hoursPerDay)`), rolls whether
  growth is paused by cold, and calls the crop's growth step. Two guards: "Don't fast-forward for more than the past
  year" (anything older is skipped, "doing nothing"), and a negative gap (an imported save from the future) is
  treated as a rollback. While the chunk is loaded the same function runs every 4.5 seconds with a staggered start,
  so live play and catch-up use one code path.
- *Animal breeding catches up only one step.* `BehaviorMultiply.CheckMultiply` runs every 3 seconds while the animal
  is loaded. A pregnancy completes by calendar (`daysNow - TotalDaysPregnancyStart > PregnancyDays`), so an animal
  that was pregnant when you left gives birth on your return. But *becoming* pregnant (`TryGetPregnant`) needs a
  6% roll per check, an expired cooldown (6–12 days), a male nearby and `saturation >= PortionsEatenForMultiply`
  (three portions eaten) — and eating is something the loaded animal does. So an unloaded herd completes at most the
  pregnancies already under way; it does not run further breeding cycles.

**What it costs.** Nothing while unloaded; on reload, one loop of a few hundred steps per crop (a year at 3–4-hour
steps is about 2,500 steps), and one check per animal.

**Fit for Bug Farmer.**
- *Use one rule for live and catch-up.* Their crop step is the same function at 4.5-second intervals live and at
  3–4-hour intervals on reload. Our server's group-level swarm tick could likewise be the catch-up step, just called
  with a large time step and an averaged food input — avoiding two rule sets that drift apart (the X4 problem).
- *Replay past conditions, not today's.* Asking the weather "for the supplied date" during fast-forward is cheap and
  matters for us: if the director made it rain or brought drought while the zone was empty, the catch-up should step
  through those days with the conditions that actually held.
- *Cap the catch-up window.* A one-year cap bounds the cost of a zone left empty for a very long time; for us, a cap
  of a few game days (beyond which the zone is treated as at its long-run equilibrium) bounds catch-up cost.
- *This is the precise trap the owner fears.* Vintage Story ties breeding to eating and does not simulate eating
  off-screen, so a farm grows by at most one litter while you are away. Our flies' breeding is tied to feeding the
  same way, so the catch-up must include a feeding stand-in or farms will look frozen. Their "animals never starve"
  shortcut is the opposite error and would remove real danger from neglecting a farm.

## Source table

| # | Source | Technique | Cost | Fit for Bug Farmer |
|---|---|---|---|---|
| 1 | Rain World devlog (JLJac), abstract-layer passages, read in full | Rooms as a few nodes; abstract creatures hop node to node on pre-baked travel times; predation as "4% per tick" in a shared node; flies kept as *counts per node*, made lossless ("50 bats is 50 bats"); sped-up abstract pass planned on region entry | Tiny per creature; limit was number of abstract rooms | High: counts = our swarms; per-pair kill rate = stand-in for predation; "fast-forward on entry" = our catch-up |
| 2 | S.T.A.L.K.E.R. A-Life: Iassenev interview (full) + OpenXRay code | Offline = LoD of online; two-radius switch (hysteresis); record is truth, detailed object rebuilt on switch; squads move as one; offline fights/births coded but switched off | Time-sliced scheduler; switch is the costly moment | Medium: hysteresis for zone freeze; warning about cut off-screen features and pop-in (S.T.A.L.K.E.R. 2) |
| 3 | X3/X4 out-of-sector ("low attention"), player threads (fetched) | Fights resolved as damage-per-second sums in rounds, no line-of-fire | Very cheap | Warning: abstract results differing from real ones get exploited and resented |
| 4 | Eco ModKit `Eco.Simulation.xml` (full) | Species as grid layers ticked on a schedule; predation `dz/dt = c·x·y`; capped growth; pullers fold real events in, pushers spawn/kill individuals to match; only grow if ≥1 present; integer trimming | Per cell, not per animal | High: the "estimate from food access" rule, and a clean pull/push contract |
| 5 | Veloren `rtsim` (code) | One brain for both levels; simulated NPCs only move (fights/gathering TODO); per-chunk resource factor; architect respawns deaths after ≥1 day; dev note proposing lazy closed-form catch-up; dice rebuild "TODO … exact number" | Record per NPC; brain every 10th tick staggered | High: same rules both levels, lazy closed-form catch-up, exact counts, respawn away from players |
| 6 | Cataclysm: DDA (code) | Count groups + per-monster light/heavy entries; spawn out of sight; `last_touched` + `actualize` catch-up (crops by age, fruit by season); monster `on_load` loops missed breeding with damped odds, no food check | Paid once on load | High: last-touched catch-up and light/heavy records; warning: dice damping and food-free breeding |
| 7 | Brom, Šerý, Poch 2007 (full) | Gradual LOD levels over a space tree; tasks run "atomically" at low detail; area-native objects only counted; reconstruct before the player arrives; lazy lowering | 5–10% → 0.1–0.5% CPU one level down | High: level ladder (bug → swarm → zone); reconstruct at zone approach; calibration is the open problem |
| 8 | Chenney GDC 2001 (full) | Discrete-event proxy; pick the one measurable quantity; verify by comparing means/variances over many runs; proxies ignoring delays run too fast | ~100× cheaper | High: the verification method for our stand-in, using the headless harness |
| 9 | The Sims 3 story progression / Sims 4 neighborhood stories (wiki full; EA fetched) | Rolled life events for unplayed households; population caps; occult-ratio target; Sims 4 adds asking, traits, pacing, mailbox report | Trivial | Warning + idea: never let blunt rules touch the player's own things; tell them what happened |
| 10 | RimWorld Wiki "Caravan" (full) | Group needs; feeding by rule; grazing instant where plants exist; forage yield formula; carnivores can't hunt off-map; "days of food" forecast; full map only for events | Trivial | Medium-high: swarm feeding formula; farm "days of food" display |
| 11 | Sunshine-Hill, Alibi Generation (full) + LOD Trader (sections) | Population drawn to match full-sim averages; hidden details generated lazily, consistent with what was seen; canned outcomes recorded from full runs; error types incl. "frozen in place for hours while the player was away" | Near zero at runtime | High: recorded outcome tables as the stand-in; names the exact failure |
| 12 | Vintage Story (code + forum) | Calendar things catch up, behaviour things freeze; crops fast-forward in 3–4 h steps through past weather, capped at a year; pregnancies finish but no new ones (eating not simulated); animals never starve | Loop per crop on load | High: one rule for live and catch-up; replay past conditions; warning: the farm-doesn't-grow trap |

## The 6 most useful techniques for us

1. **The group record is the truth, and every bug enters or leaves through one door.** Keep each swarm's size,
   hunger, age mix and nest on the server as the authoritative record (Rain World's counted flies, Eco's layers,
   CDDA's groups, Brom's "area-native objects are only counted"). Make the hand-over lossless: a bug count changes
   only by birth, death, being eaten, or moving zones, never in the switch itself (Rain World fixed exactly this
   "schrödinger's bats" leak). Use whole numbers when handing to the snapshot (Eco's trimming, Veloren's "exact
   number, not dice").
2. **"Last advanced at" time + catch-up in coarse steps on arrival, using the same rules as live play.** Store when
   each zone was last simulated; on entry, step the server's own group-level swarm rules forward over the gap in
   steps of, say, an in-game hour (CDDA `actualize`, Vintage Story's 3–4-hour loop, Rain World's "weigh the gap"),
   replaying the conditions that actually held (rain, drought, director events), with a cap beyond which the zone
   is treated as at its long-run state. Where a rule has a simple formula (ageing, food regrowth, a farm with a full
   feeder), jump straight to the answer (Veloren's own note on "a closed-form solution … in a lazy manner").
3. **Rate-based stand-ins for feeding and hunting.** Plant-eaters eat in proportion to the food in their area,
   capped by need (RimWorld grazing/foraging, Eco's capped growth). Predation is a rate proportional to predators ×
   prey sharing an area (Eco's `dz/dt = c·x·y`, Rain World's per-tick chance in a shared node, A-Life's victory
   probabilities). Breeding then follows from being fed, as it does live. This is what Veloren, Vintage Story and
   CDDA left out, and leaving it out is exactly what makes a farm look frozen.
4. **Calibrate the stand-in against the detailed simulation, statistically.** Run the headless per-bug ecology many
   times from varied seeds, record per-swarm outcomes over a few game hours, and fit or tabulate the stand-in's rates
   so its means and spreads match (Chenney's method; Sunshine-Hill's "canned" outcomes recorded overnight; the open
   problem Brom names). Expect a stand-in that ignores search time and crowding to run too fast (Chenney measured
   exactly that) and correct for it. Re-check after every ecology change.
5. **Heavy records for the player's own things, light records for the wild.** Farmed swarms are the "played
   household" / "area-foreign object" / CDDA "heavy entity": keep their full state and catch them up with an
   explicit, explainable rule (fed → grew; feeder empty → hungry → deaths). Wild swarms are counts that the
   director may steer. Never let caps, culls or reseeds silently act on the player's farm (the Sims lesson).
6. **Hand-over hygiene and telling the player.** Do the catch-up before anything is visible — when a player starts
   moving toward a zone, not when it appears (Brom's "when s/he enters the village"); place new or reseeded bugs out
   of sight (CDDA, Veloren's TODO, S.T.A.L.K.E.R. 2's pop-in complaints); keep a zone live for a short while after the
   last player leaves so edge-hopping doesn't flip it (A-Life's two radii, Brom's lazy lowering); let the clients'
   deterministic simulation run a few seconds on the snapshot before showing it (Chenney's "exposure" rebuild); and
   give a short "while you were away" report (Sims 4 mailbox, A-Life news, RimWorld "days of food").

## Warnings — what players disliked

- **Frozen in place.** Sunshine-Hill lists "having been frozen in place for hours while the player was away" as a
  fundamental discontinuity players notice. Vintage Story's farms grow at most one litter while you are away (eating
  isn't simulated); CDDA damps catch-up births with falling odds (1, then 1-in-3, 1-in-5…) and ignores food; a
  Vintage Story player had to ask whether his base would be "frozen in time". This is the owner's fly-farm worry.
- **Abstract results that beat (or lose to) the real thing.** X4 players "sit around in some other sector to let the
  out of sector battle simulations play out since they perform better"; X3 players kept separate fleets for
  in-sector and out-of-sector fights. If our catch-up grows farms faster than live play, players will leave zones on
  purpose; if slower, they will never leave.
- **The off-screen feature that got cut.** A-Life's offline fights and births are in the code but switched off;
  Veloren's simulated NPCs don't fight or gather ("TODO: simulate important NPC actions"); S.T.A.L.K.E.R. 2 shrank
  its bubble for performance and players filmed characters "spawning out of thin air (and even behind the player)".
  The feeding/hunting stand-in is the part projects skip; it is the part we need most.
- **Unexplained, chaotic or hostile outcomes.** The Sims 3: best friends turned rivals, Sims deleted "without my
  consent", babies killed off at a population cap; EA's own verdict that players had to "choose between a chaotic
  world and a boring one".
- **Rules that are only half paired.** Sims households filled with "babies that never age" when ageing was off;
  Vintage Story's "animals never starve" removes the danger of neglect. Births without deaths, or deaths without
  births, run away.
- **Leaks at the hand-over.** Rain World's "bats would disappear or appear in the transitions" until reworked;
  CDDA silently discards a count group if every free tile is visible; Veloren's dice rebuild drifts counts.
- **Things appearing where the player is looking.** CDDA explicitly spawns "outside the viewing range of the
  player"; Veloren notes it may respawn in loaded chunks; S.T.A.L.K.E.R. 2's pop-ins drew criticism.
- **A Bug Farmer-specific one (from our own architecture, not from a source):** because per-bug behaviour runs in
  deterministic lockstep on the players' computers, the catch-up result must be fixed by the server and carried in
  the snapshot before any client starts simulating the zone; nothing in the catch-up may depend on a client.

## Quota count

**Sources deep-read (raw text downloaded and read; 9):**
1. Rain World devlog archive — every abstract-layer passage (Updates 254–280, 319, 335, 360–361, 20 April 2015),
   found by searching the whole 2-million-character archive — https://candlesign.github.io/Rain-World-Devlog/Full%20devlog
2. Iassenev interview, "Inside the AI of S.T.A.L.K.E.R." — https://www.gamedeveloper.com/pc/interview-inside-the-ai-of-i-s-t-a-l-k-e-r-i-
3. Eco server API documentation `Eco.Simulation.xml` (all 196 entries) — https://github.com/StrangeLoopGames/EcoModKit
4. Brom, Šerý, Poch, *Simulation Level of Detail for Virtual Humans* (2007), 14 pages — https://artemis.ms.mff.cuni.cz/main/papers/IVE_IVA07.pdf
5. Chenney, *Simulation Level-Of-Detail* (GDC 2001), 15 pages — http://www.cs.wisc.edu/~schenney/research/culling/chenney-gdc2001.pdf
6. Sunshine-Hill, *Alibi Generation* (Game AI Pro, 2013), 9 pages — http://www.gameaipro.com/GameAIPro/GameAIPro_Chapter37_Alibi_Generation_Fooling_All_the_Players_All_the_Time.pdf
7. The Sims Wiki, "Story progression" (page source) — https://sims.fandom.com/wiki/Story_progression
8. RimWorld Wiki, "Caravan" (page source) — https://rimworldwiki.com/wiki/Caravan
9. Sunshine-Hill, *The LOD Trader* (Game AI Pro, 2013) — the sections on the problem, the error types and practical
   uses (partial; the optimisation algorithm skimmed) — http://www.gameaipro.com/GameAIPro/GameAIPro_Chapter14_Phenomenal_AI_Level-of-Detail_Control_with_the_LOD_Trader.pdf

**Fetched (read through a page-digest tool, used only for what they plainly report):** Rain World modding and
official wiki pages (Rooms, AbstractWorldEntity, Abstractization, World File Format); GamingBolt on S.T.A.L.K.E.R. 2;
Egosoft forum "Some M6 OOS Combat Findings"; two X4 Steam threads; EA "Introducing Neighborhood Stories"; Mod The
Sims thread 498835; Vintage Story forum topic 12753.

**Codebases studied (4; the quota was 2):**
1. **Veloren `rtsim`** (Rust), https://gitlab.com/veloren/veloren — `rtsim/src/data/actor.rs`,
   `rtsim/src/data/nature.rs`, `rtsim/src/rule/simulate_npcs.rs`, `rtsim/src/rule/replenish_resources.rs`,
   `rtsim/src/rule/architect.rs`, `rtsim/src/data/architect.rs`, `rtsim/src/rule/npc_ai/mod.rs`,
   `server/src/rtsim/tick.rs`, `server/src/rtsim/mod.rs`, `server/src/rtsim/rule/deplete_resources.rs`,
   `world/src/lib.rs` (lines 570–613), `common/src/terrain/mod.rs` (chunk size).
2. **Cataclysm: Dark Days Ahead** (C++), https://github.com/CleverRaven/Cataclysm-DDA — `src/horde_entity.h/.cpp`,
   `src/horde_map.h`, `src/mongroup.h`, `src/overmap.cpp` (`move_hordes`, `process_mongroups`, `spawn_mongroup`),
   `src/overmapbuffer.cpp` (`despawn_monster`), `src/map.cpp` (`spawn_monsters_submap*`, `actualize`, `grow_plant`,
   `restock_fruits`, `produce_sap`), `src/monster.cpp` (`on_load`, `try_reproduce`, `try_upgrade`),
   `src/game_constants.h` (submap size).
3. **S.T.A.L.K.E.R. X-Ray engine via OpenXRay** (C++), https://github.com/OpenXRay/xray-16 — `src/xrGame/alife_switch_manager.cpp/.h/_inline.h`,
   `alife_dynamic_object.cpp`, `alife_monster_abstract.cpp`, `alife_online_offline_group.cpp`,
   `alife_combat_manager.cpp`, `alife_update_manager.cpp`, `alife_surge_manager.cpp`.
4. **Vintage Story game modules** (C#), https://github.com/anegostudios/vssurvivalmod —
   `BlockEntity/BlockEntityFastForwardGrowth.cs`; https://github.com/anegostudios/vsessentialsmod —
   `Entity/Behavior/BehaviorMultiply.cs`, `BehaviorMultiplyBase.cs`.

**Not covered:** Dwarf Fortress (its wiki returned 404s and an empty search index during this session) and Kenshi (no
reliable source found; a search-tool summary claiming farms stop when unloaded was not backed by the thread it cited).
Egosoft has published no technical write-up on X3/X4 out-of-sector rules that this research could find; that entry
rests on player measurements. Rain World's shipped code is not public, so its entry rests on the developer's devlog
and the modding wiki.
