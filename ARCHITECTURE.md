# Bug Farmer - Architecture Document

## Overview

Bug Farmer is a 2D multiplayer game where players farm bugs, build structures, and manage infection events. This document captures all architectural decisions and serves as the implementation roadmap.

---

## 1. Technical Stack

| Component | Technology | Status |
|-----------|------------|--------|
| Frontend | Unity 6 (2D) | Not started |
| Backend | Nakama 3.35.0 | Docker configured |
| Database | PostgreSQL 15 | Docker configured |
| Server Logic | Go modules | Structure planned |
| Realtime | Nakama WebSockets | Not started |

### 1.1 Unity Configuration (LOCKED)

| Setting | Value | Rationale |
|---------|-------|-----------|
| Unity Version | Unity 6 (latest) | Modern features, active support |
| 2D System | Built-in Tilemap | Native chunk-based rendering, good for grids |
| Tile Size | 32x32 pixels | Classic, balanced detail |
| Visible Area | 32x24 tiles | ~1 chunk visible at default zoom |
| Pixels Per Unit | 32 | 1 tile = 1 Unity unit |

### 1.2 Client Architecture (LOCKED)

The Unity client is **render-only**. All game logic runs on the server.

| Responsibility | Server | Client |
|----------------|--------|--------|
| Bug AI | ✓ | |
| Movement validation | ✓ | |
| Reproduction logic | ✓ | |
| Collision detection | ✓ | |
| Rendering | | ✓ |
| Input capture | | ✓ |
| Interpolation | | ✓ |
| Audio/VFX | | ✓ |

---

## 2. Project Structure

```
BugFarmer/
├── docker-compose.yml          # Nakama + PostgreSQL
├── nakama/
│   ├── data/
│   │   └── local.yml           # Nakama config
│   └── modules/                # Go server code
│       ├── main.go             # Entry point
│       ├── world/              # World simulation
│       ├── rpc/                # RPC handlers
│       └── entities/           # Game entities
├── unity/                      # Unity project (TBD)
├── requirements.md             # Game design requirements
└── ARCHITECTURE.md             # This document
```

---

## 3. Nakama Architecture

### 3.1 Nakama Concepts Mapping

| Bug Farmer Concept | Nakama Feature | Notes |
|-------------------|----------------|-------|
| World | Match | Long-running authoritative match |
| World metadata | Storage | Owner, access policy, settings |
| Chunk state | Match State + Storage | Live in match, persisted to storage |
| Player actions | Match Messages | OpCode-based protocol |
| World discovery | RPC | List/search/create worlds |

### 3.2 RPCs (Request/Response)

**World Management:**

| RPC Name | Purpose | Request | Response |
|----------|---------|---------|----------|
| `world_create` | Create new world | name, access_policy | world_id, match_id |
| `world_list` | List available worlds | filters, pagination | world[] |
| `world_join` | Get match ID to join | world_id | match_id |
| `world_leave` | Leave current world | world_id | success |

**Access Policy Values:**
- `public` - Anyone can join
- `private` - Owner invite only

**Player Data:**

| RPC Name | Purpose | Request | Response |
|----------|---------|---------|----------|
| `player_inventory` | Get/update inventory | action, items? | inventory state |
| `player_knowledge` | Bug discovery progress | species_id? | knowledge map |
| `player_stats` | Player progression | - | stats object |

### 3.3 Match Message OpCodes

| OpCode | Direction | Purpose |
|--------|-----------|---------|
| 1 | C→S | Player movement |
| 2 | C→S | Player action (interact) |
| 3 | C→S | Chunk subscribe |
| 4 | C→S | Chunk unsubscribe |
| 5 | C→S | Tile placement |
| 6 | C→S | Tile break |
| 7 | C→S | Tool use |
| 8-9 | C→S | *Reserved for future* |
| 10 | S→C | State update (chunk delta) |
| 11 | S→C | Entity update |
| 12 | S→C | Chat message |

---

## 4. World & Chunk System

### 4.1 World Configuration

```
TickRate: 10 ticks/second (100ms per tick)
ChunkSize: 32x32 tiles
ChunkViewDistance: 2 chunks (5x5 grid = 160x160 tiles visible)
MaxPlayersPerWorld: 100
```

### 4.2 Entity Limits (LOCKED)

```
MaxBugsPerChunk: 100          # Hard cap, prevents runaway reproduction
MaxEntitiesPerChunk: 150      # Bugs + workers + plants
EntityUpdateBatchSize: 20     # Group updates per network message
BaseUpdateFrequency: 10/sec   # Matches tick rate for near entities
ClientInterpolation: true     # Smooth movement between updates
```

**Target**: 100-300 bugs visible on screen during normal gameplay.

### 4.3 Chunk Simulation Tiers

| Tier | Name | Distance | Simulation |
|------|------|----------|------------|
| 0 | Active | ≤1 chunk | Full per-entity simulation every tick |
| 1 | Reduced | 2 chunks | Simplified, every 5th tick |
| 2 | Aggregate | >2 chunks | No entities, only aggregate counters |

### 4.4 Chunk Data Structure

```go
Chunk {
    Coord: {X, Y}
    Tier: 0|1|2
    Tiles: [32][32]Tile
    Entities: []Entity
    SeqNum: int64           // For delta ordering
    Aggregates: {           // Used in Tier 2
        BugPopulation: map[species]count
        HungerPressure: float
        ReproductionPressure: float
        InfectionPressure: float
    }
}
```

### 4.5 Tile Data Structure

```go
Tile {
    GroundType: int         // Grass, dirt, stone, etc.
    FloorType: int          // 0 = none (bugs can spawn)
    WallType: int           // 0 = none
    StructureID: string     // Station, furniture, etc.
    PlantID: string         // Growing plant
}
```

### 4.6 Spawn Suppression Rule (LOCKED)

Bugs CANNOT spawn on tiles where `FloorType > 0`. This applies to:
- Natural spawns during simulation
- Rehydration when Tier2 → Tier0

### 4.7 Entity Position System (LOCKED)

**Dual Coordinate System:**
- **Tiles**: Integer grid (0-31) within chunk - for walls, floors, structures
- **Entities**: Float position (0.0-32.0) within chunk - for bugs, players, workers

**Entity Position Structure:**
```go
EntityPosition {
    ChunkX, ChunkY int       // Which chunk the entity is in
    LocalX, LocalY float32   // Position within chunk (0.0 to 32.0)
}
```

**World Position Conversion:**
```go
// Chunk-local to world:
WorldX = ChunkX * ChunkSize + LocalX
WorldY = ChunkY * ChunkSize + LocalY

// World to chunk-local:
ChunkX = floor(WorldX / ChunkSize)
ChunkY = floor(WorldY / ChunkSize)
LocalX = WorldX - (ChunkX * ChunkSize)
LocalY = WorldY - (ChunkY * ChunkSize)
```

**Chunk Boundary Handling (End-of-Tick):**
```
At end of each tick:
1. Check if LocalX/LocalY outside [0, ChunkSize)
2. If LocalX >= ChunkSize: ChunkX++, LocalX -= ChunkSize
3. If LocalX < 0: ChunkX--, LocalX += ChunkSize
4. Same for Y axis
5. If chunk changed, move entity to new chunk's entity list
```

**Tile Collision Check:**
```go
// Entity at (LocalX=15.7, LocalY=22.3) checks tile (15, 22)
tileX := int(math.Floor(entity.LocalX))
tileY := int(math.Floor(entity.LocalY))
tile := chunk.Tiles[tileX][tileY]
```

### 4.8 World Generation (LOCKED)

Worlds use hand-crafted layouts with procedural decoration.

```
WorldSize: 16x16 chunks (512x512 tiles, ~262k total)
Layout: Hand-crafted in Unity (terrain, village, structures)
Decoration: Procedural spawning (trees, rocks, vegetation)
Hub: Central village as player spawn/hub area
```

**Generation Flow:**
1. Load pre-built world template from Unity export
2. Procedurally populate with trees, rocks, plants
3. Spawn initial bug populations based on biome rules

---

## 5. Entity System

### 5.1 Entity Types

| Type | Simulated | Persisted | Notes |
|------|-----------|-----------|-------|
| Bug | Tier 0/1 | Yes | State machine AI |
| Worker | Tier 0/1 | Yes | Assigned tasks |
| Player | Always | Yes | Client-controlled |
| Projectile | Tier 0 | No | Temporary |
| Meteor | Tier 0 | No | Infection event |

**Entity ID Format:** UUID with type prefix
- Bugs: `bug_a1b2c3d4`
- Workers: `worker_e5f6g7h8`
- Players: `player_{user_id}`

### 5.2 Bug State Machine

```
States: Idle → Wander → SeekFood → Reproduce → Aggressive
Transitions based on: hunger, reproduction readiness, threats
Decision tick: every 2 seconds (10 ticks)
Movement tick: every tick
```

### 5.3 Bug Reproduction (LOCKED)

Reproduction requires ALL conditions:
- Required plants/food present
- Available space (no floor tile)
- Cooldown timer elapsed
- Not infected

### 5.4 Worker System (LOCKED)

```
WorkerCap: per-player, upgradeable, has ceiling
Assignment: area/targets OR specific station
Inventory: limited slots
Output routing: assigned chest → worker storage → pause if full
Pathfinding: NONE (logical task execution, cosmetic animation)
```

---

## 6. Infection System

### 6.1 Infection Events

```
Trigger: Meteor strike (random or event-based)
Effect: Creates infection patch at impact location
Radius: Configurable per event
Duration: Until cleared or spreads
```

### 6.2 Infection Mechanics

- Infected bugs become aggressive/erratic
- Infection spreads via bug attacks
- Players can cure with spray tool
- Cure ingredients may require infected materials

---

## 7. Persistence Strategy

### 7.1 Storage Keys

```
Collection: "worlds"
Key: {world_id}
Value: WorldMetadata (owner, name, access_policy, created_at)

Collection: "chunks"
Key: {world_id}:{chunk_x},{chunk_y}
Value: ChunkSnapshot

Collection: "chunk_logs"
Key: {world_id}:{chunk_x},{chunk_y}:{seq_start}
Value: MutationLog[]

Collection: "players"
Key: {user_id}:inventory
Value: {items: [...], currency: int}

Key: {user_id}:knowledge
Value: {discovered_species: [...], stats: {...}}
```

### 7.2 Persistence Strategy

1. **Mutation logs**: Append-only log per chunk for each change
2. **Snapshots**: Periodic full chunk state (every 30 seconds)
3. **Compaction**: Merge logs into snapshot, discard old logs
4. **Recovery**: Load snapshot + replay logs since snapshot

---

## 8. Networking Protocol

### 8.1 Client → Server Messages

All messages are JSON with OpCode prefix.

```json
// Movement (OpCode 1)
{"x": 100.5, "y": 200.3, "facing": 45.0}

// Chunk Subscribe (OpCode 3)
{"chunks": ["3,4", "3,5", "4,4", "4,5"]}

// Chunk Unsubscribe (OpCode 4)
{"chunks": ["2,3", "2,4"]}

// Tile Placement (OpCode 5)
{"chunk": "3,4", "x": 15, "y": 20, "type": "floor", "id": 2}

// Tool Use (OpCode 7)
{"tool": "net", "target_x": 105.0, "target_y": 198.0}
```

### 8.2 Server → Client Messages

```json
// State Update (OpCode 10)
{"chunk": "3,4", "seq": 1234, "tiles": [...], "entities": [...]}

// Entity Update (OpCode 11)
{"entities": [{"id": "bug_123", "x": 50, "y": 60, "state": "wander"}]}
```

### 8.3 Error Response Format

All RPC and match errors use consistent format:

```json
{"error": "Human readable message", "code": "ERROR_CODE"}
```

**Error Codes:**
| Code | Meaning |
|------|---------|
| `WORLD_NOT_FOUND` | World ID doesn't exist |
| `WORLD_FULL` | Max players reached |
| `ACCESS_DENIED` | Private world, not invited |
| `INVALID_ACTION` | Action not allowed in current state |
| `RATE_LIMITED` | Too many requests |

---

## 9. Scalability Strategy

### 9.1 Bottleneck Analysis

| Layer | Work | Risk Level | Mitigation |
|-------|------|------------|------------|
| Server (Go) | All AI, logic, state | Medium | Efficient tick loop, entity limits |
| Network | Sync positions to clients | **High** | Batching, delta compression, 3/sec updates |
| Client (Unity) | Render + interpolate | Low | Object pooling, GPU instancing |

### 9.2 Why DOTS is Not Needed

Since the server owns all game logic:
- Client has **no AI code** - bugs are just visual sprites
- Client work: receive position → interpolate → update transform → render
- Standard Unity handles 300 sprites easily with object pooling

**DOTS consideration**: Only if we add client-heavy features (physics, complex local effects).

### 9.3 Optimization Priorities

1. **Network protocol** - Batch entity updates, delta compression
2. **Server tick efficiency** - Profile Go simulation under load
3. **Client object pooling** - Reuse GameObjects for entities
4. **GPU instancing** - For rendering many similar sprites

### 9.4 Priority-Based Entity Sync (LOCKED)

Entity updates use 3 tiers based on distance from player:

| Tier | Distance | Update Rate | Use Case |
|------|----------|-------------|----------|
| Near | ≤1 chunk | Every tick (10/sec) | Entities player is interacting with |
| Mid | 2 chunks | Every 2nd tick (5/sec) | Visible but not immediate |
| Far | >2 chunks | Every 5th tick (2/sec) | Edge of view, less critical |

**Bandwidth reduction**: ~60% compared to uniform 10/sec updates.

**Implementation**:
- Server tracks player positions
- Each entity update includes priority tier
- Client interpolates more aggressively for lower-tier entities

---

## 10. Implementation Phases

### MVP Target: Full Loop Lite

The first playable prototype includes:
1. Player movement (WASD + mouse aim)
2. Tile placement and breaking
3. Bug spawning and basic AI
4. Catching bugs with net tool
5. One processing station
6. Bug reproduction mechanics

### Phase 1: Foundation (Current)
- [x] Docker setup (Nakama + PostgreSQL)
- [x] Architecture document
- [ ] Go module structure (scaffolding)
- [ ] Basic RPC handlers (world create/list/join)
- [ ] Empty match handler (join/leave only)
- [ ] Unity 6 project setup
- [ ] Nakama SDK integration

### Phase 2: World Basics
- [ ] Tilemap chunk rendering (Unity)
- [ ] Player movement (client prediction + server reconciliation)
- [ ] Chunk subscription system
- [ ] Basic tile placement/breaking
- [ ] Object pooling for entities

### Phase 3: Entities (MVP Core)
- [ ] Bug spawning and basic AI
- [ ] Bug state machine (idle, wander, seek food)
- [ ] Player tools (net for catching)
- [ ] Bug reproduction mechanics
- [ ] One processing station

### Phase 4: Building & Automation
- [ ] Additional structures and stations
- [ ] Worker system
- [ ] Inventory and crafting
- [ ] Shop system (NPC)

### Phase 5: Infection & Events
- [ ] Meteor events
- [ ] Infection spread mechanics
- [ ] Cure mechanics (spray tool)

### Phase 6: Polish & Scale
- [ ] World moderation (kick/ban)
- [ ] Multiple access policies
- [ ] Performance optimization
- [ ] Persistence stress testing
- [ ] Multiple world instances

---

## 11. Design Decisions Log

Resolved questions and decisions made during planning:

| Question | Decision | Rationale |
|----------|----------|-----------|
| Chunk size | 32x32 tiles | Matches Factorio, visible area, good balance |
| Tick rate | **10/sec** | Industry standard (10-20 Hz), responsive gameplay |
| Region system | **Hybrid** | Procedural base + hand-placed POIs |
| Shop system | NPC shops | Players sell resources AND complete bounties for currency |
| Unity version | Unity 6 | Latest features, active support |
| 2D rendering | Built-in Tilemap | Native, efficient for grids |
| DOTS/ECS | **Not needed** | Client is render-only, standard Unity sufficient |
| Target entity count | 100-300 bugs | Achievable with object pooling |
| Entity sync | **3-tier priority** | Near=10/sec, Mid=5/sec, Far=2/sec - 60% bandwidth savings |
| Protocol | **JSON only** | Simplicity over optimization for prototype |
| Crash tolerance | **30s max** | Acceptable data loss for prototype phase |
| Entity positions | **Chunk + local float32** | Industry standard, avoids precision issues |
| Boundary handling | **End-of-tick transfer** | Simple, sufficient for slow-moving bugs |
| Access policies | **Public + Private** | Simple for prototype, can add friends-only later |
| Entity IDs | **UUID with type prefix** | Globally unique, no coordination needed |
| World generation | **Hand-crafted + procedural** | Unity layouts, procedural decoration |
| World size | **16x16 chunks** | 512x512 tiles, balanced for prototype |

### Open Questions (Remaining)

1. **Specific bug species list** - Deferred to content design phase
2. **Station types and tiers** - Deferred to Phase 4
3. **Exact region biomes** - Deferred to world generation implementation
4. **Monetization model** - Deferred

---

## Revision History

| Date | Changes |
|------|---------|
| 2024-12-22 | Initial architecture document |
| 2024-12-22 | Added Unity 6 config, scalability strategy, entity limits, player RPCs |
| 2024-12-22 | Research validation pass: tick rate 5→10/sec, added priority-based sync |
| 2024-12-22 | Added entity position system (Section 4.7): dual coordinates, boundary handling |
| 2024-12-22 | Added: access policies, entity IDs, world generation (4.8), player storage, error codes |
