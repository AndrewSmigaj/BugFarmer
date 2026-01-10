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
| `nakama/modules/entities/swarm.go` | SwarmState struct and UpdateWander |
| `nakama/modules/entities/species.go` | BugSpecies struct and LoadSpecies |
| `nakama/modules/entities/types.go` | EntityPosition, Direction, Entity interface |
| `nakama/modules/entities/vec.go` | Vec2 math operations |

### SwarmState (swarm.go:10-26)

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
}

// Methods that exist:
func (s *SwarmState) WorldX(chunkSize int) float32
func (s *SwarmState) WorldY(chunkSize int) float32
func (s *SwarmState) UpdateWander(deltaTime float32, species *BugSpecies, chunkSize int)
```

**Note:** Current SwarmState has `Count` (a single int), NOT a per-member roster. The `CurrentHP` is a single value for the whole swarm, NOT per-member.

### BugSpecies (species.go:11-60)

```go
type BugSpecies struct {
    ID          string `json:"id"`
    Name        string `json:"name"`
    Description string `json:"description"`
    Category    string `json:"category"` // "swarm", "individual", "boss"

    // Movement
    BaseSpeed    float32 `json:"base_speed"`
    WanderRadius float32 `json:"wander_radius"`

    // Swarm-specific
    MinSwarmSize   int     `json:"min_swarm_size"`
    MaxSwarmSize   int     `json:"max_swarm_size"`
    SwarmRadius    float32 `json:"swarm_radius"`
    MergeRadius    float32 `json:"merge_radius"`
    SplitThreshold int     `json:"split_threshold"`
    SplitChance    float32 `json:"split_chance"`

    // Player Reaction (DEFINED but NOT USED)
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

**What does NOT exist in BugSpecies:**
- `MovementMode` (no orbit/agent distinction)
- `OrbitParams`
- `AttractedTo`, `AttractionRadius`, `AttractionStrength`

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
```

**What does NOT exist:** OpCodes 50-59 (split events, hit events, meter events)

### SwarmData Message (messages.go:87-96)

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

**spawnInitialSwarms() (lines 469-499):**
- Hardcoded 5 fly swarms near origin
- Uses defaultFlySpecies() fallback

**checkSwarmMerging() (lines 501-547):**
- Server-side merge check every 50 ticks
- Merges same-species swarms within MergeRadius

**checkSwarmSplitting() (lines 549-597):**
- SERVER-SIDE split based on SplitThreshold and SplitChance
- Uses random chance, NOT fly positions
- **Architecture violation:** Should be client-reported, not server-computed

**handleCatchBug() (lines 619+):**
- Rate limited 200ms between catches
- Validates click within reach
- Trusts client count, no per-member targeting

---

## 1.2 Client-Side (Unity/C#)

### Key Files

| File | Purpose |
|------|---------|
| `SwarmManager.cs` | Singleton, handles OpCode 20/25, creates/destroys SwarmVisuals |
| `SwarmVisual.cs` | Single swarm rendering, fly spawning, position interpolation |
| `FlyBehavior.cs` | Brownian motion for individual flies |
| `BugMessages.cs` | Message structs for OpCodes 20, 24, 25 |
| `CatchingController.cs` | Input handling, catch detection |

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
- Fly spawning uses `Random.insideUnitCircle` (line 113) - NON-DETERMINISTIC
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

### FlyBehavior.cs

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

---

## 1.3 What's Missing (Current Gaps)

- **No `species.json` config file** - `nakama/data/entities/species.json` does not exist
- **No per-member tracking** - Both server and client only track count
- **No deterministic positions** - Client uses `Random`, not hash-based
- **No movement modes** - No orbit/agent distinction
- **No split detection on client** - Server does random splits
- **No OpCodes 50-59** - Split, combat, meter events don't exist
- **No behavior system** - PlayerReaction fields exist but aren't used

---

# PART 2: PLANNED IMPLEMENTATION

Everything in this section is TO BE IMPLEMENTED. Organized by implementation phase.

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

### Deterministic Simulation via Seeded PRNG

To ensure all clients see bugs in the same positions:

1. **Each swarm has a seed** (int64) generated by server on swarm creation
2. **Clients use deterministic RNG** initialized from seed
3. **All random decisions** (direction changes, initial spawn positions) go through seeded RNG
4. **Call order matters** - all clients must make RNG calls in same order per tick

```go
// Server-side: SwarmGroup needs seed
type SwarmGroup struct {
    // ... existing fields ...
    Seed int64 `json:"seed"` // For deterministic client simulation
}

// Generate on swarm creation
func newSwarmSeed() int64 {
    return rand.Int63()
}
```

```csharp
// Client-side: Deterministic RNG per swarm
public class DeterministicRandom {
    private uint state;

    public DeterministicRandom(long seed) {
        state = (uint)(seed ^ (seed >> 32));
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
```

**Drift mitigation:** Even with deterministic RNG, floating point differences can accumulate. Periodic snapshot sync (every 30 seconds) corrects any drift.

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

### Snapshot Triggers

Server requests bug positions from a player when:

1. **Late joiner enters active chunk** - immediate request
2. **Periodic drift correction** - every 30 seconds per chunk
3. **Manual debug** - /sync command for testing

If the requested player doesn't respond within 2 seconds, server tries another player in the chunk.

### Collision Data Access

Bugs check collision against terrain and occupants via TilemapManager:

```csharp
// BugMovement.cs - collision check
public static bool IsBlocked(Vector2 worldPos) {
    // Check ground tile
    string tileId = TilemapManager.Instance.GetTileAt(worldPos);
    if (tileId != null) {
        TileData tile = TileDatabase.Get(tileId);
        if (tile != null && tile.blocks_bugs) return true;
    }

    // Check occupant (fence, tree, etc.)
    var occupant = TilemapManager.Instance.GetOccupantAt(worldPos);
    if (occupant != null && occupant.blocks_bugs) return true;

    return false;
}
```

Tile collision data comes from `tiles.json`:
```json
{
    "water_deep": { "blocks_players": true, "blocks_bugs": true },
    "water_shallow": { "blocks_bugs": true, "movement_mult": 0.5 }
}
```

Occupant collision data comes from `placeables.json` / `occupants.json`:
```json
{
    "fence_wood": { "blocks_players": true, "blocks_bugs": true }
}
```

### Snapshot Sync (For Late Joiners & Drift)

Sync is NOT real-time authority. It's periodic correction:

1. Server periodically requests bug positions from ONE player in chunk
2. If player doesn't respond in ~1-2 seconds, try another player
3. Server relays snapshot to players who need it (late joiners, or periodic resync)
4. A 1-2 second delay is acceptable for sync purposes

```
Server: "Hey Player A, send me bug positions for chunk 5"
Player A: [sends snapshot]
Server: [relays to Player B who just joined, or to all for drift correction]
```

### BugAgent Data Model (All Clients)

```csharp
// TO IMPLEMENT - per-bug state on EVERY client
public class BugAgent {
    public int BugId;           // Unique within session
    public string SpeciesId;
    public Vector2 Pos;         // Current position
    public Vector2 Vel;         // Current velocity
    public string BehaviorState; // wander/chase/flee/idle/attack
    public GameObject Visual;
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
    OpCodeRequestSnapshot int64 = 61 // Server → Client: "Send me bug positions"
    OpCodeBugSnapshot     int64 = 62 // Client → Server: Bug positions response
    OpCodeSyncSnapshot    int64 = 63 // Server → Clients: Relayed positions for sync
)
```

**Server requests snapshot:**
```go
type SnapshotRequestMessage struct {
    ChunkID int `json:"chunk_id"`
    SwarmID string `json:"swarm_id"`
}
```

**Client responds with positions:**
```go
type BugSnapshotMessage struct {
    ChunkID   int               `json:"chunk_id"`
    SwarmID   string            `json:"swarm_id"`
    Tick      int64             `json:"tick"`
    Seed      int64             `json:"seed"`  // For deterministic sim continuation
    Bugs      []BugPositionData `json:"bugs"`
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
    Damage    int    `json:"damage"`
    HitType   string `json:"hit_type"`
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
2. **Client**: Sends HitBug(swarm_id, member_id, damage) to SERVER
3. **Server**: Validates member exists, applies damage
4. **Server**: If HP <= 0: delete member from roster, broadcast MemberRemoved
5. **All Clients**: On MemberRemoved, delete local BugAgent

**Key:** Server owns HP/roster truth. Same as current architecture.

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
    "intent_type": "wander",
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
    "attracted_to": ["compost_pile", "apple_crate", "bait_basket"],
    "attraction_radius": 20.0,
    "max_hp": 1,
    "catch_condition": "none",
    "sell_price": 1,
    "sprite_id": "fly"
  },
  "butterfly": {
    "name": "Meadow Butterfly",
    "category": "swarm",
    "collision_behavior": "jitter",
    "intent_type": "wander",
    "base_speed": 1.0,
    "wander_radius": 12.0,
    "min_swarm_size": 2,
    "max_swarm_size": 15,
    "swarm_radius": 5.0,
    "player_reaction": "curious",
    "attracted_to": ["flower_wild", "flower_red", "flower_blue", "flower_yellow"],
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
- `intent_type`: Base movement pattern ("wander" = around center, "chase" = toward players)

---

## 2.5 Files to Create/Modify

### Server (Nakama/Go)

| File | Action | Phase |
|------|--------|-------|
| `nakama/data/entities/species.json` | CREATE - species definitions | 1 |
| `nakama/modules/entities/swarm.go` | MODIFY - add Members map, meters, behavior | 1-3 |
| `nakama/modules/entities/species.go` | MODIFY - add CollisionBehavior, IntentType, AttractedTo | 1 |
| `nakama/modules/world/state.go` | MODIFY - add GlobalSimTick | 1 |
| `nakama/modules/world/messages.go` | MODIFY - add OpCodes 50-65, snapshot/split check msgs | 1-2 |
| `nakama/modules/world/match.go` | MODIFY - add snapshot/split request logic, tick sync | 1-2 |
| `nakama/modules/entities/behavior.go` | CREATE - swarm-level behavior (targeting, idle) | 3 |

### Client (Unity/C#)

| File | Action | Phase |
|------|--------|-------|
| `BugMessages.cs` | MODIFY - add snapshot messages, OpCodes 61-65 | 1 |
| `SwarmVisual.cs` | MODIFY - local simulation, snapshot/split check handlers | 1-3 |
| `SwarmManager.cs` | MODIFY - handle OpCodes 50-65, tick sync | 1-2 |
| `BugMovement.cs` | CREATE - local collision resolution (all clients run) | 1 |
| `DeterministicRandom.cs` | CREATE - seeded PRNG for deterministic sim | 1 |
| `TileDatabase.cs` | MODIFY - ensure blocks_bugs accessible | 1 |

---

## 2.6 Timing & Broadcast Rates

### Tick Rates

| Rate | Owner | Purpose | Frequency |
|------|-------|---------|-----------|
| **Server Tick** | Server (Nakama) | Swarm-level updates (center, meters) | 10 Hz (100ms) configurable |
| **Client Sim Tick** | All clients | Local per-bug simulation | 10-60 Hz (match server or higher) |
| **SwarmUpdate Broadcast** | Server → Clients | Swarm state sync | Every 3 server ticks (300ms) |
| **Snapshot Sync** | Server requests, client responds | Drift correction, late joiners | Every 30 seconds per chunk, or on late join |

### Server Tick Rate (Swarm-Level)
- **Tick rate:** 10 ticks per second (100ms per tick) - configurable via WorldConfig.TickRate
- **SwarmUpdate broadcast (OpCode 20):** Every 3 ticks (300ms)
- Server simulates: swarm center movement, targeting, idle mechanics, reproduction

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

### Snapshot Sync Rate
- **Server requests:** On-demand (late joiner, or every 30 seconds for drift correction)
- **Acceptable delay:** 1-2 seconds is fine for sync purposes
- **Fallback:** If one player doesn't respond, try another

---

## 2.7 Meter State Thresholds

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

## 2.8 Edge Cases

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

---

## 2.9 Architecture Constraints (MANDATORY)

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

## 2.10 Swarm Lifecycle

### Swarm Despawn (Count = 0)
When all members are killed or caught:
1. Server: `delete(worldState.Swarms, swarmID)`
2. Next SwarmUpdate doesn't include that swarm
3. Client: Removes SwarmVisual when swarm not in update

### Split Conflict Resolution
When multiple clients report splits for same swarm:
1. Server accepts first valid split (deduplication via LastSplitTick)
2. Server rejects subsequent splits within cooldown window
3. **Client behavior:** Do NOT visually split until server confirms (OpCode 51)
4. On rejection: Client does nothing (already waiting for confirmation)

This avoids client needing to "undo" an optimistic split.

---

## 2.11 Open Questions

- [ ] Should swarms merge across different spawn regions?
- [ ] Minimum distance for resource attraction?
- [ ] Maximum total swarms per zone? (Recommendation: 500 hard cap)
- [ ] Meter decay rates?
