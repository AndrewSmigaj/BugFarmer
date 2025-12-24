# Bug Farmer - Architecture Document

## Overview

Bug Farmer is a 2D multiplayer game where players farm bugs, build structures, and manage infection events. This document captures all architectural decisions and serves as the implementation roadmap.

---

## 1. Technical Stack

| Component | Technology | Status |
|-----------|------------|--------|
| Frontend | Unity 6 (2D) | Not started |
| Backend | Nakama 3.35.0 | ✅ Running |
| Database | PostgreSQL 15 | ✅ Running |
| Server Logic | Go modules | ✅ Compiles & loads |
| Realtime | Nakama WebSockets | Not started |

### 1.3 Dependency Versions (LOCKED)

These versions MUST match exactly for Go plugin compatibility:

```
github.com/heroiclabs/nakama-common  v1.44.0
google.golang.org/protobuf           v1.36.8
github.com/gofrs/uuid                v4.4.0+incompatible
go version                           1.23+
```

**Why this matters**: Go plugins must be compiled with identical dependency versions as the Nakama binary. Version mismatches cause `plugin was built with different version` errors.

### 1.1 Unity Configuration (LOCKED)

| Setting | Value | Rationale |
|---------|-------|-----------|
| Unity Version | 6000.2.9f1 | URP, modern features, active support |
| 2D System | Built-in Tilemap | Native chunk-based rendering, good for grids |
| Block Size | 8x8 pixels | Fine-grained placement, diggable terrain |
| Pixels Per Unit | 8 | 1 block = 1 Unity unit (all sprites use PPU=8) |
| Visible Area | ~64x48 blocks | ~1 chunk visible at default zoom |
| Perspective | Top-down | 4-direction facing (Down/Left/Right/Up) |

### 1.2 Client Architecture (LOCKED)

The Unity client is **render-only**. All game logic runs on the server.

| Responsibility | Server | Client |
|----------------|--------|--------|
| Bug AI | ✓ | |
| Movement validation | ✓ | |
| Reproduction logic | ✓ | |
| Collision detection | ✓ | |
| Tool hit detection | | ✓ |
| Damage calculation | ✓ | |
| Rendering | | ✓ |
| Input capture | | ✓ |
| Interpolation | | ✓ |
| Audio/VFX | | ✓ |

### 1.4 Tool Use Authority Model (LOCKED)

Terraria-style controls: WASD movement, mouse click to use tools.

**Model: Client Animation + Server Damage**

```
Client A clicks tree
  → Client A: plays swing animation immediately (local, responsive)
  → Client A → Server: {tool: "axe", target_id: "tree_123"}
  → Server: validates range, looks up tool damage from player stats
  → Server → ALL in chunk: {player_id: "A", tool: "axe", target_id: "tree_123", damage: 10, health: 90}
  → Client B: sees broadcast, plays A's swing animation, updates tree health
  → Client A: updates tree health (already played own animation)
```

**Why this model**:
- Animation plays instantly for the acting player (responsive feel)
- Server controls damage values (prevents cheating damage amounts)
- Other players see animations via broadcast
- Client can claim hits but cannot control damage amount

---

## 2. Project Structure

```
BugFarmer/
├── docker-compose.yml              # Nakama + PostgreSQL + Builder
├── nakama/
│   ├── data/
│   │   ├── local.yml               # Nakama config
│   │   └── .cookie                 # Session key
│   └── modules/                    # Go server code
│       ├── Dockerfile.build        # Plugin builder
│       ├── go.mod                  # Go dependencies
│       ├── go.sum                  # Dependency checksums
│       ├── main.go                 # Entry point, registers RPCs & match
│       ├── entities/
│       │   └── types.go            # EntityPosition, Entity interface
│       ├── rpc/
│       │   └── world.go            # world_create, world_list, world_join
│       └── world/
│           ├── match.go            # Match handler (runtime.Match impl)
│           ├── messages.go         # OpCode constants
│           └── state.go            # WorldState, PlayerState, WorldConfig
├── BugFarmerClient/                # Unity 6 project (6000.2.9f1, URP)
├── requirements.md                 # Game design requirements
└── ARCHITECTURE.md                 # This document
```

### 2.1 Docker Services

```yaml
services:
  postgres:     # Database, port 5432
  builder:      # Compiles Go plugin, exits after build
  nakama:       # Game server, ports 7349/7350/7351
```

**Build flow**:
1. `builder` compiles Go module → `backend.so`
2. Output stored in `modules` volume
3. `nakama` waits for builder, then loads `backend.so`

**Rebuild command**: `docker compose build builder && docker compose up -d`

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

**World Management (✅ Implemented):**

| RPC Name | Purpose | Request | Response |
|----------|---------|---------|----------|
| `world_create` | Create new world | `{name, access_policy}` | `{world_id, match_id}` |
| `world_list` | List available worlds | `{limit?, cursor?}` | `{worlds[], cursor?}` |
| `world_join` | Get match ID to join | `{world_id}` | `{match_id}` |

**Note**: `world_leave` was removed - socket disconnect triggers `MatchLeave` automatically.

**Access Policy Values:**
- `public` - Anyone can join
- `private` - Owner invite only

**Match Auto-Recreation**: If server restarts, `world_join` automatically recreates the match from stored metadata. Players don't see any error - the world persists transparently.

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
| 5 | C→S | Block placement |
| 6 | C→S | Block break |
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
ChunkSize: 64x64 blocks
BlockSize: 8x8 pixels (base unit)
ChunkPixelSize: 512x512 pixels (64 blocks × 8 pixels)
WorldSize: 16x16 chunks = 1024x1024 blocks = 8192x8192 pixels
ChunkViewDistance: 2 chunks (5x5 grid = 320x320 blocks visible)
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
    Blocks: [64][64]Block   // 64x64 blocks per chunk
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

### 4.5 Block Data Structure

```go
Block {
    GroundType: int         // Dirt, grass, stone, water, etc. (diggable at 8x8)
    ObjectType: int         // Wall, fence, furniture (0 = none)
    ObjectID: string        // Reference to object data if any
}
```

**Block vs Entity Scale:**
- Block = 1 Unity unit = 8x8 pixels (base grid unit)
- Player = 4x4 blocks = 32x32 pixels
- Fence piece = 1x3 blocks = 8x24 pixels
- Plant area = 4x4 blocks required (game rule)

### 4.6 Spawn Suppression Rule (LOCKED)

Bugs CANNOT spawn on blocks where `ObjectType > 0`. This applies to:
- Natural spawns during simulation
- Rehydration when Tier2 → Tier0

### 4.7 Entity Position System (LOCKED)

**Dual Coordinate System:**
- **Blocks**: Integer grid (0-63) within chunk - for ground, walls, objects
- **Entities**: Float position (0.0-64.0) within chunk - for bugs, players, workers

**Entity Position Structure:**
```go
EntityPosition {
    ChunkX, ChunkY int       // Which chunk the entity is in
    LocalX, LocalY float32   // Position within chunk (0.0 to 64.0)
}
```

**World Position Conversion:**
```go
// Chunk-local to world (ChunkSize = 64):
WorldX = ChunkX * 64 + LocalX
WorldY = ChunkY * 64 + LocalY

// World to chunk-local:
ChunkX = floor(WorldX / 64)
ChunkY = floor(WorldY / 64)
LocalX = WorldX - (ChunkX * 64)
LocalY = WorldY - (ChunkY * 64)
```

**Chunk Boundary Handling (End-of-Tick):**
```
At end of each tick:
1. Check if LocalX/LocalY outside [0, 64)
2. If LocalX >= 64: ChunkX++, LocalX -= 64
3. If LocalX < 0: ChunkX--, LocalX += 64
4. Same for Y axis
5. If chunk changed, move entity to new chunk's entity list
```

**Block Collision Check:**
```go
// Entity at (LocalX=15.7, LocalY=22.3) checks block (15, 22)
blockX := int(math.Floor(entity.LocalX))
blockY := int(math.Floor(entity.LocalY))
block := chunk.Blocks[blockX][blockY]
```

### 4.8 World Generation (LOCKED)

Worlds use hand-crafted layouts with procedural decoration.

```
WorldSize: 16x16 chunks = 1024x1024 blocks = 8192x8192 pixels
ChunkSize: 64x64 blocks = 512x512 pixels
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

// Block Placement (OpCode 5)
{"chunk": "3,4", "x": 15, "y": 20, "type": "object", "id": 2}

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
- [x] Docker setup (Nakama + PostgreSQL + Builder)
- [x] Architecture document
- [x] Go module structure with proper dependency versions
- [x] RPC handlers: `world_create`, `world_list`, `world_join`
- [x] Match handler with full lifecycle (init/join/leave/loop/terminate/signal)
- [x] World state management (players, config, presences)
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
| Block size | 8x8 pixels | Fine-grained placement, diggable terrain |
| PPU | 8 | 1 Unity unit = 1 block for all sprites |
| Chunk size | 64x64 blocks | Same pixel area as before (512x512 px) |
| Server grid | Uniform 8x8 | Full granularity, no hybrid layers |
| Custom art | User-created | Scrapping asset packs for custom 8x8 art |
| Entity scale | Player = 4x4 blocks | 32x32 pixels, bigger than placeable blocks |
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
| World size | **16x16 chunks** | 1024x1024 blocks = 8192x8192 pixels |
| world_leave RPC | **Removed** | Socket disconnect triggers MatchLeave automatically |
| Match persistence | **Auto-recreate** | world_join recreates match if server restarted |
| Tool authority | **Client anim + Server damage** | Responsive feel, server controls damage values |
| Player facing | **Direction enum (4-way)** | Top-down view: Down/Left/Right/Up (0-3) |
| Game perspective | **Top-down** | Like Stardew Valley, not side-view |
| UUID generation | **gofrs/uuid package** | Not in NakamaModule, use standard Go library |
| Storage ownership | **System-owned** | UserID="" for public world listing |
| Config values | **Configurable struct** | WorldConfig holds ChunkSize, TickRate, etc. |

### Open Questions (Remaining)

1. **Specific bug species list** - Deferred to content design phase
2. **Station types and tiers** - Deferred to Phase 4
3. **Exact region biomes** - Deferred to world generation implementation
4. **Monetization model** - Deferred

---

## 12. Quick Reference

### Starting the Server

```bash
cd /mnt/c/Users/emily/BugFarmer
sudo docker compose up -d
```

### Rebuilding After Code Changes

```bash
sudo docker compose down
sudo docker compose build builder
sudo docker compose up -d
```

### Checking Logs

```bash
# Module loading
sudo docker compose logs nakama | grep -E "(Bug Farmer|Registered|error)"

# All Nakama logs
sudo docker compose logs -f nakama
```

### Nakama Console

- URL: http://localhost:7351
- Default login: admin / password

### Key Files to Edit

| Purpose | File |
|---------|------|
| Add new RPC | `nakama/modules/rpc/world.go` + register in `main.go` |
| Match logic | `nakama/modules/world/match.go` |
| Game state | `nakama/modules/world/state.go` |
| OpCodes | `nakama/modules/world/messages.go` |
| Entity types | `nakama/modules/entities/types.go` |

### Verified Working State

As of 2024-12-23:
- Module loads: "Bug Farmer module loaded successfully"
- RPCs registered: `world_create`, `world_join`, `world_list`
- Match handler registered: `world`

---

## Revision History

| Date | Changes |
|------|---------|
| 2024-12-22 | Initial architecture document |
| 2024-12-22 | Added Unity 6 config, scalability strategy, entity limits, player RPCs |
| 2024-12-22 | Research validation pass: tick rate 5→10/sec, added priority-based sync |
| 2024-12-22 | Added entity position system (Section 4.7): dual coordinates, boundary handling |
| 2024-12-22 | Added: access policies, entity IDs, world generation (4.8), player storage, error codes |
| 2024-12-23 | **Phase 1 Implementation Complete**: Go module compiles and loads |
| 2024-12-23 | Added dependency versions (1.3), tool use authority model (1.4), docker services (2.1) |
| 2024-12-23 | Updated RPC section: removed world_leave, added auto-recreate match behavior |
| 2024-12-23 | Added implementation decisions: FacingLeft, UUID generation, system-owned storage |
| 2024-12-23 | **Block System Overhaul**: Tiles→Blocks, 32px→8px, ChunkSize 32→64, PPU=8 |
| 2024-12-23 | Updated all sections for 8x8 block grid, entity scale (player 4x4 blocks) |
