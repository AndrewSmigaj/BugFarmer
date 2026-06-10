using System;

namespace BugFarmer.Networking
{
    /// <summary>
    /// OpCodes for match state messages.
    /// Must match server nakama/modules/world/messages.go
    /// </summary>
    public static partial class OpCodes
    {
        // Client -> Server
        public const int Movement = 1;
        public const int Action = 2;
        public const int ChunkSubscribe = 3;
        public const int ChunkUnsub = 4;
        public const int TilePlace = 5;
        public const int TileBreak = 6;
        public const int ToolUse = 7;

        // Server -> Client
        public const int StateUpdate = 10;
        public const int EntityUpdate = 11;
        public const int Chat = 12;

        // Farming - Server -> Client
        public const int CropUpdate = 50;
        public const int TreeWaterUpdate = 51; // tree water charges (droplet indicator)

        // Farming - Client -> Server
        public const int PlantInteract = 55;
    }

    /// <summary>
    /// Direction enum matching server entities.Direction.
    /// Down=0, Left=1, Right=2, Up=3
    /// </summary>
    public enum Direction
    {
        Down = 0,
        Left = 1,
        Right = 2,
        Up = 3
    }

    // === Client -> Server Messages ===

    /// <summary>
    /// Movement message sent to server (OpCode 1).
    /// Contains world coordinates and facing direction.
    /// </summary>
    [Serializable]
    public class MovementMessage
    {
        public float x;
        public float y;
        public int facing;
    }

    // === Server -> Client Messages ===

    /// <summary>
    /// Single entity data within EntityUpdateMessage.
    /// </summary>
    [Serializable]
    public class EntityData
    {
        public string id;
        public string type;
        public float x;
        public float y;
        public int facing;
        public string eq;   // equipped item id; NULL when absent (omitempty + JsonUtility),
                            // not "" — consumers must null-coalesce
    }

    /// <summary>
    /// Entity update message from server (OpCode 11).
    /// Contains all entity positions for the tick.
    /// </summary>
    [Serializable]
    public class EntityUpdateMessage
    {
        public EntityData[] entities;
    }

    // === Farming Messages ===

    /// <summary>
    /// Tool use message sent to server (OpCode 7).
    /// Server looks up player.EquippedTool to determine action (hoe, watering can).
    /// </summary>
    [Serializable]
    public class ToolUseMessage
    {
        public int grid_x;  // Target cell X
        public int grid_y;  // Target cell Y
    }

    /// <summary>
    /// Plant interact message sent to server (OpCode 55).
    /// Used for harvesting or destroying crops.
    /// </summary>
    [Serializable]
    public class PlantInteractMessage
    {
        public int grid_x;
        public int grid_y;
        public bool destroy_intent;  // true = destroy, false = harvest
    }

    /// <summary>
    /// Crop update message from server (OpCode 50).
    /// Sent when crop state changes (growth, watering).
    /// </summary>
    [Serializable]
    public class CropUpdateMessage
    {
        public int grid_x;
        public int grid_y;
        public int stage;
        public int hp;
        public int water;
        public int flags;  // fertilized, etc.
    }

    /// <summary>
    /// Tree water charges changed (OpCode 51, display-only): show a droplet indicator over
    /// dry trees (water_charges == 0). Watering a tree grants 5 fruit worth of charges.
    /// </summary>
    [Serializable]
    public class TreeWaterUpdateMessage
    {
        public int grid_x;
        public int grid_y;
        public int water_charges;
    }
}
