# Entity Synchronization Architecture

## Overview

This document describes the real-time entity synchronization system for BugFarmer. The system handles position and facing updates for all dynamic entities (players, bugs) using a unified architecture.

## Design Principles

- **Client prediction**: Local player moves immediately for responsiveness
- **Server authority**: Server validates positions, updates state, broadcasts to all
- **Interpolation**: Remote entities smoothly interpolate between updates
- **Tick rate**: 10 updates/second (100ms intervals)
- **Unified system**: Players and bugs share the same networking/rendering pipeline

---

## Wire Protocol

### Client → Server

**OpCode 1: Movement**
```json
{
    "x": 512.5,
    "y": 320.0,
    "facing": 2
}
```
- `x`, `y`: World coordinates (blocks from origin)
- `facing`: Direction enum (0=Down, 1=Left, 2=Right, 3=Up)

### Server → Client

**OpCode 11: EntityUpdate**
```json
{
    "entities": [
        {"id": "player_abc123", "type": "player", "x": 512.5, "y": 320.0, "facing": 2},
        {"id": "bug_xyz789", "type": "bug", "x": 510.0, "y": 318.5, "facing": 1}
    ]
}
```
- `id`: Unique entity identifier (prefixed by type)
- `type`: Entity type for prefab selection ("player", "bug")
- `x`, `y`: World coordinates
- `facing`: Direction enum

---

## Server Implementation (Go)

### Direction Enum
**Location:** `nakama/modules/entities/types.go`

```go
type Direction int
const (
    DirDown  Direction = iota  // 0
    DirLeft                    // 1
    DirRight                   // 2
    DirUp                      // 3
)
```

### Message Structs
**Location:** `nakama/modules/world/messages.go`

```go
type MovementMessage struct {
    X      float32 `json:"x"`
    Y      float32 `json:"y"`
    Facing int     `json:"facing"`
}

type EntityData struct {
    ID     string  `json:"id"`
    Type   string  `json:"type"`
    X      float32 `json:"x"`
    Y      float32 `json:"y"`
    Facing int     `json:"facing"`
}

type EntityUpdateMessage struct {
    Entities []EntityData `json:"entities"`
}
```

### Position Conversion
**Location:** `nakama/modules/world/state.go`

PlayerState methods for world ↔ chunk coordinate conversion:
- `WorldX(chunkSize int) float32` - Get world X coordinate
- `WorldY(chunkSize int) float32` - Get world Y coordinate
- `SetWorldPosition(x, y float32, chunkSize int)` - Set from world coordinates

### Match Loop Processing
**Location:** `nakama/modules/world/match.go`

Each tick (100ms):
1. Process incoming OpCode 1 (Movement) messages
2. Update PlayerState position and facing
3. Collect all entity positions (players now, bugs later)
4. Broadcast OpCode 11 (EntityUpdate) to all connected clients

---

## Client Implementation (Unity C#)

### Message DTOs
**Location:** `Assets/Scripts/Networking/NetworkMessages.cs`

```csharp
public static class OpCodes {
    public const int Movement = 1;
    public const int EntityUpdate = 11;
}

[Serializable]
public class MovementMessage {
    public float x;
    public float y;
    public int facing;
}

[Serializable]
public class EntityData {
    public string id;
    public string type;
    public float x;
    public float y;
    public int facing;
}

[Serializable]
public class EntityUpdateMessage {
    public EntityData[] entities;
}
```

### Movement Sending
**Location:** `Assets/Scripts/Player/PlayerController.cs`

Send strategy (hybrid for bandwidth efficiency):
- Send on state change (start moving, stop moving, direction change)
- Send at 100ms intervals while continuously moving
- Skip if not in a match

### Entity Manager
**Location:** `Assets/Scripts/Entities/EntityManager.cs`

Singleton responsibilities:
- Listen to `WorldManager.OnEntityUpdate` events
- Maintain dictionary of active entities by ID
- Spawn correct prefab based on entity type
- Update existing entities with new positions
- Destroy entities on player leave
- Skip local player (handled by PlayerController)

Prefab mapping:
```csharp
[SerializeField] private GameObject playerPrefab;
[SerializeField] private GameObject bugPrefab;
```

### Remote Entity
**Location:** `Assets/Scripts/Entities/RemoteEntity.cs`

Base component for all networked entities:
- Position interpolation over 150ms
- Facing direction updates
- Virtual methods for type-specific behavior

```csharp
public void SetTargetState(float x, float y, int facing) {
    _startPos = transform.position;
    _targetPos = new Vector2(x, y);
    _interpProgress = 0f;
    Facing = (Direction)facing;
}
```

---

## Data Flow

```
┌─────────────┐     OpCode 1      ┌─────────────┐
│   Client A  │ ──────────────────▶│   Server    │
│  (moving)   │                    │  MatchLoop  │
└─────────────┘                    └──────┬──────┘
                                          │
                                          │ Update PlayerState
                                          │ Collect all entities
                                          │
                                          ▼
┌─────────────┐     OpCode 11     ┌─────────────┐
│   Client A  │ ◀──────────────────│   Server    │
│   Client B  │ ◀──────────────────│  Broadcast  │
└─────────────┘                    └─────────────┘
       │
       │ EntityManager
       │ dispatches to
       │ RemoteEntity
       ▼
  ┌──────────────┐
  │ Interpolated │
  │   Position   │
  └──────────────┘
```

---

## File Summary

### Server (Go)
| File | Purpose |
|------|---------|
| `nakama/modules/entities/types.go` | Direction enum, EntityPosition |
| `nakama/modules/world/messages.go` | Wire format structs |
| `nakama/modules/world/state.go` | PlayerState, position helpers |
| `nakama/modules/world/match.go` | MatchLoop processing |

### Client (C#)
| File | Purpose |
|------|---------|
| `Assets/Scripts/Networking/NetworkMessages.cs` | OpCodes, DTOs |
| `Assets/Scripts/Player/PlayerController.cs` | Movement input + sending |
| `Assets/Scripts/Networking/WorldManager.cs` | OpCode 11 parsing |
| `Assets/Scripts/Entities/EntityManager.cs` | Entity lifecycle |
| `Assets/Scripts/Entities/RemoteEntity.cs` | Interpolated movement |

### Prefabs
| Prefab | Usage |
|--------|-------|
| `Assets/Prefabs/Entities/PlayerEntity.prefab` | Remote player visualization |
| `Assets/Prefabs/Entities/BugEntity.prefab` | Bug visualization |

---

## Future Extensions (Phase 3+)

### Bug AI
- Server spawns bugs, runs AI state machine in MatchLoop
- Bug positions broadcast via same EntityUpdate message
- Client spawns BugEntity prefabs automatically

### Additional Entity Types
- Trees, workers, projectiles
- Add new type string, create prefab, register in EntityManager

### Priority-Based Updates
- Near entities (≤1 chunk): 10/sec
- Mid entities (2 chunks): 5/sec
- Far entities (>2 chunks): 2/sec
- ~60% bandwidth reduction
