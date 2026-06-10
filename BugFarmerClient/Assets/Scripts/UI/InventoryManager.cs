using System;
using Nakama;
using UnityEngine;
using BugFarmer.Networking;

namespace BugFarmer.UI
{
    /// <summary>
    /// Manages the player's inventory (bugs and items).
    /// Receives updates from server and provides data for UI.
    /// </summary>
    public class InventoryManager : MonoBehaviour
    {
        public static InventoryManager Instance { get; private set; }

        public const int BugSlotCount = 20;
        public const int ItemSlotCount = 20;

        // Slot-based inventory
        public InventorySlot[] BugSlots { get; private set; }
        public InventorySlot[] ItemSlots { get; private set; }
        public long Coins { get; private set; }
        public int SelectedSlot { get; private set; }

        // Events
        public event Action OnInventoryChanged;
        public event Action<int> OnBugSlotChanged;
        public event Action<int> OnItemSlotChanged;
        public event Action<long> OnCoinsChanged;
        public event Action<int> OnSelectedSlotChanged;

        private void Awake()
        {
            if (Instance != null && Instance != this)
            {
                Destroy(gameObject);
                return;
            }
            Instance = this;

            // Initialize slot arrays with empty slots
            BugSlots = new InventorySlot[BugSlotCount];
            for (int i = 0; i < BugSlotCount; i++)
            {
                BugSlots[i] = new InventorySlot();
            }

            ItemSlots = new InventorySlot[ItemSlotCount];
            for (int i = 0; i < ItemSlotCount; i++)
            {
                ItemSlots[i] = new InventorySlot();
            }
        }

        private void Start()
        {
            if (WorldManager.Instance != null)
            {
                WorldManager.Instance.OnMatchData += HandleMatchData;
                Debug.Log("[InventoryManager] Subscribed to WorldManager.OnMatchData");
            }
            else
            {
                Debug.LogError("[InventoryManager] WorldManager.Instance is null! Cannot subscribe to match data.");
            }
        }

        private void OnDestroy()
        {
            if (WorldManager.Instance != null)
            {
                WorldManager.Instance.OnMatchData -= HandleMatchData;
            }
        }

        private void HandleMatchData(IMatchState state)
        {
            // Debug: log inventory-related opcodes
            if (state.OpCode == OpCodes.FullInventorySync ||
                state.OpCode == OpCodes.BugSlotUpdate ||
                state.OpCode == OpCodes.ItemSlotUpdate)
            {
                Debug.Log($"[InventoryManager] HandleMatchData received OpCode {state.OpCode}");
            }

            switch (state.OpCode)
            {
                case OpCodes.FullInventorySync:
                    {
                        var json = System.Text.Encoding.UTF8.GetString(state.State);
                        var msg = JsonUtility.FromJson<FullInventorySyncMessage>(json);
                        if (msg != null) HandleFullInventorySync(msg);
                    }
                    break;
                case OpCodes.BugSlotUpdate:
                    {
                        var json = System.Text.Encoding.UTF8.GetString(state.State);
                        var msg = JsonUtility.FromJson<SlotUpdateMessage>(json);
                        if (msg != null) HandleBugSlotUpdate(msg);
                    }
                    break;
                case OpCodes.ItemSlotUpdate:
                    {
                        var json = System.Text.Encoding.UTF8.GetString(state.State);
                        var msg = JsonUtility.FromJson<SlotUpdateMessage>(json);
                        if (msg != null) HandleItemSlotUpdate(msg);
                    }
                    break;
            }
        }

        /// <summary>
        /// Handle full inventory sync from server (on join).
        /// </summary>
        private void HandleFullInventorySync(FullInventorySyncMessage msg)
        {
            // Full sync repaints everything from server truth (reconnect) and bypasses the
            // echo interception — a held cursor stack would double-render. Drop it.
            DragDropController.Instance?.ForceClearCursor();

            // Sync bug slots
            if (msg.bug_slots != null)
            {
                int count = Mathf.Min(msg.bug_slots.Length, BugSlotCount);
                for (int i = 0; i < count; i++)
                {
                    BugSlots[i].item_id = msg.bug_slots[i]?.item_id ?? "";
                    BugSlots[i].count = msg.bug_slots[i]?.count ?? 0;
                }
                for (int i = count; i < BugSlotCount; i++)
                {
                    BugSlots[i].Clear();
                }
            }

            // Sync item slots
            if (msg.item_slots != null)
            {
                int count = Mathf.Min(msg.item_slots.Length, ItemSlotCount);
                for (int i = 0; i < count; i++)
                {
                    ItemSlots[i].item_id = msg.item_slots[i]?.item_id ?? "";
                    ItemSlots[i].count = msg.item_slots[i]?.count ?? 0;
                }
                for (int i = count; i < ItemSlotCount; i++)
                {
                    ItemSlots[i].Clear();
                }
            }

            // Sync coins and reset selection to slot 0
            Coins = msg.coins;
            SelectedSlot = 0;

            Debug.Log($"[Inventory] Synced: {CountNonEmptySlots(BugSlots)} bug stacks, " +
                      $"{CountNonEmptySlots(ItemSlots)} item stacks, {Coins} coins");

            OnInventoryChanged?.Invoke();
            OnCoinsChanged?.Invoke(Coins);
            OnSelectedSlotChanged?.Invoke(SelectedSlot);
            SyncEquippedTool();
        }

        /// <summary>
        /// Handle single bug slot update from server.
        /// </summary>
        private void HandleBugSlotUpdate(SlotUpdateMessage msg)
        {
            if (msg.slot_index < 0 || msg.slot_index >= BugSlotCount)
            {
                Debug.LogWarning($"[Inventory] Invalid bug slot index: {msg.slot_index}");
                return;
            }

            // Cursor-source echo interception (inline, pre-write — see DragDropController):
            // a catch can stack bugs into the very slot the cursor is dragging from.
            if (DragDropController.Instance != null &&
                DragDropController.Instance.TryInterceptSlotEcho(
                    SlotType.Bug, msg.slot_index, msg.item_id ?? "", msg.count))
            {
                OnBugSlotChanged?.Invoke(msg.slot_index);
                OnInventoryChanged?.Invoke();
                return; // slot value stays local (remainder); the count rode the cursor
            }

            BugSlots[msg.slot_index].item_id = msg.item_id ?? "";
            BugSlots[msg.slot_index].count = msg.count;

            Debug.Log($"[Inventory] Bug slot {msg.slot_index}: {msg.item_id} x{msg.count}");

            OnBugSlotChanged?.Invoke(msg.slot_index);
            OnInventoryChanged?.Invoke();
        }

        /// <summary>
        /// Handle single item slot update from server.
        /// </summary>
        private void HandleItemSlotUpdate(SlotUpdateMessage msg)
        {
            if (msg.slot_index < 0 || msg.slot_index >= ItemSlotCount)
            {
                Debug.LogWarning($"[Inventory] Invalid item slot index: {msg.slot_index}");
                return;
            }

            // Cursor-source echo interception (inline, pre-write — see DragDropController):
            // cursor-place consumes, walk-over pickups stack, watering uses tick — all into
            // the slot the cursor is dragging from; the count belongs on the cursor.
            if (DragDropController.Instance != null &&
                DragDropController.Instance.TryInterceptSlotEcho(
                    SlotType.Item, msg.slot_index, msg.item_id ?? "", msg.count))
            {
                OnItemSlotChanged?.Invoke(msg.slot_index);
                OnInventoryChanged?.Invoke();
                return; // slot value stays local (remainder); the count rode the cursor
            }

            ItemSlots[msg.slot_index].item_id = msg.item_id ?? "";
            ItemSlots[msg.slot_index].count = msg.count;

            Debug.Log($"[Inventory] Item slot {msg.slot_index}: {msg.item_id} x{msg.count}");

            OnItemSlotChanged?.Invoke(msg.slot_index);
            OnInventoryChanged?.Invoke();

            // Slot contents changed under the selection → keep the server's equipped tool fresh.
            if (msg.slot_index == SelectedSlot)
                SyncEquippedTool();
        }

        /// <summary>
        /// Select a hotbar slot (0-9). Sends EquipTool to server.
        /// </summary>
        public void SelectSlot(int slot)
        {
            if (slot < 0 || slot >= ItemSlotCount)
                return;

            if (slot == SelectedSlot)
                return;

            SelectedSlot = slot;
            OnSelectedSlotChanged?.Invoke(slot);
            SyncEquippedTool();
        }

        // The server's player.EquippedTool must track the equipped item's VALUE, not just the
        // selected index — dragging a tool into the selected slot (or consuming the held stack)
        // changes what's equipped without a slot switch. Resend whenever the value changes.
        private string _lastSentToolId;

        private void SyncEquippedTool()
        {
            string toolId = GetEquippedToolId();
            if (toolId == _lastSentToolId) return;
            _lastSentToolId = toolId;
            SendEquipTool(toolId);
        }

        /// <summary>
        /// Get the item ID of currently equipped tool.
        /// </summary>
        public string GetEquippedToolId()
        {
            return ItemSlots[SelectedSlot].item_id ?? "";
        }

        /// <summary>
        /// Local (client-only) slot mutations — DragDropController moving stacks onto/off
        /// the cursor — bypass the server-echo path, so the UI repaint + equipped-tool sync
        /// the echo tail normally provides must be triggered explicitly. Picking the equipped
        /// item onto the cursor correctly equips "" server-side (and cancel re-equips it;
        /// SyncEquippedTool dedupes by value).
        /// </summary>
        public void NotifyLocalSlotMutation(SlotType slotType, int index)
        {
            if (slotType == SlotType.Bug)
            {
                OnBugSlotChanged?.Invoke(index);
            }
            else
            {
                OnItemSlotChanged?.Invoke(index);
                if (index == SelectedSlot)
                    SyncEquippedTool();
            }
            OnInventoryChanged?.Invoke();
        }

        /// <summary>
        /// Clear inventory. Used when leaving world.
        /// </summary>
        public void Clear()
        {
            for (int i = 0; i < BugSlotCount; i++)
            {
                BugSlots[i].Clear();
            }
            for (int i = 0; i < ItemSlotCount; i++)
            {
                ItemSlots[i].Clear();
            }
            Coins = 0;
            SelectedSlot = 0;

            OnInventoryChanged?.Invoke();
            OnCoinsChanged?.Invoke(0);
            OnSelectedSlotChanged?.Invoke(0);
        }

        private void SendEquipTool(string toolId)
        {
            var world = WorldManager.Instance;
            if (world?.CurrentMatch == null) return;

            var socket = NetworkManager.Instance?.Socket;
            if (socket == null || !socket.IsConnected) return;

            var msg = new EquipToolMessage { tool_id = toolId };
            var json = JsonUtility.ToJson(msg);
            _ = socket.SendMatchStateAsync(world.CurrentMatch.Id, OpCodes.EquipTool, json);
        }

        private static int CountNonEmptySlots(InventorySlot[] slots)
        {
            int count = 0;
            foreach (var slot in slots)
            {
                if (!slot.IsEmpty) count++;
            }
            return count;
        }
    }
}
