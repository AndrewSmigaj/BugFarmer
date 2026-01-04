using System;

namespace BugFarmer.Networking
{
    /// <summary>
    /// World Building OpCodes (extends OpCodes partial class).
    /// Must match server nakama/modules/world/messages.go
    /// </summary>
    public static partial class OpCodes
    {
        // Server -> Client (World Building)
        public const int ChunkData = 44;      // S->C: Full chunk on subscribe
        public const int BreakProgress = 45;  // S->C: Breaking progress update
        public const int WorldUpdate = 46;    // S->C: Single cell changed

        // Ground Items (Phase 5)
        public const int GroundItemSpawn = 47;  // S->C: Item dropped on ground
        public const int GroundItemRemove = 48; // S->C: Item picked up/despawned
        public const int PickupItem = 49;       // C->S: Player picks up item
    }

    // === Client -> Server Messages ===

    /// <summary>
    /// Subscribe/unsubscribe to chunk (OpCode 3/4).
    /// Matches server ChunkSubscribeMessage in messages.go
    /// </summary>
    [Serializable]
    public class ChunkSubscribeMessage
    {
        public int chunk_x;
        public int chunk_y;
    }

    /// <summary>
    /// Place an occupant (OpCode 5).
    /// Matches server TilePlaceMessage in messages.go
    /// </summary>
    [Serializable]
    public class TilePlaceMessage
    {
        public int grid_x;        // Global cell X
        public int grid_y;        // Global cell Y
        public string occupant_id;
        public int direction;     // 0-3 facing
    }

    /// <summary>
    /// Break an occupant (OpCode 6).
    /// Matches server TileBreakMessage in messages.go
    /// </summary>
    [Serializable]
    public class TileBreakMessage
    {
        public int grid_x;        // Global cell X
        public int grid_y;        // Global cell Y
    }

    // === Server -> Client Messages ===

    /// <summary>
    /// Placed occupant data within chunk.
    /// Matches server PlacedOccupant in occupants.go
    /// </summary>
    [Serializable]
    public class PlacedOccupant
    {
        public string id;
        public int dir;           // 0=down, 1=left, 2=right, 3=up
    }

    /// <summary>
    /// Breaking progress (OpCode 45).
    /// Matches server BreakProgressMessage in messages.go
    /// </summary>
    [Serializable]
    public class BreakProgressMessage
    {
        public int grid_x;
        public int grid_y;
        public int current_hp;
        public int max_hp;
        public string player_id;
    }

    // === Ground Item Messages (Phase 5) ===

    /// <summary>
    /// Ground item spawned (OpCode 47).
    /// Matches server GroundItemSpawnMessage in messages.go
    /// </summary>
    [Serializable]
    public class GroundItemSpawnMessage
    {
        public string id;        // Unique instance ID
        public string item_type; // Type of item (e.g., "rock_small")
        public int count;        // Stack count
        public float x;          // World X position
        public float y;          // World Y position
    }

    /// <summary>
    /// Ground item removed (OpCode 48).
    /// Matches server GroundItemRemoveMessage in messages.go
    /// </summary>
    [Serializable]
    public class GroundItemRemoveMessage
    {
        public string id; // Unique instance ID to remove
    }

    /// <summary>
    /// Pickup item request (OpCode 49).
    /// Matches server PickupItemMessage in messages.go
    /// </summary>
    [Serializable]
    public class PickupItemMessage
    {
        public string id; // Unique instance ID to pick up
    }

    // === Notes on ChunkData and WorldUpdate ===
    //
    // ChunkDataMessage (OpCode 44) and WorldUpdateMessage (OpCode 46)
    // cannot use Unity's JsonUtility due to polymorphic occupants array.
    //
    // The server sends occupants as:
    //   - null: empty cell
    //   - "@": blocked by multi-cell occupant anchor elsewhere
    //   - {id, dir}: anchor cell with occupant data
    //
    // These messages are parsed directly in TilemapManager using
    // Newtonsoft.Json (JObject/JArray) which is included via Nakama package.
    //
    // Server struct reference:
    // type ChunkDataMessage struct {
    //     ChunkX    int                 `json:"chunk_x"`
    //     ChunkY    int                 `json:"chunk_y"`
    //     Ground    [][]string          `json:"ground"`    // 32x32 tile IDs
    //     Occupants [][]json.RawMessage `json:"occupants"` // 32x32 polymorphic
    // }
    //
    // type WorldUpdateMessage struct {
    //     GridX    int         `json:"grid_x"`
    //     GridY    int         `json:"grid_y"`
    //     Ground   string      `json:"ground,omitempty"`
    //     Occupant interface{} `json:"occupant,omitempty"` // nil, "@", or {id,dir}
    // }
}
