# Phase 1 Implementation Plan: Per-Bug Local Simulation + Swarm AI

## Overview

This plan implements the bug system's three-layer architecture with proper player interaction (chase/flee/curious behaviors).

---

## Architecture: Three Layers

### Layer 1: Server-Side Swarm AI (WHERE swarm centers go)
- Server owns swarm CENTER movement
- Server owns swarm LIFECYCLE (phase, meters)
- Vision-based resource seeking based on **current phase** (hungry→food, reproducing→breeding sites)
- **Swarm centers respect obstacles** - bounce/redirect when hitting fences/walls until finding gap
- Server does NOT handle per-bug behavior

### Layer 2: Client-Side Bug Behavior (WHAT each bug does)
- ALL clients simulate per-bug behavior locally (deterministic)
- Each bug independently decides: wander, chase player, or flee from player
- Uses `player_reaction` from species config
- **Deterministic target selection** ensures all clients pick same targets

### Layer 3: Client-Side Movement Style (HOW each bug moves)
- Visual movement pattern: brownian (erratic) vs gliding (smooth arcs)
- Applied on top of behavior (chase with brownian = erratic pursuit)

---

## Swarm Lifecycle System (Server-Side)

### Phases
Each swarm has a lifecycle phase tracked by server:

| Phase | Description | Triggers Transition |
|-------|-------------|---------------------|
| `feeding` | Swarm needs food, attracted to food sources | satiation meter full → `reproducing` |
| `reproducing` | Swarm ready to breed, attracted to breeding sites | reproduction meter full → spawn eggs, reset to `feeding` |
| `idle` | No needs, wanders randomly | satiation drops → `feeding` |

### Lifecycle Meters (Server-Side)

```go
type SwarmState struct {
    // Existing fields...

    // Lifecycle
    Phase              string  `json:"phase"`  // "feeding", "reproducing", "idle"
    Satiation          float32 // 0-100, increases when bugs feed
    ReproductionMeter  float32 // 0-100, increases when bugs visit breeding sites
}
```

### Phase-Based Attractions

Instead of static `attracted_to`, species define attractions PER PHASE:

```json
{
  "fly": {
    "attractions_by_phase": {
      "feeding": ["compost_pile", "rotten_fruit", "bait_basket"],
      "reproducing": ["rotten_fruit", "manure_pile", "breeding_plant"]
    }
  },
  "butterfly": {
    "attractions_by_phase": {
      "feeding": ["flower_wild", "flower_red", "flower_blue", "nectar_feeder"],
      "reproducing": ["breeding_plant", "host_plant"]
    }
  }
}
```

**Note:** Some resources overlap (rotten_fruit = food AND breeding for flies). This is intentional.

### Individual Bug → Server Meter Updates (Aggregated)

Instead of per-interaction events (spammy), use aggregated reporting like snapshots:

```
1. Client tracks interactions locally per swarm
2. Every 3-5 seconds, server requests interaction summary from ONE client
3. Client responds: { swarm_id: { food_count: 12, breed_count: 3 } }
4. Server validates counts (sanity check), updates meters
5. Server broadcasts updated phase if transition occurred
6. Client resets local counters after reporting
```

**OpCodes for interaction sync:**
```go
const (
    OpCodeRequestInteractions int64 = 69  // S→C: "Send interaction counts"
    OpCodeInteractionReport   int64 = 70  // C→S: Aggregated interaction counts
)

type InteractionReportMessage struct {
    Reports []SwarmInteractionReport `json:"reports"`
}

type SwarmInteractionReport struct {
    SwarmID    string `json:"swarm_id"`
    FoodCount  int    `json:"food_count"`   // Number of feeding interactions
    BreedCount int    `json:"breed_count"`  // Number of breeding interactions
}
```

**Client-side tracking:**
```csharp
// In BugAgentManager - track interactions per swarm
Dictionary<string, (int food, int breed)> _interactionCounts = new();

void OnBugReachedResource(string swarmId, string resourceType) {
    if (!_interactionCounts.ContainsKey(swarmId))
        _interactionCounts[swarmId] = (0, 0);

    var counts = _interactionCounts[swarmId];
    if (resourceType == "food") counts.food++;
    else if (resourceType == "breeding") counts.breed++;
    _interactionCounts[swarmId] = counts;
}

// Called when server requests (OpCode 69)
void SendInteractionReport() {
    var reports = _interactionCounts.Select(kvp => new SwarmInteractionReport {
        SwarmID = kvp.Key,
        FoodCount = kvp.Value.food,
        BreedCount = kvp.Value.breed
    }).ToList();

    NetworkManager.Instance.SendInteractionReport(reports);
    _interactionCounts.Clear();  // Reset after reporting
}
```

**Why aggregated is better:**
- ~1 message every 3-5 seconds vs potentially hundreds per second
- Matches snapshot pattern (server picks one client to ask)
- Server can sanity-check totals (reject impossibly high counts)
- Deterministic client simulation means all clients have similar counts

### Server Phase Transitions

```go
func (s *SwarmState) CheckPhaseTransition(species *BugSpecies) {
    switch s.Phase {
    case "feeding":
        if s.Satiation >= 100 {
            s.Phase = "reproducing"
            s.Satiation = 50  // Partial reset
        }
    case "reproducing":
        if s.ReproductionMeter >= 100 {
            // Spawn eggs (existing reproduction logic)
            s.SpawnEggs(species)
            s.Phase = "feeding"
            s.ReproductionMeter = 0
            s.Satiation = 0  // Hungry again after breeding
        }
    case "idle":
        s.Satiation -= 0.1 * deltaTime  // Slowly get hungry
        if s.Satiation <= 20 {
            s.Phase = "feeding"
        }
    }
}
```

### Vision Query Uses Current Phase

```go
func (s *SwarmState) GetCurrentAttractions(species *BugSpecies) []string {
    if attractions, ok := species.AttractionsByPhase[s.Phase]; ok {
        return attractions
    }
    return nil  // No attractions for this phase
}
```

---

## Swarm Center Collision (Server-Side)

Swarm centers are NOT phantoms - they must respect obstacles like fences and walls.

### Design: Raycast on Target Selection

Instead of checking collision every tick (expensive, doesn't scale with fast bugs), we:
1. **Raycast once when picking a new target** - find how far we can go before hitting a block
2. **Move toward pre-validated target** - no collision checks needed per tick
3. **Pick new target when arrived** - or occasionally for variety

This scales well: 500 swarms × ~2 target picks/sec × ~10 cells raycasted = ~10,000 cell checks/sec (trivial)

### SwarmState Fields

```go
type SwarmState struct {
    // ... existing fields

    // Movement target (pre-validated path)
    TargetX   float32 // Destination X (validated to be reachable)
    TargetY   float32 // Destination Y
    HasTarget bool    // Whether we have an active target
}
```

### Species Config

```go
WanderChangeRate float32 `json:"wander_change_rate"` // Chance per tick to change direction
```

- Fly: 0.3 (erratic, changes often)
- Butterfly: 0.05 (smooth, rarely changes)

### Think/Move Split

Swarms don't "think" every tick - they make decisions every few seconds.

**Think() - called every 3-5 seconds:**
```go
func (s *SwarmState) Think(species *BugSpecies, chunkSize int,
    resourceX, resourceY float32, isBlocked BlockedChecker) {

    if hasResource {
        rawTarget = resource position
    } else {
        rawTarget = random direction within vision range
    }
    s.TargetX, s.TargetY = raycastToBlock(curr, rawTarget, isBlocked)
    s.HasTarget = true
}
```

**Move() - called every tick:**
```go
func (s *SwarmState) Move(deltaTime float32, species *BugSpecies, chunkSize int) {
    if !s.HasTarget { stop; return }
    if dist < 0.5 { arrived, clear target, stop; return }
    move toward target at BaseSpeed
}
```

**MatchLoop:**
```go
for _, swarm := range state.Swarms {
    // THINK: Every 3-5 seconds (expensive)
    if tick >= swarm.NextThinkTick {
        hits := FindNearbyResources(...)
        swarm.Think(species, chunkSize, resourceX, resourceY, isBlocked)
        swarm.NextThinkTick = tick + 30 + rand.Int63n(21)
    }

    // MOVE: Every tick (cheap)
    swarm.Move(deltaTime, species, chunkSize)
}
```

### Raycast Function

```go
func raycastToBlock(startX, startY, endX, endY float32, isBlocked BlockedChecker) (float32, float32) {
    // Step through line in 0.5-block increments
    // Return position just before first blocked cell
    // If path is clear, return end position
}
```

### Why This Is Better

- **Scales with speed**: Fast bugs work fine, no step-size limits
- **Efficient**: O(distance) work only when picking target, not every tick
- **Simple**: Pick target → raycast → move. No complex per-tick collision
- **Natural behavior**: Swarm heads toward goal until blocked, then picks new direction
```

### Server Needs Blocking Data

Server must know which tiles/occupants block swarm movement:

```go
// In WorldState or helper
func (w *WorldState) IsBlocked(x, y float32) bool {
    chunkX, chunkY := int(x) / w.ChunkSize, int(y) / w.ChunkSize
    chunk := w.GetChunk(chunkX, chunkY)
    if chunk == nil { return true }  // Out of bounds = blocked

    localX, localY := int(x) % w.ChunkSize, int(y) % w.ChunkSize

    // Check occupant layer (fences, walls, trees)
    occupant := chunk.Occupants[localY][localX]
    if occupant != "" {
        entry := w.PlaceableData[occupant]
        if entry != nil && entry.BlocksBugs {
            return true
        }
    }

    // Check ground tile (water, lava)
    ground := chunk.Ground[localY][localX]
    if ground == "water" || ground == "lava" {
        return true
    }

    return false
}
```

### Why This Matters

- Swarms can't teleport through fences to reach flowers
- Creates strategic gameplay: players can corral swarms with fences
- Swarm must find gaps in barriers (emergent pathfinding)
- Matches individual bug collision (both respect same obstacles)

### Verification

21. **Swarm center stops at fence** - doesn't phase through
22. **Swarm bounces and finds gap** - redirects around obstacle
23. **Fully enclosed swarm stays trapped** - can't escape fenced area

---

## Player Targeting: Deterministic Design

### Existing Player Sync System
- **EntityUpdate (OpCode 11)** broadcasts all player positions every 100ms
- **EntityManager** stores remote players: `Dictionary<string, RemoteEntity>`
- All clients have identical player position data

### Per-Bug Target Selection (All Clients Compute Identically)

```csharp
// In BugAgent.UpdateBehavior()
string PickTarget(BugAgent bug, float reactionRadius) {
    // Get all players from EntityManager (same data on all clients)
    var players = EntityManager.Instance.GetAllPlayers();

    // Find players within THIS bug's reaction radius
    var inRange = new List<(string id, float dist)>();
    foreach (var player in players) {
        float dist = FixedPointDistance(bug.Position, player.Position);
        if (dist <= reactionRadius) {
            inRange.Add((player.Id, dist));
        }
    }

    if (inRange.Count == 0) return null;  // No target → wander

    // Sort by distance, then by player ID (deterministic tie-breaker)
    inRange.Sort((a, b) => {
        int cmp = a.dist.CompareTo(b.dist);
        if (cmp != 0) return cmp;
        return string.Compare(a.id, b.id, StringComparison.Ordinal);
    });

    return inRange[0].id;  // All clients pick same player
}
```

### Why This Is Deterministic
1. All clients receive same player positions (EntityUpdate sync)
2. All clients have same bug positions (deterministic simulation)
3. Distance uses FixedPoint math (no float divergence)
4. Tie-breaker uses player ID string comparison (same everywhere)

### Behavior Flow Per Tick

```
1. Get player positions (EntityManager.GetAllPlayers() + local PlayerController)
2. For each bug:
   a. Check if any player within reaction_radius
   b. If player_reaction == "attack" and player in range → chase nearest
   c. If player_reaction == "flee" and player in range → flee from nearest
   d. If player_reaction == "curious" and player in range → slowly drift toward nearest
   e. Otherwise → wander around swarm center
3. Apply movement_mode to chosen behavior (brownian/gliding style)
4. Resolve collision
```

### Client Needs Player List (Including Local Player)

EntityManager only has remote players. For targeting, we need ALL players:

```csharp
// In BugAgentManager or helper
List<PlayerPosition> GetAllPlayerPositions() {
    var result = new List<PlayerPosition>();

    // Add local player
    var local = PlayerController.Instance;
    if (local != null) {
        result.Add(new PlayerPosition(local.UserId, local.transform.position));
    }

    // Add remote players from EntityManager
    foreach (var remote in EntityManager.Instance.GetAllEntities()) {
        if (remote.EntityType == "player") {
            result.Add(new PlayerPosition(remote.EntityId, remote.transform.position));
        }
    }

    return result;
}
```

### Client Needs Species Config

Client needs `player_reaction`, `reaction_radius`, `movement_mode` per species.

**Options:**
1. **Hardcode in MovementFactory** (simplest for Phase 1)
2. **Load species.json on client** (more flexible)
3. **Server sends in SwarmUpdate** (dynamic)

**Phase 1: Hardcode in MovementFactory** - matches server species.json values.

---

## Step 0: Update bugs_new.md

**Already added:**
- Two-layer architecture section
- Updated species.json with vision_range, movement_mode, intent_range
- Server-side swarm AI section
- Client-side movement behaviors section

**Still needs to be added:**
- Swarm lifecycle system (phases, meters, phase transitions)
- Phase-based attractions (`attractions_by_phase` instead of static `attracted_to`)
- Swarm center collision (bouncing off obstacles)
- Aggregated interaction reporting (OpCodes 69-70)
- Player_reaction behavior documentation (chase/flee/curious)

---

## Implementation Steps

### PART A: Server-Side Swarm AI

#### Step 1: Add Vision + Lifecycle Fields to BugSpecies
**File:** `nakama/modules/entities/species.go`

```go
// Vision-based resource seeking
VisionRange          float32             `json:"vision_range"`
AttractionsByPhase   map[string][]string `json:"attractions_by_phase"`  // phase → resource IDs
AttractionStrength   float32             `json:"attraction_strength"`

// Lifecycle parameters
FeedAmount           float32 `json:"feed_amount"`           // Satiation per feeding event
BreedAmount          float32 `json:"breed_amount"`          // Reproduction progress per breeding event
SatiationDecayRate   float32 `json:"satiation_decay_rate"`  // Per second in idle
```

#### Step 1b: Add Lifecycle Fields to SwarmState
**File:** `nakama/modules/entities/swarm.go`

```go
// Lifecycle (server-owned)
Phase              string  `json:"phase"`  // "feeding", "reproducing", "idle"
Satiation          float32 // 0-100
ReproductionMeter  float32 // 0-100
```

#### Step 2: Update species.json with Lifecycle Data
**File:** `nakama/data/species.json`

Add vision_range, attractions_by_phase, lifecycle parameters for fly and butterfly:

```json
{
  "fly": {
    "vision_range": 8.0,
    "attraction_strength": 0.6,
    "attractions_by_phase": {
      "feeding": ["compost_pile", "rotten_fruit", "bait_basket"],
      "reproducing": ["rotten_fruit", "manure_pile"]
    },
    "feed_amount": 5.0,
    "breed_amount": 10.0,
    "satiation_decay_rate": 0.5
  }
}
```

#### Step 3: Create Resource Query Helper
**File:** `nakama/modules/world/resource_query.go` (NEW)

```go
func FindNearbyResources(state *WorldState, pos EntityPosition, visionRange float32, targetIDs []string) []ResourceHit
```

#### Step 4: Modify UpdateWander for Vision + Lifecycle + Collision
**File:** `nakama/modules/entities/swarm.go`

- Add resources parameter, bias toward closest when found
- Use `swarm.Phase` to get current attractions from species
- Add `CheckPhaseTransition()` method
- **Add collision check for swarm center** - bounce off obstacles

```go
func (s *SwarmState) UpdateWander(deltaTime float32, species *BugSpecies, worldState *WorldState, resources []ResourceHit) {
    // Get attractions for current phase
    attractions := species.AttractionsByPhase[s.Phase]

    // Calculate desired velocity (toward resource or random)
    desiredVel := s.calculateDesiredVelocity(species, attractions, resources)

    // Proposed new position
    proposedX := s.Position.X + desiredVel.X * deltaTime
    proposedY := s.Position.Y + desiredVel.Y * deltaTime

    // Check collision - swarm centers can't phase through obstacles
    if !worldState.IsBlocked(proposedX, proposedY) {
        s.Position.X = proposedX
        s.Position.Y = proposedY
        s.Velocity = desiredVel
    } else {
        // Blocked - try random directions until finding gap
        s.handleCenterCollision(deltaTime, worldState, species)
    }
}
```

#### Step 4b: Add IsBlocked Helper
**File:** `nakama/modules/world/state.go`

```go
func (w *WorldState) IsBlocked(x, y float32) bool {
    // Check occupants (fences, walls) and ground (water)
    // Uses PlaceableData to check BlocksBugs flag
}
```

#### Step 5: Add Aggregated Interaction Handler
**File:** `nakama/modules/world/match.go`

Every 3-5 seconds, request interaction report from one client, then process:

```go
// In match loop - every 3-5 seconds
func (m *MatchHandler) requestInteractionReport() {
    // Pick one player per active chunk (like snapshot)
    for chunkKey, players := range m.worldState.ChunkSubs {
        if len(players) == 0 { continue }
        playerID := pickOne(players)
        m.sendToPlayer(playerID, OpCodeRequestInteractions, nil)
    }
}

// Handle OpCode 70 (InteractionReport)
func (m *MatchHandler) handleInteractionReport(msg *InteractionReportMessage, sender string) {
    for _, report := range msg.Reports {
        swarm := m.worldState.Swarms[report.SwarmID]
        if swarm == nil { continue }

        species := m.species[swarm.SpeciesID]

        // Sanity check - cap at reasonable max per report period
        foodCount := min(report.FoodCount, 50)
        breedCount := min(report.BreedCount, 50)

        if swarm.Phase == "feeding" {
            swarm.Satiation += float32(foodCount) * species.FeedAmount
        }
        if swarm.Phase == "reproducing" {
            swarm.ReproductionMeter += float32(breedCount) * species.BreedAmount
        }

        swarm.CheckPhaseTransition(species)
    }
}
```

#### Step 6: Wire Up in MatchLoop
**File:** `nakama/modules/world/match.go`

- Call FindNearbyResources before UpdateWander
- Register OpCode 69-70 handlers
- Pass WorldState to UpdateWander for collision checking

**Also update SwarmData in messages.go:**
```go
type SwarmData struct {
    ID        string  `json:"id"`
    SpeciesID string  `json:"species_id"`
    X         float32 `json:"x"`
    Y         float32 `json:"y"`
    Radius    float32 `json:"radius"`
    Count     int     `json:"count"`
    Facing    int     `json:"facing"`
    Phase     string  `json:"phase"`  // NEW: "feeding", "reproducing", "idle"
}
```

#### Step 7: Send WorldInit on Player Join
**File:** `nakama/modules/world/match.go`

Send OpCode 68 with WorldSeed and Tick when player joins match:

```go
const OpCodeWorldInit int64 = 68

type WorldInitMessage struct {
    WorldSeed int64 `json:"world_seed"`  // For deterministic bug RNG
    Tick      int64 `json:"tick"`        // Current simulation tick
}

// In MatchJoin handler
func (m *MatchHandler) onPlayerJoin(presence runtime.Presence) {
    // Send WorldInit so client can start deterministic simulation
    m.sendToPlayer(presence.GetUserId(), OpCodeWorldInit, WorldInitMessage{
        WorldSeed: m.worldState.WorldSeed,
        Tick:      m.worldState.GlobalTick,
    })
}
```

---

### PART B: Client-Side Bug Movement

#### Step 8: Update IBugMovement Interface
**File:** `BugFarmerClient/Assets/Scripts/Bugs/IBugMovement.cs`

Add methods for chase/flee/curious:
```csharp
public interface IBugMovement {
    void UpdateMovement(BugAgent bug, FixedPoint2 swarmCenter, FixedPoint wanderRadiusSqr);
    void MoveToward(BugAgent bug, FixedPoint2 target);      // For chase (full speed)
    void MoveTowardSlow(BugAgent bug, FixedPoint2 target);  // For curious (gentle drift)
    void MoveAwayFrom(BugAgent bug, FixedPoint2 target);    // For flee
}
```

#### Step 9: BrownianMovement.cs
**File:** `BugFarmerClient/Assets/Scripts/Bugs/BrownianMovement.cs`

Flies: intentRange 1.5, changeRate 0.3, erratic buzzing.
- `MoveToward`: erratic pursuit (zig-zag toward target)
- `MoveAwayFrom`: erratic scatter (zig-zag away from target)

#### Step 10: GlidingMovement.cs
**File:** `BugFarmerClient/Assets/Scripts/Bugs/GlidingMovement.cs`

Butterflies: intentRange 10, changeRate 0.05, turnRate 0.1, smooth arcs.
- `MoveToward`: smooth arc toward target
- `MoveAwayFrom`: smooth arc away from target

#### Step 11: MovementFactory.cs + SpeciesConfig
**File:** `BugFarmerClient/Assets/Scripts/Bugs/MovementFactory.cs`

Create movement by species ID AND provide species behavior config:

```csharp
public static class SpeciesConfig {
    public static (IBugMovement movement, string playerReaction, float reactionRadius)
    GetConfig(string speciesId) => speciesId switch {
        "fly" => (
            new BrownianMovement(1.5f, 1.5f, 0.3f),
            "flee",
            6.0f
        ),
        "butterfly" => (
            new GlidingMovement(1.2f, 10f, 0.05f, 0.1f),
            "curious",
            8.0f
        ),
        "scorpion" => (
            new BrownianMovement(0.8f, 2.0f, 0.2f),  // Slower, more deliberate
            "attack",
            10.0f
        ),
        _ => (new BrownianMovement(1.0f, 2.0f, 0.3f), "ignore", 0f)
    };
}
```

#### Step 12: BugAgent.cs
**File:** `BugFarmerClient/Assets/Scripts/Bugs/BugAgent.cs`

Per-bug entity with:
- Deterministic RNG (seeded per-bug)
- Fixed-point position/velocity
- Movement strategy (IBugMovement)
- **Behavior state**: wander, chase, flee
- **Target selection**: deterministic player targeting (see architecture section above)

```csharp
public class BugAgent {
    public int BugId;
    public string SwarmId, SpeciesId;
    public DeterministicRandom Rng;
    public FixedPoint2 Position, Velocity;
    public IBugMovement Movement;

    // Behavior
    public string CurrentBehavior;  // "wander", "chase", "flee"
    public string TargetPlayerId;   // null if wandering

    public void SimulateTick(FixedPoint2 swarmCenter, FixedPoint wanderRadiusSqr,
                             string playerReaction, float reactionRadius) {
        // 1. Determine behavior based on nearby players
        UpdateBehavior(playerReaction, reactionRadius);

        // 2. Apply movement based on behavior
        switch (CurrentBehavior) {
            case "chase":
                if (TargetPlayerId != null) {
                    var chasePos = GetPlayerPosition(TargetPlayerId);
                    Movement.MoveToward(this, chasePos);
                }
                break;

            case "flee":
                if (TargetPlayerId != null) {
                    var fleePos = GetPlayerPosition(TargetPlayerId);
                    Movement.MoveAwayFrom(this, fleePos);
                }
                break;

            case "curious":
                if (TargetPlayerId != null) {
                    var curiousPos = GetPlayerPosition(TargetPlayerId);
                    Movement.MoveTowardSlow(this, curiousPos);  // Gentle drift
                }
                break;

            default:  // "wander" or "ignore"
                Movement.UpdateMovement(this, swarmCenter, wanderRadiusSqr);
                break;
        }

        // 3. Resolve collision
        Position = BugCollision.Resolve(Position, Position + Velocity * deltaTime);
    }
}
```

#### Step 13: TilemapManager.GetGroundAt()
**File:** `BugFarmerClient/Assets/Scripts/World/TilemapManager.cs`

Query ground tile for collision (water blocks bugs).

#### Step 14: BugCollision.cs
**File:** `BugFarmerClient/Assets/Scripts/Bugs/BugCollision.cs`

Deterministic collision: X-axis first, check ground + occupants.

#### Step 15: BugAgentManager.cs
**File:** `BugFarmerClient/Assets/Scripts/Bugs/BugAgentManager.cs`

Singleton managing all bugs:
- Receives WorldSeed from OpCode 68
- Simulates all bugs in ID order (deterministic)
- Queries EntityManager for player positions (for behavior targeting)

#### Step 16: BugMessages.cs
**File:** `BugFarmerClient/Assets/Scripts/Networking/BugMessages.cs`

Add WorldInitMessage for OpCode 68.

#### Step 17: Bug-Resource Interaction (Client-Side Aggregation)
**File:** `BugFarmerClient/Assets/Scripts/Bugs/BugAgentManager.cs`

Track interactions locally, report when server requests:

```csharp
// Track interactions per swarm (aggregated)
private Dictionary<string, (int food, int breed)> _interactionCounts = new();

// Called by BugAgent when it reaches a resource
public void RecordInteraction(string swarmId, string resourceType) {
    if (!_interactionCounts.ContainsKey(swarmId))
        _interactionCounts[swarmId] = (0, 0);

    var counts = _interactionCounts[swarmId];
    if (resourceType == "food") counts.food++;
    else if (resourceType == "breeding") counts.breed++;
    _interactionCounts[swarmId] = counts;
}

// Called when server requests (OpCode 69)
void OnInteractionRequest() {
    var reports = _interactionCounts
        .Where(kvp => kvp.Value.food > 0 || kvp.Value.breed > 0)
        .Select(kvp => new SwarmInteractionReport {
            SwarmID = kvp.Key,
            FoodCount = kvp.Value.food,
            BreedCount = kvp.Value.breed
        }).ToList();

    if (reports.Count > 0) {
        NetworkManager.Instance.SendInteractionReport(reports);
    }
    _interactionCounts.Clear();  // Reset after reporting
}
```

**BugAgent calls BugAgentManager:**
```csharp
// In BugAgent.SimulateTick()
void CheckResourceInteraction() {
    if (_interactCooldown > 0) return;

    var occupant = TilemapManager.Instance.GetOccupantAt(WorldPosition);
    if (occupant == null) return;

    string resourceType = GetResourceType(occupant.Id, _swarmPhase);
    if (resourceType != null) {
        BugAgentManager.Instance.RecordInteraction(_swarmId, resourceType);
        _interactCooldown = 1.0f;  // Per-bug cooldown
    }
}
```

**Note:** Client needs swarm phase in SwarmUpdate (OpCode 20) to determine valid resources.

#### Step 18: Integration
- SwarmVisual delegates to BugAgentManager
- CatchingController queries BugAgentManager
- BugAgentManager queries EntityManager for player positions
- SwarmUpdate includes `phase` for resource interaction decisions

---

## Files Summary

| File | Action | Step |
|------|--------|------|
| `tools/LLM Guides/bugs_new.md` | UPDATE - add lifecycle docs | 0 |
| `nakama/modules/entities/species.go` | Add vision + lifecycle fields | 1 |
| `nakama/modules/entities/swarm.go` | Add Phase, Satiation, ReproductionMeter fields | 1b |
| `nakama/data/species.json` | Add attractions_by_phase, lifecycle params | 2 |
| `nakama/modules/world/resource_query.go` | CREATE | 3 |
| `nakama/modules/entities/swarm.go` | Modify UpdateWander for vision + collision | 4 |
| `nakama/modules/world/state.go` | Add IsBlocked helper for swarm collision | 4b |
| `nakama/modules/world/match.go` | Add interaction request + OpCode 70 handler | 5 |
| `nakama/modules/world/match.go` | Wire up resources, send WorldInit | 6 |
| `nakama/modules/world/messages.go` | Add OpCodes 68-70, InteractionReport, SwarmData.Phase | 5-6 |
| `Assets/Scripts/Bugs/IBugMovement.cs` | Add MoveToward/MoveAwayFrom | 8 |
| `Assets/Scripts/Bugs/BrownianMovement.cs` | CREATE | 9 |
| `Assets/Scripts/Bugs/GlidingMovement.cs` | CREATE | 10 |
| `Assets/Scripts/Bugs/MovementFactory.cs` | CREATE | 11 |
| `Assets/Scripts/Bugs/BugAgent.cs` | CREATE (with behavior + resource interaction) | 12, 17 |
| `Assets/Scripts/World/TilemapManager.cs` | Add GetGroundAt() | 13 |
| `Assets/Scripts/Bugs/BugCollision.cs` | CREATE | 14 |
| `Assets/Scripts/Bugs/BugAgentManager.cs` | CREATE | 15 |
| `Assets/Scripts/Networking/BugMessages.cs` | Add WorldInitMessage, BugInteractMessage | 16 |
| `Assets/Scripts/Entities/SwarmVisual.cs` | Delegate to BugAgentManager | 18 |

---

## Verification

### Swarm Center Movement (Server)
1. **Butterfly swarm moves to flowers** - server vision finds flowers, moves center
2. **Fly swarm stays near compost** - short vision, stays local
3. **Hungry swarm seeks food** - swarm in "feeding" phase moves toward food resources
4. **Fed swarm seeks breeding sites** - after feeding, phase changes to "reproducing"

### Swarm Lifecycle (Server)
5. **Satiation increases when bugs feed** - client sends BugInteract, server updates meter
6. **Phase transitions correctly** - satiation full → reproducing phase
7. **Eggs spawn after reproduction** - reproduction meter full → eggs appear

### Individual Bug Movement (Client)
8. **Individual butterflies glide** - smooth arcs
9. **Individual flies buzz** - erratic brownian movement
10. **Bugs pile up at fences** - collision works

### Player Interaction (Behavior)
11. **Scorpions chase nearest player** - each bug picks target, pursues
12. **Flies scatter from player** - flee behavior disperses swarm
13. **Two players, bugs split targets** - some chase A, some chase B (deterministic)
14. **All clients see same behavior** - deterministic target selection

### Bug-Resource Interaction (Aggregated)
15. **Interactions aggregated locally** - Client counts food/breed per swarm
16. **Server requests report every 3-5s** - OpCode 69 triggers client response
17. **Server receives aggregated counts** - OpCode 70 with totals per swarm
18. **Swarm phase visible to client** - SwarmUpdate includes phase field

### Sync
19. **Two clients see same positions** - deterministic RNG
20. **Late joiner sees bugs** - WorldInit provides seed

---

## Late Joiner Sync (Already Designed)

Per bugs_new.md, the snapshot system handles late joiners:

1. Late joiner enters active chunk
2. Server requests snapshot from existing player (OpCode 66)
3. Existing player sends FullSnapshotMessage with all bug positions (OpCode 67)
4. Server relays to late joiner
5. Late joiner spawns bugs at received positions, starts simulating

**OpCodes 66-67 message structs already exist in messages.go.** Implementation needed in Phase 1.

---

## Deferred to Phase 2

- Sample-based drift detection (OpCodes 61-63) - periodic sync check
- Per-bug HP and combat (HitBug, MemberRemoved OpCodes)
- Split detection (server-requested via OpCodes 64-65)
- Bug-to-bug combat
- Detailed nectar collection mechanics (visual effects, per-flower tracking)
