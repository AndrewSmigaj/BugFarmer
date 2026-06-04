# Bug & Swarm Entity System

## Overview

This architecture describes the unified entity system for all bugs in BugFarmer. The system handles two distinct entity patterns:

1. **Swarms**: Aggregate units (flies, ants, eggs) - count-based, server simulates swarm center
2. **Individual Bugs**: Single entities (millipedes) - unique movement patterns (Bezier curves)

Both types share networking infrastructure but have different simulation and rendering approaches.

---

## Problem Statement

### Bandwidth Analysis (10,000 bugs, 10 users)

Total server egress = Entities × Updates/sec × Bytes × Users

| Approach | Entities/Update | Updates/sec | Bytes/Entity | Server Egress |
|----------|-----------------|-------------|--------------|---------------|
| Naive (all bugs) | 10,000 | 10 | 75 | **75 MB/sec** |
| Distance culling | ~2,000 visible | 10 | 75 | **15 MB/sec** |
| Aggressive culling | ~500 near | 10 | 75 | **3.75 MB/sec** |
| **Swarm heuristic** | ~200 swarms | 10 | 50 | **1 MB/sec** |

**Conclusion**: Swarm-based approach reduces bandwidth by ~75x while maintaining visual density.

---

## Design Principles

1. **Swarms are the networked unit** - Server simulates swarm center, not individual bugs
2. **Client renders individuals** - Each client spawns local flies within swarm bounds
3. **Brownian motion preserved** - Flies buzz naturally (client-side)
4. **Server authority** - Positions, counts, reproduction are server-controlled
5. **Click-to-catch** - Players click directly on bug sprites; server validates and broadcasts
6. **Data-driven species** - Species definitions loaded from config, extensible
7. **Merge priority** - Swarms prefer to merge over splitting to minimize entity count

---

## Client vs Server Responsibilities

### Server (Authoritative)

The server owns all game state and validates all actions:

- **Swarm state**: Position (center point), count, facing
- **Condition meters**: Current condition value (calm, stun, distract), HP for combat bugs
- **Hostile/alerted state**: Which swarms are reacting to players
- **Catching validation**: Verifies net size, condition thresholds met, range
- **Reproduction logic**: When swarms breed, egg hatching
- **Merge/split decisions**: When swarms combine or separate
- **Inventory**: What bugs each player has caught

### Client (Visual Only)

The client handles rendering and sends inputs to server:

- **Individual fly positions**: Brownian motion within swarm bounds (purely visual)
- **Fly sprite animation**: Wing flapping, direction facing
- **Swarm visual interpolation**: Smooth movement between server updates
- **Click detection**: Detects clicks on individual fly sprites
- **Net size validation**: Early reject if wrong net (server still validates)
- **UI feedback**: "Too Big!", "Not Ready!", catch animations, condition meter display

### Key Insight

Individual flies **do not exist on the server**. The server only knows:
- Swarm center position
- Swarm count
- Species ID

Each client independently spawns and manages its own fly GameObjects within the swarm's visual bounds. This is what makes the swarm system bandwidth-efficient.

---

## Entity Type Taxonomy

| Category | Examples | Networking | Movement | Count |
|----------|----------|------------|----------|-------|
| **Swarm** | Flies, ants, bees | Swarm center + count | Brownian wander | 1-100+ |
| **EggCluster** | Fly eggs, ant eggs | Cluster pos + count | Stationary | 1-50 |
| **Individual** | Millipede, beetle | Full entity position | Bezier/custom | 1 |
| **Plant** | Breeding plants | Block position | Stationary | 1 |

---

## Swarm Management

### Merging (Priority)

Swarms actively seek to merge to keep entity counts low. Merge radius and max size are per-species in config:

```go
// Called every 50 ticks (5 seconds) to limit O(n^2) performance impact
// NOTE: For >500 swarms, consider spatial hashing optimization
// NOTE: Collect IDs first, then delete - don't modify map during iteration
func (m *Match) checkSwarmMerging(state *WorldState) {
    merged := make(map[string]bool)
    toDelete := []string{}

    for id1, swarm1 := range state.Swarms {
        if merged[id1] { continue }
        species1 := state.Species[swarm1.SpeciesID]

        for id2, swarm2 := range state.Swarms {
            if id1 == id2 || merged[id2] { continue }
            if swarm1.SpeciesID != swarm2.SpeciesID { continue }

            // Use species-specific merge radius
            if distBetween(swarm1.Position, swarm2.Position) <= species1.MergeRadius {
                combined := swarm1.Count + swarm2.Count
                // Use species-specific max swarm size
                if combined <= species1.MaxSwarmSize {
                    // Merge swarm2 into swarm1
                    swarm1.Count = combined
                    merged[id2] = true
                    toDelete = append(toDelete, id2)
                }
            }
        }
    }

    // Delete after iteration complete
    for _, id := range toDelete {
        delete(state.Swarms, id)
    }
}
```

### Splitting (Random/Occasional)

Splitting only happens randomly to prevent runaway fragmentation. Split threshold and chance are per-species in config:

```go
// Low probability split for very large swarms
// NOTE: Collect new swarms first, add after iteration
func (m *Match) checkSwarmSplitting(state *WorldState) {
    newSwarms := []*SwarmState{}

    for _, swarm := range state.Swarms {
        species := state.Species[swarm.SpeciesID]

        // Use species-specific split threshold and chance
        if swarm.Count > species.SplitThreshold && rand.Float32() < species.SplitChance {
            // Split roughly in half
            splitCount := swarm.Count / 2 + rand.Intn(10) - 5
            swarm.Count -= splitCount

            // New swarm nearby
            newSwarm := &SwarmState{
                ID:        fmt.Sprintf("swarm_%s", uuid.NewString()[:8]),
                SpeciesID: swarm.SpeciesID,
                Position:  offsetPosition(swarm.Position, 3.0), // 3 blocks away
                Radius:    swarm.Radius,
                Count:     splitCount,
                HomePos:   swarm.Position, // New home at split point
                WanderRad: swarm.WanderRad,
            }
            newSwarms = append(newSwarms, newSwarm)
        }
    }

    // Add after iteration complete
    for _, s := range newSwarms {
        state.Swarms[s.ID] = s
    }
}
```

---

## Species System (Data-Driven)

### Species Definition

```go
// File: nakama/modules/entities/species.go

type BugSpecies struct {
    ID              string            `json:"id"`
    Name            string            `json:"name"`
    Description     string            `json:"description"` // For inspection UI
    Category        string            `json:"category"`    // "swarm", "individual", "boss"

    // Movement
    BaseSpeed       float32           `json:"base_speed"`
    WanderRadius    float32           `json:"wander_radius"`

    // Swarm-specific (category=swarm only)
    MinSwarmSize    int               `json:"min_swarm_size"`
    MaxSwarmSize    int               `json:"max_swarm_size"`
    SwarmRadius     float32           `json:"swarm_radius"`     // Visual spread
    MergeRadius     float32           `json:"merge_radius"`     // Distance to trigger merge
    SplitThreshold  int               `json:"split_threshold"`  // Count above which may split
    SplitChance     float32           `json:"split_chance"`     // Per-tick probability

    // Player Reaction AI
    PlayerReaction  string            `json:"player_reaction"`  // "ignore", "flee", "attack", "curious"
    ReactionRadius  float32           `json:"reaction_radius"`  // Trigger distance
    FleeSpeedMult   float32           `json:"flee_speed_mult"`  // Speed multiplier when fleeing
    AttackDamage    int               `json:"attack_damage"`
    AttackCooldown  float32           `json:"attack_cooldown"`

    // Catching Requirements
    NetSize           string             `json:"net_size"`           // "small", "medium", "large", "trap_only"

    // Condition Meter System
    CatchCondition    string             `json:"catch_condition"`    // "always", "calm", "stunned", "distracted", "weakened"
    ConditionThreshold float32           `json:"condition_threshold"` // Value needed (0-100) for catch
    ConditionDecay    float32            `json:"condition_decay"`    // Decay per second when not applied
    ConditionTools    map[string]float32 `json:"condition_tools"`    // Tool -> meter increase: {"smoke_gun": 30}

    // HP (for "weakened" condition type)
    MaxHP             int                `json:"max_hp"`             // 0 = no HP, >0 = has health
    DamageTools       map[string]int     `json:"damage_tools"`       // Tool -> damage: {"sword": 20}

    // Economy
    SellPrice       int               `json:"sell_price"`

    // Reproduction
    BreedingPlants  []string          `json:"breeding_plants"`
    EggCountMin     int               `json:"egg_count_min"`
    EggCountMax     int               `json:"egg_count_max"`
    HatchTime       float32           `json:"hatch_time"`
    ReproduceCooldown float32         `json:"reproduce_cooldown"`

    // Sprites (client uses these IDs to load assets)
    SpriteID        string            `json:"sprite_id"`
    EggSpriteID     string            `json:"egg_sprite_id"`
}
```

### Initial Species Set

| Species | Category | Net Size | Reaction | Condition | Threshold | Sell Price |
|---------|----------|----------|----------|-----------|-----------|------------|
| `fly` | swarm | small | ignore | always | 0 | 1 |
| `bee` | swarm | small | attack | calm | 80 | 5 |
| `ant` | swarm | small | flee | distracted | 50 | 2 |
| `beetle` | individual | medium | flee | stunned | 60 | 50 |
| `giant_beetle` | individual | large | attack | weakened | HP=0 | 200 |

### Species Loading

```go
// File: nakama/modules/entities/species.go

import (
    "encoding/json"
    "os"
)

// LoadSpecies reads species definitions from JSON config
func LoadSpecies(path string) (map[string]*BugSpecies, error) {
    data, err := os.ReadFile(path)
    if err != nil {
        return nil, fmt.Errorf("failed to read species config: %w", err)
    }

    var raw map[string]json.RawMessage
    if err := json.Unmarshal(data, &raw); err != nil {
        return nil, fmt.Errorf("failed to parse species config: %w", err)
    }

    species := make(map[string]*BugSpecies)
    for id, specData := range raw {
        var spec BugSpecies
        if err := json.Unmarshal(specData, &spec); err != nil {
            return nil, fmt.Errorf("failed to parse species %s: %w", id, err)
        }
        spec.ID = id
        species[id] = &spec
    }

    return species, nil
}

// Called during MatchInit
func (m *Match) initSpecies(state *WorldState) error {
    species, err := LoadSpecies("data/species.json")
    if err != nil {
        return err
    }
    state.Species = species
    return nil
}
```

---

## Data Structures

### Server: SwarmState

```go
// File: nakama/modules/entities/swarm.go

type SwarmState struct {
    ID            string
    SpeciesID     string           // References BugSpecies
    Position      EntityPosition   // Center position
    Radius        float32          // Spread radius in blocks
    Count         int              // Number of bugs
    Facing        Direction        // Movement direction hint
    Velocity      Vec2             // Current movement
    HomePos       EntityPosition   // Wander anchor
    WanderRad     float32          // Max distance from home
    ReproduceCooldown float32      // Seconds until can reproduce again

    // Condition meter (for subduing mechanics)
    ConditionValue float32         // Current meter level (0-100)
    CurrentHP      int             // For HP-based creatures (starts at MaxHP, 0 = catchable)
}

type Vec2 struct {
    X, Y float32
}
```

### Server: EggClusterState

```go
// File: nakama/modules/entities/eggs.go

type EggClusterState struct {
    ID          string
    SpeciesID   string           // What species will hatch
    Position    EntityPosition   // Where eggs were laid
    Count       int              // Number of eggs
    HatchTimer  float32          // Countdown until hatch
    ParentSwarm string           // Original swarm ID (for merging back)
}
```

### Server: IndividualBugState

```go
// File: nakama/modules/entities/individual.go

type IndividualBugState struct {
    ID         string
    SpeciesID  string
    Position   EntityPosition
    Facing     Direction

    // Bezier movement
    PathPoints []Vec2           // Control points
    PathT      float32          // Progress along curve [0, 1]
    Speed      float32

    // AI state
    State      BugAIState       // idle, wander, alert, chase, flee
    TargetID   string           // Player ID if chasing/fleeing

    // Condition meter (for subduing mechanics)
    ConditionValue float32      // Current meter level (0-100)
    CurrentHP      int          // For HP-based creatures (starts at MaxHP, 0 = catchable)
}

type BugAIState int
const (
    BugIdle BugAIState = iota
    BugWander
    BugAlert
    BugChase
    BugFlee
)
```

### Server: PlantState

```go
// File: nakama/modules/entities/plant.go

type PlantState struct {
    ID         string
    PlantType  string           // "rotting_fruit", "flower", etc.
    Position   EntityPosition   // Grid origin position
    Health     int              // Consumed when breeding occurs
    GrowthTime float32          // Time since planted (for natural ones)
}
```

### Server: PlantDef (Configuration)

```go
// File: nakama/modules/entities/plant.go

// PlantDef defines a plant type's properties (loaded from config)
type PlantDef struct {
    PlantType   string   `json:"plant_type"`   // "rotting_fruit", "flower", "oak_tree"
    SeedType    string   `json:"seed_type"`    // "fruit_seed", "flower_seed", "acorn"
    Health      int      `json:"health"`       // How many breeding cycles before consumed
    DropsSeed   bool     `json:"drops_seed"`   // Does it drop seed when destroyed?
    SpawnWeight float32  `json:"spawn_weight"` // Relative probability for natural spawning
    BreedTypes  []string `json:"breed_types"`  // Which bug species can breed here
}
```

### Server: GroundItem

```go
// File: nakama/modules/entities/items.go

// GroundItem represents a dropped item in the world (seeds, etc.)
type GroundItem struct {
    ID       string
    ItemType string           // "acorn", "flower_seed", etc.
    Position EntityPosition
    Lifetime float32          // Seconds until despawn (60.0 default)
}
```

---

## Footprint System (Plants & Structures)

Sprites can be any visual size, but occupy a defined "footprint" on the grid for placement and collision.

### Two Collision Types

1. **Footprint (Placement/Walking)** - Grid cells that are "occupied"
   - Blocks placement of other structures
   - Optionally blocks player walking
   - Stored as compound rectangles

2. **Interaction Bounds (Clicking)** - Full sprite area
   - Uses Unity's Collider2D on the sprite
   - No special system needed

### Footprint Component

```csharp
// File: Assets/Scripts/Entities/Footprint.cs

[System.Serializable]
public struct FootprintRect
{
    public Vector2Int position;   // Relative to entity grid origin
    public Vector2Int size;       // Width x Height in grid cells
    public bool blocksWalking;    // Can players walk here?
}

public class Footprint : MonoBehaviour
{
    [SerializeField] private Vector2Int gridOrigin;  // Sprite pivot to grid origin offset
    [SerializeField] private List<FootprintRect> rects;

    /// <summary>
    /// Get all grid cells occupied by this footprint at a world position.
    /// </summary>
    public IEnumerable<Vector2Int> GetOccupiedCells(Vector2Int worldGridPos)
    {
        foreach (var rect in rects)
        {
            for (int x = 0; x < rect.size.x; x++)
            {
                for (int y = 0; y < rect.size.y; y++)
                {
                    yield return worldGridPos + gridOrigin + rect.position + new Vector2Int(x, y);
                }
            }
        }
    }

    /// <summary>
    /// Check if a grid cell blocks walking.
    /// </summary>
    public bool BlocksWalkingAt(Vector2Int worldGridPos, Vector2Int checkCell)
    {
        foreach (var rect in rects)
        {
            if (!rect.blocksWalking) continue;
            var rectOrigin = worldGridPos + gridOrigin + rect.position;
            if (checkCell.x >= rectOrigin.x && checkCell.x < rectOrigin.x + rect.size.x &&
                checkCell.y >= rectOrigin.y && checkCell.y < rectOrigin.y + rect.size.y)
            {
                return true;
            }
        }
        return false;
    }

    private void OnDrawGizmosSelected()
    {
        // Draw footprint overlay in editor
        Gizmos.color = new Color(1f, 0f, 0f, 0.3f);
        foreach (var rect in rects)
        {
            var origin = (Vector2)(gridOrigin + rect.position);
            var size = (Vector2)rect.size;
            Gizmos.DrawCube(transform.position + new Vector3(origin.x + size.x/2, origin.y + size.y/2, 0),
                           new Vector3(size.x, size.y, 0.1f));
        }
    }
}
```

### Example Footprints

| Structure | Rects | Visual |
|-----------|-------|--------|
| Tree (1x1) | `[{pos:(0,0), size:(1,1)}]` | `X` |
| House (3x2) | `[{pos:(0,0), size:(3,2)}]` | `XXX`<br>`XXX` |
| L-barn | `[{pos:(0,0), size:(4,2)}, {pos:(0,2), size:(2,2)}]` | `XX`<br>`XX`<br>`XXXX`<br>`XXXX` |
| Bridge | `[{pos:(0,0), size:(1,4), blocksWalking:false}]` | Occupied but walkable |

### Server Validation

Server needs footprint data to validate placements:

```go
// File: nakama/modules/entities/footprints.go

type FootprintRect struct {
    X, Y          int
    Width, Height int
    BlocksWalking bool
}

type FootprintDef struct {
    OriginX, OriginY int
    Rects            []FootprintRect
}

// Loaded from structures.json or embedded in species.json for plants
var Footprints = map[string]*FootprintDef{
    "tree":         {Rects: []FootprintRect{{0, 0, 1, 1, true}}},
    "rotting_fruit": {Rects: []FootprintRect{{0, 0, 1, 1, true}}},
    "flower":       {Rects: []FootprintRect{{0, 0, 1, 1, true}}},
}

func (state *WorldState) CanPlace(structureType string, gridX, gridY int) bool {
    def := Footprints[structureType]
    if def == nil {
        return false
    }

    for _, rect := range def.Rects {
        for dx := 0; dx < rect.Width; dx++ {
            for dy := 0; dy < rect.Height; dy++ {
                cell := Vec2Int{gridX + def.OriginX + rect.X + dx, gridY + def.OriginY + rect.Y + dy}
                if state.OccupiedCells[cell] {
                    return false
                }
            }
        }
    }
    return true
}
```

### Server: WorldState Additions

```go
// File: nakama/modules/world/state.go

type Vec2Int struct {
    X, Y int
}

type WorldState struct {
    // ... existing fields ...
    Swarms      map[string]*SwarmState
    EggClusters map[string]*EggClusterState
    Individuals map[string]*IndividualBugState
    Plants      map[string]*PlantState
    Species     map[string]*BugSpecies  // Loaded from config

    // Footprint/placement tracking
    OccupiedCells map[Vec2Int]string  // Grid cell -> entity ID that occupies it

    // Plant system
    PlantDefs    map[string]*PlantDef   // Plant type -> definition (loaded from config)
    GroundItems  map[string]*GroundItem // Dropped items (seeds, etc.)

    // Cleanup slices (avoid map modification during iteration)
    PlantsToDelete []string

    // Per-tick tracking to prevent race conditions
    ConsumedPlants map[string]bool  // Plants consumed this tick (prevents double-consume)
}
```

---

## Wire Protocol

### OpCodes

Existing OpCodes (from Phase 2):
- 1-7: Client → Server (Movement, Action, ChunkSubscribe, etc.)
- 10-12: Server → Client (StateUpdate, EntityUpdate, Chat)
- 13-19: Reserved for future core systems

New OpCodes for Bug System (20-29):

| OpCode | Direction | Name | Purpose |
|--------|-----------|------|---------|
| 20 | S→C | SwarmUpdate | Swarm positions/counts/status (batched) |
| 21 | S→C | EggUpdate | Egg cluster positions/counts (batched) |
| 22 | S→C | IndividualUpdate | Individual bug positions (batched) |
| 23 | S→C | PlantUpdate | Plant positions/health (batched) |
| 24 | C→S | CatchBug | Player clicked on a bug |
| 25 | S→C | BugCaught | Broadcast: bug was caught (includes catch position) |
| 26 | S→C | InventoryUpdate | Player's inventory changed |
| 27 | C→S | UseToolOnBug | Player uses tool (smoke gun, etc.) on bug |
| 28 | S→C | BugConditionUpdate | Bug condition meter changed |

Tool/Trap OpCodes (30-39):

| OpCode | Direction | Name | Purpose |
|--------|-----------|------|---------|
| 29 | C→S | PlaceTrap | Player places a trap/net |
| 30 | S→C | TrapUpdate | Trap state changes, catches |
| 31 | C→S | InspectBug | Player uses magnifying glass on bug |
| 32 | S→C | BugInfo | Server sends species data for inspection UI |
| 33 | C→S | PlantSeed | Player plants a seed at position |
| 34 | S→C | SeedPlanted | Confirms plant was created |
| 35 | S→C | GroundItemUpdate | Batched ground item positions |
| 36 | S→C | ItemPickedUp | Item was collected (for animation) |

**Note:** OpCodes 20-29 for bug/swarm system, 30-39 for traps/tools/planting.

### Message Structs

```go
// File: nakama/modules/world/messages.go

// OpCode 20: SwarmUpdate - batched swarm data
type SwarmData struct {
    ID             string  `json:"id"`
    SpeciesID      string  `json:"species_id"`
    X              float32 `json:"x"`
    Y              float32 `json:"y"`
    Radius         float32 `json:"radius"`
    Count          int     `json:"count"`
    Facing         int     `json:"facing"`
    ConditionValue float32 `json:"condition_value"` // For meter display (0-100)
    CurrentHP      int     `json:"current_hp"`      // For HP bar display
    MaxHP          int     `json:"max_hp"`          // For HP bar max
}
type SwarmUpdateMessage struct {
    Swarms []SwarmData `json:"swarms"`
}

// OpCode 21: EggUpdate - batched egg data
type EggData struct {
    ID        string  `json:"id"`
    SpeciesID string  `json:"species_id"`
    X         float32 `json:"x"`
    Y        float32 `json:"y"`
    Count    int     `json:"count"`
    HatchPct float32 `json:"hatch_pct"`  // 0-1 progress
}
type EggUpdateMessage struct {
    Eggs []EggData `json:"eggs"`
}

// OpCode 22: IndividualUpdate - batched individual data
type IndividualData struct {
    ID             string  `json:"id"`
    SpeciesID      string  `json:"species_id"`
    X              float32 `json:"x"`
    Y              float32 `json:"y"`
    Facing         int     `json:"facing"`
    State          int     `json:"state"`           // AI state
    ConditionValue float32 `json:"condition_value"` // For meter display (0-100)
    CurrentHP      int     `json:"current_hp"`      // For HP bar display
    MaxHP          int     `json:"max_hp"`          // For HP bar max
}
type IndividualUpdateMessage struct {
    Individuals []IndividualData `json:"individuals"`
}

// OpCode 23: PlantUpdate - batched plant data
type PlantData struct {
    ID      string  `json:"id"`
    Type    string  `json:"type"`
    X       float32 `json:"x"`
    Y       float32 `json:"y"`
    Health  int     `json:"health"`
}
type PlantUpdateMessage struct {
    Plants []PlantData `json:"plants"`
}

// OpCode 24: CatchBug (C→S) - AoE net swing at click position
type CatchBugMessage struct {
    ClickX float32 `json:"click_x"` // World position of click
    ClickY float32 `json:"click_y"`
}

// OpCode 25: BugEffect (S→C) - unified message for all swarm/bug state changes
// Replaces old BugCaught and BugConditionUpdate messages
type BugEffect struct {
    TargetID   string  `json:"target_id"`   // Swarm or individual bug ID
    TargetType string  `json:"target_type"` // "swarm" | "bug"
    EffectType string  `json:"effect_type"` // "catch", "smoke", "stun", "damage", "spawn", etc.
    ActorID    string  `json:"actor_id"`    // Who caused it (player ID)
    X          float32 `json:"x"`           // Effect position (for visuals)
    Y          float32 `json:"y"`

    // Swarm fields (when target_type = "swarm")
    CountDelta int `json:"count_delta"` // -3 = lost 3 flies, +2 = spawned 2
    NewCount   int `json:"new_count"`   // Authoritative count after change

    // Individual fields (when target_type = "bug")
    Removed bool `json:"removed"` // true = bug caught/destroyed

    // State fields (both types)
    ConditionDelta float32 `json:"condition_delta"` // +30 calm, -20 HP, etc.
    NewCondition   float32 `json:"new_condition"`   // Authoritative value

    // Effect-specific data
    Params string `json:"params"` // JSON for extra data (e.g., {"duration":3.0})
}

// OpCode 37: CatchResult (S→C) - feedback sent ONLY to the catcher
type CatchResult struct {
    TotalCaught int      `json:"total_caught"` // Sum from all swarms/bugs caught
    Reasons     []string `json:"reasons"`      // Failure reasons: "miss", "wrong_net:Bee", "condition:calm"
    X           float32  `json:"x"`
    Y           float32  `json:"y"`
}

// OpCode 26: InventoryUpdate (S→C) - sent only to the player who caught
type InventoryUpdateMessage struct {
    SpeciesID string `json:"species_id"`
    Count     int    `json:"count"` // New total for this species
}

// OpCode 33: PlantSeed (C→S) - player plants a seed
type PlantSeedMessage struct {
    SeedType string  `json:"seed_type"` // "acorn", "flower_seed", etc.
    X        float32 `json:"x"`
    Y        float32 `json:"y"`
}

// OpCode 34: SeedPlanted (S→C) - confirms plant was created
type SeedPlantedMessage struct {
    PlantID   string  `json:"plant_id"`
    PlantType string  `json:"plant_type"`
    X         float32 `json:"x"`
    Y         float32 `json:"y"`
}

// OpCode 35: GroundItemUpdate (S→C) - batched ground items
type GroundItemData struct {
    ID       string  `json:"id"`
    ItemType string  `json:"item_type"` // "acorn", "flower_seed"
    X        float32 `json:"x"`
    Y        float32 `json:"y"`
}
type GroundItemUpdateMessage struct {
    Items []GroundItemData `json:"items"`
}

// OpCode 36: ItemPickedUp (S→C) - item was collected
type ItemPickedUpMessage struct {
    ItemID   string `json:"item_id"`
    PlayerID string `json:"player_id"`
    ItemType string `json:"item_type"`
}
```

### Client DTOs (C#)

**File:** `Assets/Scripts/Networking/BugMessages.cs`

```csharp
using System;

namespace BugFarmer.Networking
{
    // OpCode 24: CatchBug (C→S) - AoE net swing
    [Serializable]
    public class CatchBugMessage
    {
        public float click_x;
        public float click_y;
    }

    // OpCode 27: UseToolOnBug (C→S)
    [Serializable]
    public class UseToolOnBugMessage
    {
        public string tool_id;
        public string target_id;
        public float x;
        public float y;
    }

    // OpCode 31: InspectBug (C→S)
    [Serializable]
    public class InspectBugMessage
    {
        public string target_id;
    }

    // OpCode 20: SwarmUpdate (S→C)
    [Serializable]
    public class SwarmData
    {
        public string id;
        public string species_id;
        public float x;
        public float y;
        public float radius;
        public int count;
        public int facing;
        public float condition_value;
        public int current_hp;
        public int max_hp;
    }

    [Serializable]
    public class SwarmUpdateMessage
    {
        public SwarmData[] swarms;
    }

    // OpCode 22: IndividualUpdate (S→C)
    [Serializable]
    public class IndividualData
    {
        public string id;
        public string species_id;
        public float x;
        public float y;
        public int facing;
        public int state;
        public float condition_value;
        public int current_hp;
        public int max_hp;
    }

    [Serializable]
    public class IndividualUpdateMessage
    {
        public IndividualData[] individuals;
    }

    // OpCode 25: BugEffect (S→C) - unified effect for all swarm/bug state changes
    [Serializable]
    public class BugEffect
    {
        public string target_id;
        public string target_type;  // "swarm" | "bug"
        public string effect_type;  // "catch", "smoke", "stun", "damage", "spawn"
        public string actor_id;
        public float x;
        public float y;

        // Swarm fields
        public int count_delta;
        public int new_count;

        // Individual fields
        public bool removed;

        // State fields
        public float condition_delta;
        public float new_condition;

        // Extra data
        public string @params;
    }

    // OpCode 26: InventoryUpdate (S→C)
    [Serializable]
    public class InventoryUpdateMessage
    {
        public string species_id;
        public int count;
    }

    // OpCode 37: CatchResult (S→C) - feedback sent only to catcher
    [Serializable]
    public class CatchResult
    {
        public int total_caught;
        public string[] reasons;
        public float x;
        public float y;
    }

    // OpCode 32: BugInfo (S→C)
    [Serializable]
    public class BugInfoMessage
    {
        public string species_id;
        public string name;
        public string description;
        public string net_size;
        public string catch_condition;
        public float condition_threshold;
        public int max_hp;
        public int sell_price;
        public string breeding_info;
    }

    // OpCode 33: PlantSeed (C→S)
    [Serializable]
    public class PlantSeedMessage
    {
        public string seed_type;
        public float x;
        public float y;
    }

    // OpCode 34: SeedPlanted (S→C)
    [Serializable]
    public class SeedPlantedMessage
    {
        public string plant_id;
        public string plant_type;
        public float x;
        public float y;
    }

    // OpCode 35: GroundItemUpdate (S→C)
    [Serializable]
    public class GroundItemData
    {
        public string id;
        public string item_type;
        public float x;
        public float y;
    }

    [Serializable]
    public class GroundItemUpdateMessage
    {
        public GroundItemData[] items;
    }

    // OpCode 36: ItemPickedUp (S→C)
    [Serializable]
    public class ItemPickedUpMessage
    {
        public string item_id;
        public string player_id;
        public string item_type;
    }
}
```

---

## Catching System

### Flow

```
1. Player clicks on fly sprite (client-side)
2. Client sends CatchBug (OpCode 24) with swarm ID and click position
3. Server validates:
   - Swarm exists
   - Click is within swarm radius (+ tolerance)
   - Player is within catch range (e.g., 10 blocks)
   - Rate limit check (prevent spam)
   - [Phase 2+] Net size matches species requirement
   - Condition thresholds met (catch_condition)
4. Server:
   - Decrements swarm count
   - Adds bug to player inventory
   - Broadcasts BugCaught (OpCode 25) to ALL players
   - Sends InventoryUpdate (OpCode 26) to catcher only
5. Clients:
   - Catcher: Plays own catching animation, removes local fly
   - Others: See net swing animation at catch position, remove random local fly
```

### Visual Feedback

**Activity Indicator:**
- BugCaught message includes catch position (X, Y)
- Other players show net swing animation at that position
- No separate activity message needed

**Animations:**
- Catcher sees their own detailed catching animation
- All other players see a simpler net swing animation at the catch position
- Fly disappears with small poof effect

### Server Handler

```go
// OpCode constants for bug system
const (
    // Bug/Swarm OpCodes (20-29)
    OpCodeSwarmUpdate      int64 = 20
    OpCodeEggUpdate        int64 = 21
    OpCodeIndividualUpdate int64 = 22
    OpCodePlantUpdate      int64 = 23
    OpCodeCatchBug         int64 = 24
    OpCodeBugEffect        int64 = 25  // Unified swarm/bug state changes (replaces BugCaught, BugConditionUpdate)
    OpCodeInventoryUpdate  int64 = 26
    OpCodeUseToolOnBug     int64 = 27
    // OpCode 28 deprecated (was BugConditionUpdate, now handled by BugEffect)

    // Trap/Tool OpCodes (30-39)
    OpCodePlaceTrap        int64 = 29
    OpCodeTrapUpdate       int64 = 30
    OpCodeInspectBug       int64 = 31
    OpCodeBugInfo          int64 = 32
    OpCodeCatchResult      int64 = 37  // Catch feedback sent only to catcher
)

// Net radius configuration
var NetRadii = map[string]float32{
    "net_small":  1.5,
    "net_medium": 2.5,
    "net_large":  4.0,
}

// In MatchLoop message processing - AoE catch handler
func (m *Match) handleCatchBug(
    ctx context.Context,
    logger runtime.Logger,
    dispatcher runtime.MatchDispatcher,
    state *WorldState,
    msg CatchBugMessage,
    playerID string,
) {
    player, playerExists := state.Players[playerID]
    if !playerExists {
        return
    }

    // Rate limit: one catch per 200ms per player
    now := time.Now().UnixMilli()
    if now-player.LastCatchTime < 200 {
        return
    }
    player.LastCatchTime = now

    // Get net radius from equipped tool
    netRadius, ok := NetRadii[player.EquippedTool]
    if !ok {
        return // Not a net equipped
    }

    // Validate player is within reach (arm length + net radius)
    chunkSize := float32(state.Config.ChunkSize)
    playerX := float32(player.Position.ChunkX)*chunkSize + player.Position.LocalX
    playerY := float32(player.Position.ChunkY)*chunkSize + player.Position.LocalY
    dx := msg.ClickX - playerX
    dy := msg.ClickY - playerY
    maxReach := 3.0 + netRadius
    if dx*dx+dy*dy > maxReach*maxReach {
        return
    }

    totalCaught := 0
    reasons := []string{}

    // Check all swarms for overlap with catch circle
    for _, swarm := range state.Swarms {
        caught, reason := m.tryCatchFromSwarm(state, swarm, msg.ClickX, msg.ClickY, netRadius, player, dispatcher)
        if caught > 0 {
            totalCaught += caught
        } else if reason != "" {
            reasons = append(reasons, reason)
        }
    }

    // Check all individual bugs for overlap
    for _, bug := range state.Individuals {
        caught, reason := m.tryCatchIndividual(state, bug, msg.ClickX, msg.ClickY, netRadius, player, dispatcher)
        if caught {
            totalCaught++
        } else if reason != "" {
            reasons = append(reasons, reason)
        }
    }

    // Send feedback to catcher only
    if totalCaught == 0 && len(reasons) == 0 {
        reasons = append(reasons, "miss")
    }

    resultMsg := CatchResult{
        TotalCaught: totalCaught,
        Reasons:     reasons,
        X:           msg.ClickX,
        Y:           msg.ClickY,
    }
    resultData, _ := json.Marshal(resultMsg)
    dispatcher.BroadcastMessage(OpCodeCatchResult, resultData,
        []runtime.Presence{state.Presences[playerID]}, nil, true)
}

// Try to catch flies from a swarm within net radius
func (m *Match) tryCatchFromSwarm(
    state *WorldState,
    swarm *SwarmState,
    clickX, clickY, netRadius float32,
    player *PlayerState,
    dispatcher runtime.MatchDispatcher,
) (int, string) {
    species := state.Species[swarm.SpeciesID]
    chunkSize := float32(state.Config.ChunkSize)

    // Validate net size matches species requirement
    if getNetSize(player.EquippedTool) != species.NetSize {
        return 0, fmt.Sprintf("wrong_net:%s", species.Name)
    }

    // Validate condition is met
    if !m.canCatchSwarm(swarm, species) {
        return 0, fmt.Sprintf("condition:%s", species.CatchCondition)
    }

    // Check overlap between net circle and swarm circle
    swarmX := float32(swarm.Position.ChunkX)*chunkSize + swarm.Position.LocalX
    swarmY := float32(swarm.Position.ChunkY)*chunkSize + swarm.Position.LocalY
    dx := clickX - swarmX
    dy := clickY - swarmY
    dist := float32(math.Sqrt(float64(dx*dx + dy*dy)))

    if dist > netRadius+swarm.Radius {
        return 0, "" // No overlap
    }

    // Calculate caught count based on overlap
    caught := m.calculateCaughtCount(swarm, dist, netRadius)
    if caught <= 0 {
        return 0, ""
    }

    // Apply catch
    swarm.Count -= caught
    player.AddToInventory(swarm.SpeciesID, caught)

    // Broadcast BugEffect to all players
    effect := BugEffect{
        TargetID:   swarm.ID,
        TargetType: "swarm",
        EffectType: "catch",
        ActorID:    player.ID,
        X:          clickX,
        Y:          clickY,
        CountDelta: -caught,
        NewCount:   swarm.Count,
    }
    data, _ := json.Marshal(effect)
    dispatcher.BroadcastMessage(OpCodeBugEffect, data, nil, nil, true)

    // Clean up empty swarm
    if swarm.Count <= 0 {
        delete(state.Swarms, swarm.ID)
    }

    return caught, ""
}

// Try to catch an individual bug within net radius
func (m *Match) tryCatchIndividual(
    state *WorldState,
    bug *IndividualBugState,
    clickX, clickY, netRadius float32,
    player *PlayerState,
    dispatcher runtime.MatchDispatcher,
) (bool, string) {
    species := state.Species[bug.SpeciesID]
    chunkSize := float32(state.Config.ChunkSize)

    // Validate net size matches species requirement
    if getNetSize(player.EquippedTool) != species.NetSize {
        return false, fmt.Sprintf("wrong_net:%s", species.Name)
    }

    // Validate condition is met
    if !m.canCatchIndividual(bug, species) {
        return false, fmt.Sprintf("condition:%s", species.CatchCondition)
    }

    // Check if bug is within net radius
    bugX := float32(bug.Position.ChunkX)*chunkSize + bug.Position.LocalX
    bugY := float32(bug.Position.ChunkY)*chunkSize + bug.Position.LocalY
    dx := clickX - bugX
    dy := clickY - bugY
    if dx*dx+dy*dy > netRadius*netRadius {
        return false, "" // Not in range
    }

    // Apply catch
    player.AddToInventory(bug.SpeciesID, 1)

    // Broadcast BugEffect to all players
    effect := BugEffect{
        TargetID:   bug.ID,
        TargetType: "bug",
        EffectType: "catch",
        ActorID:    player.ID,
        X:          clickX,
        Y:          clickY,
        Removed:    true,
    }
    data, _ := json.Marshal(effect)
    dispatcher.BroadcastMessage(OpCodeBugEffect, data, nil, nil, true)

    delete(state.Individuals, bug.ID)
    return true, ""
}

// Calculate how many flies to catch based on net/swarm overlap
func (m *Match) calculateCaughtCount(swarm *SwarmState, dist, netRadius float32) int {
    // Full coverage - net completely covers swarm
    if dist <= netRadius-swarm.Radius {
        return swarm.Count
    }

    // Partial overlap - proportional catch
    overlap := (netRadius + swarm.Radius - dist) / (2 * swarm.Radius)
    if overlap > 1 {
        overlap = 1
    }

    // Catch ~50% of flies in overlap area (some escape)
    caught := int(float32(swarm.Count) * overlap * 0.5)
    if caught < 1 && overlap > 0.1 {
        caught = 1 // At least 1 if decent overlap
    }

    return caught
}

// Validation helpers
func (m *Match) canCatchSwarm(swarm *SwarmState, species *BugSpecies) bool {
    switch species.CatchCondition {
    case "always":
        return true
    case "weakened":
        return swarm.CurrentHP <= 0
    default:
        return swarm.ConditionValue >= species.ConditionThreshold
    }
}

func (m *Match) canCatchIndividual(bug *IndividualBugState, species *BugSpecies) bool {
    switch species.CatchCondition {
    case "always":
        return true
    case "weakened":
        return bug.CurrentHP <= 0
    default:
        return bug.ConditionValue >= species.ConditionThreshold
    }
}
```

### Race Condition Handling

When two players interact with the same swarm simultaneously:
- Server processes sequentially (match loop is single-threaded)
- Both catches can succeed if swarm count >= 2
- Each client removes a random fly from their own local representation
- Important: Flies don't exist on the server - only swarm center and count
- Each client independently spawns and manages its own fly instances within the swarm bounds

---

## Condition Meter System

Each bug species has ONE condition type that determines how it becomes catchable. Tools add to the condition meter, which decays over time.

### Condition Types

| Condition | Meter | Threshold | Tools | Gameplay |
|-----------|-------|-----------|-------|----------|
| `always` | N/A | 0 | Net only | Easy catch (flies) |
| `calm` | Calm | 80 | Smoke gun, incense | Beekeeping |
| `stunned` | Stun | 60 | Stun prod, traps | Action |
| `distracted` | Distract | 50 | Bait | Lure mechanics |
| `weakened` | HP (inverted) | HP=0 | Weapons | Combat |

### How It Works

1. **Tools modify the condition meter** - smoke gun adds +30 to calm meter
2. **Meter decays over time** - species-specific decay rate (e.g., 5 per second)
3. **Catchable when threshold met** - `ConditionValue >= species.ConditionThreshold`
4. **HP-based is inverted** - weapons reduce HP, catchable at HP=0

### Example: Catching a Bee

1. Bee has `catch_condition: "calm"`, `condition_threshold: 80`
2. Player equips smoke gun
3. Player uses smoke gun on bee swarm (OpCode 27: UseToolOnBug)
4. Server adds `species.ConditionTools["smoke_gun"]` (30) to `swarm.ConditionValue`
5. Meter decays at `species.ConditionDecay` (5) per second
6. When `ConditionValue >= 80`, player can net the bee (OpCode 24: CatchBug)
7. Server validates condition threshold is met before allowing catch

### Example: Catching a Giant Beetle

1. Beetle has `catch_condition: "weakened"`, `max_hp: 100`
2. Player equips sword
3. Player attacks beetle (OpCode 27: UseToolOnBug)
4. Server subtracts `species.DamageTools["sword"]` (20) from `swarm.CurrentHP`
5. When `CurrentHP <= 0`, beetle is catchable
6. Player uses net (OpCode 24: CatchBug)

### Condition Messages

```go
// OpCode 27: UseToolOnBug (C→S)
type UseToolOnBugMessage struct {
    ToolID   string  `json:"tool_id"`   // "smoke_gun", "sword", etc.
    TargetID string  `json:"target_id"` // Swarm or individual bug ID
    X        float32 `json:"x"`         // Aim position
    Y        float32 `json:"y"`
}

// OpCode 28: BugConditionUpdate (S→C)
type BugConditionUpdateMessage struct {
    BugID          string  `json:"bug_id"`
    ConditionValue float32 `json:"condition_value"` // 0-100
    CurrentHP      int     `json:"current_hp"`      // Only for HP-based
    MaxHP          int     `json:"max_hp"`          // For HP bar display
}
```

### Server: Condition Tick

```go
func (m *Match) tickConditions(state *WorldState, dt float32) {
    // Tick swarm conditions
    for _, swarm := range state.Swarms {
        species := state.Species[swarm.SpeciesID]

        // Skip if no condition decay or always-catchable
        if species.CatchCondition == "always" || species.ConditionDecay == 0 {
            continue
        }

        // HP-based creatures don't decay (damage is permanent)
        if species.CatchCondition == "weakened" {
            continue
        }

        // Decay condition meter toward 0
        if swarm.ConditionValue > 0 {
            swarm.ConditionValue -= species.ConditionDecay * dt
            if swarm.ConditionValue < 0 {
                swarm.ConditionValue = 0
            }
        }
    }

    // Tick individual bug conditions
    for _, bug := range state.Individuals {
        species := state.Species[bug.SpeciesID]

        // Skip if no condition decay or always-catchable
        if species.CatchCondition == "always" || species.ConditionDecay == 0 {
            continue
        }

        // HP-based creatures don't decay (damage is permanent)
        if species.CatchCondition == "weakened" {
            continue
        }

        // Decay condition meter toward 0
        if bug.ConditionValue > 0 {
            bug.ConditionValue -= species.ConditionDecay * dt
            if bug.ConditionValue < 0 {
                bug.ConditionValue = 0
            }
        }
    }
}
```

### Server: Tool Handler

```go
func (m *Match) handleUseToolOnBug(
    ctx context.Context,
    state *WorldState,
    msg UseToolOnBugMessage,
    playerID string,
    dispatcher runtime.MatchDispatcher,
) {
    player, playerExists := state.Players[playerID]
    if !playerExists {
        return
    }

    // Validate player has tool equipped
    if player.EquippedTool != msg.ToolID {
        return // Tool not equipped
    }

    // Rate limit tool usage (500ms between uses)
    now := time.Now().UnixMilli()
    if now - player.LastToolTime < 500 {
        return
    }
    player.LastToolTime = now

    // Validate player is within tool range (8 blocks)
    playerX := player.Position.ChunkX*state.Config.ChunkSize + int(player.Position.LocalX)
    playerY := player.Position.ChunkY*state.Config.ChunkSize + int(player.Position.LocalY)
    dx := msg.X - float32(playerX)
    dy := msg.Y - float32(playerY)
    if dx*dx + dy*dy > 64 { // 8^2 = 64
        return // Too far
    }

    var bugID string
    var conditionValue float32
    var currentHP int
    var maxHP int

    // Try swarm first, then individual
    if swarm, exists := state.Swarms[msg.TargetID]; exists {
        species := state.Species[swarm.SpeciesID]
        bugID = swarm.ID

        // Apply damage
        if damage, ok := species.DamageTools[msg.ToolID]; ok {
            swarm.CurrentHP -= damage
            if swarm.CurrentHP < 0 {
                swarm.CurrentHP = 0
            }
        }

        // Apply condition
        if amount, ok := species.ConditionTools[msg.ToolID]; ok {
            swarm.ConditionValue += amount
            if swarm.ConditionValue > 100 {
                swarm.ConditionValue = 100
            }
        }

        conditionValue = swarm.ConditionValue
        currentHP = swarm.CurrentHP
        maxHP = species.MaxHP

    } else if individual, exists := state.Individuals[msg.TargetID]; exists {
        species := state.Species[individual.SpeciesID]
        bugID = individual.ID

        // Apply damage
        if damage, ok := species.DamageTools[msg.ToolID]; ok {
            individual.CurrentHP -= damage
            if individual.CurrentHP < 0 {
                individual.CurrentHP = 0
            }
        }

        // Apply condition
        if amount, ok := species.ConditionTools[msg.ToolID]; ok {
            individual.ConditionValue += amount
            if individual.ConditionValue > 100 {
                individual.ConditionValue = 100
            }
        }

        conditionValue = individual.ConditionValue
        currentHP = individual.CurrentHP
        maxHP = species.MaxHP

    } else {
        return // Target not found
    }

    // Broadcast using unified BugEffect
    effectMsg := BugEffect{
        TargetID:       bugID,
        TargetType:     "bug",
        EffectType:     "damage",
        ActorID:        senderID,
        ConditionDelta: -damageAmount,
        NewCondition:   conditionValue,
    }
    data, _ := json.Marshal(effectMsg)
    dispatcher.BroadcastMessage(OpCodeBugEffect, data, nil, nil, true)
}
```

---

## Magnifying Glass / Inspection

Players can use a magnifying glass to inspect bugs and learn their requirements.

### What Inspection Reveals

- Species name and description
- Net size required
- Condition type and threshold (e.g., "calm 80" or "weaken to 0 HP")
- Reproduction conditions (which plants, timing)
- Sell price

### Messages

```go
// OpCode 31: InspectBug (C→S)
type InspectBugMessage struct {
    TargetID string `json:"target_id"` // Swarm or individual bug ID
}

// OpCode 32: BugInfo (S→C)
type BugInfoMessage struct {
    SpeciesID          string  `json:"species_id"`
    Name               string  `json:"name"`
    Description        string  `json:"description"`
    NetSize            string  `json:"net_size"`
    CatchCondition     string  `json:"catch_condition"`     // "always", "calm", "weakened", etc.
    ConditionThreshold float32 `json:"condition_threshold"` // 0-100
    MaxHP              int     `json:"max_hp"`              // For HP-based creatures
    SellPrice          int     `json:"sell_price"`
    BreedingInfo       string  `json:"breeding_info"` // Human-readable
}
```

---

## Inventory System

### Server: Player Inventory

```go
// File: nakama/modules/world/state.go

type PlayerState struct {
    UserID        string
    Username      string
    Position      entities.EntityPosition
    Facing        entities.Direction

    // Bug catching
    Inventory     map[string]int  // species_id -> count
    LastCatchTime int64           // Unix millis, for rate limiting

    // Tool system (nets are tools)
    EquippedTool  string          // Current tool ID (e.g., "net_small", "smoke_gun")
    LastToolTime  int64           // Unix millis, for rate limiting tools
}

// Helper to determine net size from tool ID
func getNetSize(toolID string) string {
    switch toolID {
    case "net_small":
        return "small"
    case "net_medium":
        return "medium"
    case "net_large":
        return "large"
    default:
        return ""
    }
}

// Helper to add bugs to inventory (called from catch handler)
func (p *PlayerState) AddToInventory(speciesID string, count int) {
    if p.Inventory == nil {
        p.Inventory = make(map[string]int)
    }
    p.Inventory[speciesID] += count
}
```

### Client: Inventory Display

- UI panel showing caught bugs by species
- Count per species with icon
- Future: Use bugs in crafting, selling, breeding stations

---

## Server Implementation

### MatchLoop Structure

**File:** `nakama/modules/world/match.go`

Each tick (100ms):
```
1. Process player inputs (movement, catch attempts, plant seeds)
2. Simulate swarms (Brownian motion)
3. Simulate individuals (Bezier movement, AI)
4. Tick egg timers (hatch when ready)
5. Check reproduction (swarm near plant)
6. Check swarm merging (every 10 ticks)
7. Check swarm splitting (every 10 ticks)
8. Tick ground items (lifetime countdown)
9. Check item pickups (player walks over item)
10. Tick plant respawn (if count < max)
11. Collect visible entities by player
12. Broadcast updates (OpCodes 20-28, 35-36)
```

### Swarm Simulation

```go
func (m *Match) simulateSwarms(state *WorldState, dt float32) {
    for _, swarm := range state.Swarms {
        species := state.Species[swarm.SpeciesID]

        // Brownian motion: random direction changes
        if rand.Float32() < 0.1 {
            angle := rand.Float32() * 2 * math.Pi
            swarm.Velocity = Vec2{
                X: float32(math.Cos(float64(angle))) * species.BaseSpeed,
                Y: float32(math.Sin(float64(angle))) * species.BaseSpeed,
            }
        }

        // Pull toward home if too far
        if distFromHome(swarm) > swarm.WanderRad {
            swarm.Velocity = biasTowardHome(swarm)
        }

        // Apply velocity
        swarm.Position.LocalX += swarm.Velocity.X * dt
        swarm.Position.LocalY += swarm.Velocity.Y * dt
        swarm.Position.Normalize(state.Config.ChunkSize)

        // Check reproduction (pass dt for cooldown)
        m.checkReproduction(state, swarm, dt)
    }

    // Clean up plants marked for deletion during reproduction
    for _, id := range state.PlantsToDelete {
        m.removePlant(state, id) // Uses helper to also free OccupiedCells
    }
    state.PlantsToDelete = state.PlantsToDelete[:0] // Clear slice

    // Clear consumed plants tracking for next tick
    state.ConsumedPlants = make(map[string]bool)
}
```

### Reproduction Cycle

```go
func (m *Match) checkReproduction(state *WorldState, swarm *SwarmState, dt float32) {
    // Decrement cooldown
    if swarm.ReproduceCooldown > 0 {
        swarm.ReproduceCooldown -= dt
        return // Still on cooldown
    }

    species := state.Species[swarm.SpeciesID]

    // Need minimum swarm size to reproduce
    if swarm.Count < species.MinSwarmSize {
        return
    }

    // Find nearby plant of correct type
    for id, plant := range state.Plants {
        if !contains(species.BreedingPlants, plant.PlantType) {
            continue
        }
        if distBetween(swarm.Position, plant.Position) > 3.0 {
            continue
        }
        // Skip plants already consumed this tick (prevents multiple swarms using same plant)
        if state.ConsumedPlants[id] {
            continue
        }

        // Mark plant as consumed for this tick
        state.ConsumedPlants[id] = true

        // Lay eggs! Use species-specific egg count range
        eggCount := species.EggCountMin + rand.Intn(species.EggCountMax - species.EggCountMin + 1)
        eggs := &EggClusterState{
            ID:          fmt.Sprintf("eggs_%s", uuid.NewString()[:8]),
            SpeciesID:   swarm.SpeciesID,
            Position:    plant.Position,
            Count:       eggCount,
            HatchTimer:  species.HatchTime,
            ParentSwarm: swarm.ID,
        }
        state.EggClusters[eggs.ID] = eggs

        // Start cooldown (uses species-specific cooldown)
        swarm.ReproduceCooldown = species.ReproduceCooldown

        // Consume plant health
        plant.Health--
        if plant.Health <= 0 {
            // Mark for deletion (don't delete during iteration)
            state.PlantsToDelete = append(state.PlantsToDelete, id)
        }

        break // One reproduction per tick
    }
}
```

### Egg Hatching

```go
func (m *Match) tickEggs(state *WorldState, dt float32) {
    // NOTE: Collect eggs to hatch, don't modify map during iteration
    toHatch := []*EggClusterState{}
    toDelete := []string{}

    for id, eggs := range state.EggClusters {
        eggs.HatchTimer -= dt
        if eggs.HatchTimer <= 0 {
            toHatch = append(toHatch, eggs)
            toDelete = append(toDelete, id)
        }
    }

    // Process hatching after iteration
    for _, eggs := range toHatch {
        m.hatchEggs(state, eggs)
    }
    for _, id := range toDelete {
        delete(state.EggClusters, id)
    }
}

func (m *Match) hatchEggs(state *WorldState, eggs *EggClusterState) {
    species := state.Species[eggs.SpeciesID]

    // Try to merge with nearby swarm of same species (PRIORITY)
    // Uses species-specific merge radius
    for _, swarm := range state.Swarms {
        if swarm.SpeciesID != eggs.SpeciesID {
            continue
        }
        if distBetween(swarm.Position, eggs.Position) <= species.MergeRadius {
            swarm.Count += eggs.Count
            return  // Merged, done
        }
    }

    // No nearby swarm - create new one
    newSwarm := &SwarmState{
        ID:        fmt.Sprintf("swarm_%s", uuid.NewString()[:8]),
        SpeciesID: eggs.SpeciesID,
        Position:  eggs.Position,
        Radius:    species.SwarmRadius,
        Count:     eggs.Count,
        HomePos:   eggs.Position,
        WanderRad: species.WanderRadius,
    }
    state.Swarms[newSwarm.ID] = newSwarm
}
```

### Individual Bug Simulation

```go
func (m *Match) simulateIndividuals(state *WorldState, dt float32) {
    for _, bug := range state.Individuals {
        species := state.Species[bug.SpeciesID]

        // Check for player proximity to trigger reactions
        if bug.State == BugIdle || bug.State == BugWander {
            if target := findNearestPlayer(state, bug.Position, species.ReactionRadius); target != nil {
                switch species.PlayerReaction {
                case "attack":
                    bug.State = BugAlert
                case "flee":
                    bug.State = BugFlee
                    bug.TargetID = target.UserID
                    bug.PathPoints = generateFleePath(bug.Position, target.Position)
                    bug.PathT = 0
                // "ignore" and "curious" don't change state
                }
            }
        }

        switch bug.State {
        case BugIdle:
            if rand.Float32() < 0.02 {
                bug.State = BugWander
                bug.PathPoints = generateWanderPath(bug.Position, species.WanderRadius)
                bug.PathT = 0
            }

        case BugWander:
            bug.PathT += bug.Speed * dt
            if bug.PathT >= 1.0 {
                bug.State = BugIdle
                bug.PathT = 1.0
            }
            bug.Position = evaluateBezier(bug.PathPoints, bug.PathT)

        case BugAlert:
            if target := findNearestPlayer(state, bug.Position, species.ReactionRadius); target != nil {
                bug.State = BugChase
                bug.TargetID = target.UserID
                bug.PathPoints = generateChasePath(bug.Position, target.Position)
                bug.PathT = 0
            } else {
                bug.State = BugIdle
            }

        case BugChase:
            bug.PathT += bug.Speed * dt * 1.5
            if bug.PathT >= 1.0 {
                if target := state.Players[bug.TargetID]; target != nil {
                    bug.PathPoints = generateChasePath(bug.Position, target.Position)
                    bug.PathT = 0
                } else {
                    bug.State = BugIdle
                }
            }
            bug.Position = evaluateBezier(bug.PathPoints, bug.PathT)

        case BugFlee:
            bug.PathT += bug.Speed * dt * species.FleeSpeedMult
            if bug.PathT >= 1.0 {
                // Check if player still nearby
                if target := state.Players[bug.TargetID]; target != nil {
                    dist := distBetween(bug.Position, target.Position)
                    if dist < species.ReactionRadius {
                        // Still too close, keep fleeing
                        bug.PathPoints = generateFleePath(bug.Position, target.Position)
                        bug.PathT = 0
                    } else {
                        // Escaped, go idle
                        bug.State = BugIdle
                    }
                } else {
                    bug.State = BugIdle
                }
            }
            bug.Position = evaluateBezier(bug.PathPoints, bug.PathT)
        }

        bug.Position.Normalize(state.Config.ChunkSize)
        bug.Facing = pathToDirection(bug.PathPoints, bug.PathT)
    }
}

// Generate path moving away from target
func generateFleePath(from, targetPos EntityPosition) []Vec2 {
    // Calculate direction away from target
    dx := from.LocalX - targetPos.LocalX
    dy := from.LocalY - targetPos.LocalY
    dist := float32(math.Sqrt(float64(dx*dx + dy*dy)))
    if dist < 0.1 {
        dist = 1.0
    }

    // Normalize and extend
    fleeX := from.LocalX + (dx/dist)*8.0
    fleeY := from.LocalY + (dy/dist)*8.0

    // Generate bezier curve away
    return []Vec2{
        {from.LocalX, from.LocalY},
        {from.LocalX + dx/dist*4, from.LocalY + dy/dist*4},
        {fleeX, fleeY},
    }
}

// Evaluate quadratic Bezier curve at parameter t (0-1)
func evaluateBezier(points []Vec2, t float32) EntityPosition {
    if len(points) < 3 {
        return EntityPosition{} // Need at least 3 control points
    }

    // Quadratic bezier: B(t) = (1-t)²*P0 + 2(1-t)t*P1 + t²*P2
    oneMinusT := 1 - t
    x := oneMinusT*oneMinusT*points[0].X + 2*oneMinusT*t*points[1].X + t*t*points[2].X
    y := oneMinusT*oneMinusT*points[0].Y + 2*oneMinusT*t*points[1].Y + t*t*points[2].Y

    return EntityPosition{LocalX: x, LocalY: y}
}

// Generate random wander path within wander radius
func generateWanderPath(from EntityPosition, wanderRadius float32) []Vec2 {
    // Random angle and distance
    angle := rand.Float32() * 2 * math.Pi
    dist := rand.Float32() * wanderRadius

    targetX := from.LocalX + float32(math.Cos(float64(angle)))*dist
    targetY := from.LocalY + float32(math.Sin(float64(angle)))*dist

    // Control point at midpoint with slight offset
    midX := (from.LocalX + targetX) / 2 + (rand.Float32()-0.5)*2
    midY := (from.LocalY + targetY) / 2 + (rand.Float32()-0.5)*2

    return []Vec2{
        {from.LocalX, from.LocalY},
        {midX, midY},
        {targetX, targetY},
    }
}

// Generate path toward target with slight curve
func generateChasePath(from, target EntityPosition) []Vec2 {
    // Direction to target
    dx := target.LocalX - from.LocalX
    dy := target.LocalY - from.LocalY

    // Control point perpendicular to path for natural curve
    perpX := -dy * 0.3 * (rand.Float32() - 0.5)
    perpY := dx * 0.3 * (rand.Float32() - 0.5)
    midX := (from.LocalX+target.LocalX)/2 + perpX
    midY := (from.LocalY+target.LocalY)/2 + perpY

    return []Vec2{
        {from.LocalX, from.LocalY},
        {midX, midY},
        {target.LocalX, target.LocalY},
    }
}

// Convert path direction to facing Direction
func pathToDirection(points []Vec2, t float32) Direction {
    if len(points) < 2 {
        return DirectionDown
    }

    // Get tangent at current position (derivative of bezier)
    oneMinusT := 1 - t
    dx := 2*oneMinusT*(points[1].X-points[0].X) + 2*t*(points[2].X-points[1].X)
    dy := 2*oneMinusT*(points[1].Y-points[0].Y) + 2*t*(points[2].Y-points[1].Y)

    // Convert to cardinal direction
    if math.Abs(float64(dx)) > math.Abs(float64(dy)) {
        if dx > 0 {
            return DirectionRight
        }
        return DirectionLeft
    }
    if dy > 0 {
        return DirectionUp
    }
    return DirectionDown
}
```

### Plant & Seed System

#### Ground Item Ticks

```go
func (m *Match) tickGroundItems(state *WorldState, dt float32) {
    for id, item := range state.GroundItems {
        item.Lifetime -= dt
        if item.Lifetime <= 0 {
            delete(state.GroundItems, id)
        }
    }
}

func (m *Match) checkItemPickups(state *WorldState, dispatcher runtime.MatchDispatcher) {
    pickupRadius := float32(1.5) // blocks

    for itemID, item := range state.GroundItems {
        itemX := float32(item.Position.ChunkX)*float32(state.Config.ChunkSize) + item.Position.LocalX
        itemY := float32(item.Position.ChunkY)*float32(state.Config.ChunkSize) + item.Position.LocalY

        for playerID, player := range state.Players {
            playerX := float32(player.Position.ChunkX)*float32(state.Config.ChunkSize) + player.Position.LocalX
            playerY := float32(player.Position.ChunkY)*float32(state.Config.ChunkSize) + player.Position.LocalY

            dx := itemX - playerX
            dy := itemY - playerY
            if dx*dx + dy*dy <= pickupRadius*pickupRadius {
                // Add to player inventory
                player.AddToInventory(item.ItemType, 1)

                // Notify player of inventory update
                invMsg := InventoryUpdateMessage{
                    Species: item.ItemType,
                    Count:   player.Inventory[item.ItemType],
                }
                invData, _ := json.Marshal(invMsg)
                dispatcher.BroadcastMessage(OpCodeInventoryUpdate, invData,
                    []runtime.Presence{{UserID: playerID}}, nil, true)

                // Broadcast pickup for visual feedback
                pickupMsg := ItemPickedUpMessage{
                    ItemID:   itemID,
                    PlayerID: playerID,
                    ItemType: item.ItemType,
                }
                pickupData, _ := json.Marshal(pickupMsg)
                dispatcher.BroadcastMessage(OpCodeItemPickedUp, pickupData, nil, nil, true)

                // Remove from ground
                delete(state.GroundItems, itemID)
                break // Item picked up, move to next
            }
        }
    }
}
```

#### Plant Respawn

```go
func (m *Match) tickPlantRespawn(state *WorldState) {
    if len(state.Plants) >= state.Config.MaxPlantCount {
        return
    }

    // Low chance per tick (~1% = roughly 1 plant every 10 seconds at 10Hz)
    if rand.Float32() > 0.01 {
        return
    }

    // Weighted random plant type selection
    plantType := selectWeightedPlantType(state.PlantDefs)
    plantDef := state.PlantDefs[plantType]

    // Random position (try a few times to find unoccupied cell)
    for attempts := 0; attempts < 5; attempts++ {
        x := rand.Intn(state.Config.WorldSizeBlocks)
        y := rand.Intn(state.Config.WorldSizeBlocks)
        cell := Vec2Int{x, y}

        if state.OccupiedCells[cell] != "" {
            continue // Cell occupied
        }

        // Spawn plant
        plant := &PlantState{
            ID:        fmt.Sprintf("plant_%s", uuid.NewString()[:8]),
            PlantType: plantType,
            Position:  EntityPosition{LocalX: float32(x), LocalY: float32(y)},
            Health:    plantDef.Health,
        }
        state.Plants[plant.ID] = plant
        state.OccupiedCells[cell] = plant.ID
        return
    }
}

func selectWeightedPlantType(defs map[string]*PlantDef) string {
    // Calculate total weight
    totalWeight := float32(0)
    for _, def := range defs {
        totalWeight += def.SpawnWeight
    }

    // Random selection
    roll := rand.Float32() * totalWeight
    cumulative := float32(0)
    for plantType, def := range defs {
        cumulative += def.SpawnWeight
        if roll <= cumulative {
            return plantType
        }
    }

    // Fallback (shouldn't happen)
    for plantType := range defs {
        return plantType
    }
    return ""
}
```

#### Plant Seed Handler

```go
func (m *Match) handlePlantSeed(
    ctx context.Context,
    state *WorldState,
    msg PlantSeedMessage,
    playerID string,
    dispatcher runtime.MatchDispatcher,
) {
    player, exists := state.Players[playerID]
    if !exists {
        return
    }

    // Check player has seed in inventory
    if player.Inventory[msg.SeedType] <= 0 {
        return
    }

    // Find plant definition for this seed type
    var plantDef *PlantDef
    var plantType string
    for ptype, def := range state.PlantDefs {
        if def.SeedType == msg.SeedType {
            plantDef = def
            plantType = ptype
            break
        }
    }
    if plantDef == nil {
        return // Unknown seed type
    }

    // Check position is valid (grid cell not occupied)
    gridX := int(msg.X)
    gridY := int(msg.Y)
    cell := Vec2Int{gridX, gridY}
    if state.OccupiedCells[cell] != "" {
        return // Cell occupied
    }

    // Check player is in range (4 blocks)
    playerX := float32(player.Position.ChunkX)*float32(state.Config.ChunkSize) + player.Position.LocalX
    playerY := float32(player.Position.ChunkY)*float32(state.Config.ChunkSize) + player.Position.LocalY
    dx := msg.X - playerX
    dy := msg.Y - playerY
    if dx*dx + dy*dy > 16 { // 4^2
        return // Too far
    }

    // Remove seed from inventory
    player.Inventory[msg.SeedType]--

    // Create plant
    plant := &PlantState{
        ID:        fmt.Sprintf("plant_%s", uuid.NewString()[:8]),
        PlantType: plantType,
        Position:  EntityPosition{LocalX: float32(gridX), LocalY: float32(gridY)},
        Health:    plantDef.Health,
    }
    state.Plants[plant.ID] = plant
    state.OccupiedCells[cell] = plant.ID

    // Notify player of inventory update
    invMsg := InventoryUpdateMessage{
        Species: msg.SeedType,
        Count:   player.Inventory[msg.SeedType],
    }
    invData, _ := json.Marshal(invMsg)
    dispatcher.BroadcastMessage(OpCodeInventoryUpdate, invData,
        []runtime.Presence{{UserID: playerID}}, nil, true)

    // Broadcast plant creation
    plantedMsg := SeedPlantedMessage{
        PlantID:   plant.ID,
        PlantType: plantType,
        X:         float32(gridX),
        Y:         float32(gridY),
    }
    plantedData, _ := json.Marshal(plantedMsg)
    dispatcher.BroadcastMessage(OpCodeSeedPlanted, plantedData, nil, nil, true)
}
```

---

## Client Implementation

### Architecture Overview

```
WorldManager
    ├── OnSwarmUpdate (OpCode 20) → BugManager.HandleSwarms()
    ├── OnEggUpdate (OpCode 21) → BugManager.HandleEggs()
    ├── OnIndividualUpdate (OpCode 22) → BugManager.HandleIndividuals()
    ├── OnPlantUpdate (OpCode 23) → PlantManager.HandlePlants()
    ├── OnBugCaught (OpCode 25) → BugManager.HandleCaught()
    ├── OnInventoryUpdate (OpCode 26) → InventoryManager.HandleUpdate()
    ├── OnBugConditionUpdate (OpCode 28) → BugManager.HandleConditionUpdate()
    ├── OnSeedPlanted (OpCode 34) → PlantManager.HandleSeedPlanted()
    ├── OnGroundItemUpdate (OpCode 35) → ItemManager.HandleGroundItems()
    └── OnItemPickedUp (OpCode 36) → ItemManager.HandlePickup()

BugManager (Singleton)
    ├── Dictionary<string, SwarmVisual> _swarms
    ├── Dictionary<string, EggClusterVisual> _eggs
    ├── Dictionary<string, IndividualBugVisual> _individuals
    ├── Object pool for fly GameObjects
    └── Handles spawning, updating, destroying

SwarmVisual
    ├── List<FlyBehavior> _flies (local instances from pool)
    ├── Interpolates swarm center position
    ├── Shows net animation on catches (for other players)
    └── Adjusts fly count on updates
```

### SwarmVisual with Activity Indicator

**File:** `Assets/Scripts/Entities/SwarmVisual.cs`

```csharp
public class SwarmVisual : MonoBehaviour
{
    public string SwarmID { get; private set; }

    [SerializeField] private GameObject activityIndicatorPrefab;
    [SerializeField] private GameObject flyPrefab;

    private List<FlyBehavior> _flies = new();
    private Vector2 _targetCenter;
    private float _radius;
    private GameObject _activityIndicator;
    private Coroutine _hideActivityCoroutine;

    public void UpdateFromServer(SwarmData data, Sprite bugSprite)
    {
        SwarmID = data.id;
        _targetCenter = new Vector2(data.x, data.y);
        _radius = data.radius;

        AdjustFlyCount(Mathf.Min(data.count, BugManager.Instance.MaxFliesPerSwarm));

        foreach (var fly in _flies)
        {
            fly.GetComponent<SpriteRenderer>().sprite = bugSprite;
        }
    }

    public void ShowCatchAnimation(Vector2 catchPos, string catcherID)
    {
        // Don't show net for local player (they have their own animation)
        // Note: Use WorldManager.Self.UserId, not Session (which is async)
        if (catcherID == WorldManager.Instance.Self?.UserId)
            return;

        // Show net icon at catch position
        if (_activityIndicator == null)
        {
            _activityIndicator = Instantiate(activityIndicatorPrefab, transform);
        }
        _activityIndicator.transform.position = catchPos;
        _activityIndicator.SetActive(true);

        // Hide after short delay using coroutine (Unity 6 best practice)
        if (_hideActivityCoroutine != null)
            StopCoroutine(_hideActivityCoroutine);
        _hideActivityCoroutine = StartCoroutine(HideActivityAfterDelay(0.5f));
    }

    private IEnumerator HideActivityAfterDelay(float delay)
    {
        yield return new WaitForSeconds(delay);
        if (_activityIndicator != null)
            _activityIndicator.SetActive(false);
        _hideActivityCoroutine = null;
    }

    /// <summary>
    /// Remove multiple random flies (called when BugEffect with count_delta received)
    /// </summary>
    public void RemoveRandomFlies(int count)
    {
        for (int i = 0; i < count && _flies.Count > 0; i++)
        {
            int idx = Random.Range(0, _flies.Count);
            Vector3 flyPos = _flies[idx].transform.position;

            // Return to pool instead of destroying
            BugManager.Instance.ReturnFlyToPool(_flies[idx].gameObject);
            _flies.RemoveAt(idx);

            // Play poof effect at fly's last position
            PlayPoofEffect(flyPos);
        }
    }

    /// <summary>
    /// Set fly count to match server authority (handles both add/remove)
    /// </summary>
    public void SetCount(int targetCount)
    {
        AdjustFlyCount(Mathf.Min(targetCount, BugManager.Instance.MaxFliesPerSwarm));
    }

    private void AdjustFlyCount(int targetCount)
    {
        // Add flies if needed
        while (_flies.Count < targetCount)
        {
            var flyGO = BugManager.Instance.GetFlyFromPool();
            if (flyGO == null)
                break; // Pool exhausted, can't add more

            flyGO.transform.SetParent(transform);
            Vector2 offset = Random.insideUnitCircle * _radius;
            flyGO.transform.localPosition = offset;

            var fly = flyGO.GetComponent<FlyBehavior>();
            fly.ResetForPool(); // Reset state from previous use
            fly.SetHomePosition(transform.position + (Vector3)offset);
            fly.SetWanderRadius(_radius);
            _flies.Add(fly);
        }

        // Remove excess flies
        while (_flies.Count > targetCount)
        {
            int idx = _flies.Count - 1;
            BugManager.Instance.ReturnFlyToPool(_flies[idx].gameObject);
            _flies.RemoveAt(idx);
        }
    }

    private void Update()
    {
        // Smoothly interpolate swarm center
        transform.position = Vector2.Lerp(transform.position, _targetCenter, 5f * Time.deltaTime);
    }

    private void PlayPoofEffect(Vector3 position)
    {
        // TODO: Instantiate poof particle effect
    }

    private void OnDestroy()
    {
        // Return all flies to pool
        foreach (var fly in _flies)
        {
            if (fly != null)
                BugManager.Instance.ReturnFlyToPool(fly.gameObject);
        }
        _flies.Clear();
    }
}
```

### BugCatcher - AoE Net Swing

**File:** `Assets/Scripts/Player/BugCatcher.cs`

```csharp
/// <summary>
/// Handles player clicking to swing net. Uses AoE - server determines what gets caught.
/// </summary>
public class BugCatcher : MonoBehaviour
{
    [SerializeField] private GameObject netSwingEffectPrefab;
    [SerializeField] private float catchCooldown = 0.2f;

    private Camera _camera;
    private float _lastSwingTime;

    // Net radius lookup (matches server)
    private static readonly Dictionary<string, float> NetRadii = new()
    {
        { "net_small", 1.5f },
        { "net_medium", 2.5f },
        { "net_large", 4.0f }
    };

    private void Awake()
    {
        _camera = Camera.main;
    }

    private void Update()
    {
        if (Input.GetMouseButtonDown(0) && Time.time - _lastSwingTime > catchCooldown)
        {
            TrySwingNet();
        }
    }

    private void TrySwingNet()
    {
        // Check if we have a net equipped
        string tool = PlayerState.EquippedTool;
        if (!NetRadii.TryGetValue(tool, out float radius))
            return; // No net equipped

        if (_camera == null)
        {
            Debug.LogWarning("[BugCatcher] No main camera found");
            return;
        }

        Vector3 worldPos = _camera.ScreenToWorldPoint(Input.mousePosition);
        worldPos.z = 0;

        _lastSwingTime = Time.time;

        // Show immediate visual feedback (local net swing effect)
        ShowNetSwingEffect(worldPos, radius);

        // Send AoE catch request to server (no target_id, just position)
        SendCatchRequest(worldPos);
    }

    private void ShowNetSwingEffect(Vector3 position, float radius)
    {
        if (netSwingEffectPrefab != null)
        {
            var effect = Instantiate(netSwingEffectPrefab, position, Quaternion.identity);
            effect.transform.localScale = Vector3.one * radius * 2;
            Destroy(effect, 0.3f);
        }
    }

    private void SendCatchRequest(Vector2 clickPos)
    {
        var world = WorldManager.Instance;
        if (world?.CurrentMatch == null) return;

        var socket = NetworkManager.Instance?.Socket;
        if (socket == null || !socket.IsConnected) return;

        var msg = new CatchBugMessage
        {
            click_x = clickPos.x,
            click_y = clickPos.y
        };
        var json = JsonUtility.ToJson(msg);

        _ = socket.SendMatchStateAsync(world.CurrentMatch.Id, OpCodes.CatchBug, json);
    }
}
```

### BugManager Handling Catches

**File:** `Assets/Scripts/Entities/BugManager.cs`

```csharp
public class BugManager : MonoBehaviour
{
    public static BugManager Instance { get; private set; }

    [Header("Prefabs")]
    [SerializeField] private GameObject swarmPrefab;
    [SerializeField] private GameObject flyPrefab;

    [Header("Pooling")]
    [SerializeField] private int initialPoolSize = 200;
    public int MaxFliesPerSwarm => 50;
    public int MaxTotalFlies => 500;

    private Dictionary<string, SwarmVisual> _swarms = new();
    private Queue<GameObject> _flyPool = new();
    private int _activeFlyCount = 0;

    private void Awake()
    {
        Instance = this;
        InitializeFlyPool();
    }

    private void InitializeFlyPool()
    {
        for (int i = 0; i < initialPoolSize; i++)
        {
            var fly = Instantiate(flyPrefab);
            fly.SetActive(false);
            _flyPool.Enqueue(fly);
        }
    }

    public GameObject GetFlyFromPool()
    {
        if (_activeFlyCount >= MaxTotalFlies)
            return null;

        GameObject fly;
        if (_flyPool.Count > 0)
        {
            fly = _flyPool.Dequeue();
        }
        else
        {
            fly = Instantiate(flyPrefab);
        }
        fly.SetActive(true);
        _activeFlyCount++;
        return fly;
    }

    public void ReturnFlyToPool(GameObject fly)
    {
        fly.SetActive(false);
        fly.transform.SetParent(transform);
        _flyPool.Enqueue(fly);
        _activeFlyCount--;
    }

    /// <summary>
    /// Handle unified BugEffect message (replaces old HandleCaught)
    /// </summary>
    public void HandleBugEffect(BugEffect effect)
    {
        // Play visual at effect position
        BugEffectHandler.Instance?.PlayVisual(effect);

        if (effect.target_type == "swarm")
        {
            if (_swarms.TryGetValue(effect.target_id, out var swarm))
            {
                switch (effect.effect_type)
                {
                    case "catch":
                        // Remove random flies based on count_delta
                        swarm.RemoveRandomFlies(-effect.count_delta);

                        if (effect.new_count <= 0)
                        {
                            Destroy(swarm.gameObject);
                            _swarms.Remove(effect.target_id);
                        }
                        break;

                    case "smoke":
                    case "stun":
                        swarm.SetCondition(effect.new_condition);
                        break;

                    case "spawn":
                        swarm.SetCount(effect.new_count);
                        break;
                }
            }
        }
        else // target_type == "bug"
        {
            if (_individuals.TryGetValue(effect.target_id, out var individual))
            {
                switch (effect.effect_type)
                {
                    case "catch":
                        if (effect.removed)
                        {
                            // Individual is caught - remove it
                            Destroy(individual.gameObject);
                            _individuals.Remove(effect.target_id);
                        }
                        break;

                    case "damage":
                        individual.TakeDamage(-effect.condition_delta);
                        break;

                    case "stun":
                        individual.ApplyStun(effect.new_condition);
                        break;
                }
            }
        }
    }

    public void HandleSwarms(SwarmUpdateMessage update)
    {
        var updated = new HashSet<string>();
        foreach (var data in update.swarms)
        {
            updated.Add(data.id);
            if (!_swarms.TryGetValue(data.id, out var visual))
            {
                var go = Instantiate(swarmPrefab);
                visual = go.GetComponent<SwarmVisual>();
                _swarms[data.id] = visual;
            }
            visual.UpdateFromServer(data, GetSpeciesSprite(data.species));
        }

        // Remove stale swarms
        var toRemove = new List<string>();
        foreach (var kvp in _swarms)
        {
            if (!updated.Contains(kvp.Key))
                toRemove.Add(kvp.Key);
        }
        foreach (var id in toRemove)
        {
            Destroy(_swarms[id].gameObject);
            _swarms.Remove(id);
        }
    }

    private Sprite GetSpeciesSprite(string speciesId)
    {
        // TODO: Load from species sprite map
        return null;
    }
}
```

### BugEffectHandler - Unified Visual Effects

**File:** `Assets/Scripts/Entities/BugEffectHandler.cs`

```csharp
/// <summary>
/// Handles visual effects for all bug interactions.
/// Extensible - add new effect_types by adding prefabs and switch cases.
/// </summary>
public class BugEffectHandler : MonoBehaviour
{
    public static BugEffectHandler Instance { get; private set; }

    [SerializeField] private GameObject catchEffectPrefab;
    [SerializeField] private GameObject smokeEffectPrefab;
    [SerializeField] private GameObject stunEffectPrefab;
    [SerializeField] private GameObject damageEffectPrefab;

    private void Awake() => Instance = this;

    public void PlayVisual(BugEffect effect)
    {
        var prefab = effect.effect_type switch
        {
            "catch" => catchEffectPrefab,
            "smoke" => smokeEffectPrefab,
            "stun" => stunEffectPrefab,
            "damage" => damageEffectPrefab,
            _ => null
        };

        if (prefab != null)
        {
            var vfx = Instantiate(prefab, new Vector3(effect.x, effect.y, 0), Quaternion.identity);
            Destroy(vfx, 0.5f);
        }
    }
}
```

### CatchFeedback - Player Feedback Popups

**File:** `Assets/Scripts/UI/CatchFeedback.cs`

```csharp
/// <summary>
/// Shows popup feedback when catching (or failing to catch) bugs.
/// Receives CatchResult messages from server.
/// </summary>
public class CatchFeedback : MonoBehaviour
{
    public static CatchFeedback Instance { get; private set; }

    [SerializeField] private GameObject feedbackPopupPrefab;

    private void Awake() => Instance = this;

    public void ShowResult(CatchResult msg)
    {
        Vector3 pos = new Vector3(msg.x, msg.y, 0);

        if (msg.total_caught > 0)
        {
            // Success popup
            ShowPopup(pos, $"+{msg.total_caught}", Color.green);
        }
        else if (msg.reasons != null && msg.reasons.Length > 0)
        {
            // Failure popup with reason
            string text = ParseReason(msg.reasons[0]);
            ShowPopup(pos, text, Color.red);
        }
    }

    private void ShowPopup(Vector3 position, string text, Color color)
    {
        if (feedbackPopupPrefab == null) return;

        var popup = Instantiate(feedbackPopupPrefab, position, Quaternion.identity);
        var tmp = popup.GetComponent<TMPro.TMP_Text>();
        if (tmp != null)
        {
            tmp.text = text;
            tmp.color = color;
        }
        Destroy(popup, 1.5f);
    }

    private string ParseReason(string reason) => reason switch
    {
        "miss" => "Missed!",
        var r when r.StartsWith("wrong_net:") => $"Wrong net for {r[10..]}!",
        var r when r.StartsWith("condition:") => r[10..] switch
        {
            "calm" => "Too alert!",
            "stunned" => "Not stunned!",
            "weakened" => "Too strong!",
            _ => "Can't catch!"
        },
        _ => "Can't catch!"
    };
}
```

### FlyBehavior Modifications

**File:** `Assets/Scripts/Entities/FlyBehavior.cs`

Add collider for click detection and configurable wander radius:

```csharp
public class FlyBehavior : MonoBehaviour
{
    [SerializeField] private float speed = 2f;
    [SerializeField] private float directionChangeInterval = 0.3f;
    [SerializeField] private float smoothing = 5f;
    [SerializeField] private float wanderRadius = 5f;

    private Vector2 _targetDirection;
    private Vector2 _currentDirection;
    private Vector2 _startPosition;
    private float _directionTimer;

    private void Start()
    {
        _startPosition = transform.position;
        PickNewDirection();

        // Ensure collider exists for click detection
        var collider = GetComponent<CircleCollider2D>();
        if (collider == null)
        {
            collider = gameObject.AddComponent<CircleCollider2D>();
            collider.radius = 0.3f;
            collider.isTrigger = true; // Don't block physics
        }
    }

    // ... existing Update, PickNewDirection methods ...

    /// <summary>
    /// Set the center point for wandering (called by spawner/pool).
    /// </summary>
    public void SetHomePosition(Vector2 pos)
    {
        _startPosition = pos;
    }

    /// <summary>
    /// Set maximum wander distance from home (called by SwarmVisual).
    /// </summary>
    public void SetWanderRadius(float radius)
    {
        wanderRadius = radius;
    }

    /// <summary>
    /// Reset state when retrieved from pool.
    /// </summary>
    public void ResetForPool()
    {
        _directionTimer = 0f;
        _currentDirection = Vector2.zero;
        PickNewDirection();
    }
}
```

---

## Configuration

### Server Config

```go
type WorldConfig struct {
    // ... existing fields ...
    InitialSwarmCount int     // Default: 200
    InitialPlantCount int     // Default: 100
    ViewDistance      int     // Default: 2 chunks
    WorldSizeBlocks   int     // World dimensions in blocks
    // NOTE: SwarmMergeRadius and MaxSwarmSize are now per-species in species.json
}
```

### Spawn Initialization

Called during match initialization to populate the world:

```go
// File: nakama/modules/world/spawner.go

func (m *Match) SpawnInitialEntities(state *WorldState) {
    // Collect swarm species for weighted spawning
    swarmSpecies := []*BugSpecies{}
    for _, spec := range state.Species {
        if spec.Category == "swarm" {
            swarmSpecies = append(swarmSpecies, spec)
        }
    }

    // Spawn initial swarms distributed across the world
    for i := 0; i < state.Config.InitialSwarmCount; i++ {
        // Random species (equal weight for now)
        spec := swarmSpecies[rand.Intn(len(swarmSpecies))]

        // Random position within world bounds
        x := rand.Float32() * float32(state.Config.WorldSizeBlocks)
        y := rand.Float32() * float32(state.Config.WorldSizeBlocks)

        // Random count within species range
        count := spec.MinSwarmSize + rand.Intn(spec.MaxSwarmSize-spec.MinSwarmSize+1)

        swarm := &SwarmState{
            ID:         fmt.Sprintf("swarm_%s", uuid.NewString()[:8]),
            SpeciesID:  spec.ID,
            Position:   EntityPosition{LocalX: x, LocalY: y},
            Radius:     spec.SwarmRadius,
            Count:      count,
            HomePos:    EntityPosition{LocalX: x, LocalY: y},
            WanderRad:  spec.WanderRadius,
            CurrentHP:  spec.MaxHP,
        }
        state.Swarms[swarm.ID] = swarm
    }

    // Spawn initial plants
    plantTypes := []string{"rotting_fruit", "flower", "leaf_pile"}
    for i := 0; i < state.Config.InitialPlantCount; i++ {
        x := rand.Intn(state.Config.WorldSizeBlocks)
        y := rand.Intn(state.Config.WorldSizeBlocks)

        // Skip if cell already occupied
        cell := Vec2Int{x, y}
        if state.OccupiedCells[cell] != "" {
            continue
        }

        plantType := plantTypes[rand.Intn(len(plantTypes))]
        plant := &PlantState{
            ID:        fmt.Sprintf("plant_%s", uuid.NewString()[:8]),
            PlantType: plantType,
            Position:  EntityPosition{LocalX: float32(x), LocalY: float32(y)},
            Health:    3, // Can support 3 breeding cycles
        }
        state.Plants[plant.ID] = plant

        // Mark cell as occupied
        state.OccupiedCells[cell] = plant.ID
    }
}

// Helper to remove plant, drop seed, and free occupied cells
func (m *Match) removePlant(state *WorldState, plantID string) {
    plant, exists := state.Plants[plantID]
    if !exists {
        return
    }

    // Drop seed as ground item if configured
    if plantDef, ok := state.PlantDefs[plant.PlantType]; ok {
        if plantDef.DropsSeed && plantDef.SeedType != "" {
            item := &GroundItem{
                ID:       fmt.Sprintf("item_%s", uuid.NewString()[:8]),
                ItemType: plantDef.SeedType,
                Position: plant.Position,
                Lifetime: 60.0, // 60 seconds to pick up
            }
            state.GroundItems[item.ID] = item
        }
    }

    // Free the occupied cell
    cell := Vec2Int{int(plant.Position.LocalX), int(plant.Position.LocalY)}
    delete(state.OccupiedCells, cell)

    // Remove the plant
    delete(state.Plants, plantID)
}
```

### Species Config (JSON)

```json
{
  "fly": {
    "name": "Common Fly",
    "category": "swarm",
    "base_speed": 1.5,
    "wander_radius": 8.0,
    "min_swarm_size": 30,
    "max_swarm_size": 100,
    "swarm_radius": 4.0,
    "merge_radius": 8.0,
    "split_threshold": 80,
    "split_chance": 0.01,
    "player_reaction": "ignore",
    "reaction_radius": 0,
    "flee_speed_mult": 1.0,
    "attack_damage": 0,
    "attack_cooldown": 0,
    "net_size": "small",
    "catch_condition": "always",
    "condition_threshold": 0,
    "condition_decay": 0,
    "condition_tools": {},
    "max_hp": 0,
    "damage_tools": {},
    "sell_price": 1,
    "breeding_plants": ["rotting_fruit"],
    "egg_count_min": 20,
    "egg_count_max": 40,
    "hatch_time": 30.0,
    "reproduce_cooldown": 30.0,
    "sprite_id": "fly",
    "egg_sprite_id": "fly_eggs"
  },
  "bee": {
    "name": "Honey Bee",
    "category": "swarm",
    "base_speed": 2.0,
    "wander_radius": 10.0,
    "min_swarm_size": 20,
    "max_swarm_size": 80,
    "swarm_radius": 3.0,
    "merge_radius": 6.0,
    "split_threshold": 60,
    "split_chance": 0.02,
    "player_reaction": "attack",
    "reaction_radius": 5.0,
    "flee_speed_mult": 1.0,
    "attack_damage": 5,
    "attack_cooldown": 1.0,
    "net_size": "small",
    "catch_condition": "calm",
    "condition_threshold": 80,
    "condition_decay": 5.0,
    "condition_tools": {
      "smoke_gun": 30,
      "incense": 10
    },
    "max_hp": 0,
    "damage_tools": {},
    "sell_price": 5,
    "breeding_plants": ["flower"],
    "egg_count_min": 10,
    "egg_count_max": 25,
    "hatch_time": 45.0,
    "reproduce_cooldown": 60.0,
    "sprite_id": "bee",
    "egg_sprite_id": "bee_eggs"
  },
  "ant": {
    "name": "Worker Ant",
    "category": "swarm",
    "base_speed": 1.0,
    "wander_radius": 12.0,
    "min_swarm_size": 50,
    "max_swarm_size": 200,
    "swarm_radius": 2.0,
    "merge_radius": 5.0,
    "split_threshold": 150,
    "split_chance": 0.01,
    "player_reaction": "flee",
    "reaction_radius": 3.0,
    "flee_speed_mult": 1.5,
    "attack_damage": 0,
    "attack_cooldown": 0,
    "net_size": "small",
    "catch_condition": "distracted",
    "condition_threshold": 50,
    "condition_decay": 8.0,
    "condition_tools": {
      "bait": 40,
      "sugar_trap": 60
    },
    "max_hp": 0,
    "damage_tools": {},
    "sell_price": 2,
    "breeding_plants": ["leaf_pile"],
    "egg_count_min": 30,
    "egg_count_max": 60,
    "hatch_time": 20.0,
    "reproduce_cooldown": 40.0,
    "sprite_id": "ant",
    "egg_sprite_id": "ant_eggs"
  },
  "beetle": {
    "name": "Beetle",
    "category": "individual",
    "base_speed": 0.8,
    "wander_radius": 10.0,
    "min_swarm_size": 1,
    "max_swarm_size": 1,
    "swarm_radius": 0,
    "merge_radius": 0,
    "split_threshold": 0,
    "split_chance": 0,
    "player_reaction": "flee",
    "reaction_radius": 6.0,
    "flee_speed_mult": 2.0,
    "attack_damage": 0,
    "attack_cooldown": 0,
    "net_size": "medium",
    "catch_condition": "stunned",
    "condition_threshold": 60,
    "condition_decay": 10.0,
    "condition_tools": {
      "stun_prod": 50,
      "trap": 30
    },
    "max_hp": 0,
    "damage_tools": {},
    "sell_price": 50,
    "breeding_plants": ["rotting_fruit", "leaf_pile"],
    "egg_count_min": 3,
    "egg_count_max": 8,
    "hatch_time": 60.0,
    "reproduce_cooldown": 120.0,
    "sprite_id": "beetle",
    "egg_sprite_id": "beetle_eggs"
  },
  "giant_beetle": {
    "name": "Giant Beetle",
    "category": "individual",
    "base_speed": 0.5,
    "wander_radius": 15.0,
    "min_swarm_size": 1,
    "max_swarm_size": 1,
    "swarm_radius": 0,
    "merge_radius": 0,
    "split_threshold": 0,
    "split_chance": 0,
    "player_reaction": "attack",
    "reaction_radius": 10.0,
    "flee_speed_mult": 1.0,
    "attack_damage": 15,
    "attack_cooldown": 2.0,
    "net_size": "large",
    "catch_condition": "weakened",
    "condition_threshold": 0,
    "condition_decay": 0,
    "condition_tools": {},
    "max_hp": 100,
    "damage_tools": {
      "sword": 20,
      "hammer": 35,
      "spear": 25
    },
    "sell_price": 200,
    "breeding_plants": ["giant_mushroom"],
    "egg_count_min": 1,
    "egg_count_max": 3,
    "hatch_time": 120.0,
    "reproduce_cooldown": 300.0,
    "sprite_id": "giant_beetle",
    "egg_sprite_id": "giant_beetle_eggs"
  }
}
```

### Plant Config (JSON)

**File:** `data/plants.json`

```json
{
  "rotting_fruit": {
    "plant_type": "rotting_fruit",
    "seed_type": "fruit_seed",
    "health": 3,
    "drops_seed": true,
    "spawn_weight": 1.0,
    "breed_types": ["fly"]
  },
  "flower": {
    "plant_type": "flower",
    "seed_type": "flower_seed",
    "health": 2,
    "drops_seed": true,
    "spawn_weight": 0.8,
    "breed_types": ["bee", "fly"]
  },
  "leaf_pile": {
    "plant_type": "leaf_pile",
    "seed_type": "",
    "health": 5,
    "drops_seed": false,
    "spawn_weight": 0.5,
    "breed_types": ["ant", "beetle"]
  },
  "oak_tree": {
    "plant_type": "oak_tree",
    "seed_type": "acorn",
    "health": 10,
    "drops_seed": true,
    "spawn_weight": 0.2,
    "breed_types": ["beetle", "ant"]
  }
}
```

---

## Files Summary

### Server (Go) - Create:
| File | Purpose |
|------|---------|
| `nakama/modules/entities/species.go` | BugSpecies struct, LoadSpecies() |
| `nakama/modules/entities/swarm.go` | SwarmState, Vec2, merge/split logic |
| `nakama/modules/entities/eggs.go` | EggClusterState |
| `nakama/modules/entities/individual.go` | IndividualBugState, BugAIState |
| `nakama/modules/entities/plant.go` | PlantState, PlantDef, LoadPlantDefs() |
| `nakama/modules/entities/items.go` | GroundItem |
| `nakama/modules/world/spawner.go` | SpawnInitialSwarms(), SpawnPlants(), tickPlantRespawn() |
| `nakama/data/species.json` | Species definitions |
| `nakama/data/plants.json` | Plant definitions |

### Server (Go) - Modify:
| File | Change |
|------|--------|
| `nakama/modules/world/state.go` | Add Swarms, EggClusters, Individuals, Plants, Species, Inventory, PlantDefs, GroundItems |
| `nakama/modules/world/messages.go` | Add all message structs, OpCodes 20-28, 29-36 |
| `nakama/modules/world/match.go` | Full simulation loop, catch handler, merge/split, item pickups, plant seeds |

### Client (C#) - Create:
| File | Purpose |
|------|---------|
| `Assets/Scripts/Entities/BugManager.cs` | Unified manager + object pooling |
| `Assets/Scripts/Entities/SwarmVisual.cs` | Swarm rendering + net animation |
| `Assets/Scripts/Entities/EggClusterVisual.cs` | Egg cluster rendering |
| `Assets/Scripts/Entities/IndividualBugVisual.cs` | Millipede with segments |
| `Assets/Scripts/Entities/Footprint.cs` | Compound-rect footprint for placement |
| `Assets/Scripts/Entities/ItemManager.cs` | Ground item visuals + pickup feedback |
| `Assets/Scripts/Entities/PlantManager.cs` | Plant visuals + seed planting UI |
| `Assets/Scripts/Player/BugCatcher.cs` | Click-to-catch with animation |
| `Assets/Scripts/UI/InventoryManager.cs` | Bug/seed inventory tracking |

### Client (C#) - Modify:
| File | Change |
|------|--------|
| `Assets/Scripts/Networking/NetworkMessages.cs` | Add all DTOs, OpCodes 20-28, 29-32 |
| `Assets/Scripts/Networking/WorldManager.cs` | Handle OpCodes 20-28, 29-32, add events |
| `Assets/Scripts/Entities/FlyBehavior.cs` | Add collider, SetWanderRadius(), ResetForPool() |

---

## Design Decisions

| Question | Decision | Rationale |
|----------|----------|-----------|
| Swarm management | Merge priority, random split | Keep entity count low |
| Click target | Individual fly sprite | More satisfying interaction |
| Catching feedback | Net animation at catch position | Clear visual feedback; merged into BugCaught message |
| Inventory | Server-authoritative | Prevent cheating, persist properly |
| Egg hatching | Merge nearby first | Natural population dynamics |
| Species data | JSON config | Easy to add new species |
| Object pooling | Client-side fly pool | Reduce GC pressure, smooth performance |
| Delay patterns | Coroutines, not Invoke | Unity 6 best practice, easier to cancel |
| Map iteration safety | Collect IDs, modify after | Go maps can't be modified during iteration |
| Rate limiting | 200ms server, 200ms client | Prevent spam clicks, reduce server load |
| Reproduction cooldown | 30s per swarm | Prevent population explosion |
