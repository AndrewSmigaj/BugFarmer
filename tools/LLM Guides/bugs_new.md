# Bug System Architecture - BugFarmer

## Overview

This document defines the architecture for insects (bugs) in BugFarmer.

**DOCUMENT STRUCTURE:**
- **Part 1: Current Implementation** - What actually exists in the code today
- **Part 2: Planned Implementation** - What needs to be added (phased)

---

# PART 1: CURRENT IMPLEMENTATION

Everything in this section exists in the codebase and can be verified.

---

## 1.1 Server-Side (Go/Nakama)

### Key Files

| File | Purpose |
|------|---------|
| `nakama/modules/world/match.go` | Match lifecycle, tick loop, message handlers |
| `nakama/modules/world/state.go` | WorldState, PlayerState structs |
| `nakama/modules/world/messages.go` | OpCodes and message structs |
| `nakama/modules/world/resource_query.go` | FindNearbyResources for swarm attraction |
| `nakama/modules/entities/swarm.go` | SwarmState struct, Think/Move methods |
| `nakama/modules/entities/species.go` | BugSpecies struct and LoadSpecies |
| `nakama/modules/entities/types.go` | EntityPosition, Direction, Entity interface |
| `nakama/modules/entities/vec.go` | Vec2 math operations |
| `nakama/data/species.json` | Species definitions (fly, butterfly, etc.) |

### SwarmState (swarm.go)

```go
type SwarmState struct {
    ID        string
    SpeciesID string
    Position  EntityPosition
    Radius    float32   // Visual spread radius in blocks
    Count     int       // Number of bugs in swarm
    Facing    Direction // Movement direction hint for client
    Velocity  Vec2      // Current movement
    HomePos   EntityPosition
    WanderRad float32   // Max distance from home

    ReproduceCooldown float32 // Seconds until can reproduce

    // Condition meter (for subduing mechanics, 0-100 range)
    ConditionValue float32
    CurrentHP      int

    // Lifecycle (server-owned)
    Phase             string  // "feeding", "reproducing", "idle"
    Satiation         float32 // 0-100, increases when bugs feed
    ReproductionMeter float32 // 0-100, increases when bugs visit breeding sites

    // Movement target (pre-validated path)
    TargetX       float32 // Destination X (validated to be reachable)
    TargetY       float32 // Destination Y
    HasTarget     bool    // Whether we have an active target
    NextThinkTick int64   // Tick when swarm next evaluates targets
}

// Methods that exist:
func (s *SwarmState) WorldX(chunkSize int) float32
func (s *SwarmState) WorldY(chunkSize int) float32
func (s *SwarmState) Think(species *BugSpecies, chunkSize int, resourceX, resourceY float32, isBlocked BlockedChecker)
func (s *SwarmState) Move(deltaTime float32, species *BugSpecies, chunkSize int)
func (s *SwarmState) CheckPhaseTransition(species *BugSpecies)
func (s *SwarmState) GetCurrentAttractions(species *BugSpecies) []string
```

**Think/Move Split:** Server calls `Think()` every 30-50 ticks (3-5 seconds) to pick a new target. `Move()` is called every tick to apply velocity toward the target. This reduces pathfinding cost.

**Note:** Current SwarmState has `Count` (a single int), NOT a per-member roster. The `CurrentHP` is a single value for the whole swarm, NOT per-member.

### BugSpecies (species.go)

```go
type BugSpecies struct {
    ID          string `json:"id"`
    Name        string `json:"name"`
    Description string `json:"description"`
    Category    string `json:"category"` // "swarm", "individual", "boss"

    // Movement
    BaseSpeed        float32 `json:"base_speed"`
    WanderRadius     float32 `json:"wander_radius"`
    WanderChangeRate float32 `json:"wander_change_rate"` // Chance per tick to change direction

    // Vision-based resource seeking (server-side swarm AI)
    VisionRange        float32             `json:"vision_range"`        // How far swarm can "see" resources
    AttractionsByPhase map[string][]string `json:"attractions_by_phase"` // phase → resource IDs
    AttractionStrength float32             `json:"attraction_strength"`

    // Lifecycle parameters
    FeedAmount         float32 `json:"feed_amount"`          // Satiation per feeding event
    BreedAmount        float32 `json:"breed_amount"`         // Reproduction progress per breeding event
    SatiationDecayRate float32 `json:"satiation_decay_rate"` // Per second in idle

    // Swarm-specific (category=swarm only)
    MinSwarmSize   int     `json:"min_swarm_size"`
    MaxSwarmSize   int     `json:"max_swarm_size"`
    SwarmRadius    float32 `json:"swarm_radius"`
    MergeRadius    float32 `json:"merge_radius"`
    SplitThreshold int     `json:"split_threshold"`
    SplitChance    float32 `json:"split_chance"`

    // Player Reaction AI
    PlayerReaction string  `json:"player_reaction"` // "ignore", "flee", "attack", "curious"
    ReactionRadius float32 `json:"reaction_radius"`
    FleeSpeedMult  float32 `json:"flee_speed_mult"`
    AttackDamage   int     `json:"attack_damage"`
    AttackCooldown float32 `json:"attack_cooldown"`

    // Catching
    NetSize            string             `json:"net_size"`
    CatchCondition     string             `json:"catch_condition"`
    ConditionThreshold float32            `json:"condition_threshold"`
    ConditionDecay     float32            `json:"condition_decay"`
    ConditionTools     map[string]float32 `json:"condition_tools"`

    // HP
    MaxHP       int            `json:"max_hp"`
    DamageTools map[string]int `json:"damage_tools"`

    // Economy
    SellPrice int `json:"sell_price"`

    // Reproduction
    BreedingPlants    []string `json:"breeding_plants"`
    EggCountMin       int      `json:"egg_count_min"`
    EggCountMax       int      `json:"egg_count_max"`
    HatchTime         float32  `json:"hatch_time"`
    ReproduceCooldown float32  `json:"reproduce_cooldown"`

    // Sprites
    SpriteID    string `json:"sprite_id"`
    EggSpriteID string `json:"egg_sprite_id"`
}
```

**Vision-based attraction:** Swarms use `VisionRange` to find nearby resources matching `AttractionsByPhase[currentPhase]`. Flies (vision 8) stay local; butterflies (vision 24) seek distant flowers.

### OpCodes (messages.go)

```go
// Bug System OpCodes (Server → Client)
const (
    OpCodeSwarmUpdate int64 = 20 // Batched swarm positions
)

// Bug Catching OpCodes
const (
    OpCodeCatchBug  int64 = 24 // C→S: Player clicks to catch
    OpCodeBugCaught int64 = 25 // S→C: Broadcast catch event
    OpCodeEquipTool int64 = 27 // C→S: Player equips/unequips a tool
)

// Bug Simulation OpCodes (Phase 1 - Deterministic Per-Bug)
const (
    OpCodeRequestSample       int64 = 61 // S→C: Request positions for specific bug IDs
    OpCodeSampleResponse      int64 = 62 // C→S: Positions for requested bugs
    OpCodeSampleBroadcast     int64 = 63 // S→C: Sample for comparison by all clients
    OpCodeRequestSnapshot     int64 = 66 // C→S: Client requests full snapshot (drift detected)
    OpCodeFullSnapshot        int64 = 67 // S→C: Full bug positions for swarm
    OpCodeWorldInit           int64 = 68 // S→C: WorldSeed on join (sent once)
    OpCodeRequestInteractions int64 = 69 // S→C: Request aggregated interaction counts
    OpCodeInteractionReport   int64 = 70 // C→S: Aggregated interaction counts per swarm
)
```

**Note:** OpCodes 50-60 (hit/catch/meter events) do NOT exist yet. Phase 1 sync OpCodes (61-70) ARE defined but client handlers not fully implemented.

### SwarmData Message (messages.go)

```go
type SwarmData struct {
    ID        string  `json:"id"`
    SpeciesID string  `json:"species_id"`
    X         float32 `json:"x"`
    Y         float32 `json:"y"`
    Radius    float32 `json:"radius"`
    Count     int     `json:"count"`
    Facing    int     `json:"facing"`
}

type SwarmUpdateMessage struct {
    Swarms []SwarmData `json:"swarms"`
}
```

**What does NOT exist in SwarmData:**
- `tick` field (for deterministic position)
- `roster` field (member IDs)

### Match Handlers (match.go)

**Tick Loop Structure:**
- `Think()` called every 30-50 ticks (3-5 seconds) via `NextThinkTick` check
- `Move()` called every tick to apply velocity toward target
- `CheckPhaseTransition()` called to update lifecycle state
- Resources found via `FindNearbyResources()` in `resource_query.go`

**spawnInitialSwarms():**
- Spawns swarms from zone configuration or defaults
- Loads species from `data/species.json`

**checkSwarmMerging():**
- Server-side merge check every 50 ticks
- Merges same-species swarms within MergeRadius

**checkSwarmSplitting():**
- SERVER-SIDE split based on SplitThreshold and SplitChance
- Uses random chance, NOT fly positions
- **Architecture violation:** Should be client-reported, not server-computed

**handleCatchBug():**
- Rate limited 200ms between catches
- Validates click within reach
- Trusts client count, no per-member targeting

**handleInteractionReport() (OpCode 70):**
- Receives aggregated food/breed counts from client
- Updates `Satiation` and `ReproductionMeter` on swarms
- Triggers phase transitions via `CheckPhaseTransition()`

**WorldInit (OpCode 68):**
- Sent on player join
- Contains `WorldSeed` (int64) for deterministic client simulation
- Contains current server `Tick` for sync

---

## 1.2 Client-Side (Unity/C#)

### Key Files

| File | Purpose |
|------|---------|
| `SwarmManager.cs` | Singleton, handles OpCode 20/25, creates/destroys SwarmVisuals |
| `SwarmVisual.cs` | Single swarm rendering, fly spawning, position interpolation |
| `FlyBehavior.cs` | Brownian motion for individual flies (legacy system) |
| `BugMessages.cs` | Message structs for OpCodes 20, 24, 25 |
| `CatchingController.cs` | Input handling, catch detection |
| `Bugs/DeterministicRandom.cs` | Seeded PRNG with FNV-1a hashing (per-bug seeds) |
| `Bugs/FixedPoint.cs` | Fixed-point math struct (scale 1000) for determinism |
| `Bugs/FixedPointMath.cs` | FixedPoint2 for 2D vectors, distance calculations |
| `Bugs/BugAgent.cs` | Per-bug state: position, velocity, behavior, RNG |
| `Bugs/IBugMovement.cs` | Interface for species-specific movement |
| `Bugs/BrownianMovement.cs` | Erratic fly-like movement (deterministic) |
| `Bugs/GlidingMovement.cs` | Smooth butterfly-like movement (deterministic) |
| `Bugs/MovementFactory.cs` | Creates movement instances by species ID |
| `Bugs/BugCollision.cs` | Collision detection infrastructure |

### SwarmManager.cs

```csharp
public class SwarmManager : MonoBehaviour
{
    public static SwarmManager Instance { get; private set; }

    private readonly Dictionary<string, SwarmVisual> _swarms = new();

    // Handles OpCode 20 (SwarmUpdate) and 25 (BugCaught)

    public SwarmVisual GetSwarm(string swarmId);
    public IEnumerable<SwarmVisual> GetAllSwarms();
    public List<CatchResult> CatchAtPosition(Vector2 worldPosition, float catchRadius);
}
```

### SwarmVisual.cs

```csharp
public class SwarmVisual : MonoBehaviour
{
    private readonly List<FlyBehavior> _flies = new();
    private static readonly Stack<FlyBehavior> _flyPool = new();  // Object pooling

    // Position interpolation (150ms)
    private Vector2 _previousPos, _targetPos;
    private const float InterpDuration = 0.15f;

    public void Initialize(SwarmData data, GameObject flyPrefabOverride = null);
    public void UpdateFromServer(SwarmData data);
    public void RemoveRandomFlies(int count);
    public int RemoveFliesInRadius(Vector2 worldPosition, float radius);
}
```

**Key implementation details:**
- Fly spawning uses `Random.insideUnitCircle` - NON-DETERMINISTIC
- Flies tracked as `List<FlyBehavior>`, NOT by member ID
- No split detection code exists

### BugMessages.cs

```csharp
public class SwarmData {
    public string id;
    public string species_id;
    public float x, y;
    public float radius;
    public int count;
    public int facing;
}

public class SwarmUpdateMessage {
    public SwarmData[] swarms;
}
```

**What does NOT exist:**
- `tick` field in SwarmUpdateMessage
- `roster` field in SwarmData
- SwarmSplitMessage, MemberRemovedMessage, etc.

### FlyBehavior.cs (Legacy)

```csharp
public class FlyBehavior : MonoBehaviour
{
    [SerializeField] private float speed = 2f;
    [SerializeField] private float directionChangeInterval = 0.3f;
    [SerializeField] private float wanderRadius = 5f;

    // Uses Random for Brownian motion - NOT deterministic
    // Update(): random direction changes, bias back to home
}
```

**Note:** This is the LEGACY system used by SwarmVisual. Being replaced by BugAgent + deterministic movement.

### DeterministicRandom.cs (Phase 1 Foundation)

```csharp
// IMPLEMENTED - per-bug seeded PRNG using xorshift32
public class DeterministicRandom
{
    private uint _state;

    public DeterministicRandom(long seed);

    /// Creates RNG for specific bug. Same inputs = same sequence on all clients.
    public static DeterministicRandom ForBug(long worldSeed, string swarmId, int bugId);

    /// Combines (worldSeed, swarmId, bugId) using FNV-1a 64-bit hash.
    public static long ComputeBugSeed(long worldSeed, string swarmId, int bugId);

    public float NextFloat();           // [0, 1)
    public float Range(float min, float max);
    public int RangeInt(int min, int max);
}
```

### FixedPoint.cs (Phase 1 Foundation)

```csharp
// IMPLEMENTED - fixed-point math to avoid floating-point non-determinism
public struct FixedPoint
{
    public const int Scale = 1000;  // 3 decimal places
    public int Value;               // Actual = Value / 1000.0f

    public static FixedPoint FromFloat(float f);
    public float ToFloat();
    // Operators: +, -, *, /
}

public struct FixedPoint2  // 2D vector
{
    public FixedPoint X, Y;

    public FixedPoint SqrDistanceTo(FixedPoint2 other);
    public FixedPoint SqrMagnitude();
    public Vector2 ToVector2();
}
```

### BugAgent.cs (Phase 1 Foundation)

```csharp
// IMPLEMENTED - per-bug state (NOT yet integrated into SwarmVisual)
public class BugAgent
{
    public int BugId;
    public string SwarmId;
    public string SpeciesId;

    public DeterministicRandom Rng;   // Per-bug seeded RNG
    public FixedPoint2 Position;      // Fixed-point for determinism
    public FixedPoint2 Velocity;
    public IBugMovement Movement;     // Species-specific movement

    public string CurrentBehavior;    // "wander", "flee", "attack", "curious"
    public string TargetPlayerId;

    public BugAgent(long worldSeed, string swarmId, string speciesId, int bugId, FixedPoint2 startPosition);

    /// Simulate one tick: update behavior, apply movement, update position
    public void SimulateTick(FixedPoint2 swarmCenter, List<PlayerTarget> players);
}
```

**Stochastic alert system:** Bugs don't all react instantly. They have a 30% chance per check (every 5-15 ticks) to notice a player within `ReactionRadius`. This creates emergent behavior - some bugs flee first, others follow.

### IBugMovement Interface

```csharp
public interface IBugMovement
{
    void UpdateMovement(BugAgent bug, FixedPoint2 swarmCenter, FixedPoint wanderRadiusSqr);
    void MoveToward(BugAgent bug, FixedPoint2 target);
    void MoveAwayFrom(BugAgent bug, FixedPoint2 threat);
    void MoveTowardSlow(BugAgent bug, FixedPoint2 target);  // For "curious"
}
```

**Implementations:** `BrownianMovement` (erratic buzzing for flies), `GlidingMovement` (smooth arcs for butterflies)

---

## 1.3 What's Missing (Integration Gaps)

The following components exist but are **NOT YET INTEGRATED**:

- **BugAgent not wired into SwarmVisual** - `BugAgent.cs` exists with full per-bug state, but `SwarmVisual` still uses `List<FlyBehavior>` with non-deterministic `Random.insideUnitCircle`
- **Sample/snapshot handlers incomplete** - OpCodes 61-67 are defined, but client comparison logic and snapshot request handlers not implemented
- **Collision detection not hooked in** - `BugCollision.cs` exists but bugs don't check terrain/occupants during movement
- **No per-member roster on server** - Server has `Count` but no `MemberIDs []int` for targeting specific bugs
- **Server-side split detection** - Should be client-requested per architecture doc, but server uses random `SplitChance`
- **OpCodes 50-60 not defined** - Hit/catch/meter events for per-member combat don't exist yet

**What DOES exist now:**
- ✓ `nakama/data/species.json` with lifecycle/attraction data
- ✓ `DeterministicRandom`, `FixedPoint`, `BugAgent` classes
- ✓ `IBugMovement` with `BrownianMovement` and `GlidingMovement`
- ✓ Server-side resource seeking with `FindNearbyResources()`
- ✓ Lifecycle phases (feeding → reproducing → idle)
- ✓ OpCodes 61-70 for sample/snapshot sync (message structs defined)

---

## 1.4 World Building / Occupant System

### Multi-Cell Occupants (Footprint System)

Occupants like trees, fences, and buildings can span multiple cells. The system uses an **anchor + footprint** model:

- **Anchor cell:** The primary cell where the occupant is logically placed (bottom-left corner)
- **Footprint cells:** Additional cells occupied by the entity (based on size/direction)

### Storage Format

**Anchor cell:** `{"id":"tree_oak","dir":0,"anchor":true}`
**Footprint cell:** `{"id":"tree_oak","dir":0}` (anchor field omitted = false)

### PlacedOccupant Structure

**Server (Go) - occupants.go:**
```go
type PlacedOccupant struct {
    ID     string `json:"id"`
    Dir    int    `json:"dir"`    // 0-3 facing direction
    Anchor bool   `json:"anchor"` // true for anchor cell, false for footprint
}
```

**Client (C#) - WorldMessages.cs:**
```csharp
public class PlacedOccupant {
    public string id;
    public int dir;
    public bool anchor;  // true = anchor cell, false = footprint cell
}
```

### Key Files

| File | Purpose |
|------|---------|
| `nakama/modules/world/occupants.go` | PlacedOccupant struct, OccupantCell helpers |
| `nakama/modules/world/zone.go` | Chunk storage, SetOccupant, SetFootprintCell |
| `nakama/modules/world/handlers_world.go` | handleTilePlace, handleTileBreak |
| `TilemapManager.cs` | Client chunk storage, rendering, occupancy queries |

### Client Data Structures

```csharp
// Stores ALL cells (anchor + footprint) - use for collision/placement checks
private Dictionary<Vector2Int, ChunkOccupantData> _loadedChunks;

// Stores rendered GameObjects (anchor cells ONLY) - use for sprite management
private Dictionary<Vector2Int, GameObject> _occupantObjects;
```

**Critical distinction:**
- `_loadedChunks` has data for **every occupied cell** → use for `IsCellOccupied()`, `GetOccupantAt()`
- `_occupantObjects` has **only anchor cells** → use for visual sprite management

### Server → Client Sync Flow

**Initial Load (ChunkData - OpCode 44):**
1. Server sends full chunk JSON with ALL cells (anchor + footprint)
2. Client parses into `_loadedChunks[chunkPos].Occupants[y][x]`
3. Client renders only anchor cells (`RenderOccupant` checks `anchor` flag)

**Real-time Update (WorldUpdate - OpCode 46):**
1. Server broadcasts **only anchor cell** via WorldUpdate message
2. Client receives anchor cell with `anchor=true`
3. Client computes full footprint via `EntityDatabase.GetFootprint(id, dir)`
4. Client updates ALL cells in `_loadedChunks` via `UpdateOccupantCellData()`
5. Client renders sprite only at anchor position

### Occupancy Checking

```csharp
// CORRECT: Checks _loadedChunks which has ALL occupied cells (anchor + footprint)
public string GetOccupantAt(Vector2Int cellPos) {
    // Returns occupant ID at cell, or null if empty
}

// CORRECT: Uses GetOccupantAt internally for proper footprint detection
public bool IsCellOccupied(Vector2Int cellPos) {
    string occ = GetOccupantAt(cellPos);
    return !string.IsNullOrEmpty(occ);
}
```

**Warning:** Do NOT use `_occupantObjects.ContainsKey()` for occupancy checks - it only has anchor cells and will miss footprint cells.

### Server-Side Occupant Placement (handleTilePlace)

```go
// 1. Store anchor cell
chunk.SetOccupant(lx, ly, occ)  // Sets Anchor=true automatically

// 2. Store footprint cells for multi-cell occupants
w, h := def.GetFootprint(msg.Direction)
for dy := 0; dy < h; dy++ {
    for dx := 0; dx < w; dx++ {
        if dx == 0 && dy == 0 { continue }  // Skip anchor
        bChunk.SetFootprintCell(blx, bly, msg.OccupantID, msg.Direction)
    }
}

// 3. Broadcast only anchor cell to clients
m.broadcastWorldUpdate(dispatcher, state, cx, cy, msg.GridX, msg.GridY, "", occ)
```

### Server-Side Occupant Breaking (handleTileBreak)

```go
// 1. Clear anchor cell
chunk.ClearOccupant(lx, ly)

// 2. Clear all footprint cells
w, h := def.GetFootprint(occ.Dir)
for dy := 0; dy < h; dy++ {
    for dx := 0; dx < w; dx++ {
        bChunk.ClearOccupant(blx, bly)
    }
}

// 3. Broadcast removal (nil occupant)
m.broadcastWorldUpdate(dispatcher, state, cx, cy, msg.GridX, msg.GridY, "", nil)
```

---

## 1.5 Implementation Status Summary

| Component | Status | Location | Notes |
|-----------|--------|----------|-------|
| DeterministicRandom | ✓ Complete | `Bugs/DeterministicRandom.cs` | Per-bug seeded xorshift32 PRNG |
| FixedPoint math | ✓ Complete | `Bugs/FixedPoint.cs`, `FixedPointMath.cs` | Scale 1000, deterministic ops |
| BugAgent class | ✓ Complete | `Bugs/BugAgent.cs` | Per-bug state, behaviors, SimulateTick |
| BrownianMovement | ✓ Complete | `Bugs/BrownianMovement.cs` | Erratic fly movement |
| GlidingMovement | ✓ Complete | `Bugs/GlidingMovement.cs` | Smooth butterfly arcs |
| MovementFactory | ✓ Complete | `Bugs/MovementFactory.cs` | Creates movement by species |
| BugCollision | ✓ Structure | `Bugs/BugCollision.cs` | Framework exists, not hooked in |
| species.json | ✓ Complete | `nakama/data/species.json` | Full lifecycle/attraction data |
| Server resource seeking | ✓ Working | `resource_query.go`, `swarm.go` | Think/Move split, FindNearbyResources |
| Lifecycle phases | ✓ Working | `swarm.go` | feeding → reproducing → idle |
| OpCodes 61-70 | ✓ Defined | `messages.go` | Sample/snapshot/interaction structs |
| **SwarmVisual integration** | **⚠ Pending** | `SwarmVisual.cs` | Still uses List<FlyBehavior> |
| **Client sync handlers** | **⚠ Pending** | - | OpCode 61-67 handlers not implemented |
| **Server member roster** | **⚠ Pending** | `swarm.go` | No MemberIDs for per-bug targeting |

**Next integration step:** Wire `BugAgent` into `SwarmVisual` to replace `FlyBehavior`. This enables deterministic per-bug simulation on all clients.

---

# PART 2: PLANNED IMPLEMENTATION

Everything in this section is TO BE IMPLEMENTED. Organized by implementation phase.

---

## Two-Layer Architecture

The bug system has two distinct simulation layers:

### Layer 1: Server-Side Swarm AI (WHERE swarms go)
- Server owns swarm CENTER movement
- Each species has a **vision range** - how far the swarm can "see" resources
- Butterflies: long vision (24 blocks) → swarm centers move far to reach flowers
- Flies: short vision (8 blocks) → swarm centers stay local near compost/fruit
- Server runs resource detection, biases swarm velocity toward attractive objects
- This creates purposeful, species-specific swarm movement

### Layer 2: Client-Side Bug Movement (HOW individual bugs move)
- ALL clients simulate per-bug positions locally (deterministic)
- Bugs have species-specific **movement patterns**:
  - Flies: Brownian motion (erratic buzzing, short intent range)
  - Butterflies: Gliding motion (smooth arcs, long intent range)
- All bugs **bias toward swarm center** (follow where server moved it)
- When butterfly swarm center moves to flowers, individual butterflies glide there gracefully

### Key Insight: Intent Range
Different bugs have different "vision" when choosing local movement:

| Species | Intent Range | Dir Change Rate | Visual Result |
|---------|--------------|-----------------|---------------|
| Fly | 1.5 blocks | 30% per tick | Erratic buzzing, stays local |
| Butterfly | 10 blocks | 5% per tick | Long gliding arcs across screen |

- Flies pick random directions nearby → frequent changes → buzzy movement
- Butterflies pick destination points far away → commit to direction → graceful arcs

---

## 2.1 Phase 1: Per-Member Tracking + Local Simulation with Sync

### Goal
Enable targeting specific bugs within a swarm. All clients simulate locally for responsive rendering. Server requests snapshots for sync.

### Hard Locks (MANDATORY)

```
1. Server owns swarm-level (center, count, meters, reproduction)
2. ALL clients simulate per-bug positions locally (same code, same ticks)
3. Bugs must not phase through blocks/fences. Collision resolved locally.
4. Server requests snapshots from one player for sync (late joiners, drift correction)
5. Combat/catching goes through SERVER (not a special "authority" client)
6. No per-bug-per-frame streaming. Sync is periodic, on-demand.
7. Inactive areas are aggregated. No per-agent sim in chunks with no players.
```

### Core Concepts

| Term | Definition |
|------|------------|
| **Chunk** | Fixed-size region (32x32 or 64x64 tiles). Sync is chunk-scoped. |
| **Active Chunk** | A chunk within interest radius of any player. All nearby players simulate. |
| **Inactive Chunk** | A chunk with no players nearby. Bugs represented as aggregated SwarmGroups only. |
| **Bug Agent** | A single simulated bug with pos, vel, behavior. Each client creates these locally. |
| **Swarm Group** | Species-specific grouping (count, meters, reproduction). Server always owns this. |

### Simulation Model

| Layer | Owner | What It Does |
|-------|-------|--------------|
| Swarm-level | Server (Nakama) | Center movement, targeting, idle mechanics, reproduction, aggregation |
| Per-bug | ALL clients (locally) | Individual bug positions, terrain collision, behaviors |
| Sync | Server requests from one player | Late joiner positions, drift correction |

**Key insight:** Everyone simulates. Sync is just for consistency, not authority.

### All Clients Simulate Locally

Every player in a chunk runs the bug simulation:
- Same tick-based movement code
- Same collision resolution against terrain
- Same species behaviors

This gives responsive local rendering. Players see bugs moving immediately without network delay.

### Deterministic Simulation via Per-Bug Seeded PRNG

To ensure all clients see bugs in the same positions:

1. **Each bug has its own seed**: `seed = hash(worldSeed, swarmID, bugID)`
2. **Independent RNG per bug**: Removal of bug 2 doesn't affect bug 3's RNG
3. **Fixed-point positions**: Use int32 × 1000 to avoid floating point drift
4. **ID-order updates**: Bugs MUST be updated in ascending bugID order
5. **Lerp on resync**: Smooth correction over 250ms avoids visual pops

```go
// Server-side: SwarmGroup needs world seed (shared) not per-swarm seed
type SwarmGroup struct {
    // ... existing fields ...
    // WorldSeed is global, not per-swarm
}

// Bug seed derived from stable IDs
func bugSeed(worldSeed int64, swarmID string, bugID int) int64 {
    h := fnv.New64a()
    binary.Write(h, binary.LittleEndian, worldSeed)
    h.Write([]byte(swarmID))
    binary.Write(h, binary.LittleEndian, int64(bugID))
    return int64(h.Sum64())
}
```

```csharp
// Client-side: Deterministic RNG per BUG (not per swarm)
public class DeterministicRandom {
    private uint state;

    public DeterministicRandom(long seed) {
        state = (uint)(seed ^ (seed >> 32));
        if (state == 0) state = 1; // Prevent zero state
    }

    public float NextFloat() {
        // Xorshift32
        state ^= state << 13;
        state ^= state >> 17;
        state ^= state << 5;
        return (state & 0x7FFFFFFF) / (float)0x7FFFFFFF;
    }

    public float Range(float min, float max) {
        return min + NextFloat() * (max - min);
    }
}

// Each bug has its own RNG
public class BugAgent {
    public int BugId;
    public DeterministicRandom Rng;  // Seeded with hash(worldSeed, swarmId, bugId)
    // ...
}
```

### Fixed-Point Positions

To eliminate floating point non-determinism across platforms:

```csharp
// Use int32 with 3 decimal places (multiply by 1000)
public struct FixedPoint {
    public int Value;  // Actual position = Value / 1000.0f

    public static FixedPoint FromFloat(float f) => new FixedPoint { Value = (int)(f * 1000) };
    public float ToFloat() => Value / 1000f;

    public static FixedPoint operator +(FixedPoint a, FixedPoint b) =>
        new FixedPoint { Value = a.Value + b.Value };
}

// BugAgent uses fixed-point internally
public class BugAgent {
    public FixedPoint PosX, PosY;  // Fixed-point for determinism
    public FixedPoint VelX, VelY;

    public Vector2 WorldPosition => new Vector2(PosX.ToFloat(), PosY.ToFloat());
}
```

### Update Order Rule

**CRITICAL:** Bugs must be updated in ascending ID order to ensure all clients make RNG calls in the same sequence:

```csharp
void SimulateTick() {
    // Sort by ID (or use sorted data structure)
    var sortedBugs = _bugs.OrderBy(b => b.BugId);

    foreach (var bug in sortedBugs) {
        bug.UpdateMovement();  // RNG calls happen in same order on all clients
    }
}
```

### Resync with Lerp Correction

When a snapshot is received, don't teleport bugs - smoothly correct over 250ms:

```csharp
void OnSnapshotReceived(FullSnapshotMessage snapshot) {
    foreach (var bugData in snapshot.Bugs) {
        var bug = GetBug(bugData.BugID);
        if (bug != null) {
            // Start lerping to correct position
            bug.StartCorrection(bugData.X, bugData.Y, duration: 0.25f);
        }
    }
}

// In BugAgent
public void StartCorrection(float targetX, float targetY, float duration) {
    _correctionStart = WorldPosition;
    _correctionTarget = new Vector2(targetX, targetY);
    _correctionTimer = duration;
}

void Update() {
    if (_correctionTimer > 0) {
        float t = 1 - (_correctionTimer / 0.25f);
        transform.position = Vector2.Lerp(_correctionStart, _correctionTarget, t);
        _correctionTimer -= Time.deltaTime;
    }
}
```

**Why per-bug seeds work:**
- Bug 2's removal doesn't affect bug 3's RNG (independent seeds)
- Fixed-point eliminates floating point non-determinism
- ID-order updates ensure all clients call RNG in same sequence
- Lerp correction avoids jarring visual pops on resync
- 30-second sample sync catches any remaining drift

### Swarm Center Behavior

The server-simulated swarm center is a **TARGET**, not truth:

- Server moves center freely (ignores terrain collision)
- Bugs bias toward center but respect local collision
- Bugs may pile up against fences trying to reach center
- This is intentional - creates emergent splitting when terrain separates bugs

```
[Swarm Center] ------ bugs bias toward -----> [FENCE] <--- bugs blocked
                                                  |
                                            bugs pile up here
```

When enough bugs drift outside `wander_radius` due to obstacles, a split is triggered.

### BugId Assignment

```
BugId assignment rules:
- IDs are per-swarm, starting from 0 (unique for O(1) lookup)
- Lookup key: (swarm_id, member_id) composite
- First player to activate chunk assigns IDs (0 to Count-1)
- IDs included in snapshot for late joiners
- On deactivation, IDs are discarded
- On reactivation, new IDs assigned (0 to Count-1 again)
```

Server tracks member roster for combat validation:
```go
type SwarmGroup struct {
    // ... existing fields ...
    MemberIDs []int // [0, 1, 2, ...] up to Count-1
    MemberHP  []int // HP per member, indexed by MemberID
}
```

### Drift Detection (Sample-Based)

Full snapshots are expensive (1000 bugs × 12 bytes = 12KB per swarm). Since deterministic RNG keeps players in sync most of the time, we use **sample-based drift detection** to minimize bandwidth:

```
Every 30 seconds per active swarm:

1. Server picks 5-10 random bug IDs from swarm roster
2. Server requests those positions from ONE player
3. Server broadcasts sample: {swarm_id, tick, samples: [{id, x, y}, ...]}
4. Each player compares their local positions for those same IDs
5. If max_distance < 0.5 blocks: do nothing (in sync)
6. If max_distance >= 0.5 blocks: player requests full snapshot
```

**Bandwidth comparison:**
| Scenario | Full Snapshot | Sample Check |
|----------|---------------|--------------|
| 1000 bugs | ~12 KB | ~120 bytes (10 samples) |
| In sync | Wasted 12 KB | 120 bytes, no action |
| Drifted | 12 KB | 120 bytes + 12 KB (only when needed) |

**Why sample-based works:**
- Floating point drift is gradual and affects all bugs similarly
- Random sampling catches drift over multiple 30-second checks
- Threshold (0.5 blocks) allows imperceptible differences
- Hash-based would fail on any tiny difference (useless for our case)

### Sample Comparison Timing

When server broadcasts a sample at tick T, clients may be at different ticks:

- Sample includes the tick number it was captured at
- Client compares against their LOCAL state at that tick
- If client is ahead (at T+5): lookup historical position from buffer
- If client is behind (at T-2): wait until reaching tick T, then compare

**Implementation:** Client stores last ~60 ticks of bug positions for each swarm:

```csharp
// Ring buffer for position history (60 ticks = ~6 seconds at 10 Hz)
private Dictionary<int, Vector2>[] _positionHistory = new Dictionary<int, Vector2>[60];
private int _historyIndex = 0;

void OnSimulationTick(long tick) {
    // Store current positions
    _positionHistory[_historyIndex] = CaptureBugPositions();
    _historyIndex = (_historyIndex + 1) % 60;
}

Vector2? GetPositionAtTick(int bugId, long targetTick) {
    int ticksAgo = (int)(_currentTick - targetTick);
    if (ticksAgo < 0 || ticksAgo >= 60) return null; // Out of range
    int index = (_historyIndex - ticksAgo - 1 + 60) % 60;
    return _positionHistory[index].TryGetValue(bugId, out var pos) ? pos : null;
}
```

**If history unavailable:** Client can skip comparison and request full snapshot to be safe.

### Snapshot Triggers

Full snapshot is only sent when actually needed:

1. **Late joiner enters active chunk** - immediate full snapshot (no local state to compare)
2. **Drift detected via sample check** - player requests full snapshot for that swarm
3. **Manual debug** - /sync command for testing

If the requested player doesn't respond within 2 seconds, server tries another player in the chunk.

### Collision Data Access

Bugs check collision against terrain and occupants via TilemapManager.
**See Section 1.4** for details on the occupant footprint system and why `GetOccupantAt()` correctly handles multi-cell occupants.

```csharp
// BugMovement.cs - collision check
public static bool IsBlocked(Vector2 worldPos) {
    // Check ground tile
    string tileId = TilemapManager.Instance.GetTileAt(worldPos);
    if (tileId != null) {
        var tileEntry = TileDatabase.Instance.GetGroundTileEntry(tileId);
        if (tileEntry != null && tileEntry.blocksBugs) return true;
    }

    // Check occupant (fence, tree, etc.)
    // GetOccupantAt uses _loadedChunks which includes BOTH anchor and footprint cells
    var occupant = TilemapManager.Instance.GetOccupantAt(worldPos);
    if (occupant != null) {
        var entry = TileDatabase.Instance.GetOccupant(occupant.Id);
        if (entry != null && entry.blocksBugs) return true;
    }

    return false;
}
```

**Implementation note:** TileDatabase.cs exists at `Assets/Scripts/World/TileDatabase.cs` but needs `blocksBugs` field added:

```csharp
// Add to GroundTileEntry:
public bool blocksBugs;  // Water, lava, etc.

// Add to OccupantEntry:
public bool blocksBugs;  // Fences, walls, etc.
```

Server-side blocking data comes from existing JSON files:
- `nakama/data/entities/placeables.json` - has `blocks_players` field, add `blocks_bugs`
- Ground tile blocking defined in tile data or hardcoded (water always blocks bugs)

### Sync Flow (Sample Check + On-Demand Snapshot)

**Normal operation (players in sync):**
```
Server: "Player A, send positions for bugs [3, 17, 42, 88, 156]"
Player A: [{3, 10.23, 5.67}, {17, 8.91, 12.34}, ...]  (120 bytes)
Server: Broadcasts sample to all players
Player B: Compares local bugs 3, 17, 42... all within 0.5 blocks. Done.
Player C: Compares local bugs 3, 17, 42... all within 0.5 blocks. Done.
```

**Drift detected:**
```
Player D: Bug 42 is at (15.2, 9.8) locally, sample says (12.1, 8.2)
         Distance = 3.4 blocks > 0.5 threshold
Player D: Sends RequestFullSnapshot to server
Server: Requests full snapshot from Player A, relays to Player D
Player D: Replaces local bug positions with snapshot
```

**Late joiner (no local state):**
```
Player E: Joins chunk, has no bugs spawned yet
Server: Immediately requests full snapshot from Player A
Server: Sends snapshot to Player E
Player E: Spawns bugs at snapshot positions, starts simulating
```

### BugAgent Data Model (All Clients)

```csharp
// TO IMPLEMENT - per-bug state on EVERY client
public class BugAgent {
    public int BugId;              // Unique within swarm (0 to Count-1)
    public string SpeciesId;
    public DeterministicRandom Rng; // Per-bug RNG: seed = hash(worldSeed, swarmId, bugId)

    // Fixed-point for determinism (int32 × 1000)
    public FixedPoint PosX, PosY;
    public FixedPoint VelX, VelY;

    public string BehaviorState;   // wander/chase/flee/idle/attack
    public GameObject Visual;

    // For lerp correction on resync
    private Vector2 _correctionStart, _correctionTarget;
    private float _correctionTimer;

    public Vector2 WorldPosition => new Vector2(PosX.ToFloat(), PosY.ToFloat());
}
```

**No alive/dead flags.** When caught/killed, DELETE from local state.

### SwarmGroup Data Model (Server)

```go
// Server-side swarm state
type SwarmGroup struct {
    SwarmID           string
    SpeciesID         string
    Position          Vec2        // Swarm center
    Count             int         // Number of bugs (server owns this)
    Meters            MeterState  // calm/agitation/panic
    ReproductionState ReproState
    HomeRegion        Bounds
    WanderRadius      float32
    // Note: WorldSeed is global (in WorldState), not per-swarm
    // Bug seeds derived from: hash(WorldSeed, SwarmID, BugID)
}
```

The server simulates swarm center movement, targeting, idle mechanics, and reproduction.

### Movement & Collision (All Clients)

Per simulation tick, EACH client updates its local BugAgents:

1. **Compute intent** (from behavior):
   - `wander`: Brownian motion + bias to swarm center
   - `chase`: Direction toward target player
   - `flee`: Direction away from nearest player

2. **Proposed move**: `p_next = pos + vel * dt`

3. **Collision resolve** against world solids:
   - If blocked: slide along surface OR stop (species-configurable)
   - Never end up inside solid tile

4. **Commit**: `pos = resolved_position`

```csharp
// TO IMPLEMENT - local movement (all clients run this)
public static class BugMovement {
    public static Vector2 ResolveMovement(
        Vector2 currentPos,
        Vector2 velocity,
        float deltaTime,
        TileGrid grid,
        string collisionBehavior
    ) {
        Vector2 proposed = currentPos + velocity * deltaTime;

        if (!grid.IsBlocked(proposed)) {
            return proposed;
        }

        switch (collisionBehavior) {
            case "slide":
                Vector2 slideX = currentPos + new Vector2(velocity.x, 0) * deltaTime;
                if (!grid.IsBlocked(slideX)) return slideX;
                Vector2 slideY = currentPos + new Vector2(0, velocity.y) * deltaTime;
                if (!grid.IsBlocked(slideY)) return slideY;
                return currentPos;

            case "bounce":
                return currentPos - velocity.normalized * 0.1f;

            case "jitter":
            default:
                return currentPos;
        }
    }
}
```

### Collision Determinism Rules

**CRITICAL:** Collision resolution must be identical on all clients. Follow these rules:

1. **Axis order**: Always resolve X before Y (never randomize)
2. **Tile alignment**: Use floor division for tile lookup: `tileX = (int)Math.Floor(posX)`
3. **Rounding**: Use consistent rounding (floor for negative, truncate for positive is NOT okay - pick one)
4. **Fixed-point**: All collision math uses FixedPoint, convert to tile coords deterministically

```csharp
// Deterministic tile lookup from fixed-point position
public static (int tileX, int tileY) GetTileCoords(FixedPoint posX, FixedPoint posY) {
    // Use integer division (floor toward negative infinity)
    int tileX = posX.Value >= 0 ? posX.Value / 1000 : (posX.Value - 999) / 1000;
    int tileY = posY.Value >= 0 ? posY.Value / 1000 : (posY.Value - 999) / 1000;
    return (tileX, tileY);
}

// Collision check order is ALWAYS: X-axis first, then Y-axis
public static FixedPoint2 ResolveCollision(FixedPoint2 current, FixedPoint2 proposed) {
    // 1. Try full move
    if (!IsBlocked(proposed)) return proposed;

    // 2. Try X-only (ALWAYS first)
    var xOnly = new FixedPoint2(proposed.X, current.Y);
    if (!IsBlocked(xOnly)) return xOnly;

    // 3. Try Y-only (ALWAYS second)
    var yOnly = new FixedPoint2(current.X, proposed.Y);
    if (!IsBlocked(yOnly)) return yOnly;

    // 4. No movement possible
    return current;
}
```

**Never use:**
- `Random` for collision tiebreakers
- Platform-specific rounding (`MidpointRounding` varies)
- Floating-point for intermediate collision math

### Chunk Transitions

**Activation (player enters chunk):**
1. Client receives swarm state from server (center, count, meters) via OpCode 20
2. Client spawns N bugs at positions within swarm radius
3. Client starts simulating locally

**Late joiner enters active chunk:**
1. Server requests snapshot from existing player in chunk
2. Server relays snapshot to late joiner
3. Late joiner spawns bugs at received positions
4. Late joiner starts simulating from there

**Deactivation (no players in chunk):**
1. All clients stop simulating that chunk
2. Per-bug state is discarded (not persisted)
3. Server continues swarm-level sim (center, meters)
4. On re-activation: first player spawns fresh bugs from count

### Networking Messages

**New OpCodes:**
```go
// TO IMPLEMENT
const (
    // Sample-based drift detection (lightweight, every 30s)
    OpCodeRequestSample   int64 = 61 // Server → Client: "Send positions for these bug IDs"
    OpCodeSampleResponse  int64 = 62 // Client → Server: Positions for requested bugs
    OpCodeSampleBroadcast int64 = 63 // Server → Clients: Sample for local comparison

    // Full snapshot (only when needed)
    OpCodeRequestSnapshot int64 = 66 // Client → Server: "I'm drifted, send full snapshot"
    OpCodeFullSnapshot    int64 = 67 // Server → Client: Full bug positions for resync
)
```

**Sample request (server picks random bug IDs):**
```go
type SampleRequestMessage struct {
    SwarmID  string `json:"swarm_id"`
    BugIDs   []int  `json:"bug_ids"`  // 5-10 random IDs to sample
}
```

**Sample response (player sends positions for requested IDs):**
```go
type SampleResponseMessage struct {
    SwarmID  string            `json:"swarm_id"`
    Tick     int64             `json:"tick"`
    Samples  []BugPositionData `json:"samples"`  // Only the requested bugs
}
```

**Sample broadcast (server relays to all players for comparison):**
```go
type SampleBroadcastMessage struct {
    SwarmID  string            `json:"swarm_id"`
    Tick     int64             `json:"tick"`
    Samples  []BugPositionData `json:"samples"`  // ~120 bytes for 10 samples
}
// Each player compares local positions, requests full snapshot if drift > 0.5 blocks
```

**Full snapshot request (player detected drift):**
```go
type SnapshotRequestMessage struct {
    SwarmID string `json:"swarm_id"`
}
```

**Full snapshot (only sent on-demand):**
```go
type FullSnapshotMessage struct {
    SwarmID   string            `json:"swarm_id"`
    Tick      int64             `json:"tick"`
    Seed      int64             `json:"seed"`
    Bugs      []BugPositionData `json:"bugs"`  // All bugs in swarm
}

type BugPositionData struct {
    BugID int     `json:"bug_id"`
    X     float32 `json:"x"`
    Y     float32 `json:"y"`
}
```

**SwarmData includes seed for deterministic sim:**
```go
type SwarmData struct {
    ID        string  `json:"id"`
    SpeciesID string  `json:"species_id"`
    X         float32 `json:"x"`
    Y         float32 `json:"y"`
    Radius    float32 `json:"radius"`
    Count     int     `json:"count"`
    Facing    int     `json:"facing"`
    Seed      int64   `json:"seed"`  // For deterministic client simulation
}
```

### Server Changes

**Add to BugSpecies (species.go):**
```go
// TO IMPLEMENT
CollisionBehavior string `json:"collision_behavior"` // "slide", "bounce", "jitter"
IntentType        string `json:"intent_type"`        // "wander", "chase", "flee"
```

**Add snapshot request logic (match.go):**
```go
// TO IMPLEMENT - server requests snapshot from a player
func requestSnapshot(chunkID int, swarmID string) {
    // Pick a player in the chunk
    // Send OpCode 61 request
    // On response, relay to players who need sync
    // If no response in 1-2 seconds, try another player
}
```

### Client Changes

**SwarmVisual.cs:**
- All clients simulate locally (not authority/observer split)
- Handle snapshot request: serialize bug positions when server asks
- Handle sync snapshot: update positions from server relay

### Key Properties

- Bugs NEVER cross solid terrain
- Bugs pile up against fences
- Bugs escape only through gaps
- All clients simulate locally (responsive rendering)
- Server requests snapshots for sync (late joiners, drift correction)
- Combat/catching goes through server (not special authority)

---

## 2.2 Phase 2: Combat & Catching

### Goal
Per-member HP, damage, and catch validation.

### New OpCodes (messages.go)

```go
// TO IMPLEMENT
const (
    OpCodeSwarmSplit       int64 = 50 // C->S: Client reports split
    OpCodeSwarmSplitResult int64 = 51 // S->C: Split result
    OpCodeSwarmMergeResult int64 = 52 // S->C: Merge result
    OpCodeHitBug           int64 = 53 // C->S: Damage member
    OpCodeMemberHPChanged  int64 = 54 // S->C: HP update
    OpCodeCatchAttempt     int64 = 55 // C->S: Catch specific member
    OpCodeCatchResult      int64 = 56 // S->C: Catch success/fail
    OpCodeMeterDelta       int64 = 57 // C->S: Meter influence
    OpCodeSwarmMeterUpdate int64 = 58 // S->C: Meter broadcast
    OpCodeMemberRemoved    int64 = 59 // S->C: Death or catch
    OpCodeRosterChanged    int64 = 60 // S->C: Member roster changed
)
// NOTE: No AgentIntent OpCode needed - intent computed deterministically by client
```

### Message Structs

```go
// TO IMPLEMENT
type HitBugMessage struct {
    SwarmID   string `json:"swarm_id"`
    MemberID  int    `json:"member_id"`
    ToolID    string `json:"tool_id"`  // Server calculates damage from species.DamageTools[tool]
}

type MemberRemovedMessage struct {
    SwarmID       string `json:"swarm_id"`
    MemberID      int    `json:"member_id"`
    Reason        string `json:"reason"`  // "death", "caught"
    NewSwarmCount int    `json:"new_swarm_count"`
    CatcherID     string `json:"catcher_id"`
}

type CatchAttemptMessage struct {
    SwarmID  string `json:"swarm_id"`
    MemberID int    `json:"member_id"`
    ToolID   string `json:"tool_id"`
}

type SwarmSplitMessage struct {
    SwarmID     string  `json:"swarm_id"`
    SplitPos    Vec2    `json:"split_pos"`    // Centroid of separating group
    MemberIDs   []int   `json:"member_ids"`   // Members to split off
}

type SwarmSplitResultMessage struct {
    OriginalID string `json:"original_id"`
    NewSwarmID string `json:"new_swarm_id"`  // "" if rejected
    Accepted   bool   `json:"accepted"`
    Reason     string `json:"reason"`        // "ok", "cooldown", "too_small"
}

type SwarmMergeResultMessage struct {
    SurvivorID   string `json:"survivor_id"`
    AbsorbedID   string `json:"absorbed_id"`
    NewCount     int    `json:"new_count"`
    MergedRoster []int  `json:"merged_roster"`
}

type MemberHPChangedMessage struct {
    SwarmID   string `json:"swarm_id"`
    MemberID  int    `json:"member_id"`
    NewHP     int    `json:"new_hp"`
    MaxHP     int    `json:"max_hp"`
}

type CatchResultMessage struct {
    SwarmID  string `json:"swarm_id"`
    MemberID int    `json:"member_id"`
    Success  bool   `json:"success"`
    Reason   string `json:"reason"`  // "ok", "escaped", "wrong_tool", "not_subdued"
}

type MeterDeltaMessage struct {
    SwarmID string  `json:"swarm_id"`
    Meter   string  `json:"meter"`  // "calm", "agitation", "panic"
    Delta   float32 `json:"delta"`
    ToolID  string  `json:"tool_id"`
}

type SwarmMeterUpdateMessage struct {
    SwarmID    string  `json:"swarm_id"`
    Calm       float32 `json:"calm"`
    Agitation  float32 `json:"agitation"`
    Panic      float32 `json:"panic"`
    MeterState string  `json:"meter_state"`  // derived state
}
```

### Combat Flow (Server-Validated)

**Hitting a bug:**
1. **Client**: Detects hit collision locally (shows VFX for responsiveness)
2. **Client**: Sends HitBug(swarm_id, member_id, tool_id) to SERVER
3. **Server**: Validates member exists, calculates damage from `species.DamageTools[tool_id]`
4. **Server**: Applies damage. If HP <= 0: delete member from roster, broadcast MemberRemoved
5. **All Clients**: On MemberRemoved, delete local BugAgent

**Key:** Server owns HP/roster truth. Server calculates damage (never trust client damage values).

### Catch Flow (Server-Validated)

1. **Client**: Uses net on bug, sends CatchAttempt(swarm_id, member_id, tool_id) to SERVER
2. **Server**: Validates:
   - Member exists in swarm roster
   - Tool is valid for this species
   - Swarm meters/conditions met (if species requires calm/weakened)
3. **Server**: If success: delete member, add to inventory, broadcast MemberRemoved
4. **All Clients**: On MemberRemoved, delete local BugAgent

**Note:** No "authority client" involved. Server validates all combat/catching.

---

## 2.3 Phase 3: Behaviors & Server-Requested Split Detection

### Goal
Implement flee/curious/attract behaviors. Split detection is server-requested (not client-initiated) to avoid race conditions.

### Server Changes

**Add to SwarmState (swarm.go):**
```go
// TO IMPLEMENT
Calm           float32  // Shared meter (0-100)
Agitation      float32
Panic          float32
MeterState     string   // "calm", "neutral", "agitated", "panic"

Behavior       string   // "wander", "flee", "curious", "seek_resource"
BehaviorTimer  float32
TargetPos      *Vec2
LastSplitTick  int64    // For split deduplication
LastSplitCheck int64    // For debouncing split checks
```

**Add to BugSpecies:**
```go
// TO IMPLEMENT
AttractedTo        []string `json:"attracted_to"`
AttractionRadius   float32  `json:"attraction_radius"`
AttractionStrength float32  `json:"attraction_strength"`
```

**Remove from match.go:**
- `checkSwarmSplitting()` - Replace with server-requested split checks

**Add split check request logic (match.go):**
```go
// Server periodically requests split check from ONE player
// Similar to snapshot sync mechanism
func requestSplitCheck(swarmID string, playerID string) {
    // Send OpCode 64: "Check if this swarm should split"
    // Player responds with split report or "no split"
    // If "no split", debounce 5 seconds before asking again
    // If split detected, validate and create new swarm
}
```

**New OpCode for split check:**
```go
const (
    OpCodeRequestSplitCheck int64 = 64 // Server → Client: "Check for split"
    OpCodeSplitCheckResult  int64 = 65 // Client → Server: Split report or "none"
)
```

**Add handler for OpCode 65 (SplitCheckResult):**
- If client reports split: validate min sizes, deduplication, create new swarm
- If client reports "no split": set debounce timer (5 seconds)

### Client Changes

**Add to SwarmVisual.cs:**
```csharp
// TO IMPLEMENT - called when server requests split check (OpCode 64)
private void HandleSplitCheckRequest() {
    int outsideCount = 0;
    Vector2 outsideCentroid = Vector2.zero;
    List<int> outsideMembers = new List<int>();

    foreach (var kvp in _bugs) {  // Dictionary<int, BugAgent>
        int memberId = kvp.Key;
        var bug = kvp.Value;
        // Use wander_radius - bugs outside this have truly separated
        if (Vector2.Distance(bug.Position, _swarmCenter) > _wanderRadius) {
            outsideCount++;
            outsideCentroid += bug.Position;
            outsideMembers.Add(memberId);
        }
    }

    if (outsideCount >= _splitThreshold) {
        outsideCentroid /= outsideCount;
        // Send OpCode 65 with split data
        SendSplitCheckResult(_swarmId, outsideCentroid, outsideMembers);
    } else {
        // Send OpCode 65 with "no split"
        SendSplitCheckResult(_swarmId, null, null);
    }
}
```

**Why server-requested (not client-initiated)?**
- All clients simulate locally, any could detect split
- Client-initiated would cause race conditions (multiple clients reporting)
- Server picks ONE player to ask (like snapshot sync)
- 5 second debounce if no split detected

**Why wander_radius (not swarm_radius)?**
- `swarm_radius` = visual spread, bugs naturally stay within this
- `wander_radius` = max distance from swarm center before considered "separated"
- Bugs blocked by fences/walls drift past wander_radius → triggers split
- This is EMERGENT behavior from collision, not scripted

---

## 2.4 Create species.json

**New file:** `nakama/data/entities/species.json`

```json
{
  "fly": {
    "name": "Common Fly",
    "category": "swarm",
    "collision_behavior": "slide",
    "base_speed": 1.5,
    "wander_radius": 8.0,
    "min_swarm_size": 5,
    "max_swarm_size": 50,
    "swarm_radius": 4.0,
    "merge_radius": 4.0,
    "split_threshold": 8,
    "player_reaction": "flee",
    "reaction_radius": 6.0,
    "flee_speed_mult": 2.0,
    "vision_range": 8.0,
    "attracted_to": ["compost_pile", "rotten_fruit", "bait_basket"],
    "attraction_strength": 0.6,
    "movement_mode": "brownian",
    "intent_range": 1.5,
    "direction_change_rate": 0.3,
    "max_hp": 1,
    "catch_condition": "none",
    "sell_price": 1,
    "sprite_id": "fly"
  },
  "butterfly": {
    "name": "Meadow Butterfly",
    "category": "swarm",
    "collision_behavior": "jitter",
    "base_speed": 1.2,
    "wander_radius": 12.0,
    "min_swarm_size": 2,
    "max_swarm_size": 15,
    "swarm_radius": 5.0,
    "player_reaction": "curious",
    "vision_range": 24.0,
    "attracted_to": ["flower_wild", "flower_red", "flower_blue", "flower_yellow"],
    "attraction_strength": 0.8,
    "movement_mode": "gliding",
    "intent_range": 10.0,
    "direction_change_rate": 0.05,
    "turn_rate": 0.1,
    "max_hp": 2,
    "catch_condition": "calm",
    "condition_threshold": 50,
    "sell_price": 5,
    "sprite_id": "butterfly"
  },
  "giant_scorpion": {
    "name": "Giant Scorpion",
    "category": "swarm",
    "collision_behavior": "slide",
    "intent_type": "chase",
    "base_speed": 0.8,
    "wander_radius": 15.0,
    "min_swarm_size": 1,
    "max_swarm_size": 5,
    "swarm_radius": 3.0,
    "player_reaction": "attack",
    "reaction_radius": 10.0,
    "attack_damage": 15,
    "attack_cooldown": 2.0,
    "max_hp": 120,
    "catch_condition": "weakened",
    "condition_threshold": 30,
    "sell_price": 50,
    "sprite_id": "scorpion"
  }
}
```

**Field Descriptions:**
- `collision_behavior`: How bug handles blocked movement ("slide", "bounce", "jitter")
- `vision_range`: Server-side - how far swarm can "see" resources (blocks)
- `attracted_to`: Server-side - object IDs that attract this species
- `attraction_strength`: Server-side - 0-1, how strongly swarm biases toward resources
- `movement_mode`: Client-side - "brownian" (erratic) or "gliding" (smooth arcs)
- `intent_range`: Client-side - how far ahead bug "looks" when choosing direction (blocks)
- `direction_change_rate`: Client-side - 0-1, chance per tick to pick new direction
- `turn_rate`: Client-side (gliding only) - 0-1, how fast bug turns toward destination

---

## 2.5 Server-Side Swarm AI

### Vision-Based Resource Seeking

Each swarm has a vision range determined by species. Every tick:

1. Server queries nearby occupants within `vision_range`
2. Filter by `species.attracted_to` (flowers for butterflies, compost for flies)
3. If resources found: bias swarm velocity toward closest resource
4. If no resources: continue brownian wander within home radius

### Resource Query

```go
func FindNearbyResources(state *WorldState, pos EntityPosition, visionRange float32, targetIDs []string) []ResourceHit
```

Iterates chunks within vision range, checks occupant layer for matching IDs.

### UpdateWander with Vision

```go
func (s *SwarmState) UpdateWander(deltaTime float32, species *BugSpecies, chunkSize int, resources []ResourceHit) {
    if len(resources) > 0 {
        // Bias toward closest resource
        closest := resources[0]
        dx := closest.X - s.WorldX(chunkSize)
        dy := closest.Y - s.WorldY(chunkSize)
        dist := math.Sqrt(dx*dx + dy*dy)
        attractVel := Vec2{X: dx/dist * species.BaseSpeed, Y: dy/dist * species.BaseSpeed}
        s.Velocity = BlendVelocity(s.Velocity, attractVel, species.AttractionStrength)
    } else {
        // Pure brownian motion (existing logic)
        if rand.Float32() < 0.3 {
            angle := rand.Float32() * 2 * math.Pi
            s.Velocity = Vec2{X: cos(angle) * species.BaseSpeed, Y: sin(angle) * species.BaseSpeed}
        }
    }
    // Apply velocity, normalize, check home bounds...
}
```

### Why This Matters
- Butterfly swarms actively seek flowers across the map
- Fly swarms stay near food sources
- Creates emergent, species-appropriate behavior
- Players can observe swarm movement to find resources

---

## 2.6 Client-Side Movement Behaviors

### Movement Strategy Pattern

Each bug has an `IBugMovement` that determines its local movement:

```csharp
public interface IBugMovement {
    void UpdateMovement(BugAgent bug, FixedPoint2 swarmCenter, FixedPoint wanderRadiusSqr);
}
```

### BrownianMovement (Flies)

- Short intent range (1.5 blocks)
- High direction change rate (30% per tick)
- Picks random direction, not destination
- Results in erratic, buzzy movement
- Strong bias back toward swarm center when outside wander radius

```csharp
public class BrownianMovement : IBugMovement {
    private readonly float _intentRange = 1.5f;
    private readonly float _directionChangeChance = 0.3f;
    private readonly FixedPoint _speed;

    public void UpdateMovement(BugAgent bug, FixedPoint2 swarmCenter, FixedPoint wanderRadiusSqr) {
        if (bug.Rng.NextFloat() < _directionChangeChance) {
            if (bug.Position.SqrDistanceTo(swarmCenter) > wanderRadiusSqr) {
                // Too far - bias back toward center
                BiasTowardCenter(bug, swarmCenter);
            } else {
                // Random direction with short intent range
                float angle = bug.Rng.NextFloat() * 2f * Mathf.PI;
                bug.Velocity = new FixedPoint2 {
                    X = FixedPoint.FromFloat(Mathf.Cos(angle) * _speed.ToFloat()),
                    Y = FixedPoint.FromFloat(Mathf.Sin(angle) * _speed.ToFloat())
                };
            }
        }
    }
}
```

### GlidingMovement (Butterflies)

- Long intent range (10 blocks)
- Low direction change rate (5% per tick)
- Picks destination points far away
- Smooth turning toward destination (`turn_rate: 0.1`)
- Results in graceful arcing paths
- Bias toward swarm center creates sweeping traversals

```csharp
public class GlidingMovement : IBugMovement {
    private readonly float _intentRange = 10.0f;
    private readonly float _directionChangeChance = 0.05f;
    private readonly float _turnRate = 0.1f;
    private readonly FixedPoint _speed;

    private FixedPoint2 _targetPoint;
    private bool _hasTarget;

    public void UpdateMovement(BugAgent bug, FixedPoint2 swarmCenter, FixedPoint wanderRadiusSqr) {
        // Pick new target point when needed
        if (!_hasTarget || bug.Rng.NextFloat() < _directionChangeChance) {
            PickNewTarget(bug, swarmCenter, wanderRadiusSqr);
        }

        // Smooth turn toward target (creates arcs)
        var toTarget = _targetPoint - bug.Position;
        var targetDir = toTarget.Normalized();
        float speedFloat = _speed.ToFloat();
        bug.Velocity = new FixedPoint2 {
            X = FixedPoint.FromFloat(Mathf.Lerp(bug.Velocity.X.ToFloat(),
                targetDir.X.ToFloat() * speedFloat, _turnRate)),
            Y = FixedPoint.FromFloat(Mathf.Lerp(bug.Velocity.Y.ToFloat(),
                targetDir.Y.ToFloat() * speedFloat, _turnRate))
        };
    }
}
```

### MovementFactory

```csharp
public static class MovementFactory {
    public static IBugMovement Create(string speciesId) => speciesId switch {
        "fly" => new BrownianMovement(speed: 1.5f, intentRange: 1.5f, changeRate: 0.3f),
        "butterfly" => new GlidingMovement(speed: 1.2f, intentRange: 10f, changeRate: 0.05f, turnRate: 0.1f),
        _ => new BrownianMovement(speed: 1.0f, intentRange: 2.0f, changeRate: 0.3f)
    };
}
```

---

## 2.7 Files to Create/Modify

### Server (Nakama/Go)

| File | Action | Phase |
|------|--------|-------|
| `nakama/data/entities/species.json` | CREATE - species definitions | 1 |
| `nakama/modules/entities/swarm.go` | MODIFY - add Members map, meters, behavior | 1-3 |
| `nakama/modules/entities/species.go` | MODIFY - add CollisionBehavior, IntentType, AttractedTo | 1 |
| `nakama/modules/world/state.go` | MODIFY - add GlobalSimTick | 1 |
| `nakama/modules/world/messages.go` | MODIFY - add OpCodes 50-67, sample/snapshot/split msgs | 1-2 |
| `nakama/modules/world/match.go` | MODIFY - add snapshot/split request logic, tick sync | 1-2 |
| `nakama/modules/entities/behavior.go` | CREATE - swarm-level behavior (targeting, idle) | 3 |

### Client (Unity/C#)

| File | Action | Phase |
|------|--------|-------|
| `BugMessages.cs` | MODIFY - add sample/snapshot messages, OpCodes 61-67 | 1 |
| `SwarmVisual.cs` | MODIFY - local simulation, sample comparison, snapshot handlers | 1-3 |
| `SwarmManager.cs` | MODIFY - handle OpCodes 50-67, tick sync, drift detection | 1-2 |
| `BugMovement.cs` | CREATE - local collision resolution (all clients run) | 1 |
| `DeterministicRandom.cs` | CREATE - seeded PRNG for deterministic sim | 1 |
| `TileDatabase.cs` | MODIFY - ensure blocks_bugs accessible | 1 |

---

## 2.8 Timing & Broadcast Rates

### Tick Rates

| Rate | Owner | Purpose | Frequency |
|------|-------|---------|-----------|
| **Server Tick** | Server (Nakama) | Swarm-level updates (center, meters) | 10 Hz (100ms) configurable |
| **Client Sim Tick** | All clients | Local per-bug simulation | 10-60 Hz (match server or higher) |
| **SwarmUpdate Broadcast** | Server → Clients | Swarm state sync | Every 3 server ticks (300ms) |
| **Sample Check** | Server → Clients | Drift detection (10 bug samples) | Every 30 seconds per swarm (~120 bytes) |
| **Full Snapshot** | On-demand | Resync drifted players, late joiners | Only when drift > 0.5 blocks detected |

### Server Tick Rate (Swarm-Level)
- **Tick rate:** 10 ticks per second (100ms per tick) - configurable via WorldConfig.TickRate
- **SwarmUpdate broadcast (OpCode 20):** Every 3 ticks (300ms)
- Server simulates: swarm center movement, targeting, idle mechanics, reproduction

### SwarmUpdate Filtering

OpCode 20 is per-player, only includes swarms in subscribed chunks:

```go
// Each player gets a different SwarmUpdateMessage
func broadcastSwarmUpdates(worldState *WorldState) {
    for playerID, player := range worldState.Players {
        visibleSwarms := filterSwarmsByChunks(worldState.Swarms, player.ChunkSubs)
        sendToPlayer(playerID, OpCodeSwarmUpdate, visibleSwarms)
    }
}
```

**Benefits:**
- Reduces bandwidth (only relevant swarms per player)
- Players in different areas don't receive irrelevant swarm data
- Scales with world size

### Client Simulation Rate (Per-Bug)
- **Simulation:** All clients run locally at 10-60 Hz (must be >= server tick rate)
- **Uses server tick counter** for deterministic behavior

### Tick Synchronization

Clients need to know the current server tick for deterministic simulation:

```go
// SwarmUpdateMessage includes global tick
type SwarmUpdateMessage struct {
    Tick   int64      `json:"tick"` // Server's current simulation tick
    Swarms []SwarmData `json:"swarms"`
}
```

```csharp
// Client tracks and uses server tick
public class SwarmManager {
    private long _serverTick;

    void OnSwarmUpdate(SwarmUpdateMessage msg) {
        _serverTick = msg.tick;
        // Advance simulation to match server tick if behind
    }

    // Each swarm uses tick for deterministic RNG advancement
    void SimulateBugs(SwarmVisual swarm) {
        swarm.SimulateToTick(_serverTick);
    }
}
```

**Why tick sync matters:**
- Seeded RNG must advance same number of times on all clients
- Tick counter ensures all clients are "at the same point" in simulation
- Late joiners receive current tick with snapshot

### Sample-Based Drift Detection Rate
- **Sample check:** Every 30 seconds per swarm, server requests 10 bug positions (~120 bytes)
- **Broadcast:** Server relays sample to all players for local comparison
- **Threshold:** 0.5 blocks - anything less is imperceptible drift, ignore it
- **Full snapshot:** Only sent on-demand when player detects drift > threshold
- **Fallback:** If sampled player doesn't respond in 2 seconds, try another

**Why this scales:**
- 100 swarms × 120 bytes = 12 KB total every 30 seconds (vs 1.2 MB with full snapshots)
- Most of the time players are in sync, so no full snapshots needed
- Only drifted players request full sync, not everyone

---

## 2.9 Meter State Thresholds

### Three Meters (0-100 each)
| Meter | Description |
|-------|-------------|
| Calm | Increases with calm spray, decreases near players |
| Agitation | Increases with player proximity, tool swings |
| Panic | Increases when HP lost, swarm members die |

### MeterState Derivation
```
if Panic >= 60:        MeterState = "panic"
else if Agitation >= 50: MeterState = "agitated"
else if Calm >= 70:    MeterState = "calm"
else:                  MeterState = "neutral"
```

### Meter Effects
| State | Behavior | Catch Modifier |
|-------|----------|----------------|
| calm | Slower wander, reduced flee | Catch easier (+20% success) |
| neutral | Normal behavior | Normal catch rate |
| agitated | Faster movement, wider spread | Catch harder (-20% success) |
| panic | Flee at max speed, may split | Cannot catch |

---

## 2.10 Edge Cases

### Chunk Activation Definition

A chunk is "active" based on player subscriptions tracked by the server:

```go
// Server tracks which players see which chunks
ChunkSubs map[string]map[string]bool  // "chunkX,chunkY" -> player IDs

// A chunk is active if it has subscribers
func isChunkActive(chunkKey string) bool {
    return len(worldState.ChunkSubs[chunkKey]) > 0
}
```

- **First subscriber** triggers chunk activation
- **Last unsubscriber** triggers chunk deactivation
- Players subscribe to a 5x5 grid of chunks centered on their position (viewDistanceChunks = 2)

### Chunk Activation (First Player Enters)

When the first player enters an inactive chunk:
1. Server sends current swarm state (center, count, meters) via OpCode 20
2. Player spawns N bugs at random positions within swarm radius
3. Player starts local simulation

**No history needed.** First player creates bugs from count, starts simulating immediately.

### Chunk Deactivation (All Players Leave)

When the last player leaves a chunk:
1. All clients stop simulating that chunk
2. Per-bug positions are discarded (not persisted)
3. Server continues swarm-level sim (center, meters, reproduction)
4. On re-activation: first player spawns fresh bugs from count

**Per-bug state is ephemeral.** Only swarm-level state persists.

### Late Joiner Sync

When a new player enters an already-active chunk:
1. Server requests snapshot from an existing player in chunk
2. Server relays snapshot to late joiner
3. Late joiner spawns bugs at received positions
4. Late joiner starts simulating locally (same as everyone else)

**No replay. No history streaming.** Late joiners become correct via snapshot.

### Player Leaves But Others Remain

When a player leaves a chunk but others are still there:
1. Nothing special happens - other players continue simulating locally
2. Server can request snapshots from any remaining player
3. No "handoff" needed since everyone simulates

**All players simulate.** There's no single "authority" to hand off.

### Below MinSwarmSize

When catching/kills reduce swarm below `min_swarm_size`:
1. Swarm persists in diminished state (no forced despawn)
2. Server sets `MergeSeek = true` - swarm center moves toward nearest same-species
3. If no merge possible within 60 seconds, swarm despawns naturally

### Split Cooldown

- `LastSplitTick` tracked per swarm on server
- Cooldown: 100 ticks (5 seconds)
- Prevents split spam from any client

### Cross-Chunk Swarms

When a swarm's center moves between chunks:

- Swarm is included in player's update if center is in ANY subscribed chunk
- Bugs may physically be in adjacent chunk (within `wander_radius` of center)
- No special handling needed: bugs bias toward center and will follow
- Players see swarm appear/disappear naturally as they subscribe/unsubscribe from chunks

```
Example: Swarm center moves from chunk (0,0) to (1,0)
- Player subscribed to (0,0) only: swarm disappears from their updates
- Player subscribed to (1,0) only: swarm appears in their updates
- Player subscribed to both: continuous visibility
```

---

## 2.11 Architecture Constraints (MANDATORY)

### Architecture Lock

> **BugFarmer uses local simulation with server-requested sync. The server owns swarm-level state (center, count, meters, reproduction). ALL clients simulate per-bug positions locally. Server requests snapshots for late joiners and drift correction. Combat/catching goes through server. Bugs must never phase through barriers.**

### Hard Locks

1. **Two-layer split** - Server owns swarm-level (center, targeting, idle, aggregation); ALL clients simulate per-bug locally
2. **Server always runs** - Swarm center movement, idle mechanics, reproduction happen on server regardless of players
3. **All clients simulate** - Every player in a chunk runs the same tick-based movement code locally
4. **Server requests snapshots** - For late joiners and periodic drift correction, server asks ONE player for positions
5. **Combat goes to server** - All catching/hitting requests go to server for validation (no special authority client)
6. **Bugs respect barriers** - Collision resolved locally on each client, no phasing through walls/fences
7. **Periodic sync only** - No per-bug-per-frame replication. Sync is on-demand, 1-2 second delay acceptable.
8. **Inactive = aggregated** - No per-bug sim in empty chunks (server still runs swarm-level)
9. **Late joiners get snapshots** - No replay, no history streaming
10. **No alive/dead flags** - Members are DELETED on death/catch, not marked

### Intent Types (All Use Same Collision Model)

| Intent Type | Behavior | Examples |
|-------------|----------|----------|
| `wander` | Brownian motion, bias to swarm center | Flies, butterflies |
| `chase` | Move toward nearest player | Scorpions, aggressive bugs |
| `flee` | Move away from nearest player | Scared bugs |

### Anti-Patterns (DO NOT DO)

- Client simulating swarm center movement (server owns this)
- Server simulating per-bug positions (doesn't scale)
- Per-frame position streaming
- Replaying simulation history for late joiners
- Simulating per-bug in inactive chunks
- Allowing bugs to pass through solid blocks
- Using alive/dead flags instead of deletion
- Making one client "authority" that validates combat (server does this)
- Having "observer" clients that only interpolate (everyone simulates)

### Late Joiner Sync

Late joiners become correct via snapshots:
- Late joiner receives: swarm state from server (OpCode 20)
- Late joiner receives: per-bug positions from snapshot (server requests from existing player)
- Late joiner spawns bugs at received positions, starts simulating locally
- **No replay, no history needed** - become correct at next snapshot

---

## 2.12 Swarm Lifecycle

### Swarm Despawn (Count = 0)
When all members are killed or caught:
1. Server: `delete(worldState.Swarms, swarmID)`
2. Next SwarmUpdate doesn't include that swarm
3. Client: Removes SwarmVisual when swarm not in update

### Split Handling

Since server requests split checks from ONE player at a time (Section 2.3):
- No race conditions possible - only one player is ever asked
- If player reports "no split": server debounces 5 seconds before asking again
- If player reports split: server validates min sizes, creates new swarm
- SwarmSplitResult (OpCode 51) confirms to all clients
- **Client behavior:** Do NOT visually split until server confirms (OpCode 51)

This avoids both race conditions and optimistic split rollbacks.

---

## 2.13 Open Questions

- [ ] Should swarms merge across different spawn regions?
- [ ] Minimum distance for resource attraction?
- [ ] Maximum total swarms per zone? (Recommendation: 500 hard cap)
- [ ] Meter decay rates?
