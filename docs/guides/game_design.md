BugFarmer
Game Design Document (GDD)

1. Game Overview
BugFarmer is a top-down multiplayer sandbox game inspired by Terraria and Stardew Valley, focused on emergent ecology, insect farming, environmental interaction, and player-driven problem solving.
Players dig, build, explore, catch, farm, fight, and sell bugs in a persistent world that expands outward from a central village. Progression is driven by tools, knowledge, preparation, and spatial design—not skill trees, scripted events, or stat grinding.
The game supports two complementary playstyles:
Hands-on, risky exploration in the shared world


Stable, optimization-focused farming in private plots


The core experience emphasizes curiosity, experimentation, and readable cause-and-effect systems rather than prescribed objectives.

2. Core Gameplay Loop
Explore the world and discover new zones


Interact with insects through catching, combat, farming, or observation


Gather resources (bugs, plants, materials)


Build structures, pens, and tools


Influence local ecology through player action


Sell goods, unlock tools, and improve efficiency


Expand into more dangerous zones with higher rewards


There is no “endgame.” The world evolves through player interaction and ecological dynamics.

3. World Structure
3.1 World Layout
Top-down, tile-based sandbox world


World expands radially from a starting village


Farther zones are:


More dangerous


Richer in resources


Home to more complex insect interactions


3.2 Terrain & Barriers
Cliffside horizontal digging


Mines carved into rock


Underground tunnels, ore veins, ant colonies


Natural barriers separate zones:


Rivers


Elevation changes


Terrain chokepoints


Shallow crossings exist to allow controlled access between difficulty tiers


3.3 Navigation & Discovery
Signposts and waypoints:


Allow fast travel


Set spawn points


Secrets:


Hermit cabins


Special merchants


Hidden gear and items


The world favors exploration over map icons or quest markers.

4. Bugs & Creatures
4.1 Bug Categories
There are approximately 50 planned bug species across multiple biomes.
Bugs are divided into two functional categories:
Swarm Bugs
Examples:
Flies


Mosquitoes


Butterflies


Bees


Characteristics:
Exist primarily as swarms


Represented visually as many individuals


Interactions resolve at the swarm level


Individual Bugs
Examples:
Spiders


Frogs


Wasps


Large arthropods


Boss-scale insects


Characteristics:
Tracked and interacted with individually


Used for combat, danger, and boss encounters


Some grow more dangerous over time based on consumption or environment



5. Swarms & Representation
5.1 Swarm-Level State
The game treats swarms as the authoritative unit for ecology and progression.
Each swarm tracks:
Center position


Wander radius


Population count


Behavioral meters (calm, agitation)


Resource counters (nectar, food)


Reproduction readiness flags


5.2 Client-Side Bug Rendering
Individual insects are rendered client-side for:
Visual density


Player interaction


Feedback and feel


All players see the same individual insects in the same positions through deterministic local simulation. Swarm-level state (count, center, meters) is authoritative on the server; individual bug positions are computed identically on all clients using seeded RNG and fixed-point math.
5.3 Player Interaction with Swarms
Catching bugs reduces swarm count


Other players see the swarm shrink


Interactions affect swarm meters rather than individual stats


No heavy anti-cheat or strict authority model (player-hosted servers)



6. Life Stages & Biology
6.1 Life Stages
All creatures have life stages:
Eggs


Juvenile / larva


Adult


Life stages exist to:
Teach biology incidentally


Introduce delays and consequences


Enable emergent population dynamics


Life stages are tracked at the population level, not per individual.
6.2 Egg Mechanics (Example: Flies)
Rotten fruit or suitable substrate creates egg piles


Egg piles:


Consume the resource


Persist after the resource is gone


Track egg count server-side


Hatching:


Reinforces nearby swarm if present


Otherwise spawns a new swarm


Eggs are visible world objects that players can interact with.

7. Tools & Capture Mechanics
7.1 Nets
Multiple sizes


Visible area-of-effect indicators


Beginner nets catch easy bugs instantly


Variants:
Throwable nets


Area capture nets


Placeable ground nets (used in farming setups)


7.2 Smokers
Calm bees and other insects


Used as a general subdual mechanic


7.3 Capture Rules
Some bugs require HP reduction


Some require calming


Using the wrong tool can agitate a swarm


Tools unlock new behaviors and efficiencies rather than replacing older ones



8. Containment & Farming
8.1 Pens & Enclosures
Players build containment manually using:
Fence blocks


Walls


Doors


Terrain


Water


Containment strength depends on materials:
Wood → Iron → Steel → Advanced materials


8.2 Bug Escape Behavior
Some bugs:
Never break fences


Slowly damage them


Rapidly destroy weak materials (e.g., termites)


Escapes are:
Visible


Gradual


Recoverable


If enough bugs escape, the swarm center shifts accordingly.
Any bug can be farmed if containment and conditions are met.

9. Ecology Scenarios
9.1 Butterfly Zone
Located north of the starting village


Not an early-game zone


Contains:
Butterflies and milkweed


More valuable flies


Predators (frogs, spiders)


If milkweed reaches zero:
Butterflies stop reproducing


Population ages out naturally


9.2 Bees & Wasps
Wasps prey on bees


Wasp reproduction requires successful predation


Bees reproduce when:


A hive exists


Sufficient food is available


Pollination:
Triggered when swarm centers pass near flowers


Heuristic-based, not per-bug simulation


9.3 Starting Fly Dynamics
Early gameplay focuses on fly farming:
Food sources: rotting fruit


Predators: frogs, spiders


Wasps migrate from adjacent zones



10. Shared World vs Private Plot
10.1 Shared World
Persistent


Chaotic


No ownership of pens


Supports exploration and group farms


Farming is possible but risky


10.2 Private Plot
Separate scene owned by the player


Shared world unloads when entering


Used for:


Stable farming


Experiments


Ownership-based achievements


Private plots are expandable via City Hall.

11. Idle & Automation Systems (Private Plot Only)
11.1 Design Goals
Idle systems:
Reduce tedium


Reward planning and layout


Never replace gameplay


Hard constraints:
No purchasable bug pens


No FAST or free automation — no instant auto-catching, no automated combat. The one allowed
catching automation is the AUTONET (11.4): deliberately slow and capacity-capped, so it eases
tedium without out-producing the hand net.


Containment is always emergent


11.2 NPC Workers
NPCs are physical entities placed in the world.
Examples:
Lumberjack: harvests trees


Miner: processes materials


Bug Handler: repairs fences, resets traps, calms escaped bugs


NPCs never fully solve problems.
11.3 Structures & Stations
Support structures:
Beehives


Incubators


Extractors


Compost bins


Processing stations


They enable production but do not provide containment.

11.4 Autonet (the one allowed auto-catcher)
A more expensive, later-purchase structure (players start with the hand net / manual catching).
A small vat with a fan that slowly sucks nearby flies through an opening into an internal net.
Deliberately SLOW, and a capacity that FILLS UP and then stops until emptied — so it trims tedium
but never out-produces active hand-netting. Other bugs/zones may get their own slow auto-collectors
in the same spirit.

11.5 Furniture production boosts
Decorative furniture in the private plot can grant small idle production multipliers with
DIMINISHING RETURNS per duplicate (a second sofa adds less than the first) and an overall cap —
rewarding thoughtful layout without replacing gameplay.

12. Risk, Events, and Offline Behavior
12.1 Private Plot Safety
No random invasions


No offline damage


Simulation pauses when offline


Production is aggregated safely


12.2 Shared World Risk
Bugs migrate, hunt, compete


Events arise from spatial and ecological conditions


No timer-based disasters


No forced invasions



13. NPCs & Quests
13.1 NPC Roles
Ecologist (only NPC interpreting ecology)


Builder


Miner


Beekeeper


Traders


Only the Ecologist offers ecology-related quests.
13.2 Quest Philosophy
Optional


World-state driven


Multiple solutions


Never forced


Never create artificial problems



14. Combat
14.1 Core Model
Real-time combat


Player has HP only


No stamina


No skill trees


Power comes from items and preparation


14.2 Enemy Types
Swarm-based threats


Large arthropods (millipedes, scorpions)


Emergent bosses created by overgrowth


Bosses:
Persist until killed


Are not scripted


Telegraphed visually



15. Gear & Progression
15.1 Armor Layers
Armor (always equipped)


Utility gear (overlay)


Accessories (optimization layer)


No gear friction. No forced swapping.
15.2 Accessories
Small, meaningful bonuses


2–4 slots maximum


No loot treadmill


Encourage experimentation



16. Weather & Time
Shared day/night cycle


Soft modifiers only


No disasters


Weather nudges ecology subtly



17. Learning & Discovery
17.1 Magnifying Glass
Inspect unique instances


Unlocks:


Preferences


Avoidances


Breeding conditions


Supports curiosity, not progression gating



18. Design Pillars Summary
Emergent systems over scripts


Player agency over obligation


Readable ecology


Item-based progression


No offline punishment


No autoplay


No forced chaos



