using System;

namespace BugFarmer.Networking
{
    /// <summary>
    /// Bug system OpCodes (extends OpCodes partial class).
    /// Must match server nakama/modules/world/messages.go
    /// </summary>
    public static partial class OpCodes
    {
        // Bug System - Server -> Client
        public const int SwarmUpdate = 20;

        // Bug Catching (Phase 2a)
        public const int CatchBug = 24;           // C->S: Click to catch
        public const int BugCaught = 25;          // S->C: Broadcast catch event
        // OpCode 26 (BugSlotUpdate) moved to InventoryMessages.cs
        public const int EquipTool = 27;          // C->S: Equip/unequip tool
    }

    /// <summary>
    /// Single swarm data within SwarmUpdateMessage.
    /// Matches server SwarmData struct.
    /// </summary>
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
    }

    /// <summary>
    /// Swarm update message from server (OpCode 20).
    /// Contains all swarm positions for the tick.
    /// </summary>
    [Serializable]
    public class SwarmUpdateMessage
    {
        public SwarmData[] swarms;
    }

    // === Bug Catching Messages (Phase 2a) ===

    /// <summary>
    /// Catch attempt sent to server (OpCode 24).
    /// Client detects flies in radius and sends count per swarm.
    /// </summary>
    [Serializable]
    public class CatchBugMessage
    {
        public float click_x;
        public float click_y;
        public string swarm_id;
        public int caught_count;
    }

    /// <summary>
    /// Catch event broadcast to all clients (OpCode 25).
    /// Used to update swarm visuals and show catch animation.
    /// </summary>
    [Serializable]
    public class BugCaughtMessage
    {
        public string swarm_id;
        public string catcher_id;
        public int count;
        public int new_total;
        public float x;
        public float y;
    }

    // BugInventoryUpdateMessage removed - replaced by SlotUpdateMessage in InventoryMessages.cs

    /// <summary>
    /// Tool equip message sent to server (OpCode 27).
    /// Syncs equipped tool state for reach validation.
    /// </summary>
    [Serializable]
    public class EquipToolMessage
    {
        public string tool_id; // "" for hand, "small_net" for small net, etc.
    }
}
