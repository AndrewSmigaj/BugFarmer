using UnityEngine;
using UnityEngine.EventSystems;

namespace BugFarmer.UI
{
    /// <summary>
    /// The armor/equipment flow: 7 slots (head, body, arms, legs, feet,
    /// acc1, acc2). Skeleton for the armor pass — the equip/unequip RPCs,
    /// EquipmentState mirror, and composer wiring land there; until then the
    /// equipment slots are visible but inert.
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

        /// <summary>Equipment slot clicks (routed by DragDropController).</summary>
        public void OnEquipSlotClicked(InventorySlotUI slot, PointerEventData eventData,
                                       DragDropController drag)
        {
            // Armor pass wires this up (equip from cursor / pick back / swap).
            Debug.Log($"[Equipment] slot {SlotNames[slot.SlotIndex]} clicked (inert until the armor pass)");
        }
    }
}
