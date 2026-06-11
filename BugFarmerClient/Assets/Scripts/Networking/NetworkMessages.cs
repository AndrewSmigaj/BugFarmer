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

        // World environment (dev tool + display) - must match server messages.go
        public const int DebugWorld = 90;       // C->S: set time / force weather / spawn swarm
        public const int WorldEnv = 91;         // S->C: day offset + weather (on change + join)
        public const int TreeHarvest = 92;      // C->S: hands-pick one fruit
        public const int TreeFruitUpdate = 93;  // S->C: a tree's fruit count (canopy overlay)
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
    /// Tree water/tank state (OpCode 51, display-only). Droplet rule, computed client-side:
    /// show iff water_level &lt; 3 &amp;&amp; last_water_day != currentDay — so the droplet
    /// reappears at the day rollover without a new message.
    /// </summary>
    [Serializable]
    public class TreeWaterUpdateMessage
    {
        public int grid_x;
        public int grid_y;
        public int water_level;      // 0..3 tank
        public int pending_growth;   // fruits left to grow in the current batch
        public long last_water_day;  // day index of the last MANUAL watering (-1 = never)
    }

    /// <summary>
    /// World environment display state (OpCode 91): sent on change and to each joiner.
    /// Time of day on both sides: ((tick + day_offset_ticks) % 8400) / 8400.
    /// weather_until_tick shares the SimulationTick domain — the missed-stop fallback;
    /// the weather field applies ON RECEIPT ("" = stop now).
    /// </summary>
    [Serializable]
    public class WorldEnvMessage
    {
        public long day_offset_ticks;
        public string weather;            // "" or "rain"
        public long weather_until_tick;
    }

    /// <summary>
    /// Debug world controls (OpCode 90, dev tool — the F8 panel). Sentinels for "leave
    /// alone": set_time_ticks -1, weather "", spawn_species "".
    /// </summary>
    [Serializable]
    public class DebugWorldMessage
    {
        public int set_time_ticks = -1;   // -1 or 0..8399
        public string weather = "";       // "" | "rain" | "stop"
        public string spawn_species = "";
        public int spawn_count;
        public float spawn_x;
        public float spawn_y;
    }

    /// <summary>
    /// A tree's fruit count changed (OpCode 93, display-only): drives the canopy fruit
    /// overlay. Broadcast on change + re-sent per chunk-subscribe for fruited trees.
    /// </summary>
    [Serializable]
    public class TreeFruitUpdateMessage
    {
        public int grid_x;
        public int grid_y;
        public int fruit_count;
        public string fruit_type;         // item id for the overlay sprite ("apple")
    }

    /// <summary>Hands-pick one fruit from the tree at (gx, gy) (OpCode 92).</summary>
    [Serializable]
    public class TreeHarvestMessage
    {
        public int gx;
        public int gy;
    }
}
