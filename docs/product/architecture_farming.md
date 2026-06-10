# BugFarmer Farming System Architecture

## Overview

This document defines the architecture for the farming system in BugFarmer, covering:
- Tilling ground with a hoe
- Planting seeds
- Watering crops (watering can, sprinklers, rain)
- Crop growth and harvesting
- Integration with bug ecology (bugs eating crops)

This integrates with the **Frontier-Gated Deterministic Simulation** system where:
- Clients simulate locally and deterministically
- Server finalizes irreversible world state through sparse, ordered events
- Clients advance only up to the server's published tick frontier
- All events are applied with **end-of-tick (effects-at-(t+1)) semantics** (see below)

---

## Synchronization Architecture

### Definitions (Must Match Code)

| Term | Definition |
|------|------------|
| **Tick Rate** | 10 Hz (100ms per tick) |
| **SimulationTick** | Client: "I have simulated through this tick already" |
| **AuthoritativeTick** | Server frontier: "All events for ticks ≤ this are finalized" |
| **Global Ordering** | Events ordered by `(tick, seq)` where `seq` is strictly increasing per zone |

### Event Timing Semantics (CRITICAL)

**Rule: Events with tick T are applied at the END of tick T, after simulating T and
before simulating T+1. Their effects are first visible in tick T+1 (effects-at-(t+1)).**

This is what `SwarmManager.AdvanceOneTick()` actually does, in both LIVE and REPLAY (they
share the same code path, so the semantics are identical and cross-client consistent):

```
AdvanceOneTick():
  → ProcessEventsForTick(simTick)   // apply all events stamped tick == simTick
  → simTick++                       // now entering the next tick
  → Simulate(simTick)               // event effects are visible here (T+1)
```

```
Client holds Event(tick=T)
  → Finishes simulating tick T
  → Applies Event(T) at end of tick T
  → Simulates tick T+1 using updated state
  → Event effects are visible starting at tick T+1
```

This applies to ALL events:
- `BUG_REMOVED` - bug is gone from tick T+1 onward
- `SWARM_SET_TARGET` - new center leg takes effect from tick T+1 onward
- `PLANT_WATER_COMMIT` - water level updated for tick T+1
- `PLANT_DAMAGE_COMMIT` - HP updated for tick T+1
- `PLANT_STAGE_COMMIT` - stage updated for tick T+1

> Note: the 1-tick (100 ms) application lag is uniform across all clients because LIVE and
> REPLAY share `AdvanceOneTick`, so it never causes divergence. It is a deliberate, consistent
> contract — not a reaction-lag bug to "fix" by moving application before simulation.

**Replay algorithm** (same `AdvanceOneTick` as LIVE — events applied at end of tick):
```
simTick = snapshotTick
while simTick < endTick:
    apply all events where event.tick == simTick   // end of tick simTick
    simTick++
    simulate simTick                                // effects of tick-simTick-1 events visible here
```

### Key Concepts

**1. Tick Frontier (OpCode 78 - ZoneTickBroadcast)**
- Server broadcasts every tick (10 Hz)
- Contains `authoritative_tick` and `last_event_seq` (watermark)
- **Invariant:** Server MUST NOT broadcast frontier tick T unless all events with `event.tick == T` have already been broadcast
- Clients advance only when `SimulationTick < AuthoritativeTick` AND watermark satisfied

**2. Influence Events (OpCode 71 - InfluenceBroadcast)**
- Discrete, server-authored events for deterministic simulation
- Sequenced with `Seq` (zone-local, strictly increasing, never resets)
- Logged in `zone.InfluenceLog` for late joiner replay
- Bug events: `PLAYER_CELL_ENTER`, `PLAYER_CELL_LEAVE`, `BUG_REMOVED`, `BUG_SPAWNED`, `SWARM_CENTER_MOVE`
- Plant events: `PLANT_WATER_COMMIT`, `PLANT_DAMAGE_COMMIT`, `PLANT_STAGE_COMMIT`, `PLANT_DIED`, `PLANT_HARVEST_RESULT`
- Fruit tree events: `TREE_FRUIT_GROW`, `TREE_FRUIT_HARVEST`, `TREE_FRUIT_DROP`, `ITEM_ROTTED`
- Rotten fruit events: `ROTTEN_FRUIT_CONSUMED` (FoodValue depleted)

**3. World Updates (OpCode 46 - WorldUpdateMessage)**
- Immediate state changes (ground tile or occupant placement)
- Broadcast to chunk subscribers only
- NOT influence events (not logged for replay)
- Used for: hoeing ground, placing seeds (occupant creation)

### Classification of Farming Actions

| Action | Sync Type | Reason |
|--------|-----------|--------|
| Hoeing ground | WorldUpdate | Changes ground tile, no bug AI impact |
| Planting seed | WorldUpdate | Creates occupant, no bug AI impact |
| Watering crop | CropUpdate (new) | Updates crop state, no bug AI impact |
| Harvesting | WorldUpdate + ItemSpawn | Removes occupant, drops items |
| Growth stage advance | CropUpdate | Server-driven on day tick |
| Bug eating crop | **InfluenceEvent** | Future: aphids, caterpillars (not yet implemented) |
| Fruit growing on tree | **InfluenceEvent** | Affects bug AI (food availability) |
| Fruit harvested | **InfluenceEvent** | Affects bug AI (food availability) |
| Fruit dropped to ground | **InfluenceEvent** | Creates GroundItem, affects bug AI |
| Ground item rotting | **InfluenceEvent** | Changes item type, affects bug AI |
| Fly consuming rotten fruit | **InfluenceEvent** | Must be deterministic for fly AI replay |

### Plant Influence Events (Server-Authoritative)

All irreversible plant state changes MUST be influence events (logged for late joiner replay):

```go
const (
    // Plant events
    InfluencePlantWaterCommit  = "PLANT_WATER_COMMIT"   // Water level committed
    InfluencePlantDamageCommit = "PLANT_DAMAGE_COMMIT"  // HP reduced (by bugs)
    InfluencePlantStageCommit  = "PLANT_STAGE_COMMIT"   // Growth stage advanced
    InfluencePlantDied         = "PLANT_DIED"           // HP reached 0
    InfluencePlantHarvest      = "PLANT_HARVEST_RESULT" // Harvested, yields determined

    // Fruit tree events
    InfluenceTreeFruitGrow     = "TREE_FRUIT_GROW"      // Fruit count increased
    InfluenceTreeFruitHarvest  = "TREE_FRUIT_HARVEST"   // Fruit count decreased (player)
    InfluenceTreeFruitDrop     = "TREE_FRUIT_DROP"      // Fruit fell to ground

    // Ground item events
    InfluenceItemRotted        = "ITEM_ROTTED"          // Item type changed (apple → rotten_apple)
    InfluenceRottenFruitConsumed = "ROTTEN_FRUIT_CONSUMED" // FoodValue reduced by flies
)
```

**Event structure extension:**
```go
type InfluenceEvent struct {
    Tick     int64  `json:"tick"`
    Seq      int64  `json:"seq"`
    Type     string `json:"type"`
    ZoneID   string `json:"zone_id,omitempty"`
    // Existing bug fields...
    PlayerID string `json:"player_id,omitempty"`
    SwarmID  string `json:"swarm_id,omitempty"`
    // Plant fields...
    PlantID  string `json:"plant_id,omitempty"`
    NewValue int    `json:"new_value,omitempty"` // HP, Water, Stage, or FruitCount depending on type
    // Fruit tree fields...
    TreeID      string `json:"tree_id,omitempty"`      // For TREE_* events
    GroundItemID string `json:"ground_item_id,omitempty"` // For TREE_FRUIT_DROP, ITEM_ROTTED
    NewItemType  string `json:"new_item_type,omitempty"`  // For ITEM_ROTTED (e.g., "rotten_apple")
}
```

### Bug-Plant Damage (Scalable Strategy)

**Problem:** With thousands of bugs, we cannot send per-bite messages.

**Solution: Authority-client damage summary (Strategy 3)**

The zone authority client periodically reports plant damage:

```go
type PlantDamageReport struct {
    TickRange    [2]int64        `json:"tick_range"`    // [from_tick, to_tick] inclusive
    PlantChanges map[string]int  `json:"plant_changes"` // plantId -> newHP (only changed plants)
}
```

**Flow:**
1. Authority client simulates bug-plant interactions deterministically
2. Every N ticks (e.g., 20), authority sends `PlantDamageReport`
3. Server validates (bounds check, plausibility)
4. Server emits `PLANT_DAMAGE_COMMIT` events for each changed plant
5. Server emits `PLANT_DIED` for plants that hit HP=0
6. All clients receive events and apply them

**Why this works:**
- No per-bug messages
- Authority client already exists for bug snapshots
- Server validates but doesn't simulate bugs
- Scales to thousands of bugs

### Message Flow Diagrams

**Hoeing (Immediate State Update):**
```
Client                    Server                    Other Clients
   |                         |                           |
   |--ToolUse(hoe,x,y)------>|                           |
   |                         |--validate--               |
   |                         |--change ground tile--     |
   |                         |--WorldUpdate(x,y,tile)--->|
   |<--WorldUpdate-----------|                           |
```

**Planting (Immediate State Update):**
```
Client                    Server                    Other Clients
   |                         |                           |
   |--TilePlace(seed,x,y)--->|                           |
   |                         |--validate--               |
   |                         |--create CropOccupant--    |
   |                         |--consume seed from inv--  |
   |                         |--WorldUpdate(x,y,occ)---->|
   |<--WorldUpdate-----------|                           |
   |<--SlotUpdate(inv)-------|                           |
```

**Watering (State Update, no WorldUpdate needed):**
```
Client                    Server                    Other Clients
   |                         |                           |
   |--ToolUse(water,x,y)---->|                           |
   |                         |--validate--               |
   |                         |--increment crop watering--|
   |                         |--decrement can uses--     |
   |                         |--CropUpdate(x,y,watered)->|
   |<--CropUpdate------------|                           |
   |<--ToolStateUpdate-------|  (water remaining)        |
```

**Bug Eating Crop (Influence Event for Determinism):**
```
Server (during swarm.Think)           All Clients
         |                                  |
         |--swarm reaches crop--            |
         |--emit CROP_DAMAGED event--       |
         |--update crop HP--                |
         |--InfluenceBroadcast------------->|  (for bug AI replay)
         |--CropUpdate(x,y,hp)------------->|  (for visual)
         |                                  |--replay event in bug sim
```

**Fruit Tree Lifecycle (Influence Events):**
```
Server                                All Clients
   |                                       |
   |--tick: fruit growth timer fires--     |
   |--increment FruitCount--               |
   |--emit TREE_FRUIT_GROW---------------->|  (influence event)
   |                                       |--update local FruitTreeState
   |                                       |
   |--tick: drop timer fires (unharvested)-|
   |--decrement FruitCount--               |
   |--create GroundItem (apple)--          |
   |--emit TREE_FRUIT_DROP---------------->|  (influence event)
   |                                       |--spawn ground item visual
   |                                       |
   |--tick: rot timer fires on ground item-|
   |--change item type to rotten_apple--   |
   |--FoodValue=100--                      |
   |--emit ITEM_ROTTED (food_id+cell+lvl)->|  (influence event -> client FOOD REGISTRY)
   |                                       |--fly AI now targets this food
   |                                       |
   |--SERVER advances meters itself--      |  (IMPLEMENTED: no client reports — the server
   |  (swarm centre at cached food target: |   knows centres+counts+food; ledger-first.
   |   Satiation+, FoodValue -= rate*Count)|   The old "authority reports eating" sketch
   |--emit FOOD_CONSUMED at 75/50/25/0---->|   and OpCode-70 are RETIRED.)
   |                                       |--registry level updated (bugs land visuals)
   |                                       |
   |--Satiation 100 -> phase=reproducing-- |
   |--meter fills AT a DEPLETABLE source-- |  (v1 rule: flora never depletes, so breeding
   |--REPRODUCE: Count*=2, food-=50------- |   requires items/stations — bounded growth)
   |--emit SWARM_REPRODUCED (n, idBase)--->|  (clients SpawnBugAt the centre, idempotent)
   |                                       |
   |--FoodValue reaches 0--                |
   |--remove ground item------------------ |
   |--emit FOOD_CONSUMED level=0---------->|  (registry drops it; OpCode 48 removes visual)
```
**Stations (general pattern — composter first):** a placeable with `world.station =
{accepts, capacity, food_per_unit, providers}`. The player right-clicks → a menu →
deposits accepted items (`StationDeposit`, OpCode 85) → the fill meter rises
(`StationUpdate`, OpCode 86, display-only). A non-empty station is a food+breeding
provider drained by the SAME consumption path (its level changes ride `FOOD_CONSUMED`
with `food_id = station_<gx>_<gy>`). Feed troughs / bait baskets are future instances —
pure JSON.

**Late Joiner Sync:**
```
Server                              Late Joiner
   |                                     |
   |--ChunkData (OpCode 44)------------->|  (occupants include plant PlacedOccupants)
   |--LateJoinSnapshot (OpCode 72)------>|  (swarms + plants + influence log)
   |--ZoneHandoff (OpCode 73)----------->|
   |                                     |--restore chunk occupants
   |                                     |--restore plant states from snapshot
   |                                     |--restore swarm states from snapshot
   |                                     |--replay influence events (tick by tick)
   |                                     |--start live simulation
```

**ZoneSnapshot must include plants, fruit trees, and rotten fruit:**
```go
type ZoneSnapshotMessage struct {
    ZoneID       string               `json:"zone_id"`
    SnapshotTick int64                `json:"snapshot_tick"`
    Swarms       []SwarmSnapshot      `json:"swarms"`        // existing
    Plants       []PlantSnapshot      `json:"plants"`        // planted crops
    FruitTrees   []FruitTreeSnapshot  `json:"fruit_trees"`   // fruit tree state
    RottenFruit  []RottenFruitSnapshot `json:"rotten_fruit"` // consumable rotten fruit
    StateHash    string               `json:"state_hash"`
}

type PlantSnapshot struct {
    PlantID           string `json:"plant_id"`
    PlantType         string `json:"plant_type"`
    GridX             int    `json:"grid_x"`
    GridY             int    `json:"grid_y"`
    Stage             int    `json:"stage"`
    HP                int    `json:"hp"`
    Water             int    `json:"water"`
    Flags             uint8  `json:"flags"`
    HarvestsRemaining int    `json:"harvests_remaining"`
}

type FruitTreeSnapshot struct {
    TreeID         string `json:"tree_id"`
    GridX          int    `json:"grid_x"`
    GridY          int    `json:"grid_y"`
    FruitCount     int    `json:"fruit_count"`
    GrowthProgress int    `json:"growth_progress"`
}

type RottenFruitSnapshot struct {
    ItemID    string `json:"item_id"`
    GridX     int    `json:"grid_x"`
    GridY     int    `json:"grid_y"`
    FoodValue int    `json:"food_value"`
}
```

**Replay includes plant, fruit tree, and rotten fruit events:**
Late joiner receives `influence_log` containing all events where `evt.tick > snapshot_tick && evt.tick <= end_tick`, including:
- `PLANT_WATER_COMMIT`
- `PLANT_DAMAGE_COMMIT`
- `PLANT_STAGE_COMMIT`
- `PLANT_DIED`
- `PLANT_HARVEST_RESULT`
- `TREE_FRUIT_GROW`
- `TREE_FRUIT_HARVEST`
- `TREE_FRUIT_DROP`
- `ITEM_ROTTED`
- `ROTTEN_FRUIT_CONSUMED`

Client replays using end-of-tick semantics (apply event at the end of its tick, before simulating the next tick — see "Event Timing Semantics").

### Plant State Storage

**Two-layer storage model:**

**Layer 1: Occupant (in ChunkData)**
```go
// Standard PlacedOccupant - identifies WHAT is planted and WHERE
type PlacedOccupant struct {
    ID     string `json:"id"`     // "plant_tomato", "plant_corn"
    Dir    int    `json:"dir"`    // unused for plants
    Anchor bool   `json:"anchor"` // true
}
```

**Layer 2: PlantState (separate map in WorldState)**
```go
// In WorldState - stores all deterministic plant state
PlantStates map[string]*PlantState  // "gx,gy" -> plant state

type PlantState struct {
    PlantID           string  // Unique ID for this plant instance
    PlantType         string  // "tomato", "corn" - determines growth logic
    GridX, GridY      int     // Cell position (for targeting, pressure grid)
    Stage             int     // 0=seed, 1=sprout, 2=young, 3=mature, 4=dead
    HP                int     // 100 max typical, bugs reduce, 0=dead
    Water             int     // Hydration score, affects growth
    Flags             uint8   // Bitmask: fertilized, protected, withering
    HarvestsRemaining int     // For multi-harvest crops: decrements each harvest, 0=dies
    PlantedTick       int64   // When planted (for growth formulas)
    LastCommitTick    int64   // Last server commit (for drift debugging)
}

// Flag constants
const (
    PlantFlagFertilized = 0x01
    PlantFlagProtected  = 0x02
    PlantFlagWithering  = 0x04
)
```

**Fruit Tree State (separate from PlantState):**
```go
// In WorldState - tracks fruit production on trees
FruitTreeStates map[string]*FruitTreeState  // "gx,gy" -> state

type FruitTreeState struct {
    TreeID          string  // Unique ID for this tree instance
    GridX, GridY    int     // Cell position
    FruitCount      int     // Current fruit on tree (0-max)
    MaxFruit        int     // Maximum fruit capacity (e.g., 5)
    GrowthProgress  int     // Ticks until next fruit appears
    LastHarvestTick int64   // For regrowth timing
}
```

**Rotten Fruit State (ground items with FoodValue):**
```go
// In WorldState - tracks rotten fruit being consumed by flies
RottenFruitStates map[string]*RottenFruitState  // itemId -> state

type RottenFruitState struct {
    ItemID       string  // Unique ground item ID
    ItemType     string  // "rotten_apple", "rotten_orange"
    GridX, GridY int     // Cell position
    FoodValue    int     // 100 = full, 0 = fully consumed
    LastCommitTick int64 // For drift debugging
}
```

**Sync requirements for these states:**
- FruitTreeState included in ZoneSnapshot for late joiners
- RottenFruitState included in ZoneSnapshot for late joiners
- Changes to FruitCount and FoodValue are influence events (affects bug AI)
- Authority client reports changes; server emits commit events

**Why this approach:**
- All fields required for deterministic simulation and replay
- PlantID enables stable iteration order (sort by ID)
- HP separate from Water (bugs damage HP, watering affects Water)
- Flags as bitmask is efficient and extensible
- LastCommitTick enables drift detection

**Key rule: Clients never commit plant state changes locally.**
- Clients may predict visually (wilting animation, growth progress bar)
- Only server events commit real state changes
- This ensures determinism across all clients

### Backend Responsibilities

| Responsibility | Location | Details |
|---------------|----------|---------|
| Validate hoe action | `handlers_farming.go` | Check ground supports hoe, cell empty, tool equipped |
| Change ground tile | `handlers_farming.go` | Set ground to `garden_plot`, broadcast WorldUpdate |
| Validate seed placement | `handlers_world.go` | Check garden_plot, empty cell, has seed in inventory |
| Create crop occupant | `handlers_world.go` | PlacedOccupant in chunk + CropState entry |
| Track crop state | `state.go` | `WorldState.CropStates` map (separate from chunks) |
| Process watering | `handlers_farming.go` | Validate crop exists, increment waters, decrement can uses |
| Track watering can state | `state.go` | `PlayerState.ToolStates` or item durability |
| Apply fertilizer | `handlers_farming.go` | Set CropState.FertilizerType and YieldBonus |
| Day transition | `match.go` | Iterate CropStates: reset watered, check growth, rain bonus |
| Sprinkler watering | `match.go` | Iterate SprinklerLocations, water adjacent crops |
| Harvest | `handlers_farming.go` | Calculate yield (with fertilizer), spawn items, remove crop |
| Bug-crop interaction | `swarm.go` | Detect crop in range, emit CROP_DAMAGED influence event |
| Broadcast crop updates | `match.go` | CropUpdate (OpCode 50) to chunk subscribers |
| Late joiner crop sync | `match.go` | CropStateSync (OpCode 51) with subscribed chunk crops |

### Performance Considerations

**Efficient crop iteration:**
```go
// In WorldState - maintain index for fast lookup
CropsByChunk map[string][]string  // chunkKey -> ["gx,gy", ...]

// On crop plant: add to index
// On crop harvest: remove from index
// On day transition: iterate index, not full chunks
```

**Batch updates:**
```go
// During day transition, collect all updates then broadcast once
var updates []CropUpdateMessage
for cropKey, crop := range state.CropStates {
    if cropChanged {
        updates = append(updates, CropUpdateMessage{...})
    }
}
// Broadcast batch to each chunk's subscribers
```

### Client Responsibilities

| Responsibility | Location | Details |
|---------------|----------|---------|
| Send ToolUse for hoe/water | `FarmingController.cs` | New controller for farming tools |
| Send TilePlace for seeds | `PlacementController.cs` | Extend existing system |
| Render crop by stage | `CropVisual.cs` | Sprite selection based on growth_stage |
| Show watered indicator | `CropVisual.cs` | Visual overlay when watered_today=true |
| Handle CropUpdate | `TilemapManager.cs` | Update crop visual state |
| Watering can UI | `ToolbarUI.cs` | Show remaining uses |

---

## Design Goals

1. **Stardew-style simplicity** - Manual daily watering, rain auto-waters
2. **No punishment** - Crops don't wilt, just pause growth without water
3. **Bug integration** - Future bugs (aphids, caterpillars) will eat crops; current bugs don't
4. **Emergent ecology** - Fruit trees produce fruit → rotten fruit → fly feeding/breeding

---

## Core Mechanics

### 1. Ground Tilling (Hoe)

**Flow:**
```
Player equips hoe → Left-click on grass/dirt tile → Tile becomes garden_plot
```

**Requirements:**
- Target cell must be empty (no occupant)
- Ground tile must support hoeing (`tool_actions.hoe` in tile definition)
- Player within tool reach distance

**Implementation:**
- Uses `OpCode 7 (ToolUse)` - fully implemented in `handlers_farming.go`
- Server validates and changes ground tile via `WorldUpdateMessage`
- Client sends via `ToolUseController.cs` (must be attached to Player GameObject)

### 2. Seed Planting

**Flow:**
```
Player equips seed → Right-click on garden_plot → Crop planted
```

**Requirements:**
- Ground tile is `garden_plot` (has `accepts_plant: true`)
- Cell has no existing occupant
- Player has seed in inventory

**Implementation:**
- Uses existing `OpCode 5 (TilePlace)` placement system
- Seeds become `CropOccupant` with growth state

### 3. Crop Growth System

**Growth Model:**
```
Seed → Stage 1 → Stage 2 → ... → Harvestable
         ↑          ↑              ↑
      (water)   (water)        (water)
```

**State per Crop:**
```go
type CropState struct {
    CropType       string   // e.g., "tomato", "corn"
    GrowthStage    int      // 0 = seed, max = harvestable
    WateringsToday int      // Reset each day
    TotalWaterings int      // Cumulative, drives growth
    PlantedDay     int      // World day when planted
}
```

**Growth Rules:**
- Each crop type defines `waterings_per_stage` (e.g., 3 waterings to advance)
- When `TotalWaterings` reaches threshold → advance `GrowthStage`
- Rain increments `WateringsToday` for all outdoor crops (max 1 per day)
- Manual watering increments if `WateringsToday < max_daily_waterings`

### 4. Watering

**Flow:**
```
Player equips watering can → Left-click on crop → Crop watered
```

**Watering Can Properties:**
- `capacity` - How many uses before refill
- `uses_remaining` - Current water level
- `area` - 1x1 for basic, 3x3 for upgraded

**Refill:**
- Use watering can on water tile to refill

**Rain:**
- Weather system broadcasts rain start/stop
- On day transition, all outdoor crops with rain get +1 watering

### 5. Harvesting & Destruction

**Design principle: "Harvesting should be effortless; destruction should be intentional."**

**Harvest Flow (click on mature plant):**
```
Player clicks mature plant → HarvestAttempt → Server validates → Items drop
```

**Destroy Flow (modifier + click, or long-press):**
```
Player modifier+clicks plant → DestroyAttempt → Server validates → Plant removed
```

**New message for harvest/destroy:**
```go
type PlantInteractMessage struct {
    PlantID       string `json:"plant_id"`
    DestroyIntent bool   `json:"destroy_intent"` // true = destroy, false = harvest
}
```

**Server handling:**
1. Receive `PlantInteractMessage`
2. If `DestroyIntent == false` (harvest attempt):
   - Check if `Stage == mature` → reject if not
   - Calculate drops: base amount × fertilizer bonus
   - Emit `PLANT_HARVEST_RESULT` event
   - For multi-harvest crops: reset to earlier stage (regrow)
   - For single-harvest crops: remove plant
3. If `DestroyIntent == true` (destroy attempt):
   - Remove plant regardless of stage
   - Maybe drop seeds (design choice)
   - Emit `PLANT_REMOVE` event

**Harvest Results:**
- Primary produce (tomatoes, corn, etc.) - randomized within range
- Optional seed drop (based on `seed_drop_chance`)
- Fertilizer bonus applied to quantity
- Ground tile remains `garden_plot` (can replant)

**Multi-harvest crops (e.g., tomatoes):**
- After harvest, plant resets to earlier growth stage
- Continues producing without replanting

---

## Data Structures

### Crop Definitions (`data/entities/crops.json`)

```json
{
  "tomato": {
    "display_name": "Tomato",
    "seed_item": "tomato_seeds",
    "growth_stages": 4,
    "waterings_per_stage": 3,
    "max_daily_waterings": 2,
    "harvest_item": "tomato",
    "harvest_count": [2, 4],
    "seed_drop_chance": 0.5,
    "sprite_prefix": "crop_tomato",
    "bug_food": true,
    "bug_attractiveness": 0.3
  }
}
```

### Seed Items (`data/entities/items.json` additions)

```json
{
  "tomato_seeds": {
    "display_name": "Tomato Seeds",
    "category": "seed",
    "placeable": true,
    "places_crop": "tomato",
    "stack_size": 99,
    "sprite": "item_tomato_seeds"
  }
}
```

### Hoe Tool (`data/entities/items.json` additions)

```json
{
  "hoe_wood": {
    "display_name": "Wooden Hoe",
    "category": "tool",
    "tool_type": "hoe",
    "tool_tier": 1,
    "reach": 3.5
  }
}
```

### Watering Can (`data/entities/items.json` additions)

```json
{
  "watering_can_basic": {
    "display_name": "Watering Can",
    "category": "tool",
    "tool_type": "watering_can",
    "capacity": 40,
    "area": 1
  }
}
```

### Watering Can State Tracking

Watering cans have **per-instance state** (uses remaining). Using **slot metadata** approach:

```go
type InventorySlot struct {
    ItemID   string
    Count    int
    Metadata map[string]int  // {"uses": 35, "capacity": 40}
}
```

**Benefits:**
- Multiple cans with different capacities
- Larger cans hold more water
- Metadata persists with item

**Refill Flow:**
```
Player uses watering can on water tile (shallow/deep)
→ Server receives ToolUse at water tile coords
→ Server validates: is water tile, has watering can equipped
→ Server sets slot.Metadata["uses"] = slot.Metadata["capacity"]
→ Server sends SlotUpdate to client (includes metadata)
```

**Items to define:**
```json
{
  "watering_can_basic": {
    "display_name": "Watering Can",
    "category": "tool",
    "tool_type": "watering_can",
    "metadata_defaults": {"capacity": 40, "uses": 40}
  },
  "watering_can_large": {
    "display_name": "Large Watering Can",
    "category": "tool",
    "tool_type": "watering_can",
    "metadata_defaults": {"capacity": 80, "uses": 80}
  }
}
```

---

## Server-Side Implementation

### New Files

| File | Purpose |
|------|---------|
| `entities/crop.go` | CropState, CropDef, growth logic |
| `handlers_farming.go` | ToolUse handler, watering, harvesting |
| `data/entities/crops.json` | Crop definitions |

### Modified Files

| File | Changes |
|------|---------|
| `messages.go` | Add crop-related message structs |
| `match.go` | Daily tick for rain watering |
| `handlers_world.go` | Extend TilePlace for seeds |
| `state.go` | Track crops in chunks |
| `data/entities/items.json` | Add hoe, watering can, seeds |

### OpCode Usage

| OpCode | Use |
|--------|-----|
| 7 (ToolUse) | Hoeing ground, watering crops |
| 5 (TilePlace) | Planting seeds |
| 55 (PlantInteract) | Harvesting/destroying crops |
| 46 (WorldUpdate) | Crop growth stage changes |
| 50 (CropUpdate) | Crop state changes (water, HP) |

---

## Client-Side Implementation

### New Files

| File | Purpose |
|------|---------|
| `CropVisual.cs` | Render crop sprites by growth stage |
| `WateringController.cs` | Handle watering can input |

### Modified Files

| File | Changes |
|------|---------|
| `BreakingController.cs` | Use ToolUse for hoe actions |
| `PlacementController.cs` | Handle seed placement |
| `EntityDatabase.cs` | Load crop definitions |
| `TilemapManager.cs` | Render crops as occupants |

---

## Bug Integration

### Current Bug Species

Only two bug species are currently implemented:

| Bug | Food Source | Breeding Site | Damages Crops? |
|-----|-------------|---------------|----------------|
| **Fly** | Rotten fruit | Rotten fruit (later) | No |
| **Butterfly** | Flower nectar | Milkweed | No |

### Bug-Plant Interactions (Current)

**Flies:**
- Attracted to rotten fruit (not fresh fruit, not crops)
- Feed on rotten fruit, depleting FoodValue
- Will breed on rotten fruit (future feature)
- Do NOT damage crops

**Butterflies:**
- Sip nectar from flowers
- Breed on milkweed plants
- Do NOT damage crops

### Future Bug Species (Not Yet Implemented)

The plant HP/damage system exists for future bugs that DO eat crops:

```json
{
  "aphid": { "food_preferences": ["plant"], "damages_crops": true },
  "caterpillar": { "food_preferences": ["leaf", "plant"], "damages_crops": true },
  "locust": { "food_preferences": ["plant", "grass"], "damages_crops": true }
}
```

Until these are implemented, plant HP will remain at 100 (no damage sources).

---

## Fruit Trees

Fruit trees are a special category: **permanent plants that produce harvestable fruit**.

### Lifecycle
```
Fruit Tree (permanent) → Produces Fruit (on tree) → Fruit falls to ground → Rots over time → Flies attracted
```

### Tree Types

| Tree ID | Fruit Item | Rotten Item |
|---------|------------|-------------|
| `tree_apple` | `apple` | `rotten_apple` |
| `tree_orange` | `orange` | `rotten_orange` |

### Fruit Production State

Fruit trees have additional state:
```go
type FruitTreeState struct {
    TreeID          string
    FruitCount      int     // Current fruit on tree (0-max)
    MaxFruit        int     // e.g., 5
    FruitGrowthTick int64   // When next fruit appears
    LastHarvestTick int64
}
```

### Fruit Flow

1. **Growth**: Every N ticks, if `FruitCount < MaxFruit`, increment `FruitCount`
2. **Harvest**: Player clicks tree → remove one fruit → drop `apple`/`orange` item
3. **Natural drop**: After M ticks, unharvested fruit falls to ground as `GroundItem`
4. **Rot**: Ground fruit has decay timer → becomes `rotten_apple`/`rotten_orange`
5. **Fly attraction**: Rotten fruit attracts fly swarms (existing ecology)

### Server Events (All are Influence Events)

All fruit tree events are **influence events** because they affect bug AI (food availability):

```go
const (
    // Fruit appeared on tree - affects fly/bee attraction
    InfluenceTreeFruitGrow = "TREE_FRUIT_GROW"  // TreeID, NewValue (fruit count)

    // Fruit harvested by player - removes food source
    InfluenceTreeFruitHarvest = "TREE_FRUIT_HARVEST"  // TreeID, NewValue (fruit count)

    // Fruit fell to ground naturally - creates ground item
    InfluenceTreeFruitDrop = "TREE_FRUIT_DROP"  // TreeID, GroundItemID, GridX, GridY

    // Ground item rotted - changes item type, enables fly attraction
    InfluenceItemRotted = "ITEM_ROTTED"  // GroundItemID, NewItemType

    // Rotten fruit consumed by flies - FoodValue reduced
    InfluenceRottenFruitConsumed = "ROTTEN_FRUIT_CONSUMED"  // GroundItemID, NewValue (FoodValue)
)
```

**Why influence events (not WorldUpdate):**
- Bug AI needs to know food locations for navigation
- Fly swarms target rotten fruit based on FoodValue
- All clients must simulate identical fly behavior
- Late joiners must replay food availability changes

### Trees vs Crops

| Property | Fruit Trees | Crops |
|----------|-------------|-------|
| Lifespan | Permanent (unless attacked) | Limited harvests then die |
| Planting | World-placed (occupant) | Player-planted (seed) |
| Harvest | Click picks one fruit | Click harvests all produce |
| Regrowth | Continuous fruit production | Multi-harvest: regrows X times then dies |
| Destruction | Requires axe + modifier | Requires modifier key |

---

## Multi-Harvest Crop Lifespan

Multi-harvest crops (tomatoes, peppers, etc.) are NOT permanent like fruit trees.

### Lifespan Model
```go
type PlantState struct {
    // ... existing fields ...
    HarvestsRemaining int  // Decrements on each harvest, 0 = plant dies
}
```

### Crop Type Definition
```json
{
  "tomato": {
    "multi_harvest": true,
    "max_harvests": 4,
    "regrow_ticks": 500
  },
  "corn": {
    "multi_harvest": false
  },
  "wheat": {
    "multi_harvest": false
  }
}
```

### Flow
1. Plant seed → grows to mature
2. Harvest → produce drops, `HarvestsRemaining--`, plant resets to earlier stage
3. Regrow to mature again (after `regrow_ticks`)
4. Repeat until `HarvestsRemaining == 0`
5. Plant dies (becomes `stage: dead`, then removed)

This creates a cycle where players must replant crops periodically, unlike permanent fruit trees.

---

## Network Messages

### Summary: What Goes Over the Network

**Every tick (10 Hz):**
- `ZoneTickBroadcast` (frontier + watermark)
- `InfluenceBroadcast` (only if there were events)

**Occasionally (sparse):**
- `PLANT_*` commit events (stage changes, damage thresholds, death)
- `WEATHER_START` / `WEATHER_STOP` events
- `ZONE_WATER_PULSE` events (sprinklers)
- Snapshots from authority client (for late join)
- Late join snapshot delivery

**Player-driven:**
- `WATER_ATTEMPT`
- `HARVEST_ATTEMPT`
- `PLANT_SEED_ATTEMPT`
- `ToolUse` (hoeing)

**Never sent:**
- Per-bug bite messages
- Per-bug movement messages
- Per-plant per-tick watering messages

### Player Action Messages (Client → Server)

These are **requests**, not commits. Server validates and emits commit events.

```go
// OpCode 7 - ToolUse (hoeing, watering)
// Server looks up player.EquippedTool to determine action
type ToolUseMessage struct {
    GridX int `json:"grid_x"` // Target cell X
    GridY int `json:"grid_y"` // Target cell Y
}

// OpCode TBD - Water attempt
type WaterAttemptMessage struct {
    PlantID string `json:"plant_id"`
    ToolID  string `json:"tool_id"`
}

// OpCode TBD - Harvest attempt
type HarvestAttemptMessage struct {
    PlantID string `json:"plant_id"`
}

// OpCode TBD - Plant seed attempt
type PlantSeedAttemptMessage struct {
    GridX    int    `json:"grid_x"`
    GridY    int    `json:"grid_y"`
    SeedType string `json:"seed_type"`
}
```

### Server Commit Events (via InfluenceBroadcast)

All plant state changes come as influence events with `(tick, seq)`:

```go
// PLANT_WATER_COMMIT - Water level committed
// Event fields: PlantID, NewValue (water level)

// PLANT_DAMAGE_COMMIT - HP reduced by bugs
// Event fields: PlantID, NewValue (new HP)

// PLANT_STAGE_COMMIT - Growth stage advanced
// Event fields: PlantID, NewValue (new stage)

// PLANT_DIED - Plant HP reached 0
// Event fields: PlantID

// PLANT_HARVEST_RESULT - Harvest completed
// Event fields: PlantID, yields (item drops)
```

### Authority Client Reports

```go
// Periodic damage summary from authority client
type PlantDamageReport struct {
    TickRange    [2]int64        `json:"tick_range"`    // [from, to] inclusive
    PlantChanges map[string]int  `json:"plant_changes"` // plantId -> newHP
}
```

### Tool State Updates

```go
// OpCode 54 - Watering can capacity update
type ToolStateUpdateMessage struct {
    ToolSlot      int `json:"tool_slot"`
    UsesRemaining int `json:"uses_remaining"`
}
```

---

## Day/Night & Weather Integration

**NOTE:** No day/night system currently exists. It must be implemented for farming.

### Weather Approach: Deterministic Seed (Option B)

Instead of per-tick watering messages, use weather start/stop events with a deterministic seed:

```go
// Server emits when weather starts
type WeatherStartEvent struct {
    Tick          int64  // Event tick
    Seq           int64  // Event sequence
    Type          string // "WEATHER_START"
    WeatherType   string // "rain", "storm"
    Seed          int64  // Deterministic seed for rain pattern
    DurationTicks int64  // How long weather lasts
}

// Server emits when weather ends (optional, can compute from duration)
type WeatherStopEvent struct {
    Tick int64
    Seq  int64
    Type string // "WEATHER_STOP"
}
```

**Client behavior:**
- On `WEATHER_START`: Begin deterministic rain simulation using seed
- Compute which cells get watered each tick using `CounterRng(seed, cellX, cellY, tick)`
- Plants in rained cells accumulate water deterministically
- Server commits `PLANT_WATER_COMMIT` at thresholds (not every tick)

**Benefits:**
- Near-zero bandwidth
- Fully deterministic (all clients compute same rain pattern)
- Late joiners can replay weather from events

### Sprinklers: Zone Water Pulse (Option A)

For sprinklers, use periodic zone-level watering events:

```go
type ZoneWaterPulseEvent struct {
    Tick      int64
    Seq       int64
    Type      string // "ZONE_WATER_PULSE"
    RegionID  string // Which area/chunk
    Intensity int    // Water amount
}
```

Server emits every N ticks for regions with active sprinklers.
Clients deterministically apply hydration to plants in region.

### Plant Growth (Server Commits Only)

**Rule: Clients predict growth visually, server commits stage changes.**

Growth commits happen:
- When stage boundary crossed (seed→sprout→young→mature)
- At periodic intervals (e.g., every 50 ticks) for consistency
- Never per-tick

```go
// Server emits when growth stage changes
type PlantStageCommitEvent struct {
    Tick     int64
    Seq      int64
    Type     string // "PLANT_STAGE_COMMIT"
    PlantID  string
    NewStage int
}
```

### Hydration Decay (Deterministic, Sparse Commits)

Plants lose water over time (deterministic decay).
Clients simulate this locally, but server commits only at thresholds:

```go
// Server emits when water level crosses threshold
type PlantWaterCommitEvent struct {
    Tick      int64
    Seq       int64
    Type      string // "PLANT_WATER_COMMIT"
    PlantID   string
    NewWater  int
}
```

Thresholds: 100 → 75 → 50 → 25 → 0 (withering)

### Day Transition (If Using Day/Night Cycle)

If implementing explicit days:

```go
type DayNightState struct {
    CurrentTime    float32 // 0.0 = midnight, 0.5 = noon
    DayNumber      int     // Cumulative day count
    DayLengthTicks int64   // 8400 ticks = 14 minutes (like Stardew Valley)
}
```

Day transition triggers:
1. Weather roll for new day
2. Sprinkler pulse processing
3. Growth stage check and commits
4. `DayChangeMessage` broadcast to clients

---

## Codebase Integration Analysis

**This section documents what already exists vs what needs to be added.**

### Existing Infrastructure (Can Reuse)

| Component | Location | Status | Notes |
|-----------|----------|--------|-------|
| **tiles.json** | `nakama/data/tiles.json` | ✓ Ready | `grass`/`dirt` have `tool_actions.hoe: "garden_plot"` |
| **garden_plot tile** | `nakama/data/tiles.json:40-44` | ✓ Ready | Has `accepts_plant: true` |
| **water_shallow tile** | `nakama/data/tiles.json:56-60` | ✓ Ready | For watering can refill |
| **OpCode 7 (ToolUse)** | `messages.go:13`, `handlers_farming.go` | ✓ Implemented | Routes to handleHoe/handleWatering |
| **GroundItem** | `entities/items.go` | ✓ Ready | Has ID, ItemType, Count, Position, Lifetime |
| **PlacedOccupant** | `world/occupants.go:5-9` | ✓ Ready | Has ID, Dir, Anchor |
| **EntityDef** | `world/entities.go:15-42` | ✓ Ready | Has ToolType, ToolTier, Reach, World data |
| **WorldUpdateMessage** | `messages.go:221-228` | ✓ Ready | GridX, GridY, Ground, Occupant |
| **broadcastWorldUpdate()** | `handlers_world.go:396-411` | ✓ Ready | For ground tile changes |
| **getToolStats()** | `handlers_world.go:413-425` | ✓ Ready | Gets ToolType, ToolTier from equipped |
| **fly_common species** | `species.json:2-44` | ✓ Ready | `attractions_by_phase.feeding: ["rotten_fruit"]` |
| **butterfly_meadow species** | `species.json:45-87` | ✓ Ready | `attractions_by_phase.feeding: ["flower_*"]` |

### Existing Code That Needs Modification

| Component | Location | Change Required |
|-----------|----------|-----------------|
| **InventorySlot** | `state.go:126-130` | Add `Metadata map[string]int` for watering can |
| **InventorySlot (client)** | `InventoryMessages.cs:26-51` | Add metadata field |
| **PlayerState** | `state.go:132-147` | Add `LastToolTick int64` for cooldown |
| **match.go MatchLoop** | `match.go:334-456` | Add case for `OpCodeToolUse` |
| **GroundItem** | `entities/items.go:4-10` | Add `DecaysTo string` for rot (apple → rotten_apple) |
| **EntityDef** | `entities.go:15-42` | Add `CooldownTicks int` for tools |
| **plant.go PlantState** | `entities/plant.go:11-17` | Rename to `BreedingPlantState` (used for bug breeding) |

### New Code Required

| Component | Location | Purpose |
|-----------|----------|---------|
| **CropState** | `entities/crop.go` (NEW) | Farming crop state (HP, Water, Stage, HarvestsRemaining) |
| **CropDef** | `entities/crop.go` (NEW) | Crop type definitions |
| **FruitTreeState** | `entities/fruit_tree.go` (NEW) | Fruit production state |
| **RottenFruitState** | `entities/rotten_fruit.go` (NEW) | FoodValue tracking for fly consumption |
| **handleToolUse()** | `handlers_farming.go` (NEW) | Hoe, watering can actions |
| **crops.json** | `data/entities/crops.json` (NEW) | Crop type definitions |
| **CropUpdate (OpCode 50)** | `messages.go` | Crop state changes |
| **WeatherStartEvent** | `messages.go` | Rain/weather events |
| **Plant influence events** | `state.go` | PLANT_WATER_COMMIT, PLANT_DAMAGE_COMMIT, etc. |
| **Fruit tree influence events** | `state.go` | TREE_FRUIT_GROW, TREE_FRUIT_DROP, etc. |

### Key File Paths Reference

**Server (nakama/modules/):**
```
world/
├── match.go           # Main loop, tick broadcast (line 588-615)
├── state.go           # WorldState, PlayerState, InventorySlot (line 126-130)
├── messages.go        # OpCodes, message structs
├── handlers_world.go  # TilePlace, TileBreak handlers
├── zone.go            # ChunkData, TileDefinition
├── occupants.go       # PlacedOccupant struct
├── entities.go        # EntityDef, WorldData, BreakableData
├── tiles.go           # Tile loading
└── inventory.go       # AddItem, RemoveItem, MoveSlot

entities/
├── swarm.go           # SwarmState (existing)
├── plant.go           # PlantState (for bug breeding, rename to BreedingPlantState)
├── items.go           # GroundItem (existing)
├── eggs.go            # EggCluster (existing)
├── crop.go            # CropState (NEW)
├── fruit_tree.go      # FruitTreeState (NEW)
└── rotten_fruit.go    # RottenFruitState (NEW)

data/
├── tiles.json         # Tile definitions (garden_plot exists!)
├── species.json       # Bug species (fly attracted to rotten_fruit!)
└── entities/
    ├── items.json     # Inventory items (add hoe, watering_can, seeds)
    ├── occupants.json # World objects (add fruit trees)
    └── placeables.json # Placeable items (add sprinklers)
```

**Client (BugFarmerClient/Assets/Scripts/):**
```
Networking/
├── NetworkManager.cs    # Socket connection
├── WorldManager.cs      # Match data dispatch
├── BugMessages.cs       # Influence events, tick frontier
├── WorldMessages.cs     # ChunkData, WorldUpdate
└── InventoryMessages.cs # InventorySlot (add metadata)

Entities/
├── SwarmManager.cs      # Tick frontier gating (line 176-201)
└── SwarmVisual.cs       # Bug rendering

Bugs/
├── InfluenceManager.cs  # Player cell positions, event processing
├── BugAgent.cs          # Deterministic simulation
└── DeterministicRandom.cs # Counter-based RNG

World/
├── TilemapManager.cs    # Chunk rendering, occupants
└── (NEW) CropVisual.cs  # Crop stage rendering

Data/
└── EntityDatabase.cs    # JSON loading, sprites

UI/
├── InventoryManager.cs  # Slot management
└── InventorySlotUI.cs   # UI rendering
```

### InventorySlot Metadata Change

**Current structure (`state.go:126-130`):**
```go
type InventorySlot struct {
    ItemID string `json:"item_id"`
    Count  int    `json:"count"`
}
```

**Required change:**
```go
type InventorySlot struct {
    ItemID   string         `json:"item_id"`
    Count    int            `json:"count"`
    Metadata map[string]int `json:"metadata,omitempty"` // NEW: {"uses": 35, "capacity": 40}
}
```

**Client-side (`InventoryMessages.cs`):**
```csharp
[Serializable]
public class InventorySlot
{
    public string item_id;
    public int count;
    public Dictionary<string, int> metadata;  // NEW
}
```

### GroundItem Decay Change

**Current structure (`entities/items.go:4-10`):**
```go
type GroundItem struct {
    ID       string
    ItemType string
    Count    int
    Position EntityPosition
    Lifetime float32
}
```

**Required change:**
```go
type GroundItem struct {
    ID        string
    ItemType  string
    Count     int
    Position  EntityPosition
    Lifetime  float32
    DecaysTo  string  // NEW: "rotten_apple" when Lifetime expires (empty = despawn)
    FoodValue int     // NEW: For rotten fruit only (100 = full, 0 = consumed)
}
```

---

## Implementation Phases

### Phase 1: Core Tilling & Planting
- [ ] Add hoe tool definitions (wood, stone, copper, iron)
- [ ] Implement ToolUse handler (OpCode 7) for hoeing
- [ ] Add seed item definitions
- [ ] Extend TilePlace for seed planting
- [ ] Basic CropState storage in chunks
- [ ] CropDef loading from crops.json

### Phase 2: Growth & Harvesting
- [ ] Crop growth stage system
- [ ] Visual crop rendering (client) - sprites per growth stage
- [ ] Harvesting via PlantInteract (OpCode 55)
- [ ] Item drops on harvest (with randomized count range)
- [ ] Seed drop chance on harvest

### Phase 3: Watering
- [ ] Watering can tool (with capacity)
- [ ] Watering action via ToolUse
- [ ] Water capacity tracking & refill on water tiles
- [ ] Daily watering counter per crop
- [ ] Visual indicator for watered/unwatered crops

### Phase 4: Day/Weather Integration
- [ ] Day transition hook for crops
- [ ] Reset WateringsToday on new day
- [ ] Rain watering bonus (auto-water outdoor crops)
- [ ] Growth stage advancement check
- [ ] Broadcast crop updates to subscribers

### Phase 5: Fertilizer & Sprinklers
- [ ] Fertilizer item and placement
- [ ] Yield bonus calculation on harvest
- [ ] Sprinkler structure placement
- [ ] Sprinkler day-transition watering logic
- [ ] Different sprinkler tiers and patterns

### Phase 6: Bug Integration (Later)
- [ ] Crop attractiveness to swarms
- [ ] Swarm eating behavior
- [ ] Crop damage/destruction system

---

## Design Decisions

| Question | Decision |
|----------|----------|
| Seasons | **No seasons** - all crops available year-round |
| Greenhouse | **Later feature** - not in initial implementation |
| Fertilizer | **Yes** - increases harvest yield (not growth speed) |
| Crop quality | **Later feature** - no star ratings initially |
| Sprinklers | **Yes** - auto-water nearby crops each day |

---

## Fertilizer System

**NOTE:** Due to one-occupant-per-cell limit, fertilizer is stored as an **attribute of CropState**, not a separate occupant.

### Mechanics
- Crafted from compost bin (bug remains, plant matter)
- Applied via ToolUse on a crop cell (not placement)
- Sets `CropState.FertilizerType` and `YieldBonus`
- Increases harvest yield multiplier (e.g., 1.5x)
- One-time use per crop cycle (bonus resets on harvest)

### Application Flow
```
Player equips fertilizer → Left-click on planted crop → Fertilizer applied
```

**Server handling:**
1. Receive ToolUse with fertilizer equipped
2. Validate: crop exists at cell, not already fertilized
3. Consume fertilizer from inventory
4. Set `CropState.FertilizerType` and `YieldBonus`
5. Broadcast CropUpdate (client shows visual indicator)

### Item Definition
```json
{
  "basic_fertilizer": {
    "display_name": "Fertilizer",
    "category": "consumable",
    "use_action": "fertilize",
    "yield_bonus": 1.5,
    "stack_size": 99
  }
}
```

---

## Sprinkler System

**NOTE:** Sprinklers ARE separate occupants (placed on their own cells, not on crops).

### Mechanics
- Placeable structure via TilePlace (uses existing system)
- Placed on any ground tile (grass, dirt, stone_path, etc.)
- Waters crops in adjacent cells at day transition
- Different tiers with increasing radius

### Storage

Sprinklers are standard PlacedOccupants - no extra state needed:
```go
// In ChunkData.Occupants
PlacedOccupant{ID: "sprinkler_basic", Dir: 0, Anchor: true}
```

For efficient day-transition processing, track sprinkler locations:
```go
// In WorldState
SprinklerLocations map[string]string  // "gx,gy" -> sprinkler type
```

### Entity Definitions
```json
{
  "sprinkler_basic": {
    "display_name": "Sprinkler",
    "category": "structure",
    "placeable": true,
    "footprint": [1, 1],
    "water_radius": 1,
    "water_pattern": "adjacent"
  },
  "sprinkler_quality": {
    "display_name": "Quality Sprinkler",
    "category": "structure",
    "placeable": true,
    "footprint": [1, 1],
    "water_radius": 2,
    "water_pattern": "square"
  }
}
```

### Water Patterns
- `adjacent` - 4 tiles (N/S/E/W only)
- `square` - 8 tiles (3x3 minus center)
- `large_square` - 24 tiles (5x5 minus center)

### Day Transition Processing

```go
func (m *Match) processSprinklerWatering(state *WorldState) {
    for locKey, sprinklerType := range state.SprinklerLocations {
        gx, gy := parseGridKey(locKey)
        def := state.Entities[sprinklerType]

        // Get cells to water based on pattern
        cells := getWaterPattern(gx, gy, def.WaterRadius, def.WaterPattern)

        for _, cell := range cells {
            cropKey := fmt.Sprintf("%d,%d", cell.X, cell.Y)
            crop := state.CropStates[cropKey]
            if crop == nil { continue }

            cropDef := state.CropDefs[crop.CropType]
            if crop.WateringsToday < cropDef.MaxDailyWaterings {
                crop.TotalWaterings++
                crop.WateringsToday++
                // Queue CropUpdate broadcast
            }
        }
    }
}

func getWaterPattern(cx, cy, radius int, pattern string) []GridCell {
    var cells []GridCell
    switch pattern {
    case "adjacent":
        cells = []GridCell{{cx, cy-1}, {cx, cy+1}, {cx-1, cy}, {cx+1, cy}}
    case "square":
        for dy := -radius; dy <= radius; dy++ {
            for dx := -radius; dx <= radius; dx++ {
                if dx == 0 && dy == 0 { continue }
                cells = append(cells, GridCell{cx + dx, cy + dy})
            }
        }
    }
    return cells
}
```

---

## Determinism Rules (Critical)

These must be enforced everywhere in simulation code:

### Iteration Order
- Iterate swarms by `OrderBy(swarmId)`
- Iterate bugs by `OrderBy(bugId)`
- Iterate plants by `OrderBy(plantId)` or stable spatial index
- Iterate players by `OrderBy(playerId)`
- **Never rely on Dictionary/map iteration order**

### State Access
- Simulation reads only committed state
- Never read Unity Transforms for logic
- Use `InfluenceManager` player cells for player positions

### Deterministic Randomness
Use counter-based RNG with no mutable state:
```go
func CounterRng(worldSeed, entityId, tick, purposeId int64) float32 {
    // Hash all inputs to produce deterministic value
    // All clients compute identical results
}
```

### Failure Modes

| Condition | Response |
|-----------|----------|
| Event arrives with `evt.tick < SimulationTick` and wasn't applied | Protocol violation → `RequestResync()` |
| Missing seq gap in events | Warn loudly, optionally request resync |
| Drift detected (hash mismatch) | Log for diagnosis, optionally resync |

### Drift Detection (Recommended)
Every N ticks, compute lightweight hash of:
- Plant states: `plantId + stage + hp + water`
- Key bug states (if cheap)

Log locally for diagnosis.

---

## Finalized Design Decisions

### Watering Can Tracking
**Slot metadata approach** - Each inventory slot can have metadata:
```go
type InventorySlot struct {
    ItemID   string
    Count    int
    Metadata map[string]int  // e.g., {"uses": 35, "capacity": 40}
}
```
- Supports multiple cans with different capacities
- Refill sets `uses = capacity`

### Harvest vs Destroy
**Design principle: "Harvesting should be effortless; destruction should be intentional."**

| Action | Result |
|--------|--------|
| Click on harvestable plant | Harvest (get produce) |
| Click on immature plant | Nothing (action rejected) |
| Modifier + click (or long-press) | Destroy (plant removed, maybe seeds drop) |

Server checks:
1. Is plant harvestable? → process harvest
2. Else if destroy intent flag set? → process destruction
3. Else → reject action

Multi-harvest crops (e.g., tomatoes) regrow after harvest automatically.

### Damage Report Frequency
**Threshold-based** - Authority client reports only when plant HP crosses threshold bands:
- 100 → 75 → 50 → 25 → 0

This minimizes bandwidth while ensuring timely death notifications.

### Weather Frequency
**Random per day** - Each day has X% chance of rain (e.g., 30%).
Server rolls weather at day start, emits `WEATHER_START` if rain.

### Bug Food Priority
**Species-specific** - Each bug species has specific food sources.
Current implementation:
```json
{
  "fly": { "food_preferences": ["rotten_fruit"] },
  "butterfly": { "food_preferences": ["flower_nectar"] }
}
```
Future bugs (aphid, caterpillar, locust) will target crops directly.

### Sprinklers
**Provided in inventory** (no crafting system yet).
Items to add: `sprinkler_basic`, `sprinkler_quality`

### Tool Cooldowns (Critical for Scalability)

**Rule: The server MUST enforce a per-player cooldown on all tool actions.**

Requests during cooldown MUST be rejected silently (no commit event). This guarantees harvest/destruction/watering cannot exceed fixed rates even under load or malicious input.

**Why this works:**
- Intent messages are the only input volume (one message per click)
- Cooldown caps message rate per player globally
- Server batching into InfluenceBroadcast caps outbound traffic
- 30 players harvesting = 30 messages every 300ms = trivial load
- DoS attempts irrelevant (server throttles)
- Preserves determinism (server still validates, assigns tick/seq)

**Recommended cooldown values:**

| Tool Action | Cooldown (ticks) | Time |
|-------------|------------------|------|
| Harvest | 3 | 300ms |
| Hoe | 5 | 500ms |
| Watering Can | 5 | 500ms |
| Fertilizer | 5 | 500ms |
| Shake Fruit Tree | 5 | 500ms |
| Destroy Plant | 8 | 800ms |

**Server validation:**
```go
func (m *Match) validateToolCooldown(player *PlayerState, toolID string, tick int64) bool {
    def := m.state.Entities[toolID]
    cooldown := int64(def.CooldownTicks)
    if cooldown == 0 {
        cooldown = 5 // Default 500ms
    }

    if tick < player.LastToolTick + cooldown {
        return false // Silently reject
    }

    player.LastToolTick = tick
    return true
}
```

**EntityDef addition:**
```go
type EntityDef struct {
    // ... existing fields ...
    CooldownTicks int `json:"cooldown_ticks,omitempty"` // Tool use cooldown
}
```

**PlayerState addition:**
```go
type PlayerState struct {
    // ... existing fields ...
    LastToolTick int64 // Last tick a tool action was accepted
}
```

**Scalability guarantee:**
- O(players) instead of O(players × plants)
- Hot-spots (busy farms) scale perfectly
- No new messages, no protocol changes

---

## Objects & Items Required

**IMPORTANT:** Follow the `tools/LLM Guides/creating_objects.md` pipeline for all new objects.

### New Objects Summary

| Entity ID | Type | JSON File | Sprites Needed |
|-----------|------|-----------|----------------|
| `hoe_wood` | item | items.json | `Items/hoe_wood_icon.png` |
| `hoe_iron` | item | items.json | `Items/hoe_iron_icon.png` |
| `watering_can_basic` | item | items.json | `Items/watering_can_basic_icon.png` |
| `watering_can_large` | item | items.json | `Items/watering_can_large_icon.png` |
| `sprinkler_basic` | placeable | placeables.json | `Items/sprinkler_basic_icon.png`, `Objects/sprinkler_basic.png` |
| `sprinkler_quality` | placeable | placeables.json | `Items/sprinkler_quality_icon.png`, `Objects/sprinkler_quality.png` |
| `seed_tomato` | item | items.json | `Items/seed_tomato_icon.png` |
| `seed_corn` | item | items.json | `Items/seed_corn_icon.png` |
| `seed_wheat` | item | items.json | `Items/seed_wheat_icon.png` |
| `basic_fertilizer` | item | items.json | `Items/basic_fertilizer_icon.png` |
| `plant_tomato` | occupant | occupants.json | `Objects/plant_tomato_stage0.png` through `stage3.png` |
| `plant_corn` | occupant | occupants.json | `Objects/plant_corn_stage0.png` through `stage3.png` |
| `plant_wheat` | occupant | occupants.json | `Objects/plant_wheat_stage0.png` through `stage3.png` |
| `tree_apple` | occupant | occupants.json | `Objects/tree_apple.png`, `Objects/tree_apple_fruit.png` |
| `tree_orange` | occupant | occupants.json | `Objects/tree_orange.png`, `Objects/tree_orange_fruit.png` |
| `apple` | item | items.json | `Items/apple_icon.png` |
| `orange` | item | items.json | `Items/orange_icon.png` |
| `rotten_apple` | item | items.json | `Items/rotten_apple_icon.png` |
| `rotten_orange` | item | items.json | `Items/rotten_orange_icon.png` |
| `tomato` | item | items.json | `Items/tomato_icon.png` |
| `corn` | item | items.json | `Items/corn_icon.png` |
| `wheat` | item | items.json | `Items/wheat_icon.png` |

### Items for Player Inventory (Testing)

These should be given to player on spawn for testing:

| Item ID | Category | Purpose |
|---------|----------|---------|
| `hoe_wood` | tool | Till ground into garden_plot |
| `watering_can_basic` | tool | Water plants (40 uses) |
| `sprinkler_basic` | structure | Auto-water adjacent tiles |
| `sprinkler_quality` | structure | Auto-water 3x3 area |
| `seed_tomato` | seed | Plant tomatoes (multi-harvest, 4 harvests) |
| `seed_corn` | seed | Plant corn (single-harvest, realistic) |
| `seed_wheat` | seed | Plant wheat (single-harvest) |
| `basic_fertilizer` | consumable | Boost yield 1.5x |

### Fruit Trees (World-Placed Occupants)

Fruit trees spawn in the world (not player-planted):

| Tree ID | Fruit | Rotten Version | Fly Attraction |
|---------|-------|----------------|----------------|
| `tree_apple` | `apple` | `rotten_apple` | High |
| `tree_orange` | `orange` | `rotten_orange` | High |

### Day/Night Timing

| Parameter | Value |
|-----------|-------|
| Day length | 14 minutes (840 seconds, 8,400 ticks) |
| Tick rate | 10 Hz |

### Ground Item Decay

| Item | Decay Time | Ticks | Becomes |
|------|------------|-------|---------|
| `apple` (on ground) | ~2 days | 16,800 | `rotten_apple` |
| `orange` (on ground) | ~2 days | 16,800 | `rotten_orange` |

### Rotten Fruit Consumption

Rotten fruit does NOT decay on a timer - it gets **consumed by flies**.

```go
type RottenFruitState struct {
    ItemID     string
    GridX, GridY int
    FoodValue  int    // Starts at 100, flies deplete it
}
```

**Mechanics:**
- Rotten fruit spawns with `FoodValue = 100`
- Flies feeding on it reduce `FoodValue` over time
- When `FoodValue = 0`, fruit is fully consumed and despawns
- More flies = faster consumption
- No flies nearby = fruit persists indefinitely

This creates the ecology loop:
1. Fruit tree drops fruit
2. Fruit rots after 2 days
3. Rotten fruit attracts flies
4. Flies feed and breed, consuming the fruit
5. When fruit depleted, flies must find new food source
6. Player can sustain fly population by maintaining rotten fruit supply

### Rotten Fruit Sync (Authority-Client Pattern)

Fly consumption of rotten fruit uses the same authority-client pattern as bug-plant damage.

**Flow:**
1. Authority client simulates flies eating rotten fruit deterministically
2. Every N ticks, authority sends `RottenFruitReport`:
```go
type RottenFruitReport struct {
    TickRange     [2]int64       `json:"tick_range"`     // [from, to] inclusive
    FruitChanges  map[string]int `json:"fruit_changes"`  // itemId -> newFoodValue
}
```
3. Server validates (bounds check, plausibility)
4. Server emits `ROTTEN_FRUIT_CONSUMED` influence events at thresholds (100→75→50→25→0)
5. When FoodValue reaches 0, server emits event to despawn the item
6. All clients receive events and apply them deterministically

**Why influence events (not WorldUpdate):**
- Rotten fruit is food for flies
- Fly AI uses rotten fruit location for navigation
- FoodValue determines how attractive the item is
- All clients must agree on food availability for deterministic fly behavior

**Determinism requirements:**
- Iterate rotten fruit by `OrderBy(itemId)`
- Flies consume rotten fruit in deterministic order
- Use counter-based RNG for consumption amounts

---

## Troubleshooting

### Common Issues

**Hoe/Watering can does nothing:**

1. **Check Unity Setup:** `ToolUseController.cs` must be attached to the Player GameObject
   - Select Player in scene hierarchy
   - Click Add Component → ToolUseController
   - Default settings are fine (cooldown: 0.3, max distance: 4)

2. **Check Client Console:** Look for `[ToolUseController] Sent ToolUse at (X, Y)`
   - If NOT seen: ToolUseController not attached or tool type not "hoe"/"watering_can"
   - If seen: Message is being sent, check server

3. **Check Server Logs:** `docker compose logs -f nakama | grep -i "tool\|hoe\|water"`
   - Should see: `ToolUse received from <userID>: grid(X,Y), equipped=<toolID>`
   - Should see: `Player X hoed tile at X,Y -> garden_plot`

4. **Check EquippedTool is set:**
   - Client must send OpCode 27 (EquipTool) when selecting hotbar slot
   - Verify with server logs: the `equipped=` value should match the tool ID

### Debug Commands

```bash
# Watch server logs live
docker compose logs -f nakama | grep -i "tool\|hoe\|water"

# Rebuild server if code changes made
docker compose build --no-cache builder && docker compose down && docker compose up -d
```

---

## Revision History

| Date | Author | Changes |
|------|--------|---------|
| 2026-01-18 | Claude | Initial architecture draft |
| 2026-01-18 | Claude | Added sync architecture section with message flows |
| 2026-01-18 | Claude | Fixed crop storage: separate CropStates map (not inline in occupant) |
| 2026-01-18 | Claude | Added day/night system design (not yet implemented) |
| 2026-01-18 | Claude | Fixed fertilizer: stored as CropState attribute, not separate occupant |
| 2026-01-18 | Claude | Added new OpCodes: CropUpdate(50), CropStateSync(51), DayChange(52), etc. |
| 2026-01-18 | Claude | Added watering can state tracking options |
| 2026-01-18 | Claude | Added performance considerations for crop iteration |
| 2026-01-18 | Claude | **MAJOR:** Integrated frontier-gated determinism spec |
| 2026-01-18 | Claude | Renamed CropState → PlantState with HP, Water, Flags fields |
| 2026-01-18 | Claude | Added plant influence events (PLANT_WATER_COMMIT, PLANT_DAMAGE_COMMIT, etc.) |
| 2026-01-18 | Claude | **CRITICAL:** Confirmed effects-at-t semantics (events applied BEFORE simulating tick t) |
| 2026-01-18 | Claude | Added authority-client PlantDamageReport for scalable bug damage |
| 2026-01-18 | Claude | Added ZoneSnapshot.Plants for late joiner sync |
| 2026-01-18 | Claude | Added weather seed approach (WEATHER_START/STOP) for rain |
| 2026-01-18 | Claude | Added zone water pulse for sprinklers |
| 2026-01-18 | Claude | Added determinism rules section |
| 2026-01-18 | Claude | Finalized: watering can uses slot metadata (multiple cans supported) |
| 2026-01-18 | Claude | Finalized: harvest vs destroy separation with intent flag |
| 2026-01-18 | Claude | Finalized: threshold-based damage reports |
| 2026-01-18 | Claude | Finalized: random-per-day weather |
| 2026-01-18 | Claude | Finalized: species-specific food preferences |
| 2026-01-18 | Claude | Added items required for testing section |
| 2026-01-18 | Claude | Added fruit trees (apple, orange) with rot mechanics |
| 2026-01-18 | Claude | Added multi-harvest crop lifespan (HarvestsRemaining) |
| 2026-01-18 | Claude | Added FruitTreeState for fruit production tracking |
| 2026-01-18 | Claude | Added ground item decay (apple → rotten_apple) |
| 2026-01-18 | Claude | Referenced creating_objects.md pipeline for new objects |
| 2026-01-18 | Claude | Set day length to 14 minutes (8,400 ticks), fruit rots in ~2 days |
| 2026-01-18 | Claude | **SYNC FIX:** Added FruitTreeState and RottenFruitState to ZoneSnapshot |
| 2026-01-18 | Claude | **SYNC FIX:** Added fruit tree fields to InfluenceEvent struct |
| 2026-01-18 | Claude | **SYNC FIX:** Added rotten fruit consumption authority-client pattern |
| 2026-01-18 | Claude | Added fruit tree lifecycle message flow diagram |
| 2026-01-18 | Claude | Consolidated all influence event constants in one location |
| 2026-01-18 | Claude | Clarified: corn=single harvest, tomato=multi harvest (realistic) |
| 2026-01-18 | Claude | Clarified: only flies and butterflies implemented; neither damages crops |
| 2026-01-18 | Claude | Flies eat rotten fruit only; butterflies sip nectar, breed on milkweed |
| 2026-01-18 | Claude | **CODEBASE REVIEW:** Added integration analysis section |
| 2026-01-18 | Claude | Documented: tiles.json already has garden_plot, hoe tool_actions |
| 2026-01-18 | Claude | Documented: species.json has fly_common attracted to rotten_fruit |
| 2026-01-18 | Claude | Documented: OpCode 7 (ToolUse) defined but NOT implemented |
| 2026-01-18 | Claude | Documented: InventorySlot needs Metadata field for watering can |
| 2026-01-18 | Claude | Documented: GroundItem needs DecaysTo and FoodValue fields |
| 2026-01-18 | Claude | Documented: plant.go exists (rename to BreedingPlantState) |
| 2026-01-18 | Claude | Added complete file path reference for server and client |
| 2026-01-18 | Claude | Added tool cooldown system for scalability (O(players) not O(players×plants)) |
| 2026-01-18 | Claude | Added troubleshooting section for debugging hoe/watering can issues |
| 2026-01-18 | Claude | Updated: OpCode 7 (ToolUse) now fully implemented in handlers_farming.go |
| 2026-06-02 | Claude | **CORRECTION:** Event semantics are end-of-tick / effects-at-(t+1) as implemented in AdvanceOneTick (events stamped tick T applied after simulating T, visible at T+1), uniform across LIVE+REPLAY. Supersedes the 2026-01-18 "effects-at-t" entry. |
| 2026-06-02 | Claude | Swarm-center determinism: server emits sparse SWARM_SET_TARGET legs (origin+target+speed); clients march centers in fixed-point. Per-tick center firehose removed; SwarmUpdate made event-driven (SwarmsDirty). |
| 2026-06-02 | Claude | Recovery routed through zone late-join resync (RequestResync → LateJoinSnapshot); removed legacy chunk-scoped FullSnapshot path. Wired frontier-stall + handshake-wait timers. |
| 2026-06-02 | Claude | Alert roll now integer-only (CounterRng.Chance 3/10) — removed last float from sim hot path. |

## Watering visuals — RESOLVED (2026-06)
The "watered beds look blocked out" report: the wet-ground flow was correct all along
(handleWatering swaps garden_plot → garden_plot_wet AND broadcasts the WorldUpdate; the tile
art exists) — the blocker was the crop-stage PLACEHOLDER sprites (52%-opaque 32×32 labeled
blobs) that the CropUpdate stage-swap rendered over the cell. All 11 stage sprites
(tomato/corn 0-3, wheat 0-2) are now real generated art (catalog looks in
tools/art/catalog/crops.json); the wet tile is visible under the alpha-trimmed plants.
