using UnityEngine;
using UnityEngine.EventSystems;
using BugFarmer.Data;

namespace BugFarmer.UI
{
    /// <summary>
    /// The armor/equipment flow: 7 slots (head, body, arms, legs, feet, acc1,
    /// acc2). Cosmetic + server-synced: every change is an OpCode-96 request;
    /// state updates ONLY on the server's OpCode-97 echo (the client never
    /// guesses). Interactions:
    ///  - cursor holds armor + click matching equipment slot -> equip (swap-safe:
    ///    the server puts any displaced piece into the vacated inventory slot)
    ///  - cursor empty + click a worn slot -> unequip to inventory
    ///  - right-click armor in the inventory (cursor empty) -> quick-equip
    /// </summary>
    public class EquipmentController : MonoBehaviour
    {
        public static EquipmentController Instance { get; private set; }

        public static readonly string[] SlotNames =
            { "head", "body", "arms", "legs", "feet", "acc1", "acc2" };

        private void Awake()
        {
            if (Instance != null && Instance != this) { Destroy(this); return; }
            Instance = this;
        }

        private void OnDestroy()
        {
            if (Instance == this) Instance = null;
        }

        /// <summary>The armor_slot name an equipment slot index accepts.</summary>
        private static string AcceptsSlot(int equipIndex) =>
            equipIndex >= 5 ? "accessory" : SlotNames[equipIndex];

        /// <summary>Equipment slot clicks (routed by DragDropController).</summary>
        public void OnEquipSlotClicked(InventorySlotUI slot, PointerEventData eventData,
                                       DragDropController drag)
        {
            var inv = InventoryManager.Instance;
            if (inv == null) return;

            if (drag.HasCursorItem)
            {
                // place the held armor into this slot (must match; must have come
                // from the ITEM inventory — the server takes it from there)
                var def = EntityDatabase.Get(drag.CursorItemId);
                if (def?.Category != "armor" || def.ArmorSlot != AcceptsSlot(slot.SlotIndex))
                    return; // wrong slot — keep holding
                if (drag.CursorSourceType != SlotType.Item)
                    return;
                inv.SendEquipArmor(slot.SlotIndex, drag.CursorSourceIndex);
                drag.ForceClearCursor(); // echoes repaint the truth
            }
            else if (eventData.button == PointerEventData.InputButton.Left ||
                     eventData.button == PointerEventData.InputButton.Right)
            {
                // unequip the worn piece back to the inventory
                if (!string.IsNullOrEmpty(inv.Equipment[slot.SlotIndex]))
                    inv.SendEquipArmor(slot.SlotIndex, -1);
            }
        }

        /// <summary>
        /// Right-click quick-equip from an ITEM slot (cursor empty). True if the
        /// click was consumed (the item is armor and was sent to its slot).
        /// </summary>
        public bool TryQuickEquip(InventorySlotUI slot)
        {
            var inv = InventoryManager.Instance;
            if (inv == null || slot.SlotType != SlotType.Item) return false;
            var def = EntityDatabase.Get(slot.CurrentItemId);
            if (def?.Category != "armor") return false;

            int equipIndex = System.Array.IndexOf(SlotNames, def.ArmorSlot);
            if (def.ArmorSlot == "accessory")
                equipIndex = string.IsNullOrEmpty(inv.Equipment[5]) || !string.IsNullOrEmpty(inv.Equipment[6]) ? 5 : 6;
            if (equipIndex < 0) return false;

            inv.SendEquipArmor(equipIndex, slot.SlotIndex);
            return true;
        }
    }
}
