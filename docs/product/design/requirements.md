FINAL — BUG FARMER
Master Requirements & Architecture Decisions Document

Frontend: Unity (2D)
Backend: Nakama (authoritative, persistent worlds)
Purpose: Capture all locked design decisions and system requirements for implementation planning.

1. Locked Technical Stack
1.1 Frontend

Engine: Unity

Rendering: 2D sprites

Camera: Top-down (bird’s-eye) or slight isometric tilt

Movement: WASD

Combat/Action Aim: Mouse controls attack/tool direction (Terraria-style)

Physics: lightweight 2D collisions (no heavy rigidbody simulation required)

1.2 Backend

Backend: Nakama

Authority: server-authoritative

Real-time: sockets for realtime state; RPC/HTTP for commands where appropriate

Persistence: server-side persistence for worlds and players

1.3 Deployment

Start with one server deployment

Designed to support multiple worlds hosted/managed on that server

Scale later by adding additional servers / capacity

2. World & Session Model (LOCKED)
2.1 Multiple Worlds (Not One Shared Global World)

The game supports multiple worlds.

Players can have their own world (including single-player worlds).

Worlds are separate persistent instances.

Key reason (locked): moderation & control (kick griefers), and letting groups choose their own play style.

2.2 World Access / Moderation (Required)

Each world has moderation controls:

world owner / admin(s)

ability to kick/ban players from that world

world access policy is configurable (public/private/invite) (exact UX deferred)

2.3 “Start with one” means:

Start with one deployed Nakama server

Host multiple worlds within it

Later: multiple servers hosting additional worlds

3. Multiplayer Permissions Model (Terraria-style)

Within a given world:

Anyone can place or break blocks

Anyone can interact with structures

No land ownership / claim system by default

Moderation happens at the world level (kick/ban), not per-tile permissions

4. World Representation
4.1 Tile Grid

World is a 2D grid of tiles; tile coordinates are canonical.

Tiles can contain:

ground type

optional floor

optional wall

structures/stations

plants

entities (bugs, players, workers)

4.2 Regions

The world is divided into regions (logical zones, not instanced).

Regions define:

spawn rates (per bug pool)

resource distributions/rarities (ores, plants, trees, etc.)

visual palette (biome feel)

Explicitly NOT region-defined:

Infection likelihood (infection is its own system/events, configured independently)

Regions are continuous; players and bugs can cross boundaries.

5. Chunking, Replication, and Simulation (CRITICAL LOCK)
5.1 Chunk System

World grid is partitioned into chunks (size configurable).

Chunk is the unit of:

simulation tiering

persistence snapshots/logs

network subscription and deltas

5.2 Simulation Tiers

Chunks operate in tiers based on player proximity:

Tier 0 — Active

full simulation near players

individual bugs, workers, stations, combat, reproduction timers

Tier 1 — Reduced

simplified updates, reduced decision frequency

no fine-grained simulation that isn’t necessary for player perception

Tier 2 — Aggregate

no per-agent simulation

store aggregate fields (per species / per chunk) such as:

population count

hunger pressure

reproduction pressure

infection pressure (if infection patch affects chunk)

worker throughput summaries

6. Persistence Model (LOCKED)
6.1 Chunk Persistence Strategy

Persistence uses:

append-only mutation logs per chunk

periodic snapshots

compaction to bound log growth

crash recovery: load snapshot + replay log

6.2 World Identity Keys

All persisted objects/events are keyed by:

worldId + chunkId + objectId (+ chunkSeq where needed)

7. Networking Consistency (LOCKED)
7.1 Server Authority

Clients request actions; server validates and applies changes.

Clients render and interpolate; they do not own truth.

7.2 Ordering

Per-chunk action serialization

Per-chunk monotonic sequence numbers (chunkSeq) for delta application

7.3 Interest Management

Players subscribe to nearby chunks

Receive snapshots on subscribe, then deltas

8. Core Gameplay Loop (Prototype Foundation)

Players:

start with minimal gear

gather resources (hand tools slow)

craft/buy improved tools and stations

build structures (floors/walls/fences)

farm bugs via reproduction conditions and traps

respond to infection events and dangerous regions

9. Tools, Combat, and Interaction
9.1 Movement

WASD movement

9.2 Aim & Actions (LOCKED)

Mouse controls facing/aim direction for:

attacks

tool use (chop, mine, net, spray)

(Terraria-like: you move one way, swing/aim another)

10. Building & Spawn Suppression
10.1 Placement

Grid-based placement (Terraria/Minecraft style)

Structures include floors, walls, fences, stations, furniture

10.2 Spawn Rule (LOCKED)

Bugs cannot spawn on floor tiles.

This applies to:

natural spawns

Tier2→Tier0 rehydration spawns

Players can sterilize/pave areas if they want; that is acceptable.

10.3 Additional Spawn Deterrents (Supported)

Light, smoke, incense/pheromones, traps, plant types can modify spawn behavior (details tunable)

11. Bugs & Reproduction (Bug Farmer identity)
11.1 Behavior

Simple state machines (idle/wander, seek food, reproduce, aggressive)

Decision ticks every few seconds; cheap movement ticks

11.2 Reproduction (LOCKED)

No infinite spontaneous spawning

Bugs reproduce when conditions are met:

required plants/food

space

time

Players facilitate reproduction by planting the right things.

12. Infection System (Independent of Regions)
12.1 Fiction

Infection is space-borne bacteria delivered via meteors

12.2 Infection Events

Meteors strike and create localized infection patches

Patches affect plants/bugs in their area

12.3 Outcomes

Bugs may become infected (“zombie bugs”):

more aggressive/erratic

may spread infection via attacks

12.4 Cure

Players can kill or cure infected bugs

Cure delivered via a spray-type tool; cure ingredients can involve infected materials

13. Inventory, Equipment, Shops, Processing
13.1 Inventory & Equipment

Players have inventory slots and equipped tools

Equipment gates capability and throughput

13.2 Shops (LOCKED direction)

Players can buy equipment (not everything must be crafted)

Processing equipment tiers:

small bottles / small processing early

larger kegs / higher throughput later

Specific items/tiers are extendable and not exhaustively listed yet

13.3 Stations

Stations process inputs over time:

input slots

timers

output slots

Tiers provide throughput/efficiency bonuses

14. Knowledge & Discovery System
14.1 Magnifying Glass (LOCKED)

Players can inspect bugs to unlock species knowledge progressively

Knowledge is per-species per-player and persistent

Helps players learn:

preferences (light/smoke/incense)

reproduction needs

infection susceptibility (as unlocked)

15. Workers & Soft Automation (LOCKED)
15.1 Philosophy

Automation via workers as people, not factory graphs

Workers behave like soft stations (assigned tasks), not roaming AI

15.2 Worker Cap (LOCKED)

Players have a worker cap

Cap can be increased via upgrades

Cap has a maximum ceiling

15.3 Worker Types

Role-based: woodcutters, miners, station tenders, later farmhands, etc.

15.4 Assignments

Workers can be assigned to:

areas/targets (trees/rocks/plot groups)

specific stations (worker at stove, worker at keg)

15.5 Worker Output Routing (LOCKED)

Workers have limited internal inventory slots

Worker can be assigned a destination chest/bin

If destination missing/full → output goes to worker storage

If worker storage full → worker pauses (“blocked/full”)

15.6 Performance Constraints (LOCKED)

No heavy pathfinding

No global scanning

Logical task execution; animations are cosmetic

Tier 2 aggregation for offscreen workers

16. Scaling Plan

Phase 1: one deployed server hosting multiple worlds

Phase 2: additional servers hosting more worlds

Phase 3: optional sharding/advanced partitioning if a single world ever needs it (not required for current direction)

17. What We Are Deferring (Intentionally)

These are intentionally not fully specified yet:

full item list, recipes, exact tiers and numbers

full bug species list

exact region names/count

final pricing/monetization model

But the architecture and systems are designed so adding these later does not require a rewrite.