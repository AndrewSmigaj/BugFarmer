using System;
using System.Collections.Generic;

namespace BugFarmer.Networking
{
    /// <summary>
    /// Inventory system OpCodes (extends OpCodes partial class).
    /// Must match server nakama/modules/world/messages.go
    /// </summary>
    public static partial class OpCodes
    {
        // Inventory - Server -> Client
        public const int BugSlotUpdate = 26;      // S->C: Single bug slot changed
        public const int ItemSlotUpdate = 37;     // S->C: Single item slot changed
        public const int FullInventorySync = 38;  // S->C: Complete inventory on join
        public const int ErrorMessage = 40;       // S->C: Operation failed

        // Inventory - Client -> Server
        public const int MoveSlot = 28;           // C->S: Move/swap items between slots
        public const int ReleaseBugs = 29;        // C->S: Release bugs from slot
    }

    /// <summary>
    /// Represents a single inventory slot (bug or item).
    /// Matches server InventorySlot struct.
    /// </summary>
    [Serializable]
    public class InventorySlot
    {
        public string item_id;  // species_id for bugs, item_id for tools, "" = empty
        public int count;
        public Dictionary<string, int> metadata;  // For tools with state (watering can uses)

        public bool IsEmpty => string.IsNullOrEmpty(item_id) || count <= 0;

        public InventorySlot()
        {
            item_id = "";
            count = 0;
            metadata = null;
        }

        public InventorySlot(string itemId, int count)
        {
            this.item_id = itemId;
            this.count = count;
            this.metadata = null;
        }

        public void Clear()
        {
            item_id = "";
            count = 0;
            metadata = null;
        }

        /// <summary>
        /// Get metadata value or default.
        /// </summary>
        public int GetMetadata(string key, int defaultValue = 0)
        {
            if (metadata == null || !metadata.ContainsKey(key))
                return defaultValue;
            return metadata[key];
        }
    }

    // === Server -> Client Messages ===

    /// <summary>
    /// Slot update from server (OpCode 26 for bugs, OpCode 37 for items).
    /// Sent when a single slot changes.
    /// </summary>
    [Serializable]
    public class SlotUpdateMessage
    {
        public int slot_index;
        public string item_id;  // "" = empty slot
        public int count;
        public Dictionary<string, int> metadata;  // For tools with state (watering can uses)
    }

    /// <summary>
    /// Full inventory sync from server (OpCode 38).
    /// Sent when player joins to sync complete inventory state.
    /// </summary>
    [Serializable]
    public class FullInventorySyncMessage
    {
        public InventorySlot[] bug_slots;   // All 20 bug slots
        public InventorySlot[] item_slots;  // All 10 item slots (= hotbar)
        public long coins;
    }

    /// <summary>
    /// Error message from server (OpCode 40).
    /// Sent when an operation fails.
    /// </summary>
    [Serializable]
    public class ErrorMessage
    {
        public string error;
    }

    // === Client -> Server Messages ===

    /// <summary>
    /// Move/swap items between slots (OpCode 28).
    /// Handles drag-drop and stack splitting.
    /// </summary>
    [Serializable]
    public class MoveSlotMessage
    {
        public string source_type;  // "bug" or "item"
        public int source_index;
        public string dest_type;    // "bug" or "item"
        public int dest_index;
        public int count;           // -1 = all, else specific amount
    }

    /// <summary>
    /// Release bugs from a slot AT a world point (OpCode 29). Released bugs join a nearby
    /// same-species swarm (within max(merge radius, the swarm's visual radius) of the
    /// click) or form a new swarm there.
    /// </summary>
    [Serializable]
    public class ReleaseBugsMessage
    {
        public int slot_index;
        public int count;  // -1 = all (the client sends the CURSOR count, never -1 —
                           // a half-pickup's remainder belongs to the slot)
        public float x;    // world release point (the click)
        public float y;
    }

    /// <summary>OpCode 96 (C->S): equip ItemSlots[inv_slot] into equipment slot
    /// equip_slot (0 head..4 feet, 5/6 accessories); inv_slot -1 = unequip.</summary>
    [System.Serializable]
    public class EquipArmorMessage
    {
        public int equip_slot;
        public int inv_slot;
    }

    /// <summary>OpCode 97 (S->C): the authoritative 7 worn-armor slot ids.</summary>
    [System.Serializable]
    public class EquipmentUpdateMessage
    {
        public string[] equipment;
    }
}
